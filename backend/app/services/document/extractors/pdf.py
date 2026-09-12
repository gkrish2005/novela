"""
PDF Extractor using PyMuPDF (fitz) with layout awareness, font/flag extraction,
stable character offsets, native TOC bookmarks, and OCR quality checks.
"""

from __future__ import annotations

from pathlib import Path
from typing import Union

import fitz

from app.services.document.extractors.base import BaseExtractor
from app.services.document.models import (
    DocumentBlock,
    DocumentLine,
    DocumentPage,
    DocumentSpan,
    NormalizedDocument,
    TOCEntry,
)


class PDFExtractor(BaseExtractor):
    """Layout-aware PDF extractor preserving typography, bboxes, lines, spans, and offsets."""

    def can_handle(self, source: Union[str, Path, bytes]) -> bool:
        if isinstance(source, (str, Path)):
            return str(source).lower().endswith(".pdf")
        if isinstance(source, bytes):
            return source.startswith(b"%PDF")
        return False

    def extract(self, source: Union[str, Path, bytes], title_hint: str = "") -> NormalizedDocument:
        if isinstance(source, bytes):
            doc = fitz.open(stream=source, filetype="pdf")
            source_path = None
        else:
            path = Path(source)
            doc = fitz.open(path)
            source_path = str(path)

        # 1. Metadata and cover extraction
        meta_title = doc.metadata.get("title") if doc.metadata else None
        meta_author = doc.metadata.get("author") if doc.metadata else None
        title = meta_title or title_hint
        if not title and source_path:
            title = Path(source_path).stem.replace("_", " ").replace("-", " ")

        cover_bytes = None
        try:
            pix = doc[0].get_pixmap(matrix=fitz.Matrix(2, 2))
            cover_bytes = pix.tobytes("png")
        except Exception:
            cover_bytes = None

        # 2. Extract native bookmarks/TOC
        toc_entries: list[TOCEntry] = []
        try:
            raw_toc = doc.get_toc()  # [[lvl, title, page, dest], ...]
            for item in raw_toc:
                if len(item) >= 3:
                    lvl, t_title, p_num = item[0], str(item[1]).strip(), int(item[2])
                    if t_title:
                        toc_entries.append(
                            TOCEntry(
                                title=t_title,
                                level=lvl,
                                page_num=p_num,
                                source="native",
                            )
                        )
        except Exception:
            pass

        # 3. Layout and span extraction across pages
        pages: list[DocumentPage] = []
        doc_char_cursor = 0
        total_extracted_chars = 0
        warnings: list[str] = []

        for p_idx, page in enumerate(doc):
            p_num = p_idx + 1
            p_dict = page.get_text("dict")
            width = float(page.rect.width)
            height = float(page.rect.height)

            page_blocks: list[DocumentBlock] = []
            page_raw_parts: list[str] = []
            page_char_start = doc_char_cursor
            p_char_cursor = 0

            for b in p_dict.get("blocks", []):
                if b.get("type") != 0:  # Skip image/vector blocks in text layout
                    continue

                b_lines: list[DocumentLine] = []
                b_spans: list[DocumentSpan] = []
                b_text_parts: list[str] = []
                b_bbox = tuple(float(x) for x in b.get("bbox", (0, 0, 0, 0)))

                font_sizes: list[float] = []
                font_names: list[str] = []
                bold_flags: list[bool] = []
                italic_flags: list[bool] = []

                b_char_start = doc_char_cursor

                for line in b.get("lines", []):
                    l_spans: list[DocumentSpan] = []
                    l_text_parts: list[str] = []
                    l_bbox = tuple(float(x) for x in line.get("bbox", (0, 0, 0, 0)))
                    l_char_start = doc_char_cursor

                    for span in line.get("spans", []):
                        s_text = span.get("text", "")
                        if not s_text:
                            continue

                        s_len = len(s_text)
                        s_font = span.get("font", "Default")
                        s_size = float(span.get("size", 10.0))
                        s_flags = int(span.get("flags", 0))
                        s_bbox = tuple(float(x) for x in span.get("bbox", (0, 0, 0, 0)))

                        is_bold = bool(s_flags & 2**4) or "bold" in s_font.lower() or "black" in s_font.lower()
                        is_italic = bool(s_flags & 2**1) or "italic" in s_font.lower() or "oblique" in s_font.lower()
                        is_caps = s_text.isupper() and len(s_text.strip()) > 2

                        d_span = DocumentSpan(
                            text=s_text,
                            doc_char_start=doc_char_cursor,
                            doc_char_end=doc_char_cursor + s_len,
                            page_char_start=p_char_cursor,
                            page_char_end=p_char_cursor + s_len,
                            page_start=p_num,
                            page_end=p_num,
                            bbox=s_bbox,
                            font_name=s_font,
                            font_size=s_size,
                            flags=s_flags,
                            is_bold=is_bold,
                            is_italic=is_italic,
                            is_all_caps=is_caps,
                        )

                        l_spans.append(d_span)
                        b_spans.append(d_span)
                        l_text_parts.append(s_text)
                        font_sizes.append(s_size)
                        font_names.append(s_font)
                        bold_flags.append(is_bold)
                        italic_flags.append(is_italic)

                        doc_char_cursor += s_len
                        p_char_cursor += s_len
                        total_extracted_chars += s_len

                    if l_spans:
                        l_text = " ".join(l_text_parts)
                        b_lines.append(
                            DocumentLine(
                                spans=l_spans,
                                bbox=l_bbox,
                                text=l_text,
                                doc_char_start=l_char_start,
                                doc_char_end=doc_char_cursor,
                            )
                        )
                        b_text_parts.append(l_text)

                if b_spans:
                    b_text = "\n".join(b_text_parts)
                    avg_size = sum(font_sizes) / len(font_sizes) if font_sizes else 10.0
                    is_b = any(bold_flags)
                    is_it = any(italic_flags)
                    is_caps = b_text.isupper() and len(b_text.strip()) > 2
                    primary_font = max(set(font_names), key=font_names.count) if font_names else "Default"

                    block_obj = DocumentBlock(
                        text=b_text,
                        spans=b_spans,
                        lines=b_lines,
                        bbox=b_bbox,
                        page_num=p_num,
                        avg_font_size=avg_size,
                        primary_font=primary_font,
                        is_bold=is_b,
                        is_italic=is_it,
                        is_all_caps=is_caps,
                        line_count=len(b_lines),
                        doc_char_start=b_char_start,
                        doc_char_end=doc_char_cursor,
                    )
                    page_blocks.append(block_obj)
                    page_raw_parts.append(b_text)

            p_raw = "\n\n".join(page_raw_parts)
            pages.append(
                DocumentPage(
                    page_num=p_num,
                    width=width,
                    height=height,
                    blocks=page_blocks,
                    raw_text=p_raw,
                    doc_char_start=page_char_start,
                    doc_char_end=doc_char_cursor,
                )
            )

        doc.close()

        # 4. Check for scanned / image PDF quality
        total_pages = len(pages)
        avg_chars_per_page = total_extracted_chars / max(1, total_pages)
        quality_score = 1.0
        if total_pages > 0 and avg_chars_per_page < 30:
            quality_score = 0.2
            warnings.append("Low text density detected (< 30 chars/page). PDF may be scanned or image-based.")

        full_raw_text = "\n\n".join(p.raw_text for p in pages if p.raw_text)

        # Fallback title from first page if needed
        if not title and pages and pages[0].blocks:
            first_block_text = pages[0].blocks[0].text.strip()
            if 3 < len(first_block_text) < 60:
                title = first_block_text

        return NormalizedDocument(
            source_type="pdf",
            source_path=source_path,
            title=title or "Untitled Document",
            author=meta_author,
            pages=pages,
            raw_text=full_raw_text,
            normalized_text=full_raw_text,
            toc_entries=toc_entries,
            cover_bytes=cover_bytes,
            extraction_warnings=warnings,
            quality_score=quality_score,
            metadata={"total_pages": total_pages, "avg_chars_per_page": avg_chars_per_page},
        )
