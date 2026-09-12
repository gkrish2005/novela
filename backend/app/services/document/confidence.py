"""
Confidence calculation and explainability scoring for document structure elements.
Computes a bounded, documented composite score and preserves detailed evidence subscores.
"""

from __future__ import annotations

from typing import Any, Optional


def compute_node_confidence(
    detection_method: str,
    has_font_elevation: bool = False,
    has_bold: bool = False,
    is_toc_matched: bool = False,
    is_ordinal_sequential: bool = False,
    word_count: int = 0,
    is_multi_line: bool = False,
    is_centered: bool = False,
    has_space_around: bool = False,
    is_dialogue_suspect: bool = False,
    ocr_quality: float = 1.0,
) -> tuple[float, dict[str, float], list[str], list[str]]:
    """
    Computes a composite confidence score [0.0, 1.0], a detailed breakdown of evidence subscores,
    an explainable factor list, and a list of uncertainty reasons if ambiguous.
    """
    evidence: dict[str, float] = {
        "typography": 0.50,
        "geometry": 0.50,
        "lexical": 0.50,
        "numbering": 0.50,
        "sequence": 0.50,
        "toc": 0.0,
        "penalties": 0.0,
    }
    factors: list[str] = []
    uncertainty_reasons: list[str] = []

    # 1. Lexical & detection method base
    if detection_method == "pdf_toc_outline":
        evidence["lexical"] = 1.0
        evidence["toc"] = 1.0
        score = 0.95
        factors.append("+0.95 (Native PDF Outline bookmark)")
    elif detection_method in ("lexical_part", "lexical_chapter", "lexical_book", "lexical_volume"):
        evidence["lexical"] = 0.90
        score = 0.85
        factors.append(f"+0.85 ({detection_method.replace('_', ' ').title()})")
    elif detection_method == "lexical_special_matter":
        evidence["lexical"] = 0.85
        score = 0.85
        factors.append("+0.85 (Front/Back Matter Keyword)")
    elif detection_method == "numbered_section":
        evidence["lexical"] = 0.80
        evidence["numbering"] = 0.85
        score = 0.80
        factors.append("+0.80 (Numbered Section Pattern)")
    elif detection_method == "printed_toc":
        evidence["toc"] = 0.85
        score = 0.80
        factors.append("+0.80 (Printed TOC Match)")
    elif detection_method == "typography_prominence":
        evidence["typography"] = 0.85
        score = 0.70
        factors.append("+0.70 (Prominent Typography)")
    else:
        score = 0.50
        factors.append("+0.50 (Heuristic Baseline)")

    # 2. Typography & Geometry evidence
    typo_score = 0.50
    if has_font_elevation:
        typo_score += 0.25
        score += 0.05
        factors.append("+0.05 (Font size elevated above body median)")
    if has_bold:
        typo_score += 0.25
        score += 0.03
        factors.append("+0.03 (Bold font weight)")
    evidence["typography"] = min(1.0, typo_score)

    geom_score = 0.50
    if is_centered:
        geom_score += 0.25
        score += 0.03
        factors.append("+0.03 (Horizontally centered)")
    if has_space_around:
        geom_score += 0.25
        score += 0.02
        factors.append("+0.02 (Vertical whitespace separation)")
    evidence["geometry"] = min(1.0, geom_score)

    # 3. TOC & Sequence corroboration
    if is_toc_matched:
        evidence["toc"] = 1.0
        if detection_method != "pdf_toc_outline":
            score += 0.10
            factors.append("+0.10 (Corroborated by Table of Contents)")

    if is_ordinal_sequential:
        evidence["sequence"] = 0.95
        score += 0.05
        factors.append("+0.05 (Sequential ordinal verified)")
    else:
        evidence["sequence"] = 0.50

    if is_multi_line:
        score += 0.02
        factors.append("+0.02 (Multi-line title merged)")

    # 4. Penalties and uncertainty checks
    penalty = 0.0
    if word_count > 15:
        penalty += 0.15
        score -= 0.15
        factors.append("-0.15 (High word count penalty for heading)")
        uncertainty_reasons.append("High word count for a structural heading")
    elif word_count > 10:
        penalty += 0.05
        score -= 0.05
        factors.append("-0.05 (Elevated word count)")

    if is_dialogue_suspect:
        penalty += 0.30
        score -= 0.30
        factors.append("-0.30 (Suspected dialogue or quote)")
        uncertainty_reasons.append("Suspected dialogue or quoted text")

    if ocr_quality < 0.5:
        penalty += 0.20
        score -= 0.20
        factors.append("-0.20 (Low OCR text quality)")
        uncertainty_reasons.append("Low OCR text quality")

    evidence["penalties"] = round(penalty, 2)

    final_score = max(0.1, min(1.0, round(score, 2)))
    if final_score < 0.70 and not uncertainty_reasons:
        uncertainty_reasons.append("Ambiguous structural evidence below high-confidence threshold")

    return final_score, evidence, factors, uncertainty_reasons
