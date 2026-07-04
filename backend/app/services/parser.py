"""Document text extraction — language-agnostic."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


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
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _split_chapters(text: str) -> list[ParsedChapter]:
    pattern = re.compile(
        r"(?:^|\n)(?:chapter|CHAPTER|Chapter)\s+(\d+|[IVXLCDM]+)[:\s\-–—]*(.*?)(?=\n|$)",
        re.MULTILINE,
    )
    matches = list(pattern.finditer(text))
    if not matches:
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        if len(paragraphs) <= 1:
            return [ParsedChapter(title="Chapter 1", text=text)]
        chunk_size = max(1, len(paragraphs) // 8)
        chapters: list[ParsedChapter] = []
        for i in range(0, len(paragraphs), chunk_size):
            body = "\n\n".join(paragraphs[i : i + chunk_size])
            chapters.append(ParsedChapter(title=f"Chapter {len(chapters) + 1}", text=body))
        return chapters

    chapters = []
    for i, match in enumerate(matches):
        start = match.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        body = text[start:end].strip()
        label = match.group(2).strip() if match.group(2) else f"Chapter {match.group(1)}"
        title = label if label else f"Chapter {match.group(1)}"
        chapters.append(ParsedChapter(title=title, text=body))
    return chapters


def parse_txt(path: Path) -> ParsedBook:
    raw = path.read_text(encoding="utf-8", errors="replace")
    text = _clean_text(raw)
    title = path.stem.replace("_", " ").replace("-", " ")
    return ParsedBook(title=title, author=None, chapters=_split_chapters(text))


def parse_md(path: Path) -> ParsedBook:
    return parse_txt(path)


def parse_pdf(path: Path) -> ParsedBook:
    import pdfplumber

    pages: list[str] = []
    cover_bytes: bytes | None = None
    with pdfplumber.open(path) as pdf:
        for i, page in enumerate(pdf.pages):
            pages.append(page.extract_text() or "")
            if i == 0:
                try:
                    import fitz

                    doc = fitz.open(path)
                    pix = doc[0].get_pixmap(matrix=fitz.Matrix(2, 2))
                    cover_bytes = pix.tobytes("png")
                    doc.close()
                except Exception:
                    cover_bytes = None

    text = _clean_text("\n\n".join(pages))
    if len(text) < 50:
        try:
            import fitz

            doc = fitz.open(path)
            pages = [doc[i].get_text() for i in range(len(doc))]
            if not cover_bytes and len(doc) > 0:
                pix = doc[0].get_pixmap(matrix=fitz.Matrix(2, 2))
                cover_bytes = pix.tobytes("png")
            doc.close()
            text = _clean_text("\n\n".join(pages))
        except Exception:
            pass

    title = path.stem.replace("_", " ")
    return ParsedBook(title=title, author=None, chapters=_split_chapters(text), cover_bytes=cover_bytes)


def parse_epub(path: Path) -> ParsedBook:
    from ebooklib import epub
    from bs4 import BeautifulSoup

    book = epub.read_epub(str(path))
    title = book.get_metadata("DC", "title")
    book_title = title[0][0] if title else path.stem
    author_meta = book.get_metadata("DC", "creator")
    author = author_meta[0][0] if author_meta else None

    chapters: list[ParsedChapter] = []
    for item in book.get_items():
        if item.get_type() == 9:  # DOCUMENT
            soup = BeautifulSoup(item.get_content(), "html.parser")
            text = _clean_text(soup.get_text("\n"))
            if text:
                chapters.append(ParsedChapter(title=f"Section {len(chapters) + 1}", text=text))

    if not chapters:
        chapters = [ParsedChapter(title="Chapter 1", text="")]
    return ParsedBook(title=book_title, author=author, chapters=chapters)


def parse_docx(path: Path) -> ParsedBook:
    from docx import Document

    doc = Document(str(path))
    text = _clean_text("\n\n".join(p.text for p in doc.paragraphs if p.text.strip()))
    title = path.stem.replace("_", " ")
    return ParsedBook(title=title, author=None, chapters=_split_chapters(text))


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
