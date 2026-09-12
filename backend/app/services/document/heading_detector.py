"""
Multi-signal candidate heading detector.
Combines typography, layout geometry, lexical/numbering patterns, TOC matching,
and multi-line title mergers while protecting against dialogue/quote false positives.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Optional

from app.services.document.confidence import compute_node_confidence
from app.services.document.layout import DocumentLayout, LayoutBlock
from app.services.document.models import NodeType
from app.services.document.toc import ParsedTOC


@dataclass
class HeadingCandidate:
    title: str
    clean_title: str
    node_type: NodeType
    level: int  # 1=Book/Part, 2=Chapter/Prologue, 3=Section, 4=Subsection
    ordinal: Optional[int]
    page_num: int
    raw_block_text: str
    confidence: float
    detection_method: str
    evidence: dict[str, Any] = field(default_factory=dict)
    uncertainty_reasons: list[str] = field(default_factory=list)
    is_multi_line: bool = False
    doc_char_start: int = 0
    doc_char_end: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)


# Lexical regex rules
VOLUME_BOOK_PATTERNS = [
    re.compile(r"^\s*['\"`_*~-]*\s*(?:VOLUME|BOOK|ग्रंथ|किताब)\s+(?P<num>[IVXLCDM]+|\d+|[\u0966-\u096F]+|ONE|TWO|THREE|FOUR|FIVE|SIX|SEVEN|EIGHT|NINE|TEN|FIRST|SECOND|THIRD|FOURTH|FIFTH)(?:\s*[:.-]\s*(?P<title>.*))?['\"`_*~-]*$", re.IGNORECASE),
    re.compile(r"^\s*(?:VOLUME|BOOK)\s+[IVXLCDM\d\u0966-\u096F]+\s*$", re.IGNORECASE),
]

PART_PATTERNS = [
    re.compile(r"^\s*['\"`_*~-]*\s*(?:PART|भाग|खण्ड|खंड)\s+(?P<num>[IVXLCDM]+|\d+|[\u0966-\u096F]+|ONE|TWO|THREE|FOUR|FIVE|SIX|SEVEN|EIGHT|NINE|TEN|FIRST|SECOND|THIRD|FOURTH|FIFTH)(?:\s*[:.-]\s*(?P<title>.*))?['\"`_*~-]*$", re.IGNORECASE),
    re.compile(r"^\s*(?:PART|भाग)\s+[IVXLCDM\d\u0966-\u096F]+\s*$", re.IGNORECASE),
]

CHAPTER_PATTERNS = [
    re.compile(r"^\s*['\"`_*~-]*\s*(?:CHAPTER|ACT|SCENE|अध्याय|सर्ग|पाठ)\s+(?P<num>[IVXLCDM]+|\d+|[\u0966-\u096F]+|ONE|TWO|THREE|FOUR|FIVE|SIX|SEVEN|EIGHT|NINE|TEN|ELEVEN|TWELVE|THIRTEEN|FOURTEEN|FIFTEEN|SIXTEEN|SEVENTEEN|EIGHTEEN|NINETEEN|TWENTY)(?:\s*[:.-]\s*(?P<title>.*))?['\"`_*~-]*$", re.IGNORECASE),
    re.compile(r"^\s*['\"`_*~-]*\s*(?P<num>ONE|TWO|THREE|FOUR|FIVE|SIX|SEVEN|EIGHT|NINE|TEN|ELEVEN|TWELVE|THIRTEEN|FOURTEEN|FIFTEEN|SIXTEEN|SEVENTEEN|EIGHTEEN|NINETEEN|TWENTY|II|III|IV|VI|VII|VIII|IX|XI|XII|XIII|XIV|XV|XVI|XVII|XVIII|XIX|XX)\s*['\"`_*~-]*$", re.IGNORECASE),
]

NUMBERED_SECTION_PATTERNS = [
    re.compile(r"^\s*['\"`_*~-]*\s*(?P<num>[\d\u0966-\u096F]+(?:\.[\d\u0966-\u096F]+)+)\s*[:.)-]?\s+(?P<title>[A-Z\u0900-\u097F][^\n]{2,80})['\"`_*~-]*$"),
    re.compile(r"^\s*['\"`_*~-]*\s*(?P<num>[\d\u0966-\u096F]+)\s*[:.)-]\s+(?P<title>[A-Z\u0900-\u097F][^\n]{2,80})['\"`_*~-]*$"),
    re.compile(r"^\s*['\"`_*~-]*\s*(?P<num>[IVXLCDM]+)\s*[:.)-]\s+(?P<title>[A-Z\u0900-\u097F][^\n]{2,80})['\"`_*~-]*$"),
]

FRONT_BACK_MATTER_PATTERNS = [
    (re.compile(r"^\s*(?:PROLOGUE|प्रस्तावना)(?:\s*[:.-]\s*(?P<title>.*))?$", re.IGNORECASE), NodeType.PROLOGUE, 2),
    (re.compile(r"^\s*(?:EPILOGUE|उपसंहार)(?:\s*[:.-]\s*(?P<title>.*))?$", re.IGNORECASE), NodeType.EPILOGUE, 2),
    (re.compile(r"^\s*(?:PREFACE|प्राक्कथन)(?:\s*[:.-]\s*(?P<title>.*))?$", re.IGNORECASE), NodeType.PREFACE, 2),
    (re.compile(r"^\s*(?:INTRODUCTION|भूमिका)(?:\s*[:.-]\s*(?P<title>.*))?$", re.IGNORECASE), NodeType.INTRODUCTION, 2),
    (re.compile(r"^\s*(?:DEDICATION|समर्पण)(?:\s*[:.-]\s*(?P<title>.*))?$", re.IGNORECASE), NodeType.DEDICATION, 2),
    (re.compile(r"^\s*(?:EPIGRAPH)(?:\s*[:.-]\s*(?P<title>.*))?$", re.IGNORECASE), NodeType.EPIGRAPH, 2),
    (re.compile(r"^\s*(?:APPENDIX|परिशिष्ट)(?:\s*(?P<num>[A-Z]|\d+|[\u0966-\u096F]+))?(?:\s*[:.-]\s*(?P<title>.*))?$", re.IGNORECASE), NodeType.APPENDIX, 2),
    (re.compile(r"^\s*(?:GLOSSARY|शब्दावली)(?:\s*[:.-]\s*(?P<title>.*))?$", re.IGNORECASE), NodeType.GLOSSARY, 2),
    (re.compile(r"^\s*(?:NOTES|टिप्पणियाँ)(?:\s*[:.-]\s*(?P<title>.*))?$", re.IGNORECASE), NodeType.NOTES, 2),
    (re.compile(r"^\s*(?:BIBLIOGRAPHY|संदर्भ ग्रंथ सूची)(?:\s*[:.-]\s*(?P<title>.*))?$", re.IGNORECASE), NodeType.BIBLIOGRAPHY, 2),
    (re.compile(r"^\s*(?:AFTERWORD|उत्तरकथा)(?:\s*[:.-]\s*(?P<title>.*))?$", re.IGNORECASE), NodeType.AFTERWORD, 2),
]


def _normalize_title(text: Optional[str]) -> str:
    if not text:
        return ""
    cleaned = re.sub(r"\s+", " ", text).strip()
    if cleaned.isupper() and len(cleaned) > 3:
        return cleaned.title()
    return cleaned


def _parse_ordinal(token: Optional[str]) -> Optional[int]:
    if not token:
        return None
    token = token.strip().upper()

    dev_map = {"०": "0", "१": "1", "२": "2", "३": "3", "४": "4", "५": "5", "६": "6", "७": "7", "८": "8", "९": "9"}
    for d_char, a_char in dev_map.items():
        token = token.replace(d_char, a_char)

    if token.isdigit():
        return int(token)
    word_map = {
        "ONE": 1, "FIRST": 1, "TWO": 2, "SECOND": 2, "THREE": 3, "THIRD": 3,
        "FOUR": 4, "FOURTH": 4, "FIVE": 5, "FIFTH": 5, "SIX": 6, "SEVEN": 7,
        "EIGHT": 8, "NINE": 9, "TEN": 10, "ELEVEN": 11, "TWELVE": 12,
        "THIRTEEN": 13, "FOURTEEN": 14, "FIFTEEN": 15, "SIXTEEN": 16,
        "SEVENTEEN": 17, "EIGHTEEN": 18, "NINETEEN": 19, "TWENTY": 20
    }
    if token in word_map:
        return word_map[token]
    roman_map = {
        "I": 1, "II": 2, "III": 3, "IV": 4, "V": 5, "VI": 6, "VII": 7,
        "VIII": 8, "IX": 9, "X": 10, "XI": 11, "XII": 12, "XIII": 13,
        "XIV": 14, "XV": 15, "XVI": 16, "XVII": 17, "XVIII": 18, "XIX": 19, "XX": 20
    }
    if token in roman_map:
        return roman_map[token]
    return None


def is_dialogue_or_quote(text: str) -> bool:
    """General check if text is dialogue, inline quote, citation, or legal boilerplate."""
    stripped = text.strip()
    if (stripped.startswith('"') and stripped.endswith('"')) or (stripped.startswith("'") and stripped.endswith("'")):
        return True
    if stripped.startswith('"') or stripped.startswith("'") or stripped.startswith("“") or stripped.startswith("‘"):
        return True
    if re.search(r'\b(?:said|whispered|screamed|answered|replied|cried|thought)\b', stripped, re.IGNORECASE):
        return True
    if stripped.endswith(",") or stripped.endswith(";") or stripped.endswith("—") or stripped.endswith("--"):
        return True
    if re.search(r"\b(?:Printing|Avenue|Madison|Copyright|All rights reserved|Published by|Library of Congress|ISBN)\b", stripped, re.IGNORECASE):
        return True
    return False


def detect_candidate_headings(
    layout: DocumentLayout,
    toc: Optional[ParsedTOC] = None,
) -> list[HeadingCandidate]:
    """
    Extracts all candidate headings across document pages using multi-signal analysis.
    """
    candidates: list[HeadingCandidate] = []
    body_size = layout.body_font_size or 10.0
    heading_threshold = layout.heading_font_size_threshold or (body_size * 1.12)

    all_blocks: list[tuple[int, int, LayoutBlock]] = []
    for p_idx, page in enumerate(layout.pages):
        for b_idx, block in enumerate(page.blocks):
            if not getattr(block, "is_header", False) and not getattr(block, "is_footer", False):
                all_blocks.append((p_idx, b_idx, block))

    total_blocks = len(all_blocks)
    consumed_indices = set()
    prev_ordinal: Optional[int] = None

    for i in range(total_blocks):
        if i in consumed_indices:
            continue

        p_idx, b_idx, block = all_blocks[i]
        text = block.text.strip()
        if not text or len(text) > 250:
            continue

        if is_dialogue_or_quote(text):
            continue

        page_num = p_idx + 1
        avg_size = block.avg_font_size
        is_bold = block.is_bold
        is_large = avg_size >= heading_threshold
        is_caps = block.is_all_caps
        line_count = block.line_count
        word_count = len(text.split())

        matched_candidate: Optional[HeadingCandidate] = None

        # Check TOC matching
        is_toc_matched = False
        if toc and toc.entries:
            clean_l = text.lower()
            is_toc_matched = any(e.title.lower() in clean_l or clean_l in e.title.lower() for e in toc.entries)

        # Signal 1: Front / Back matter patterns
        for pat, n_type, lvl in FRONT_BACK_MATTER_PATTERNS:
            m = pat.match(text)
            if m:
                extra_title = m.groupdict().get("title") if hasattr(m, "groupdict") else ""
                base_name = n_type.value.replace("_", " ").title()
                norm_extra = _normalize_title(extra_title)
                final_title = f"{base_name}: {norm_extra}" if norm_extra else base_name
                conf, ev, _, uncert = compute_node_confidence(
                    detection_method="lexical_special_matter",
                    has_font_elevation=is_large,
                    has_bold=is_bold,
                    is_toc_matched=is_toc_matched,
                    word_count=word_count,
                )
                matched_candidate = HeadingCandidate(
                    title=final_title,
                    clean_title=base_name,
                    node_type=n_type,
                    level=lvl,
                    ordinal=None,
                    page_num=page_num,
                    raw_block_text=text,
                    confidence=conf,
                    detection_method="lexical_special_matter",
                    evidence=ev,
                    uncertainty_reasons=uncert,
                )
                break

        # Signal 2: Book / Volume patterns
        if not matched_candidate:
            for pat in VOLUME_BOOK_PATTERNS:
                m = pat.match(text)
                if m:
                    num_str = m.groupdict().get("num") if hasattr(m, "groupdict") else None
                    ord_val = _parse_ordinal(num_str) if num_str else None
                    extra_title = m.groupdict().get("title") if hasattr(m, "groupdict") else ""
                    label = f"Book {num_str}" if num_str else "Book"
                    norm_extra = _normalize_title(extra_title)
                    final_title = f"{label} - {norm_extra}" if norm_extra else label
                    conf, ev, _, uncert = compute_node_confidence(
                        detection_method="lexical_book",
                        has_font_elevation=is_large,
                        has_bold=is_bold,
                        is_toc_matched=is_toc_matched,
                        is_ordinal_sequential=(ord_val == (prev_ordinal or 0) + 1) if ord_val else False,
                        word_count=word_count,
                    )
                    matched_candidate = HeadingCandidate(
                        title=final_title,
                        clean_title=norm_extra or label,
                        node_type=NodeType.BOOK,
                        level=1,
                        ordinal=ord_val,
                        page_num=page_num,
                        raw_block_text=text,
                        confidence=conf,
                        detection_method="lexical_book",
                        evidence=ev,
                        uncertainty_reasons=uncert,
                    )
                    break

        # Signal 3: Part patterns
        if not matched_candidate:
            for pat in PART_PATTERNS:
                m = pat.match(text)
                if m:
                    num_str = m.groupdict().get("num") if hasattr(m, "groupdict") else None
                    ord_val = _parse_ordinal(num_str) if num_str else None
                    extra_title = m.groupdict().get("title") if hasattr(m, "groupdict") else ""
                    part_label = f"Part {num_str}" if num_str else "Part"
                    norm_extra = _normalize_title(extra_title)
                    final_title = f"{part_label} - {norm_extra}" if norm_extra else part_label
                    conf, ev, _, uncert = compute_node_confidence(
                        detection_method="lexical_part",
                        has_font_elevation=is_large,
                        has_bold=is_bold,
                        is_toc_matched=is_toc_matched,
                        is_ordinal_sequential=(ord_val == (prev_ordinal or 0) + 1) if ord_val else False,
                        word_count=word_count,
                    )
                    matched_candidate = HeadingCandidate(
                        title=final_title,
                        clean_title=norm_extra or part_label,
                        node_type=NodeType.PART,
                        level=1,
                        ordinal=ord_val,
                        page_num=page_num,
                        raw_block_text=text,
                        confidence=conf,
                        detection_method="lexical_part",
                        evidence=ev,
                        uncertainty_reasons=uncert,
                    )
                    break

        # Signal 4: Explicit Chapter patterns + Multi-line title merger
        if not matched_candidate:
            for pat in CHAPTER_PATTERNS:
                m = pat.match(text)
                if m:
                    num_str = m.groupdict().get("num") if hasattr(m, "groupdict") else None
                    ord_val = _parse_ordinal(num_str) if num_str else None
                    extra_title = m.groupdict().get("title") if hasattr(m, "groupdict") else ""
                    chap_label = f"Chapter {num_str}" if num_str else "Chapter"
                    norm_extra = _normalize_title(extra_title)
                    final_title = f"{chap_label} - {norm_extra}" if norm_extra else chap_label

                    merged = False
                    if not norm_extra and i + 1 < total_blocks:
                        next_p, next_b, next_block = all_blocks[i + 1]
                        if next_p == p_idx and next_block.line_count <= 2:
                            next_text = next_block.text.strip()
                            if (
                                len(next_text) <= 80
                                and not next_text.endswith(".")
                                and (next_block.avg_font_size >= body_size * 1.05 or next_block.is_bold or next_block.is_all_caps or next_text.istitle() or next_text.isupper())
                                and not is_dialogue_or_quote(next_text)
                                and not any(p.match(next_text) for p in CHAPTER_PATTERNS + PART_PATTERNS)
                            ):
                                final_title = f"{chap_label}: {_normalize_title(next_text)}"
                                merged = True
                                consumed_indices.add(i + 1)

                    is_seq = (ord_val == (prev_ordinal or 0) + 1) if ord_val else False
                    conf, ev, _, uncert = compute_node_confidence(
                        detection_method="lexical_chapter",
                        has_font_elevation=is_large,
                        has_bold=is_bold,
                        is_toc_matched=is_toc_matched,
                        is_ordinal_sequential=is_seq,
                        word_count=word_count,
                        is_multi_line=merged,
                    )
                    matched_candidate = HeadingCandidate(
                        title=final_title,
                        clean_title=norm_extra or chap_label,
                        node_type=NodeType.CHAPTER,
                        level=2,
                        ordinal=ord_val,
                        page_num=page_num,
                        raw_block_text=text,
                        confidence=conf,
                        detection_method="lexical_chapter",
                        evidence=ev,
                        uncertainty_reasons=uncert,
                        is_multi_line=merged,
                    )
                    break

        # Signal 5: Numbered Section patterns ("1.1 Title" or "1. Title")
        if not matched_candidate:
            for pat in NUMBERED_SECTION_PATTERNS:
                m = pat.match(text)
                if m:
                    num_str = m.group("num")
                    sec_title = m.group("title").strip()
                    if num_str.isdigit() and int(num_str) > 150:
                        continue
                    ord_val = int(num_str.split(".")[0]) if num_str.replace(".", "").isdigit() else _parse_ordinal(num_str)
                    lvl = 3 if "." in num_str else 2
                    n_type = NodeType.SECTION if lvl == 3 else NodeType.CHAPTER
                    norm_sec = _normalize_title(sec_title)
                    conf, ev, _, uncert = compute_node_confidence(
                        detection_method="numbered_section",
                        has_font_elevation=is_large,
                        has_bold=is_bold,
                        is_toc_matched=is_toc_matched,
                        is_ordinal_sequential=(ord_val == (prev_ordinal or 0) + 1) if ord_val else False,
                        word_count=word_count,
                    )
                    matched_candidate = HeadingCandidate(
                        title=f"{num_str}. {norm_sec}",
                        clean_title=norm_sec,
                        node_type=n_type,
                        level=lvl,
                        ordinal=ord_val,
                        page_num=page_num,
                        raw_block_text=text,
                        confidence=conf,
                        detection_method="numbered_section",
                        evidence=ev,
                        uncertainty_reasons=uncert,
                    )
                    break

        # Signal 6: Typography Prominence without keywords
        if not matched_candidate and is_large and is_bold and line_count <= 2:
            clean_first = text.split("\n")[0].strip()
            if 3 <= len(clean_first) <= 60 and not clean_first.endswith(".") and not is_dialogue_or_quote(clean_first):
                conf, ev, _, uncert = compute_node_confidence(
                    detection_method="typography_prominence",
                    has_font_elevation=True,
                    has_bold=True,
                    is_toc_matched=is_toc_matched,
                    word_count=word_count,
                )
                norm_prom = _normalize_title(clean_first)
                matched_candidate = HeadingCandidate(
                    title=norm_prom,
                    clean_title=norm_prom,
                    node_type=NodeType.CHAPTER,
                    level=2,
                    ordinal=None,
                    page_num=page_num,
                    raw_block_text=text,
                    confidence=conf,
                    detection_method="typography_prominence",
                    evidence=ev,
                    uncertainty_reasons=uncert,
                )

        if matched_candidate:
            if matched_candidate.ordinal:
                prev_ordinal = matched_candidate.ordinal
            candidates.append(matched_candidate)

    return candidates
