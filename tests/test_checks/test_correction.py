"""Tests for deterministic correction checks."""

from __future__ import annotations

from veritail.checks.correction import (
    check_correction_vocabulary,
    check_unnecessary_correction,
)
from veritail.types import SearchResult


def _make_results(titles: list[str]) -> list[SearchResult]:
    return [
        SearchResult(
            product_id=f"SKU-{i}",
            title=title,
            description=f"Description for {title}",
            category="Test",
            price=10.0,
            position=i,
        )
        for i, title in enumerate(titles)
    ]


class TestCheckCorrectionVocabulary:
    def test_new_tokens_found_in_results(self):
        results = _make_results(["Dinner Plates", "Salad Plates"])
        check = check_correction_vocabulary("plats", "plates", results)
        assert check.passed
        assert check.check_name == "correction_vocabulary"
        assert check.product_id is None

    def test_new_tokens_missing_from_results(self):
        results = _make_results(["Steam Table Pan", "Serving Tray"])
        check = check_correction_vocabulary("plats", "planes", results)
        assert not check.passed
        assert "planes" in check.detail

    def test_no_new_tokens(self):
        results = _make_results(["Running Shoes"])
        check = check_correction_vocabulary("runnign shoes", "running shoes", results)
        # "running" and "shoes" are subsets, "runnign" is removed
        # New tokens: {"running"} - {"runnign", "shoes"} = {"running"}
        # "running" appears in result title
        assert check.passed

    def test_empty_results(self):
        check = check_correction_vocabulary("plats", "plates", [])
        assert not check.passed
        assert "plates" in check.detail

    def test_correction_adds_no_tokens(self):
        # If correction only removes tokens, no new tokens to check
        results = _make_results(["Red Shoes"])
        check = check_correction_vocabulary("red running shoes", "red shoes", results)
        assert check.passed
        assert "did not introduce new tokens" in check.detail

    def test_severity_is_warning(self):
        results = _make_results(["Test"])
        check = check_correction_vocabulary("foo", "bar", results)
        assert check.severity == "warning"

    def test_partial_match(self):
        results = _make_results(["Blue Widget", "Red Gadget"])
        # "foo" -> "blue red" introduces "blue" and "red", both found
        check = check_correction_vocabulary("foo", "blue red", results)
        assert check.passed


class TestCheckUnnecessaryCorrection:
    def test_original_tokens_found_in_results(self):
        results = _make_results(["Cambro Food Pan", "Cambro Lid"])
        check = check_unnecessary_correction("cambro", "camaro", results)
        assert not check.passed
        assert "cambro" in check.detail

    def test_original_tokens_not_in_results(self):
        results = _make_results(["Running Shoes", "Trail Shoes"])
        check = check_unnecessary_correction("runnign shoes", "running shoes", results)
        # "runnign" is removed, doesn't appear in results
        assert check.passed

    def test_no_removed_tokens(self):
        results = _make_results(["Test Product"])
        # "shoes" -> "red shoes" adds "red" but removes nothing
        check = check_unnecessary_correction("shoes", "red shoes", results)
        assert check.passed
        assert "did not remove any tokens" in check.detail

    def test_empty_results(self):
        check = check_unnecessary_correction("cambro", "camaro", [])
        # removed "cambro" not found in empty results = pass
        assert check.passed

    def test_severity_is_warning(self):
        results = _make_results(["Test"])
        check = check_unnecessary_correction("foo", "bar", results)
        assert check.severity == "warning"

    def test_query_level_no_product_id(self):
        results = _make_results(["Test"])
        check = check_unnecessary_correction("foo", "bar", results)
        assert check.product_id is None
        assert check.check_name == "unnecessary_correction"
