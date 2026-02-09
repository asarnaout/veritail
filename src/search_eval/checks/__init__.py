"""Deterministic search quality checks."""

from __future__ import annotations

from search_eval.checks.query_level import check_result_count, check_zero_results
from search_eval.checks.result_level import (
    check_attribute_match,
    check_category_alignment,
    check_duplicates,
    check_price_outliers,
    check_text_overlap,
)
from search_eval.types import CheckResult, QueryEntry, SearchResult


def run_all_checks(
    query: QueryEntry,
    results: list[SearchResult],
) -> list[CheckResult]:
    """Run all applicable deterministic checks for a query and its results."""
    checks: list[CheckResult] = []

    # Query-level checks
    checks.append(check_zero_results(query.query, results))
    checks.append(check_result_count(query.query, results))

    # Result-level checks (only if we have results)
    if results:
        checks.extend(check_category_alignment(query, results))
        checks.extend(check_attribute_match(query.query, results))
        checks.extend(check_text_overlap(query.query, results))
        checks.extend(check_price_outliers(query.query, results))
        checks.extend(check_duplicates(query.query, results))

    return checks


__all__ = [
    "check_zero_results",
    "check_result_count",
    "check_category_alignment",
    "check_attribute_match",
    "check_text_overlap",
    "check_price_outliers",
    "check_duplicates",
    "run_all_checks",
]
