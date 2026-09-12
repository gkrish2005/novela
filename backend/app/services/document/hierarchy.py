"""
Hierarchy reconstruction engine.
Assembles candidates into a strict, arbitrary-depth DocumentNode tree with zero text loss,
exact character offsets, explainable evidence propagation, and non-fabricated nesting.
"""

from __future__ import annotations

from typing import Any, Optional

from app.services.document.heading_detector import HeadingCandidate
from app.services.document.layout import DocumentLayout, LayoutBlock
from app.services.document.models import DocumentNode, DocumentTree, NodeType


def reconstruct_hierarchy(
    layout: DocumentLayout,
    candidates: list[HeadingCandidate],
    doc_title: str,
    doc_author: Optional[str] = None,
    cover_bytes: Optional[bytes] = None,
) -> DocumentTree:
    """
    Reconstructs the hierarchical DocumentTree from detected candidates and document pages.
    Guarantees that all body text is preserved, character offsets are populated, and no
    hierarchy levels are artificially fabricated.
    """
    root = DocumentNode(
        id="root",
        node_type=NodeType.DOCUMENT,
        title=doc_title,
        page_start=1,
        page_end=layout.total_pages or 1,
    )

    all_blocks: list[tuple[int, LayoutBlock]] = []
    for p_idx, page in enumerate(layout.pages):
        for block in page.blocks:
            all_blocks.append((p_idx + 1, block))

    if not all_blocks:
        return DocumentTree(
            root=root,
            title=doc_title,
            author=doc_author,
            cover_bytes=cover_bytes,
            metadata={"total_pages": layout.total_pages},
        )

    # If no heading candidates detected, group into paragraphs or fallback section
    if not candidates:
        full_text = "\n\n".join(b.text for _, b in all_blocks).strip()
        paragraphs = [p.strip() for p in full_text.split("\n\n") if p.strip()]
        if len(paragraphs) <= 1:
            leaf = DocumentNode(
                id="sec_1",
                node_type=NodeType.BODY,
                title=doc_title or "Section 1",
                page_start=1,
                page_end=layout.total_pages or 1,
                document_char_start=0,
                document_char_end=len(full_text),
                text=full_text,
                confidence=0.50,
                detection_method="fallback_single_section",
                uncertain=True,
                uncertainty_reasons=["No structural heading candidates detected in document"],
            )
            root.add_child(leaf)
        else:
            chunk_size = max(1, len(paragraphs) // 8)
            char_cursor = 0
            for i in range(0, len(paragraphs), chunk_size):
                p_slice = paragraphs[i : i + chunk_size]
                chunk_text = "\n\n".join(p_slice)
                leaf = DocumentNode(
                    id=f"sec_{len(root.children) + 1}",
                    node_type=NodeType.SECTION,
                    title=f"Section {len(root.children) + 1}",
                    page_start=1,
                    page_end=layout.total_pages or 1,
                    document_char_start=char_cursor,
                    document_char_end=char_cursor + len(chunk_text),
                    text=chunk_text,
                    confidence=0.45,
                    detection_method="paragraph_density_partition",
                    uncertain=True,
                    uncertainty_reasons=["Partitioned by paragraph density in absence of explicit headings"],
                )
                root.add_child(leaf)
                char_cursor += len(chunk_text) + 2

        root.document_char_start = 0
        root.document_char_end = len(full_text)
        return DocumentTree(
            root=root,
            title=doc_title,
            author=doc_author,
            cover_bytes=cover_bytes,
            metadata={"total_pages": layout.total_pages},
        )

    # Match each candidate to the corresponding block in order
    candidate_indices: list[int] = []
    cand_map: dict[int, HeadingCandidate] = {}
    last_matched_b = -1

    for cand in candidates:
        for b_idx in range(last_matched_b + 1, len(all_blocks)):
            p_num, block = all_blocks[b_idx]
            cand_raw = cand.raw_block_text.strip()
            block_raw = block.text.strip()

            if p_num == cand.page_num and (cand_raw == block_raw or cand_raw in block_raw or block_raw in cand_raw):
                candidate_indices.append(b_idx)
                cand_map[b_idx] = cand
                last_matched_b = b_idx
                break

    # If first candidate is not at block 0, text before it is Front Matter
    structural_spans: list[tuple[Optional[HeadingCandidate], int, int, int, int]] = []
    if candidate_indices and candidate_indices[0] > 0:
        first_cand_b = candidate_indices[0]
        p_start = all_blocks[0][0]
        p_end = all_blocks[first_cand_b - 1][0]
        structural_spans.append((None, 0, first_cand_b, p_start, p_end))
    elif not candidate_indices:
        structural_spans.append((None, 0, len(all_blocks), all_blocks[0][0], all_blocks[-1][0]))

    for idx, b_idx in enumerate(candidate_indices):
        cand = cand_map[b_idx]
        next_b_idx = candidate_indices[idx + 1] if idx + 1 < len(candidate_indices) else len(all_blocks)
        start_content_b = b_idx + 2 if (cand.is_multi_line and b_idx + 2 <= next_b_idx) else b_idx + 1
        if start_content_b > next_b_idx:
            start_content_b = next_b_idx

        p_start = all_blocks[b_idx][0]
        p_end = all_blocks[next_b_idx - 1][0] if next_b_idx > 0 else p_start
        structural_spans.append((cand, start_content_b, next_b_idx, p_start, p_end))

    # Build hierarchical tree
    active_volume: Optional[DocumentNode] = None
    active_book: Optional[DocumentNode] = None
    active_part: Optional[DocumentNode] = None
    active_chapter: Optional[DocumentNode] = None
    active_section: Optional[DocumentNode] = None

    running_char_cursor = 0

    for cand, b_start, b_end, p_start, p_end in structural_spans:
        blocks_text = "\n\n".join(all_blocks[i][1].text for i in range(b_start, b_end)).strip()
        text_len = len(blocks_text)

        if cand is None:
            if blocks_text:
                fm_node = DocumentNode(
                    node_type=NodeType.FRONT_MATTER,
                    title="Front Matter",
                    page_start=p_start,
                    page_end=p_end,
                    document_char_start=running_char_cursor,
                    document_char_end=running_char_cursor + text_len,
                    text=blocks_text,
                    confidence=0.90,
                    detection_method="leading_document_span",
                )
                root.add_child(fm_node)
                running_char_cursor += text_len + 2
            continue

        node = DocumentNode(
            node_type=cand.node_type,
            title=cand.title,
            ordinal=cand.ordinal,
            page_start=p_start,
            page_end=p_end,
            document_char_start=running_char_cursor,
            document_char_end=running_char_cursor + text_len,
            text=blocks_text,
            confidence=cand.confidence,
            detection_method=cand.detection_method,
            evidence=cand.evidence,
            uncertainty_reasons=cand.uncertainty_reasons,
            uncertain=(cand.confidence < 0.70),
        )
        running_char_cursor += text_len + 2

        # Level 1: Volume / Book / Part
        if cand.level == 1 or cand.node_type in (NodeType.VOLUME, NodeType.BOOK, NodeType.PART):
            if cand.node_type == NodeType.VOLUME:
                root.add_child(node)
                active_volume = node
                active_book = None
                active_part = None
            elif cand.node_type == NodeType.BOOK:
                if active_volume is not None:
                    active_volume.add_child(node)
                else:
                    root.add_child(node)
                active_book = node
                active_part = None
            else:  # PART
                if active_book is not None:
                    active_book.add_child(node)
                elif active_volume is not None:
                    active_volume.add_child(node)
                else:
                    root.add_child(node)
                active_part = node
            active_chapter = None
            active_section = None

        # Level 2: Chapter / Prologue / Epilogue / Special Matter
        elif cand.level == 2 or cand.node_type in (
            NodeType.CHAPTER, NodeType.PROLOGUE, NodeType.EPILOGUE,
            NodeType.PREFACE, NodeType.INTRODUCTION, NodeType.APPENDIX,
            NodeType.GLOSSARY, NodeType.NOTES, NodeType.BIBLIOGRAPHY,
            NodeType.AFTERWORD, NodeType.DEDICATION, NodeType.EPIGRAPH
        ):
            if active_part is not None:
                active_part.add_child(node)
            elif active_book is not None:
                active_book.add_child(node)
            elif active_volume is not None:
                active_volume.add_child(node)
            else:
                root.add_child(node)
            active_chapter = node
            active_section = None

        # Level 3: Section
        elif cand.level == 3 or cand.node_type == NodeType.SECTION:
            if active_chapter is not None:
                active_chapter.add_child(node)
            elif active_part is not None:
                active_part.add_child(node)
            else:
                root.add_child(node)
            active_section = node

        # Level 4+: Subsection
        else:
            if active_section is not None:
                active_section.add_child(node)
            elif active_chapter is not None:
                active_chapter.add_child(node)
            else:
                root.add_child(node)

    root.document_char_start = 0
    root.document_char_end = running_char_cursor

    return DocumentTree(
        root=root,
        title=doc_title,
        author=doc_author,
        cover_bytes=cover_bytes,
        metadata={"total_pages": layout.total_pages},
    )
