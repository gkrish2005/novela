"""
Document text extraction and structure parsing — language-agnostic.
Powered by the Universal Document Structure Understanding Engine.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from app.services.document.engine import DocumentStructureEngine
from app.services.document.parser_utils import clean_text_segment, normalize_heading_for_tts


@dataclass
class ParsedChapter:
    title: str
    text: str


@dataclass
class ParsedBook:
    title: str
    author: str | None
    chapters: list[ParsedChapter]
    cover_bytes: bytes | None = None


def _clean_text(text: str) -> str:
    return clean_text_segment(text)


def _normalize_heading_for_tts(text: str) -> str:
    return normalize_heading_for_tts(text)


def _split_chapters_structural(text: str, book_title: str) -> list[ParsedChapter]:
    """
    Splits text stream into structural chapters using DocumentStructureEngine.
    """
    tree = DocumentStructureEngine.parse_text_stream(text, book_title)
    return tree.to_narratable_chapters()


def parse_txt(path: Path) -> ParsedBook:
    raw = path.read_text(encoding="utf-8", errors="replace")
    title = path.stem.replace("_", " ").replace("-", " ")
    if title.lower() == "book":
        title = "Untitled Book"

    tree = DocumentStructureEngine.parse_text_stream(raw, title)
    return ParsedBook(
        title=tree.title or title,
        author=tree.author,
        chapters=tree.to_narratable_chapters(),
    )


def parse_md(path: Path) -> ParsedBook:
    return parse_txt(path)


def parse_pdf(path: Path) -> ParsedBook:
    tree = DocumentStructureEngine.parse_pdf(path)
    return ParsedBook(
        title=tree.title,
        author=tree.author,
        chapters=tree.to_narratable_chapters(),
        cover_bytes=tree.cover_bytes,
    )


def parse_epub(path: Path) -> ParsedBook:
    from ebooklib import epub
    from bs4 import BeautifulSoup

    book = epub.read_epub(str(path))
    title_meta = book.get_metadata("DC", "title")
    book_title = title_meta[0][0] if title_meta else path.stem
    author_meta = book.get_metadata("DC", "creator")
    author = author_meta[0][0] if author_meta else None

    section_texts: list[str] = []
    for item in book.get_items():
        if item.get_type() == 9:  # DOCUMENT
            soup = BeautifulSoup(item.get_content(), "html.parser")
            text = _clean_text(soup.get_text("\n"))
            if text:
                section_texts.append(text)

    combined_text = "\n\n".join(section_texts)
    tree = DocumentStructureEngine.parse_text_stream(combined_text, book_title)

    return ParsedBook(
        title=book_title,
        author=author,
        chapters=tree.to_narratable_chapters(),
    )


def parse_docx(path: Path) -> ParsedBook:
    from docx import Document

    doc = Document(str(path))
    text = _clean_text("\n\n".join(p.text for p in doc.paragraphs if p.text.strip()))
    title = path.stem.replace("_", " ")

    tree = DocumentStructureEngine.parse_text_stream(text, title)
    return ParsedBook(
        title=title,
        author=None,
        chapters=tree.to_narratable_chapters(),
    )


def parse_document(path: Path) -> ParsedBook:
    suffix = path.suffix.lower()
    parsers = {
        ".txt": parse_txt,
        ".md": parse_md,
        ".pdf": parse_pdf,
        ".epub": parse_epub,
        ".docx": parse_docx,
    }
    parser = parsers.get(suffix)
    if not parser:
        raise ValueError(f"Unsupported format: {suffix}")
    return parser(path)
