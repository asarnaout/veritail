"""IR metrics computation."""

from veritail.metrics.ir import (
    average_precision,
    compute_all_metrics,
    mrr,
    ndcg_at_k,
    precision_at_k,
)

__all__ = [
    "ndcg_at_k",
    "mrr",
    "average_precision",
    "precision_at_k",
    "compute_all_metrics",
]
