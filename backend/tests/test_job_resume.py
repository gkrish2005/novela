"""Restart-safe narration job tests."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

# jobs -> aligner imports torch; stub it for unit tests without ML deps installed.
sys.modules.setdefault("torch", MagicMock())

from sqlmodel import Session, SQLModel, create_engine, select

from app.db.models import Book, Chapter, Chunk, Job
from app.services import jobs as job_svc


@pytest.fixture
def job_env(tmp_path, monkeypatch):
  """Isolated SQLite DB and audio dir for job tests."""
  db_path = tmp_path / "jobs.sqlite"
  audio_dir = tmp_path / "audio"
  audio_dir.mkdir()

  monkeypatch.setattr("app.config.DB_PATH", db_path)
  monkeypatch.setattr("app.config.AUDIO_DIR", audio_dir)
  monkeypatch.setattr("app.services.jobs.config.AUDIO_DIR", audio_dir)

  test_engine = create_engine(
    f"sqlite:///{db_path}",
    connect_args={"check_same_thread": False},
  )
  monkeypatch.setattr("app.db.database.engine", test_engine)
  monkeypatch.setattr("app.services.jobs.engine", test_engine)

  SQLModel.metadata.create_all(test_engine)

  monkeypatch.setattr("app.services.jobs.audio_svc.audio_duration_ms", lambda _p: 1000)
  monkeypatch.setattr(
    "app.services.jobs.audio_svc.concat_wavs",
    lambda paths, out: Path(out).write_bytes(b"concat"),
  )
  monkeypatch.setattr("app.services.jobs.align_audio", lambda _w, _t, _l: [])

  return test_engine


def _seed_book_with_chunks(engine, chunk_count: int = 3) -> tuple[int, int, list[int]]:
  with Session(engine) as session:
    book = Book(title="Resume Test", source_file_path="/tmp/t.txt", language="en")
    session.add(book)
    session.commit()
    session.refresh(book)

    chapter = Chapter(book_id=book.id, index=0, title="Ch 1", language="en", status="pending")
    session.add(chapter)
    session.commit()
    session.refresh(chapter)

    chunk_ids: list[int] = []
    for i in range(chunk_count):
      chunk = Chunk(
        chapter_id=chapter.id,
        index=i,
        text=f"chunk {i}",
        spoken_text=f"chunk {i}",
        language="en",
        status="pending",
      )
      session.add(chunk)
      session.commit()
      session.refresh(chunk)
      chunk_ids.append(chunk.id)

    job = Job(book_id=book.id, status="queued", progress=0.0, message="Queued")
    session.add(job)
    session.commit()
    session.refresh(job)

    return book.id, job.id, chunk_ids


def test_resume_skips_completed_chunks_after_simulated_crash(job_env, monkeypatch):
  """Simulate crash after first chunk; resume must not redo chunk 0."""
  engine = job_env
  book_id, job_id, chunk_ids = _seed_book_with_chunks(engine, chunk_count=3)

  synthesize_calls: list[int] = []
  crash_state = {"armed": True}

  def mock_synthesize(text: str, lang: str, output_path: Path, **kwargs) -> str:
    chunk_idx = int(output_path.stem.replace("chunk", ""))
    synthesize_calls.append(chunk_idx)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(b"wav")
    if crash_state["armed"] and len(synthesize_calls) == 2:
      crash_state["armed"] = False
      raise RuntimeError("simulated crash mid-chapter")
    return "kokoro"

  monkeypatch.setattr("app.services.jobs.synthesize", mock_synthesize)

  job_svc.process_book(book_id, job_id)
  assert synthesize_calls == [0, 1]

  with Session(engine) as session:
    job = session.get(Job, job_id)
    assert job is not None
    assert job.status == "error"
    assert job.current_chapter_id is not None
    assert job.current_chunk_id == chunk_ids[1]

    chunks = session.exec(select(Chunk).where(Chunk.chapter_id != None)).all()  # noqa: E711
    ready = [c for c in chunks if c.status == "ready"]
    assert len(ready) == 1
    assert ready[0].index == 0
    assert Path(ready[0].audio_path).exists()

  synthesize_calls.clear()

  with Session(engine) as session:
    job = session.get(Job, job_id)
    job.status = "queued"
    session.add(job)
    session.commit()

  job_svc.process_book(book_id, job_id)

  assert synthesize_calls == [1, 2], f"resume should only process chunks 1 and 2, got {synthesize_calls}"

  with Session(engine) as session:
    job = session.get(Job, job_id)
    assert job.status == "done"
    assert job.current_chapter_id is None
    assert job.current_chunk_id is None

    chunks = list(session.exec(select(Chunk).order_by(Chunk.index)).all())
    assert all(c.status == "ready" for c in chunks)
    assert all(c.audio_path and Path(c.audio_path).exists() for c in chunks)

    chapter = session.exec(select(Chapter)).first()
    assert chapter.status == "ready"
    assert chapter.audio_path is not None


def test_recover_interrupted_jobs_resumes_latest_per_book(job_env, monkeypatch):
  """Startup recovery should resume queued/running jobs, one per book."""
  engine = job_env
  book_id, job_id, _ = _seed_book_with_chunks(engine, chunk_count=1)

  def _quick_synth(text: str, lang: str, output_path: Path, **kwargs) -> str:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(b"wav")
    return "kokoro"

  monkeypatch.setattr("app.services.jobs.synthesize", _quick_synth)

  with Session(engine) as session:
    job = session.get(Job, job_id)
    job.status = "running"
    session.add(job)
    session.commit()

    older = Job(book_id=book_id, status="queued", progress=0.0, message="older")
    session.add(older)
    session.commit()

  started: list[int] = []
  real_start = job_svc._start_job_thread

  def track_start(bid: int, jid: int) -> bool:
    started.append(jid)
    return real_start(bid, jid)

  monkeypatch.setattr("app.services.jobs._start_job_thread", track_start)

  job_svc.recover_interrupted_jobs()

  assert job_id in started
  assert len(started) == 1
