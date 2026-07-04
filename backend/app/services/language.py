"""Central language detection — single dispatch point per PRD section 5."""

from __future__ import annotations

import re

SUPPORTED = frozenset({"en", "hi"})


def detect_language(text: str) -> str:
    """Return 'en' or 'hi' for a text sample."""
    sample = text[:8000].strip()
    if not sample:
        return "en"

    devanagari = len(re.findall(r"[\u0900-\u097F]", sample))
    latin = len(re.findall(r"[A-Za-z]", sample))
    if devanagari > latin * 0.3 and devanagari > 20:
        return "hi"
    if devanagari > latin:
        return "hi"

    try:
        from ftlangdetect import detect as ft_detect

        result = ft_detect(sample.replace("\n", " "), low_memory=True)
        code = result.get("lang", "en")
        if code == "hi":
            return "hi"
        return "en"
    except Exception:
        pass

    try:
        from langdetect import detect as ld_detect

        code = ld_detect(sample)
        return "hi" if code == "hi" else "en"
    except Exception:
        return "en"


def detect_book_language(chapter_texts: list[str]) -> str:
    """Aggregate chapter samples into en | hi | mixed."""
    if not chapter_texts:
        return "en"
    codes = [detect_language(t) for t in chapter_texts if t.strip()]
    if not codes:
        return "en"
    en_count = codes.count("en")
    hi_count = codes.count("hi")
    if en_count > 0 and hi_count > 0:
        return "mixed"
    return "hi" if hi_count >= en_count else "en"


def resolve_chunk_language(
    book_language: str,
    chapter_language: str | None,
    text: str,
) -> str:
    """Pick effective language for a chunk."""
    if chapter_language in SUPPORTED:
        return chapter_language
    if book_language in SUPPORTED:
        return book_language
    if book_language == "mixed":
        return detect_language(text)
    return detect_language(text)
