# Ground Truth Audit & Structural Alignment Report

**Date:** September 12, 2026  
**Auditor:** Antigravity Engineering (Phase 3 Quality Assurance)  
**Status:** `PROPOSED / NEEDS HUMAN REVIEW` (`human_verified = false`)  
**Corpus Target:** 10 Public Domain Books (`validation/corpus/`)  
**Ground Truth Location:** `validation/ground_truth/*.json`

---

## Executive Summary

An audit of the proposed ground-truth files (`validation/ground_truth/*.json`) across the 10 corpus books reveals that the current reference dataset represents **programmatically generated canonical models** rather than **human-verified, edition-accurate representations**.

Several headline metric discrepancies in the preliminary baseline—most notably *Les Misérables* (0% F1 despite 35 extracted chapters) and *The Iliad* (58 false positives caused by scholarly apparatus)—stem directly from **ground-truth granularity mismatches** and **edition-specific structural variance**, rather than parser failures alone.

All ground truth files must remain tagged `PROPOSED / NEEDS HUMAN REVIEW` (`human_verified = false`) until human curators verify edition-specific headings, Roman/Arabic numbering conventions, and hierarchy levels.

---

## Document-by-Document Ground Truth Audit

---

### 1. `001_middlemarch` (*Middlemarch* — George Eliot)
- **Source Edition:** `2015.42254.Middlemarch.pdf` (638 pages, 54.4 MB, scanned archive)
- **Expected Structural Hierarchy:**
  ```
  Book (8 Books)
    └── Chapter (86 Chapters)
  + Front Matter (Prelude)
  + Back Matter (Finale)
  ```
- **Proposed GT Hierarchy:** 10 nodes (Prelude, Book I to VIII, Finale). GT does not specify the 86 constituent chapters.
- **Likely GT Errors:** Granularity truncation (omits 86 chapters).
- **Likely Parser Errors:** N/A (Image-only scan with 0 text characters; parser gracefully returned empty tree).
- **Ambiguous Cases:** None.
- **Recommended Human Decision:** Mark as `EXTRACTION LIMITATION (IMAGE-ONLY)`. Isolate from native-text parser accuracy metrics until OCR synthesis is introduced. Expand GT to include all 86 chapters for when OCR is enabled.

---

### 2. `002_frankenstein` (*Frankenstein* — Mary Shelley)
- **Source Edition:** `Shelley_1888_Frankenstein.pdf` (316 pages, 7.5 MB, 1888 edition)
- **Expected Structural Hierarchy:**
  ```
  Document
    ├── Front Matter (Author's Introduction, Preface)
    ├── Letters (Letter I, Letter II, Letter III, Letter IV)
    └── Chapters (Chapter I through Chapter XXIV)
  ```
- **Proposed GT Hierarchy:** 30 nodes (Introduction, Preface, Letter I–IV, Chapter 1–24).
- **Likely GT Errors:**
  1. GT uses Arabic numerals (`Chapter 1`), while the 1888 edition prints Roman numerals (`Chapter I`). (Resolved by comparator normalization).
  2. GT treats `Letter I` through `Letter IV` as type `chapter`, which is semantically acceptable but differs in naming.
- **Likely Parser Errors:**
  1. Failed to detect `Letter I` .. `Letter IV` (parser only looked for `"Chapter"` / `"Book"` / `"Part"`).
  2. Sub-pagination headers in the introduction (`Introduction: vii`, `ix`, `xi`, `Preface: XV`) were captured as separate heading nodes.
  3. `Chapter XVI` heading was corrupted by running header collision.
- **Ambiguous Cases:** Whether Roman numeral romanettes in the Introduction should be separate sections or part of the parent Introduction.
- **Recommended Human Decision:** Keep Introduction, Preface, 4 Letters, and 24 Chapters in GT. Update GT status to `HUMAN_REVIEW_READY`.

---

### 3. `003_the_time_machine` (*The Time Machine* — H. G. Wells)
- **Source Edition:** `Wells_1922_Time_Machine.pdf` (221 pages, 3.2 MB, 1922 edition)
- **Expected Structural Hierarchy:**
  ```
  Document
    ├── Front Matter
    ├── Chapters (Chapter I through Chapter XVI)
    └── Back Matter (Epilogue)
  ```
- **Proposed GT Hierarchy:** 17 nodes (Chapter 1–16, Epilogue).
- **Likely GT Errors:** None; GT matches standard edition structure.
- **Likely Parser Errors:**
  1. Detected `Chapter vii` on page 5 (printed TOC line).
  2. Duplicate detection of `Chapter XI` across page boundaries.
  3. Missed `Epilogue` due to lack of standard chapter keyword.
- **Ambiguous Cases:** None.
- **Recommended Human Decision:** Verify page numbers for Chapters 1–16 and Epilogue.

---

### 4. `004_les_miserables` (*Les Misérables* — Victor Hugo)
- **Source Edition:** `[Hugo_Victor]_Les_Miserables.pdf` (1,279 pages, 4.0 MB, complete multi-volume text)
- **Expected Structural Hierarchy:**
  ```
  Volume (5 Volumes: Fantine, Cosette, Marius, The Idyll, Jean Valjean)
    └── Book (e.g. Book 1: An Upright Man, Book 2: The Fall, etc.)
          └── Chapter (e.g. Chapter I: M. Myriel, Chapter II...)
  ```
- **Proposed GT Hierarchy:** **Only 5 nodes** (`Volume I: Fantine` through `Volume V: Jean Valjean`).
- **Likely GT Errors:** **CRITICAL GRANULARITY MISMATCH.** GT lists only the 5 top-level Volumes, ignoring the ~50 Books and ~300 Chapters. As a result, when the parser accurately extracted 35 granular Book and Chapter headings (`Book SECOND`, `Chapter I: M. Myriel`), the comparator marked all 35 as False Positives, producing an artificial 0% F1.
- **Likely Parser Errors:** None on granularity; parser correctly attempted to extract Books and Chapters.
- **Ambiguous Cases:** Whether Volume headings appear explicitly on separate title pages or as running book headers.
- **Recommended Human Decision:** **Revise Ground Truth to 3-level hierarchy (`Volume -> Book -> Chapter`)**. This single fix will transform Les Misérables from an artificial 0% critical failure to an accurate evaluation of Hugo's epic structure.

---

### 5. `005_sherlock_holmes` (*The Adventures of Sherlock Holmes* — Arthur Conan Doyle)
- **Source Edition:** `adventuresofsher001892doyl.pdf` (332 pages, 29.0 MB, 1892 George Newnes first edition)
- **Expected Structural Hierarchy:**
  ```
  Document
    └── 12 Short Story Adventures:
          ├── ADVENTURE I. A SCANDAL IN BOHEMIA
          ├── ADVENTURE II. THE RED-HEADED LEAGUE
          ...
          └── ADVENTURE XII. THE ADVENTURE OF THE COPPER BEECHES
  ```
- **Proposed GT Hierarchy:** 12 nodes (`ADVENTURE I` to `XII`).
- **Likely GT Errors:** None; GT is structurally sound.
- **Likely Parser Errors:** **Deterministic Keyword Gap.** Parser regex suite lacks `"ADVENTURE"` as a primary heading trigger. Parser detected 0 headings and fell back to 9 paragraph density partitions (`Section 1..9`).
- **Ambiguous Cases:** None.
- **Recommended Human Decision:** Keep GT. Add `"ADVENTURE"` keyword rule in Phase 3B deterministic parser improvements.

---

### 6. `006_alices_adventures` (*Alice's Adventures in Wonderland* — Lewis Carroll)
- **Source Edition:** `alicesadventures00carr_20.pdf` (226 pages, 126.3 MB, illustrated edition)
- **Expected Structural Hierarchy:**
  ```
  Document
    ├── Front Matter (Prefatory poem "All in the golden afternoon...")
    └── Chapters (CHAPTER I. DOWN THE RABBIT-HOLE through CHAPTER XII. ALICE'S EVIDENCE)
  ```
- **Proposed GT Hierarchy:** 12 nodes (`CHAPTER I` to `XII`).
- **Likely GT Errors:** None.
- **Likely Parser Errors:** Heading detection missed chapter titles because illustrated dropped-cap initials (e.g. giant "A", "T") broke paragraph line aggregation, and chapter title font size was identical to body text. Fell back to 9 partitions.
- **Ambiguous Cases:** Whether prefatory poem should be front matter or standalone introductory section.
- **Recommended Human Decision:** Keep 12 chapters in GT. Annotate page offsets for all 12 chapters.

---

### 7. `007_count_of_monte_cristo` (*The Count of Monte Cristo, Vol. 1* — Alexandre Dumas)
- **Source Edition:** `countofmontecris01duma.pdf` (360 pages, 23.8 MB, Volume 1)
- **Expected Structural Hierarchy:**
  ```
  Document
    └── Chapters (Chapter I: Marseilles -- The Arrival through Chapter XXXVIII: The Rendezvous)
  ```
- **Proposed GT Hierarchy:** 38 nodes (`Chapter 1` to `38`).
- **Likely GT Errors:** None.
- **Likely Parser Errors:** Parser correctly extracted 25 chapters with 100% precision! Missed 13 chapters because 19th-century OCR scan introduced letter degradation into heading lines (e.g. `Chapter XXVI: The A.Ubebge Of Pont Dt' Gabd`).
- **Ambiguous Cases:** None.
- **Recommended Human Decision:** Maintain 38 chapters in GT.

---

### 8. `008_the_iliad` (*The Iliad* — Homer, tr. Robert Fagles)
- **Source Edition:** `homer_the_iliad_penguin_classics_deluxe_edition-robert-fagles.pdf` (699 pages, 9.3 MB, Penguin Deluxe Edition)
- **Expected Structural Hierarchy:**
  ```
  Document
    ├── Front Matter (Preface by Knox, Introduction by Knox)
    ├── The Iliad: Books 1–24 (e.g. BOOK 1: The Rage of Achilles)
    ├── Scholarly Apparatus:
    │     ├── The Genealogy of the Gods
    │     ├── Notes on the Translation
    │     └── Pronouncing Glossary
  ```
- **Proposed GT Hierarchy:** 28 nodes (Preface, Introduction, Books 1–24, Notes, Glossary).
- **Likely GT Errors:** GT mixes primary narrative (24 epic Books) with extensive multi-chapter scholarly essays (Knox's Introduction is ~80 pages with subheadings).
- **Likely Parser Errors:** Parser detected 73 nodes (20 Books + 53 essay sections and running headers). Running headers like `"Book ONE"`, `"Book TWO"` on verso pages were captured as spurious book nodes (58 False Positives).
- **Ambiguous Cases:** How to hierarchically represent Knox's sub-essays vs Homer's primary books.
- **Recommended Human Decision:** Split GT into `primary_narrative` (24 Books) and `ancillary_apparatus` (Preface, Intro, Notes, Glossary).

---

### 9. `009_moby_dick` (*Moby-Dick; or, The Whale* — Herman Melville)
- **Source Edition:** `mobydickorwhale01melvuoft.pdf` (394 pages, 28.1 MB, 1851 edition)
- **Expected Structural Hierarchy:**
  ```
  Document
    ├── Front Matter (Etymology, Extracts)
    ├── Chapters 1–135 (e.g. Chapter 1: Loomings, Chapter 32: Cetology)
    │     └── Sub-books in Cetology (Folio, Octavo, Duodecimo)
    └── Back Matter (Epilogue)
  ```
- **Proposed GT Hierarchy:** 138 nodes (Etymology, Extracts, Chapters 1–135, Epilogue).
- **Likely GT Errors:** GT is structurally complete and high quality.
- **Likely Parser Errors:**
  1. **TOC Contamination:** 46 lines from the printed Table of Contents on pages 13–14 were captured as numbered section nodes (`II. The Carpet-Bag ...... 8`), generating 46 False Positives.
  2. OCR noise in chapter headings on degraded pages.
- **Ambiguous Cases:** Whether Cetology sub-books (Folio, Octavo, Duodecimo) are Level 2 sub-sections or separate books.
- **Recommended Human Decision:** Keep 138 canonical nodes in GT. Add TOC page suppression rule in parser during Phase 3B.

---

### 10. `010_picture_of_dorian_gray` (*The Picture of Dorian Gray* — Oscar Wilde)
- **Source Edition:** `pictureofdoriang0000osca_s9a9.pdf` (248 pages, 12.6 MB, early edition)
- **Expected Structural Hierarchy:**
  ```
  Document
    ├── The Preface (Wilde's famous aphorisms)
    └── Chapters 1–20 (CHAPTER I through CHAPTER XX)
  ```
- **Proposed GT Hierarchy:** 21 nodes (The Preface, Chapters 1–20).
- **Likely GT Errors:** None.
- **Likely Parser Errors:** Chapter headers (`CHAPTER I`) are printed in small-caps font identical in size to body text without extra line spacing. Parser's font-size ratio threshold failed to separate them from body paragraphs, triggering fallback to 9 partitions.
- **Ambiguous Cases:** None.
- **Recommended Human Decision:** Keep 21 nodes in GT.

---

## Ground Truth Summary Matrix

| Book ID | Book Title | Current GT Node Count | Recommended Curated Node Count | Dominant Alignment Issue |
|---|---|---|---|---|
| `001_middlemarch` | *Middlemarch* | 10 | 96 (8 Books, 86 Ch, 2 Matter) | Scanned PDF / GT Truncation |
| `002_frankenstein` | *Frankenstein* | 30 | 30 (Intro, Pref, 4 Let, 24 Ch) | Roman vs Arabic; Intro sub-pages |
| `003_the_time_machine` | *The Time Machine* | 17 | 17 (16 Chapters, Epilogue) | Clean alignment; TOC noise |
| `004_les_miserables` | *Les Misérables* | 5 | ~55 (5 Vols, ~50 Books) | **Major Granularity Mismatch (GT too coarse)** |
| `005_sherlock_holmes` | *Sherlock Holmes* | 12 | 12 (12 Adventures) | Parser keyword gap (`ADVENTURE`) |
| `006_alices_adventures` | *Alice in Wonderland* | 12 | 12 (12 Chapters) | Typography / dropped initials |
| `007_count_of_monte_cristo` | *Monte Cristo (Vol. 1)* | 38 | 38 (38 Chapters) | Clean alignment; OCR noise |
| `008_the_iliad` | *The Iliad* | 28 | 28 primary + apparatus | Apparatus vs Narrative; Running headers |
| `009_moby_dick` | *Moby-Dick* | 138 | 138 (Etym, Extr, 135 Ch, Epil) | **TOC Contamination on p. 13–14** |
| `010_picture_of_dorian_gray` | *Dorian Gray* | 21 | 21 (Preface, 20 Chapters) | Small-caps font size uniformity |
