"""Result-level deterministic checks."""

from __future__ import annotations

import re
from difflib import SequenceMatcher

from veritail.types import CheckResult, SearchResult


def _tokenize(text: str) -> set[str]:
    """Lowercase and split text into word tokens."""
    return set(re.findall(r"\w+", text.lower()))


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
                    f"Best overlap: {best_score:.2f} "
                    f"on {best_field} (tokens: {best_tokens})"
                    if passed
                    else (
                        f"Low overlap across all fields "
                        f"(best: {best_score:.2f} on {best_field})"
                    )
                ),
                severity="info" if passed else "warning",
            )
        )

    return checks


def _interpolated_percentile(sorted_data: list[float], percentile: float) -> float:
    """Compute percentile using linear interpolation (numpy-style)."""
    n = len(sorted_data)
    pos = percentile * (n - 1)
    lo = int(pos)
    hi = min(lo + 1, n - 1)
    frac = pos - lo
    return sorted_data[lo] + frac * (sorted_data[hi] - sorted_data[lo])


def _mad_outlier_bounds(
    sorted_prices: list[float], threshold: float = 3.0
) -> tuple[float, float]:
    """Compute outlier bounds using Modified Z-Score (MAD-based).

    When MAD = 0 (more than half the values are identical), falls back to
    relative bounds: prices beyond ``threshold`` times the median are flagged.
    Mean absolute deviation cannot be used here because the outlier itself
    contaminates the measure at small n, producing false positives.
    """
    n = len(sorted_prices)
    median = (
        sorted_prices[n // 2]
        if n % 2
        else (sorted_prices[n // 2 - 1] + sorted_prices[n // 2]) / 2
    )
    abs_devs = sorted([abs(p - median) for p in sorted_prices])
    mad = abs_devs[n // 2] if n % 2 else (abs_devs[n // 2 - 1] + abs_devs[n // 2]) / 2

    if mad == 0:
        # MAD=0 means more than half the values cluster at the median.
        # Use relative bounds: flag prices more than threshold× the median.
        if median == 0:
            # No meaningful price scale when the majority are $0.
            return (sorted_prices[0], sorted_prices[-1])
        return (median / threshold, median * threshold)

    # Scale MAD to be consistent with std dev for normal data
    mad_scaled = mad * 1.4826
    lower = median - threshold * mad_scaled
    upper = median + threshold * mad_scaled
    return (lower, upper)


def check_price_outliers(
    query: str,
    results: list[SearchResult],
    iqr_multiplier: float = 1.5,
) -> list[CheckResult]:
    """Flag results with prices far outside the result set norm.

    Uses Modified Z-Score (MAD) for 3-7 results and IQR method for 8+.
    """
    checks: list[CheckResult] = []

    prices = [r.price for r in results]
    if len(prices) < 3:
        return checks

    sorted_prices = sorted(prices)
    n = len(sorted_prices)

    if n < 8:
        lower_bound, upper_bound = _mad_outlier_bounds(sorted_prices)
    else:
        q1 = _interpolated_percentile(sorted_prices, 0.25)
        q3 = _interpolated_percentile(sorted_prices, 0.75)
        iqr = q3 - q1
        if iqr == 0:
            # IQR=0 means ≥50% of values are identical (Q1 == Q3).
            # Fall back to relative bounds to avoid false positives
            # from bounds collapsing to a single point.
            lower_bound, upper_bound = _mad_outlier_bounds(sorted_prices)
        else:
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
                    f"Price ${result.price:.2f} is within "
                    f"normal range "
                    f"(${lower_bound:.2f}-${upper_bound:.2f})"
                    if not is_outlier
                    else (
                        f"Price ${result.price:.2f} is an "
                        f"outlier (normal range: "
                        f"${lower_bound:.2f}-${upper_bound:.2f})"
                    )
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


def check_title_length(
    query: str,
    results: list[SearchResult],
    max_length: int = 120,
    min_length: int = 10,
) -> list[CheckResult]:
    """Flag titles that are too long or too short."""
    checks: list[CheckResult] = []

    for result in results:
        length = len(result.title)
        if length > max_length:
            checks.append(
                CheckResult(
                    check_name="title_length",
                    query=query,
                    product_id=result.product_id,
                    passed=False,
                    detail=(
                        f"Title is {length} chars "
                        f"(> {max_length} max): '{result.title}'"
                    ),
                    severity="info",
                )
            )
        elif length < min_length:
            checks.append(
                CheckResult(
                    check_name="title_length",
                    query=query,
                    product_id=result.product_id,
                    passed=False,
                    detail=(
                        f"Title is {length} chars "
                        f"(< {min_length} min): '{result.title}'"
                    ),
                    severity="info",
                )
            )
        else:
            checks.append(
                CheckResult(
                    check_name="title_length",
                    query=query,
                    product_id=result.product_id,
                    passed=True,
                    detail=f"Title length {length} chars is within normal range",
                    severity="info",
                )
            )

    return checks


def check_out_of_stock_prominence(
    query: str,
    results: list[SearchResult],
) -> list[CheckResult]:
    """Flag out-of-stock products that appear too high in ranking.

    Rules:
    - position 0 and out-of-stock -> fail severity
    - positions 1-4 and out-of-stock -> warning severity
    """
    checks: list[CheckResult] = []

    for result in results:
        if result.in_stock:
            checks.append(
                CheckResult(
                    check_name="out_of_stock_prominence",
                    query=query,
                    product_id=result.product_id,
                    passed=True,
                    detail="In stock",
                    severity="info",
                )
            )
            continue

        if result.position == 0:
            checks.append(
                CheckResult(
                    check_name="out_of_stock_prominence",
                    query=query,
                    product_id=result.product_id,
                    passed=False,
                    detail=("Out-of-stock product appears at position 1 (top result)"),
                    severity="fail",
                )
            )
        elif 1 <= result.position <= 4:
            checks.append(
                CheckResult(
                    check_name="out_of_stock_prominence",
                    query=query,
                    product_id=result.product_id,
                    passed=False,
                    detail=(
                        "Out-of-stock product appears in top 5 "
                        f"(position {result.position + 1})"
                    ),
                    severity="warning",
                )
            )
        else:
            checks.append(
                CheckResult(
                    check_name="out_of_stock_prominence",
                    query=query,
                    product_id=result.product_id,
                    passed=True,
                    detail=(
                        "Out-of-stock product appears below top 5 "
                        f"(position {result.position + 1})"
                    ),
                    severity="info",
                )
            )

    return checks
