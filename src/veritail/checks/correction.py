"""Deterministic checks for query corrections."""

from __future__ import annotations

from veritail.checks.result_level import _tokenize
from veritail.types import CheckResult, SearchResult


def check_correction_vocabulary(
    original_query: str,
    corrected_query: str,
    results: list[SearchResult],
) -> CheckResult:
    """Check if tokens introduced by correction appear in result text.

    If the corrected query introduced new tokens that don't appear in any
    result title or description, the correction may have produced phantom
    matches.
    """
    original_tokens = _tokenize(original_query)
    corrected_tokens = _tokenize(corrected_query)
    new_tokens = corrected_tokens - original_tokens

    if not new_tokens:
        return CheckResult(
            check_name="correction_vocabulary",
            query=original_query,
            product_id=None,
            passed=True,
            detail="Correction did not introduce new tokens",
            severity="warning",
        )

    # Check if new tokens appear in any result text
    result_tokens: set[str] = set()
    for r in results:
        result_tokens |= _tokenize(r.title)
        result_tokens |= _tokenize(r.description)

    found = new_tokens & result_tokens
    missing = new_tokens - result_tokens
    passed = len(missing) == 0

    if passed:
        return CheckResult(
            check_name="correction_vocabulary",
            query=original_query,
            product_id=None,
            passed=True,
            detail=(f"Corrected tokens {sorted(found)} appear in result text"),
            severity="warning",
        )
    return CheckResult(
        check_name="correction_vocabulary",
        query=original_query,
        product_id=None,
        passed=False,
        detail=(
            f"Corrected tokens {sorted(missing)} not found in any result "
            f"title or description ('{original_query}' -> '{corrected_query}')"
        ),
        severity="warning",
    )


def check_unnecessary_correction(
    original_query: str,
    corrected_query: str,
    results: list[SearchResult],
) -> CheckResult:
    """Check if original query tokens appear in results.

    Suggests correction was unnecessary.

    If tokens that were corrected away still appear in result titles or
    descriptions, the original query may have been a valid catalog term
    and the correction was unnecessary.
    """
    original_tokens = _tokenize(original_query)
    corrected_tokens = _tokenize(corrected_query)
    removed_tokens = original_tokens - corrected_tokens

    if not removed_tokens:
        return CheckResult(
            check_name="unnecessary_correction",
            query=original_query,
            product_id=None,
            passed=True,
            detail="Correction did not remove any tokens",
            severity="warning",
        )

    # Check if removed tokens appear in result text
    result_tokens: set[str] = set()
    for r in results:
        result_tokens |= _tokenize(r.title)
        result_tokens |= _tokenize(r.description)

    found_in_results = removed_tokens & result_tokens

    if found_in_results:
        return CheckResult(
            check_name="unnecessary_correction",
            query=original_query,
            product_id=None,
            passed=False,
            detail=(
                f"Original tokens {sorted(found_in_results)} appear in results, "
                f"suggesting correction was unnecessary "
                f"('{original_query}' -> '{corrected_query}')"
            ),
            severity="warning",
        )
    return CheckResult(
        check_name="unnecessary_correction",
        query=original_query,
        product_id=None,
        passed=True,
        detail=(f"Original tokens {sorted(removed_tokens)} not found in results"),
        severity="warning",
    )
