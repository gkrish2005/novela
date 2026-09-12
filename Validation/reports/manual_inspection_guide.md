# Human Review & Manual Inspection Guide

**Date:** September 12, 2026  
**Auditor:** Antigravity Engineering  
**Purpose:** Compact reference guide for human reviewers auditing structural candidates, edge cases, and failure patterns in the Novela Document Engine.

---

## 1. Missed Headings (False Negatives)

### Example 1.1: Short Story Collection Title (*The Adventures of Sherlock Holmes*)
- **Document:** `005_sherlock_holmes` (`adventuresofsher001892doyl.pdf`)
- **Page:** 11 (Physical Page 11)
- **Extracted Text Snippet:**
  ```text
  ADVENTURES OF SHERLOCK HOLMES.
  
  ADVENTURE I.—A SCANDAL IN BOHEMIA.
  
  CHAPTER I.
  
  To Sherlock Holmes she is always the woman. I have 
  seldom heard him mention her under any other name...
  ```
- **Parser Behavior:** Missed. Fallback to paragraph partition.
- **Root Cause:** Regex pattern suite only contains `Chapter`, `Book`, `Part`, `Act`, `Scene`; lacks `Adventure`.
- **Reviewer Question:** *Is `ADVENTURE I.—A SCANDAL IN BOHEMIA` the primary structural heading, and `CHAPTER I` a sub-chapter?*

---

### Example 1.2: Small-Caps Header with No Font Contrast (*The Picture of Dorian Gray*)
- **Document:** `010_picture_of_dorian_gray` (`pictureofdoriang0000osca_s9a9.pdf`)
- **Page:** 11 (Physical Page 11)
- **Extracted Text Snippet:**
  ```text
  THE PREFACE
  
  The artist is the creator of beautiful things.
  To reveal art and conceal the artist is art's aim.
  The critic is he who can translate into another manner...
  ```
- **Parser Behavior:** Missed. Font size was 10.0pt (identical to body text).
- **Root Cause:** Font-size ratio threshold requires candidate font to be $> 1.05\times$ body font size when unnumbered.
- **Reviewer Question:** *Should `THE PREFACE` be recognized as front matter based on all-caps formatting and short line length?*

---

### Example 1.3: Epistolary Letters (*Frankenstein*)
- **Document:** `002_frankenstein` (`Shelley_1888_Frankenstein.pdf`)
- **Page:** 18 (Physical Page 18)
- **Extracted Text Snippet:**
  ```text
  FRANKENSTEIN; OR,
  THE MODERN PROMETHEUS
  
  LETTER I.
  To Mrs. SAVILLE, England.
  
  St. Petersburgh, Dec. 11th, 17—.
  You will rejoice to hear that no disaster has accompanied the
  commencement of an enterprise which you have regarded with...
  ```
- **Parser Behavior:** Missed `LETTER I` through `LETTER IV`.
- **Root Cause:** Lexical candidate generator does not match `Letter [IVXLCDM]+`.
- **Reviewer Question:** *Should `LETTER I` through `LETTER IV` be classified as `NodeType.CHAPTER` or `NodeType.SECTION`?*

---

## 2. False Heading Candidates (False Positives)

### Example 2.1: Table of Contents Line with Dot Leaders (*Moby-Dick*)
- **Document:** `009_moby_dick` (`mobydickorwhale01melvuoft.pdf`)
- **Page:** 13 (Physical Page 13)
- **Extracted Text Snippet:**
  ```text
  CONTENTS.
  
  I. Loomings . . . . . . . 1
  II. The Carpet-Bag ...... 8
  III. The Spouter-Inn ..... 14
  IV. The Counterpane ..... 30
  V. Breakfast ....... 36
  ```
- **Parser Behavior:** Detected each line as a `numbered_section` heading (`II. The Carpet-Bag ...... 8`).
- **Root Cause:** Numbered section regex matched Roman numerals with trailing text; TOC page was not suppressed.
- **Reviewer Question:** *Confirm this is TOC noise that should be filtered out by printed TOC suppression.*

---

### Example 2.2: Verso Running Header Bleed (*The Iliad*)
- **Document:** `008_the_iliad` (`homer_the_iliad_...pdf`)
- **Page:** 215 (Physical Page 215)
- **Extracted Text Snippet:**
  ```text
  BOOK FIVE
  
  216  THE ILIAD
  
  Now Pallas Athena gave Tydeus' son Diomedes
  boundless strength and daring, so the man would stand out...
  ```
- **Parser Behavior:** Detected `BOOK FIVE` at top of page as a new Book heading (duplicate of Book 5 on page 201).
- **Root Cause:** Running header vertical position was at $y = 0.13$, exceeding the 12% top margin threshold.
- **Reviewer Question:** *Confirm that running headers repeating the current book name must not trigger section splits.*

---

## 3. Ambiguous Editorial & Scholarly Structures

### Example 3.1: Sub-Pagination Romanettes in Special Matter (*Frankenstein*)
- **Document:** `002_frankenstein` (`Shelley_1888_Frankenstein.pdf`)
- **Page:** 6 (Physical Page 6)
- **Extracted Text Snippet:**
  ```text
  INTRODUCTION.
  vii
  
  It is not singular that, as the daughter of two persons of
  distinguished literary celebrity, I should very early in life...
  ```
- **Parser Behavior:** Extracted `Introduction: vii`, `Introduction: ix`, `Introduction: xi` as separate sections.
- **Root Cause:** Header/footer classifier grouped page number romanettes into the introduction block.
- **Reviewer Question:** *Should multi-page introductions remain a single contiguous node regardless of page number markers?*

---

### Example 3.2: Scholarly Apparatus Essays (*The Iliad*)
- **Document:** `008_the_iliad` (`homer_the_iliad_...pdf`)
- **Page:** 45 (Physical Page 45)
- **Extracted Text Snippet:**
  ```text
  THE SPEECH OF HOMER
  
  Bernard Knox
  
  The language of the Iliad and the Odyssey is unique in Greek
  literature. It is a composite dialect that was never spoken...
  ```
- **Parser Behavior:** Detected as `NodeType.SECTION` under Introduction.
- **Reviewer Question:** *Should translator/scholar essays preceding classical works be kept as `front_matter` children or ignored from narrative audiobooks?*

---

## 4. Multi-Level Granularity Verification

### Example 4.1: Volume vs Book vs Chapter (*Les Misérables*)
- **Document:** `004_les_miserables` (`[Hugo_Victor]_Les_Miserables.pdf`)
- **Page:** 3 (Physical Page 3)
- **Extracted Text Snippet:**
  ```text
  LES MISÉRABLES
  
  VOLUME I—FANTINE.
  
  BOOK FIRST.—AN UPRIGHT MAN.
  
  CHAPTER I—M. MYRIEL.
  
  In 1815, M. Charles-François-Bienvenu Myriel was Bishop of D——.
  He was an old man of about seventy-five years of age...
  ```
- **Parser Behavior:** Detected `Book SECOND`, `Chapter I: M. Myriel` (Level 2/3), but GT only expected `Volume I—FANTINE` (Level 1).
- **Reviewer Action Required:** Update Ground Truth to reflect 3-level nesting:
  ```json
  {
    "type": "part",
    "title": "VOLUME I—FANTINE",
    "children": [
      {
        "type": "book",
        "title": "BOOK FIRST—AN UPRIGHT MAN",
        "children": [
          {"type": "chapter", "title": "CHAPTER I—M. MYRIEL"}
        ]
      }
    ]
  }
  ```

---

## 5. Fallback Partitions vs Semantic Headings

### Example 5.1: Zero-Loss Density Partitioning (*Alice in Wonderland*)
- **Document:** `006_alices_adventures` (`alicesadventures00carr_20.pdf`)
- **Page:** 1–226
- **Parser Output:**
  ```json
  {
    "node_type": "section",
    "title": "Section 1",
    "detection_method": "paragraph_density_partition",
    "confidence": 0.45,
    "uncertain": true,
    "uncertainty_reasons": ["Partitioned by paragraph density in absence of explicit headings"]
  }
  ```
- **Validation Rule:** These 9 sections are content partitions created to ensure zero text loss. They are **not** semantic headings and must **never** be penalized as false-positive heading detections.
