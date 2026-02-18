"""Tests for autocomplete metrics with hand-computed expected values."""

from __future__ import annotations

from veritail.autocomplete.metrics import (
    autocomplete_mrr,
    compute_autocomplete_metrics,
    e_saved,
    p_saved,
    success_rate_at_k,
)
from veritail.types import AutocompleteResponse, PrefixEntry


class TestAutocompleteMrr:
    def test_first_position(self) -> None:
        assert autocomplete_mrr(["running shoes", "run"], "running shoes") == 1.0

    def test_second_position(self) -> None:
        assert autocomplete_mrr(["run", "running shoes"], "running shoes") == 0.5

    def test_not_found(self) -> None:
        assert autocomplete_mrr(["run", "jog"], "running shoes") == 0.0

    def test_case_insensitive(self) -> None:
        assert autocomplete_mrr(["Running Shoes"], "running shoes") == 1.0

    def test_with_k(self) -> None:
        suggestions = ["a", "b", "running shoes"]
        assert autocomplete_mrr(suggestions, "running shoes", k=2) == 0.0
        assert autocomplete_mrr(suggestions, "running shoes", k=3) == 1.0 / 3

    def test_empty_suggestions(self) -> None:
        assert autocomplete_mrr([], "running shoes") == 0.0


class TestSuccessRateAtK:
    def test_found_within_k(self) -> None:
        assert success_rate_at_k(["a", "target"], "target", k=5) == 1.0

    def test_not_found_within_k(self) -> None:
        sug = ["a", "b", "c", "d", "e", "target"]
        assert success_rate_at_k(sug, "target", k=5) == 0.0

    def test_exact_at_k(self) -> None:
        suggestions = ["a", "b", "c", "d", "target"]
        assert success_rate_at_k(suggestions, "target", k=5) == 1.0

    def test_case_insensitive(self) -> None:
        assert success_rate_at_k(["TARGET"], "target", k=5) == 1.0


class TestPSaved:
    def test_basic(self) -> None:
        # "running shoes" has 13 chars, "run" has 3 chars
        # (13 - 3) / 13 = 10/13 ≈ 0.7692
        result = p_saved("run", "running shoes")
        assert abs(result - 10 / 13) < 1e-6

    def test_full_prefix(self) -> None:
        # prefix == target -> 0.0
        assert p_saved("running shoes", "running shoes") == 0.0

    def test_longer_prefix(self) -> None:
        # prefix longer than target -> clamped to 0
        assert p_saved("running shoes extended", "running") == 0.0

    def test_empty_target(self) -> None:
        assert p_saved("run", "") == 0.0

    def test_single_char(self) -> None:
        # (5 - 1) / 5 = 0.8
        assert abs(p_saved("r", "shoes") - 0.8) < 1e-6


class TestESaved:
    def test_target_found(self) -> None:
        # pSaved * SR@K = (10/13) * 1.0 = 10/13
        result = e_saved("run", "running shoes", ["running shoes"], k=5)
        assert abs(result - 10 / 13) < 1e-6

    def test_target_not_found(self) -> None:
        result = e_saved("run", "running shoes", ["other"], k=5)
        assert result == 0.0

    def test_zero_psaved(self) -> None:
        result = e_saved("running shoes", "running shoes", ["running shoes"], k=5)
        assert result == 0.0


class TestComputeAutocompleteMetrics:
    def test_basic(self) -> None:
        prefixes = [
            PrefixEntry(prefix="run", target_query="running shoes"),
            PrefixEntry(prefix="nik", target_query="nike"),
        ]
        responses = {
            0: AutocompleteResponse(suggestions=["running shoes", "runner"]),
            1: AutocompleteResponse(suggestions=["nike", "nikon"]),
        }
        metrics = compute_autocomplete_metrics(responses, prefixes, k_values=[5])
        names = {m.metric_name for m in metrics}
        assert "mrr" in names
        assert "psaved" in names
        assert "sr@5" in names
        assert "esaved@5" in names

        mrr_metric = next(m for m in metrics if m.metric_name == "mrr")
        # Both found at position 0 -> MRR = 1.0 for each
        assert mrr_metric.value == 1.0

    def test_with_types(self) -> None:
        prefixes = [
            PrefixEntry(
                prefix="run",
                target_query="running shoes",
                type="short_prefix",
            ),
            PrefixEntry(
                prefix="running sh",
                target_query="running shoes",
                type="long_prefix",
            ),
        ]
        responses = {
            0: AutocompleteResponse(suggestions=["running shoes"]),
            1: AutocompleteResponse(suggestions=["running shoes"]),
        }
        metrics = compute_autocomplete_metrics(responses, prefixes)
        mrr_metric = next(m for m in metrics if m.metric_name == "mrr")
        assert "short_prefix" in mrr_metric.by_query_type
        assert "long_prefix" in mrr_metric.by_query_type

    def test_missing_response(self) -> None:
        prefixes = [PrefixEntry(prefix="run", target_query="running shoes")]
        # No response for prefix 0
        metrics = compute_autocomplete_metrics({}, prefixes)
        mrr_metric = next(m for m in metrics if m.metric_name == "mrr")
        assert mrr_metric.value == 0.0

    def test_default_k_values(self) -> None:
        prefixes = [PrefixEntry(prefix="a", target_query="ab")]
        responses = {0: AutocompleteResponse(suggestions=["ab"])}
        metrics = compute_autocomplete_metrics(responses, prefixes)
        names = {m.metric_name for m in metrics}
        assert "sr@5" in names
        assert "sr@10" in names
        assert "esaved@5" in names
        assert "esaved@10" in names
