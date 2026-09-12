# Novela Phase 3A — High-Impact Human Review Queue

**Status:** `ACTIVE REVIEW QUEUE — PENDING HUMAN ADJUDICATION`  
**Ground Truth Status:** `PRELIMINARY — CANDIDATE GT — NOT HUMAN VERIFIED` (`human_verified: false`)  
**Review Instruction:** Review only the prioritized items below. Full-book reading is not required. Each item has a decision field left unresolved for your adjudication.

---

## Priority Review Index

- **P0 (Highest Impact on Benchmark Boundaries):**
  1. [`009_moby_dick`](#1-009_moby_dick-vol-1-ch-160-vs-printed-toc): Chapter Headings vs Printed Table of Contents (pp. 13–14)
  2. [`004_les_miserables`](#2-004_les_miserables-volume-book-boundaries-vs-deferred-chapters): Option A Volume/Book boundaries vs deferred chapter scope
  3. [`008_the_iliad`](#3-008_the_iliad-narrative-books-124-vs-scholarly-apparatus): Narrative Books 1–24 vs Knox/Fagles scholarly apparatus (pp. 637–648)
  4. [`002_frankenstein`](#4-002_frankenstein-walton-letters-vs-chapters): Walton Letters I–IV type classification vs chapters (pp. 15–37)
- **P1 (Parser Heuristic Defects on Native Text):**
  5. [`005_sherlock_holmes`](#5-005_sherlock_holmes-adventure-keyword-pattern): `ADVENTURE I` keyword pattern
  6. [`006_alices_adventures`](#6-006_alices_adventures-drop-cap-chapter-initials): Illuminated drop-cap initials on chapter openings
  7. [`010_picture_of_dorian_gray`](#7-010_picture_of_dorian_gray-small-caps-roman-numerals): Small-caps Roman numeral headings
  8. [`003_the_time_machine`](#8-003_the_time_machine-chapter-and-epilogue-boundaries): Chapter 12/15/16 and Epilogue boundaries
  9. [`007_count_of_monte_cristo`](#9-007_count_of_monte_cristo-vol-1-chapters-138): Volume 1 (38 chapters) missing chapter boundaries
- **P2 (Extraction Limitations):**
  10. [`001_middlemarch`](#10-001_middlemarch-scanned-bitmap-edition): Scanned bitmap edition (remains `extraction_limitation` pending OCR)

---

## P0 Items — Critical Structural Boundaries

### 1. `009_moby_dick` (Vol. 1: Ch 1–60 vs Printed TOC)
- **Document:** `009_moby_dick` (`mobydickorwhale01melvuoft.pdf`, 394 pages)
- **PDF Page:** 13–14 (Printed TOC) and 383 (Terminal Chapter LX)
- **Candidate GT Interpretation:** 62 canonical nodes (Etymology, Extracts, Chapters 1–60).
- **Parser Interpretation:** 106 nodes (59 TP, 47 FP, 3 FN). Emitted 18 false chapters from printed TOC lines on pp. 13–14.
- **Disagreement:** Printed TOC entries (e.g. `II. THE CARPET-BAG ...... 8`) extracted as body chapter headings.
- **Contextual Snippet (p. 13):** `CONTENTS / CHAP. PAGE / I. LOOMINGS . 1 / II. THE CARPET-BAG . 8`
- **Recommended Decision:** Approve Candidate GT as strictly Volume 1 (62 nodes). Treat printed TOC extractions as Category A parser defects to be suppressed in Phase 3B.
- **Human Decision:** `[ ] UNRESOLVED — PENDING USER ADJUDICATION`

---

### 2. `004_les_miserables` (Volume / Book Boundaries vs Deferred Chapters)
- **Document:** `004_les_miserables` (`[Hugo_Victor]_Les_Miserables.pdf`, 1,279 pages)
- **PDF Page:** 20, 69, 117, 143...
- **Candidate GT Interpretation:** 53 scored nodes (5 Volumes, 48 Books, `scored: [volume, book]`, `deferred: [chapter]`).
- **Parser Interpretation:** 35 nodes (31 flat chapters, 2 books, 1 preface, 1 front matter).
- **Disagreement:** Full work contains 5 Volumes $\rightarrow$ 48 Books $\rightarrow$ ~365 Chapters.
- **Contextual Snippet (p. 20):** `VOLUME I.—FANTINE. / BOOK FIRST.—AN UPRIGHT MAN. / CHAPTER I.—M. MYRIEL.`
- **Recommended Decision:** Approve Option A hierarchy (`scored: [volume, book]`, `deferred: [chapter]`). 31 parser-detected chapters classified as `out_of_scope` (Category C), not penalized as false positives.
- **Human Decision:** `[ ] UNRESOLVED — PENDING USER ADJUDICATION`

---

### 3. `008_the_iliad` (Narrative Books 1–24 vs Scholarly Apparatus)
- **Document:** `008_the_iliad` (`homer_the_iliad_...pdf`, 699 pages)
- **PDF Page:** 15 (TOC), 77–636 (Books 1–24), 637–648 (Notes)
- **Candidate GT Interpretation:** 31 scored nodes (3 Front Matter, 24 Narrative Books, 4 Back Matter).
- **Parser Interpretation:** 73 nodes (29 matched, 44 FP, 2 FN). Emitted 14 TOC lines on p. 15 and 21 line-note citations on pp. 637–648.
- **Disagreement:** Scholarly line-number citations (`1.1. Goddess...`, `9.171...`) extracted as structural section headings.
- **Contextual Snippet (p. 637):** `NOTES ON THE TRANSLATION / 1.1. Goddess: the Muse who personifies the inspiration...`
- **Recommended Decision:** Confirm 3-zone candidate GT architecture. Treat internal line-note annotations as non-structural apparatus.
- **Human Decision:** `[ ] UNRESOLVED — PENDING USER ADJUDICATION`

---

### 4. `002_frankenstein` (Walton Letters vs Chapters)
- **Document:** `002_frankenstein` (`Shelley_1888_Frankenstein.pdf`, 316 pages)
- **PDF Page:** 15, 20, 25, 27 (Letters), 6–14 (Running Headers)
- **Candidate GT Interpretation:** 30 scored nodes (Introduction, Preface, Letters I–IV as `type: "letter"`, Chapters I–XXIV).
- **Parser Interpretation:** 30 nodes (25 matched, 5 FP, 5 FN). Missed Letters I–IV; emitted 4 roman running header false splits (`Introduction: vii`, `Preface: XV`).
- **Disagreement:** Epistolary framing letters classified as type `letter` vs generic chapters.
- **Contextual Snippet (p. 15):** `FRANKENSTEIN; / OR, / THE MODERN PROMETHEUS. / LETTER I. / To Mrs. Saville, England.`
- **Recommended Decision:** Confirm type `letter` for Walton Letters; classify running header splits as Category A parser noise.
- **Human Decision:** `[ ] UNRESOLVED — PENDING USER ADJUDICATION`

---

## P1 Items — Parser Heuristic Defects on Native Text

### 5. `005_sherlock_holmes` (`ADVENTURE` Keyword Pattern)
- **Document:** `005_sherlock_holmes` (`adventuresofsher001892doyl.pdf`, 332 pages)
- **PDF Page:** 9, 36, 61...
- **Candidate GT Interpretation:** 12 short story adventures.
- **Parser Interpretation:** 0 semantic nodes, 9 fallback partitions.
- **Contextual Snippet (p. 9):** `THE ADVENTURES OF SHERLOCK HOLMES. / ADVENTURE I. / A SCANDAL IN BOHEMIA`
- **Recommended Decision:** Approve 12-adventure candidate GT. Add `"ADVENTURE"` keyword to parser lexical table in Phase 3B.
- **Human Decision:** `[ ] UNRESOLVED — PENDING USER ADJUDICATION`

---

### 6. `006_alices_adventures` (Drop-Cap Chapter Initials)
- **Document:** `006_alices_adventures` (`alicesadventures00carr_20.pdf`, 226 pages)
- **PDF Page:** 13, 27, 41...
- **Candidate GT Interpretation:** 12 body chapters.
- **Parser Interpretation:** 0 semantic nodes, 9 fallback partitions.
- **Contextual Snippet (p. 13):** `CHAPTER I. / Down the Rabbit-Hole / [Drop-Cap 'A'] LICE was beginning...`
- **Recommended Decision:** Approve 12-chapter candidate GT. Update typography thresholding to decouple drop-caps in Phase 3B.
- **Human Decision:** `[ ] UNRESOLVED — PENDING USER ADJUDICATION`

---

### 7. `010_picture_of_dorian_gray` (Small-Caps Roman Numerals)
- **Document:** `010_picture_of_dorian_gray` (`pictureofdoriang0000osca_s9a9.pdf`, 248 pages)
- **PDF Page:** 5 (Preface), 9 (Chapter I), 25...
- **Candidate GT Interpretation:** The Preface + 20 body chapters.
- **Parser Interpretation:** 0 semantic nodes, 9 fallback partitions.
- **Contextual Snippet (p. 9):** `THE PICTURE OF DORIAN GRAY / CHAPTER I.` (Small-caps typography, $1.0\times\text{body}$)
- **Recommended Decision:** Approve Preface + 20 chapters candidate GT. Add small-caps font-flag detection in Phase 3B.
- **Human Decision:** `[ ] UNRESOLVED — PENDING USER ADJUDICATION`

---

### 8. `003_the_time_machine` (Chapter & Epilogue Boundaries)
- **Document:** `003_the_time_machine` (`Wells_1922_Time_Machine.pdf`, 221 pages)
- **PDF Page:** 6–221
- **Candidate GT Interpretation:** 16 Chapters + Epilogue (17 nodes).
- **Parser Interpretation:** 16 nodes (13 matched, 3 FP, 4 FN: missed Ch 12, 15, 16, Epilogue).
- **Recommended Decision:** Approve 17-node candidate GT. Tune chapter-tail OCR and epilogue regex in Phase 3B.
- **Human Decision:** `[ ] UNRESOLVED — PENDING USER ADJUDICATION`

---

### 9. `007_count_of_monte_cristo` (Vol. 1: Chapters 1–38)
- **Document:** `007_count_of_monte_cristo` (`countofmontecris01duma.pdf`, 360 pages)
- **PDF Page:** 7–360
- **Candidate GT Interpretation:** 38 Chapters in Volume 1 edition.
- **Parser Interpretation:** 26 nodes (25 matched, 1 FP, 13 FN).
- **Recommended Decision:** Approve 38-chapter Volume 1 candidate GT.
- **Human Decision:** `[ ] UNRESOLVED — PENDING USER ADJUDICATION`

---

## P2 Items — Extraction Limitations

### 10. `001_middlemarch` (Scanned Bitmap Edition)
- **Document:** `001_middlemarch` (`2015.42254.Middlemarch.pdf`, 638 pages)
- **Embedded Text Characters:** `0` (Image scan)
- **Candidate GT Interpretation:** 10 reference nodes (Prelude, Books I–VIII, Finale).
- **Parser Interpretation:** 0 semantic nodes (isolated under `EXTRACTION_LIMITATION`).
- **Recommended Decision:** Maintain `benchmark_status: "extraction_limitation"`. No parser penalties assessed.
- **Human Decision:** `[ ] UNRESOLVED — PENDING USER ADJUDICATION`
