"""veritail: Ecommerce search relevance evaluation tool."""

__version__ = "0.1.0"

from veritail.types import (
    CheckResult,
    CorrectionJudgment,
    ExperimentConfig,
    JudgmentRecord,
    MetricResult,
    QueryEntry,
    SearchResponse,
    SearchResult,
)

__all__ = [
    "SearchResult",
    "SearchResponse",
    "QueryEntry",
    "JudgmentRecord",
    "CheckResult",
    "CorrectionJudgment",
    "ExperimentConfig",
    "MetricResult",
]
