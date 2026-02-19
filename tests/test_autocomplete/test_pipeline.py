"""Tests for autocomplete pipeline orchestrators."""

from __future__ import annotations

from veritail.autocomplete.pipeline import (
    run_autocomplete_evaluation,
    run_dual_autocomplete_evaluation,
)
from veritail.types import AutocompleteConfig, AutocompleteResponse, PrefixEntry


def _make_adapter(suggestions_map: dict[str, list[str]]):
    """Create a mock suggest adapter from a prefix->suggestions mapping."""

    def adapter(prefix: str) -> AutocompleteResponse:
        return AutocompleteResponse(suggestions=suggestions_map.get(prefix, []))

    return adapter


class TestRunAutocompleteEvaluation:
    def test_happy_path(self) -> None:
        prefixes = [
            PrefixEntry(prefix="run"),
            PrefixEntry(prefix="nik"),
        ]
        adapter = _make_adapter(
            {"run": ["running shoes", "runner"], "nik": ["nike", "nikon"]}
        )
        config = AutocompleteConfig(name="test", adapter_path="test.py")

        checks, responses = run_autocomplete_evaluation(prefixes, adapter, config)
        assert len(responses) == 2
        assert len(checks) > 0

    def test_adapter_error_resilience(self) -> None:
        prefixes = [
            PrefixEntry(prefix="run"),
        ]

        def failing_adapter(prefix: str) -> AutocompleteResponse:
            raise RuntimeError("API down")

        config = AutocompleteConfig(name="test", adapter_path="test.py")
        checks, responses = run_autocomplete_evaluation(
            prefixes, failing_adapter, config
        )
        # Should not raise, should return empty suggestions
        assert 0 in responses
        assert responses[0].suggestions == []

    def test_top_k_trimming(self) -> None:
        prefixes = [PrefixEntry(prefix="a")]
        adapter = _make_adapter({"a": ["a1", "a2", "a3", "a4", "a5", "a6"]})
        config = AutocompleteConfig(name="test", adapter_path="test.py", top_k=3)
        _, responses = run_autocomplete_evaluation(prefixes, adapter, config)
        assert len(responses[0].suggestions) == 3


class TestRunDualAutocompleteEvaluation:
    def test_dual_eval(self) -> None:
        prefixes = [
            PrefixEntry(prefix="run"),
        ]
        adapter_a = _make_adapter({"run": ["running shoes", "runner"]})
        adapter_b = _make_adapter({"run": ["run fast", "running shoes"]})
        config_a = AutocompleteConfig(name="a", adapter_path="a.py")
        config_b = AutocompleteConfig(name="b", adapter_path="b.py")

        checks_a, checks_b, comparison_checks = run_dual_autocomplete_evaluation(
            prefixes, adapter_a, config_a, adapter_b, config_b
        )
        assert len(checks_a) > 0
        assert len(checks_b) > 0
        assert len(comparison_checks) > 0

        # Should have both overlap and rank agreement checks
        check_names = {c.check_name for c in comparison_checks}
        assert "suggestion_overlap" in check_names
        assert "rank_agreement" in check_names
