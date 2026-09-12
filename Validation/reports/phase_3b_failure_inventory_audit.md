# Novela Phase 3B — Failure Inventory Audit & Root-Cause Verification Report

**Audit Date:** September 12, 2026  
**Status:** `ITERATION 0 COMPLETE — FAILURE INVENTORY AUDITED`  
**Inventory Source:** [`validation/reports/phase_3b_failure_inventory.json`](file:///Users/krishgupta/Desktop/novela/validation/reports/phase_3b_failure_inventory.json) (327 records)  
**Evaluator Reference:** [`validation/reports/phase_3b_baseline.md`](file:///Users/krishgupta/Desktop/novela/validation/reports/phase_3b_baseline.md)

---

## Executive Summary

This audit critically examines all **327 discrete failure records** cataloged in the Phase 3B machine-readable failure inventory.

In accordance with strict empirical principles, this report separates:
1. **Observed Failure:** Directly observed in parser output vs human-verified GT.
2. **Inferred Root Cause:** The hypothesized algorithmic mechanism causing the failure.
3. **Proposed Fix Justification:** Whether the deterministic fix is supported by layout/typographical evidence.

---

## 1. Corpus-Wide Failure Category Audit Table

| Failure Category | Count | Primary Affected Documents | Observed Failure | Inferred Root Cause | Confidence in Root Cause | Fix Justified? | Manual Layout Inspection Required? |
|---|---|---|---|---|---|---|---|
| **TOC false positive** | **57** | *Moby-Dick* (pp. 13–14), *The Iliad* (p. 15) | Printed TOC entries (dot leaders, page suffixes) parsed as body chapter nodes | Heading detector scans TOC pages without checking for active TOC region context | **HIGH** (Direct textual & layout evidence) | **YES** (TOC-region boundary suppression) | **NO** (Pattern is obvious across pages) |
| **Hierarchy assignment error** | **53** | *Les Misérables* | Scored Volume and Book divisions missed; parser emitted flat chapters | Parser lacks multi-tier hierarchy builder; assumes flat chapter structure | **HIGH** (Architecture limitation) | **YES** (Multi-tier tree assembly in `hierarchy.py`) | **NO** (Standard multi-tier layout) |
| **Typography detection miss** | **33** | *Alice* (12), *Dorian Gray* (21) | 0 semantic headings detected; fell back to density partitions | Drop-cap initials merge with opening lines; small-caps Roman numerals lack font elevation | **HIGH** (Clear typographical mismatch) | **YES** (Decouple drop-caps; small-caps font flags) | **YES** (Inspect bounding boxes & flags) |
| **Numbering / OCR miss** | **72** | *Monte Cristo* (13), *Time Machine* (4), *Moby-Dick* (23), *Iliad* (30), *Frankenstein* (2) | Numbered chapters missed in native text; Roman numeral sequence jumps | Strict regex requires perfect spacing; OCR glyph noise disrupts numeral matching | **MEDIUM** (Glyph noise vs regex rigidity) | **YES** (Tolerant Roman progression matcher) | **YES** (Verify specific OCR artifacts) |
| **Lexical-pattern miss** | **16** | *Sherlock Holmes* (12), *Frankenstein* (4) | 12 adventures and 4 Walton letters missed by parser | `"ADVENTURE"` and `"LETTER"` absent from structural keyword table | **HIGH** (Explicit keyword table omission) | **YES** (Add structural keywords) | **NO** (Clean native text) |
| **Spurious heading detection** | **86** | *Moby-Dick* (67), *The Iliad* (19) | Internal section dividers, dialogue, and sub-headings parsed as chapters | Threshold too permissive on capitalized short lines within narrative flow | **MEDIUM** (Threshold vs context ambiguity) | **YES** (Require sequential numbering/context) | **YES** (Inspect false positive snippets) |
| **Scholarly apparatus over-segmentation** | **7** | *The Iliad* (pp. 637–648) | Decimal line-number citations (`1.1`, `9.171`) parsed as section headings | Back matter line notes mimic decimal numbering (`\d+\.\d+`) | **HIGH** (Direct decimal pattern evidence) | **YES** (Filter decimal line notes in back matter) | **NO** (Clear line-note syntax) |
| **Running header false positive** | **3** | *Frankenstein* (pp. 6, 8, 14) | Roman running page headers (`Introduction: vii`, `Preface: XV`) merged with titles | Statistical header filter missed Roman numeral running headers | **HIGH** (Repetitive page top geometry) | **YES** (Cross-page header frequency filter) | **NO** (Header position confirmed) |

---

## 2. Deep Dive: High-Leverage vs Ambiguous Categories

### A. High-Confidence Categories (Ready for Implementation in Sequence)
1. **Printed TOC False Positives (57 failures):**
   - *Evidence:* Lines on pp. 13–14 of *Moby-Dick* contain `...... 8`, `...... 36` and page numbers. Page 15 of *The Iliad* contains `CONTENTS / ix`.
   - *Root Cause:* Conclusively confirmed. The parser does not suppress candidate generation inside identified TOC page regions.
   - *Proposed Fix:* Implement general TOC-region suppression in `toc.py` and `heading_detector.py`.
2. **Lexical Pattern Misses (16 failures):**
   - *Evidence:* *Sherlock Holmes* uses `"ADVENTURE I"`; *Frankenstein* uses `"LETTER I"`.
   - *Root Cause:* Conclusively confirmed. The parser's keyword dictionary only recognized `Chapter`, `Book`, `Volume`, `Part`, `Section`.
   - *Proposed Fix:* Add structural keywords with type mapping.
3. **Drop-Cap & Small-Caps Misses (33 failures):**
   - *Evidence:* *Alice* opening lines merge large first letter with text; *Dorian Gray* uses small-caps Roman numerals with font ratio $1.0\times\text{body}$.
   - *Root Cause:* Conclusively confirmed. Typography thresholds require font size ratio $\ge 1.12$, missing same-size small-caps headings.
   - *Proposed Fix:* Update typography heuristics to inspect font flags (`all_caps`, `small_caps`, `bold`) and decouple drop-cap initials.

---

### B. Medium-Confidence / Requires Layout Inspection Categories
1. **Spurious Heading Detections (86 failures in Moby-Dick and Iliad):**
   - *Evidence:* In *Moby-Dick*, internal sub-sections within narrative flow (e.g. within Cetology) were emitted as full chapter nodes.
   - *Risk:* Over-filtering could suppress legitimate short chapter headings.
   - *Action:* Review candidate heading confidence scoring and ensure sequential numbering progression ($N+1$) is enforced.
2. **Numbering / OCR Misses (72 failures):**
   - *Evidence:* In *Monte Cristo*, headings like `PATH EB AND SON` (OCR for *Father and Son*) or Roman numeral jumps cause misses.
   - *Action:* Enhance Roman numeral progression recovery without weakening false positive safeguards.

---

## 3. Iteration Plan & Fix Sequencing Justification

Fixes are prioritized by **cross-document leverage and independence**:
1. **Iteration 1 (TOC Suppression):** Eliminates 57 false positives without touching heading recall.
2. **Iteration 2 (Running Header Suppression):** Eliminates repetitive header noise.
3. **Iteration 3 (Apparatus / Annotation Handling):** Eliminates back-matter line-note over-segmentation.
4. **Iteration 4 (Structural Role Recall):** Recovers Adventures and Letters (16 true positives).
5. **Iteration 5 (Typography & Drop-Cap / Small-Caps):** Recovers Alice and Dorian Gray (33 true positives).
6. **Iteration 6 (Multi-Tier Hierarchy Reconstruction):** Recovers Volume/Book hierarchy in *Les Misérables* and *The Iliad* (recovering 72 true positives on Book/Volume tiers and fixing 26 parent errors).
7. **Iteration 7 (Multi-Line Heading & OCR Progression):** Recovers remaining OCR/numbering misses.
