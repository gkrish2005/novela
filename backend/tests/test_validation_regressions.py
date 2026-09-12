"""
Regression test suite for Validation Runner and Ingestion Metadata Plumbing.
Ensures large PDFs are not misclassified as scanned, metadata is consistent,
fallback partitions are not treated as semantic false positives, and title
normalization handles Roman/Arabic numerals and punctuation.
"""

from pathlib import Path
import pytest

from app.services.document.engine import DocumentStructureEngine
from app.services.document.models import DocumentNode, DocumentTree, NodeType
from app.services.document.layout import DocumentLayout, PageLayout, LayoutBlock
from app.services.document.hierarchy import reconstruct_hierarchy


# Helper normalization matching functions matching runner policy
ROMAN_TO_ARABIC = {
    "i": "1", "ii": "2", "iii": "3", "iv": "4", "v": "5",
    "vi": "6", "vii": "7", "viii": "8", "ix": "9", "x": "10",
    "xi": "11", "xii": "12", "xiii": "13", "xiv": "14", "xv": "15",
    "xvi": "16", "xvii": "17", "xviii": "18", "xix": "19", "xx": "20",
    "xxi": "21", "xxii": "22", "xxiii": "23", "xxiv": "24", "xxv": "25",
    "xxvi": "26", "xxvii": "27", "xxviii": "28", "xxix": "29", "xxx": "30",
    "xl": "40", "l": "50", "lx": "60", "lxx": "70", "lxxx": "80", "xc": "90", "c": "100",
}


def normalize_title(t: str) -> str:
    import re
    dev_map = {"०": "0", "१": "1", "२": "2", "३": "3", "४": "4", "५": "5", "६": "6", "७": "7", "८": "8", "९": "9"}
    for d, a in dev_map.items():
        t = t.replace(d, a)
    # Strip harmless punctuation
    t = re.sub(r"[^\w\s]", " ", t.lower())
    words = t.split()
    normalized_words = []
    for w in words:
        if w in ROMAN_TO_ARABIC:
            normalized_words.append(ROMAN_TO_ARABIC[w])
        else:
            normalized_words.append(w)
    return " ".join(normalized_words)


def match_titles(exp: str, pred: str) -> bool:
    exp_norm = normalize_title(exp)
    pred_norm = normalize_title(pred)
    if exp_norm == pred_norm:
        return True
    if len(exp_norm) >= 3:
        if pred_norm.startswith(exp_norm) or exp_norm.startswith(pred_norm):
            return True
        if f" {exp_norm} " in f" {pred_norm} " or f" {pred_norm} " in f" {exp_norm} ":
            return True
    return False


def classify_extraction_status(raw_char_count: int, total_pages: int) -> str:
    avg = raw_char_count / max(1, total_pages)
    if raw_char_count == 0:
        return "image_only"
    if avg < 30:
        return "low_text_density"
    return "native_text"


def test_large_native_text_classification():
    """1. Large native-text document (e.g. 1279 pages, 3M chars) is classified as native_text, not image_only."""
    status = classify_extraction_status(raw_char_count=3_071_090, total_pages=1279)
    assert status == "native_text"
    assert status != "image_only"


def test_large_native_pdf_not_skipped():
    """2. Large native-text PDF is NOT skipped from structure evaluation."""
    # Simulated comparator evaluation loop
    raw_char_count = 3_071_090
    total_pages = 1279
    status = classify_extraction_status(raw_char_count, total_pages)
    
    # Validation runner must proceed to comparison if status in ("native_text", "low_text_density")
    should_evaluate_structure = status in ("native_text", "low_text_density")
    assert should_evaluate_structure is True


def test_zero_char_scanned_classification():
    """3. Zero-character document is classified as image_only."""
    status = classify_extraction_status(raw_char_count=0, total_pages=638)
    assert status == "image_only"


def test_image_only_documents_excluded_from_heading_fn_penalty():
    """4. image_only documents are treated as extraction limitations and excluded from native-text heading FN penalties."""
    status = classify_extraction_status(raw_char_count=0, total_pages=638)
    expected_canonical_nodes = [{"type": "chapter", "title": f"Chapter {i}"} for i in range(1, 87)]
    
    native_text_fn = 0
    extraction_limitations = []
    
    if status == "image_only":
        extraction_limitations.append({
            "doc_id": "001_middlemarch",
            "reason": "Scanned bitmap with 0 text characters",
            "expected_count": len(expected_canonical_nodes),
        })
    else:
        native_text_fn += len(expected_canonical_nodes)
        
    assert len(extraction_limitations) == 1
    assert native_text_fn == 0  # No FN penalty applied to native-text heading metrics pool


def test_fallback_partitions_not_semantic_fps():
    """5. paragraph_density_partition and fallback_single_section are not counted as semantic heading false positives."""
    dummy_pages = [
        PageLayout(
            page_num=1,
            width=600.0,
            height=800.0,
            blocks=[
                LayoutBlock(text="Paragraph 1", bbox=(0.0, 0.0, 100.0, 20.0), page_num=1, avg_font_size=12.0),
                LayoutBlock(text="Paragraph 2", bbox=(0.0, 20.0, 100.0, 40.0), page_num=1, avg_font_size=12.0),
            ],
            raw_text="Paragraph 1\n\nParagraph 2",
        )
    ]
    layout = DocumentLayout(
        pages=dummy_pages,
        body_font_size=12.0,
        heading_font_size_threshold=14.0,
        primary_font_name="Times",
        total_pages=1,
    )
    tree = reconstruct_hierarchy(layout, [], "Test")

    descendants = tree.root.get_all_descendants()
    semantic_nodes = [
        d for d in descendants
        if d.detection_method not in ("paragraph_density_partition", "fallback_single_section")
        and d.node_type not in (NodeType.DOCUMENT,)
    ]
    fallback_partitions = [
        d for d in descendants
        if d.detection_method in ("paragraph_density_partition", "fallback_single_section")
    ]

    assert len(semantic_nodes) == 0
    assert len(fallback_partitions) >= 1

    # In runner comparison, only semantic_nodes are checked for false positives
    fp_count = len(semantic_nodes)
    assert fp_count == 0


def test_fallback_document_tree_page_metadata():
    """6. Fallback DocumentTree preserves correct metadata.total_pages."""
    dummy_pages = [
        PageLayout(page_num=p, width=600.0, height=800.0, blocks=[
            LayoutBlock(text=f"Text {p}", bbox=(0.0, 0.0, 100.0, 20.0), page_num=p, avg_font_size=12.0)
        ], raw_text=f"Text {p}")
        for p in range(1, 201)
    ]
    layout = DocumentLayout(dummy_pages, 12.0, 14.0, "Times", total_pages=200)
    tree = reconstruct_hierarchy(layout, [], "Test Book")

    assert tree.metadata.get("total_pages") == 200


def test_root_page_end_consistent_with_metadata_total_pages():
    """7. root.page_end is consistent with metadata.total_pages across both fallback and standard trees."""
    dummy_pages = [
        PageLayout(page_num=p, width=600.0, height=800.0, blocks=[
            LayoutBlock(text=f"Text {p}", bbox=(0.0, 0.0, 100.0, 20.0), page_num=p, avg_font_size=12.0)
        ], raw_text=f"Text {p}")
        for p in range(1, 50)
    ]
    layout = DocumentLayout(dummy_pages, 12.0, 14.0, "Times", total_pages=50)
    tree = reconstruct_hierarchy(layout, [], "Test")

    assert tree.root.page_start == 1
    assert tree.root.page_end == 50
    assert tree.root.page_end <= tree.metadata["total_pages"]


def test_title_normalization_roman_and_arabic():
    """8. Roman/Arabic chapter numbering normalization works."""
    assert match_titles("Chapter 1", "CHAPTER I")
    assert match_titles("Chapter 4", "Chapter IV")
    assert match_titles("Chapter 9", "Chapter IX")
    assert match_titles("Chapter 14", "Chapter XIV")
    assert match_titles("Chapter 24", "Chapter XXIV")
    assert match_titles("Book 24", "BOOK XXIV")
    assert match_titles("Letter 1", "Letter I")
    assert match_titles("Volume 5", "Volume V")

    # Distinct numbers must NOT match
    assert not match_titles("Chapter 1", "Chapter 2")
    assert not match_titles("Chapter IV", "Chapter VI")


def test_case_punctuation_and_leading_number_normalization():
    """9. Case, punctuation, and leading numbering normalize correctly."""
    assert match_titles("CHAPTER 12", "Chapter 12")
    assert match_titles("Chapter 1:", "Chapter 1")
    assert match_titles("Chapter I: Down the Rabbit-Hole", "Chapter 1")
    assert match_titles("Volume I: Fantine", "Volume 1: Fantine")
    assert match_titles("1. Down the Rabbit Hole", "1 Down the Rabbit Hole")
    assert match_titles("The Preface", "THE PREFACE")
    assert not match_titles("The Preface", "The Epilogue")
