"""Tests for query-level deterministic checks."""

from search_eval.checks.query_level import check_result_count, check_zero_results
from search_eval.types import SearchResult


def _make_result(product_id: str = "SKU-001") -> SearchResult:
    return SearchResult(
        product_id=product_id,
        title="Test Product",
        description="Test",
        category="Test",
        price=9.99,
        position=0,
    )


def test_zero_results_with_empty_list():
    result = check_zero_results("running shoes", [])
    assert not result.passed
    assert result.severity == "fail"
    assert result.check_name == "zero_results"


def test_zero_results_with_results():
    result = check_zero_results("running shoes", [_make_result()])
    assert result.passed
    assert result.severity == "info"


def test_result_count_zero():
    result = check_result_count("running shoes", [])
    assert not result.passed
    assert result.severity == "fail"


def test_result_count_below_minimum():
    result = check_result_count("running shoes", [_make_result()], min_expected=3)
    assert not result.passed
    assert result.severity == "warning"


def test_result_count_meets_minimum():
    results = [_make_result(f"SKU-{i}") for i in range(5)]
    result = check_result_count("running shoes", results, min_expected=3)
    assert result.passed
    assert result.severity == "info"
