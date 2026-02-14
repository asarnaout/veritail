"""Tests for IR metrics with hand-computed expected values."""

from __future__ import annotations

import math

import pytest

from veritail.metrics.ir import (
    attribute_match_rate_at_k,
    average_precision,
    compute_all_metrics,
    mrr,
    ndcg_at_k,
    precision_at_k,
)
from veritail.types import JudgmentRecord, QueryEntry, SearchResult


def _j(
    score: int,
    position: int,
    query: str = "test",
    attribute_verdict: str = "n/a",
) -> JudgmentRecord:
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
        attribute_verdict=attribute_verdict,
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

    def test_idcg_uses_all_judged_results(self):
        # Relevant items buried below rank k should lower NDCG@k.
        # Positions 0-1: irrelevant, positions 2-3: highly relevant.
        judgments = [_j(0, 0), _j(0, 1), _j(3, 2), _j(3, 3)]
        result = ndcg_at_k(judgments, k=2)
        # DCG@2 = (2^0-1)/log2(2) + (2^0-1)/log2(3) = 0
        # IDCG@2 uses best 2 scores from ALL 4 judged: [3, 3]
        #       = (2^3-1)/log2(2) + (2^3-1)/log2(3) = 7 + 4.416 = 11.416
        # NDCG = 0 / 11.416 = 0.0
        assert result == pytest.approx(0.0)

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


class TestAttributeMatchRate:
    def test_all_match(self):
        judgments = [
            _j(3, 0, attribute_verdict="match"),
            _j(2, 1, attribute_verdict="match"),
            _j(1, 2, attribute_verdict="match"),
        ]
        assert attribute_match_rate_at_k(judgments, k=5) == pytest.approx(1.0)

    def test_all_mismatch(self):
        judgments = [
            _j(3, 0, attribute_verdict="mismatch"),
            _j(2, 1, attribute_verdict="mismatch"),
        ]
        assert attribute_match_rate_at_k(judgments, k=5) == pytest.approx(0.0)

    def test_partial_counts_as_match(self):
        judgments = [
            _j(3, 0, attribute_verdict="match"),
            _j(2, 1, attribute_verdict="partial"),
        ]
        assert attribute_match_rate_at_k(judgments, k=5) == pytest.approx(1.0)

    def test_mixed(self):
        judgments = [
            _j(3, 0, attribute_verdict="match"),
            _j(2, 1, attribute_verdict="mismatch"),
            _j(1, 2, attribute_verdict="partial"),
            _j(0, 3, attribute_verdict="mismatch"),
        ]
        # 2 match/partial out of 4 applicable
        assert attribute_match_rate_at_k(judgments, k=5) == pytest.approx(0.5)

    def test_all_na_returns_none(self):
        judgments = [_j(3, 0), _j(2, 1)]  # default is "n/a"
        assert attribute_match_rate_at_k(judgments, k=5) is None

    def test_na_excluded_from_denominator(self):
        judgments = [
            _j(3, 0, attribute_verdict="match"),
            _j(2, 1),  # n/a
            _j(1, 2, attribute_verdict="mismatch"),
        ]
        # 1 match out of 2 applicable (n/a excluded)
        assert attribute_match_rate_at_k(judgments, k=5) == pytest.approx(0.5)

    def test_empty(self):
        assert attribute_match_rate_at_k([], k=5) is None

    def test_respects_k(self):
        judgments = [
            _j(3, 0, attribute_verdict="match"),
            _j(2, 1, attribute_verdict="match"),
            _j(1, 2, attribute_verdict="mismatch"),  # outside k=2
        ]
        assert attribute_match_rate_at_k(judgments, k=2) == pytest.approx(1.0)


class TestComputeAllMetrics:
    def test_basic(self):
        queries = [
            QueryEntry(query="shoes", type="broad"),
            QueryEntry(query="laptop", type="navigational"),
        ]
        judgments_by_query = {
            "shoes": [
                _j(3, 0, "shoes", attribute_verdict="match"),
                _j(2, 1, "shoes", attribute_verdict="mismatch"),
            ],
            "laptop": [
                _j(0, 0, "laptop", attribute_verdict="match"),
                _j(3, 1, "laptop", attribute_verdict="partial"),
            ],
        }

        results = compute_all_metrics(judgments_by_query, queries)
        metric_names = [r.metric_name for r in results]

        assert "ndcg@5" in metric_names
        assert "ndcg@10" in metric_names
        assert "mrr" in metric_names
        assert "map" in metric_names
        assert "p@5" in metric_names
        assert "p@10" in metric_names
        assert "attribute_match@5" in metric_names
        assert "attribute_match@10" in metric_names

        # Check per-query values exist
        ndcg10 = next(r for r in results if r.metric_name == "ndcg@10")
        assert "shoes" in ndcg10.per_query
        assert "laptop" in ndcg10.per_query

        # Check by-type values exist
        assert "broad" in ndcg10.by_query_type
        assert "navigational" in ndcg10.by_query_type

        # Check attribute metric values
        attr5 = next(r for r in results if r.metric_name == "attribute_match@5")
        assert "shoes" in attr5.per_query
        assert "laptop" in attr5.per_query
        # shoes: 1 match, 1 mismatch -> 0.5; laptop: 2 match/partial -> 1.0
        assert attr5.per_query["shoes"] == pytest.approx(0.5)
        assert attr5.per_query["laptop"] == pytest.approx(1.0)
        assert attr5.value == pytest.approx(0.75)  # mean of 0.5 and 1.0

    def test_duplicate_query_text_disambiguated_by_occurrence(self):
        queries = [
            QueryEntry(query="shoes"),
            QueryEntry(query="shoes"),
        ]
        judgments_by_query = {
            0: [_j(3, 0, "shoes", attribute_verdict="n/a")],
            1: [_j(0, 0, "shoes", attribute_verdict="n/a")],
        }

        results = compute_all_metrics(judgments_by_query, queries)
        ndcg10 = next(r for r in results if r.metric_name == "ndcg@10")

        assert list(ndcg10.per_query.keys()) == ["shoes [1]", "shoes [2]"]
        assert ndcg10.per_query["shoes [1]"] == pytest.approx(1.0)
        assert ndcg10.per_query["shoes [2]"] == pytest.approx(0.0)
        assert ndcg10.value == pytest.approx(0.5)
