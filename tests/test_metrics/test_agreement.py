"""Tests for Cohen's kappa and agreement computation."""

from __future__ import annotations

import pytest

from search_eval.metrics.agreement import cohens_kappa, compute_agreement
from search_eval.types import HumanScore, JudgmentRecord, SearchResult


def _j(query: str, product_id: str, score: int) -> JudgmentRecord:
    return JudgmentRecord(
        query=query,
        product=SearchResult(
            product_id=product_id,
            title="Product",
            description="",
            category="Test",
            price=10.0,
            position=0,
        ),
        score=score,
        reasoning="",
        model="test",
        experiment="test",
    )


class TestCohensKappa:
    def test_perfect_agreement(self):
        a = [0, 1, 2, 3, 0, 1, 2, 3]
        b = [0, 1, 2, 3, 0, 1, 2, 3]
        assert cohens_kappa(a, b) == pytest.approx(1.0)

    def test_complete_disagreement(self):
        # When raters never agree, kappa <= 0
        # With constant values per rater (all 0 vs all 3), p_e = 0, p_o = 0 -> kappa = 0
        a = [0, 0, 0, 0]
        b = [3, 3, 3, 3]
        kappa = cohens_kappa(a, b)
        assert kappa <= 0

    def test_systematic_disagreement(self):
        # Ratings that actively disagree more than chance
        a = [0, 1, 2, 3, 0, 1, 2, 3]
        b = [3, 2, 1, 0, 3, 2, 1, 0]
        kappa = cohens_kappa(a, b)
        assert kappa < 0  # Negative kappa = worse than chance

    def test_chance_agreement(self):
        # When ratings are distributed uniformly and independently,
        # kappa should be near 0
        a = [0, 1, 2, 3] * 25
        b = [1, 2, 3, 0] * 25  # Systematic shift
        kappa = cohens_kappa(a, b)
        assert -0.5 < kappa < 0.5

    def test_empty_lists(self):
        assert cohens_kappa([], []) == 0.0

    def test_mismatched_lengths(self):
        with pytest.raises(ValueError, match="same length"):
            cohens_kappa([1, 2], [1])

    def test_all_same_category(self):
        # Both raters always say 2
        a = [2, 2, 2, 2]
        b = [2, 2, 2, 2]
        assert cohens_kappa(a, b) == pytest.approx(1.0)


class TestComputeAgreement:
    def test_perfect_agreement(self):
        judgments = [
            _j("shoes", "SKU-1", 3),
            _j("shoes", "SKU-2", 1),
            _j("laptop", "SKU-3", 2),
        ]
        human_scores = [
            HumanScore(query="shoes", product_id="SKU-1", score=3, experiment="test"),
            HumanScore(query="shoes", product_id="SKU-2", score=1, experiment="test"),
            HumanScore(query="laptop", product_id="SKU-3", score=2, experiment="test"),
        ]

        result = compute_agreement(judgments, human_scores)
        assert result["kappa"] == pytest.approx(1.0)
        assert result["n_matched"] == 3
        assert result["agreement_rate"] == pytest.approx(1.0)
        assert "trustworthy" in result["calibration"]

    def test_no_matches(self):
        judgments = [_j("shoes", "SKU-1", 3)]
        human_scores = [
            HumanScore(query="laptop", product_id="SKU-99", score=2, experiment="test"),
        ]

        result = compute_agreement(judgments, human_scores)
        assert result["n_matched"] == 0
        assert result["kappa"] == 0.0

    def test_partial_agreement(self):
        judgments = [
            _j("shoes", "SKU-1", 3),
            _j("shoes", "SKU-2", 2),
            _j("laptop", "SKU-3", 0),
            _j("laptop", "SKU-4", 1),
        ]
        human_scores = [
            HumanScore(query="shoes", product_id="SKU-1", score=3, experiment="test"),
            HumanScore(query="shoes", product_id="SKU-2", score=0, experiment="test"),
            HumanScore(query="laptop", product_id="SKU-3", score=0, experiment="test"),
            HumanScore(query="laptop", product_id="SKU-4", score=3, experiment="test"),
        ]

        result = compute_agreement(judgments, human_scores)
        assert result["n_matched"] == 4
        assert 0 < result["agreement_rate"] < 1.0

    def test_calibration_thresholds(self):
        # Low kappa -> unreliable
        judgments = [_j("q1", "p1", 0), _j("q2", "p2", 0)]
        human = [
            HumanScore(query="q1", product_id="p1", score=3, experiment="t"),
            HumanScore(query="q2", product_id="p2", score=3, experiment="t"),
        ]
        result = compute_agreement(judgments, human)
        assert "unreliable" in result["calibration"]
