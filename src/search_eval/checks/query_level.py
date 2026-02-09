"""Query-level deterministic checks."""

from __future__ import annotations

from search_eval.types import CheckResult, SearchResult


def check_zero_results(query: str, results: list[SearchResult]) -> CheckResult:
    """Check if a query returned zero results."""
    if not results:
        return CheckResult(
            check_name="zero_results",
            query=query,
            product_id=None,
            passed=False,
            detail=f"Query '{query}' returned zero results",
            severity="fail",
        )
    return CheckResult(
        check_name="zero_results",
        query=query,
        product_id=None,
        passed=True,
        detail=f"Query returned {len(results)} result(s)",
        severity="info",
    )


def check_result_count(
    query: str,
    results: list[SearchResult],
    min_expected: int = 3,
) -> CheckResult:
    """Check if the result count is suspiciously low."""
    count = len(results)
    if count == 0:
        return CheckResult(
            check_name="result_count",
            query=query,
            product_id=None,
            passed=False,
            detail=f"Query '{query}' returned 0 results (expected >= {min_expected})",
            severity="fail",
        )
    if count < min_expected:
        return CheckResult(
            check_name="result_count",
            query=query,
            product_id=None,
            passed=False,
            detail=f"Query '{query}' returned only {count} result(s) (expected >= {min_expected})",
            severity="warning",
        )
    return CheckResult(
        check_name="result_count",
        query=query,
        product_id=None,
        passed=True,
        detail=f"Query returned {count} results",
        severity="info",
    )
