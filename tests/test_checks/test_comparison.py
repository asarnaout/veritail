"""Tests for cross-configuration comparison checks."""

from __future__ import annotations

from search_eval.checks.comparison import (
    check_rank_correlation,
    check_result_overlap,
    find_position_shifts,
)
from search_eval.types import SearchResult


def _make_result(product_id: str, position: int) -> SearchResult:
    return SearchResult(
        product_id=product_id,
        title=f"Product {product_id}",
        description="Test",
        category="Test",
        price=10.0,
        position=position,
    )


class TestResultOverlap:
    def test_complete_overlap(self):
        results_a = [_make_result("A", 0), _make_result("B", 1)]
        results_b = [_make_result("A", 0), _make_result("B", 1)]
        check = check_result_overlap("shoes", results_a, results_b)
        assert "1.00" in check.detail

    def test_no_overlap(self):
        results_a = [_make_result("A", 0)]
        results_b = [_make_result("B", 0)]
        check = check_result_overlap("shoes", results_a, results_b)
        assert "0.00" in check.detail

    def test_partial_overlap(self):
        results_a = [_make_result("A", 0), _make_result("B", 1)]
        results_b = [_make_result("B", 0), _make_result("C", 1)]
        check = check_result_overlap("shoes", results_a, results_b)
        # 1 shared out of 3 unique -> ~0.33
        assert "0.33" in check.detail

    def test_both_empty(self):
        check = check_result_overlap("shoes", [], [])
        assert check.passed


class TestRankCorrelation:
    def test_identical_ranking(self):
        results_a = [_make_result("A", 0), _make_result("B", 1), _make_result("C", 2)]
        results_b = [_make_result("A", 0), _make_result("B", 1), _make_result("C", 2)]
        check = check_rank_correlation("shoes", results_a, results_b)
        assert "1.000" in check.detail

    def test_reversed_ranking(self):
        results_a = [_make_result("A", 0), _make_result("B", 1), _make_result("C", 2)]
        results_b = [_make_result("A", 2), _make_result("B", 1), _make_result("C", 0)]
        check = check_rank_correlation("shoes", results_a, results_b)
        # Perfect negative correlation
        assert "-" in check.detail

    def test_too_few_shared(self):
        results_a = [_make_result("A", 0)]
        results_b = [_make_result("A", 0)]
        check = check_rank_correlation("shoes", results_a, results_b)
        assert "Too few" in check.detail


class TestPositionShifts:
    def test_large_shift_detected(self):
        results_a = [_make_result("A", 0), _make_result("B", 1)]
        results_b = [_make_result("A", 5), _make_result("B", 0)]
        shifts = find_position_shifts("shoes", results_a, results_b, min_shift=3)
        assert len(shifts) == 1
        assert "A" in shifts[0].detail
        assert "dropped" in shifts[0].detail

    def test_small_shift_ignored(self):
        results_a = [_make_result("A", 0)]
        results_b = [_make_result("A", 1)]
        shifts = find_position_shifts("shoes", results_a, results_b, min_shift=3)
        assert len(shifts) == 0

    def test_no_shared_products(self):
        results_a = [_make_result("A", 0)]
        results_b = [_make_result("B", 0)]
        shifts = find_position_shifts("shoes", results_a, results_b)
        assert len(shifts) == 0
