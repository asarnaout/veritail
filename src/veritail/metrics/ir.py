"""Information retrieval metrics: NDCG@K, MRR, MAP, P@K."""

from __future__ import annotations

import math
from collections import defaultdict

from veritail.types import JudgmentRecord, MetricResult, QueryEntry


def ndcg_at_k(judgments: list[JudgmentRecord], k: int = 10) -> float:
    """Compute Normalized Discounted Cumulative Gain at K.

    Uses the graded relevance scores (0-3) from judgments.
    Judgments should be sorted by position (ascending).
    """
    if not judgments:
        return 0.0

    # Take top k
    top_k = sorted(judgments, key=lambda j: j.product.position)[:k]
    scores = [j.score for j in top_k]

    # DCG
    dcg = sum(
        (2 ** score - 1) / math.log2(i + 2)  # i+2 because log2(1) = 0
        for i, score in enumerate(scores)
    )

    # Ideal DCG (sort by score descending)
    ideal_scores = sorted(scores, reverse=True)
    idcg = sum(
        (2 ** score - 1) / math.log2(i + 2)
        for i, score in enumerate(ideal_scores)
    )

    if idcg == 0:
        return 0.0

    return dcg / idcg


def mrr(judgments: list[JudgmentRecord], relevance_threshold: int = 2) -> float:
    """Compute Mean Reciprocal Rank.

    Returns the reciprocal of the rank of the first result with
    score >= relevance_threshold.
    """
    if not judgments:
        return 0.0

    sorted_judgments = sorted(judgments, key=lambda j: j.product.position)
    for i, j in enumerate(sorted_judgments):
        if j.score >= relevance_threshold:
            return 1.0 / (i + 1)

    return 0.0


def average_precision(
    judgments: list[JudgmentRecord],
    relevance_threshold: int = 2,
) -> float:
    """Compute Average Precision for a single query.

    Used for computing MAP (Mean Average Precision) across queries.
    """
    if not judgments:
        return 0.0

    sorted_judgments = sorted(judgments, key=lambda j: j.product.position)

    relevant_count = 0
    precision_sum = 0.0

    for i, j in enumerate(sorted_judgments):
        if j.score >= relevance_threshold:
            relevant_count += 1
            precision_sum += relevant_count / (i + 1)

    if relevant_count == 0:
        return 0.0

    return precision_sum / relevant_count


def precision_at_k(
    judgments: list[JudgmentRecord],
    k: int = 5,
    relevance_threshold: int = 2,
) -> float:
    """Compute Precision at K.

    Fraction of top K results that are considered relevant
    (score >= relevance_threshold).
    """
    if not judgments:
        return 0.0

    top_k = sorted(judgments, key=lambda j: j.product.position)[:k]
    if not top_k:
        return 0.0

    relevant = sum(1 for j in top_k if j.score >= relevance_threshold)
    return relevant / len(top_k)


def compute_all_metrics(
    judgments_by_query: dict[str, list[JudgmentRecord]],
    queries: list[QueryEntry],
) -> list[MetricResult]:
    """Compute all IR metrics across all queries.

    Returns aggregate metrics, per-query breakdowns, and by-query-type breakdowns.
    """
    # Build query type lookup
    query_types: dict[str, str] = {}
    for q in queries:
        if q.type:
            query_types[q.query] = q.type

    metrics_config = [
        ("ndcg@5", lambda j: ndcg_at_k(j, k=5)),
        ("ndcg@10", lambda j: ndcg_at_k(j, k=10)),
        ("mrr", lambda j: mrr(j)),
        ("map", lambda j: average_precision(j)),
        ("p@5", lambda j: precision_at_k(j, k=5)),
        ("p@10", lambda j: precision_at_k(j, k=10)),
    ]

    results: list[MetricResult] = []

    for metric_name, metric_fn in metrics_config:
        per_query: dict[str, float] = {}
        by_type: dict[str, list[float]] = defaultdict(list)

        for query_str, query_judgments in judgments_by_query.items():
            value = metric_fn(query_judgments)
            per_query[query_str] = value

            qtype = query_types.get(query_str)
            if qtype:
                by_type[qtype].append(value)

        # Aggregate: mean across queries
        all_values = list(per_query.values())
        aggregate = sum(all_values) / len(all_values) if all_values else 0.0

        # Average by type
        by_query_type = {
            t: sum(vals) / len(vals) for t, vals in by_type.items()
        }

        results.append(
            MetricResult(
                metric_name=metric_name,
                value=aggregate,
                per_query=per_query,
                by_query_type=by_query_type,
            )
        )

    return results
