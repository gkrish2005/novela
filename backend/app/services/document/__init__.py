"""
Universal Document Structure Understanding Package for Novela.
"""

from app.services.document.engine import DocumentStructureEngine
from app.services.document.heading_detector import HeadingCandidate, detect_candidate_headings
from app.services.document.models import (
    DocumentBlock,
    DocumentLine,
    DocumentNode,
    DocumentPage,
    DocumentSpan,
    DocumentTree,
    NodeType,
    NormalizedDocument,
    TOCEntry,
)
from app.services.document.narration_plan import (
    NarrationPlan,
    NarrationPlanBuilder,
    NarrationUnit,
)
from app.services.document.validator import ValidationReport, validate_document_tree

__all__ = [
    "DocumentStructureEngine",
    "DocumentTree",
    "DocumentNode",
    "NodeType",
    "NormalizedDocument",
    "DocumentPage",
    "DocumentBlock",
    "DocumentLine",
    "DocumentSpan",
    "TOCEntry",
    "NarrationPlan",
    "NarrationUnit",
    "NarrationPlanBuilder",
    "HeadingCandidate",
    "detect_candidate_headings",
    "ValidationReport",
    "validate_document_tree",
]
