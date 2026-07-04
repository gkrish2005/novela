"""Tests for language detection and chunking."""

from app.services.chunker import chunk_text
from app.services.language import detect_language


def test_detect_english():
    assert detect_language("The quick brown fox jumps over the lazy dog.") == "en"


def test_detect_hindi():
    text = "यह एक हिंदी वाक्य है जो परीक्षण के लिए लिखा गया है।"
    assert detect_language(text) == "hi"


def test_chunk_text_splits_long_passage():
    text = "Word. " * 200
    chunks = chunk_text(text, max_chars=100)
    assert len(chunks) > 1
    assert all(len(c) <= 120 for c in chunks)
