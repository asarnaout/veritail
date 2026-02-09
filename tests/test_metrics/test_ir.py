"""Tests for IR metrics with hand-computed expected values."""

from __future__ import annotations

import math

import pytest

from search_eval.metrics.ir import (
    average_precision,
    compute_all_metrics,
    mrr,
    ndcg_at_k,
    precision_at_k,
)
from search_eval.types import JudgmentRecord, QueryEntry, SearchResult


def _j(score: int, position: int, query: str = "test") -> JudgmentRecord:
    """Helper to create a judgment with just a score and position."""
    return JudgmentRecord(
        query=query,
        product=SearchResult(
            product_id=f"SKU-{position}",
            title=f"Product {position}",
            description="",
            category="Test",
            price=10.0,
            position=position,
        ),
        score=score,
        reasoning="",
        model="test",
        experiment="test",
    )


class TestNDCG:
    def test_perfect_ranking(self):
        # Scores: [3, 2, 1, 0] — already in ideal order
        judgments = [_j(3, 0), _j(2, 1), _j(1, 2), _j(0, 3)]
        assert ndcg_at_k(judgments, k=4) == pytest.approx(1.0)

    def test_reversed_ranking(self):
        # Scores: [0, 1, 2, 3] — worst order
        judgments = [_j(0, 0), _j(1, 1), _j(2, 2), _j(3, 3)]
        result = ndcg_at_k(judgments, k=4)
        assert 0.0 < result < 1.0

    def test_all_zero_scores(self):
        judgments = [_j(0, 0), _j(0, 1), _j(0, 2)]
        assert ndcg_at_k(judgments, k=3) == 0.0

    def test_empty(self):
        assert ndcg_at_k([], k=5) == 0.0

    def test_k_larger_than_results(self):
        judgments = [_j(3, 0), _j(2, 1)]
        result = ndcg_at_k(judgments, k=10)
        assert result == pytest.approx(1.0)  # Still perfect if ideal

    def test_specific_value(self):
        # Position 0: score=3, Position 1: score=0, Position 2: score=2
        judgments = [_j(3, 0), _j(0, 1), _j(2, 2)]
        # DCG = (2^3-1)/log2(2) + (2^0-1)/log2(3) + (2^2-1)/log2(4)
        #     = 7/1 + 0/1.585 + 3/2 = 7 + 0 + 1.5 = 8.5
        # Ideal order: [3, 2, 0]
        # IDCG = 7/1 + 3/1.585 + 0/2 = 7 + 1.893 + 0 = 8.893
        expected_dcg = 7.0 + 0.0 + 3.0 / 2.0
        expected_idcg = 7.0 + 3.0 / math.log2(3) + 0.0
        expected = expected_dcg / expected_idcg
        assert ndcg_at_k(judgments, k=3) == pytest.approx(expected, rel=1e-4)


class TestMRR:
    def test_first_result_relevant(self):
        judgments = [_j(3, 0), _j(0, 1), _j(0, 2)]
        assert mrr(judgments) == pytest.approx(1.0)

    def test_second_result_relevant(self):
        judgments = [_j(0, 0), _j(3, 1), _j(0, 2)]
        assert mrr(judgments) == pytest.approx(0.5)

    def test_no_relevant_results(self):
        judgments = [_j(0, 0), _j(1, 1), _j(0, 2)]  # threshold=2
        assert mrr(judgments) == 0.0

    def test_empty(self):
        assert mrr([]) == 0.0

    def test_custom_threshold(self):
        judgments = [_j(0, 0), _j(1, 1), _j(2, 2)]
        assert mrr(judgments, relevance_threshold=1) == pytest.approx(0.5)


class TestAveragePrecision:
    def test_all_relevant(self):
        judgments = [_j(3, 0), _j(2, 1), _j(3, 2)]
        # AP = (1/1 + 2/2 + 3/3) / 3 = 1.0
        assert average_precision(judgments) == pytest.approx(1.0)

    def test_interleaved(self):
        # Relevant at positions 0, 2 (threshold=2)
        judgments = [_j(3, 0), _j(0, 1), _j(2, 2)]
        # P@1 when first relevant found = 1/1
        # P@3 when second relevant found = 2/3
        # AP = (1 + 2/3) / 2 = 5/6
        assert average_precision(judgments) == pytest.approx(5.0 / 6.0, rel=1e-4)

    def test_no_relevant(self):
        judgments = [_j(0, 0), _j(1, 1), _j(0, 2)]
        assert average_precision(judgments) == 0.0

    def test_empty(self):
        assert average_precision([]) == 0.0


class TestPrecisionAtK:
    def test_all_relevant(self):
        judgments = [_j(3, 0), _j(2, 1), _j(3, 2)]
        assert precision_at_k(judgments, k=3) == pytest.approx(1.0)

    def test_half_relevant(self):
        judgments = [_j(3, 0), _j(0, 1), _j(2, 2), _j(0, 3)]
        assert precision_at_k(judgments, k=4) == pytest.approx(0.5)

    def test_none_relevant(self):
        judgments = [_j(0, 0), _j(1, 1)]
        assert precision_at_k(judgments, k=2) == 0.0

    def test_k_smaller_than_results(self):
        judgments = [_j(3, 0), _j(0, 1), _j(0, 2)]
        assert precision_at_k(judgments, k=1) == pytest.approx(1.0)

    def test_empty(self):
        assert precision_at_k([], k=5) == 0.0


class TestComputeAllMetrics:
    def test_basic(self):
        queries = [
            QueryEntry(query="shoes", type="broad"),
            QueryEntry(query="laptop", type="navigational"),
        ]
        judgments_by_query = {
            "shoes": [_j(3, 0, "shoes"), _j(2, 1, "shoes")],
            "laptop": [_j(0, 0, "laptop"), _j(3, 1, "laptop")],
        }

        results = compute_all_metrics(judgments_by_query, queries)
        metric_names = [r.metric_name for r in results]

        assert "ndcg@5" in metric_names
        assert "ndcg@10" in metric_names
        assert "mrr" in metric_names
        assert "map" in metric_names
        assert "p@5" in metric_names
        assert "p@10" in metric_names

        # Check per-query values exist
        ndcg10 = next(r for r in results if r.metric_name == "ndcg@10")
        assert "shoes" in ndcg10.per_query
        assert "laptop" in ndcg10.per_query

        # Check by-type values exist
        assert "broad" in ndcg10.by_query_type
        assert "navigational" in ndcg10.by_query_type
