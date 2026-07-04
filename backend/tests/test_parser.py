"""Tests for document parsing."""

from pathlib import Path

from app.services.parser import parse_txt


def test_parse_txt_single_chapter(tmp_path: Path):
    p = tmp_path / "sample.txt"
    p.write_text("Chapter 1\n\nHello world.\n\nMore text here.", encoding="utf-8")
    book = parse_txt(p)
    assert book.title == "sample"
    assert len(book.chapters) >= 1
    assert "Hello" in book.chapters[0].text
