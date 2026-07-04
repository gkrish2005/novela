"""SQLModel schema — mirrors docs/PRD.md section 6."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class Book(SQLModel, table=True):
    __tablename__ = "books"

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    author: Optional[str] = None
    cover_path: Optional[str] = None
    cover_source: str = "generated"  # custom | extracted | generated
    source_file_path: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    total_duration_ms: int = 0
    language: str = "en"  # en | hi | mixed


class Chapter(SQLModel, table=True):
    __tablename__ = "chapters"

    id: Optional[int] = Field(default=None, primary_key=True)
    book_id: int = Field(foreign_key="books.id", index=True)
    index: int
    title: str
    audio_path: Optional[str] = None
    status: str = "pending"  # pending | processing | ready | error
    language: str = "en"
    start_ms: int = 0
    duration_ms: int = 0


class Chunk(SQLModel, table=True):
    __tablename__ = "chunks"

    id: Optional[int] = Field(default=None, primary_key=True)
    chapter_id: int = Field(foreign_key="chapters.id", index=True)
    index: int
    text: str
    spoken_text: Optional[str] = None
    audio_path: Optional[str] = None
    status: str = "pending"
    language: str = "en"
    tts_engine: Optional[str] = None


class WordTimestamp(SQLModel, table=True):
    __tablename__ = "word_timestamps"

    id: Optional[int] = Field(default=None, primary_key=True)
    chapter_id: int = Field(foreign_key="chapters.id", index=True)
    word: str
    start_ms: int
    end_ms: int
    char_start: int
    char_end: int
    language: str = "en"


class PlaybackState(SQLModel, table=True):
    __tablename__ = "playback_state"

    book_id: int = Field(primary_key=True, foreign_key="books.id")
    chapter_id: Optional[int] = Field(default=None, foreign_key="chapters.id")
    position_ms: int = 0
    speed: float = 1.0
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Job(SQLModel, table=True):
    __tablename__ = "jobs"

    id: Optional[int] = Field(default=None, primary_key=True)
    book_id: int = Field(foreign_key="books.id", index=True)
    status: str = "queued"  # queued | running | done | error
    progress: float = 0.0
    message: str = ""
    current_chapter_id: Optional[int] = Field(default=None, foreign_key="chapters.id")
    current_chunk_id: Optional[int] = Field(default=None, foreign_key="chunks.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
