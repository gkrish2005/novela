"""
Plain text extractor mapping paragraphs to blocks, lines, and spans with stable offsets.
"""

from __future__ import annotations

from pathlib import Path
from typing import Union

from app.services.document.extractors.base import BaseExtractor
from app.services.document.models import (
    DocumentBlock,
    DocumentLine,
    DocumentPage,
    DocumentSpan,
    NormalizedDocument,
)
from app.services.document.parser_utils import clean_text_segment


class TXTExtractor(BaseExtractor):
    """Extracts plain text into NormalizedDocument representation."""

    def can_handle(self, source: Union[str, Path, bytes]) -> bool:
        if isinstance(source, (str, Path)):
            return str(source).lower().endswith(".txt")
        return False

    def extract(self, source: Union[str, Path, bytes], title_hint: str = "") -> NormalizedDocument:
        source_path = None
        if isinstance(source, bytes):
            raw_text = source.decode("utf-8", errors="replace")
        elif isinstance(source, Path) or (isinstance(source, str) and (source.endswith(".txt") or "\n" not in source)):
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
        if not title:
            first_line = cleaned.strip().split("\n")[0].strip()
            if 0 < len(first_line) < 60:
                title = first_line
            else:
                title = "Untitled Document"

        # Split into logical paragraphs
        paragraphs = [p.strip() for p in cleaned.split("\n\n") if p.strip()]
        blocks: list[DocumentBlock] = []
        doc_cursor = 0

        for p_idx, p in enumerate(paragraphs):
            lines_raw = [l.strip() for l in p.split("\n") if l.strip()]
            if not lines_raw:
                continue

            b_lines: list[DocumentLine] = []
            b_spans: list[DocumentSpan] = []
            b_start = doc_cursor

            is_heading_like = len(lines_raw) == 1 and len(p) < 80 and (p.isupper() or p.startswith("Chapter") or p.startswith("Part") or p.startswith("Section"))
            font_size = 14.0 if is_heading_like else 10.0
            is_bold = is_heading_like

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
                    font_size=font_size,
                    is_bold=is_bold,
                    is_all_caps=l_raw.isupper() and len(l_raw) > 2,
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
                text=p,
                spans=b_spans,
                lines=b_lines,
                page_num=1,
                avg_font_size=font_size,
                is_bold=is_bold,
                is_all_caps=p.isupper() and len(p) > 2,
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
            source_type="txt",
            source_path=source_path,
            title=title,
            pages=[page],
            raw_text=cleaned,
            normalized_text=cleaned,
            toc_entries=[],
            quality_score=1.0,
        )
