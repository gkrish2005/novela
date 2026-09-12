"""
Table of Contents (TOC) Extraction and Reconciliation.
Extracts native PDF bookmark outlines, parses printed TOC pages, and reconciles page offsets.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class TOCEntry:
    level: int  # 1-indexed hierarchy level (1=Part/Book, 2=Chapter, 3=Section)
    title: str
    page: Optional[int] = None
    target_dest: Optional[str] = None
    confidence: float = 1.0
    source: str = "pdf_outline"  # "pdf_outline" | "printed_toc" | "epub_ncx"


@dataclass
class ParsedTOC:
    entries: list[TOCEntry] = field(default_factory=list)
    has_native_outline: bool = False
    has_printed_toc: bool = False
    source_page_num: Optional[int] = None
    page_offset: int = 0  # Offset between printed page number and physical PDF page index


def extract_native_toc(doc: Any) -> Optional[ParsedTOC]:
    """
    Extracts native outline/bookmarks from a PyMuPDF document if present.
    PyMuPDF returns list of [level, title, page, ...]
    """
    try:
        raw_toc = doc.get_toc(simple=True)
        if not raw_toc:
            return None

        entries: list[TOCEntry] = []
        for item in raw_toc:
            if len(item) >= 3:
                lvl, title, page = item[0], str(item[1]).strip(), int(item[2])
                if title and page > 0:
                    entries.append(
                        TOCEntry(
                            level=lvl,
                            title=title,
                            page=page,
                            confidence=0.95,
                            source="pdf_outline",
                        )
                    )

        if entries:
            return ParsedTOC(entries=entries, has_native_outline=True)
    except Exception:
        pass
    return None


def detect_printed_toc(pages: list[Any]) -> Optional[ParsedTOC]:
    """
    Scans initial document pages (first 25 pages) for a printed Table of Contents.
    Looks for heading triggers ("Contents", "Table of Contents", "Index", "अनुक्रमणिका", "विषय-सूची")
    and lines with dot leaders or trailing page numbers.
    """
    toc_line_pat = re.compile(
        r"^(?P<title>.+?)(?:[\s.·•_-]{3,}|\t+|\s{3,})(?P<page>\d+|[ivxlcdm]+)\s*$",
        re.IGNORECASE,
    )
    toc_heading_pat = re.compile(
        r"^\s*(?:TABLE OF CONTENTS|CONTENTS|INDEX|अनुक्रमणिका|विषय-सूची|तालिका)\s*$",
        re.IGNORECASE,
    )

    for p_idx in range(min(25, len(pages))):
        page = pages[p_idx]
        raw_text = page.raw_text if hasattr(page, "raw_text") else str(page)
        lines = [l.strip() for l in raw_text.split("\n") if l.strip()]

        if not lines:
            continue

        first_line = lines[0]
        has_toc_heading = bool(toc_heading_pat.match(first_line)) or any(
            toc_heading_pat.match(l) for l in lines[:3]
        )

        entries: list[TOCEntry] = []
        for line in lines:
            if toc_heading_pat.match(line):
                continue

            m = toc_line_pat.match(line)
            if m:
                t_str = m.group("title").strip().rstrip(".").strip()
                p_str = m.group("page").strip()
                p_num = int(p_str) if p_str.isdigit() else None

                level = 2
                if re.match(r"^(?:PART|BOOK|VOLUME|भाग|खण्ड|खंड|ग्रंथ)\b", t_str, re.IGNORECASE):
                    level = 1
                elif re.match(r"^\d+\.\d+\b", t_str):
                    level = 3

                if len(t_str) >= 2:
                    entries.append(
                        TOCEntry(
                            level=level,
                            title=t_str,
                            page=p_num,
                            confidence=0.85 if has_toc_heading else 0.70,
                            source="printed_toc",
                        )
                    )

        if len(entries) >= 3 or (has_toc_heading and len(entries) >= 1):
            return ParsedTOC(
                entries=entries,
                has_printed_toc=True,
                source_page_num=p_idx + 1,
            )

    return None


def reconcile_toc_with_candidates(
    toc: Optional[ParsedTOC],
    candidates: list[Any],
    total_pages: int = 1,
) -> dict[str, Any]:
    """
    Reconciles TOC entries with body heading candidates to calculate page offsets
    and check for agreements or disagreements.
    """
    if not toc or not toc.entries or not candidates:
        return {"reconciled": False, "page_offset": 0, "matches": 0, "disagreements": []}

    matches = 0
    offsets: list[int] = []
    disagreements: list[str] = []

    for entry in toc.entries:
        entry_title_norm = re.sub(r"[^\w\s]", "", entry.title.lower()).strip()
        found = False

        for cand in candidates:
            cand_title = cand.clean_title if hasattr(cand, "clean_title") else str(cand)
            cand_title_norm = re.sub(r"[^\w\s]", "", cand_title.lower()).strip()

            if (
                entry_title_norm in cand_title_norm
                or cand_title_norm in entry_title_norm
                or (len(entry_title_norm) > 4 and entry_title_norm[:15] == cand_title_norm[:15])
            ):
                matches += 1
                found = True
                if entry.page and hasattr(cand, "page_num") and cand.page_num:
                    offset = cand.page_num - entry.page
                    offsets.append(offset)
                break

        if not found and entry.page:
            disagreements.append(f"TOC entry '{entry.title}' (page {entry.page}) not found in body headings")

    calculated_offset = round(sum(offsets) / len(offsets)) if offsets else 0
    toc.page_offset = calculated_offset

    return {
        "reconciled": matches > 0,
        "page_offset": calculated_offset,
        "matches": matches,
        "total_toc_entries": len(toc.entries),
        "disagreements": disagreements,
    }
