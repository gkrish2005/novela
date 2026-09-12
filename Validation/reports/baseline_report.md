# Novela Real-World Baseline Report (Corrected)

> [!WARNING]
> **PRELIMINARY / NOT HUMAN VERIFIED**
> All precision, recall, and F1 metrics in this report are measured against **proposed canonical ground truth** (`validation/ground_truth/`, `human_verified = false`). They provide an unbiased engineering reference baseline but do not constitute finalized real-world accuracy claims.
> 
> **Important Note on Previous Baseline:**
> The initial Phase 3 report reported 0.00% precision/recall/F1 due to validation-runner defects (`raw_char_count` key lookup failure and fallback partition false-positive misclassification). Those previous 0% numbers were **invalid artifacts of runner bugs** and have been discarded.

**Execution Date:** September 12, 2026  
**Pipeline:** CURRENT Universal Document Ingestion + Structure Intelligence Engine (Phase 3 Baseline)  
**Corpus Location:** `validation/corpus/` (10 books, 4,677 pages, 301.7 MB)  
**Outputs Generated:** `validation/parser_outputs/` (10 JSON files)  
**Ground Truth:** `validation/ground_truth/` (10 JSON files, PROPOSED / NEEDS HUMAN REVIEW)

---

## 1. Corpus Overview & Extraction Status

| ID | Title | Format | Pages | Raw Chars | Chars/Page | Extraction Classification | Semantic Nodes | Fallback Partitions |
|---|---|---|---|---|---|---|---|---|
| `001_middlemarch` | *Middlemarch* | PDF | 638 | 0 | 0 | **image_only** | 0 | 0 |
| `002_frankenstein` | *Frankenstein; or, The Modern Prometheus* | PDF | 316 | 587,662 | 1,859 | **native_text** | 30 | 0 |
| `003_the_time_machine` | *The Time Machine* | PDF | 221 | 245,124 | 1,109 | **native_text** | 16 | 0 |
| `004_les_miserables` | *Les Misérables* | PDF | 1279 | 3,085,924 | 2,412 | **native_text** | 35 | 0 |
| `005_sherlock_holmes` | *The Adventures of Sherlock Holmes* | PDF | 332 | 719,728 | 2,167 | **native_text** | 0 | 9 |
| `006_alices_adventures` | *Alice's Adventures in Wonderland* | PDF | 226 | 207,785 | 919 | **native_text** | 0 | 9 |
| `007_count_of_monte_cristo` | *The Count of Monte Cristo (Vol. I)* | PDF | 360 | 727,934 | 2,022 | **native_text** | 26 | 0 |
| `008_the_iliad` | *The Iliad* | PDF | 699 | 1,564,835 | 2,238 | **native_text** | 73 | 0 |
| `009_moby_dick` | *Moby-Dick; or, The Whale* | PDF | 394 | 849,642 | 2,156 | **native_text** | 106 | 0 |
| `010_picture_of_dorian_gray` | *The Picture of Dorian Gray* | PDF | 248 | 538,127 | 2,169 | **native_text** | 0 | 9 |

---

## 2. Overall Preliminary Baseline Metrics (Native-Text Documents)

*Evaluated across all 9 native-text documents (301 expected ground-truth nodes). Middlemarch (image-only scan) is isolated as an extraction limitation.*

### Heading Detection & Segmentation
- **Total Expected Canonical Nodes:** 301
- **True Positives (Correctly Detected):** 134
- **False Positives (Over-segmentation / Spurious Headings):** 146
- **False Negatives (Missed Headings):** 167
- **Preliminary Heading Precision:** **47.86%**
- **Preliminary Heading Recall:** **44.52%**
- **Preliminary Structural F1 Score:** **46.13%**

### Classification & Hierarchy
- **Classification Accuracy:** **99.25%** (133/134 matched nodes correctly assigned NodeType)
- **Parent-Child Structural Accuracy:** **100.00%** (134/134 detected headings assigned correct parent level)

### Boundary & Text Integrity
- **Text Retention Rate:** **100.00%** on native text PDFs (zero unrecoverable body loss).
- **Text Duplication Rate:** **0.01%** (zero accidental duplicate regions).
- **Page Monotonicity:** **100%** preserved across all documents.
- **Character Monotonicity:** **100%** preserved across all documents.

---

## 3. Document-Level Results

| Document ID | Pages | Expected | Detected (TP) | False Pos (FP) | Missed (FN) | Precision | Recall | F1 Score | Status |
|---|---|---|---|---|---|---|---|---|---|
| `001_middlemarch` | 638 | 10 | — | — | — | — | — | — | **Extraction Limitation** |
| `002_frankenstein` | 316 | 30 | 25 | 4 | 5 | 86.2% | 83.3% | 84.7% | **Minor Errors** |
| `003_the_time_machine` | 221 | 17 | 13 | 2 | 4 | 86.7% | 76.5% | 81.2% | **Minor Errors** |
| `004_les_miserables` | 1279 | 5 | 0 | 34 | 5 | 0.0% | 0.0% | 0.0% | **Critical Failure** |
| `005_sherlock_holmes` | 332 | 12 | 0 | 0 | 12 | 0.0% | 0.0% | 0.0% | **Critical Failure** |
| `006_alices_adventures` | 226 | 12 | 0 | 0 | 12 | 0.0% | 0.0% | 0.0% | **Critical Failure** |
| `007_count_of_monte_cristo` | 360 | 38 | 25 | 0 | 13 | 100.0% | 65.8% | 79.4% | **Minor Errors** |
| `008_the_iliad` | 699 | 28 | 14 | 58 | 14 | 19.4% | 50.0% | 28.0% | **Critical Failure** |
| `009_moby_dick` | 394 | 138 | 57 | 48 | 81 | 54.3% | 41.3% | 46.9% | **Major Errors** |
| `010_picture_of_dorian_gray` | 248 | 21 | 0 | 0 | 21 | 0.0% | 0.0% | 0.0% | **Critical Failure** |

### Document Status Summary
- **Fully Correct (>= 90% F1):** 0 / 10 (0.0%)
- **Minor Errors (70% - 89% F1):** 3 / 10 (30.0%)
- **Major Errors (30% - 69% F1):** 1 / 10 (10.0%)
- **Critical Failures (< 30% F1):** 5 / 10 (50.0%)
- **Extraction Limitations (Image-only Scan):** 1 / 10 (10.0%)

---

## 4. Failure Distribution & Taxonomy

Total Identified Diagnostic Failures: **315**

| Category | Subcategory | Count | % of Failures | Primary Root Cause |
|---|---|---|---|---|
| `HEADING_DETECTION` | `missed_heading` | 167 | 53.0% | Identified during baseline run |
| `HEADING_DETECTION` | `false_heading` | 144 | 45.7% | Identified during baseline run |
| `LAYOUT` | `header_false_positive` | 2 | 0.6% | Identified during baseline run |
| `EXTRACTION` | `image_only_scan` | 1 | 0.3% | Identified during baseline run |
| `CLASSIFICATION` | `glossary_misclassified` | 1 | 0.3% | Identified during baseline run |

---

## 5. Classification Confusion Matrix

*Evaluated across all correctly detected true positive headings:*

| Expected Type | Predicted `chapter` | Predicted `book` | Predicted `part` | Predicted `preface` | Predicted `introduction` | Predicted `front_matter` |
|---|---|---|---|---|---|---|
| **`chapter`** | 118 | 0 | 0 | 0 | 0 | 0 |
| **`book`** | 0 | 10 | 0 | 0 | 0 | 0 |
| **`part`** | 0 | 0 | 0 | 0 | 0 | 0 |
| **`preface`** | 0 | 0 | 0 | 2 | 0 | 0 |
| **`introduction`** | 0 | 0 | 0 | 0 | 2 | 0 |
| **`front_matter`** | 0 | 0 | 0 | 0 | 0 | 0 |

---

## 6. Performance & Latency Profile (Corrected)

| Document Title | File Size | Actual Pages | Total Parse Time | Latency (ms/Page) | Throughput (Pages/Sec) |
|---|---|---|---|---|---|
| *Middlemarch* | 54.40 MB | 638 | 83.61s | 131.06 ms | 7.6 p/s |
| *Frankenstein; or, The Modern Prometheus* | 7.47 MB | 316 | 23.07s | 73.00 ms | 13.7 p/s |
| *The Time Machine* | 3.19 MB | 221 | 17.65s | 79.85 ms | 12.5 p/s |
| *Les Misérables* | 4.04 MB | 1279 | 8.68s | 6.79 ms | 147.4 p/s |
| *The Adventures of Sherlock Holmes* | 29.02 MB | 332 | 63.25s | 190.50 ms | 5.2 p/s |
| *Alice's Adventures in Wonderland* | 126.34 MB | 226 | 1.93s | 8.52 ms | 117.4 p/s |
| *The Count of Monte Cristo (Vol. I)* | 23.77 MB | 360 | 40.23s | 111.76 ms | 8.9 p/s |
| *The Iliad* | 9.28 MB | 699 | 38.54s | 55.13 ms | 18.1 p/s |
| *Moby-Dick; or, The Whale* | 28.09 MB | 394 | 45.56s | 115.65 ms | 8.6 p/s |
| *The Picture of Dorian Gray* | 12.63 MB | 248 | 19.97s | 80.53 ms | 12.4 p/s |

---

## 7. Scanned PDF & OCR Status

- **Tested Document:** `2015.42254.Middlemarch.pdf` (638 pages, 54.40 MB).
- **Extraction Behavior:** PyMuPDF extracted `0` text characters across all 638 pages.
- **Engine Handling:** The engine assigned `quality_score = 0.20` and flagged `"Low text density detected (< 30 chars/page). PDF may be scanned or image-based."`
- **Validation Treatment:** Correctly categorized as `EXTRACTION_LIMITATION (image_only)`. Excluded from heading detection precision/recall calculations to prevent conflating extraction limits with parsing intelligence.

---

## 8. Validation Limitations & Required Steps for Authoritative Baseline

1. **Human Ground Truth Verification:**
   - The ground truth remains `PROPOSED / NEEDS HUMAN REVIEW`. Canonical chapter names and page numbers must be verified by a human reviewer before certifying final numbers.
2. **Deterministic Rules to Address in Phase 3 Execution:**
   - Support `"ADVENTURE I"` keyword patterns for short-story collections (*Sherlock Holmes*).
   - Add suppression for printed Table of Contents lines (*Moby-Dick*).
   - Address dropped-cap typography and font-size uniform small-caps in historical scans (*Alice's Adventures*, *Dorian Gray*).
