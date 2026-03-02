"""IR metrics computation."""

from veritail.metrics.bootstrap import (
    BootstrapCI,
    PairedBootstrapResult,
    bootstrap_ci,
    paired_bootstrap_test,
)
from veritail.metrics.ir import (
    average_precision,
    compute_all_metrics,
    mrr,
    ndcg_at_k,
    precision_at_k,
)

__all__ = [
    "BootstrapCI",
    "PairedBootstrapResult",
    "bootstrap_ci",
    "paired_bootstrap_test",
    "ndcg_at_k",
    "mrr",
    "average_precision",
    "precision_at_k",
    "compute_all_metrics",
]
