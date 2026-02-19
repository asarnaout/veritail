"""Tests for autocomplete pipeline orchestrators."""

from __future__ import annotations

from unittest.mock import Mock

from veritail.autocomplete.pipeline import (
    run_autocomplete_evaluation,
    run_autocomplete_llm_evaluation,
    run_dual_autocomplete_evaluation,
)
from veritail.types import (
    AutocompleteConfig,
    AutocompleteResponse,
    PrefixEntry,
    SuggestionJudgment,
)


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


class TestRunAutocompleteLlmEvaluation:
    def test_happy_path(self) -> None:
        prefixes = [
            PrefixEntry(prefix="run"),
            PrefixEntry(prefix="nik"),
        ]
        responses = {
            0: AutocompleteResponse(suggestions=["running shoes", "runner"]),
            1: AutocompleteResponse(suggestions=["nike", "nikon"]),
        }
        config = AutocompleteConfig(name="test", adapter_path="test.py")

        mock_judge = Mock()
        mock_judge.judge.return_value = SuggestionJudgment(
            prefix="run",
            suggestions=["running shoes", "runner"],
            relevance_score=3,
            diversity_score=2,
            flagged_suggestions=[],
            reasoning="Good suggestions.",
            model="test-model",
            experiment="test",
        )

        judgments = run_autocomplete_llm_evaluation(
            prefixes, responses, mock_judge, config
        )
        assert len(judgments) == 2
        assert mock_judge.judge.call_count == 2

    def test_skips_empty_suggestions(self) -> None:
        prefixes = [
            PrefixEntry(prefix="run"),
            PrefixEntry(prefix="xyz"),
        ]
        responses = {
            0: AutocompleteResponse(suggestions=["running shoes"]),
            1: AutocompleteResponse(suggestions=[]),
        }
        config = AutocompleteConfig(name="test", adapter_path="test.py")

        mock_judge = Mock()
        mock_judge.judge.return_value = SuggestionJudgment(
            prefix="run",
            suggestions=["running shoes"],
            relevance_score=3,
            diversity_score=2,
            flagged_suggestions=[],
            reasoning="Good.",
            model="test-model",
            experiment="test",
        )

        judgments = run_autocomplete_llm_evaluation(
            prefixes, responses, mock_judge, config
        )
        assert len(judgments) == 1
        assert mock_judge.judge.call_count == 1

    def test_error_resilience(self) -> None:
        prefixes = [PrefixEntry(prefix="run")]
        responses = {
            0: AutocompleteResponse(suggestions=["running shoes"]),
        }
        config = AutocompleteConfig(name="test", adapter_path="test.py")

        mock_judge = Mock()
        mock_judge.judge.side_effect = ValueError("LLM parse error")

        judgments = run_autocomplete_llm_evaluation(
            prefixes, responses, mock_judge, config
        )
        assert len(judgments) == 1
        assert judgments[0].relevance_score == 0
        assert judgments[0].diversity_score == 0
        assert "error" in judgments[0].metadata
