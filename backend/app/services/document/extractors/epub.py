"""
EPUB Extractor using ebooklib and BeautifulSoup to preserve spine order,
HTML heading semantics, NCX table of contents, and cover art.
"""

from __future__ import annotations

import io
from pathlib import Path
from typing import Union

import bs4
import ebooklib
from ebooklib import epub

from app.services.document.extractors.base import BaseExtractor
from app.services.document.models import (
    DocumentBlock,
    DocumentLine,
    DocumentPage,
    DocumentSpan,
    NormalizedDocument,
    TOCEntry,
)
from app.services.document.parser_utils import clean_text_segment


class EPUBExtractor(BaseExtractor):
    """Extracts EPUB ebooks preserving spine items, TOC hierarchy, and styled blocks."""

    def can_handle(self, source: Union[str, Path, bytes]) -> bool:
        if isinstance(source, (str, Path)):
            return str(source).lower().endswith(".epub")
        if isinstance(source, bytes):
            return source.startswith(b"PK\x03\x04")  # Standard zip archive
        return False

    def extract(self, source: Union[str, Path, bytes], title_hint: str = "") -> NormalizedDocument:
        source_path = None
        if isinstance(source, bytes):
            book = epub.read_epub(io.BytesIO(source))
        else:
            path = Path(source)
            source_path = str(path)
            book = epub.read_epub(str(path))

        # 1. Metadata & cover
        meta_titles = book.get_metadata("DC", "title")
        title = meta_titles[0][0] if meta_titles else title_hint
        if not title and source_path:
            title = Path(source_path).stem.replace("_", " ").replace("-", " ")

        meta_creators = book.get_metadata("DC", "creator")
        author = meta_creators[0][0] if meta_creators else None

        cover_bytes = None
        try:
            for item in book.get_items():
                if item.get_type() == ebooklib.ITEM_COVER or "cover" in item.get_name().lower():
                    if isinstance(item.get_content(), bytes):
                        cover_bytes = item.get_content()
                        break
        except Exception:
            pass

        # 2. Extract TOC from NCX/nav
        toc_entries: list[TOCEntry] = []
        try:
            def _walk_toc(toc_list: list, level: int = 1) -> None:
                for item in toc_list:
                    if isinstance(item, tuple):
                        section, subitems = item
                        if hasattr(section, "title") and section.title:
                            toc_entries.append(TOCEntry(title=section.title, level=level, source="epub_ncx"))
                        _walk_toc(subitems, level + 1)
                    elif hasattr(item, "title") and item.title:
                        toc_entries.append(TOCEntry(title=item.title, level=level, source="epub_ncx"))
                    elif isinstance(item, list):
                        _walk_toc(item, level)

            _walk_toc(book.toc)
        except Exception:
            pass

        # 3. Process documents in spine order
        pages: list[DocumentPage] = []
        doc_cursor = 0
        page_idx = 1

        for item_id, linear in book.spine:
            item = book.get_item_with_id(item_id)
            if not item or item.get_type() != ebooklib.ITEM_DOCUMENT:
                continue

            content_html = item.get_content().decode("utf-8", errors="replace")
            soup = bs4.BeautifulSoup(content_html, "html.parser")

            # Extract body or root elements
            body = soup.find("body") or soup
            elements = body.find_all(["h1", "h2", "h3", "h4", "h5", "h6", "p", "div", "blockquote", "li"])
            if not elements:
                raw_text = clean_text_segment(body.get_text(separator="\n\n"))
                if not raw_text.strip():
                    continue
                # Create a single block
                span_len = len(raw_text)
                span = DocumentSpan(
                    text=raw_text,
                    doc_char_start=doc_cursor,
                    doc_char_end=doc_cursor + span_len,
                    page_char_start=0,
                    page_char_end=span_len,
                    page_start=page_idx,
                    page_end=page_idx,
                    font_size=10.0,
                )
                block = DocumentBlock(
                    text=raw_text,
                    spans=[span],
                    lines=[DocumentLine(spans=[span], text=raw_text, doc_char_start=doc_cursor, doc_char_end=doc_cursor + span_len)],
                    page_num=page_idx,
                    doc_char_start=doc_cursor,
                    doc_char_end=doc_cursor + span_len,
                )
                pages.append(DocumentPage(page_num=page_idx, blocks=[block], raw_text=raw_text, doc_char_start=doc_cursor, doc_char_end=doc_cursor + span_len))
                doc_cursor += span_len
                page_idx += 1
                continue

            page_blocks: list[DocumentBlock] = []
            page_start_cursor = doc_cursor
            page_char_cursor = 0

            for el in elements:
                t = clean_text_segment(el.get_text().strip())
                if not t:
                    continue

                tag_name = el.name.lower()
                is_heading = tag_name.startswith("h")
                h_lvl = int(tag_name[1]) if is_heading and len(tag_name) > 1 and tag_name[1].isdigit() else 0
                font_size = max(11.0, 22.0 - (h_lvl * 2.0)) if is_heading else 10.0
                is_bold = is_heading or bool(el.find(["b", "strong"]))
                is_italic = bool(el.find(["i", "em"]))

                lines_raw = [l.strip() for l in t.split("\n") if l.strip()]
                b_lines: list[DocumentLine] = []
                b_spans: list[DocumentSpan] = []
                b_start = doc_cursor

                for l_raw in lines_raw:
                    l_start = doc_cursor
                    l_len = len(l_raw)
                    span = DocumentSpan(
                        text=l_raw,
                        doc_char_start=l_start,
                        doc_char_end=l_start + l_len,
                        page_char_start=page_char_cursor,
                        page_char_end=page_char_cursor + l_len,
                        page_start=page_idx,
                        page_end=page_idx,
                        font_size=font_size,
                        is_bold=is_bold,
                        is_italic=is_italic,
                        is_all_caps=l_raw.isupper() and len(l_raw) > 2,
                    )
                    b_spans.append(span)
                    doc_cursor += l_len
                    page_char_cursor += l_len
                    b_lines.append(
                        DocumentLine(
                            spans=[span],
                            text=l_raw,
                            doc_char_start=l_start,
                            doc_char_end=doc_cursor,
                        )
                    )

                block = DocumentBlock(
                    text=t,
                    spans=b_spans,
                    lines=b_lines,
                    page_num=page_idx,
                    avg_font_size=font_size,
                    is_bold=is_bold,
                    is_italic=is_italic,
                    line_count=len(lines_raw),
                    doc_char_start=b_start,
                    doc_char_end=doc_cursor,
                )
                page_blocks.append(block)

            if page_blocks:
                page_raw = "\n\n".join(b.text for b in page_blocks)
                pages.append(
                    DocumentPage(
                        page_num=page_idx,
                        blocks=page_blocks,
                        raw_text=page_raw,
                        doc_char_start=page_start_cursor,
                        doc_char_end=doc_cursor,
                    )
                )
                page_idx += 1

        full_raw = "\n\n".join(p.raw_text for p in pages)

        return NormalizedDocument(
            source_type="epub",
            source_path=source_path,
            title=title or "Untitled EPUB Document",
            author=author,
            pages=pages,
            raw_text=full_raw,
            normalized_text=full_raw,
            toc_entries=toc_entries,
            cover_bytes=cover_bytes,
            quality_score=1.0,
        )
