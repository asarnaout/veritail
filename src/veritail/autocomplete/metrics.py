"""Autocomplete-specific evaluation metrics."""

from __future__ import annotations

from collections import defaultdict

from veritail.types import AutocompleteResponse, MetricResult, PrefixEntry


def autocomplete_mrr(
    suggestions: list[str], target_query: str, k: int | None = None
) -> float:
    """Compute reciprocal rank of first exact match (case-insensitive).

    Returns 1/rank of the first matching suggestion, or 0.0 if not found.
    """
    target_lower = target_query.lower().strip()
    candidates = suggestions[:k] if k is not None else suggestions
    for i, s in enumerate(candidates):
        if s.lower().strip() == target_lower:
            return 1.0 / (i + 1)
    return 0.0


def success_rate_at_k(suggestions: list[str], target_query: str, k: int) -> float:
    """Return 1.0 if target appears in top-K suggestions, else 0.0."""
    target_lower = target_query.lower().strip()
    for s in suggestions[:k]:
        if s.lower().strip() == target_lower:
            return 1.0
    return 0.0


def p_saved(prefix: str, target_query: str) -> float:
    """Compute proportion of keystrokes saved.

    Formula: (len(target) - len(prefix)) / len(target), clamped to >= 0.
    """
    target_len = len(target_query)
    if target_len == 0:
        return 0.0
    return max(0.0, (target_len - len(prefix)) / target_len)


def e_saved(prefix: str, target_query: str, suggestions: list[str], k: int) -> float:
    """Compute expected keystrokes saved: pSaved * SR@K."""
    return p_saved(prefix, target_query) * success_rate_at_k(
        suggestions, target_query, k
    )


def compute_autocomplete_metrics(
    results_by_prefix: dict[int, AutocompleteResponse],
    prefixes: list[PrefixEntry],
    k_values: list[int] | None = None,
) -> list[MetricResult]:
    """Compute all autocomplete metrics across prefixes.

    Args:
        results_by_prefix: Mapping from prefix index to autocomplete response.
        prefixes: The prefix entries used in the evaluation.
        k_values: K values for SR@K and eSaved@K (default: [5, 10]).

    Returns:
        List of MetricResult with aggregate, per-prefix, and by-type breakdowns.
    """
    if k_values is None:
        k_values = [5, 10]

    metrics_config: list[tuple[str, object]] = [
        ("mrr", None),
        ("psaved", None),
    ]
    for k in k_values:
        metrics_config.append((f"sr@{k}", k))
        metrics_config.append((f"esaved@{k}", k))

    results: list[MetricResult] = []

    # MRR
    per_query: dict[str, float] = {}
    by_type: dict[str, list[float]] = defaultdict(list)
    for i, entry in enumerate(prefixes):
        resp = results_by_prefix.get(i)
        suggestions = resp.suggestions if resp else []
        value = autocomplete_mrr(suggestions, entry.target_query)
        per_query[entry.prefix] = value
        if entry.type:
            by_type[entry.type].append(value)
    all_values = list(per_query.values())
    aggregate = sum(all_values) / len(all_values) if all_values else 0.0
    by_query_type = {t: sum(v) / len(v) for t, v in by_type.items()}
    results.append(
        MetricResult(
            metric_name="mrr",
            value=aggregate,
            per_query=per_query,
            by_query_type=by_query_type,
        )
    )

    # pSaved
    per_query = {}
    by_type = defaultdict(list)
    for i, entry in enumerate(prefixes):
        value = p_saved(entry.prefix, entry.target_query)
        per_query[entry.prefix] = value
        if entry.type:
            by_type[entry.type].append(value)
    all_values = list(per_query.values())
    aggregate = sum(all_values) / len(all_values) if all_values else 0.0
    by_query_type = {t: sum(v) / len(v) for t, v in by_type.items()}
    results.append(
        MetricResult(
            metric_name="psaved",
            value=aggregate,
            per_query=per_query,
            by_query_type=by_query_type,
        )
    )

    # SR@K and eSaved@K for each k
    for k in k_values:
        # SR@K
        per_query = {}
        by_type = defaultdict(list)
        for i, entry in enumerate(prefixes):
            resp = results_by_prefix.get(i)
            suggestions = resp.suggestions if resp else []
            value = success_rate_at_k(suggestions, entry.target_query, k)
            per_query[entry.prefix] = value
            if entry.type:
                by_type[entry.type].append(value)
        all_values = list(per_query.values())
        aggregate = sum(all_values) / len(all_values) if all_values else 0.0
        by_query_type = {t: sum(v) / len(v) for t, v in by_type.items()}
        results.append(
            MetricResult(
                metric_name=f"sr@{k}",
                value=aggregate,
                per_query=per_query,
                by_query_type=by_query_type,
            )
        )

        # eSaved@K
        per_query = {}
        by_type = defaultdict(list)
        for i, entry in enumerate(prefixes):
            resp = results_by_prefix.get(i)
            suggestions = resp.suggestions if resp else []
            value = e_saved(entry.prefix, entry.target_query, suggestions, k)
            per_query[entry.prefix] = value
            if entry.type:
                by_type[entry.type].append(value)
        all_values = list(per_query.values())
        aggregate = sum(all_values) / len(all_values) if all_values else 0.0
        by_query_type = {t: sum(v) / len(v) for t, v in by_type.items()}
        results.append(
            MetricResult(
                metric_name=f"esaved@{k}",
                value=aggregate,
                per_query=per_query,
                by_query_type=by_query_type,
            )
        )

    return results
