"""
Unified Document Structure Understanding Engine.
Main entry point for analyzing, structuring, validating, and generating narration plans for arbitrary documents.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Optional, Union

from app.services.document.extractors import (
    DOCXExtractor,
    EPUBExtractor,
    MarkdownExtractor,
    PDFExtractor,
    TXTExtractor,
    get_extractor,
)
from app.services.document.heading_detector import (
    CHAPTER_PATTERNS,
    FRONT_BACK_MATTER_PATTERNS,
    NUMBERED_SECTION_PATTERNS,
    PART_PATTERNS,
    VOLUME_BOOK_PATTERNS,
    detect_candidate_headings,
    is_dialogue_or_quote,
)
from app.services.document.hierarchy import reconstruct_hierarchy
from app.services.document.layout import (
    DocumentLayout,
    LayoutBlock,
    PageLayout,
    classify_headers_and_footers,
    convert_normalized_doc_to_layout,
    extract_pdf_layout,
)
from app.services.document.models import DocumentTree, NormalizedDocument
from app.services.document.narration_plan import NarrationPlan, NarrationPlanBuilder
from app.services.document.parser_utils import clean_text_segment
from app.services.document.toc import (
    ParsedTOC,
    TOCEntry,
    detect_printed_toc,
    extract_native_toc,
    reconcile_toc_with_candidates,
)
from app.services.document.validator import validate_document_tree


def _is_probable_heading_line(line: str) -> bool:
    """Fast check if a line is a candidate heading."""
    stripped = line.strip()
    if not stripped or len(stripped) > 120:
        return False
    if is_dialogue_or_quote(stripped):
        return False

    for pat in VOLUME_BOOK_PATTERNS + PART_PATTERNS + CHAPTER_PATTERNS + NUMBERED_SECTION_PATTERNS:
        if pat.match(stripped):
            return True
    for pat, _, _ in FRONT_BACK_MATTER_PATTERNS:
        if pat.match(stripped):
            return True

    if re.match(r"^\s*(?:TABLE OF CONTENTS|CONTENTS|INDEX|अनुक्रमणिका)\s*$", stripped, re.IGNORECASE):
        return True

    return False


class DocumentStructureEngine:
    """
    Universal document structure engine capable of ingesting PDF, TXT, Markdown, EPUB, and DOCX.
    Orchestrates layout analysis, TOC extraction, multi-signal heading detection,
    hierarchy assembly, zero-loss validation, and narration plan generation.
    """

    @classmethod
    def parse_file(cls, path: Union[str, Path]) -> DocumentTree:
        """Parses any supported document format by automatically routing to its extractor."""
        p = Path(path)
        ext = p.suffix.lower()
        if ext == ".pdf":
            return cls.parse_pdf(p)
        elif ext in (".epub",):
            return cls.parse_epub(p)
        elif ext in (".docx",):
            return cls.parse_docx(p)
        elif ext in (".md", ".markdown"):
            return cls.parse_markdown(p.read_text(encoding="utf-8", errors="replace"), p.stem)
        else:
            return cls.parse_text_stream(p.read_text(encoding="utf-8", errors="replace"), p.stem)

    @classmethod
    def parse_pdf(cls, path: Path) -> DocumentTree:
        """Layout-aware PDF parsing with typography, native bookmarks, printed TOC, and validation."""
        extractor = PDFExtractor()
        norm_doc = extractor.extract(path)

        # 1. Non-destructive statistical header/footer classification
        classify_headers_and_footers(norm_doc)

        # 2. Convert NormalizedDocument to layout for candidate analysis
        layout = convert_normalized_doc_to_layout(norm_doc)

        # 3. Extract TOC (Native bookmarks + Printed TOC pages)
        toc: Optional[ParsedTOC] = None
        if norm_doc.toc_entries:
            parsed_entries = [
                TOCEntry(level=e.level, title=e.title, page=e.page_num, source=e.source)
                for e in norm_doc.toc_entries
            ]
            toc = ParsedTOC(entries=parsed_entries, has_native_outline=True)
        else:
            toc = detect_printed_toc(layout.pages)

        # 4. Detect candidate headings via multi-signal analysis
        candidates = detect_candidate_headings(layout, toc=toc)

        # 5. Reconcile TOC against candidates
        if toc:
            reconcile_report = reconcile_toc_with_candidates(toc, candidates, total_pages=layout.total_pages)
            norm_doc.metadata["toc_reconciliation"] = reconcile_report

        # 6. Reconstruct universal hierarchy
        tree = reconstruct_hierarchy(
            layout=layout,
            candidates=candidates,
            doc_title=norm_doc.title,
            doc_author=norm_doc.author,
            cover_bytes=norm_doc.cover_bytes,
        )

        # 7. Zero-loss validation
        raw_char_count = sum(len(p.raw_text) for p in norm_doc.pages)
        raw_full = "\n\n".join(p.raw_text for p in layout.pages)
        report = validate_document_tree(tree, raw_text=raw_full)
        tree.metadata["total_pages"] = layout.total_pages
        tree.metadata["raw_char_count"] = raw_char_count
        tree.metadata["validation"] = {
            "is_valid": report.is_valid,
            "errors": report.errors,
            "warnings": report.warnings,
            "leaf_nodes": report.leaf_nodes,
            "text_loss_rate": report.text_loss_rate,
            "text_duplication_rate": report.text_duplication_rate,
            "raw_char_count": raw_char_count,
        }

        return tree

    @classmethod
    def parse_epub(cls, path: Path) -> DocumentTree:
        """Parses EPUB file preserving spine order, HTML heading semantics, and TOC."""
        extractor = EPUBExtractor()
        norm_doc = extractor.extract(path)
        classify_headers_and_footers(norm_doc)
        layout = convert_normalized_doc_to_layout(norm_doc)

        toc = None
        if norm_doc.toc_entries:
            parsed_entries = [
                TOCEntry(level=e.level, title=e.title, page=e.page_num, source=e.source)
                for e in norm_doc.toc_entries
            ]
            toc = ParsedTOC(entries=parsed_entries, has_native_outline=True)

        candidates = detect_candidate_headings(layout, toc=toc)
        tree = reconstruct_hierarchy(
            layout=layout,
            candidates=candidates,
            doc_title=norm_doc.title,
            doc_author=norm_doc.author,
            cover_bytes=norm_doc.cover_bytes,
        )

        report = validate_document_tree(tree, raw_text=norm_doc.raw_text)
        tree.metadata["validation"] = {
            "is_valid": report.is_valid,
            "errors": report.errors,
            "warnings": report.warnings,
        }
        return tree

    @classmethod
    def parse_docx(cls, path: Path) -> DocumentTree:
        """Parses DOCX document preserving Word heading styles and run formatting."""
        extractor = DOCXExtractor()
        norm_doc = extractor.extract(path)
        layout = convert_normalized_doc_to_layout(norm_doc)

        toc = None
        if norm_doc.toc_entries:
            parsed_entries = [
                TOCEntry(level=e.level, title=e.title, page=e.page_num, source=e.source)
                for e in norm_doc.toc_entries
            ]
            toc = ParsedTOC(entries=parsed_entries, has_native_outline=True)

        candidates = detect_candidate_headings(layout, toc=toc)
        tree = reconstruct_hierarchy(
            layout=layout,
            candidates=candidates,
            doc_title=norm_doc.title,
            doc_author=norm_doc.author,
        )

        report = validate_document_tree(tree, raw_text=norm_doc.raw_text)
        tree.metadata["validation"] = {
            "is_valid": report.is_valid,
            "errors": report.errors,
            "warnings": report.warnings,
        }
        return tree

    @classmethod
    def parse_markdown(cls, text: str, doc_title: str) -> DocumentTree:
        """Parses Markdown document preserving header levels and paragraph blocks."""
        extractor = MarkdownExtractor()
        norm_doc = extractor.extract(text, title_hint=doc_title)
        layout = convert_normalized_doc_to_layout(norm_doc)

        toc = None
        if norm_doc.toc_entries:
            parsed_entries = [
                TOCEntry(level=e.level, title=e.title, page=e.page_num, source=e.source)
                for e in norm_doc.toc_entries
            ]
            toc = ParsedTOC(entries=parsed_entries, has_native_outline=True)

        candidates = detect_candidate_headings(layout, toc=toc)
        tree = reconstruct_hierarchy(
            layout=layout,
            candidates=candidates,
            doc_title=norm_doc.title,
        )

        report = validate_document_tree(tree, raw_text=norm_doc.raw_text)
        tree.metadata["validation"] = {
            "is_valid": report.is_valid,
            "errors": report.errors,
            "warnings": report.warnings,
        }
        return tree

    @classmethod
    def parse_text_stream(cls, text: str, doc_title: str) -> DocumentTree:
        """
        Parses plain text streams constructing virtual layout pages and structured blocks.
        Accurately separates candidate heading lines from multi-line paragraph bodies.
        """
        cleaned = clean_text_segment(text)
        paragraphs = [p.strip() for p in cleaned.split("\n\n") if p.strip()]

        blocks: list[LayoutBlock] = []

        for p in paragraphs:
            lines = [l.strip() for l in p.split("\n") if l.strip()]
            if not lines:
                continue

            # Process consecutive leading heading lines
            l_idx = 0
            while l_idx < len(lines) and _is_probable_heading_line(lines[l_idx]):
                h_line = lines[l_idx]
                is_caps = h_line.isupper()
                blocks.append(
                    LayoutBlock(
                        text=h_line,
                        spans=[],
                        bbox=(0, 0, 100, 100),
                        page_num=1,
                        avg_font_size=14.0,
                        is_bold=True,
                        is_all_caps=is_caps,
                        line_count=1,
                    )
                )
                l_idx += 1

                # Check if next line is title continuation (and not itself a heading pattern)
                if (
                    l_idx < len(lines)
                    and len(lines[l_idx]) <= 60
                    and not lines[l_idx].endswith(".")
                    and not is_dialogue_or_quote(lines[l_idx])
                    and (lines[l_idx].isupper() or lines[l_idx].istitle())
                    and not _is_probable_heading_line(lines[l_idx])
                ):
                    blocks.append(
                        LayoutBlock(
                            text=lines[l_idx],
                            spans=[],
                            bbox=(0, 0, 100, 100),
                            page_num=1,
                            avg_font_size=13.0,
                            is_bold=True,
                            is_all_caps=lines[l_idx].isupper(),
                            line_count=1,
                        )
                    )
                    l_idx += 1

            # Remaining lines in this paragraph belong to body
            if l_idx < len(lines):
                rem_text = "\n".join(lines[l_idx:])
                blocks.append(
                    LayoutBlock(
                        text=rem_text,
                        spans=[],
                        bbox=(0, 0, 100, 100),
                        page_num=1,
                        avg_font_size=10.0,
                        is_bold=False,
                        is_all_caps=False,
                        line_count=len(lines) - l_idx,
                    )
                )

        page_layout = PageLayout(
            page_num=1,
            width=612,
            height=792,
            blocks=blocks,
            raw_text=cleaned,
        )

        layout = DocumentLayout(
            pages=[page_layout],
            body_font_size=10.0,
            heading_font_size_threshold=12.0,
            primary_font_name="Default",
            total_pages=1,
        )

        toc = detect_printed_toc([page_layout])
        candidates = detect_candidate_headings(layout, toc=toc)

        tree = reconstruct_hierarchy(
            layout=layout,
            candidates=candidates,
            doc_title=doc_title,
        )

        report = validate_document_tree(tree, raw_text=cleaned)
        tree.metadata["validation"] = {
            "is_valid": report.is_valid,
            "errors": report.errors,
            "warnings": report.warnings,
        }

        return tree

    @classmethod
    def create_narration_plan(cls, tree: DocumentTree) -> NarrationPlan:
        """Builds a NarrationPlan from a DocumentTree."""
        return NarrationPlanBuilder.build_from_tree(tree)
