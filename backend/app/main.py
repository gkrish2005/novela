"""
Novela backend entrypoint.

Runs as a local sidecar process (FastAPI + uvicorn) that the Tauri frontend
talks to over localhost. See docs/PRD.md for the full architecture.
"""

from __future__ import annotations

import shutil
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from sqlmodel import Session, select

from app.config import AUDIO_DIR, COVERS_DIR, IMPORTS_DIR
from app.db.database import get_session, init_db
from app.db.models import Book, Chapter, Chunk, Job, PlaybackState, WordTimestamp
from app.schemas import (
    BookOut,
    ChapterOut,
    ImportResult,
    JobOut,
    LanguageDetectResult,
    PlaybackOut,
    WordOut,
)
from app.services import jobs as job_svc
from app.services.audio import encode_export
from app.services.cover import save_custom_cover
from app.services.language import detect_language
from app.services.parser import parse_document

app = FastAPI(title="Novela Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    init_db()
    job_svc.recover_interrupted_jobs()


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


def _book_out(session: Session, book: Book) -> BookOut:
    chapters = session.exec(
        select(Chapter).where(Chapter.book_id == book.id).order_by(Chapter.index)
    ).all()
    return BookOut(
        id=book.id,
        title=book.title,
        author=book.author,
        cover_path=book.cover_path,
        cover_source=book.cover_source,
        language=book.language,
        total_duration_ms=book.total_duration_ms,
        created_at=book.created_at,
        chapters=[
            ChapterOut(
                id=c.id,
                book_id=c.book_id,
                index=c.index,
                title=c.title,
                audio_path=c.audio_path,
                status=c.status,
                language=c.language,
                start_ms=c.start_ms,
                duration_ms=c.duration_ms,
            )
            for c in chapters
        ],
        voice_id=book.voice_id,
        voice_prompt=book.voice_prompt,
    )


@app.get("/books", response_model=list[BookOut])
def list_books() -> list[BookOut]:
    with get_session() as session:
        books = session.exec(select(Book).order_by(Book.created_at.desc())).all()
        return [_book_out(session, b) for b in books]


@app.get("/books/{book_id}", response_model=BookOut)
def get_book(book_id: int) -> BookOut:
    with get_session() as session:
        book = session.get(Book, book_id)
        if not book:
            raise HTTPException(404, "Book not found")
        return _book_out(session, book)


@app.patch("/books/{book_id}")
def update_book(
    book_id: int,
    title: str | None = None,
    language: str | None = None,
    voice_id: str | None = None,
    voice_prompt: str | None = None,
) -> BookOut:
    with get_session() as session:
        book = session.get(Book, book_id)
        if not book:
            raise HTTPException(404, "Book not found")
        
        if title is not None and title.strip():
            book.title = title.strip()
        
        voice_changed = False
        if language in ("en", "hi", "mixed") and language != book.language:
            book.language = language
            voice_changed = True
        
        if voice_id is not None and voice_id != book.voice_id:
            book.voice_id = voice_id
            voice_changed = True
            
        if voice_prompt is not None and voice_prompt != book.voice_prompt:
            book.voice_prompt = voice_prompt
            voice_changed = True

        if voice_changed:
            ready_chapters = session.exec(
                select(Chapter).where(Chapter.book_id == book_id, Chapter.status == "ready")
            ).all()
            if ready_chapters:
                chapters = session.exec(select(Chapter).where(Chapter.book_id == book_id)).all()
                for ch in chapters:
                    ch.status = "pending"
                    ch.audio_path = None
                    ch.start_ms = 0
                    ch.duration_ms = 0
                    session.add(ch)
                    
                    wts = session.exec(select(WordTimestamp).where(WordTimestamp.chapter_id == ch.id)).all()
                    for wt in wts:
                        session.delete(wt)
                        
                    chunks = session.exec(select(Chunk).where(Chunk.chapter_id == ch.id)).all()
                    for chunk in chunks:
                        chunk.status = "pending"
                        chunk.audio_path = None
                        session.add(chunk)
                
                book_audio_dir = AUDIO_DIR / f"book{book_id}"
                if book_audio_dir.exists():
                    shutil.rmtree(book_audio_dir, ignore_errors=True)
                
                book.total_duration_ms = 0

        session.add(book)
        session.commit()
        session.refresh(book)
        return _book_out(session, book)


@app.delete("/books/{book_id}")
def delete_book(book_id: int):
    with get_session() as session:
        book = session.get(Book, book_id)
        if not book:
            raise HTTPException(404, "Book not found")
        
        # 1. Delete source file from imports directory
        if book.source_file_path:
            src_path = Path(book.source_file_path)
            if src_path.exists():
                try:
                    src_path.unlink()
                except Exception:
                    pass
        
        # 2. Delete cover art file
        if book.cover_path:
            cov_path = Path(book.cover_path)
            if cov_path.exists():
                try:
                    cov_path.unlink()
                except Exception:
                    pass

        # 3. Delete narration audio directory
        book_audio_dir = AUDIO_DIR / f"book{book_id}"
        if book_audio_dir.exists():
            shutil.rmtree(book_audio_dir, ignore_errors=True)
            
        # 4. Clean up relational DB objects
        chapters = session.exec(select(Chapter).where(Chapter.book_id == book_id)).all()
        for ch in chapters:
            wts = session.exec(select(WordTimestamp).where(WordTimestamp.chapter_id == ch.id)).all()
            for wt in wts:
                session.delete(wt)
                
            chunks = session.exec(select(Chunk).where(Chunk.chapter_id == ch.id)).all()
            for chunk in chunks:
                session.delete(chunk)
                
            session.delete(ch)
            
        # Delete active jobs associated with this book
        jobs = session.exec(select(Job).where(Job.book_id == book_id)).all()
        for j in jobs:
            session.delete(j)

        session.delete(book)
        session.commit()
    return {"status": "deleted"}


@app.post("/import", response_model=ImportResult)
async def import_file(
    file: UploadFile = File(...),
    language: str | None = Form(None),
    voice_id: str | None = Form(None),
    voice_prompt: str | None = Form(None),
) -> ImportResult:
    suffix = Path(file.filename or "upload.txt").suffix.lower()
    dest = IMPORTS_DIR / f"import_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}{suffix}"
    with dest.open("wb") as f:
        shutil.copyfileobj(file.file, f)

    try:
        parsed = parse_document(dest)
    except Exception as exc:
        dest.unlink(missing_ok=True)
        raise HTTPException(400, str(exc)) from exc

    override = language if language in ("en", "hi", "mixed") else None
    book_id = job_svc.import_parsed_book(parsed, dest, override, voice_id, voice_prompt)

    with get_session() as session:
        book = session.get(Book, book_id)
        chapters = session.exec(select(Chapter).where(Chapter.book_id == book_id)).all()
        return ImportResult(
            book_id=book_id,
            title=book.title if book else parsed.title,
            detected_language=book.language if book else "en",
            chapter_count=len(chapters),
        )


@app.post("/import-path", response_model=ImportResult)
async def import_local_file(
    path: str = Form(...),
    language: str | None = Form(None),
    voice_id: str | None = Form(None),
    voice_prompt: str | None = Form(None),
) -> ImportResult:
    src_path = Path(path)
    if not src_path.exists():
        raise HTTPException(400, f"File not found: {path}")

    suffix = src_path.suffix.lower()
    dest = IMPORTS_DIR / f"import_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}{suffix}"
    shutil.copy2(src_path, dest)

    try:
        parsed = parse_document(dest)
    except Exception as exc:
        dest.unlink(missing_ok=True)
        raise HTTPException(400, str(exc)) from exc

    override = language if language in ("en", "hi", "mixed") else None
    book_id = job_svc.import_parsed_book(parsed, dest, override, voice_id, voice_prompt)

    with get_session() as session:
        book = session.get(Book, book_id)
        chapters = session.exec(select(Chapter).where(Chapter.book_id == book_id)).all()
        return ImportResult(
            book_id=book_id,
            title=book.title if book else parsed.title,
            detected_language=book.language if book else "en",
            chapter_count=len(chapters),
        )



@app.post("/detect-language", response_model=LanguageDetectResult)
async def detect_language_endpoint(text: str = Form(...)) -> LanguageDetectResult:
    return LanguageDetectResult(language=detect_language(text))


@app.post("/books/{book_id}/narrate", response_model=JobOut)
def start_narration(book_id: int) -> JobOut:
    with get_session() as session:
        book = session.get(Book, book_id)
        if not book:
            raise HTTPException(404, "Book not found")

    job_id = job_svc.enqueue_narration(book_id)
    with get_session() as session:
        job = session.get(Job, job_id)
        return JobOut(
            id=job.id,
            book_id=job.book_id,
            status=job.status,
            progress=job.progress,
            message=job.message,
        )


@app.post("/chapters/{chapter_id}/prioritize", response_model=JobOut)
def prioritize_chapter(chapter_id: int) -> JobOut:
    with get_session() as session:
        chapter = session.get(Chapter, chapter_id)
        if not chapter:
            raise HTTPException(404, "Chapter not found")
        if chapter.status == "ready":
            raise HTTPException(400, "Chapter already narrated")

        job_id = job_svc.prioritize_chapter(chapter.book_id, chapter_id)
        job = session.get(Job, job_id)
        return JobOut(
            id=job.id,
            book_id=job.book_id,
            status=job.status,
            progress=job.progress,
            message=job.message,
        )


@app.get("/jobs/{job_id}", response_model=JobOut)
def get_job(job_id: int) -> JobOut:
    with get_session() as session:
        job = session.get(Job, job_id)
        if not job:
            raise HTTPException(404, "Job not found")
        return JobOut(
            id=job.id,
            book_id=job.book_id,
            status=job.status,
            progress=job.progress,
            message=job.message,
        )


@app.get("/chapters/{chapter_id}/words", response_model=list[WordOut])
def get_chapter_words(chapter_id: int) -> list[WordOut]:
    with get_session() as session:
        chapter = session.get(Chapter, chapter_id)
        if not chapter:
            raise HTTPException(404, "Chapter not found")
        words = session.exec(
            select(WordTimestamp).where(WordTimestamp.chapter_id == chapter_id)
        ).all()
        return [
            WordOut(
                word=w.word,
                start_ms=w.start_ms,
                end_ms=w.end_ms,
                char_start=w.char_start,
                char_end=w.char_end,
                language=w.language,
            )
            for w in words
        ]


@app.get("/chapters/{chapter_id}/text")
def get_chapter_text(chapter_id: int) -> dict:
    with get_session() as session:
        chunks = session.exec(
            select(Chunk).where(Chunk.chapter_id == chapter_id).order_by(Chunk.index)
        ).all()
        return {"text": " ".join(c.text for c in chunks)}


@app.get("/chapters/{chapter_id}/audio")
def get_chapter_audio(chapter_id: int) -> FileResponse:
    with get_session() as session:
        chapter = session.get(Chapter, chapter_id)
        if not chapter or not chapter.audio_path:
            raise HTTPException(404, "Audio not ready")
        path = Path(chapter.audio_path)
        if not path.exists():
            raise HTTPException(404, "Audio file missing")
        return FileResponse(path, media_type="audio/wav")


@app.get("/covers/{book_id}")
def get_cover(book_id: int) -> FileResponse:
    with get_session() as session:
        book = session.get(Book, book_id)
        if not book or not book.cover_path:
            raise HTTPException(404, "Cover not found")
        path = Path(book.cover_path)
        if not path.exists():
            raise HTTPException(404, "Cover file missing")
        return FileResponse(path, media_type="image/png")


@app.post("/books/{book_id}/cover")
async def upload_cover(book_id: int, file: UploadFile = File(...)) -> BookOut:
    suffix = Path(file.filename or "cover.png").suffix
    temp = COVERS_DIR / f"upload_{book_id}{suffix}"
    with temp.open("wb") as f:
        shutil.copyfileobj(file.file, f)

    with get_session() as session:
        book = session.get(Book, book_id)
        if not book:
            temp.unlink(missing_ok=True)
            raise HTTPException(404, "Book not found")
        book.cover_path = save_custom_cover(book_id, temp)
        book.cover_source = "custom"
        session.add(book)
        session.commit()
        temp.unlink(missing_ok=True)
        return _book_out(session, book)


@app.get("/playback/{book_id}", response_model=PlaybackOut)
def get_playback(book_id: int) -> PlaybackOut:
    with get_session() as session:
        state = session.get(PlaybackState, book_id)
        if not state:
            return PlaybackOut(book_id=book_id, chapter_id=None, position_ms=0, speed=1.0)
        return PlaybackOut(
            book_id=state.book_id,
            chapter_id=state.chapter_id,
            position_ms=state.position_ms,
            speed=state.speed,
        )


@app.put("/playback/{book_id}", response_model=PlaybackOut)
def save_playback(
    book_id: int,
    chapter_id: int | None = None,
    position_ms: int = 0,
    speed: float = 1.0,
) -> PlaybackOut:
    with get_session() as session:
        state = session.get(PlaybackState, book_id)
        if not state:
            state = PlaybackState(book_id=book_id)
        state.chapter_id = chapter_id
        state.position_ms = position_ms
        state.speed = speed
        state.updated_at = datetime.utcnow()
        session.add(state)
        session.commit()
        return PlaybackOut(
            book_id=state.book_id,
            chapter_id=state.chapter_id,
            position_ms=state.position_ms,
            speed=state.speed,
        )


@app.post("/books/{book_id}/export")
def export_book(book_id: int, fmt: str = "m4b") -> dict:
    if fmt not in ("m4b", "mp3"):
        raise HTTPException(400, "Format must be m4b or mp3")

    with get_session() as session:
        book = session.get(Book, book_id)
        if not book:
            raise HTTPException(404, "Book not found")
        chapters = session.exec(
            select(Chapter).where(Chapter.book_id == book_id, Chapter.status == "ready").order_by(
                Chapter.index
            )
        ).all()
        if not chapters:
            raise HTTPException(400, "No narrated chapters to export")

        files = []
        for ch in chapters:
            if ch.audio_path and Path(ch.audio_path).exists():
                files.append((ch.title, Path(ch.audio_path)))

        out = AUDIO_DIR / f"book{book_id}" / f"{book.title}.{fmt}"
        cover = Path(book.cover_path) if book.cover_path else None
        encode_export(files, out, cover, fmt)
        return {"path": str(out)}


@app.get("/voices")
def list_voices() -> dict:
    voices = [
        "af_alloy", "af_aoede", "af_bella", "af_heart", "af_jessica", "af_kore", 
        "af_nicole", "af_nova", "af_river", "af_sarah", "af_sky", "am_adam", 
        "am_echo", "am_eric", "am_fenrir", "am_liam", "am_michael", "am_onyx", 
        "am_puck", "am_santa", "bf_alice", "bf_emma", "bf_isabella", "bf_lily", 
        "bm_daniel", "bm_fable", "bm_george", "bm_lewis", "ef_dora", "em_alex", 
        "em_santa", "ff_siwis", "hf_alpha", "hf_beta", "hm_omega", "hm_psi", 
        "if_sara", "im_nicola", "jf_alpha", "jf_gongitsune", "jf_nezumi", 
        "jf_tebukuro", "jm_kumo", "pf_dora", "pm_alex", "pm_santa", "zf_xiaobei", 
        "zf_xiaoni", "zf_xiaoxiao", "zf_xiaoyi", "zm_yunjian", "zm_yunxi", 
        "zm_yunxia", "zm_yunyang"
    ]
    return {"voices": voices}


@app.get("/voices/hindi-presets")
def get_hindi_presets() -> list[dict]:
    return [
        {"id": "clear_warm_female", "name": "Clear Warm Female", "description": "Female speaker, clear & warm, moderate pace"},
        {"id": "deep_expressive_male", "name": "Deep Expressive Male", "description": "Male speaker, deep & expressive"},
        {"id": "slow_soft_female", "name": "Slow Soft Female", "description": "Female speaker, soft & slow"},
    ]


@app.get("/voices/preview")
def get_voice_preview(voice_id: str) -> FileResponse:
    import tempfile
    from app.services.tts.kokoro import synthesize_english

    temp_dir = Path(tempfile.gettempdir())
    preview_path = temp_dir / f"preview_{voice_id}.wav"

    text = f"This is a preview of the {voice_id.replace('af_', 'female ').replace('am_', 'male ').replace('bf_', 'British female ').replace('bm_', 'British male ')} voice."
    try:
        synthesize_english(text, preview_path, voice=voice_id)
        return FileResponse(preview_path, media_type="audio/wav")
    except Exception as e:
        raise HTTPException(500, f"Preview failed: {str(e)}")

