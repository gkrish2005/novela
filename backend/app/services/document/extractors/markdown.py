"""
Markdown extractor parsing headers (#, ##, ###) and paragraph blocks with offsets.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Union

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


class MarkdownExtractor(BaseExtractor):
    """Extracts Markdown content into a NormalizedDocument preserving header levels."""

    def can_handle(self, source: Union[str, Path, bytes]) -> bool:
        if isinstance(source, (str, Path)):
            return str(source).lower().endswith((".md", ".markdown"))
        return False

    def extract(self, source: Union[str, Path, bytes], title_hint: str = "") -> NormalizedDocument:
        source_path = None
        if isinstance(source, bytes):
            raw_text = source.decode("utf-8", errors="replace")
        elif isinstance(source, Path) or (isinstance(source, str) and (source.endswith(".md") or source.endswith(".markdown"))):
            p = Path(source)
            if p.is_file():
                source_path = str(p)
                raw_text = p.read_text(encoding="utf-8", errors="replace")
            else:
                raw_text = str(source)
        else:
            raw_text = str(source)

        cleaned = clean_text_segment(raw_text)
        title = title_hint
        if not title and source_path:
            title = Path(source_path).stem.replace("_", " ").replace("-", " ")

        blocks: list[DocumentBlock] = []
        toc_entries: list[TOCEntry] = []
        doc_cursor = 0

        # Split by double newline into markdown chunks
        chunks = [c.strip() for c in cleaned.split("\n\n") if c.strip()]

        for chunk in chunks:
            # Check if chunk starts with markdown header #
            h_match = re.match(r"^(#{1,6})\s+(.+)$", chunk, re.MULTILINE)
            if h_match:
                h_level = len(h_match.group(1))
                h_text = h_match.group(2).strip()

                if not title and h_level == 1:
                    title = h_text

                toc_entries.append(
                    TOCEntry(
                        title=h_text,
                        level=h_level,
                        page_num=1,
                        source="markdown_header",
                    )
                )

                font_size = max(11.0, 20.0 - (h_level * 2.0))
                span_len = len(h_text)
                span = DocumentSpan(
                    text=h_text,
                    doc_char_start=doc_cursor,
                    doc_char_end=doc_cursor + span_len,
                    page_char_start=doc_cursor,
                    page_char_end=doc_cursor + span_len,
                    page_start=1,
                    page_end=1,
                    font_name="MarkdownHeader",
                    font_size=font_size,
                    is_bold=True,
                )
                line = DocumentLine(
                    spans=[span],
                    text=h_text,
                    doc_char_start=doc_cursor,
                    doc_char_end=doc_cursor + span_len,
                )
                block = DocumentBlock(
                    text=h_text,
                    spans=[span],
                    lines=[line],
                    page_num=1,
                    avg_font_size=font_size,
                    is_bold=True,
                    line_count=1,
                    doc_char_start=doc_cursor,
                    doc_char_end=doc_cursor + span_len,
                )
                blocks.append(block)
                doc_cursor += span_len
            else:
                # Regular paragraph block
                lines_raw = [l.strip() for l in chunk.split("\n") if l.strip()]
                if not lines_raw:
                    continue

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
                        page_char_start=l_start,
                        page_char_end=l_start + l_len,
                        page_start=1,
                        page_end=1,
                        font_name="Default",
                        font_size=10.0,
                        is_bold=False,
                    )
                    b_spans.append(span)
                    doc_cursor += l_len
                    b_lines.append(
                        DocumentLine(
                            spans=[span],
                            text=l_raw,
                            doc_char_start=l_start,
                            doc_char_end=doc_cursor,
                        )
                    )

                block = DocumentBlock(
                    text=chunk,
                    spans=b_spans,
                    lines=b_lines,
                    page_num=1,
                    avg_font_size=10.0,
                    is_bold=False,
                    line_count=len(lines_raw),
                    doc_char_start=b_start,
                    doc_char_end=doc_cursor,
                )
                blocks.append(block)

        page = DocumentPage(
            page_num=1,
            width=612.0,
            height=792.0,
            blocks=blocks,
            raw_text=cleaned,
            doc_char_start=0,
            doc_char_end=doc_cursor,
        )

        return NormalizedDocument(
            source_type="markdown",
            source_path=source_path,
            title=title or "Untitled Markdown Document",
            pages=[page],
            raw_text=cleaned,
            normalized_text=cleaned,
            toc_entries=toc_entries,
            quality_score=1.0,
        )
