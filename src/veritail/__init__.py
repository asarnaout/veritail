"""veritail: Ecommerce search relevance evaluation tool."""

__version__ = "0.1.0"

from veritail.types import (
    CheckResult,
    ExperimentConfig,
    HumanScore,
    JudgmentRecord,
    MetricResult,
    QueryEntry,
    SearchResult,
)

__all__ = [
    "SearchResult",
    "QueryEntry",
    "JudgmentRecord",
    "HumanScore",
    "CheckResult",
    "ExperimentConfig",
    "MetricResult",
]
