"""Deterministic search quality checks."""

from __future__ import annotations

from collections.abc import Callable

from veritail.checks.query_level import check_result_count, check_zero_results
from veritail.checks.result_level import (
    check_category_alignment,
    check_duplicates,
    check_out_of_stock_prominence,
    check_price_outliers,
    check_text_overlap,
    check_title_length,
)
from veritail.types import CheckResult, QueryEntry, SearchResult


def run_all_checks(
    query: QueryEntry,
    results: list[SearchResult],
    custom_checks: (
        list[Callable[[QueryEntry, list[SearchResult]], list[CheckResult]]] | None
    ) = None,
) -> list[CheckResult]:
    """Run all applicable deterministic checks for a query and its results."""
    checks: list[CheckResult] = []

    # Query-level checks
    checks.append(check_zero_results(query.query, results))
    checks.append(check_result_count(query.query, results))

    # Result-level checks (only if we have results)
    if results:
        checks.extend(check_category_alignment(query, results))
        checks.extend(check_text_overlap(query.query, results))
        checks.extend(check_price_outliers(query.query, results))
        checks.extend(check_duplicates(query.query, results))
        checks.extend(check_title_length(query.query, results))
        checks.extend(check_out_of_stock_prominence(query.query, results))

    # Custom checks run outside the `if results:` gate
    if custom_checks:
        for check_fn in custom_checks:
            checks.extend(check_fn(query, results))

    return checks


__all__ = [
    "check_zero_results",
    "check_result_count",
    "check_category_alignment",
    "check_text_overlap",
    "check_price_outliers",
    "check_duplicates",
    "check_title_length",
    "check_out_of_stock_prominence",
    "run_all_checks",
    "check_correction_vocabulary",
    "check_unnecessary_correction",
]
