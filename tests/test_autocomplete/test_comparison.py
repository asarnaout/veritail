"""Tests for autocomplete comparison checks."""

from __future__ import annotations

from veritail.autocomplete.comparison import (
    check_rank_agreement,
    check_suggestion_overlap,
)


class TestSuggestionOverlap:
    def test_complete_overlap(self) -> None:
        check = check_suggestion_overlap("run", ["a", "b"], ["a", "b"])
        assert "1.00" in check.detail

    def test_no_overlap(self) -> None:
        check = check_suggestion_overlap("run", ["a"], ["b"])
        assert "0.00" in check.detail

    def test_partial_overlap(self) -> None:
        check = check_suggestion_overlap("run", ["a", "b"], ["b", "c"])
        # 1 shared out of 3 unique -> ~0.33
        assert "0.33" in check.detail

    def test_both_empty(self) -> None:
        check = check_suggestion_overlap("run", [], [])
        assert check.passed
        assert "zero" in check.detail.lower()

    def test_case_insensitive(self) -> None:
        check = check_suggestion_overlap("run", ["Running"], ["running"])
        assert "1.00" in check.detail


class TestRankAgreement:
    def test_identical_ranking(self) -> None:
        check = check_rank_agreement("run", ["a", "b", "c"], ["a", "b", "c"])
        assert "1.000" in check.detail

    def test_reversed_ranking(self) -> None:
        check = check_rank_agreement("run", ["a", "b", "c"], ["c", "b", "a"])
        assert "-" in check.detail

    def test_too_few_shared(self) -> None:
        check = check_rank_agreement("run", ["a"], ["a"])
        assert "Too few" in check.detail

    def test_no_shared(self) -> None:
        check = check_rank_agreement("run", ["a"], ["b"])
        assert "Too few" in check.detail
