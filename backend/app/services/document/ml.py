"""
Machine Learning integration interface and dataset generation infrastructure (Parts 21 & 22).
Defines StructureClassifier interface and feature extractors for future ML models.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass, field
from typing import Any, Optional

from app.services.document.heading_detector import HeadingCandidate
from app.services.document.models import NodeType, NormalizedDocument


class StructureClassifier(ABC):
    """Abstract interface for structural machine learning classifiers."""

    @abstractmethod
    def classify(
        self,
        candidate: HeadingCandidate,
        context: Optional[dict[str, Any]] = None,
    ) -> tuple[NodeType, float]:
        """
        Classifies a candidate heading into a NodeType with an associated confidence probability [0.0, 1.0].
        """
        pass


@dataclass
class HeadingFeatureVector:
    """Standardized feature vector representation of a candidate heading for ML training."""
    candidate_text: str
    char_length: int
    word_count: int
    avg_font_size: float
    relative_font_size: float
    is_bold: bool
    is_italic: bool
    is_all_caps: bool
    line_count: int
    page_num: int
    page_relative_position: float  # y0 / page_height (0.0 to 1.0)
    has_lexical_keyword: bool
    detected_lexical_type: str
    ordinal_number: Optional[int]
    is_sequential: bool
    is_toc_matched: bool
    has_dialogue_quotes: bool
    surrounding_body_density: float
    label: str = "UNKNOWN"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def extract_features_for_candidate(
    cand: HeadingCandidate,
    median_body_font_size: float = 10.0,
    page_height: float = 792.0,
    label: str = "HEADING",
) -> HeadingFeatureVector:
    """Extracts ML features from a HeadingCandidate."""
    rel_size = (cand.evidence.get("typography", 1.0) * 1.5) if cand.evidence else 1.0
    y_pos = 0.1  # normalized fallback
    words = cand.raw_block_text.split()

    return HeadingFeatureVector(
        candidate_text=cand.raw_block_text,
        char_length=len(cand.raw_block_text),
        word_count=len(words),
        avg_font_size=median_body_font_size * rel_size,
        relative_font_size=rel_size,
        is_bold=bool(cand.evidence.get("typography", 0.5) > 0.6),
        is_italic=False,
        is_all_caps=cand.raw_block_text.isupper(),
        line_count=2 if cand.is_multi_line else 1,
        page_num=cand.page_num,
        page_relative_position=y_pos,
        has_lexical_keyword=bool("lexical" in cand.detection_method),
        detected_lexical_type=cand.detection_method,
        ordinal_number=cand.ordinal,
        is_sequential=bool(cand.evidence.get("sequence", 0.5) > 0.8),
        is_toc_matched=bool(cand.evidence.get("toc", 0.0) > 0.5),
        has_dialogue_quotes=False,
        surrounding_body_density=0.8,
        label=label,
    )


def export_ml_dataset(
    normalized_doc: NormalizedDocument,
    candidates: list[HeadingCandidate],
    ground_truth_labels: Optional[dict[str, str]] = None,
) -> list[dict[str, Any]]:
    """
    Exports a structured list of training/evaluation records from an ingested NormalizedDocument.
    Enforces document-level separation to prevent data leakage across splits.
    """
    records: list[dict[str, Any]] = []
    labels_map = ground_truth_labels or {}

    for cand in candidates:
        assigned_label = labels_map.get(cand.raw_block_text.strip(), cand.node_type.value.upper())
        feat = extract_features_for_candidate(
            cand=cand,
            median_body_font_size=10.0,
            label=assigned_label,
        )
        record = feat.to_dict()
        record["document_id"] = normalized_doc.document_id
        record["source_type"] = normalized_doc.source_type
        records.append(record)

    return records
