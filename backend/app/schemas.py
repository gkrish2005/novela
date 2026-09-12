"""Pydantic response schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ChapterOut(BaseModel):
    id: int
    book_id: int
    index: int
    title: str
    audio_path: Optional[str]
    status: str
    language: str
    start_ms: int
    duration_ms: int


class BookOut(BaseModel):
    id: int
    title: str
    author: Optional[str]
    cover_path: Optional[str]
    cover_source: str
    language: str
    total_duration_ms: int
    created_at: datetime
    chapters: list[ChapterOut] = []
    voice_id: Optional[str] = None
    voice_prompt: Optional[str] = None


class WordOut(BaseModel):
    word: str
    start_ms: int
    end_ms: int
    char_start: int
    char_end: int
    language: str


class JobOut(BaseModel):
    id: int
    book_id: int
    status: str
    progress: float
    message: str


class PlaybackOut(BaseModel):
    book_id: int
    chapter_id: Optional[int]
    position_ms: int
    speed: float


class ImportResult(BaseModel):
    book_id: int
    title: str
    detected_language: str
    chapter_count: int


class LanguageDetectResult(BaseModel):
    language: str
