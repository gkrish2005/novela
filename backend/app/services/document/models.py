"""
Universal Document Representation — supports arbitrary nesting, rich metadata,
stable character offsets, layout features, and explainable confidence scoring.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


class NodeType(str, Enum):
    DOCUMENT = "document"
    VOLUME = "volume"
    BOOK = "book"
    PART = "part"
    CHAPTER = "chapter"
    SECTION = "section"
    SUBSECTION = "subsection"
    FRONT_MATTER = "front_matter"
    TITLE_PAGE = "title_page"
    DEDICATION = "dedication"
    EPIGRAPH = "epigraph"
    PREFACE = "preface"
    INTRODUCTION = "introduction"
    TABLE_OF_CONTENTS = "table_of_contents"
    PROLOGUE = "prologue"
    EPILOGUE = "epilogue"
    APPENDIX = "appendix"
    GLOSSARY = "glossary"
    NOTES = "notes"
    BIBLIOGRAPHY = "bibliography"
    AFTERWORD = "afterword"
    BACK_MATTER = "back_matter"
    BODY = "body"
    UNKNOWN = "unknown"


@dataclass
class DocumentSpan:
    """A granular span of text with character offsets and layout/typography metadata."""
    text: str
    doc_char_start: int = 0
    doc_char_end: int = 0
    page_char_start: int = 0
    page_char_end: int = 0
    page_start: int = 1
    page_end: int = 1
    bbox: tuple[float, float, float, float] = (0.0, 0.0, 0.0, 0.0)
    font_name: str = "Default"
    font_size: float = 10.0
    flags: int = 0
    is_bold: bool = False
    is_italic: bool = False
    is_all_caps: bool = False
    is_header: bool = False
    is_footer: bool = False
    header_footer_confidence: float = 0.0


@dataclass
class DocumentLine:
    """A single line of text consisting of one or more spans."""
    spans: list[DocumentSpan] = field(default_factory=list)
    bbox: tuple[float, float, float, float] = (0.0, 0.0, 0.0, 0.0)
    text: str = ""
    doc_char_start: int = 0
    doc_char_end: int = 0


@dataclass
class DocumentBlock:
    """A visual or logical block of lines within a document page/unit."""
    text: str
    spans: list[DocumentSpan] = field(default_factory=list)
    lines: list[DocumentLine] = field(default_factory=list)
    bbox: tuple[float, float, float, float] = (0.0, 0.0, 0.0, 0.0)
    page_num: int = 1
    avg_font_size: float = 10.0
    primary_font: str = "Default"
    is_bold: bool = False
    is_italic: bool = False
    is_all_caps: bool = False
    line_count: int = 1
    doc_char_start: int = 0
    doc_char_end: int = 0
    is_header: bool = False
    is_footer: bool = False
    header_footer_confidence: float = 0.0


@dataclass
class DocumentPage:
    """A page (or discrete unit for pageless sources) containing blocks and text."""
    page_num: int
    width: float = 612.0
    height: float = 792.0
    blocks: list[DocumentBlock] = field(default_factory=list)
    raw_text: str = ""
    doc_char_start: int = 0
    doc_char_end: int = 0


@dataclass
class TOCEntry:
    """Represents a table of contents entry extracted from native bookmarks or printed TOC."""
    title: str
    level: int = 1
    page_num: Optional[int] = None
    target_dest: Optional[str] = None
    ordinal: Optional[int] = None
    source: str = "native"  # "native" or "printed"


@dataclass
class NormalizedDocument:
    """
    Source-independent normalized document representation.
    Preserves raw text, layout metadata, stable character offsets, and TOC information.
    """
    document_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    source_type: str = "pdf"  # pdf, txt, markdown, epub, docx
    source_path: Optional[str] = None
    title: str = ""
    author: Optional[str] = None
    pages: list[DocumentPage] = field(default_factory=list)
    raw_text: str = ""
    normalized_text: str = ""
    toc_entries: list[TOCEntry] = field(default_factory=list)
    cover_bytes: Optional[bytes] = None
    metadata: dict[str, Any] = field(default_factory=dict)
    extraction_warnings: list[str] = field(default_factory=list)
    quality_score: float = 1.0  # 1.0 = clean, 0.0 = completely degraded/failed OCR

    def format_debug_view(self) -> str:
        """Outputs an observability string representing pages, blocks, headers/footers."""
        lines = [f"=== NormalizedDocument [{self.source_type.upper()}] id={self.document_id} title='{self.title}' ==="]
        for page in self.pages:
            lines.append(f"\n--- PAGE {page.page_num} (chars: {page.doc_char_start}..{page.doc_char_end}) ---")
            for b in page.blocks:
                tag = "BODY"
                if b.is_header:
                    tag = f"HEADER conf={b.header_footer_confidence:.2f}"
                elif b.is_footer:
                    tag = f"FOOTER conf={b.header_footer_confidence:.2f}"
                elif b.is_bold and b.avg_font_size > 11.0:
                    tag = f"CANDIDATE_HEADING size={b.avg_font_size:.1f}"

                preview = b.text.replace("\n", " ")[:80]
                if len(b.text) > 80:
                    preview += "..."
                lines.append(f"[{tag}] {preview}")
        return "\n".join(lines)


@dataclass
class DocumentNode:
    """A node in the universal hierarchical DocumentTree."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    parent_id: Optional[str] = None
    node_type: NodeType = NodeType.UNKNOWN
    title: str = ""
    ordinal: Optional[int] = None
    page_start: int = 1
    page_end: int = 1
    document_char_start: int = 0
    document_char_end: int = 0
    text: str = ""
    spoken_text: Optional[str] = None
    confidence: float = 1.0
    detection_method: str = "heuristic"
    evidence: dict[str, Any] = field(default_factory=dict)
    numbering_metadata: dict[str, Any] = field(default_factory=dict)
    uncertain: bool = False
    uncertainty_reasons: list[str] = field(default_factory=list)
    children: list[DocumentNode] = field(default_factory=list)

    def add_child(self, child: DocumentNode) -> None:
        child.parent_id = self.id
        self.children.append(child)

    def is_leaf(self) -> bool:
        return len(self.children) == 0

    def get_all_descendants(self) -> list[DocumentNode]:
        nodes = []
        for child in self.children:
            nodes.append(child)
            nodes.extend(child.get_all_descendants())
        return nodes

    def total_text_length(self) -> int:
        direct = len(self.text)
        children_text = sum(child.total_text_length() for child in self.children)
        return direct + children_text


@dataclass
class DocumentTree:
    """Universal hierarchical representation of an ingested document."""
    root: DocumentNode
    title: str
    author: Optional[str] = None
    cover_bytes: Optional[bytes] = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_narratable_chapters(self) -> list[Any]:
        """
        Backward compatibility adapter: delegates to NarrationPlan to produce
        ordered ParsedChapter objects for existing Novela workers and SQLite schemas.
        """
        from app.services.document.narration_plan import NarrationPlanBuilder
        plan = NarrationPlanBuilder.build_from_tree(self)
        return plan.to_parsed_chapters()

    def format_tree_debug(self, indent: int = 0) -> str:
        """Observability string showing full hierarchical document tree."""
        def _render_node(node: DocumentNode, level: int) -> list[str]:
            prefix = "  " * level + "├── " if level > 0 else ""
            conf_str = f" [conf={node.confidence:.2f}]" if node.confidence < 1.0 else ""
            uncertain_str = " (UNCERTAIN)" if node.uncertain else ""
            char_range = f" ({node.document_char_start}..{node.document_char_end})"
            line = f"{prefix}{node.node_type.value.upper()}: '{node.title}'{conf_str}{uncertain_str}{char_range}"
            out = [line]
            for child in node.children:
                out.extend(_render_node(child, level + 1))
            return out

        return "\n".join(_render_node(self.root, 0))
