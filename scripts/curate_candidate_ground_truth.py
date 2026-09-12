#!/usr/bin/env python3
"""
Novela Phase 3A — Candidate Ground Truth Curation Script.

Generates candidate canonical ground truth for all 10 corpus documents,
adhering strictly to canonical_schema.json and the Phase 3A methodological constraints:
- document-level human_verified = false
- node-level verification_status = candidate (or disputed)
- explicit scored_levels and deferred_levels
- edition-specific structure based on validation/Corpus PDFs
"""

import json
import os
import jsonschema

CORPUS_DIR = "validation/Corpus"
GT_DIR = "validation/ground_truth"
SCHEMA_PATH = "validation/schema/canonical_schema.json"

def build_all_candidate_gt():
    ground_truth_data = {}

    # =========================================================================
    # 001_middlemarch
    # =========================================================================
    ground_truth_data["001_middlemarch"] = {
        "document_id": "001_middlemarch",
        "title": "Middlemarch",
        "author": "George Eliot",
        "source_file": "2015.42254.Middlemarch.pdf",
        "edition_notes": "Scanned bitmap archive edition (638 pages, published ~1871-1872). Raw character extraction yields 0 characters without OCR. Structural verification against physical scan text is pending OCR enablement.",
        "human_verified": False,
        "verification_coverage": "candidate_machine_curated",
        "structural_notes": "Standard literary reference structure comprises a Prelude, 8 Books (each containing chapters), and a Finale. In this specific PDF, text is completely un-extracted (image-only scan). Chapter-level and Book-level structure are deferred from scoring until OCR is available.",
        "scored_levels": [],
        "deferred_levels": ["book", "chapter"],
        "benchmark_status": "extraction_limitation",
        "nodes": [
            {
                "node_id": "mm_prelude",
                "parent_id": None,
                "title": "Prelude",
                "type": "preface",
                "level": 1,
                "order": 1,
                "page_start": None,
                "page_end": None,
                "verification_status": "candidate",
                "verification_notes": "Known canonical structural node; unverified in source PDF due to 0-char extraction limitation.",
                "benchmark_status": "deferred"
            },
            {
                "node_id": "mm_book_1",
                "parent_id": None,
                "title": "Book I. Miss Brooke",
                "type": "book",
                "level": 1,
                "order": 2,
                "page_start": None,
                "page_end": None,
                "verification_status": "candidate",
                "verification_notes": "Canonical Book I; unverified in source PDF due to 0-char extraction limitation.",
                "benchmark_status": "deferred"
            },
            {
                "node_id": "mm_book_2",
                "parent_id": None,
                "title": "Book II. Old and Young",
                "type": "book",
                "level": 1,
                "order": 3,
                "page_start": None,
                "page_end": None,
                "verification_status": "candidate",
                "verification_notes": "Canonical Book II; unverified in source PDF due to 0-char extraction limitation.",
                "benchmark_status": "deferred"
            },
            {
                "node_id": "mm_book_3",
                "parent_id": None,
                "title": "Book III. Waiting for Death",
                "type": "book",
                "level": 1,
                "order": 4,
                "page_start": None,
                "page_end": None,
                "verification_status": "candidate",
                "verification_notes": "Canonical Book III; unverified in source PDF due to 0-char extraction limitation.",
                "benchmark_status": "deferred"
            },
            {
                "node_id": "mm_book_4",
                "parent_id": None,
                "title": "Book IV. Three Love Problems",
                "type": "book",
                "level": 1,
                "order": 5,
                "page_start": None,
                "page_end": None,
                "verification_status": "candidate",
                "verification_notes": "Canonical Book IV; unverified in source PDF due to 0-char extraction limitation.",
                "benchmark_status": "deferred"
            },
            {
                "node_id": "mm_book_5",
                "parent_id": None,
                "title": "Book V. The Dead Hand",
                "type": "book",
                "level": 1,
                "order": 6,
                "page_start": None,
                "page_end": None,
                "verification_status": "candidate",
                "verification_notes": "Canonical Book V; unverified in source PDF due to 0-char extraction limitation.",
                "benchmark_status": "deferred"
            },
            {
                "node_id": "mm_book_6",
                "parent_id": None,
                "title": "Book VI. The Widow and the Wife",
                "type": "book",
                "level": 1,
                "order": 7,
                "page_start": None,
                "page_end": None,
                "verification_status": "candidate",
                "verification_notes": "Canonical Book VI; unverified in source PDF due to 0-char extraction limitation.",
                "benchmark_status": "deferred"
            },
            {
                "node_id": "mm_book_7",
                "parent_id": None,
                "title": "Book VII. Two Temptations",
                "type": "book",
                "level": 1,
                "order": 8,
                "page_start": None,
                "page_end": None,
                "verification_status": "candidate",
                "verification_notes": "Canonical Book VII; unverified in source PDF due to 0-char extraction limitation.",
                "benchmark_status": "deferred"
            },
            {
                "node_id": "mm_book_8",
                "parent_id": None,
                "title": "Book VIII. Sunset and Sunrise",
                "type": "book",
                "level": 1,
                "order": 9,
                "page_start": None,
                "page_end": None,
                "verification_status": "candidate",
                "verification_notes": "Canonical Book VIII; unverified in source PDF due to 0-char extraction limitation.",
                "benchmark_status": "deferred"
            },
            {
                "node_id": "mm_finale",
                "parent_id": None,
                "title": "Finale",
                "type": "epilogue",
                "level": 1,
                "order": 10,
                "page_start": None,
                "page_end": None,
                "verification_status": "candidate",
                "verification_notes": "Canonical Finale; unverified in source PDF due to 0-char extraction limitation.",
                "benchmark_status": "deferred"
            }
        ]
    }

    # =========================================================================
    # 002_frankenstein
    # =========================================================================
    frank_nodes = [
        {
            "node_id": "frank_intro",
            "parent_id": None,
            "title": "Introduction",
            "type": "introduction",
            "level": 1,
            "order": 1,
            "page_start": 4,
            "page_end": 11,
            "verification_status": "candidate",
            "verification_notes": "Author's Introduction (1831/1888 edition) on pages 4-11.",
            "benchmark_status": "scored"
        },
        {
            "node_id": "frank_preface",
            "parent_id": None,
            "title": "Preface",
            "type": "preface",
            "level": 1,
            "order": 2,
            "page_start": 12,
            "page_end": 14,
            "verification_status": "candidate",
            "verification_notes": "Original 1818 Preface (written by P.B. Shelley) on pages 12-14.",
            "benchmark_status": "scored"
        },
        {
            "node_id": "frank_letter_1",
            "parent_id": None,
            "title": "Letter I",
            "type": "letter",
            "level": 1,
            "order": 3,
            "page_start": 15,
            "page_end": 19,
            "verification_status": "candidate",
            "verification_notes": "Walton Letter I (Dec 11, 17-) starting page 15.",
            "benchmark_status": "scored"
        },
        {
            "node_id": "frank_letter_2",
            "parent_id": None,
            "title": "Letter II",
            "type": "letter",
            "level": 1,
            "order": 4,
            "page_start": 20,
            "page_end": 24,
            "verification_status": "candidate",
            "verification_notes": "Walton Letter II (March 28, 17-) starting page 20.",
            "benchmark_status": "scored"
        },
        {
            "node_id": "frank_letter_3",
            "parent_id": None,
            "title": "Letter III",
            "type": "letter",
            "level": 1,
            "order": 5,
            "page_start": 25,
            "page_end": 26,
            "verification_status": "candidate",
            "verification_notes": "Walton Letter III (July 7, 17-) starting page 25.",
            "benchmark_status": "scored"
        },
        {
            "node_id": "frank_letter_4",
            "parent_id": None,
            "title": "Letter IV",
            "type": "letter",
            "level": 1,
            "order": 6,
            "page_start": 27,
            "page_end": 37,
            "verification_status": "candidate",
            "verification_notes": "Walton Letter IV (August 5, 17-) starting page 27.",
            "benchmark_status": "scored"
        }
    ]
    # Chapters 1-24
    frank_pages = [38, 45, 52, 62, 70, 78, 89, 100, 110, 117, 126, 135, 143, 150, 157, 168, 179, 186, 196, 205, 218, 233, 246, 255]
    roman = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII", "XIII", "XIV", "XV", "XVI", "XVII", "XVIII", "XIX", "XX", "XXI", "XXII", "XXIII", "XXIV"]
    for idx, (r, p) in enumerate(zip(roman, frank_pages), start=1):
        frank_nodes.append({
            "node_id": f"frank_ch_{idx}",
            "parent_id": None,
            "title": f"Chapter {r}",
            "type": "chapter",
            "level": 1,
            "order": 6 + idx,
            "page_start": p,
            "page_end": None,
            "verification_status": "candidate",
            "verification_notes": f"Chapter {r} body heading.",
            "benchmark_status": "scored"
        })

    ground_truth_data["002_frankenstein"] = {
        "document_id": "002_frankenstein",
        "title": "Frankenstein; or, The Modern Prometheus",
        "author": "Mary Wollstonecraft Shelley",
        "source_file": "Shelley_1888_Frankenstein.pdf",
        "edition_notes": "Routledge Pocket Library edition (1888, 316 pages). Contains Introduction, Preface, 4 Letters, and 24 Chapters.",
        "human_verified": False,
        "verification_coverage": "candidate_machine_curated",
        "structural_notes": "Reclassified Letters I-IV from generic chapter to type 'letter'. Scored at level 1 across front matter, letters, and chapters.",
        "scored_levels": ["introduction", "preface", "letter", "chapter"],
        "deferred_levels": [],
        "benchmark_status": "active",
        "nodes": frank_nodes
    }

    # =========================================================================
    # 003_the_time_machine
    # =========================================================================
    tm_nodes = []
    tm_pages = [9, 17, 26, 33, 44, 59, 69, 78, 86, 96, 107, 114, 123, 131, 137, 142]
    for idx, p in enumerate(tm_pages, start=1):
        tm_nodes.append({
            "node_id": f"tm_ch_{idx}",
            "parent_id": None,
            "title": f"Chapter {idx}",
            "type": "chapter",
            "level": 1,
            "order": idx,
            "page_start": p,
            "page_end": None,
            "verification_status": "candidate",
            "verification_notes": f"Chapter {idx} heading.",
            "benchmark_status": "scored"
        })
    tm_nodes.append({
        "node_id": "tm_epilogue",
        "parent_id": None,
        "title": "Epilogue",
        "type": "epilogue",
        "level": 1,
        "order": 17,
        "page_start": 147,
        "page_end": 150,
        "verification_status": "candidate",
        "verification_notes": "Epilogue concluding narrative.",
        "benchmark_status": "scored"
    })

    ground_truth_data["003_the_time_machine"] = {
        "document_id": "003_the_time_machine",
        "title": "The Time Machine",
        "author": "H.G. Wells",
        "source_file": "Wells_1922_Time_Machine.pdf",
        "edition_notes": "Heinemann 1922 edition (221 pages). Contains 16 Chapters and an Epilogue.",
        "human_verified": False,
        "verification_coverage": "candidate_machine_curated",
        "structural_notes": "Standard single-tier chapter structure (16 chapters + epilogue). Parser successfully extracts body chapters; minor TOC noise on front pages.",
        "scored_levels": ["chapter", "epilogue"],
        "deferred_levels": [],
        "benchmark_status": "active",
        "nodes": tm_nodes
    }

    # =========================================================================
    # 004_les_miserables (Option A: Volume -> Book, Scored: [volume, book], Deferred: [chapter])
    # =========================================================================
    lm_volumes = [
        ("vol_1", "Volume I: Fantine", 1, 8, 20),
        ("vol_2", "Volume II: Cosette", 2, 8, 282),
        ("vol_3", "Volume III: Marius", 3, 8, 520),
        ("vol_4", "Volume IV: The Idyll in the Rue Plumet and the Epic in the Rue St. Denis", 4, 15, 728),
        ("vol_5", "Volume V: Jean Valjean", 5, 9, 1030)
    ]

    lm_book_titles = {
        1: [
            ("Book I: An Upright Man", 20),
            ("Book II: The Fall", 69),
            ("Book III: In the Year 1817", 117),
            ("Book IV: To Entrust Is Sometimes to Abandon", 143),
            ("Book V: The Descent", 155),
            ("Book VI: Javert", 191),
            ("Book VII: The Champmathieu Affair", 202),
            ("Book VIII: Counter-stroke", 263)
        ],
        2: [
            ("Book I: Waterloo", 282),
            ("Book II: The Ship Orion", 330),
            ("Book III: Fulfilment of the Promise to the Departed", 343),
            ("Book IV: The Old Gorbeau House", 391),
            ("Book V: A Dark Chase Needs a Silent Hound", 406),
            ("Book VI: Petit Picpus", 434),
            ("Book VII: A Parenthesis", 460),
            ("Book VIII: Cemeteries Take What Is Given Them", 472)
        ],
        3: [
            ("Book I: Paris Atomised", 520),
            ("Book II: The Grand Bourgeois", 537),
            ("Book III: The Grandfather and the Grandson", 546),
            ("Book IV: The Friends of the A B C", 578),
            ("Book V: The Excellence of Misfortune", 605),
            ("Book VI: The Conjunction of Two Stars", 622),
            ("Book VII: Patron-Minette", 638),
            ("Book VIII: The Noxious Poor", 646)
        ],
        4: [
            ("Book I: A Few Pages of History", 728),
            ("Book II: Eponine", 760),
            ("Book III: The House in the Rue Plumet", 776),
            ("Book IV: Aid from Below May Be Aid from Above", 808),
            ("Book V: The End of Which Is Unlike the Beginning", 817),
            ("Book VI: Little Gavroche", 832),
            ("Book VII: Argot", 866),
            ("Book VIII: Enchantments and Desolations", 886),
            ("Book IX: Where Are They Going?", 918),
            ("Book X: June 5th, 1832", 925),
            ("Book XI: The Atom Fraternises with the Hurricane", 944),
            ("Book XII: Corinth", 956),
            ("Book XIII: Marius Enters the Shadow", 985),
            ("Book XIV: The Grandeurs of Despair", 995),
            ("Book XV: The Rue de l'Homme Armé", 1012)
        ],
        5: [
            ("Book I: War Between Four Walls", 1030),
            ("Book II: The Intestine of the Leviathan", 1098),
            ("Book III: Mud But the Soul", 1121),
            ("Book IV: Javert Derailed", 1162),
            ("Book V: Grandson and Grandfather", 1173),
            ("Book VI: The White Night", 1205),
            ("Book VII: The Last Draught from the Cup", 1222),
            ("Book VIII: The Twilight Waning", 1238),
            ("Book IX: Supreme Darkness, Supreme Dawn", 1254)
        ]
    }

    lm_nodes = []
    global_order = 1
    for v_id, v_title, v_num, bk_count, v_page in lm_volumes:
        vol_node_id = f"lm_vol_{v_num}"
        lm_nodes.append({
            "node_id": vol_node_id,
            "parent_id": None,
            "title": v_title,
            "type": "volume",
            "level": 1,
            "order": global_order,
            "page_start": v_page,
            "page_end": None,
            "verification_status": "candidate",
            "verification_notes": f"Volume {v_num} major partition heading in source PDF.",
            "benchmark_status": "scored"
        })
        global_order += 1
        for b_idx, (b_title, b_page) in enumerate(lm_book_titles[v_num], start=1):
            lm_nodes.append({
                "node_id": f"lm_vol_{v_num}_bk_{b_idx}",
                "parent_id": vol_node_id,
                "title": b_title,
                "type": "book",
                "level": 2,
                "order": global_order,
                "page_start": b_page,
                "page_end": None,
                "verification_status": "candidate",
                "verification_notes": f"Volume {v_num}, Book {b_idx} heading verified in source PDF text.",
                "benchmark_status": "scored"
            })
            global_order += 1

    ground_truth_data["004_les_miserables"] = {
        "document_id": "004_les_miserables",
        "title": "Les Misérables",
        "author": "Victor Hugo",
        "source_file": "[Hugo_Victor]_Les_Miserables.pdf",
        "edition_notes": "Complete single-volume edition (1279 pages). Contains 5 Volumes and 48 Books.",
        "human_verified": False,
        "verification_coverage": "candidate_machine_curated",
        "structural_notes": "Implemented Option A (Volume -> Book hierarchy, 53 scored canonical nodes). Chapter-level structure (~365 chapters) is deferred from current benchmark scoring to prevent artificial false-positive distortions. Parser-detected chapter nodes are classified as out-of-scope/deferred rather than false positives.",
        "scored_levels": ["volume", "book"],
        "deferred_levels": ["chapter"],
        "benchmark_status": "active",
        "nodes": lm_nodes
    }

    # =========================================================================
    # 005_sherlock_holmes
    # =========================================================================
    sh_adventures = [
        "I. A Scandal in Bohemia",
        "II. The Red-Headed League",
        "III. A Case of Identity",
        "IV. The Boscombe Valley Mystery",
        "V. The Five Orange Pips",
        "VI. The Man with the Twisted Lip",
        "VII. The Adventure of the Blue Carbuncle",
        "VIII. The Adventure of the Speckled Band",
        "IX. The Adventure of the Engineer's Thumb",
        "X. The Adventure of the Noble Bachelor",
        "XI. The Adventure of the Beryl Coronet",
        "XII. The Adventure of the Copper Beeches"
    ]
    sh_pages = [9, 36, 61, 82, 109, 131, 157, 182, 210, 235, 262, 289]
    sh_nodes = []
    for idx, (title, p) in enumerate(zip(sh_adventures, sh_pages), start=1):
        sh_nodes.append({
            "node_id": f"sh_adv_{idx}",
            "parent_id": None,
            "title": f"Adventure {idx}: {title.split('. ', 1)[1]}",
            "type": "adventure",
            "level": 1,
            "order": idx,
            "page_start": p,
            "page_end": None,
            "subtitles": [title],
            "verification_status": "candidate",
            "verification_notes": f"Adventure {idx} starting on page {p}. Headings in PDF are styled as 'ADVENTURE I. ...'.",
            "benchmark_status": "scored"
        })

    ground_truth_data["005_sherlock_holmes"] = {
        "document_id": "005_sherlock_holmes",
        "title": "The Adventures of Sherlock Holmes",
        "author": "Arthur Conan Doyle",
        "source_file": "adventuresofsher001892doyl.pdf",
        "edition_notes": "George Newnes first book edition (1892, 332 pages). Contains 12 short story adventures.",
        "human_verified": False,
        "verification_coverage": "candidate_machine_curated",
        "structural_notes": "Single-tier collection of 12 adventures. Parser failure on this book was caused by 'ADVENTURE' keyword absence in parser lexical table, not structural ambiguity.",
        "scored_levels": ["adventure"],
        "deferred_levels": [],
        "benchmark_status": "active",
        "nodes": sh_nodes
    }

    # =========================================================================
    # 006_alices_adventures
    # =========================================================================
    alice_chapters = [
        "Down the Rabbit-Hole",
        "The Pool of Tears",
        "A Caucus-Race and a Long Tale",
        "The Rabbit Sends in a Little Bill",
        "Advice from a Caterpillar",
        "Pig and Pepper",
        "A Mad Tea-Party",
        "The Queen's Croquet-Ground",
        "The Mock Turtle's Story",
        "The Lobster Quadrille",
        "Who Stole the Tarts?",
        "Alice's Evidence"
    ]
    alice_pages = [13, 27, 41, 55, 73, 91, 111, 129, 147, 167, 185, 199]
    alice_nodes = []
    for idx, (title, p) in enumerate(zip(alice_chapters, alice_pages), start=1):
        alice_nodes.append({
            "node_id": f"alice_ch_{idx}",
            "parent_id": None,
            "title": f"Chapter {idx}: {title}",
            "type": "chapter",
            "level": 1,
            "order": idx,
            "page_start": p,
            "page_end": None,
            "subtitles": [title],
            "verification_status": "candidate",
            "verification_notes": f"Chapter {idx} starting on page {p}. Heading has large dropped capital initial line.",
            "benchmark_status": "scored"
        })

    ground_truth_data["006_alices_adventures"] = {
        "document_id": "006_alices_adventures",
        "title": "Alice's Adventures in Wonderland",
        "author": "Lewis Carroll",
        "source_file": "alicesadventures00carr_20.pdf",
        "edition_notes": "Macmillan illustrated edition (226 pages). Contains 12 Chapters.",
        "human_verified": False,
        "verification_coverage": "candidate_machine_curated",
        "structural_notes": "Single-tier chapter structure (12 chapters). Parser dropped chapters due to dropped capital initial line typography.",
        "scored_levels": ["chapter"],
        "deferred_levels": [],
        "benchmark_status": "active",
        "nodes": alice_nodes
    }

    # =========================================================================
    # 007_count_of_monte_cristo (Volume 1 edition in Corpus, 38 chapters)
    # =========================================================================
    cmc_chapters = [
        "Marseilles—The Arrival", "Father and Son", "The Catalans", "Conspiracy", "The Marriage-Feast",
        "The Deputy Procureur du Roi", "The Examination", "The Château d'If", "The Evening of the Betrothal",
        "The King's Closet", "The Corsican Ogre", "Father and Son", "The Hundred Days",
        "The Two Prisoners", "Number 34 and Number 27", "A Learned Italian", "The Abbé's Chamber",
        "The Treasure", "The Third Attack", "The Cemetery of the Château d'If", "The Isle of Tiboulen",
        "The Smugglers", "The Isle of Monte-Cristo", "The Secret Cave", "The Unknown",
        "The Pont du Gard", "The Recital", "The Prison Register", "The House of Morrel and Son",
        "The Fifth of September", "Italy—Sinbad the Sailor", "The Awakening", "Roman Bandits",
        "The Colosseum", "La Mazzolata", "The Carnival at Rome", "The Catacombs of Saint Sebastian",
        "The Compact"
    ]
    cmc_pages = [7, 15, 23, 33, 40, 52, 63, 73, 82, 88, 96, 104, 111, 118, 127, 140, 153, 169, 180, 189, 196, 204, 214, 223, 232, 245, 258, 273, 281, 294, 308, 328, 336, 357, 375, 388, 403, 421]
    cmc_nodes = []
    for idx, title in enumerate(cmc_chapters, start=1):
        cmc_nodes.append({
            "node_id": f"cmc_ch_{idx}",
            "parent_id": None,
            "title": f"Chapter {idx}: {title}",
            "type": "chapter",
            "level": 1,
            "order": idx,
            "page_start": None,
            "page_end": None,
            "subtitles": [title],
            "verification_status": "candidate",
            "verification_notes": f"Chapter {idx} in Volume 1 edition.",
            "benchmark_status": "scored"
        })

    ground_truth_data["007_count_of_monte_cristo"] = {
        "document_id": "007_count_of_monte_cristo",
        "title": "The Count of Monte-Cristo (Volume 1)",
        "author": "Alexandre Dumas",
        "source_file": "countofmontecris01duma.pdf",
        "edition_notes": "Walter Scott edition (Volume 1, 360 pages). Contains Chapters 1 to 38.",
        "human_verified": False,
        "verification_coverage": "candidate_machine_curated",
        "structural_notes": "Source PDF is Volume 1 only (38 chapters). Standard full work contains 117 chapters across multiple volumes; GT is scoped specifically to the 38 chapters present in this benchmark PDF.",
        "scored_levels": ["chapter"],
        "deferred_levels": [],
        "benchmark_status": "active",
        "nodes": cmc_nodes
    }

    # =========================================================================
    # 008_the_iliad (Penguin Classics Fagles Edition)
    # =========================================================================
    iliad_nodes = [
        # Front Matter
        {
            "node_id": "iliad_fm_preface",
            "parent_id": None,
            "title": "Preface",
            "type": "front_matter",
            "level": 1,
            "order": 1,
            "page_start": 9,
            "page_end": 14,
            "verification_status": "candidate",
            "verification_notes": "Translator's Preface by Robert Fagles (pp. 9-14).",
            "benchmark_status": "scored"
        },
        {
            "node_id": "iliad_fm_intro",
            "parent_id": None,
            "title": "Introduction",
            "type": "front_matter",
            "level": 1,
            "order": 2,
            "page_start": 17,
            "page_end": 64,
            "verification_status": "candidate",
            "verification_notes": "Scholarly Introduction by Bernard Knox (pp. 17-64). Internal thematic subheadings within Knox intro are treated as non-structural apparatus.",
            "benchmark_status": "scored"
        },
        {
            "node_id": "iliad_fm_trans_note",
            "parent_id": None,
            "title": "Note on the Translation",
            "type": "front_matter",
            "level": 1,
            "order": 3,
            "page_start": 69,
            "page_end": 74,
            "verification_status": "candidate",
            "verification_notes": "Translator's Note on verse, meter, and names (pp. 69-74).",
            "benchmark_status": "scored"
        }
    ]

    # Primary Narrative: Books 1-24
    iliad_book_pages = [77, 99, 128, 145, 164, 195, 214, 230, 251, 275, 296, 326, 342, 370, 388, 412, 442, 467, 489, 503, 520, 541, 559, 588]
    iliad_book_subtitles = [
        "The Rage of Achilles", "Great Gathering of Armies", "Helen Reviews the Champions", "The Truce Erupts in War",
        "Diomedes Fights the Gods", "Hector Returns to Troy", "Ajax Duels with Hector", "The Tide of Battle Turns",
        "The Embassy to Achilles", "Marauding Through the Night", "Agamemnon's Day of Glory", "The Trojans Storm the Rampart",
        "Battling for the Ships", "Hera Outwits Zeus", "The Achaean Armies at Bay", "Patroclus Fights and Dies",
        "The Menelaus' Finest Hour", "The Shield of Achilles", "The Champion Goes to War", "Olympian Gods in Arms",
        "Achilles Fights the River", "The Death of Hector", "Funeral Games for Patroclus", "Achilles and Priam"
    ]
    for idx, (p, subt) in enumerate(zip(iliad_book_pages, iliad_book_subtitles), start=1):
        iliad_nodes.append({
            "node_id": f"iliad_bk_{idx}",
            "parent_id": None,
            "title": f"Book {idx}: {subt}",
            "type": "book",
            "level": 1,
            "order": 3 + idx,
            "page_start": p,
            "page_end": None,
            "subtitles": [f"BOOK {idx}", subt],
            "verification_status": "candidate",
            "verification_notes": f"Primary Narrative Book {idx} starting page {p}.",
            "benchmark_status": "scored"
        })

    # Back Matter
    iliad_back_matter = [
        ("iliad_bm_notes", "Notes on the Translation", "back_matter", 637, 648, "candidate", "Explanatory scholarly notes by line reference."),
        ("iliad_bm_genealogies", "The Genealogies", "back_matter", 649, 650, "candidate", "Mythological lineage charts."),
        ("iliad_bm_reading", "Suggestions for Further Reading", "back_matter", 651, 654, "candidate", "Scholarly bibliography."),
        ("iliad_bm_glossary", "Pronouncing Glossary", "back_matter", 655, 699, "candidate", "Alphabetical character glossary with page citations.")
    ]
    for idx, (nid, title, ntype, pstart, pend, vstat, vnote) in enumerate(iliad_back_matter, start=1):
        iliad_nodes.append({
            "node_id": nid,
            "parent_id": None,
            "title": title,
            "type": ntype,
            "level": 1,
            "order": 27 + idx,
            "page_start": pstart,
            "page_end": pend,
            "verification_status": vstat,
            "verification_notes": vnote,
            "benchmark_status": "scored"
        })

    ground_truth_data["008_the_iliad"] = {
        "document_id": "008_the_iliad",
        "title": "The Iliad",
        "author": "Homer (Translated by Robert Fagles)",
        "source_file": "homer_the_iliad_penguin_classics_deluxe_edition-robert-fagles.pdf",
        "edition_notes": "Penguin Classics Deluxe Edition (699 pages, 1990). Contains extensive scholarly front matter, 24 narrative Books, and scholarly back matter apparatus.",
        "human_verified": False,
        "verification_coverage": "candidate_machine_curated",
        "structural_notes": "Separated into 3 distinct functional zones: Front Matter (Preface, Knox Introduction, Translation Note), Primary Narrative (Books 1-24), and Back Matter (Notes, Genealogies, Bibliography, Pronouncing Glossary). Ambiguous internal headings inside scholarly apparatus are marked as non-structural candidate nodes to prevent over-segmentation.",
        "scored_levels": ["front_matter", "book", "back_matter"],
        "deferred_levels": ["apparatus_subheading"],
        "benchmark_status": "active",
        "nodes": iliad_nodes
    }

    # =========================================================================
    # 009_moby_dick (Volume 1 London Bentley Edition in Corpus: Etymology, Extracts, Ch 1-60)
    # =========================================================================
    mb_nodes = [
        {
            "node_id": "mb_etymology",
            "parent_id": None,
            "title": "Etymology",
            "type": "front_matter",
            "level": 1,
            "order": 1,
            "page_start": 15,
            "page_end": 16,
            "verification_status": "candidate",
            "verification_notes": "Etymology front matter supplied by a late Consumptive Usher.",
            "benchmark_status": "scored"
        },
        {
            "node_id": "mb_extracts",
            "parent_id": None,
            "title": "Extracts",
            "type": "front_matter",
            "level": 1,
            "order": 2,
            "page_start": 17,
            "page_end": 30,
            "verification_status": "candidate",
            "verification_notes": "Extracts sub-sub-librarian compilation.",
            "benchmark_status": "scored"
        }
    ]

    mb_subtitles = [
        "Loomings", "The Carpet-Bag", "The Spouter-Inn", "The Counterpane", "Breakfast",
        "The Street", "The Chapel", "The Pulpit", "The Sermon", "A Bosom Friend",
        "Nightgown", "Biographical", "Wheelbarrow", "Nantucket", "Chowder",
        "The Ship", "The Ramadan", "His Mark", "The Prophet", "All Astir",
        "Going Aboard", "Merry Christmas", "The Lee Shore", "The Advocate", "Postscript",
        "Knights and Squires", "Knights and Squires", "Ahab", "To Him, Stubb", "The Pipe",
        "Queen Mab", "Cetology", "The Specksynder", "The Cabin-Table", "The Mast-Head",
        "The Quarter-Deck", "Sunset", "Dusk", "First Night-Watch", "Midnight, Forecastle",
        "Moby-Dick", "The Whiteness of the Whale", "Hark!", "The Chart", "The Affidavit",
        "Surmises", "The Mat-Maker", "The First Lowering", "The Hyena", "Ahab's Boat and Crew. Fedallah",
        "The Spirit-Spout", "The Albatross", "The Gam", "The Town-Ho's Story", "Of the Monstrous Pictures of Whales",
        "Of the Less Erroneous Pictures of Whales", "Of Whales in Paint; in Teeth; in Wood; in Sheet-Iron; in Stone; in Mountains; in Stars", "Brit", "Squid", "The Line"
    ]
    mb_pages = [31, 38, 43, 61, 66, 69, 72, 76, 79, 90, 95, 98, 101, 107, 110, 114, 132, 140, 145, 149, 152, 156, 162, 164, 170, 171, 175, 181, 186, 190, 191, 194, 210, 214, 221, 229, 239, 241, 243, 244, 252, 264, 275, 277, 284, 295, 299, 303, 316, 319, 323, 328, 331, 336, 361, 367, 372, 376, 380, 383]

    for idx, (subt, p) in enumerate(zip(mb_subtitles, mb_pages), start=1):
        mb_nodes.append({
            "node_id": f"mb_ch_{idx}",
            "parent_id": None,
            "title": f"Chapter {idx}",
            "type": "chapter",
            "level": 1,
            "order": 2 + idx,
            "page_start": p,
            "page_end": None,
            "subtitles": [subt, f"CHAPTER {idx}. {subt}"],
            "verification_status": "candidate",
            "verification_notes": f"Chapter {idx} ('{subt}') on page {p}. Scored primarily on chapter numbering; subtitles stored as optional metadata.",
            "benchmark_status": "scored"
        })

    ground_truth_data["009_moby_dick"] = {
        "document_id": "009_moby_dick",
        "title": "Moby-Dick; or, The Whale (Volume 1)",
        "author": "Herman Melville",
        "source_file": "mobydickorwhale01melvuoft.pdf",
        "edition_notes": "Richard Bentley 1851 first English edition (Volume 1 of 3, 394 pages). Contains Etymology, Extracts, and Chapters 1 to 60 (Loomings through The Line).",
        "human_verified": False,
        "verification_coverage": "candidate_machine_curated",
        "structural_notes": "Source PDF is Volume 1 only (60 chapters), ending at Chapter LX on page 383. Canonical GT is aligned to this actual edition rather than a 135-chapter single-volume edition. Printed TOC entries on pages 13-14 are excluded from candidate headings. Chapter matching is based on 'CHAPTER N'; descriptive subtitles are recorded as optional metadata.",
        "scored_levels": ["front_matter", "chapter"],
        "deferred_levels": [],
        "benchmark_status": "active",
        "nodes": mb_nodes
    }

    # =========================================================================
    # 010_dorian_gray
    # =========================================================================
    dg_nodes = [
        {
            "node_id": "dg_preface",
            "parent_id": None,
            "title": "The Preface",
            "type": "preface",
            "level": 1,
            "order": 1,
            "page_start": 5,
            "page_end": 7,
            "verification_status": "candidate",
            "verification_notes": "Oscar Wilde's aphoristic Preface on pages 5-7.",
            "benchmark_status": "scored"
        }
    ]
    dg_pages = [9, 25, 41, 55, 73, 85, 96, 110, 124, 137, 147, 166, 175, 185, 198, 209, 219, 227, 235, 244]
    for idx, p in enumerate(dg_pages, start=1):
        dg_nodes.append({
            "node_id": f"dg_ch_{idx}",
            "parent_id": None,
            "title": f"Chapter {idx}",
            "type": "chapter",
            "level": 1,
            "order": 1 + idx,
            "page_start": p,
            "page_end": None,
            "verification_status": "candidate",
            "verification_notes": f"Chapter {idx} body heading (styled in small-caps in source PDF).",
            "benchmark_status": "scored"
        })

    ground_truth_data["010_picture_of_dorian_gray"] = {
        "document_id": "010_picture_of_dorian_gray",
        "title": "The Picture of Dorian Gray",
        "author": "Oscar Wilde",
        "source_file": "pictureofdoriang0000osca_s9a9.pdf",
        "edition_notes": "Ward Lock and Bowden 1891 edition (248 pages). Contains Preface and 20 Chapters.",
        "human_verified": False,
        "verification_coverage": "candidate_machine_curated",
        "structural_notes": "Single-tier chapter structure (Preface + 20 chapters). Headings in this edition use small-caps styling which caused parser misses in the v1 baseline.",
        "scored_levels": ["preface", "chapter"],
        "deferred_levels": [],
        "benchmark_status": "active",
        "nodes": dg_nodes
    }

    return ground_truth_data

def validate_and_save():
    # Load schema
    with open(SCHEMA_PATH, "r") as f:
        schema = json.load(f)

    validator = jsonschema.Draft7Validator(schema)
    gt_data = build_all_candidate_gt()

    total_nodes = 0
    total_candidate_nodes = 0
    total_disputed_nodes = 0
    total_human_verified_nodes = 0
    total_deferred_nodes = 0

    os.makedirs(GT_DIR, exist_ok=True)

    for doc_id, data in sorted(gt_data.items()):
        # Validate against schema
        errors = list(validator.iter_errors(data))
        if errors:
            print(f"Validation ERROR in {doc_id}:")
            for e in errors:
                print(f"  - {e.message}")
            raise ValueError(f"Schema validation failed for {doc_id}")

        filepath = os.path.join(GT_DIR, f"{doc_id}.json")
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

        doc_nodes = len(data["nodes"])
        total_nodes += doc_nodes
        for n in data["nodes"]:
            vstat = n.get("verification_status")
            bstat = n.get("benchmark_status")
            if vstat == "candidate":
                total_candidate_nodes += 1
            elif vstat == "disputed":
                total_disputed_nodes += 1
            elif vstat == "human_verified":
                total_human_verified_nodes += 1
            
            if bstat == "deferred" or bstat == "excluded":
                total_deferred_nodes += 1

        print(f"✓ Saved candidate GT for {doc_id} ({doc_nodes} nodes, scored: {data['scored_levels']}, deferred: {data['deferred_levels']})")

    print("\n=======================================================")
    print("PHASE 3A CANDIDATE GT CURATION SUMMARY")
    print("=======================================================")
    print(f"Total documents: {len(gt_data)}")
    print(f"Total canonical nodes: {total_nodes}")
    print(f"  - Candidate nodes: {total_candidate_nodes}")
    print(f"  - Human-verified nodes: {total_human_verified_nodes} (STRICTLY 0 as required)")
    print(f"  - Disputed nodes: {total_disputed_nodes}")
    print(f"  - Benchmark-deferred nodes: {total_deferred_nodes}")
    print(f"All files validated against {SCHEMA_PATH}")

if __name__ == "__main__":
    validate_and_save()
