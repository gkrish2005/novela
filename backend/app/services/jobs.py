"""Background narration jobs — resumable across app restarts."""

from __future__ import annotations

import shutil
import threading
from datetime import datetime
from pathlib import Path

from sqlmodel import Session, select

from app import config
from app.db.database import engine
from app.db.models import Book, Chapter, Chunk, Job, WordTimestamp
from app.services import audio as audio_svc
from app.services.aligner import align_audio, fallback_word_timestamps
from app.services.chunker import chunk_text
from app.services.language import detect_language, resolve_chunk_language
from app.services.tts.router import synthesize

_executor_lock = threading.Lock()
_active_books: set[int] = set()
_priority_chapters: dict[int, list[int]] = {}


def _chunk_is_done(chunk: Chunk) -> bool:
    return chunk.status == "ready" and bool(chunk.audio_path) and Path(chunk.audio_path).exists()


def _update_job(
    session: Session,
    job: Job,
    progress: float,
    message: str,
    status: str | None = None,
    *,
    clear_position: bool = False,
) -> None:
    job.progress = progress
    job.message = message
    job.updated_at = datetime.utcnow()
    if status:
        job.status = status
    if clear_position:
        job.current_chapter_id = None
        job.current_chunk_id = None
    session.add(job)
    session.commit()


def _persist_job_progress(
    session: Session,
    job: Job,
    chapter_id: int,
    chunk_id: int,
    message: str,
) -> None:
    """Atomically record the chunk currently being processed."""
    job.status = "running"
    job.current_chapter_id = chapter_id
    job.current_chunk_id = chunk_id
    job.message = message
    job.updated_at = datetime.utcnow()
    session.add(job)
    session.commit()


def _book_timeline_end(session: Session, book_id: int) -> int:
    chapters = session.exec(
        select(Chapter).where(Chapter.book_id == book_id, Chapter.status == "ready").order_by(Chapter.index)
    ).all()
    if not chapters:
        return 0
    return max((ch.start_ms + ch.duration_ms for ch in chapters if ch.duration_ms > 0), default=0)


def _process_chunk(
    session: Session,
    book: Book,
    chapter: Chapter,
    chunk: Chunk,
    book_id: int,
    chapter_offset_ms: int,
) -> tuple[Path, int]:
    lang = resolve_chunk_language(book.language, chapter.language, chunk.text)
    chunk.language = lang
    chunk.status = "processing"
    session.add(chunk)
    session.commit()

    wav = config.AUDIO_DIR / f"book{book_id}" / f"ch{chapter.id}" / f"chunk{chunk.index}.wav"
    wav.parent.mkdir(parents=True, exist_ok=True)
    engine_name = synthesize(chunk.text, lang, wav)
    chunk.tts_engine = engine_name
    chunk.audio_path = str(wav)
    chunk.status = "ready"
    session.add(chunk)
    session.commit()

    try:
        words = align_audio(wav, chunk.text, lang)
    except Exception:
        dur = audio_svc.audio_duration_ms(wav)
        words = fallback_word_timestamps(chunk.text, dur, lang)

    for w in words:
        session.add(
            WordTimestamp(
                chapter_id=chapter.id,
                word=w["word"],
                start_ms=w["start_ms"] + chapter_offset_ms,
                end_ms=w["end_ms"] + chapter_offset_ms,
                char_start=w["char_start"],
                char_end=w["char_end"],
                language=lang,
            )
        )
    session.commit()

    duration = audio_svc.audio_duration_ms(wav)
    return wav, duration


def _finalize_chapter(
    session: Session,
    book_id: int,
    chapter: Chapter,
    chunks: list[Chunk],
    total_duration: int,
) -> int:
    wav_paths = [Path(c.audio_path) for c in chunks if c.audio_path and Path(c.audio_path).exists()]
    if not wav_paths:
        return total_duration

    chapter_audio = config.AUDIO_DIR / f"book{book_id}" / f"chapter_{chapter.index}.wav"
    audio_svc.concat_wavs(wav_paths, chapter_audio)
    chapter.audio_path = str(chapter_audio)
    chapter.start_ms = total_duration
    chapter.duration_ms = audio_svc.audio_duration_ms(chapter_audio)
    chapter.status = "ready"
    session.add(chapter)
    session.commit()
    return total_duration + chapter.duration_ms


def process_book(book_id: int, job_id: int) -> None:
    with Session(engine) as session:
        book = session.get(Book, book_id)
        job = session.get(Job, job_id)
        if not book or not job:
            return

        try:
            job.status = "running"
            session.add(job)
            session.commit()

            chapters = list(
                session.exec(select(Chapter).where(Chapter.book_id == book_id).order_by(Chapter.index)).all()
            )
            priority = _priority_chapters.get(book_id, [])
            if priority:
                priority_set = set(priority)
                prioritized = [c for pid in priority for c in chapters if c.id == pid]
                remaining = [c for c in chapters if c.id not in priority_set]
                chapters = prioritized + remaining

            total_chapters = max(len(chapters), 1)
            total_duration = _book_timeline_end(session, book_id)

            for ci, chapter in enumerate(chapters):
                if chapter.status == "ready":
                    continue

                chapter.status = "processing"
                session.add(chapter)
                session.commit()

                chapter_lang = chapter.language or book.language
                if chapter_lang == "mixed":
                    chapter_lang = detect_language(chapter.title)

                chunks = list(
                    session.exec(
                        select(Chunk).where(Chunk.chapter_id == chapter.id).order_by(Chunk.index)
                    ).all()
                )

                if not chunks:
                    texts = chunk_text("") or [""]
                    for i, t in enumerate(texts):
                        lang = resolve_chunk_language(book.language, chapter.language, t)
                        session.add(
                            Chunk(
                                chapter_id=chapter.id,
                                index=i,
                                text=t,
                                spoken_text=t,
                                language=lang,
                                status="pending",
                            )
                        )
                    session.commit()
                    chunks = list(
                        session.exec(
                            select(Chunk).where(Chunk.chapter_id == chapter.id).order_by(Chunk.index)
                        ).all()
                    )

                chapter_offset_ms = 0
                for chunk in chunks:
                    if _chunk_is_done(chunk):
                        chapter_offset_ms += audio_svc.audio_duration_ms(Path(chunk.audio_path))
                        continue

                    _persist_job_progress(
                        session,
                        job,
                        chapter.id,
                        chunk.id,
                        f"Chapter {ci + 1}/{total_chapters}, chunk {chunk.index + 1}/{len(chunks)}",
                    )

                    wav, duration = _process_chunk(
                        session, book, chapter, chunk, book_id, chapter_offset_ms
                    )
                    chapter_offset_ms += duration

                if chunks and all(_chunk_is_done(c) for c in chunks):
                    total_duration = _finalize_chapter(session, book_id, chapter, chunks, total_duration)

                progress = (ci + 1) / total_chapters * 100
                _update_job(session, job, progress, f"Chapter {ci + 1}/{total_chapters} done")

            book.total_duration_ms = _book_timeline_end(session, book_id)
            session.add(book)
            session.commit()
            _update_job(
                session,
                job,
                100.0,
                "Narration complete",
                status="done",
                clear_position=True,
            )
            _priority_chapters.pop(book_id, None)

        except Exception as exc:
            _update_job(session, job, job.progress, str(exc), status="error")
        finally:
            with _executor_lock:
                _active_books.discard(book_id)


def _start_job_thread(book_id: int, job_id: int) -> bool:
    """Start narration worker if this book is not already running."""
    with _executor_lock:
        if book_id in _active_books:
            return False
        _active_books.add(book_id)

    def _run() -> None:
        try:
            process_book(book_id, job_id)
        finally:
            with _executor_lock:
                _active_books.discard(book_id)

    thread = threading.Thread(target=_run, daemon=True)
    thread.start()
    return True


def recover_interrupted_jobs() -> None:
    """Resume queued/running jobs after app restart."""
    with Session(engine) as session:
        jobs = list(
            session.exec(
                select(Job).where(Job.status.in_(["queued", "running"]))
            ).all()
        )

    chosen_by_book: dict[int, Job] = {}
    for job in jobs:
        current = chosen_by_book.get(job.book_id)
        if current is None:
            chosen_by_book[job.book_id] = job
            continue
        if job.status == "running" and current.status != "running":
            chosen_by_book[job.book_id] = job
        elif job.status == current.status and job.created_at > current.created_at:
            chosen_by_book[job.book_id] = job

    resume_ids = {job.id for job in chosen_by_book.values()}
    for job in jobs:
        if job.id in resume_ids:
            continue
        with Session(engine) as session:
            stale = session.get(Job, job.id)
            if stale and stale.status in ("queued", "running"):
                stale.status = "error"
                stale.message = "Superseded by newer job on restart"
                stale.updated_at = datetime.utcnow()
                session.add(stale)
                session.commit()

    for job in chosen_by_book.values():
        _start_job_thread(job.book_id, job.id)


def enqueue_narration(book_id: int) -> int:
    with Session(engine) as session:
        job = Job(book_id=book_id, status="queued", progress=0.0, message="Queued")
        session.add(job)
        session.commit()
        session.refresh(job)
        job_id = job.id

    _start_job_thread(book_id, job_id)
    return job_id


def prioritize_chapter(book_id: int, chapter_id: int) -> int:
    """Move a chapter to the front of the active/future narration queue."""
    current = _priority_chapters.setdefault(book_id, [])
    _priority_chapters[book_id] = [chapter_id] + [cid for cid in current if cid != chapter_id]

    with Session(engine) as session:
        existing = session.exec(
            select(Job)
            .where(Job.book_id == book_id, Job.status.in_(["queued", "running"]))
            .order_by(Job.created_at.desc())
        ).first()
        if existing:
            existing.message = f"Chapter {chapter_id} bumped to front"
            existing.updated_at = datetime.utcnow()
            session.add(existing)
            session.commit()
            _start_job_thread(book_id, existing.id)
            return existing.id

    return enqueue_narration(book_id)


def import_parsed_book(
    parsed,
    source_path: Path,
    language_override: str | None = None,
) -> int:
    from app.services.cover import generate_placeholder, save_cover_bytes
    from app.services.language import detect_book_language

    with Session(engine) as session:
        chapter_langs = [detect_language(c.text) for c in parsed.chapters]
        detected = language_override or detect_book_language([c.text for c in parsed.chapters])

        book = Book(
            title=parsed.title,
            author=parsed.author,
            source_file_path=str(source_path),
            language=detected,
            cover_source="extracted" if parsed.cover_bytes else "generated",
        )
        session.add(book)
        session.commit()
        session.refresh(book)

        if parsed.cover_bytes:
            book.cover_path = save_cover_bytes(book.id, parsed.cover_bytes, "extracted")
        else:
            book.cover_path = generate_placeholder(parsed.title, book.id)
        session.add(book)
        session.commit()

        dest = source_path.parent
        stored = dest / f"book_{book.id}{source_path.suffix}"
        if source_path != stored:
            shutil.copy2(source_path, stored)
            book.source_file_path = str(stored)
            session.add(book)
            session.commit()

        for i, ch in enumerate(parsed.chapters):
            ch_lang = chapter_langs[i] if detected == "mixed" else detected
            if ch_lang == "mixed":
                ch_lang = detect_language(ch.text)
            chapter = Chapter(
                book_id=book.id,
                index=i,
                title=ch.title,
                language=ch_lang,
                status="pending",
                start_ms=0,
                duration_ms=0,
            )
            session.add(chapter)
            session.commit()
            session.refresh(chapter)

            for j, text in enumerate(chunk_text(ch.text)):
                lang = resolve_chunk_language(detected, ch_lang, text)
                session.add(
                    Chunk(
                        chapter_id=chapter.id,
                        index=j,
                        text=text,
                        spoken_text=text,
                        language=lang,
                        status="pending",
                    )
                )
            session.commit()

        return book.id
