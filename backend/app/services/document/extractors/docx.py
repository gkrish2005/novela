"""
DOCX Extractor using python-docx to preserve Word heading styles, run formatting,
bold/italic flags, font sizes, and paragraph ordering.
"""

from __future__ import annotations

import io
from pathlib import Path
from typing import Union

import docx

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


class DOCXExtractor(BaseExtractor):
    """Extracts DOCX documents preserving paragraph styles, run formatting, and offsets."""

    def can_handle(self, source: Union[str, Path, bytes]) -> bool:
        if isinstance(source, (str, Path)):
            return str(source).lower().endswith(".docx")
        if isinstance(source, bytes):
            return source.startswith(b"PK\x03\x04")  # Standard OOXML zip container
        return False

    def extract(self, source: Union[str, Path, bytes], title_hint: str = "") -> NormalizedDocument:
        source_path = None
        if isinstance(source, bytes):
            doc = docx.Document(io.BytesIO(source))
        else:
            path = Path(source)
            source_path = str(path)
            doc = docx.Document(str(path))

        # 1. Metadata
        title = title_hint
        if hasattr(doc, "core_properties") and doc.core_properties.title:
            title = doc.core_properties.title
        if not title and source_path:
            title = Path(source_path).stem.replace("_", " ").replace("-", " ")

        author = doc.core_properties.author if hasattr(doc, "core_properties") else None

        # 2. Extract paragraphs and runs
        blocks: list[DocumentBlock] = []
        toc_entries: list[TOCEntry] = []
        doc_cursor = 0

        for p in doc.paragraphs:
            text = clean_text_segment(p.text.strip())
            if not text:
                continue

            style_name = p.style.name.lower() if p.style and p.style.name else ""
            is_heading_style = "heading" in style_name or "title" in style_name

            # Check heading level
            h_level = 1
            if "heading 1" in style_name:
                h_level = 1
            elif "heading 2" in style_name:
                h_level = 2
            elif "heading 3" in style_name:
                h_level = 3
            elif "heading 4" in style_name:
                h_level = 4
            elif "title" in style_name:
                h_level = 1

            if is_heading_style:
                toc_entries.append(
                    TOCEntry(
                        title=text,
                        level=h_level,
                        page_num=1,
                        source="docx_style",
                    )
                )

            font_size = max(11.0, 20.0 - (h_level * 2.0)) if is_heading_style else 10.0
            is_bold = is_heading_style or any(run.bold for run in p.runs if run.bold)
            is_italic = any(run.italic for run in p.runs if run.italic)

            b_start = doc_cursor
            b_spans: list[DocumentSpan] = []
            b_lines: list[DocumentLine] = []

            # Process runs
            if p.runs:
                for run in p.runs:
                    r_text = run.text
                    if not r_text:
                        continue
                    r_len = len(r_text)
                    r_font_size = run.font.size.pt if run.font and run.font.size else font_size
                    r_bold = run.bold if run.bold is not None else is_bold
                    r_italic = run.italic if run.italic is not None else is_italic

                    span = DocumentSpan(
                        text=r_text,
                        doc_char_start=doc_cursor,
                        doc_char_end=doc_cursor + r_len,
                        page_char_start=doc_cursor,
                        page_char_end=doc_cursor + r_len,
                        page_start=1,
                        page_end=1,
                        font_size=float(r_font_size),
                        is_bold=bool(r_bold),
                        is_italic=bool(r_italic),
                        is_all_caps=r_text.isupper() and len(r_text.strip()) > 2,
                    )
                    b_spans.append(span)
                    doc_cursor += r_len
            else:
                span_len = len(text)
                span = DocumentSpan(
                    text=text,
                    doc_char_start=doc_cursor,
                    doc_char_end=doc_cursor + span_len,
                    page_char_start=doc_cursor,
                    page_char_end=doc_cursor + span_len,
                    page_start=1,
                    page_end=1,
                    font_size=font_size,
                    is_bold=is_bold,
                    is_italic=is_italic,
                    is_all_caps=text.isupper() and len(text) > 2,
                )
                b_spans.append(span)
                doc_cursor += span_len

            line = DocumentLine(
                spans=b_spans,
                text=text,
                doc_char_start=b_start,
                doc_char_end=doc_cursor,
            )
            b_lines.append(line)

            block = DocumentBlock(
                text=text,
                spans=b_spans,
                lines=b_lines,
                page_num=1,
                avg_font_size=font_size,
                is_bold=is_bold,
                is_italic=is_italic,
                line_count=1,
                doc_char_start=b_start,
                doc_char_end=doc_cursor,
            )
            blocks.append(block)

        page = DocumentPage(
            page_num=1,
            width=612.0,
            height=792.0,
            blocks=blocks,
            raw_text="\n\n".join(b.text for b in blocks),
            doc_char_start=0,
            doc_char_end=doc_cursor,
        )

        full_raw = page.raw_text

        return NormalizedDocument(
            source_type="docx",
            source_path=source_path,
            title=title or "Untitled DOCX Document",
            author=author,
            pages=[page],
            raw_text=full_raw,
            normalized_text=full_raw,
            toc_entries=toc_entries,
            quality_score=1.0,
        )
