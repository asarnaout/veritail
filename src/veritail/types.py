"""Core data types used throughout veritail."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class SearchResult:
    """Standardized search result returned by developer-provided adapters."""

    product_id: str
    title: str
    description: str
    category: str
    price: float
    position: int
    attributes: dict[str, Any] = field(default_factory=dict)
    in_stock: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class SearchResponse:
    """Wrapper returned by search adapters."""

    results: list[SearchResult]
    corrected_query: str | None = None


@dataclass
class CorrectionJudgment:
    """LLM verdict on whether a query correction was appropriate."""

    original_query: str
    corrected_query: str
    verdict: str  # "appropriate" | "inappropriate"
    reasoning: str
    model: str
    experiment: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class QueryEntry:
    """A query from the input query set (CSV or JSON)."""

    query: str
    type: str | None = None  # navigational | broad | long_tail | attribute
    category: str | None = None  # expected product category


@dataclass
class JudgmentRecord:
    """LLM relevance judgment for one query-result pair."""

    query: str
    product: SearchResult
    score: int  # 0-3 relevance scale
    reasoning: str  # brief LLM justification
    model: str  # e.g. "claude-sonnet-4-5"
    experiment: str  # config name
    attribute_verdict: str = "n/a"  # match | partial | mismatch | n/a
    query_type: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class CheckResult:
    """Result of one deterministic quality check."""

    check_name: str  # e.g. "category_alignment"
    query: str
    product_id: str | None  # None for query-level checks
    passed: bool
    detail: str  # human-readable explanation
    severity: str = "warning"  # "info" | "warning" | "fail"


@dataclass
class ExperimentConfig:
    """Configuration for one evaluation run."""

    name: str
    adapter_path: str
    llm_model: str
    rubric: str
    top_k: int = 10


@dataclass
class MetricResult:
    """Computed IR metric value."""

    metric_name: str  # e.g. "ndcg@10"
    value: float
    per_query: dict[str, float] = field(default_factory=dict)
    by_query_type: dict[str, float] = field(default_factory=dict)
    query_count: int | None = None  # queries that contributed to the aggregate
    total_queries: int | None = None  # total queries in the evaluation
