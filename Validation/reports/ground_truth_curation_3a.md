# Novela Phase 3A — Ground Truth Curation Report

**Date:** September 12, 2026  
**Status:** `PRELIMINARY — CANDIDATE GT — NOT HUMAN VERIFIED`  
**Schema Definition:** [`validation/schema/canonical_schema.json`](file:///Users/krishgupta/Desktop/novela/validation/schema/canonical_schema.json)  
**Curator Script:** [`scripts/curate_candidate_ground_truth.py`](file:///Users/krishgupta/Desktop/novela/scripts/curate_candidate_ground_truth.py)  
**Target Repository:** `/Users/krishgupta/Desktop/novela`

---

## Executive Summary

Phase 3A establishes a machine-curated, edition-accurate **Candidate Ground Truth (GT)** repository across all 10 benchmark corpus documents in `validation/Corpus/`. 

This replaces the preliminary, unvalidated 1-tier strings from the initial baseline pass with structured canonical node hierarchies adhering to JSON Schema Draft-07.

> [!IMPORTANT]
> **Methodological Invariant:**  
> In accordance with Phase 3A constraints, **`human_verified` remains strictly `false` across all 10 documents and all 286 constituent nodes**. All nodes are categorized as `verification_status: "candidate"`.

---

## 1. Corpus-Wide Candidate GT Inventory

| Metric | Count | Description |
|---|---|---|
| **Total Benchmark Documents** | **10** | 9 native text PDFs, 1 scanned bitmap PDF |
| **Total Candidate Nodes** | **286** | Hierarchical structural units curated against actual PDF editions |
| **Human-Verified Nodes** | **0** | Strictly zero pending physical human sign-off |
| **Disputed Nodes** | **0** | Unresolved boundary disputes tracked in review queue |
| **Active Scored Nodes** | **276** | Nodes evaluated under active benchmark metric passes |
| **Benchmark-Deferred Candidate Nodes** | **10** | Structural nodes recognized but deferred (e.g. Middlemarch image scan) |
| **Runtime Deferred Scopes** | **31** | Parser-detected nodes in deferred levels (e.g. Les Misérables chapters) |

---

## 2. Per-Document Curation Breakdown

### `001_middlemarch` (*Middlemarch*)
- **Source File:** `2015.42254.Middlemarch.pdf` (638 pages, 54.4 MB)
- **Edition Scope:** Scanned bitmap archive edition (~1871–1872). Embedded text characters: `0`.
- **Benchmark Status:** `extraction_limitation`
- **Candidate Nodes:** **10** (Prelude, Books I–VIII, Finale)
- **Scored Levels:** `[]` (None scored until OCR is integrated)
- **Deferred Levels:** `["book", "chapter"]`
- **Curation Notes:** Structure is cataloged from standard literary reference editions. Because raw extraction yields 0 text characters, this document is isolated in the benchmark matrix to avoid false parser penalties.

### `002_frankenstein` (*Frankenstein; or, The Modern Prometheus*)
- **Source File:** `Shelley_1888_Frankenstein.pdf` (316 pages, 7.5 MB)
- **Edition Scope:** Routledge Pocket Library edition (1888).
- **Benchmark Status:** `active`
- **Candidate Nodes:** **30**
  - `introduction`: 1 (Author's 1831 Introduction, pp. 4–11)
  - `preface`: 1 (Original 1818 Preface by P.B. Shelley, pp. 12–14)
  - `letter`: 4 (Walton Letters I–IV, pp. 15–37)
  - `chapter`: 24 (Chapters I–XXIV, pp. 38–316)
- **Scored Levels:** `["introduction", "preface", "letter", "chapter"]`
- **Deferred Levels:** `[]`
- **Curation Notes:** Walton Letters are explicitly modeled as type `letter` rather than generic chapters. Roman numerals in headings are aligned with the 1888 typography.

### `003_the_time_machine` (*The Time Machine*)
- **Source File:** `Wells_1922_Time_Machine.pdf` (221 pages, 3.2 MB)
- **Edition Scope:** Heinemann 1922 edition.
- **Benchmark Status:** `active`
- **Candidate Nodes:** **17** (Chapters 1–16 + Epilogue)
- **Scored Levels:** `["chapter", "epilogue"]`
- **Deferred Levels:** `[]`
- **Curation Notes:** Standard 16-chapter narrative with terminal Epilogue. Physical PDF pages verified from page 6 through page 221.

### `004_les_miserables` (*Les Misérables*)
- **Source File:** `[Hugo_Victor]_Les_Miserables.pdf` (1,279 pages, 4.0 MB)
- **Edition Scope:** Complete unabridged single-volume edition.
- **Benchmark Status:** `active`
- **Candidate Nodes:** **53** (5 Volumes + 48 Books)
  - Volume I (*Fantine*): 8 Books (pp. 20–281)
  - Volume II (*Cosette*): 8 Books (pp. 282–519)
  - Volume III (*Marius*): 8 Books (pp. 520–727)
  - Volume IV (*The Idyll in the Rue Plumet...*): 15 Books (pp. 728–1029)
  - Volume V (*Jean Valjean*): 9 Books (pp. 1030–1279)
- **Scored Levels:** `["volume", "book"]` (Option A hierarchy)
- **Deferred Levels:** `["chapter"]` (~365 sub-chapters deferred from scoring)
- **Curation Notes:** Implemented Option A (Volume $\rightarrow$ Book hierarchy). Chapter-level nodes detected by the parser (31 nodes in baseline pass) are classified as `out_of_scope` rather than penalized as false positives.

### `005_sherlock_holmes` (*The Adventures of Sherlock Holmes*)
- **Source File:** `adventuresofsher001892doyl.pdf` (332 pages, 29.0 MB)
- **Edition Scope:** George Newnes first book edition (1892).
- **Benchmark Status:** `active`
- **Candidate Nodes:** **12** (Adventures I–XII, pp. 9–332)
- **Scored Levels:** `["adventure"]`
- **Deferred Levels:** `[]`
- **Curation Notes:** Modelled as a flat collection of 12 distinct short-story adventures. Headings in the PDF are styled as `"ADVENTURE I. A SCANDAL IN BOHEMIA"`.

### `006_alices_adventures` (*Alice's Adventures in Wonderland*)
- **Source File:** `alicesadventures00carr_20.pdf` (226 pages, 126.3 MB)
- **Edition Scope:** Macmillan illustrated edition with John Tenniel engravings.
- **Benchmark Status:** `active`
- **Candidate Nodes:** **12** (Chapters 1–12, pp. 13–226)
- **Scored Levels:** `["chapter"]`
- **Deferred Levels:** `[]`
- **Curation Notes:** Single-tier 12-chapter narrative. Source PDF features large illuminated drop-cap initials on opening chapter paragraphs.

### `007_count_of_monte_cristo` (*The Count of Monte-Cristo, Vol. 1*)
- **Source File:** `countofmontecris01duma.pdf` (360 pages, 23.8 MB)
- **Edition Scope:** Walter Scott edition (Volume 1 of multi-volume set).
- **Benchmark Status:** `active`
- **Candidate Nodes:** **38** (Chapters 1–38, *Marseilles—The Arrival* through *The Compact*)
- **Scored Levels:** `["chapter"]`
- **Deferred Levels:** `[]`
- **Curation Notes:** The benchmark PDF comprises strictly Volume 1 (ending at Chapter 38 on page 360). Candidate GT is scoped specifically to the 38 chapters present in the physical file, rather than the 117 chapters of the full unabridged work.

### `008_the_iliad` (*The Iliad*)
- **Source File:** `homer_the_iliad_penguin_classics_deluxe_edition-robert-fagles.pdf` (699 pages, 9.3 MB)
- **Edition Scope:** Penguin Classics Deluxe Edition (Translated by Robert Fagles, 1990).
- **Benchmark Status:** `active`
- **Candidate Nodes:** **31**
  - `front_matter`: 3 (Preface pp. 9–14, Knox Introduction pp. 17–64, Translation Note pp. 69–74)
  - `book`: 24 (Primary Narrative Books 1–24, pp. 77–636)
  - `back_matter`: 4 (Notes pp. 637–648, Genealogies pp. 649–650, Further Reading pp. 651–654, Pronouncing Glossary pp. 655–699)
- **Scored Levels:** `["front_matter", "book", "back_matter"]`
- **Deferred Levels:** `["apparatus_subheading"]`
- **Curation Notes:** Clear division between scholarly front matter, 24 narrative books, and scholarly back matter apparatus. Internal thematic sub-headings inside Bernard Knox's introductory essay are deferred.

### `009_moby_dick` (*Moby-Dick; or, The Whale, Vol. 1*)
- **Source File:** `mobydickorwhale01melvuoft.pdf` (394 pages, 28.1 MB)
- **Edition Scope:** Richard Bentley 1851 first English edition (Volume 1 of 3, published as *The Whale*).
- **Benchmark Status:** `active`
- **Candidate Nodes:** **62**
  - `front_matter`: 2 (*Etymology* pp. 15–16, *Extracts* pp. 17–30)
  - `chapter`: 60 (Chapters 1–60, *Loomings* through *The Line*, pp. 31–383)
- **Scored Levels:** `["front_matter", "chapter"]`
- **Deferred Levels:** `[]`
- **Curation Notes:** Physical examination of the source PDF confirms that the file is strictly **Volume 1** (terminating with Chapter LX on page 383). The earlier baseline assumption of 138 nodes (Chapters 1–135 + Epilogue) was a major ground-truth error. Candidate GT is accurately scoped to Volume 1.

### `010_picture_of_dorian_gray` (*The Picture of Dorian Gray*)
- **Source File:** `pictureofdoriang0000osca_s9a9.pdf` (248 pages, 12.6 MB)
- **Edition Scope:** Ward, Lock and Bowden 1891 first novel edition.
- **Benchmark Status:** `active`
- **Candidate Nodes:** **21** (The Preface pp. 5–7, Chapters 1–20 pp. 9–248)
- **Scored Levels:** `["preface", "chapter"]`
- **Deferred Levels:** `[]`
- **Curation Notes:** Single-tier structure comprising Oscar Wilde's aphoristic Preface and 20 numbered body chapters. Headings are styled in small-caps.

---

## 3. Known Uncertainties & Human Review Recommendations

1. **Frankenstein Front Matter & Letters:**
   - Walton Letters I–IV are currently categorized as `letter`. If the parser continues classifying them as `chapter`, determine whether dual-alias scoring (`letter | chapter`) is acceptable.
2. **Iliad Scholarly Back Matter:**
   - Fagles line notes on pp. 637–648 contain numerical line markers (e.g. `1.1`, `9.171`) that trigger false section splits in the parser. Human review must verify that these are non-structural annotations.
3. **Moby-Dick Cetology Sub-Classifications:**
   - Chapter XXXII (*Cetology*) contains internal headings (`Book I - (Folio)`, `Book II - (Octavo)`, `Book III - (Duodecimo)`). Candidate GT treats these as internal sub-sections rather than top-level book divisions.
4. **Monte Cristo Missing Page Offsets:**
   - Specific PDF page offsets for Volume 1 chapters 20–38 should be validated during physical human review.
