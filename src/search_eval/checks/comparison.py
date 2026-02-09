"""Cross-configuration comparison checks."""

from __future__ import annotations

from search_eval.types import CheckResult, SearchResult


def check_result_overlap(
    query: str,
    results_a: list[SearchResult],
    results_b: list[SearchResult],
) -> CheckResult:
    """Compute result set overlap (Jaccard index) between two configurations."""
    ids_a = {r.product_id for r in results_a}
    ids_b = {r.product_id for r in results_b}

    if not ids_a and not ids_b:
        return CheckResult(
            check_name="result_overlap",
            query=query,
            product_id=None,
            passed=True,
            detail="Both configurations returned zero results",
            severity="info",
        )

    intersection = ids_a & ids_b
    union = ids_a | ids_b
    jaccard = len(intersection) / len(union) if union else 0.0

    return CheckResult(
        check_name="result_overlap",
        query=query,
        product_id=None,
        passed=True,
        detail=f"Result overlap: {jaccard:.2f} ({len(intersection)}/{len(union)} shared products)",
        severity="info",
    )


def check_rank_correlation(
    query: str,
    results_a: list[SearchResult],
    results_b: list[SearchResult],
) -> CheckResult:
    """Compute Spearman rank correlation for shared products between configurations."""
    # Build position maps
    pos_a = {r.product_id: r.position for r in results_a}
    pos_b = {r.product_id: r.position for r in results_b}

    shared = set(pos_a.keys()) & set(pos_b.keys())

    if len(shared) < 2:
        return CheckResult(
            check_name="rank_correlation",
            query=query,
            product_id=None,
            passed=True,
            detail=f"Too few shared products ({len(shared)}) for rank correlation",
            severity="info",
        )

    # Spearman rank correlation
    n = len(shared)
    d_squared_sum = sum(
        (pos_a[pid] - pos_b[pid]) ** 2 for pid in shared
    )
    rho = 1 - (6 * d_squared_sum) / (n * (n ** 2 - 1))

    return CheckResult(
        check_name="rank_correlation",
        query=query,
        product_id=None,
        passed=True,
        detail=f"Spearman rank correlation: {rho:.3f} ({n} shared products)",
        severity="info",
    )


def find_position_shifts(
    query: str,
    results_a: list[SearchResult],
    results_b: list[SearchResult],
    min_shift: int = 3,
) -> list[CheckResult]:
    """Find products with the largest position changes between configurations."""
    pos_a = {r.product_id: r.position for r in results_a}
    pos_b = {r.product_id: r.position for r in results_b}

    shared = set(pos_a.keys()) & set(pos_b.keys())

    shifts: list[CheckResult] = []
    for pid in shared:
        shift = pos_b[pid] - pos_a[pid]
        if abs(shift) >= min_shift:
            direction = "dropped" if shift > 0 else "rose"
            # Find the title from either result set
            title = next(
                (r.title for r in results_a if r.product_id == pid),
                pid,
            )
            shifts.append(
                CheckResult(
                    check_name="position_shift",
                    query=query,
                    product_id=pid,
                    passed=True,
                    detail=(
                        f"'{title}' {direction} {abs(shift)} positions "
                        f"(#{pos_a[pid] + 1} -> #{pos_b[pid] + 1})"
                    ),
                    severity="info",
                )
            )

    # Sort by magnitude of shift, largest first
    shifts.sort(key=lambda c: abs(int(c.detail.split(" positions")[0].split()[-1])), reverse=True)
    return shifts
