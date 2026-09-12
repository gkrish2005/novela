"""
Unit and Adversarial Regression Tests for Benchmark Matcher Engine.
Verifies strict type compatibility, page locality, and hierarchy collision resistance.
"""

import pytest
import sys
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "scripts"))

from evaluate_authoritative_benchmark import (
    strict_match_nodes,
    is_type_compatible,
    extract_structural_numeral,
    evaluate_genuine_hierarchy,
    StrictMatchResult
)


def test_book_vi_vs_chapter_vi_collision_prevention():
    """Adversarial Test: Book VI must NOT match Chapter VI."""
    gt_nodes = [
        {
            "node_id": "lm_bk_6",
            "title": "Book VI: Javert",
            "type": "book",
            "level": 2,
            "page_start": 191
        }
    ]
    # Parser emits Chapter vi at page 8
    pred_nodes = [
        {
            "id": "pred_ch_6",
            "title": "Chapter vi",
            "node_type": "chapter",
            "level": 3,
            "page_start": 8
        }
    ]

    matches, fp, fn, out_of_scope = strict_match_nodes(
        scored_gt_nodes=gt_nodes,
        semantic_pred_nodes=pred_nodes,
        deferred_levels=set(),
        max_page_window=15
    )

    # Must NOT match
    assert len(matches) == 0, "Book VI incorrectly matched Chapter VI!"
    assert len(fp) == 1
    assert len(fn) == 1


def test_volume_i_vs_book_i_collision_prevention():
    """Adversarial Test: Volume I must NOT match Book I."""
    gt_nodes = [
        {
            "node_id": "vol_1",
            "title": "Volume I: Fantine",
            "type": "volume",
            "level": 1,
            "page_start": 20
        }
    ]
    pred_nodes = [
        {
            "id": "pred_bk_1",
            "title": "Book I: An Upright Man",
            "node_type": "book",
            "level": 2,
            "page_start": 20
        }
    ]

    matches, fp, fn, out_of_scope = strict_match_nodes(
        scored_gt_nodes=gt_nodes,
        semantic_pred_nodes=pred_nodes,
        deferred_levels=set(),
        max_page_window=15
    )

    assert len(matches) == 0, "Volume I incorrectly matched Book I!"


def test_chapter_i_vs_letter_i_collision_prevention():
    """Adversarial Test: Chapter I must NOT match Letter I."""
    gt_nodes = [
        {
            "node_id": "letter_1",
            "title": "Letter I",
            "type": "letter",
            "level": 1,
            "page_start": 15
        }
    ]
    pred_nodes = [
        {
            "id": "pred_ch_1",
            "title": "Chapter I",
            "node_type": "chapter",
            "level": 1,
            "page_start": 38
        }
    ]

    matches, fp, fn, out_of_scope = strict_match_nodes(
        scored_gt_nodes=gt_nodes,
        semantic_pred_nodes=pred_nodes,
        deferred_levels=set(),
        max_page_window=15
    )

    assert len(matches) == 0, "Letter I incorrectly matched Chapter I!"


def test_page_locality_window_prevents_distant_collisions():
    """Adversarial Test: Chapter 1 on page 10 must NOT match Chapter 1 on page 300."""
    gt_nodes = [
        {
            "node_id": "ch_1",
            "title": "Chapter 1",
            "type": "chapter",
            "level": 1,
            "page_start": 10
        }
    ]
    pred_nodes = [
        {
            "id": "pred_ch_1",
            "title": "Chapter 1",
            "node_type": "chapter",
            "level": 1,
            "page_start": 300
        }
    ]

    matches, fp, fn, out_of_scope = strict_match_nodes(
        scored_gt_nodes=gt_nodes,
        semantic_pred_nodes=pred_nodes,
        deferred_levels=set(),
        max_page_window=15
    )

    assert len(matches) == 0, "Distant page collision occurred!"


def test_deferred_level_filtering_to_out_of_scope():
    """Verifies that deferred levels are routed to out_of_scope rather than FP."""
    gt_nodes = [
        {
            "node_id": "bk_1",
            "title": "Book I",
            "type": "book",
            "level": 1,
            "page_start": 20
        }
    ]
    pred_nodes = [
        {
            "id": "pred_ch_1",
            "title": "Chapter I",
            "node_type": "chapter",
            "level": 2,
            "page_start": 25
        }
    ]

    matches, fp, fn, out_of_scope = strict_match_nodes(
        scored_gt_nodes=gt_nodes,
        semantic_pred_nodes=pred_nodes,
        deferred_levels={"chapter"},
        max_page_window=15
    )

    assert len(matches) == 0
    assert len(out_of_scope) == 1
    assert len(fp) == 0
    assert len(fn) == 1
