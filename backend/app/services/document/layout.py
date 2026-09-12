"""
Layout and typography extraction for documents (PDF and structured text).
Extracts font metrics, coordinates, paragraph blocks, and statistically marks running headers/footers.
"""

from __future__ import annotations

import statistics
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

from app.services.document.models import (
    DocumentBlock,
    DocumentLine,
    DocumentPage,
    DocumentSpan,
    NormalizedDocument,
)


@dataclass
class TextSpanInfo:
    text: str
    font_name: str
    font_size: float
    flags: int  # PyMuPDF font flags (e.g. 2=italic, 16=bold)
    is_bold: bool
    is_italic: bool
    bbox: tuple[float, float, float, float]  # (x0, y0, x1, y1)
    page_num: int


@dataclass
class LayoutBlock:
    text: str
    spans: list[Any] = field(default_factory=list)
    bbox: tuple[float, float, float, float] = (0.0, 0.0, 0.0, 0.0)
    page_num: int = 1
    avg_font_size: float = 10.0
    is_bold: bool = False
    is_all_caps: bool = False
    line_count: int = 1
    is_header: bool = False
    is_footer: bool = False
    header_footer_confidence: float = 0.0


@dataclass
class PageLayout:
    page_num: int
    width: float
    height: float
    blocks: list[Any]
    raw_text: str


@dataclass
class DocumentLayout:
    pages: list[PageLayout]
    body_font_size: float
    heading_font_size_threshold: float
    primary_font_name: str
    total_pages: int


def classify_headers_and_footers(normalized_doc: NormalizedDocument) -> None:
    """
    Non-destructively classifies running headers and footers across pages in NormalizedDocument.
    Sets is_header, is_footer, and header_footer_confidence on blocks and spans.
    """
    pages = normalized_doc.pages
    if len(pages) < 2:
        return

    top_texts: list[str] = []
    bottom_texts: list[str] = []

    for page in pages:
        p_height = page.height or 792.0
        top_limit = p_height * 0.12
        bottom_limit = p_height * 0.88

        for block in page.blocks:
            b_y0 = block.bbox[1]
            b_y1 = block.bbox[3]
            clean_t = block.text.strip().lower()

            if b_y1 <= top_limit and len(clean_t) < 80:
                top_texts.append(clean_t)
            elif b_y0 >= bottom_limit and len(clean_t) < 40:
                bottom_texts.append(clean_t)

    top_counts = Counter(top_texts)
    bottom_counts = Counter(bottom_texts)

    min_repeats = max(2, int(len(pages) * 0.1))
    repeated_top = {txt for txt, count in top_counts.items() if count >= min_repeats}
    repeated_bottom = {txt for txt, count in bottom_counts.items() if count >= min_repeats}

    for page in pages:
        p_height = page.height or 792.0
        top_limit = p_height * 0.12
        bottom_limit = p_height * 0.88

        for block in page.blocks:
            b_y0 = block.bbox[1]
            b_y1 = block.bbox[3]
            stripped = block.text.strip()
            clean_t = stripped.lower()

            is_page_num = stripped.isdigit() and (b_y1 <= top_limit or b_y0 >= bottom_limit)
            is_roman_page_num = (
                clean_t in {"i", "ii", "iii", "iv", "v", "vi", "vii", "viii", "ix", "x"}
                and (b_y1 <= top_limit or b_y0 >= bottom_limit)
            )
            is_rep_top = b_y1 <= top_limit and clean_t in repeated_top
            is_rep_bottom = b_y0 >= bottom_limit and clean_t in repeated_bottom

            if is_rep_top or (b_y1 <= top_limit and (is_page_num or is_roman_page_num)):
                block.is_header = True
                block.header_footer_confidence = 0.95 if is_rep_top else 0.85
                for s in block.spans:
                    s.is_header = True
                    s.header_footer_confidence = block.header_footer_confidence
            elif is_rep_bottom or (b_y0 >= bottom_limit and (is_page_num or is_roman_page_num)):
                block.is_footer = True
                block.header_footer_confidence = 0.95 if is_rep_bottom else 0.85
                for s in block.spans:
                    s.is_footer = True
                    s.header_footer_confidence = block.header_footer_confidence


def _filter_headers_and_footers(pages: list[PageLayout]) -> None:
    """
    Identifies and filters running headers (top 12% of page) and footers (bottom 12% of page)
    that repeat across multiple pages or contain isolated page numbers.
    """
    if len(pages) < 2:
        return

    top_texts: list[str] = []
    bottom_texts: list[str] = []

    for page in pages:
        p_height = page.height or 792.0
        top_limit = p_height * 0.12
        bottom_limit = p_height * 0.88

        for block in page.blocks:
            b_y0 = block.bbox[1]
            b_y1 = block.bbox[3]
            clean_t = block.text.strip().lower()

            if b_y1 <= top_limit and len(clean_t) < 80:
                top_texts.append(clean_t)
            elif b_y0 >= bottom_limit and len(clean_t) < 40:
                bottom_texts.append(clean_t)

    top_counts = Counter(top_texts)
    bottom_counts = Counter(bottom_texts)

    min_repeats = 3 if len(pages) >= 3 else 2
    repeated_top = {txt for txt, count in top_counts.items() if count >= min_repeats}
    repeated_bottom = {txt for txt, count in bottom_counts.items() if count >= min_repeats}

    for page in pages:
        p_height = page.height or 792.0
        top_limit = p_height * 0.12
        bottom_limit = p_height * 0.88

        filtered_blocks = []
        for block in page.blocks:
            b_y0 = block.bbox[1]
            b_y1 = block.bbox[3]
            stripped = block.text.strip()
            clean_t = stripped.lower()

            is_page_num = stripped.isdigit() and (b_y1 <= top_limit or b_y0 >= bottom_limit)
            is_roman_page_num = (
                clean_t in {"i", "ii", "iii", "iv", "v", "vi", "vii", "viii", "ix", "x"}
                and (b_y1 <= top_limit or b_y0 >= bottom_limit)
            )
            is_rep_top = b_y1 <= top_limit and clean_t in repeated_top
            is_rep_bottom = b_y0 >= bottom_limit and clean_t in repeated_bottom

            if is_rep_top or (b_y1 <= top_limit and (is_page_num or is_roman_page_num)):
                block.is_header = True
                block.header_footer_confidence = 0.95
            elif is_rep_bottom or (b_y0 >= bottom_limit and (is_page_num or is_roman_page_num)):
                block.is_footer = True
                block.header_footer_confidence = 0.95
            else:
                filtered_blocks.append(block)

        page.blocks = filtered_blocks
        page.raw_text = "\n\n".join(blk.text for blk in filtered_blocks)


def extract_pdf_layout(doc: Any) -> DocumentLayout:
    """
    Extracts deep layout, typography, and blocks from a PyMuPDF Document instance.
    """
    import fitz

    pages_layout: list[PageLayout] = []
    font_sizes: list[float] = []
    font_names: list[str] = []

    for page_idx in range(len(doc)):
        page = doc[page_idx]
        rect = page.rect
        p_width, p_height = rect.width, rect.height

        page_dict = page.get_text("dict", flags=fitz.TEXT_DEHYPHENATE)
        raw_blocks = page_dict.get("blocks", [])

        layout_blocks: list[LayoutBlock] = []

        for b in raw_blocks:
            if b.get("type") != 0:
                continue

            block_text_lines: list[str] = []
            block_spans: list[TextSpanInfo] = []
            block_sizes: list[float] = []
            bold_count = 0
            total_spans = 0

            for line in b.get("lines", []):
                line_text = ""
                for span in line.get("spans", []):
                    stext = span.get("text", "")
                    if not stext:
                        continue
                    font_size = float(span.get("size", 10.0))
                    font_name = str(span.get("font", ""))
                    flags = int(span.get("flags", 0))
                    is_bold = bool(flags & 16) or ("bold" in font_name.lower()) or ("black" in font_name.lower())
                    is_italic = bool(flags & 2) or ("italic" in font_name.lower()) or ("oblique" in font_name.lower())
                    sbbox = tuple(span.get("bbox", (0, 0, 0, 0)))

                    span_info = TextSpanInfo(
                        text=stext,
                        font_name=font_name,
                        font_size=font_size,
                        flags=flags,
                        is_bold=is_bold,
                        is_italic=is_italic,
                        bbox=sbbox,  # type: ignore
                        page_num=page_idx + 1,
                    )
                    block_spans.append(span_info)
                    line_text += stext
                    font_sizes.append(font_size)
                    font_names.append(font_name)
                    block_sizes.append(font_size)
                    if is_bold:
                        bold_count += 1
                    total_spans += 1

                if line_text.strip():
                    block_text_lines.append(line_text.strip())

            full_block_text = "\n".join(block_text_lines).strip()
            if not full_block_text:
                continue

            avg_size = statistics.mean(block_sizes) if block_sizes else 10.0
            is_bold_block = (bold_count / total_spans >= 0.5) if total_spans else False
            is_caps = full_block_text.isupper() and len(full_block_text) > 3

            layout_blocks.append(
                LayoutBlock(
                    text=full_block_text,
                    spans=block_spans,
                    bbox=tuple(b.get("bbox", (0, 0, 0, 0))),  # type: ignore
                    page_num=page_idx + 1,
                    avg_font_size=avg_size,
                    is_bold=is_bold_block,
                    is_all_caps=is_caps,
                    line_count=len(block_text_lines),
                )
            )

        layout_blocks.sort(key=lambda blk: (round(blk.bbox[1] / 5.0) * 5.0, blk.bbox[0]))
        page_raw_text = "\n\n".join(blk.text for blk in layout_blocks)

        pages_layout.append(
            PageLayout(
                page_num=page_idx + 1,
                width=p_width,
                height=p_height,
                blocks=layout_blocks,
                raw_text=page_raw_text,
            )
        )

    median_body_size = statistics.median(font_sizes) if font_sizes else 10.0
    heading_threshold = median_body_size * 1.12
    primary_font = Counter(font_names).most_common(1)[0][0] if font_names else "Default"

    _filter_headers_and_footers(pages_layout)

    return DocumentLayout(
        pages=pages_layout,
        body_font_size=median_body_size,
        heading_font_size_threshold=heading_threshold,
        primary_font_name=primary_font,
        total_pages=len(pages_layout),
    )


def convert_normalized_doc_to_layout(norm_doc: NormalizedDocument) -> DocumentLayout:
    """Converts a NormalizedDocument to a DocumentLayout for candidate detection."""
    pages_layout: list[PageLayout] = []
    font_sizes: list[float] = []
    font_names: list[str] = []

    for page in norm_doc.pages:
        layout_blocks: list[LayoutBlock] = []
        for b in page.blocks:
            # Skip blocks classified as headers or footers
            if b.is_header or b.is_footer:
                continue

            font_sizes.append(b.avg_font_size)
            if b.primary_font:
                font_names.append(b.primary_font)

            layout_blocks.append(
                LayoutBlock(
                    text=b.text,
                    spans=b.spans,
                    bbox=b.bbox,
                    page_num=page.page_num,
                    avg_font_size=b.avg_font_size,
                    is_bold=b.is_bold,
                    is_all_caps=b.is_all_caps,
                    line_count=b.line_count,
                    is_header=b.is_header,
                    is_footer=b.is_footer,
                    header_footer_confidence=b.header_footer_confidence,
                )
            )

        pages_layout.append(
            PageLayout(
                page_num=page.page_num,
                width=page.width,
                height=page.height,
                blocks=layout_blocks,
                raw_text="\n\n".join(blk.text for blk in layout_blocks),
            )
        )

    median_body = statistics.median(font_sizes) if font_sizes else 10.0
    heading_thresh = median_body * 1.12
    primary_font = Counter(font_names).most_common(1)[0][0] if font_names else "Default"

    return DocumentLayout(
        pages=pages_layout,
        body_font_size=median_body,
        heading_font_size_threshold=heading_thresh,
        primary_font_name=primary_font,
        total_pages=len(pages_layout),
    )
