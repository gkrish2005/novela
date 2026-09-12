"""Tests for document parsing."""

from pathlib import Path

from app.services.parser import parse_txt, _normalize_heading_for_tts, _split_chapters_structural


def test_parse_txt_single_chapter(tmp_path: Path):
    p = tmp_path / "sample.txt"
    p.write_text("Chapter 1\n\nHello world.\n\nMore text here.", encoding="utf-8")
    book = parse_txt(p)
    assert book.title == "sample"
    assert len(book.chapters) >= 1
    assert "Hello" in book.chapters[0].text


def test_normalize_heading_for_tts():
    # ALL-CAPS headings should be normalized to title case
    assert _normalize_heading_for_tts("IGNORANCE IS STRENGTH") == "Ignorance Is Strength"
    assert _normalize_heading_for_tts("WAR IS PEACE") == "War Is Peace"
    # Normal words or small capitalized words (<= 2 chars) should remain intact or handled correctly
    assert _normalize_heading_for_tts("IT is a test") == "IT is a test"
    # Mixed case should not be touched
    assert _normalize_heading_for_tts("Winston Smith reads a book.") == "Winston Smith reads a book."


def test_split_chapters_structural_goldstein():
    sample_text = (
        "PART ONE\n"
        "ONE\n"
        "Winston was reading Goldstein's book:\n"
        "Chapter 1. IGNORANCE IS STRENGTH.\n"
        "Throughout recorded time, there have been three kinds of people.\n"
        "Chapter 3. WAR IS PEACE.\n"
        "The splitting up of the world continues.\n"
        "He closed the book."
    )
    chapters = _split_chapters_structural(sample_text, "1984")
    # It should split only on PART ONE / ONE, but NOT split on Chapter 1 and Chapter 3 of Goldstein's book!
    # So we should only have Front Matter (empty) and Chapter ONE.
    # Since Front Matter is empty and ignored/merged, chapters should have len == 1
    assert len(chapters) == 1
    assert chapters[0].title == "Part ONE - Chapter ONE"
    assert "IGNORANCE IS STRENGTH" in chapters[0].text
    assert "WAR IS PEACE" in chapters[0].text
