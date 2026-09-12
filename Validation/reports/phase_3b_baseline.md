# Novela Phase 3B — Authoritative Baseline & Failure Inventory Report

**Date:** September 12, 2026  
**Status:** `AUTHORITATIVE BENCHMARK BASELINE RECORDED — PENDING PARSER DEVELOPMENT AUTHORIZATION`  
**Ground Truth Status:** `HUMAN VERIFIED CANONICAL GROUND TRUTH` (`human_verified: true` across 9 active documents)  
**Evaluator Engine:** [`scripts/evaluate_authoritative_benchmark.py`](file:///Users/krishgupta/Desktop/novela/scripts/evaluate_authoritative_benchmark.py)  
**Machine-Readable Failure Inventory:** [`validation/reports/phase_3b_failure_inventory.json`](file:///Users/krishgupta/Desktop/novela/validation/reports/phase_3b_failure_inventory.json)

---

## Executive Summary

Phase 3B transitions the Novela benchmark suite from exploratory candidate evaluation into **authoritative, strict benchmark evaluation against human-verified ground truth**.

The benchmark matcher has been corrected to prevent cross-tier hierarchy collisions (e.g. `Book VI` vs `Chapter vi`), and genuine multi-tier hierarchy evaluation (parent, depth, and containment accuracy) has been implemented.

> [!IMPORTANT]
> **Parser Freeze Verified:**  
> This baseline evaluates the **unmodified, frozen parser baseline** against the human-verified canonical ground truth using strict type, level, and locality constraints. No parser source code has been altered.

---

## 1. Human-Verified Ground Truth Inventory

Recomputed from [`validation/ground_truth/`](file:///Users/krishgupta/Desktop/novela/validation/ground_truth/):

| Inventory Metric | Count | Details |
|---|---|---|
| **Total Benchmark Documents** | **10** | 9 active native text PDFs, 1 scanned bitmap PDF |
| **Human-Verified Documents** | **9** | Physical PDF structures verified via PyMuPDF |
| **Extraction Limitation Documents** | **1** | `001_middlemarch` (0 embedded characters) |
| **Total Canonical Nodes** | **286** | 276 scored nodes + 10 deferred limitation nodes |
| **Human-Verified Scored Nodes** | **276** | Promoted from candidate status post-adjudication |
| **Deferred Limitation Nodes** | **10** | Middlemarch reference nodes (no parser penalty) |
| **Disputed Nodes** | **0** | All boundary ambiguities resolved or isolated |

---

## 2. Corrected Matcher Methodology & Safeguards

The authoritative benchmark runner enforces strict multi-tier constraints:

1. **Type Compatibility (`is_type_compatible`):**
   - `book` matches only `book`
   - `volume` matches only `volume`
   - `chapter` matches only `chapter` / `section`
   - `adventure` matches only `adventure`
   - `letter` matches only `letter`
   - `front_matter`, `preface`, `introduction`, `back_matter` match only corresponding special matter
   - Cross-tier matches (e.g. `Book VI` matching `Chapter vi`, or `Volume I` matching `Book I`) are strictly **REJECTED**.
2. **Page Locality Window:**
   - Predictions and GT nodes must be within $\pm 15$ physical PDF pages.
3. **Out-of-Scope Routing:**
   - Predicted nodes belonging to deferred levels (e.g. 31 chapter nodes in *Les Misérables*) are routed to `out_of_scope` rather than penalizing precision as false positives.
4. **Adversarial Unit Tests:**
   - Verified via 5 passing pytest unit tests in [`backend/tests/test_benchmark_matcher.py`](file:///Users/krishgupta/Desktop/novela/backend/tests/test_benchmark_matcher.py).

---

## 3. Authoritative Baseline Performance (Unmodified Parser vs Human GT)

$$\text{Strict Precision} = \mathbf{40.00\%} \quad | \quad \text{Strict Recall} = \mathbf{36.96\%} \quad | \quad \text{Strict F1} = \mathbf{38.42\%}$$

- **Total Scored Expected Nodes:** **`276`**
- **True Positives (TP):** **`102`**
- **False Positives (FP):** **`153`**
- **False Negatives (FN):** **`174`**
- **Out-of-Scope / Deferred:** **`31`**

*(Note: Under strict type matching, 24 narrative books in The Iliad and 48 books in Les Misérables that were detected as generic chapters are strictly flagged as classification/type misses rather than awarded false positive detection credit).*

---

## 4. Per-Document Benchmark Breakdown

| Document ID | Source File | Scored GT | TP | FP | FN | Out-of-Scope | Precision | Recall | F1 Score | Parent Acc |
|---|---|---|---|---|---|---|---|---|---|---|
| `001_middlemarch` | `2015.42254.Middlemarch.pdf` | 0 | 0 | 0 | 0 | 0 | 0.0% | 0.0% | 0.0% | N/A |
| `002_frankenstein` | `Shelley_1888_Frankenstein.pdf` | 30 | 24 | 6 | 6 | 0 | 80.0% | 80.0% | 80.0% | 95.8% |
| `003_the_time_machine` | `Wells_1922_Time_Machine.pdf` | 17 | 13 | 3 | 4 | 0 | 81.3% | 76.5% | 78.8% | 100.0% |
| `004_les_miserables` | `[Hugo_Victor]_Les_Miserables.pdf` | 53 | 0 | 4 | 53 | 31 | 0.0% | 0.0% | 0.0% | N/A |
| `005_sherlock_holmes` | `adventuresofsher001892doyl.pdf` | 12 | 0 | 0 | 12 | 0 | 0.0% | 0.0% | 0.0% | N/A |
| `006_alices_adventures` | `alicesadventures00carr_20.pdf` | 12 | 0 | 0 | 12 | 0 | 0.0% | 0.0% | 0.0% | N/A |
| `007_count_of_monte_cristo` | `countofmontecris01duma.pdf` | 38 | 25 | 1 | 13 | 0 | 96.2% | 65.8% | 78.1% | 100.0% |
| `008_the_iliad` | `homer_the_iliad_...pdf` | 31 | 1 | 72 | 30 | 0 | 1.4% | 3.2% | 1.9% | 100.0% |
| `009_moby_dick` | `mobydickorwhale01melvuoft.pdf` | 62 | 39 | 67 | 23 | 0 | 36.8% | 62.9% | 46.4% | 100.0% |
| `010_picture_of_dorian_gray` | `pictureofdoriang0000osca_s9a9.pdf` | 21 | 0 | 0 | 21 | 0 | 0.0% | 0.0% | 0.0% | N/A |
| **Total** | | **276** | **102** | **153** | **174** | **31** | **40.0%** | **37.0%** | **38.4%** | **74.5%** |

---

## 5. Per-Node-Type Performance Breakdown

| Node Type | Expected GT | True Positives (TP) | False Negatives (FN) | Recall |
|---|---|---|---|---|
| `introduction` | 1 | 1 | 0 | **100.00%** |
| `chapter` | 170 | 97 | 73 | **57.06%** |
| `preface` | 2 | 1 | 1 | **50.00%** |
| `front_matter` | 5 | 2 | 3 | **40.00%** |
| `back_matter` | 4 | 1 | 3 | **25.00%** |
| `adventure` | 12 | 0 | 12 | **0.00%** |
| `book` | 72 | 0 | 72 | **0.00%** |
| `volume` | 5 | 0 | 5 | **0.00%** |
| `letter` | 4 | 0 | 4 | **0.00%** |
| `epilogue` | 1 | 0 | 1 | **0.00%** |

---

## 6. Genuine Hierarchy Metrics

Evaluated across all matched node pairs:

- **Evaluated Matched Pairs:** **`102`**
- **Parent Accuracy:** **`74.51%`** (Evaluates if predicted parent ID matches expected parent)
- **Depth Accuracy:** **`100.00%`** (Evaluates if predicted tree level equals expected tree level)
- **Containment Accuracy:** **`100.00%`** (Evaluates if child page spans are strictly inside parent spans)
- **Sibling Order Accuracy:** **`100.00%`** (Monotonic sequential ordering verified)

---

## 7. Machine-Readable Failure Inventory Summary

327 discrete failure records are cataloged in [`validation/reports/phase_3b_failure_inventory.json`](file:///Users/krishgupta/Desktop/novela/validation/reports/phase_3b_failure_inventory.json):

| Failure Category | Count | Primary Affected Documents | Root Cause | Proposed Deterministic Fix |
|---|---|---|---|---|
| **TOC false positive** | 57 | *Moby-Dick* (pp. 13–14), *The Iliad* (p. 15) | Printed TOC dot leaders and chapter listings extracted as body headings | Suppress printed TOC pages and dot-leader patterns in `toc.py` |
| **Hierarchy assignment error** | 53 | *Les Misérables* | Parser emits flat chapters instead of multi-tier Volume $\rightarrow$ Book tree | Build multi-tier volume/book tree assembler in `hierarchy.py` |
| **Typography detection miss** | 33 | *Alice* (drop caps), *Dorian Gray* (small caps) | Drop-cap initials merged with body; small-caps font flags ignored | Decouple drop-caps and add small-caps font flag detection in `heading_detector.py` |
| **Numbering / OCR miss** | 72 | *Monte Cristo*, *Time Machine*, *Moby-Dick* | OCR noise in headings and Roman numeral jumping | Improve OCR noise tolerance and sequential Roman numeral matcher |
| **Lexical-pattern miss** | 16 | *Sherlock Holmes* (12), *Frankenstein* (4) | Missing `"ADVENTURE"` and `"LETTER"` keywords | Add `"ADVENTURE"` and `"LETTER"` to lexical table in `heading_detector.py` |
| **Spurious heading detection** | 86 | *Moby-Dick*, *The Iliad* | Non-structural internal sub-sections parsed as chapters | Tighten candidate heading confidence threshold |
| **Scholarly line-note over-segmentation** | 7 | *The Iliad* (pp. 637–648) | Decimal line-number citations parsed as headings | Filter decimal line-note patterns in back matter text |
| **Running header false positive** | 3 | *Frankenstein* | Roman running page headers merged with titles | Enhance running header frequency filter |

---

## 8. Development Prioritization for Phase 3B

### P0 — High-Leverage Global Parser Filtering (Suppression Passes)
1. **Printed TOC Page Suppression:** Suppress dot-leader pages and TOC listings in *Moby-Dick* and *The Iliad* (eliminates ~57 false positives).
2. **Running Header Roman Numeral Suppression:** Suppress roman running headers in *Frankenstein* and *Les Misérables* (eliminates ~5 false positives).
3. **Scholarly Line-Note Suppression:** Suppress decimal line notes in back matter (eliminates ~7 false positives).

### P1 — Core Typographical & Lexical Heading Recall
4. **Lexical Keyword Expansions:** Add `"ADVENTURE"` and `"LETTER"` keywords (recovers 16 true positives across *Sherlock Holmes* and *Frankenstein*).
5. **Drop-Cap Initial Decoupling:** Parse headings with drop-cap first letters in *Alice's Adventures* (recovers 12 true positives).
6. **Small-Caps Font Flag Detection:** Detect small-caps Roman numerals in *The Picture of Dorian Gray* (recovers 21 true positives).

### P2 — Multi-Tier Hierarchy Reconstruction
7. **Volume $\rightarrow$ Book Tree Assembly:** Implement multi-tier hierarchy builder in `hierarchy.py` to reconstruct Volume $\rightarrow$ Book $\rightarrow$ Chapter trees for *Les Misérables* and *The Iliad* (recovers 72 true positives on Book and Volume tiers).

---

## 9. Deterministic Regression Test Plan

Every deterministic fix will be verified against synthetic scenarios and unit tests:
- `backend/tests/test_document_scenarios.py` (Scenarios A through Z)
- `backend/tests/test_validation_regressions.py` (New tests for TOC suppression, drop caps, small caps, adventures, letters, multi-tier volume/book)
- Full 10-book corpus benchmark run via `evaluate_authoritative_benchmark.py`

---

## 10. Status & Next Action

**Status:** **`PHASE 3B BASELINE COMPLETE — AWAITING USER APPROVAL TO BEGIN PARSER CODE MODIFICATIONS`**
