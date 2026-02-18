"""Cross-configuration autocomplete comparison checks."""

from __future__ import annotations

from veritail.types import CheckResult


def check_suggestion_overlap(
    prefix: str,
    suggestions_a: list[str],
    suggestions_b: list[str],
) -> CheckResult:
    """Compute suggestion overlap (Jaccard index) between two configurations."""
    set_a = {s.lower().strip() for s in suggestions_a}
    set_b = {s.lower().strip() for s in suggestions_b}

    if not set_a and not set_b:
        return CheckResult(
            check_name="suggestion_overlap",
            query=prefix,
            product_id=None,
            passed=True,
            detail="Both configurations returned zero suggestions",
            severity="info",
        )

    intersection = set_a & set_b
    union = set_a | set_b
    jaccard = len(intersection) / len(union) if union else 0.0

    return CheckResult(
        check_name="suggestion_overlap",
        query=prefix,
        product_id=None,
        passed=True,
        detail=(
            f"Suggestion overlap: {jaccard:.2f} "
            f"({len(intersection)}/{len(union)} shared suggestions)"
        ),
        severity="info",
    )


def check_rank_agreement(
    prefix: str,
    suggestions_a: list[str],
    suggestions_b: list[str],
) -> CheckResult:
    """Compute Spearman rank correlation for shared suggestions."""
    rank_a = {s.lower().strip(): i for i, s in enumerate(suggestions_a)}
    rank_b = {s.lower().strip(): i for i, s in enumerate(suggestions_b)}

    shared = set(rank_a.keys()) & set(rank_b.keys())

    if len(shared) < 2:
        return CheckResult(
            check_name="rank_agreement",
            query=prefix,
            product_id=None,
            passed=True,
            detail=f"Too few shared suggestions ({len(shared)}) for rank correlation",
            severity="info",
        )

    n = len(shared)
    d_squared_sum = sum((rank_a[s] - rank_b[s]) ** 2 for s in shared)
    rho = 1 - (6 * d_squared_sum) / (n * (n**2 - 1))

    return CheckResult(
        check_name="rank_agreement",
        query=prefix,
        product_id=None,
        passed=True,
        detail=f"Spearman rank correlation: {rho:.3f} ({n} shared suggestions)",
        severity="info",
    )
