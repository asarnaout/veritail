"""Result-level deterministic checks."""

from __future__ import annotations

import re
from collections import Counter
from difflib import SequenceMatcher
from statistics import median

from veritail.types import CheckResult, QueryEntry, SearchResult


def _tokenize(text: str) -> set[str]:
    """Lowercase and split text into word tokens."""
    return set(re.findall(r"\w+", text.lower()))


def check_category_alignment(
    query: QueryEntry,
    results: list[SearchResult],
) -> list[CheckResult]:
    """Check if results are in a consistent or expected category.

    If the query has an expected category, checks each result against it.
    Otherwise, checks each result against the majority category in the result set.
    """
    checks: list[CheckResult] = []

    if query.category:
        # Check against expected category
        expected = query.category.lower()
        for result in results:
            result_cat = result.category.lower()
            # Check if the result category contains or matches the expected category
            aligned = expected in result_cat or result_cat in expected
            checks.append(
                CheckResult(
                    check_name="category_alignment",
                    query=query.query,
                    product_id=result.product_id,
                    passed=aligned,
                    detail=(
                        f"Category '{result.category}' matches expected '{query.category}'"
                        if aligned
                        else f"Category '{result.category}' does not match expected '{query.category}'"
                    ),
                    severity="info" if aligned else "warning",
                )
            )
    else:
        # Check against majority category
        categories = [r.category for r in results]
        if not categories:
            return checks

        # Find the most common top-level category
        top_level = [c.split(">")[0].strip().lower() for c in categories]
        majority_cat = Counter(top_level).most_common(1)[0][0]

        for result in results:
            result_top = result.category.split(">")[0].strip().lower()
            aligned = result_top == majority_cat
            checks.append(
                CheckResult(
                    check_name="category_alignment",
                    query=query.query,
                    product_id=result.product_id,
                    passed=aligned,
                    detail=(
                        f"Category '{result.category}' matches majority category"
                        if aligned
                        else f"Category '{result.category}' differs from majority category"
                    ),
                    severity="info" if aligned else "warning",
                )
            )

    return checks


# Common attribute keywords that map to structured fields
_ATTRIBUTE_KEYWORDS = {
    "color": [
        "red", "blue", "green", "black", "white", "yellow", "orange", "purple",
        "pink", "brown", "grey", "gray", "navy", "beige", "gold", "silver",
    ],
    "brand": [],  # brands are dynamic, matched via attributes dict
}


def check_attribute_match(
    query: str,
    results: list[SearchResult],
) -> list[CheckResult]:
    """Check if results match attributes specified in the query.

    Extracts color and other attribute tokens from the query string and
    checks them against each result's structured attribute fields.
    """
    checks: list[CheckResult] = []
    query_lower = query.lower()
    query_tokens = _tokenize(query)

    # Check color mentions in query
    mentioned_colors = [c for c in _ATTRIBUTE_KEYWORDS["color"] if c in query_tokens]

    if not mentioned_colors:
        return checks

    for result in results:
        result_attrs = {k.lower(): str(v).lower() for k, v in result.attributes.items()}
        result_color = result_attrs.get("color", "")

        for color in mentioned_colors:
            matched = color in result_color
            checks.append(
                CheckResult(
                    check_name="attribute_match",
                    query=query,
                    product_id=result.product_id,
                    passed=matched,
                    detail=(
                        f"Result has color '{result_color}' matching query color '{color}'"
                        if matched
                        else f"Result has color '{result_color}', query specifies '{color}'"
                    ),
                    severity="info" if matched else "warning",
                )
            )

    return checks


def _jaccard(tokens_a: set[str], tokens_b: set[str]) -> float:
    """Compute Jaccard similarity between two token sets."""
    if not tokens_a or not tokens_b:
        return 0.0
    return len(tokens_a & tokens_b) / len(tokens_a | tokens_b)


def check_text_overlap(
    query: str,
    results: list[SearchResult],
    min_overlap: float = 0.1,
) -> list[CheckResult]:
    """Check if results have meaningful text overlap with the query.

    Computes Jaccard similarity between query tokens and each of the result's
    text fields (title, category, description).  The best score across fields
    is used so that a match in *any* field is sufficient.  Empty fields are
    ignored and never penalize the score.
    """
    checks: list[CheckResult] = []
    query_tokens = _tokenize(query)

    if not query_tokens:
        return checks

    for result in results:
        fields = {
            "title": _tokenize(result.title),
            "category": _tokenize(result.category),
            "description": _tokenize(result.description),
        }

        best_score = 0.0
        best_field = "title"
        best_tokens: set[str] = set()

        for name, tokens in fields.items():
            score = _jaccard(query_tokens, tokens)
            if score > best_score:
                best_score = score
                best_field = name
                best_tokens = query_tokens & tokens

        passed = best_score >= min_overlap
        checks.append(
            CheckResult(
                check_name="text_overlap",
                query=query,
                product_id=result.product_id,
                passed=passed,
                detail=(
                    f"Best overlap: {best_score:.2f} on {best_field} (tokens: {best_tokens})"
                    if passed
                    else f"Low overlap across all fields (best: {best_score:.2f} on {best_field})"
                ),
                severity="info" if passed else "warning",
            )
        )

    return checks


def check_price_outliers(
    query: str,
    results: list[SearchResult],
    iqr_multiplier: float = 1.5,
) -> list[CheckResult]:
    """Flag results with prices far outside the result set norm.

    Uses IQR method: outliers are prices below Q1 - 1.5*IQR or above Q3 + 1.5*IQR.
    """
    checks: list[CheckResult] = []

    prices = [r.price for r in results]
    if len(prices) < 3:
        return checks

    sorted_prices = sorted(prices)
    n = len(sorted_prices)
    q1 = sorted_prices[n // 4]
    q3 = sorted_prices[(3 * n) // 4]
    iqr = q3 - q1

    lower_bound = q1 - iqr_multiplier * iqr
    upper_bound = q3 + iqr_multiplier * iqr

    for result in results:
        is_outlier = result.price < lower_bound or result.price > upper_bound
        checks.append(
            CheckResult(
                check_name="price_outlier",
                query=query,
                product_id=result.product_id,
                passed=not is_outlier,
                detail=(
                    f"Price ${result.price:.2f} is within normal range (${lower_bound:.2f}-${upper_bound:.2f})"
                    if not is_outlier
                    else f"Price ${result.price:.2f} is an outlier (normal range: ${lower_bound:.2f}-${upper_bound:.2f})"
                ),
                severity="info" if not is_outlier else "warning",
            )
        )

    return checks


def check_duplicates(
    query: str,
    results: list[SearchResult],
    similarity_threshold: float = 0.85,
) -> list[CheckResult]:
    """Detect near-duplicate products in results based on title similarity."""
    checks: list[CheckResult] = []

    for i in range(len(results)):
        for j in range(i + 1, len(results)):
            similarity = SequenceMatcher(
                None,
                results[i].title.lower(),
                results[j].title.lower(),
            ).ratio()

            if similarity >= similarity_threshold:
                checks.append(
                    CheckResult(
                        check_name="duplicate",
                        query=query,
                        product_id=results[i].product_id,
                        passed=False,
                        detail=(
                            f"Near-duplicate: '{results[i].title}' and "
                            f"'{results[j].title}' (similarity: {similarity:.2f})"
                        ),
                        severity="warning",
                    )
                )

    return checks
