# Novela Real-World Baseline — Per-Document Breakdown

> [!WARNING]
> **PRELIMINARY / NOT HUMAN VERIFIED**
> Detailed inspection records for each of the 10 corpus books under the Phase 3 baseline run.

---

## Document `001_middlemarch`: *Middlemarch*

- **Filename:** `2015.42254.Middlemarch.pdf`
- **Author:** George Eliot
- **Pages:** 638
- **Raw Character Count:** 0
- **Average Chars/Page:** 0.0
- **Extraction Status:** `image_only`
- **Parser Runtime:** 83.61s (7.6 pages/sec)
- **Semantic Nodes Detected:** 0
- **Fallback Partitions:** 0
- **Proposed Ground Truth Nodes:** 10
- **Human Verification Required:** Yes (`human_verified = false`)
- **Document Evaluation Status:** **EXTRACTION_LIMITATION**

### Structural Output Breakdown
- **True Positives (TP):** 0
- **False Positives (FP):** 0
- **False Negatives (FN):** 0
- **Preliminary F1 Score:** 0.0%

### Detected Semantic Headings Sample (First 15):
*Zero text characters extracted (image-only scanned PDF).*

### Ground Truth Comparison Table:

*Comparison skipped due to extraction limitation (image-only scan).*

---

## Document `002_frankenstein`: *Frankenstein; or, The Modern Prometheus*

- **Filename:** `Shelley_1888_Frankenstein.pdf`
- **Author:** Mary Wollstonecraft Shelley
- **Pages:** 316
- **Raw Character Count:** 587,662
- **Average Chars/Page:** 1859.7
- **Extraction Status:** `native_text`
- **Parser Runtime:** 23.07s (13.7 pages/sec)
- **Semantic Nodes Detected:** 30
- **Fallback Partitions:** 0
- **Proposed Ground Truth Nodes:** 30
- **Human Verification Required:** Yes (`human_verified = false`)
- **Document Evaluation Status:** **Minor Errors**

### Structural Output Breakdown
- **True Positives (TP):** 25
- **False Positives (FP):** 4
- **False Negatives (FN):** 5
- **Preliminary F1 Score:** 84.7%

### Detected Semantic Headings Sample (First 15):
1. `[front_matter]` **Front Matter** (p. 1–3, conf=0.90, method=`leading_document_span`)
2. `[introduction]` **Introduction** (p. 4–5, conf=1.00, method=`lexical_special_matter`)
3. `[introduction]` **Introduction: vii** (p. 6–7, conf=0.95, method=`lexical_special_matter`)
4. `[introduction]` **Introduction: ix** (p. 8–9, conf=0.95, method=`lexical_special_matter`)
5. `[introduction]` **Introduction: xi** (p. 10–11, conf=0.95, method=`lexical_special_matter`)
6. `[preface]` **Preface** (p. 12–13, conf=1.00, method=`lexical_special_matter`)
7. `[preface]` **Preface: XV** (p. 14–38, conf=0.95, method=`lexical_special_matter`)
8. `[chapter]` **Chapter I** (p. 38–45, conf=0.90, method=`lexical_chapter`)
9. `[chapter]` **Chapter II** (p. 45–54, conf=0.90, method=`lexical_chapter`)
10. `[chapter]` **Chapter III** (p. 54–65, conf=0.90, method=`lexical_chapter`)
11. `[chapter]` **Chapter IV** (p. 65–75, conf=0.90, method=`lexical_chapter`)
12. `[chapter]` **Chapter V** (p. 75–84, conf=0.95, method=`lexical_chapter`)
13. `[chapter]` **Chapter VI** (p. 84–94, conf=0.90, method=`lexical_chapter`)
14. `[chapter]` **Chapter VII** (p. 94–108, conf=0.90, method=`lexical_chapter`)
15. `[chapter]` **Chapter VIII** (p. 108–120, conf=0.90, method=`lexical_chapter`)

### Ground Truth Comparison Table:

| Status | Expected Ground Truth | Predicted Heading | Page | Class Match | Parent Match | Conf | Method |
|---|---|---|---|---|---|---|---|
| **TP** | Introduction | Introduction | 4 | Yes | Yes | 1.00 | `lexical_special_matter` |
| **FP** | — | Introduction: vii | 6 | No | No | 0.95 | `lexical_special_matter` |
| **FP** | — | Introduction: ix | 8 | No | No | 0.95 | `lexical_special_matter` |
| **FP** | — | Introduction: xi | 10 | No | No | 0.95 | `lexical_special_matter` |
| **TP** | Preface | Preface | 12 | Yes | Yes | 1.00 | `lexical_special_matter` |
| **FP** | — | Preface: XV | 14 | No | No | 0.95 | `lexical_special_matter` |
| **TP** | Chapter 1 | Chapter I | 38 | Yes | Yes | 0.90 | `lexical_chapter` |
| **TP** | Chapter 2 | Chapter II | 45 | Yes | Yes | 0.90 | `lexical_chapter` |
| **TP** | Chapter 3 | Chapter III | 54 | Yes | Yes | 0.90 | `lexical_chapter` |
| **TP** | Chapter 4 | Chapter IV | 65 | Yes | Yes | 0.90 | `lexical_chapter` |
| **TP** | Chapter 5 | Chapter V | 75 | Yes | Yes | 0.95 | `lexical_chapter` |
| **TP** | Chapter 6 | Chapter VI | 84 | Yes | Yes | 0.90 | `lexical_chapter` |
| **TP** | Chapter 7 | Chapter VII | 94 | Yes | Yes | 0.90 | `lexical_chapter` |
| **TP** | Chapter 8 | Chapter VIII | 108 | Yes | Yes | 0.90 | `lexical_chapter` |
| **TP** | Chapter 9 | Chapter IX | 120 | Yes | Yes | 0.90 | `lexical_chapter` |
| **TP** | Chapter 10 | Chapter X: I SPENT the following day roaming through the | 129 | Yes | Yes | 0.97 | `lexical_chapter` |
| **TP** | Chapter 11 | Chapter XI | 138 | Yes | Yes | 0.90 | `lexical_chapter` |
| **TP** | Chapter 12 | Chapter XII | 150 | Yes | Yes | 0.90 | `lexical_chapter` |
| **TP** | Chapter 13 | Chapter XIII | 158 | Yes | Yes | 0.90 | `lexical_chapter` |
| **TP** | Chapter 14 | Chapter XIV | 167 | Yes | Yes | 0.90 | `lexical_chapter` |
| **TP** | Chapter 15 | Chapter XV | 174 | Yes | Yes | 0.95 | `lexical_chapter` |
| **TP** | Chapter 17 | Chapter XVII | 200 | Yes | Yes | 0.85 | `lexical_chapter` |
| **TP** | Chapter 18 | Chapter XVIII | 207 | Yes | Yes | 0.90 | `lexical_chapter` |
| **TP** | Chapter 19 | Chapter XIX | 219 | Yes | Yes | 0.90 | `lexical_chapter` |
| **TP** | Chapter 20 | Chapter XX | 229 | Yes | Yes | 0.95 | `lexical_chapter` |
| **TP** | Chapter 21 | Chapter XXI | 243 | Yes | Yes | 0.85 | `lexical_chapter` |
| **TP** | Chapter 22 | Chapter XXII | 258 | Yes | Yes | 0.85 | `lexical_chapter` |
| **TP** | Chapter 23 | Chapter XXIII | 271 | Yes | Yes | 0.85 | `lexical_chapter` |
| **TP** | Chapter 24 | Chapter XXIV | 282 | Yes | Yes | 0.90 | `lexical_chapter` |
| **FN** | Letter I | — | 0 | No | No | 0.00 | `missed` |
| **FN** | Letter II | — | 0 | No | No | 0.00 | `missed` |
| **FN** | Letter III | — | 0 | No | No | 0.00 | `missed` |
| **FN** | Letter IV | — | 0 | No | No | 0.00 | `missed` |
| **FN** | Chapter 16 | — | 0 | No | No | 0.00 | `missed` |

---

## Document `003_the_time_machine`: *The Time Machine*

- **Filename:** `Wells_1922_Time_Machine.pdf`
- **Author:** H. G. Wells
- **Pages:** 221
- **Raw Character Count:** 245,124
- **Average Chars/Page:** 1109.2
- **Extraction Status:** `native_text`
- **Parser Runtime:** 17.65s (12.5 pages/sec)
- **Semantic Nodes Detected:** 16
- **Fallback Partitions:** 0
- **Proposed Ground Truth Nodes:** 17
- **Human Verification Required:** Yes (`human_verified = false`)
- **Document Evaluation Status:** **Minor Errors**

### Structural Output Breakdown
- **True Positives (TP):** 13
- **False Positives (FP):** 2
- **False Negatives (FN):** 4
- **Preliminary F1 Score:** 81.2%

### Detected Semantic Headings Sample (First 15):
1. `[front_matter]` **Front Matter** (p. 1–5, conf=0.90, method=`leading_document_span`)
2. `[chapter]` **Chapter vii** (p. 5–6, conf=0.95, method=`lexical_chapter`)
3. `[chapter]` **Chapter I** (p. 6–29, conf=0.95, method=`lexical_chapter`)
4. `[chapter]` **Chapter II** (p. 30–42, conf=1.00, method=`lexical_chapter`)
5. `[chapter]` **Chapter III** (p. 43–56, conf=1.00, method=`lexical_chapter`)
6. `[chapter]` **Chapter IV** (p. 57–67, conf=1.00, method=`lexical_chapter`)
7. `[chapter]` **Chapter V** (p. 68–83, conf=1.00, method=`lexical_chapter`)
8. `[chapter]` **Chapter VI** (p. 84–96, conf=1.00, method=`lexical_chapter`)
9. `[chapter]` **Chapter VII** (p. 97–124, conf=1.00, method=`lexical_chapter`)
10. `[chapter]` **Chapter VIII** (p. 125–138, conf=1.00, method=`lexical_chapter`)
11. `[chapter]` **Chapter IX** (p. 139–155, conf=1.00, method=`lexical_chapter`)
12. `[chapter]` **Chapter X** (p. 156–172, conf=1.00, method=`lexical_chapter`)
13. `[chapter]` **Chapter XI** (p. 173–189, conf=1.00, method=`lexical_chapter`)
14. `[chapter]` **Chapter XI** (p. 190–197, conf=0.95, method=`lexical_chapter`)
15. `[chapter]` **Chapter XIII** (p. 197–211, conf=0.95, method=`lexical_chapter`)

### Ground Truth Comparison Table:

| Status | Expected Ground Truth | Predicted Heading | Page | Class Match | Parent Match | Conf | Method |
|---|---|---|---|---|---|---|---|
| **TP** | Chapter 7 | Chapter vii | 5 | Yes | Yes | 0.95 | `lexical_chapter` |
| **TP** | Chapter 1 | Chapter I | 6 | Yes | Yes | 0.95 | `lexical_chapter` |
| **TP** | Chapter 2 | Chapter II | 30 | Yes | Yes | 1.00 | `lexical_chapter` |
| **TP** | Chapter 3 | Chapter III | 43 | Yes | Yes | 1.00 | `lexical_chapter` |
| **TP** | Chapter 4 | Chapter IV | 57 | Yes | Yes | 1.00 | `lexical_chapter` |
| **TP** | Chapter 5 | Chapter V | 68 | Yes | Yes | 1.00 | `lexical_chapter` |
| **TP** | Chapter 6 | Chapter VI | 84 | Yes | Yes | 1.00 | `lexical_chapter` |
| **FP** | — | Chapter VII | 97 | No | No | 1.00 | `lexical_chapter` |
| **TP** | Chapter 8 | Chapter VIII | 125 | Yes | Yes | 1.00 | `lexical_chapter` |
| **TP** | Chapter 9 | Chapter IX | 139 | Yes | Yes | 1.00 | `lexical_chapter` |
| **TP** | Chapter 10 | Chapter X | 156 | Yes | Yes | 1.00 | `lexical_chapter` |
| **TP** | Chapter 11 | Chapter XI | 173 | Yes | Yes | 1.00 | `lexical_chapter` |
| **FP** | — | Chapter XI | 190 | No | No | 0.95 | `lexical_chapter` |
| **TP** | Chapter 13 | Chapter XIII | 197 | Yes | Yes | 0.95 | `lexical_chapter` |
| **TP** | Chapter 14 | Chapter XIV | 212 | Yes | Yes | 1.00 | `lexical_chapter` |
| **FN** | Chapter 12 | — | 0 | No | No | 0.00 | `missed` |
| **FN** | Chapter 15 | — | 0 | No | No | 0.00 | `missed` |
| **FN** | Chapter 16 | — | 0 | No | No | 0.00 | `missed` |
| **FN** | Epilogue | — | 0 | No | No | 0.00 | `missed` |

---

## Document `004_les_miserables`: *Les Misérables*

- **Filename:** `[Hugo_Victor]_Les_Miserables.pdf`
- **Author:** Victor Hugo
- **Pages:** 1279
- **Raw Character Count:** 3,085,924
- **Average Chars/Page:** 2412.8
- **Extraction Status:** `native_text`
- **Parser Runtime:** 8.68s (147.4 pages/sec)
- **Semantic Nodes Detected:** 35
- **Fallback Partitions:** 0
- **Proposed Ground Truth Nodes:** 5
- **Human Verification Required:** Yes (`human_verified = false`)
- **Document Evaluation Status:** **Critical Failure**

### Structural Output Breakdown
- **True Positives (TP):** 0
- **False Positives (FP):** 34
- **False Negatives (FN):** 5
- **Preliminary F1 Score:** 0.0%

### Detected Semantic Headings Sample (First 15):
1. `[front_matter]` **Front Matter** (p. 3–7, conf=0.90, method=`leading_document_span`)
2. `[chapter]` **Chapter vi** (p. 8–9, conf=0.85, method=`lexical_chapter`)
3. `[chapter]` **Chapter vii** (p. 9–9, conf=0.90, method=`lexical_chapter`)
4. `[preface]` **Preface** (p. 11–15, conf=0.90, method=`lexical_special_matter`)
5. `[chapter]` **Chapter xiii** (p. 15–15, conf=0.85, method=`lexical_chapter`)
6. `[chapter]` **Chapter xiv: Book** (p. 16–68, conf=0.92, method=`lexical_chapter`)
7. `[book]` **Book SECOND** (p. 69–142, conf=0.85, method=`lexical_book`)
8. `[chapter]` **Book Fourth** (p. 143–154, conf=0.78, method=`typography_prominence`)
9. `[chapter]` **Book Fifth** (p. 155–191, conf=0.78, method=`typography_prominence`)
10. `[chapter]` **Javert** (p. 191–201, conf=0.78, method=`typography_prominence`)
11. `[chapter]` **Book Seventh** (p. 202–290, conf=0.78, method=`typography_prominence`)
12. `[chapter]` **Chapter IV: A** (p. 290–390, conf=0.92, method=`lexical_chapter`)
13. `[chapter]` **Book Fourth** (p. 391–459, conf=0.78, method=`typography_prominence`)
14. `[chapter]` **Book Seventh** (p. 460–519, conf=0.78, method=`typography_prominence`)
15. `[chapter]` **Book First** (p. 520–577, conf=0.78, method=`typography_prominence`)

### Ground Truth Comparison Table:

| Status | Expected Ground Truth | Predicted Heading | Page | Class Match | Parent Match | Conf | Method |
|---|---|---|---|---|---|---|---|
| **FP** | — | Chapter vi | 8 | No | No | 0.85 | `lexical_chapter` |
| **FP** | — | Chapter vii | 9 | No | No | 0.90 | `lexical_chapter` |
| **FP** | — | Preface | 11 | No | No | 0.90 | `lexical_special_matter` |
| **FP** | — | Chapter xiii | 15 | No | No | 0.85 | `lexical_chapter` |
| **FP** | — | Chapter xiv: Book | 16 | No | No | 0.92 | `lexical_chapter` |
| **FP** | — | Book SECOND | 69 | No | No | 0.85 | `lexical_book` |
| **FP** | — | Book Fourth | 143 | No | No | 0.78 | `typography_prominence` |
| **FP** | — | Book Fifth | 155 | No | No | 0.78 | `typography_prominence` |
| **FP** | — | Javert | 191 | No | No | 0.78 | `typography_prominence` |
| **FP** | — | Book Seventh | 202 | No | No | 0.78 | `typography_prominence` |
| **FP** | — | Chapter IV: A | 290 | No | No | 0.92 | `lexical_chapter` |
| **FP** | — | Book Fourth | 391 | No | No | 0.78 | `typography_prominence` |
| **FP** | — | Book Seventh | 460 | No | No | 0.78 | `typography_prominence` |
| **FP** | — | Book First | 520 | No | No | 0.78 | `typography_prominence` |
| **FP** | — | Book Fourth | 578 | No | No | 0.78 | `typography_prominence` |
| **FP** | — | Book Eighth | 646 | No | No | 0.78 | `typography_prominence` |
| **FP** | — | M. Leblanc had written the whole. Thénardier added: | 712 | No | No | 0.80 | `numbered_section` |
| **FP** | — | M. Leblanc erased the three words. | 713 | No | No | 0.80 | `numbered_section` |
| **FP** | — | Book First | 728 | No | No | 0.78 | `typography_prominence` |
| **FP** | — | Book SECOND | 760 | No | No | 0.85 | `lexical_book` |
| **FP** | — | Eponine | 760 | No | No | 0.78 | `typography_prominence` |
| **FP** | — | Book Third | 776 | No | No | 0.78 | `typography_prominence` |
| **FP** | — | Book Fourth | 808 | No | No | 0.78 | `typography_prominence` |
| **FP** | — | Aid From Above | 808 | No | No | 0.78 | `typography_prominence` |
| **FP** | — | M. Mabeuf, very much startled, carried the thing to his governess. | 816 | No | No | 0.75 | `numbered_section` |
| **FP** | — | M. Gillenormand rang. Basque half opened the door. | 912 | No | No | 0.80 | `numbered_section` |
| **FP** | — | Book Ninth | 918 | No | No | 0.78 | `typography_prominence` |
| **FP** | — | Book Eleventh | 944 | No | No | 0.78 | `typography_prominence` |
| **FP** | — | The Hurricane | 944 | No | No | 0.78 | `typography_prominence` |
| **FP** | — | Corinth | 956 | No | No | 0.78 | `typography_prominence` |
| **FP** | — | Book Thirteenth | 985 | No | No | 0.78 | `typography_prominence` |
| **FP** | — | Book Fourteenth | 995 | No | No | 0.78 | `typography_prominence` |
| **FP** | — | Book Fifteenth | 1012 | No | No | 0.78 | `typography_prominence` |
| **FP** | — | Book First | 1030 | No | No | 0.78 | `typography_prominence` |
| **FN** | Volume I: Fantine | — | 0 | No | No | 0.00 | `missed` |
| **FN** | Volume II: Cosette | — | 0 | No | No | 0.00 | `missed` |
| **FN** | Volume III: Marius | — | 0 | No | No | 0.00 | `missed` |
| **FN** | Volume IV: The Idyll in the Rue Plumet and the Epic in the Rue St. Denis | — | 0 | No | No | 0.00 | `missed` |
| **FN** | Volume V: Jean Valjean | — | 0 | No | No | 0.00 | `missed` |

---

## Document `005_sherlock_holmes`: *The Adventures of Sherlock Holmes*

- **Filename:** `adventuresofsher001892doyl.pdf`
- **Author:** Arthur Conan Doyle
- **Pages:** 332
- **Raw Character Count:** 719,728
- **Average Chars/Page:** 2167.9
- **Extraction Status:** `native_text`
- **Parser Runtime:** 63.25s (5.2 pages/sec)
- **Semantic Nodes Detected:** 0
- **Fallback Partitions:** 9
- **Proposed Ground Truth Nodes:** 12
- **Human Verification Required:** Yes (`human_verified = false`)
- **Document Evaluation Status:** **Critical Failure**

### Structural Output Breakdown
- **True Positives (TP):** 0
- **False Positives (FP):** 0
- **False Negatives (FN):** 12
- **Preliminary F1 Score:** 0.0%

### Detected Semantic Headings Sample (First 15):
*No semantic headings detected. Engine generated 9 zero-loss fallback partitions (`paragraph_density_partition`).*

### Ground Truth Comparison Table:

| Status | Expected Ground Truth | Predicted Heading | Page | Class Match | Parent Match | Conf | Method |
|---|---|---|---|---|---|---|---|
| **FN** | ADVENTURE I. A SCANDAL IN BOHEMIA | — | 0 | No | No | 0.00 | `missed` |
| **FN** | ADVENTURE II. THE RED-HEADED LEAGUE | — | 0 | No | No | 0.00 | `missed` |
| **FN** | ADVENTURE III. A CASE OF IDENTITY | — | 0 | No | No | 0.00 | `missed` |
| **FN** | ADVENTURE IV. THE BOSCOMBE VALLEY MYSTERY | — | 0 | No | No | 0.00 | `missed` |
| **FN** | ADVENTURE V. THE FIVE ORANGE PIPS | — | 0 | No | No | 0.00 | `missed` |
| **FN** | ADVENTURE VI. THE MAN WITH THE TWISTED LIP | — | 0 | No | No | 0.00 | `missed` |
| **FN** | ADVENTURE VII. THE ADVENTURE OF THE BLUE CARBUNCLE | — | 0 | No | No | 0.00 | `missed` |
| **FN** | ADVENTURE VIII. THE ADVENTURE OF THE SPECKLED BAND | — | 0 | No | No | 0.00 | `missed` |
| **FN** | ADVENTURE IX. THE ADVENTURE OF THE ENGINEER'S THUMB | — | 0 | No | No | 0.00 | `missed` |
| **FN** | ADVENTURE X. THE ADVENTURE OF THE NOBLE BACHELOR | — | 0 | No | No | 0.00 | `missed` |
| **FN** | ADVENTURE XI. THE ADVENTURE OF THE BERYL CORONET | — | 0 | No | No | 0.00 | `missed` |
| **FN** | ADVENTURE XII. THE ADVENTURE OF THE COPPER BEECHES | — | 0 | No | No | 0.00 | `missed` |

---

## Document `006_alices_adventures`: *Alice's Adventures in Wonderland*

- **Filename:** `alicesadventures00carr_20.pdf`
- **Author:** Lewis Carroll
- **Pages:** 226
- **Raw Character Count:** 207,785
- **Average Chars/Page:** 919.4
- **Extraction Status:** `native_text`
- **Parser Runtime:** 1.93s (117.4 pages/sec)
- **Semantic Nodes Detected:** 0
- **Fallback Partitions:** 9
- **Proposed Ground Truth Nodes:** 12
- **Human Verification Required:** Yes (`human_verified = false`)
- **Document Evaluation Status:** **Critical Failure**

### Structural Output Breakdown
- **True Positives (TP):** 0
- **False Positives (FP):** 0
- **False Negatives (FN):** 12
- **Preliminary F1 Score:** 0.0%

### Detected Semantic Headings Sample (First 15):
*No semantic headings detected. Engine generated 9 zero-loss fallback partitions (`paragraph_density_partition`).*

### Ground Truth Comparison Table:

| Status | Expected Ground Truth | Predicted Heading | Page | Class Match | Parent Match | Conf | Method |
|---|---|---|---|---|---|---|---|
| **FN** | CHAPTER I. DOWN THE RABBIT-HOLE | — | 0 | No | No | 0.00 | `missed` |
| **FN** | CHAPTER II. THE POOL OF TEARS | — | 0 | No | No | 0.00 | `missed` |
| **FN** | CHAPTER III. A CAUCUS-RACE AND A LONG TALE | — | 0 | No | No | 0.00 | `missed` |
| **FN** | CHAPTER IV. THE RABBIT SENDS IN A LITTLE BILL | — | 0 | No | No | 0.00 | `missed` |
| **FN** | CHAPTER V. ADVICE FROM A CATERPILLAR | — | 0 | No | No | 0.00 | `missed` |
| **FN** | CHAPTER VI. PIG AND PEPPER | — | 0 | No | No | 0.00 | `missed` |
| **FN** | CHAPTER VII. A MAD TEA-PARTY | — | 0 | No | No | 0.00 | `missed` |
| **FN** | CHAPTER VIII. THE QUEEN'S CROQUET-GROUND | — | 0 | No | No | 0.00 | `missed` |
| **FN** | CHAPTER IX. THE MOCK TURTLE'S STORY | — | 0 | No | No | 0.00 | `missed` |
| **FN** | CHAPTER X. THE LOBSTER QUADRILLE | — | 0 | No | No | 0.00 | `missed` |
| **FN** | CHAPTER XI. WHO STOLE THE TARTS? | — | 0 | No | No | 0.00 | `missed` |
| **FN** | CHAPTER XII. ALICE'S EVIDENCE | — | 0 | No | No | 0.00 | `missed` |

---

## Document `007_count_of_monte_cristo`: *The Count of Monte Cristo (Vol. I)*

- **Filename:** `countofmontecris01duma.pdf`
- **Author:** Alexandre Dumas
- **Pages:** 360
- **Raw Character Count:** 727,934
- **Average Chars/Page:** 2022.0
- **Extraction Status:** `native_text`
- **Parser Runtime:** 40.23s (8.9 pages/sec)
- **Semantic Nodes Detected:** 26
- **Fallback Partitions:** 0
- **Proposed Ground Truth Nodes:** 38
- **Human Verification Required:** Yes (`human_verified = false`)
- **Document Evaluation Status:** **Minor Errors**

### Structural Output Breakdown
- **True Positives (TP):** 25
- **False Positives (FP):** 0
- **False Negatives (FN):** 13
- **Preliminary F1 Score:** 79.4%

### Detected Semantic Headings Sample (First 15):
1. `[front_matter]` **Front Matter** (p. 2–32, conf=0.90, method=`leading_document_span`)
2. `[chapter]` **Chapter II: Path Eb And Son** (p. 33–42, conf=0.92, method=`lexical_chapter`)
3. `[chapter]` **Chapter III: The Catalans** (p. 43–53, conf=0.97, method=`lexical_chapter`)
4. `[chapter]` **Chapter IV: Conspiracy** (p. 54–62, conf=0.97, method=`lexical_chapter`)
5. `[chapter]` **Chapter V: The Maiuuage Feast** (p. 63–82, conf=0.97, method=`lexical_chapter`)
6. `[chapter]` **Chapter VI** (p. 83–94, conf=0.95, method=`lexical_chapter`)
7. `[chapter]` **Chapter VII: The Examination** (p. 95–121, conf=0.97, method=`lexical_chapter`)
8. `[chapter]` **Chapter IX: The Evening Of The Betrothal** (p. 122–128, conf=0.92, method=`lexical_chapter`)
9. `[chapter]` **Chapter X: The Small Cabinet Of The Tuileries** (p. 129–136, conf=0.97, method=`lexical_chapter`)
10. `[chapter]` **Chapter XI** (p. 139–149, conf=0.95, method=`lexical_chapter`)
11. `[chapter]` **Chapter XII: F Aihee And Son** (p. 150–157, conf=0.97, method=`lexical_chapter`)
12. `[chapter]` **Chapter XIII: The Ii Undeed Days** (p. 158–168, conf=0.97, method=`lexical_chapter`)
13. `[chapter]` **Chapter XIV: The Two Prisoners** (p. 169–181, conf=0.97, method=`lexical_chapter`)
14. `[chapter]` **Chapter XV** (p. 182–199, conf=0.95, method=`lexical_chapter`)
15. `[chapter]` **Chapter XVI: A Learned Italian** (p. 200–211, conf=0.97, method=`lexical_chapter`)

### Ground Truth Comparison Table:

| Status | Expected Ground Truth | Predicted Heading | Page | Class Match | Parent Match | Conf | Method |
|---|---|---|---|---|---|---|---|
| **TP** | Chapter 2 | Chapter II: Path Eb And Son | 33 | Yes | Yes | 0.92 | `lexical_chapter` |
| **TP** | Chapter 3 | Chapter III: The Catalans | 43 | Yes | Yes | 0.97 | `lexical_chapter` |
| **TP** | Chapter 4 | Chapter IV: Conspiracy | 54 | Yes | Yes | 0.97 | `lexical_chapter` |
| **TP** | Chapter 5 | Chapter V: The Maiuuage Feast | 63 | Yes | Yes | 0.97 | `lexical_chapter` |
| **TP** | Chapter 6 | Chapter VI | 83 | Yes | Yes | 0.95 | `lexical_chapter` |
| **TP** | Chapter 7 | Chapter VII: The Examination | 95 | Yes | Yes | 0.97 | `lexical_chapter` |
| **TP** | Chapter 9 | Chapter IX: The Evening Of The Betrothal | 122 | Yes | Yes | 0.92 | `lexical_chapter` |
| **TP** | Chapter 1 | Chapter X: The Small Cabinet Of The Tuileries | 129 | Yes | Yes | 0.97 | `lexical_chapter` |
| **TP** | Chapter 11 | Chapter XI | 139 | Yes | Yes | 0.95 | `lexical_chapter` |
| **TP** | Chapter 12 | Chapter XII: F Aihee And Son | 150 | Yes | Yes | 0.97 | `lexical_chapter` |
| **TP** | Chapter 13 | Chapter XIII: The Ii Undeed Days | 158 | Yes | Yes | 0.97 | `lexical_chapter` |
| **TP** | Chapter 14 | Chapter XIV: The Two Prisoners | 169 | Yes | Yes | 0.97 | `lexical_chapter` |
| **TP** | Chapter 15 | Chapter XV | 182 | Yes | Yes | 0.95 | `lexical_chapter` |
| **TP** | Chapter 16 | Chapter XVI: A Learned Italian | 200 | Yes | Yes | 0.97 | `lexical_chapter` |
| **TP** | Chapter 17 | Chapter XVII: The Abbe'S Chamber | 212 | Yes | Yes | 0.97 | `lexical_chapter` |
| **TP** | Chapter 18 | Chapter XVIII: The The As Tee | 235 | Yes | Yes | 0.97 | `lexical_chapter` |
| **TP** | Chapter 19 | Chapter XIX: The Thikd Attack | 250 | Yes | Yes | 0.97 | `lexical_chapter` |
| **TP** | Chapter 20 | Chapter XX | 261 | Yes | Yes | 0.95 | `lexical_chapter` |
| **TP** | Chapter 21 | Chapter XXI | 269 | Yes | Yes | 0.90 | `lexical_chapter` |
| **TP** | Chapter 22 | Chapter XXII: The Smugglers | 281 | Yes | Yes | 0.92 | `lexical_chapter` |
| **TP** | Chapter 23 | Chapter XXIII: The Isle Of M0Nte-Crist0 | 291 | Yes | Yes | 0.92 | `lexical_chapter` |
| **TP** | Chapter 24 | Chapter XXIV: The Secret Cave | 299 | Yes | Yes | 0.92 | `lexical_chapter` |
| **TP** | Chapter 25 | Chapter XXV: The Unknown | 310 | Yes | Yes | 0.92 | `lexical_chapter` |
| **TP** | Chapter 26 | Chapter XXVI: The A.Ubebge Of Pont Dt' Gabd | 321 | Yes | Yes | 0.92 | `lexical_chapter` |
| **TP** | Chapter 27 | Chapter XXVII: Tiif. Recital | 337 | Yes | Yes | 0.92 | `lexical_chapter` |
| **FN** | Chapter 8 | — | 0 | No | No | 0.00 | `missed` |
| **FN** | Chapter 10 | — | 0 | No | No | 0.00 | `missed` |
| **FN** | Chapter 28 | — | 0 | No | No | 0.00 | `missed` |
| **FN** | Chapter 29 | — | 0 | No | No | 0.00 | `missed` |
| **FN** | Chapter 30 | — | 0 | No | No | 0.00 | `missed` |
| **FN** | Chapter 31 | — | 0 | No | No | 0.00 | `missed` |
| **FN** | Chapter 32 | — | 0 | No | No | 0.00 | `missed` |
| **FN** | Chapter 33 | — | 0 | No | No | 0.00 | `missed` |
| **FN** | Chapter 34 | — | 0 | No | No | 0.00 | `missed` |
| **FN** | Chapter 35 | — | 0 | No | No | 0.00 | `missed` |
| **FN** | Chapter 36 | — | 0 | No | No | 0.00 | `missed` |
| **FN** | Chapter 37 | — | 0 | No | No | 0.00 | `missed` |
| **FN** | Chapter 38 | — | 0 | No | No | 0.00 | `missed` |

---

## Document `008_the_iliad`: *The Iliad*

- **Filename:** `homer_the_iliad_penguin_classics_deluxe_edition-robert-fagles.pdf`
- **Author:** Homer (tr. Robert Fagles)
- **Pages:** 699
- **Raw Character Count:** 1,564,835
- **Average Chars/Page:** 2238.7
- **Extraction Status:** `native_text`
- **Parser Runtime:** 38.54s (18.1 pages/sec)
- **Semantic Nodes Detected:** 73
- **Fallback Partitions:** 0
- **Proposed Ground Truth Nodes:** 28
- **Human Verification Required:** Yes (`human_verified = false`)
- **Document Evaluation Status:** **Critical Failure**

### Structural Output Breakdown
- **True Positives (TP):** 14
- **False Positives (FP):** 58
- **False Negatives (FN):** 14
- **Preliminary F1 Score:** 28.0%

### Detected Semantic Headings Sample (First 15):
1. `[front_matter]` **Front Matter** (p. 1–1, conf=0.90, method=`leading_document_span`)
2. `[chapter]` **The** (p. 1–5, conf=0.88, method=`typography_prominence`)
3. `[chapter]` **The** (p. 5–9, conf=0.88, method=`typography_prominence`)
4. `[preface]` **Preface** (p. 9–15, conf=1.00, method=`lexical_special_matter`)
5. `[introduction]` **Introduction** (p. 15–15, conf=0.95, method=`lexical_special_matter`)
6. `[introduction]` **Introduction** (p. 15–15, conf=0.95, method=`lexical_special_matter`)
7. `[chapter]` **Chapter ix** (p. 15–15, conf=0.95, method=`lexical_chapter`)
8. `[book]` **Book 1 - The Rage of Achilles** (p. 15–15, conf=0.85, method=`lexical_book`)
9. `[book]` **Book 2 - The Great Gathering of Armies** (p. 15–15, conf=0.90, method=`lexical_book`)
10. `[book]` **Book 3 - Helen Reviews the Champions** (p. 15–15, conf=0.90, method=`lexical_book`)
11. `[book]` **Book 4 - The Truce Erupts in War** (p. 15–15, conf=0.90, method=`lexical_book`)
12. `[book]` **Book 5 - Diomedes Fights the Gods** (p. 15–15, conf=0.90, method=`lexical_book`)
13. `[book]` **Book 6 - Hector Returns to Troy** (p. 15–15, conf=0.90, method=`lexical_book`)
14. `[book]` **Book 7 - Ajax Duels with Hector** (p. 15–15, conf=0.90, method=`lexical_book`)
15. `[book]` **Book 8 - The Tide of Battle Turns** (p. 15–15, conf=0.90, method=`lexical_book`)

### Ground Truth Comparison Table:

| Status | Expected Ground Truth | Predicted Heading | Page | Class Match | Parent Match | Conf | Method |
|---|---|---|---|---|---|---|---|
| **TP** | The Genealogy of the Gods and Pronouncing Glossary | The | 1 | No | Yes | 0.88 | `typography_prominence` |
| **FP** | — | The | 5 | No | No | 0.88 | `typography_prominence` |
| **TP** | Preface | Preface | 9 | Yes | Yes | 1.00 | `lexical_special_matter` |
| **TP** | Introduction | Introduction | 15 | Yes | Yes | 0.95 | `lexical_special_matter` |
| **FP** | — | Introduction | 15 | No | No | 0.95 | `lexical_special_matter` |
| **FP** | — | Chapter ix | 15 | No | No | 0.95 | `lexical_chapter` |
| **TP** | BOOK 1 | Book 1 - The Rage of Achilles | 15 | Yes | Yes | 0.85 | `lexical_book` |
| **TP** | BOOK 2 | Book 2 - The Great Gathering of Armies | 15 | Yes | Yes | 0.90 | `lexical_book` |
| **TP** | BOOK 3 | Book 3 - Helen Reviews the Champions | 15 | Yes | Yes | 0.90 | `lexical_book` |
| **TP** | BOOK 4 | Book 4 - The Truce Erupts in War | 15 | Yes | Yes | 0.90 | `lexical_book` |
| **TP** | BOOK 5 | Book 5 - Diomedes Fights the Gods | 15 | Yes | Yes | 0.90 | `lexical_book` |
| **TP** | BOOK 6 | Book 6 - Hector Returns to Troy | 15 | Yes | Yes | 0.90 | `lexical_book` |
| **TP** | BOOK 7 | Book 7 - Ajax Duels with Hector | 15 | Yes | Yes | 0.90 | `lexical_book` |
| **TP** | BOOK 8 | Book 8 - The Tide of Battle Turns | 15 | Yes | Yes | 0.90 | `lexical_book` |
| **TP** | BOOK 9 | Book 9 - The Embassy to Achilles | 15 | Yes | Yes | 0.90 | `lexical_book` |
| **TP** | BOOK 10 | Book 10 - Marauding Through the Night | 15 | Yes | Yes | 0.90 | `lexical_book` |
| **FP** | — | Chapter xv | 15 | No | No | 0.85 | `lexical_chapter` |
| **TP** | Notes | Notes | 16 | Yes | Yes | 0.95 | `lexical_special_matter` |
| **FP** | — | Introduction | 17 | No | No | 1.00 | `lexical_special_matter` |
| **FP** | — | Introduction | 19 | No | No | 1.00 | `lexical_special_matter` |
| **FP** | — | (IONiAN | 84 | No | No | 0.78 | `typography_prominence` |
| **FP** | — | EAN | 85 | No | No | 0.88 | `typography_prominence` |
| **FP** | — | Sea) | 85 | No | No | 0.78 | `typography_prominence` |
| **FP** | — | Sea) | 86 | No | No | 0.78 | `typography_prominence` |
| **FP** | — | (fONIAN | 86 | No | No | 0.78 | `typography_prominence` |
| **FP** | — | Book ONE | 93 | No | No | 0.90 | `lexical_book` |
| **FP** | — | The Rage of Achilles | 93 | No | No | 0.78 | `typography_prominence` |
| **FP** | — | Book TWO | 115 | No | No | 0.95 | `lexical_book` |
| **FP** | — | The Great | 115 | No | No | 0.78 | `typography_prominence` |
| **FP** | — | Gathering of Armies | 115 | No | No | 0.78 | `typography_prominence` |
| **FP** | — | Book THREE | 144 | No | No | 0.98 | `lexical_book` |
| **FP** | — | Helen Reviews | 144 | No | No | 0.78 | `typography_prominence` |
| **FP** | — | Book FOUR | 161 | No | No | 0.95 | `lexical_book` |
| **FP** | — | The Truce | 161 | No | No | 0.78 | `typography_prominence` |
| **FP** | — | Book FIVE | 180 | No | No | 0.98 | `lexical_book` |
| **FP** | — | Diornedes | 180 | No | No | 0.78 | `typography_prominence` |
| **FP** | — | Book SIX | 211 | No | No | 0.98 | `lexical_book` |
| **FP** | — | Hector | 211 | No | No | 0.78 | `typography_prominence` |
| **FP** | — | Book SEVEN | 230 | No | No | 0.95 | `lexical_book` |
| **FP** | — | Ajax Duels | 230 | No | No | 0.78 | `typography_prominence` |
| **FP** | — | Book EIGHT | 247 | No | No | 0.98 | `lexical_book` |
| **FP** | — | The Tide | 247 | No | No | 0.78 | `typography_prominence` |
| **FP** | — | Book NINE | 267 | No | No | 0.95 | `lexical_book` |
| **FP** | — | The Embassy | 267 | No | No | 0.78 | `typography_prominence` |
| **FP** | — | Book TEN | 292 | No | No | 0.95 | `lexical_book` |
| **FP** | — | Marauding | 292 | No | No | 0.78 | `typography_prominence` |
| **FP** | — | Agamemnon's | 312 | No | No | 0.78 | `typography_prominence` |
| **FP** | — | The Trojans | 341 | No | No | 0.78 | `typography_prominence` |
| **FP** | — | Storm the Rampart | 341 | No | No | 0.78 | `typography_prominence` |
| **FP** | — | Battling | 357 | No | No | 0.78 | `typography_prominence` |
| **FP** | — | Hera | 385 | No | No | 0.88 | `typography_prominence` |
| **FP** | — | Outflanks Zeus | 385 | No | No | 0.78 | `typography_prominence` |
| **FP** | — | The Achaean | 403 | No | No | 0.78 | `typography_prominence` |
| **FP** | — | Patroclus | 428 | No | No | 0.78 | `typography_prominence` |
| **FP** | — | Menelaus' | 458 | No | No | 0.88 | `typography_prominence` |
| **FP** | — | Finest Hour | 458 | No | No | 0.88 | `typography_prominence` |
| **FP** | — | The Shield of | 483 | No | No | 0.78 | `typography_prominence` |
| **FP** | — | The Champion | 504 | No | No | 0.78 | `typography_prominence` |
| **FP** | — | Olympian Gods | 519 | No | No | 0.78 | `typography_prominence` |
| **FP** | — | Achilles | 536 | No | No | 0.78 | `typography_prominence` |
| **FP** | — | The Death of Hector | 557 | No | No | 0.78 | `typography_prominence` |
| **FP** | — | Funeral Games | 575 | No | No | 0.78 | `typography_prominence` |
| **FP** | — | Achilles and Priam | 604 | No | No | 0.78 | `typography_prominence` |
| **FP** | — | 1.1. Goddess: the Muse who personifies the inspiration for epic poetry. | 637 | No | No | 0.75 | `numbered_section` |
| **FP** | — | 9.171. Accept the blood-price: see note 18.581-92. | 644 | No | No | 0.83 | `numbered_section` |
| **FP** | — | 19.106. Ruin. eldest daughter of Zeus: see note 2.130. | 647 | No | No | 0.83 | `numbered_section` |
| **FP** | — | 21.506. Those troubles we suffered here alongside Tray: see note 7.523-25. | 648 | No | No | 0.75 | `numbered_section` |
| **FP** | — | 24.97. Samos: the island facing Thrace. later called Samothrace. | 649 | No | No | 0.83 | `numbered_section` |
| **FP** | — | 1. Texts and Commentaries | 651 | No | No | 0.85 | `numbered_section` |
| **FP** | — | Pronouncing | 655 | No | No | 0.88 | `typography_prominence` |
| **FP** | — | Glossary | 655 | No | No | 1.00 | `lexical_special_matter` |
| **FP** | — | 15.107. See note 2.86. | 696 | No | No | 0.80 | `numbered_section` |
| **FN** | BOOK 11 | — | 0 | No | No | 0.00 | `missed` |
| **FN** | BOOK 12 | — | 0 | No | No | 0.00 | `missed` |
| **FN** | BOOK 13 | — | 0 | No | No | 0.00 | `missed` |
| **FN** | BOOK 14 | — | 0 | No | No | 0.00 | `missed` |
| **FN** | BOOK 15 | — | 0 | No | No | 0.00 | `missed` |
| **FN** | BOOK 16 | — | 0 | No | No | 0.00 | `missed` |
| **FN** | BOOK 17 | — | 0 | No | No | 0.00 | `missed` |
| **FN** | BOOK 18 | — | 0 | No | No | 0.00 | `missed` |
| **FN** | BOOK 19 | — | 0 | No | No | 0.00 | `missed` |
| **FN** | BOOK 20 | — | 0 | No | No | 0.00 | `missed` |
| **FN** | BOOK 21 | — | 0 | No | No | 0.00 | `missed` |
| **FN** | BOOK 22 | — | 0 | No | No | 0.00 | `missed` |
| **FN** | BOOK 23 | — | 0 | No | No | 0.00 | `missed` |
| **FN** | BOOK 24 | — | 0 | No | No | 0.00 | `missed` |

---

## Document `009_moby_dick`: *Moby-Dick; or, The Whale*

- **Filename:** `mobydickorwhale01melvuoft.pdf`
- **Author:** Herman Melville
- **Pages:** 394
- **Raw Character Count:** 849,642
- **Average Chars/Page:** 2156.5
- **Extraction Status:** `native_text`
- **Parser Runtime:** 45.56s (8.6 pages/sec)
- **Semantic Nodes Detected:** 106
- **Fallback Partitions:** 0
- **Proposed Ground Truth Nodes:** 138
- **Human Verification Required:** Yes (`human_verified = false`)
- **Document Evaluation Status:** **Major Errors**

### Structural Output Breakdown
- **True Positives (TP):** 57
- **False Positives (FP):** 48
- **False Negatives (FN):** 81
- **Preliminary F1 Score:** 46.9%

### Detected Semantic Headings Sample (First 15):
1. `[front_matter]` **Front Matter** (p. 2–7, conf=0.90, method=`leading_document_span`)
2. `[chapter]` **Chapter VII** (p. 7–13, conf=1.00, method=`lexical_chapter`)
3. `[chapter]` **II. The Carpet-Bag ...... 8** (p. 13–13, conf=0.90, method=`numbered_section`)
4. `[chapter]` **V. Breakfast ...... 36** (p. 13–13, conf=0.90, method=`numbered_section`)
5. `[chapter]` **VI. The Street . . . . . 39** (p. 13–13, conf=0.95, method=`numbered_section`)
6. `[chapter]` **VII. The Chapel . . . . . . 42** (p. 13–13, conf=0.95, method=`numbered_section`)
7. `[chapter]` **VIII. The Pulpit ....... 46** (p. 13–13, conf=0.95, method=`numbered_section`)
8. `[chapter]` **IX. The Sermon ...... 49** (p. 13–13, conf=0.95, method=`numbered_section`)
9. `[chapter]` **X. A Bosom Friend ...... 60** (p. 13–13, conf=0.95, method=`numbered_section`)
10. `[chapter]` **XI. Nightgown 65** (p. 13–13, conf=1.00, method=`numbered_section`)
11. `[chapter]` **XII. Biographical ...... 68** (p. 13–13, conf=0.95, method=`numbered_section`)
12. `[chapter]` **XIII. Wheelbarrow . . . . . . 71** (p. 13–13, conf=0.95, method=`numbered_section`)
13. `[chapter]` **XIV. Nantucket ....... 77** (p. 13–13, conf=0.95, method=`numbered_section`)
14. `[chapter]` **XV. Chowder ....... 80** (p. 13–13, conf=0.95, method=`numbered_section`)
15. `[chapter]` **XVII. The Ramadan ...... 102** (p. 13–13, conf=0.90, method=`numbered_section`)

### Ground Truth Comparison Table:

| Status | Expected Ground Truth | Predicted Heading | Page | Class Match | Parent Match | Conf | Method |
|---|---|---|---|---|---|---|---|
| **TP** | CHAPTER 7 | Chapter VII | 7 | Yes | Yes | 1.00 | `lexical_chapter` |
| **FP** | — | II. The Carpet-Bag ...... 8 | 13 | No | No | 0.90 | `numbered_section` |
| **FP** | — | V. Breakfast ...... 36 | 13 | No | No | 0.90 | `numbered_section` |
| **FP** | — | VI. The Street . . . . . 39 | 13 | No | No | 0.95 | `numbered_section` |
| **FP** | — | VII. The Chapel . . . . . . 42 | 13 | No | No | 0.95 | `numbered_section` |
| **FP** | — | VIII. The Pulpit ....... 46 | 13 | No | No | 0.95 | `numbered_section` |
| **FP** | — | IX. The Sermon ...... 49 | 13 | No | No | 0.95 | `numbered_section` |
| **FP** | — | X. A Bosom Friend ...... 60 | 13 | No | No | 0.95 | `numbered_section` |
| **FP** | — | XI. Nightgown 65 | 13 | No | No | 1.00 | `numbered_section` |
| **FP** | — | XII. Biographical ...... 68 | 13 | No | No | 0.95 | `numbered_section` |
| **FP** | — | XIII. Wheelbarrow . . . . . . 71 | 13 | No | No | 0.95 | `numbered_section` |
| **FP** | — | XIV. Nantucket ....... 77 | 13 | No | No | 0.95 | `numbered_section` |
| **FP** | — | XV. Chowder ....... 80 | 13 | No | No | 0.95 | `numbered_section` |
| **FP** | — | XVII. The Ramadan ...... 102 | 13 | No | No | 0.90 | `numbered_section` |
| **FP** | — | XIX. The Prophet . . . . . .115 | 13 | No | No | 0.90 | `numbered_section` |
| **FP** | — | XX. All Astir ....... 119 | 13 | No | No | 0.95 | `numbered_section` |
| **FP** | — | XXI. Going Aboard ...... 122 | 13 | No | No | 0.90 | `numbered_section` |
| **FP** | — | XXII. Merry Christmas . . . . .126 | 13 | No | No | 0.90 | `numbered_section` |
| **FP** | — | XXIII. The Lee Shore . . . . . .132 | 13 | No | No | 0.90 | `numbered_section` |
| **FP** | — | XXIV. The Advocate . . . . . .134 | 13 | No | No | 0.90 | `numbered_section` |
| **FP** | — | XXV. Postscript . . . . . 140 | 13 | No | No | 0.90 | `numbered_section` |
| **FP** | — | XXVI. Knights And Squires . . . .141 | 13 | No | No | 0.90 | `numbered_section` |
| **FP** | — | XXVII. Knights And Squires .... 145 | 13 | No | No | 0.90 | `numbered_section` |
| **FP** | — | XXIX. Enter Ahab ; To Him, Stubb . . .156 | 14 | No | No | 0.80 | `numbered_section` |
| **FP** | — | XXX. The Pipe ...... 160 | 14 | No | No | 0.80 | `numbered_section` |
| **FP** | — | XXXII. Cetology . . . . . .164 | 14 | No | No | 0.80 | `numbered_section` |
| **FP** | — | XXXV. The Mast-Head . . . . .191 | 14 | No | No | 0.80 | `numbered_section` |
| **FP** | — | XXXVI. The Quarter-Deck ..... 199 | 14 | No | No | 0.80 | `numbered_section` |
| **FP** | — | XXXVII. Sunset . . . . . . . 209 | 14 | No | No | 0.80 | `numbered_section` |
| **FP** | — | XXXIX. First Night-Watch . . . . .213 | 14 | No | No | 0.80 | `numbered_section` |
| **FP** | — | XL. Midnight, Forecastle . . . .214 | 14 | No | No | 0.80 | `numbered_section` |
| **FP** | — | XLI. Moby-Dick ...... 222 | 14 | No | No | 0.80 | `numbered_section` |
| **FP** | — | XLII. The Whiteness Of The Whale . . 234 | 14 | No | No | 0.80 | `numbered_section` |
| **FP** | — | XLV. The Affidavit ...... 254 | 14 | No | No | 0.80 | `numbered_section` |
| **FP** | — | XLIX. The Hyena ...... 286 | 14 | No | No | 0.80 | `numbered_section` |
| **FP** | — | L. Ahab'S Boat And Crew. Fed Allah . . 289 | 14 | No | No | 0.80 | `numbered_section` |
| **FP** | — | LI. The Spirit-Spout 293 | 14 | No | No | 0.80 | `numbered_section` |
| **FP** | — | MI. The Albatross ...... 298 | 14 | No | No | 0.80 | `numbered_section` |
| **FP** | — | LIV. The Town-Ho'S Story 306 | 14 | No | No | 0.80 | `numbered_section` |
| **FP** | — | LV. Of The Monstrous Pictures Of Whales . 331 | 14 | No | No | 0.80 | `numbered_section` |
| **FP** | — | LVI. Of The Less Erroneous Pictures Of Whales 337 | 14 | No | No | 0.80 | `numbered_section` |
| **FP** | — | LVII. Of Whales In Paint, In Teeth, Etc. . 342 | 14 | No | No | 0.80 | `numbered_section` |
| **FP** | — | LIX. Squid 350 | 14 | No | No | 0.85 | `numbered_section` |
| **FP** | — | LX. The Line . 353 | 14 | No | No | 0.85 | `numbered_section` |
| **TP** | CHAPTER 1 | Chapter xii | 18 | Yes | Yes | 0.95 | `lexical_chapter` |
| **FP** | — | Chapter I: Loomings | 31 | No | No | 0.92 | `lexical_chapter` |
| **TP** | CHAPTER 2 | Chapter II: The Carpet-Bag | 38 | Yes | Yes | 0.92 | `lexical_chapter` |
| **TP** | CHAPTER 3 | Chapter III: The Spottter-Inn | 43 | Yes | Yes | 0.97 | `lexical_chapter` |
| **TP** | CHAPTER 4 | Chapter IV: The Counterpane | 61 | Yes | Yes | 0.97 | `lexical_chapter` |
| **TP** | CHAPTER 5 | Chapter V: Breakfast | 66 | Yes | Yes | 0.97 | `lexical_chapter` |
| **TP** | CHAPTER 6 | Chapter VI: The Street | 69 | Yes | Yes | 0.97 | `lexical_chapter` |
| **FP** | — | Chapter VII: The Chapel | 72 | No | No | 0.97 | `lexical_chapter` |
| **TP** | CHAPTER 8 | Chapter VIII: The Pulpit | 76 | Yes | Yes | 0.97 | `lexical_chapter` |
| **TP** | CHAPTER 9 | Chapter IX: The Sermon | 79 | Yes | Yes | 0.97 | `lexical_chapter` |
| **TP** | CHAPTER 10 | Chapter X: A Bosom Friend | 90 | Yes | Yes | 0.97 | `lexical_chapter` |
| **TP** | CHAPTER 11 | Chapter XI: Nightgown | 95 | Yes | Yes | 0.97 | `lexical_chapter` |
| **TP** | CHAPTER 12 | Chapter XII: Biographical | 98 | Yes | Yes | 0.97 | `lexical_chapter` |
| **TP** | CHAPTER 13 | Chapter XIII: Wheelbarrow | 101 | Yes | Yes | 0.97 | `lexical_chapter` |
| **TP** | CHAPTER 14 | Chapter XIV: Nantucket | 107 | Yes | Yes | 0.97 | `lexical_chapter` |
| **TP** | CHAPTER 15 | Chapter XV: Chowder | 110 | Yes | Yes | 0.97 | `lexical_chapter` |
| **TP** | CHAPTER 16 | Chapter XVI: The Ship | 114 | Yes | Yes | 0.97 | `lexical_chapter` |
| **TP** | CHAPTER 17 | Chapter XVII: The Ramadan | 132 | Yes | Yes | 0.97 | `lexical_chapter` |
| **TP** | CHAPTER 18 | Chapter XVIII: His Mark | 140 | Yes | Yes | 0.97 | `lexical_chapter` |
| **TP** | CHAPTER 19 | Chapter XIX: The Peophet | 145 | Yes | Yes | 0.97 | `lexical_chapter` |
| **TP** | CHAPTER 20 | Chapter XX: All Astir | 149 | Yes | Yes | 0.97 | `lexical_chapter` |
| **TP** | CHAPTER 21 | Chapter XXI: Going Aboard | 152 | Yes | Yes | 0.92 | `lexical_chapter` |
| **TP** | CHAPTER 22 | Chapter XXII: Merry Christmas | 156 | Yes | Yes | 0.92 | `lexical_chapter` |
| **TP** | CHAPTER 23 | Chapter XXIII: The Lee Shore | 162 | Yes | Yes | 0.92 | `lexical_chapter` |
| **TP** | CHAPTER 24 | Chapter XXIV: The Advocate | 164 | Yes | Yes | 0.92 | `lexical_chapter` |
| **TP** | CHAPTER 25 | Chapter XXV: Postscript | 170 | Yes | Yes | 0.92 | `lexical_chapter` |
| **TP** | CHAPTER 26 | Chapter XXVI: Knights And Squires | 171 | Yes | Yes | 0.92 | `lexical_chapter` |
| **TP** | CHAPTER 27 | Chapter XXVII: Knights And Squires | 175 | Yes | Yes | 0.92 | `lexical_chapter` |
| **TP** | CHAPTER 28 | Chapter XXVIII: Ahab | 181 | Yes | Yes | 0.92 | `lexical_chapter` |
| **TP** | CHAPTER 29 | Chapter XXIX: To Him, Stubb | 186 | Yes | Yes | 0.92 | `lexical_chapter` |
| **TP** | CHAPTER 30 | Chapter XXX: The Pipe | 190 | Yes | Yes | 0.92 | `lexical_chapter` |
| **TP** | CHAPTER 31 | Chapter XXXI: Queen Mab | 191 | Yes | Yes | 0.92 | `lexical_chapter` |
| **TP** | CHAPTER 32 | Chapter XXXII: Cetology | 194 | Yes | Yes | 0.92 | `lexical_chapter` |
| **FP** | — | Book I - (Folio), CHAPTER I. (Sperm Whale).— This | 198 | No | No | 0.85 | `lexical_book` |
| **FP** | — | Book II - (Octavo), CHAPTER II. (Black Fish).— I give | 204 | No | No | 0.90 | `lexical_book` |
| **FP** | — | Book III - (Duodecimo), CHAPTER II. (Algerine Por- | 208 | No | No | 0.90 | `lexical_book` |
| **TP** | CHAPTER 33 | Chapter XXXIII: The Specksynder | 210 | Yes | Yes | 0.92 | `lexical_chapter` |
| **TP** | CHAPTER 34 | Chapter XXXIV: The Cabin-Table | 214 | Yes | Yes | 0.92 | `lexical_chapter` |
| **TP** | CHAPTER 35 | Chapter XXXV: The Mast-Head | 221 | Yes | Yes | 0.92 | `lexical_chapter` |
| **TP** | CHAPTER 36 | Chapter XXXVI: The Quartek-Deck | 229 | Yes | Yes | 0.92 | `lexical_chapter` |
| **TP** | CHAPTER 37 | Chapter XXXVII: Sunset | 239 | Yes | Yes | 0.92 | `lexical_chapter` |
| **TP** | CHAPTER 38 | Chapter XXXVIII: Dusk | 241 | Yes | Yes | 0.92 | `lexical_chapter` |
| **TP** | CHAPTER 39 | Chapter XXXIX: First Night-Watch | 243 | Yes | Yes | 0.92 | `lexical_chapter` |
| **TP** | CHAPTER 40 | Chapter XL: Midnight, Forecastle | 244 | Yes | Yes | 0.92 | `lexical_chapter` |
| **TP** | CHAPTER 41 | Chapter XLI: Moby-Dick | 252 | Yes | Yes | 0.92 | `lexical_chapter` |
| **TP** | CHAPTER 42 | Chapter XLII: The Whiteness Of The Whale | 264 | Yes | Yes | 0.92 | `lexical_chapter` |
| **TP** | CHAPTER 43 | Chapter XLIII: Hark ! | 275 | Yes | Yes | 0.92 | `lexical_chapter` |
| **TP** | CHAPTER 44 | Chapter XLIV: The Chart | 277 | Yes | Yes | 0.92 | `lexical_chapter` |
| **TP** | CHAPTER 45 | Chapter XLV: The Affidavit | 284 | Yes | Yes | 0.92 | `lexical_chapter` |
| **TP** | CHAPTER 46 | Chapter XLVI: Surmises | 295 | Yes | Yes | 0.92 | `lexical_chapter` |
| **TP** | CHAPTER 47 | Chapter XLVII: The Mat-Maker | 299 | Yes | Yes | 0.92 | `lexical_chapter` |
| **TP** | CHAPTER 48 | Chapter XLVIII: The First Lowering | 303 | Yes | Yes | 0.92 | `lexical_chapter` |
| **TP** | CHAPTER 50 | Chapter L: Arab'S Boat And Crew. Fedallah | 319 | Yes | Yes | 0.92 | `lexical_chapter` |
| **TP** | CHAPTER 51 | Chapter LI: The Spirit- Spout | 323 | Yes | Yes | 0.92 | `lexical_chapter` |
| **TP** | CHAPTER 52 | Chapter LII: The Albatross | 328 | Yes | Yes | 0.92 | `lexical_chapter` |
| **TP** | CHAPTER 53 | Chapter LIII: The Gam | 331 | Yes | Yes | 0.92 | `lexical_chapter` |
| **TP** | CHAPTER 55 | Chapter LV: Of The Monstrous Pictures Of Whales | 361 | Yes | Yes | 0.92 | `lexical_chapter` |
| **TP** | CHAPTER 56 | Chapter LVI: Of The Less Erroneous Pictures Of Whales, And The | 367 | Yes | Yes | 0.92 | `lexical_chapter` |
| **TP** | CHAPTER 57 | Chapter LVII | 372 | Yes | Yes | 0.90 | `lexical_chapter` |
| **TP** | CHAPTER 59 | Chapter LIX: Squid | 380 | Yes | Yes | 0.92 | `lexical_chapter` |
| **TP** | CHAPTER 60 | Chapter LX: The Line | 383 | Yes | Yes | 0.92 | `lexical_chapter` |
| **FN** | ETYMOLOGY | — | 0 | No | No | 0.00 | `missed` |
| **FN** | EXTRACTS | — | 0 | No | No | 0.00 | `missed` |
| **FN** | CHAPTER 49 | — | 0 | No | No | 0.00 | `missed` |
| **FN** | CHAPTER 54 | — | 0 | No | No | 0.00 | `missed` |
| **FN** | CHAPTER 58 | — | 0 | No | No | 0.00 | `missed` |
| **FN** | CHAPTER 61 | — | 0 | No | No | 0.00 | `missed` |
| **FN** | CHAPTER 62 | — | 0 | No | No | 0.00 | `missed` |
| **FN** | CHAPTER 63 | — | 0 | No | No | 0.00 | `missed` |
| **FN** | CHAPTER 64 | — | 0 | No | No | 0.00 | `missed` |
| **FN** | CHAPTER 65 | — | 0 | No | No | 0.00 | `missed` |
| **FN** | CHAPTER 66 | — | 0 | No | No | 0.00 | `missed` |
| **FN** | CHAPTER 67 | — | 0 | No | No | 0.00 | `missed` |
| **FN** | CHAPTER 68 | — | 0 | No | No | 0.00 | `missed` |
| **FN** | CHAPTER 69 | — | 0 | No | No | 0.00 | `missed` |
| **FN** | CHAPTER 70 | — | 0 | No | No | 0.00 | `missed` |
| **FN** | CHAPTER 71 | — | 0 | No | No | 0.00 | `missed` |
| **FN** | CHAPTER 72 | — | 0 | No | No | 0.00 | `missed` |
| **FN** | CHAPTER 73 | — | 0 | No | No | 0.00 | `missed` |
| **FN** | CHAPTER 74 | — | 0 | No | No | 0.00 | `missed` |
| **FN** | CHAPTER 75 | — | 0 | No | No | 0.00 | `missed` |
| **FN** | CHAPTER 76 | — | 0 | No | No | 0.00 | `missed` |
| **FN** | CHAPTER 77 | — | 0 | No | No | 0.00 | `missed` |
| **FN** | CHAPTER 78 | — | 0 | No | No | 0.00 | `missed` |
| **FN** | CHAPTER 79 | — | 0 | No | No | 0.00 | `missed` |
| **FN** | CHAPTER 80 | — | 0 | No | No | 0.00 | `missed` |
| **FN** | CHAPTER 81 | — | 0 | No | No | 0.00 | `missed` |
| **FN** | CHAPTER 82 | — | 0 | No | No | 0.00 | `missed` |
| **FN** | CHAPTER 83 | — | 0 | No | No | 0.00 | `missed` |
| **FN** | CHAPTER 84 | — | 0 | No | No | 0.00 | `missed` |
| **FN** | CHAPTER 85 | — | 0 | No | No | 0.00 | `missed` |
| **FN** | CHAPTER 86 | — | 0 | No | No | 0.00 | `missed` |
| **FN** | CHAPTER 87 | — | 0 | No | No | 0.00 | `missed` |
| **FN** | CHAPTER 88 | — | 0 | No | No | 0.00 | `missed` |
| **FN** | CHAPTER 89 | — | 0 | No | No | 0.00 | `missed` |
| **FN** | CHAPTER 90 | — | 0 | No | No | 0.00 | `missed` |
| **FN** | CHAPTER 91 | — | 0 | No | No | 0.00 | `missed` |
| **FN** | CHAPTER 92 | — | 0 | No | No | 0.00 | `missed` |
| **FN** | CHAPTER 93 | — | 0 | No | No | 0.00 | `missed` |
| **FN** | CHAPTER 94 | — | 0 | No | No | 0.00 | `missed` |
| **FN** | CHAPTER 95 | — | 0 | No | No | 0.00 | `missed` |
| **FN** | CHAPTER 96 | — | 0 | No | No | 0.00 | `missed` |
| **FN** | CHAPTER 97 | — | 0 | No | No | 0.00 | `missed` |
| **FN** | CHAPTER 98 | — | 0 | No | No | 0.00 | `missed` |
| **FN** | CHAPTER 99 | — | 0 | No | No | 0.00 | `missed` |
| **FN** | CHAPTER 100 | — | 0 | No | No | 0.00 | `missed` |
| **FN** | CHAPTER 101 | — | 0 | No | No | 0.00 | `missed` |
| **FN** | CHAPTER 102 | — | 0 | No | No | 0.00 | `missed` |
| **FN** | CHAPTER 103 | — | 0 | No | No | 0.00 | `missed` |
| **FN** | CHAPTER 104 | — | 0 | No | No | 0.00 | `missed` |
| **FN** | CHAPTER 105 | — | 0 | No | No | 0.00 | `missed` |
| **FN** | CHAPTER 106 | — | 0 | No | No | 0.00 | `missed` |
| **FN** | CHAPTER 107 | — | 0 | No | No | 0.00 | `missed` |
| **FN** | CHAPTER 108 | — | 0 | No | No | 0.00 | `missed` |
| **FN** | CHAPTER 109 | — | 0 | No | No | 0.00 | `missed` |
| **FN** | CHAPTER 110 | — | 0 | No | No | 0.00 | `missed` |
| **FN** | CHAPTER 111 | — | 0 | No | No | 0.00 | `missed` |
| **FN** | CHAPTER 112 | — | 0 | No | No | 0.00 | `missed` |
| **FN** | CHAPTER 113 | — | 0 | No | No | 0.00 | `missed` |
| **FN** | CHAPTER 114 | — | 0 | No | No | 0.00 | `missed` |
| **FN** | CHAPTER 115 | — | 0 | No | No | 0.00 | `missed` |
| **FN** | CHAPTER 116 | — | 0 | No | No | 0.00 | `missed` |
| **FN** | CHAPTER 117 | — | 0 | No | No | 0.00 | `missed` |
| **FN** | CHAPTER 118 | — | 0 | No | No | 0.00 | `missed` |
| **FN** | CHAPTER 119 | — | 0 | No | No | 0.00 | `missed` |
| **FN** | CHAPTER 120 | — | 0 | No | No | 0.00 | `missed` |
| **FN** | CHAPTER 121 | — | 0 | No | No | 0.00 | `missed` |
| **FN** | CHAPTER 122 | — | 0 | No | No | 0.00 | `missed` |
| **FN** | CHAPTER 123 | — | 0 | No | No | 0.00 | `missed` |
| **FN** | CHAPTER 124 | — | 0 | No | No | 0.00 | `missed` |
| **FN** | CHAPTER 125 | — | 0 | No | No | 0.00 | `missed` |
| **FN** | CHAPTER 126 | — | 0 | No | No | 0.00 | `missed` |
| **FN** | CHAPTER 127 | — | 0 | No | No | 0.00 | `missed` |
| **FN** | CHAPTER 128 | — | 0 | No | No | 0.00 | `missed` |
| **FN** | CHAPTER 129 | — | 0 | No | No | 0.00 | `missed` |
| **FN** | CHAPTER 130 | — | 0 | No | No | 0.00 | `missed` |
| **FN** | CHAPTER 131 | — | 0 | No | No | 0.00 | `missed` |
| **FN** | CHAPTER 132 | — | 0 | No | No | 0.00 | `missed` |
| **FN** | CHAPTER 133 | — | 0 | No | No | 0.00 | `missed` |
| **FN** | CHAPTER 134 | — | 0 | No | No | 0.00 | `missed` |
| **FN** | CHAPTER 135 | — | 0 | No | No | 0.00 | `missed` |
| **FN** | EPILOGUE | — | 0 | No | No | 0.00 | `missed` |

---

## Document `010_picture_of_dorian_gray`: *The Picture of Dorian Gray*

- **Filename:** `pictureofdoriang0000osca_s9a9.pdf`
- **Author:** Oscar Wilde
- **Pages:** 248
- **Raw Character Count:** 538,127
- **Average Chars/Page:** 2169.9
- **Extraction Status:** `native_text`
- **Parser Runtime:** 19.97s (12.4 pages/sec)
- **Semantic Nodes Detected:** 0
- **Fallback Partitions:** 9
- **Proposed Ground Truth Nodes:** 21
- **Human Verification Required:** Yes (`human_verified = false`)
- **Document Evaluation Status:** **Critical Failure**

### Structural Output Breakdown
- **True Positives (TP):** 0
- **False Positives (FP):** 0
- **False Negatives (FN):** 21
- **Preliminary F1 Score:** 0.0%

### Detected Semantic Headings Sample (First 15):
*No semantic headings detected. Engine generated 9 zero-loss fallback partitions (`paragraph_density_partition`).*

### Ground Truth Comparison Table:

| Status | Expected Ground Truth | Predicted Heading | Page | Class Match | Parent Match | Conf | Method |
|---|---|---|---|---|---|---|---|
| **FN** | THE PREFACE | — | 0 | No | No | 0.00 | `missed` |
| **FN** | CHAPTER 1 | — | 0 | No | No | 0.00 | `missed` |
| **FN** | CHAPTER 2 | — | 0 | No | No | 0.00 | `missed` |
| **FN** | CHAPTER 3 | — | 0 | No | No | 0.00 | `missed` |
| **FN** | CHAPTER 4 | — | 0 | No | No | 0.00 | `missed` |
| **FN** | CHAPTER 5 | — | 0 | No | No | 0.00 | `missed` |
| **FN** | CHAPTER 6 | — | 0 | No | No | 0.00 | `missed` |
| **FN** | CHAPTER 7 | — | 0 | No | No | 0.00 | `missed` |
| **FN** | CHAPTER 8 | — | 0 | No | No | 0.00 | `missed` |
| **FN** | CHAPTER 9 | — | 0 | No | No | 0.00 | `missed` |
| **FN** | CHAPTER 10 | — | 0 | No | No | 0.00 | `missed` |
| **FN** | CHAPTER 11 | — | 0 | No | No | 0.00 | `missed` |
| **FN** | CHAPTER 12 | — | 0 | No | No | 0.00 | `missed` |
| **FN** | CHAPTER 13 | — | 0 | No | No | 0.00 | `missed` |
| **FN** | CHAPTER 14 | — | 0 | No | No | 0.00 | `missed` |
| **FN** | CHAPTER 15 | — | 0 | No | No | 0.00 | `missed` |
| **FN** | CHAPTER 16 | — | 0 | No | No | 0.00 | `missed` |
| **FN** | CHAPTER 17 | — | 0 | No | No | 0.00 | `missed` |
| **FN** | CHAPTER 18 | — | 0 | No | No | 0.00 | `missed` |
| **FN** | CHAPTER 19 | — | 0 | No | No | 0.00 | `missed` |
| **FN** | CHAPTER 20 | — | 0 | No | No | 0.00 | `missed` |

---
