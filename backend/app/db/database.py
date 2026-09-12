"""Database engine and session helpers."""

from __future__ import annotations

import sqlite3

from sqlmodel import Session, SQLModel, create_engine

from app.config import DB_PATH
from app.db import models  # noqa: F401 — register tables
from app.services.audio import audio_duration_ms

engine = create_engine(f"sqlite:///{DB_PATH}", connect_args={"check_same_thread": False})


def init_db() -> None:
    SQLModel.metadata.create_all(engine)
    run_migrations()


def _column_exists(conn: sqlite3.Connection, table: str, column: str) -> bool:
    rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
    return any(r[1] == column for r in rows)


def run_migrations() -> None:
    """Additive SQLite migrations for schema updates."""
    with sqlite3.connect(DB_PATH) as conn:
        if not _column_exists(conn, "books", "voice_id"):
            conn.execute("ALTER TABLE books ADD COLUMN voice_id TEXT")
        if not _column_exists(conn, "books", "voice_prompt"):
            conn.execute("ALTER TABLE books ADD COLUMN voice_prompt TEXT")
        if not _column_exists(conn, "chapters", "start_ms"):
            conn.execute("ALTER TABLE chapters ADD COLUMN start_ms INTEGER NOT NULL DEFAULT 0")
        if not _column_exists(conn, "chapters", "duration_ms"):
            conn.execute("ALTER TABLE chapters ADD COLUMN duration_ms INTEGER NOT NULL DEFAULT 0")
        if not _column_exists(conn, "jobs", "current_chapter_id"):
            conn.execute("ALTER TABLE jobs ADD COLUMN current_chapter_id INTEGER")
        if not _column_exists(conn, "jobs", "current_chunk_id"):
            conn.execute("ALTER TABLE jobs ADD COLUMN current_chunk_id INTEGER")

        chapters = conn.execute(
            "SELECT id, book_id, \"index\", audio_path, start_ms, duration_ms FROM chapters ORDER BY book_id, \"index\""
        ).fetchall()
        per_book_cursor: dict[int, int] = {}
        for chapter_id, book_id, _idx, audio_path, start_ms, duration_ms in chapters:
            cursor = per_book_cursor.get(book_id, 0)
            fixed_start = start_ms if (start_ms and start_ms >= 0) else cursor
            fixed_duration = duration_ms if (duration_ms and duration_ms > 0) else 0
            if fixed_duration == 0 and audio_path:
                try:
                    fixed_duration = audio_duration_ms(audio_path)
                except Exception:
                    fixed_duration = 0
            conn.execute(
                "UPDATE chapters SET start_ms=?, duration_ms=? WHERE id=?",
                (fixed_start, fixed_duration, chapter_id),
            )
            per_book_cursor[book_id] = fixed_start + fixed_duration
        conn.commit()


def get_session() -> Session:
    return Session(engine)
