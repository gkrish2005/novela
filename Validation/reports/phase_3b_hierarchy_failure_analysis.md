# Novela Phase 3B — Hierarchy Failure Analysis & Multi-Tier Architecture Report

**Audit Date:** September 12, 2026  
**Status:** `ITERATION 0 COMPLETE — HIERARCHY FAILURE MECHANISM CONFIRMED`  
**Evaluator Reference:** [`scripts/evaluate_authoritative_benchmark.py`](file:///Users/krishgupta/Desktop/novela/scripts/evaluate_authoritative_benchmark.py)  
**Baseline Snapshot:** [`validation/reports/baseline_snapshot_3a_human_verified.json`](file:///Users/krishgupta/Desktop/novela/validation/reports/baseline_snapshot_3a_human_verified.json)

---

## Executive Summary

In the Phase 3B authoritative baseline, genuine hierarchy evaluation on the **102 strictly matched node pairs** produced:
- **Depth Accuracy:** **`100.00%`**
- **Containment Accuracy:** **`100.00%`**
- **Sibling Order Accuracy:** **`100.00%`**
- **Parent Accuracy:** **`74.51%`** ($76$ correct parents, $26$ incorrect parents)

This report investigates the exact algorithmic mechanism causing **26 parent-assignment failures** and specifies the general multi-tier hierarchy architecture to resolve them in Phase 3B Iteration 6.

---

## 1. Itemized Parent-Assignment Failure Inventory

All 26 parent-assignment failures across the corpus were traced to **two specific false parent entrapment events**:

| Document ID | Node ID | Canonical Title | Canonical Type | Page | Expected Parent | Predicted Parent ID | Predicted Parent Heading | Root Cause |
|---|---|---|---|---|---|---|---|---|
| `008_the_iliad` | `iliad_bm_glossary` | Pronouncing Glossary | `back_matter` | 655 | `ROOT` (None) | `173e54d0` | `1. Texts and Commentaries` (p. 651) | Spurious apparatus section trapped subsequent back matter |
| `009_moby_dick` | `mb_ch_33` | Chapter 33 | `chapter` | 210 | `ROOT` (None) | `df027b14` | `Book III - (Duodecimo)...` (p. 208) | Spurious book division trapped subsequent chapters |
| `009_moby_dick` | `mb_ch_34` | Chapter 34 | `chapter` | 214 | `ROOT` (None) | `df027b14` | `Book III - (Duodecimo)...` (p. 208) | False parent entrapment |
| `009_moby_dick` | `mb_ch_35` | Chapter 35 | `chapter` | 221 | `ROOT` (None) | `df027b14` | `Book III - (Duodecimo)...` (p. 208) | False parent entrapment |
| `009_moby_dick` | `mb_ch_36` | Chapter 36 | `chapter` | 229 | `ROOT` (None) | `df027b14` | `Book III - (Duodecimo)...` (p. 208) | False parent entrapment |
| `009_moby_dick` | `mb_ch_37` | Chapter 37 | `chapter` | 239 | `ROOT` (None) | `df027b14` | `Book III - (Duodecimo)...` (p. 208) | False parent entrapment |
| `009_moby_dick` | `mb_ch_38` | Chapter 38 | `chapter` | 241 | `ROOT` (None) | `df027b14` | `Book III - (Duodecimo)...` (p. 208) | False parent entrapment |
| `009_moby_dick` | `mb_ch_39` | Chapter 39 | `chapter` | 243 | `ROOT` (None) | `df027b14` | `Book III - (Duodecimo)...` (p. 208) | False parent entrapment |
| `009_moby_dick` | `mb_ch_40` | Chapter 40 | `chapter` | 244 | `ROOT` (None) | `df027b14` | `Book III - (Duodecimo)...` (p. 208) | False parent entrapment |
| `009_moby_dick` | `mb_ch_41` | Chapter 41 | `chapter` | 252 | `ROOT` (None) | `df027b14` | `Book III - (Duodecimo)...` (p. 208) | False parent entrapment |
| `009_moby_dick` | `mb_ch_42` | Chapter 42 | `chapter` | 264 | `ROOT` (None) | `df027b14` | `Book III - (Duodecimo)...` (p. 208) | False parent entrapment |
| `009_moby_dick` | `mb_ch_43` | Chapter 43 | `chapter` | 275 | `ROOT` (None) | `df027b14` | `Book III - (Duodecimo)...` (p. 208) | False parent entrapment |
| `009_moby_dick` | `mb_ch_44` | Chapter 44 | `chapter` | 277 | `ROOT` (None) | `df027b14` | `Book III - (Duodecimo)...` (p. 208) | False parent entrapment |
| `009_moby_dick` | `mb_ch_45` | Chapter 45 | `chapter` | 284 | `ROOT` (None) | `df027b14` | `Book III - (Duodecimo)...` (p. 208) | False parent entrapment |
| `009_moby_dick` | `mb_ch_46` | Chapter 46 | `chapter` | 295 | `ROOT` (None) | `df027b14` | `Book III - (Duodecimo)...` (p. 208) | False parent entrapment |
| `009_moby_dick` | `mb_ch_47` | Chapter 47 | `chapter` | 299 | `ROOT` (None) | `df027b14` | `Book III - (Duodecimo)...` (p. 208) | False parent entrapment |
| `009_moby_dick` | `mb_ch_48` | Chapter 48 | `chapter` | 303 | `ROOT` (None) | `df027b14` | `Book III - (Duodecimo)...` (p. 208) | False parent entrapment |
| `009_moby_dick` | `mb_ch_50` | Chapter 50 | `chapter` | 319 | `ROOT` (None) | `df027b14` | `Book III - (Duodecimo)...` (p. 208) | False parent entrapment |
| `009_moby_dick` | `mb_ch_51` | Chapter 51 | `chapter` | 323 | `ROOT` (None) | `df027b14` | `Book III - (Duodecimo)...` (p. 208) | False parent entrapment |
| `009_moby_dick` | `mb_ch_52` | Chapter 52 | `chapter` | 328 | `ROOT` (None) | `df027b14` | `Book III - (Duodecimo)...` (p. 208) | False parent entrapment |
| `009_moby_dick` | `mb_ch_53` | Chapter 53 | `chapter` | 331 | `ROOT` (None) | `df027b14` | `Book III - (Duodecimo)...` (p. 208) | False parent entrapment |
| `009_moby_dick` | `mb_ch_55` | Chapter 55 | `chapter` | 361 | `ROOT` (None) | `df027b14` | `Book III - (Duodecimo)...` (p. 208) | False parent entrapment |
| `009_moby_dick` | `mb_ch_56` | Chapter 56 | `chapter` | 367 | `ROOT` (None) | `df027b14` | `Book III - (Duodecimo)...` (p. 208) | False parent entrapment |
| `009_moby_dick` | `mb_ch_57` | Chapter 57 | `chapter` | 372 | `ROOT` (None) | `df027b14` | `Book III - (Duodecimo)...` (p. 208) | False parent entrapment |
| `009_moby_dick` | `mb_ch_59` | Chapter 59 | `chapter` | 380 | `ROOT` (None) | `df027b14` | `Book III - (Duodecimo)...` (p. 208) | False parent entrapment |
| `009_moby_dick` | `mb_ch_60` | Chapter 60 | `chapter` | 383 | `ROOT` (None) | `df027b14` | `Book III - (Duodecimo)...` (p. 208) | False parent entrapment |

---

## 2. Root-Cause Analysis: The "False Parent Entrapment" Mechanism

### How 25 Moby-Dick Chapters Became Children of a Cetology Sub-Book:
1. In `009_moby_dick`, Chapter XXXII (*Cetology*, page 194) contains Herman Melville's humorous classification of whales:
   - Page 198: `Book I - (Folio)...`
   - Page 204: `Book II - (Octavo)...`
   - Page 208: `Book III - (Duodecimo)...`
2. The parser detected `Book III - (Duodecimo)` as a structural `NodeType.BOOK` (Level 1 / container node).
3. The hierarchy builder in `backend/app/services/document/hierarchy.py` operates as a stateful stack:
   ```python
   # When a BOOK node is encountered, it is pushed onto the parent stack:
   if node.node_type in (NodeType.VOLUME, NodeType.BOOK, NodeType.PART):
       current_container = node
   ```
4. Because the book never emitted an explicit "End of Book" or higher-level container, `current_container` remained set to `Book III` (`df027b14`) for the remainder of the volume.
5. All subsequent narrative chapters (`Chapter 33: The Specksynder` through `Chapter 60: The Line`) were automatically attached as children of `Book III`!

### How the Iliad Glossary Became a Child of a Bibliography Subsection:
1. In `008_the_iliad`, page 651 contains `SUGGESTIONS FOR FURTHER READING` with subsection `1. Texts and Commentaries`.
2. The parser created a container node `173e54d0` for `1. Texts and Commentaries`.
3. When `Pronouncing Glossary` appeared on page 655, the stack failed to pop back to `ROOT` because `1. Texts and Commentaries` was not bounded by an explicit parent closure.

---

## 3. General Multi-Tier Hierarchy Architecture Specification

To prevent false parent entrapment and support arbitrary hierarchy depths (e.g. *Les Misérables* Volume $\rightarrow$ Book $\rightarrow$ Chapter), the hierarchy engine in `hierarchy.py` will be redesigned in Phase 3B Iteration 6 around **two universal principles**:

### Universal Principle 1: Bounded Container Scopes & Sibling Resets
A container node (e.g. `Volume` or `Book` or `Section`) can only capture children within its legitimate scope:
- A `Book` cannot capture sibling `Chapters` that began before the book, nor can an internal sub-book inside a chapter capture subsequent top-level chapters.
- Container boundaries must be bounded by:
  1. Occurrence of a sibling or higher-level node (e.g. next `Chapter` with matching numbering progression pops internal sub-containers).
  2. Transition to distinct functional zones (e.g. `Back Matter` automatically resets all narrative containers to `ROOT`).

### Universal Principle 2: Arbitrary-Depth DocumentTree Support
The DocumentTree model will support arbitrary recursive nesting without hardcoding depth assumptions:

```
Document
 ├── Front Matter
 │    ├── Preface
 │    └── Introduction
 ├── Volume I
 │    ├── Book I
 │    │    ├── Chapter 1
 │    │    └── Chapter 2
 │    └── Book II
 │         ├── Chapter 3
 │         └── Chapter 4
 ├── Volume II
 │    └── ...
 └── Back Matter
      ├── Notes
      └── Glossary
```

---

## 4. Status & Readiness

- **Hierarchy Failure Mechanism:** **`CONCLUDED & VERIFIED (False Parent Stack Entrapment)`**
- **Action Plan:** Ready for implementation in **Phase 3B Iteration 6** after suppression passes (Iterations 1–3) and recall passes (Iterations 4–5) are complete.
