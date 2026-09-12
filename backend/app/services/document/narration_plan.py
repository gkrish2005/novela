"""
Narration Plan Layer.
Decouples logical document structure (DocumentTree) from audio narration execution.
Determines what nodes are narratable, what is skipped/grouped, and provides backward-compatibility
adapters producing ParsedChapter objects for existing Novela workers and SQLite schemas.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

from app.services.document.models import DocumentNode, DocumentTree, NodeType


@dataclass
class NarrationUnit:
    """A discrete unit intended for voice narration and TTS chunking."""
    id: str
    source_node_id: str
    display_title: str
    raw_title: str
    text: str
    spoken_text: Optional[str] = None
    node_type: NodeType = NodeType.CHAPTER
    page_start: int = 1
    page_end: int = 1
    document_char_start: int = 0
    document_char_end: int = 0
    is_narratable: bool = True
    skip_reason: Optional[str] = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def word_count(self) -> int:
        return len(self.text.split()) if self.text else 0


@dataclass
class NarrationPlan:
    """Complete audio narration execution plan generated from a DocumentTree."""
    units: list[NarrationUnit] = field(default_factory=list)
    skipped_units: list[NarrationUnit] = field(default_factory=list)
    document_title: str = ""
    author: Optional[str] = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def total_words(self) -> int:
        return sum(u.word_count for u in self.units)

    @property
    def estimated_duration_minutes(self) -> float:
        # Assuming ~150 words per minute average speaking rate
        return round(self.total_words / 150.0, 1)

    def to_parsed_chapters(self) -> list[Any]:
        """
        Backward compatibility adapter: converts narratable units into ParsedChapter
        objects required by Novela's existing SQLite schema and narration workers.
        """
        from app.services.parser import ParsedChapter

        chapters: list[ParsedChapter] = []
        for unit in self.units:
            if not unit.is_narratable or not unit.text.strip():
                continue

            chapters.append(
                ParsedChapter(
                    title=unit.display_title,
                    text=unit.text.strip(),
                )
            )

        if not chapters and self.document_title:
            # Fallback if nothing was marked narratable but text existed
            chapters.append(ParsedChapter(title="Chapter 1", text=self.document_title))

        return chapters


class NarrationPlanBuilder:
    """Builds an optimized NarrationPlan from a DocumentTree."""

    NON_NARRATABLE_TYPES = {
        NodeType.TABLE_OF_CONTENTS,
        NodeType.TITLE_PAGE,
    }

    @classmethod
    def build_from_tree(cls, tree: DocumentTree) -> NarrationPlan:
        units: list[NarrationUnit] = []
        skipped: list[NarrationUnit] = []

        def _walk_tree(node: DocumentNode, path_titles: list[str]) -> None:
            current_path = path_titles.copy()
            if node.node_type not in (NodeType.DOCUMENT, NodeType.UNKNOWN):
                if node.title and node.title not in current_path:
                    current_path.append(node.title)

            # Check if this node has direct text content
            if node.text.strip():
                display_title = " - ".join(current_path) if current_path else (node.title or f"Section {len(units) + 1}")

                # Determine if node should be narrated
                is_narratable = True
                skip_reason = None

                if node.node_type in cls.NON_NARRATABLE_TYPES:
                    is_narratable = False
                    skip_reason = f"Node type {node.node_type.value} marked non-narratable"
                elif len(node.text.strip()) < 10 and not node.children:
                    is_narratable = False
                    skip_reason = "Insufficient text length (< 10 chars)"

                unit = NarrationUnit(
                    id=f"unit_{len(units) + len(skipped) + 1}",
                    source_node_id=node.id,
                    display_title=display_title,
                    raw_title=node.title,
                    text=node.text.strip(),
                    spoken_text=node.spoken_text,
                    node_type=node.node_type,
                    page_start=node.page_start,
                    page_end=node.page_end,
                    document_char_start=node.document_char_start,
                    document_char_end=node.document_char_end,
                    is_narratable=is_narratable,
                    skip_reason=skip_reason,
                    metadata={"confidence": node.confidence, "detection_method": node.detection_method},
                )

                if is_narratable:
                    units.append(unit)
                else:
                    skipped.append(unit)

            for child in node.children:
                _walk_tree(child, current_path)

        _walk_tree(tree.root, [])

        # Fallback if no nodes produced text but root has text
        if not units and tree.root.text.strip():
            root_unit = NarrationUnit(
                id="unit_1",
                source_node_id=tree.root.id,
                display_title="Chapter 1",
                raw_title="Chapter 1",
                text=tree.root.text.strip(),
                page_start=tree.root.page_start,
                page_end=tree.root.page_end,
                document_char_start=tree.root.document_char_start,
                document_char_end=tree.root.document_char_end,
                is_narratable=True,
            )
            units.append(root_unit)

        return NarrationPlan(
            units=units,
            skipped_units=skipped,
            document_title=tree.title,
            author=tree.author,
            metadata=tree.metadata,
        )
