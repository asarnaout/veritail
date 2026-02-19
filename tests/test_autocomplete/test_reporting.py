"""Tests for autocomplete report generation."""

from __future__ import annotations

from veritail.autocomplete.reporting import (
    generate_autocomplete_comparison_report,
    generate_autocomplete_report,
)
from veritail.types import (
    AutocompleteResponse,
    CheckResult,
    PrefixEntry,
    SuggestionJudgment,
)


def _make_check(name: str, prefix: str, passed: bool) -> CheckResult:
    return CheckResult(
        check_name=name,
        query=prefix,
        product_id=None,
        passed=passed,
        detail="test detail",
        severity="info",
    )


class TestGenerateAutocompleteReport:
    def test_terminal_format(self) -> None:
        checks = [_make_check("empty_suggestions", "run", True)]
        report = generate_autocomplete_report(checks, format="terminal")
        assert "Autocomplete Evaluation Report" in report

    def test_terminal_with_prefix_details(self) -> None:
        checks = [_make_check("empty_suggestions", "run", True)]
        prefixes = [PrefixEntry(prefix="run")]
        responses = {0: AutocompleteResponse(suggestions=["running shoes"])}
        report = generate_autocomplete_report(
            checks,
            format="terminal",
            responses_by_prefix=responses,
            prefixes=prefixes,
        )
        assert "Per-Prefix" in report
        assert "running shoes" in report

    def test_html_format(self) -> None:
        checks = [_make_check("empty_suggestions", "run", True)]
        report = generate_autocomplete_report(checks, format="html")
        assert "<html" in report
        assert "Autocomplete Evaluation Report" in report

    def test_html_with_prefix_details(self) -> None:
        checks = [_make_check("empty_suggestions", "run", True)]
        prefixes = [PrefixEntry(prefix="run")]
        responses = {0: AutocompleteResponse(suggestions=["running shoes"])}
        report = generate_autocomplete_report(
            checks,
            format="html",
            responses_by_prefix=responses,
            prefixes=prefixes,
        )
        assert "Per-Prefix" in report
        assert "running shoes" in report


class TestGenerateAutocompleteComparisonReport:
    def test_terminal_format(self) -> None:
        checks_a = [_make_check("empty_suggestions", "run", True)]
        checks_b = [_make_check("empty_suggestions", "run", True)]
        comparison_checks = [
            _make_check("suggestion_overlap", "run", True),
        ]
        report = generate_autocomplete_comparison_report(
            checks_a,
            checks_b,
            comparison_checks,
            "config_a",
            "config_b",
            format="terminal",
        )
        assert "Comparison" in report
        assert "config_a" in report
        assert "config_b" in report

    def test_html_format(self) -> None:
        checks_a = [_make_check("empty_suggestions", "run", True)]
        checks_b = [_make_check("empty_suggestions", "run", True)]
        comparison_checks = [
            _make_check("suggestion_overlap", "run", True),
        ]
        report = generate_autocomplete_comparison_report(
            checks_a,
            checks_b,
            comparison_checks,
            "config_a",
            "config_b",
            format="html",
        )
        assert "<html" in report
        assert "Comparison" in report


def _make_judgment(
    prefix: str,
    relevance: int = 3,
    diversity: int = 2,
    flagged: list[str] | None = None,
) -> SuggestionJudgment:
    return SuggestionJudgment(
        prefix=prefix,
        suggestions=["s1", "s2"],
        relevance_score=relevance,
        diversity_score=diversity,
        flagged_suggestions=flagged or [],
        reasoning="Test reasoning.",
        model="test-model",
        experiment="test",
    )


class TestAutocompleteReportWithLlm:
    def test_terminal_shows_llm_summary(self) -> None:
        checks = [_make_check("empty_suggestions", "run", True)]
        judgments = [_make_judgment("run", relevance=3, diversity=2)]
        report = generate_autocomplete_report(
            checks,
            format="terminal",
            suggestion_judgments=judgments,
        )
        assert "LLM Suggestion Quality" in report
        assert "Avg Relevance" in report
        assert "Avg Diversity" in report

    def test_terminal_shows_flagged_suggestions(self) -> None:
        checks = [_make_check("empty_suggestions", "deck", True)]
        judgments = [
            _make_judgment("deck", relevance=1, diversity=2, flagged=["deck of cards"])
        ]
        report = generate_autocomplete_report(
            checks,
            format="terminal",
            suggestion_judgments=judgments,
        )
        assert "Flagged Suggestions" in report
        assert "deck of cards" in report

    def test_terminal_shows_lowest_relevance(self) -> None:
        checks = [_make_check("empty_suggestions", "run", True)]
        judgments = [_make_judgment("run", relevance=0, diversity=1)]
        report = generate_autocomplete_report(
            checks,
            format="terminal",
            suggestion_judgments=judgments,
        )
        assert "Lowest Relevance" in report

    def test_terminal_drill_down_has_rel_div_columns(self) -> None:
        checks = [_make_check("empty_suggestions", "run", True)]
        prefixes = [PrefixEntry(prefix="run")]
        responses = {0: AutocompleteResponse(suggestions=["running shoes"])}
        judgments = [_make_judgment("run", relevance=3, diversity=2)]
        report = generate_autocomplete_report(
            checks,
            format="terminal",
            responses_by_prefix=responses,
            prefixes=prefixes,
            suggestion_judgments=judgments,
        )
        assert "Rel" in report
        assert "Div" in report

    def test_html_shows_llm_summary(self) -> None:
        checks = [_make_check("empty_suggestions", "run", True)]
        judgments = [_make_judgment("run", relevance=3, diversity=2)]
        report = generate_autocomplete_report(
            checks,
            format="html",
            suggestion_judgments=judgments,
        )
        assert "LLM Suggestion Quality" in report
        assert "Avg Relevance" in report

    def test_html_shows_flagged_details(self) -> None:
        checks = [_make_check("empty_suggestions", "deck", True)]
        judgments = [
            _make_judgment("deck", relevance=1, diversity=2, flagged=["deck of cards"])
        ]
        report = generate_autocomplete_report(
            checks,
            format="html",
            suggestion_judgments=judgments,
        )
        assert "Flagged Suggestions" in report
        assert "deck of cards" in report

    def test_html_prefix_detail_has_llm_scores(self) -> None:
        checks = [_make_check("empty_suggestions", "run", True)]
        prefixes = [PrefixEntry(prefix="run")]
        responses = {0: AutocompleteResponse(suggestions=["running shoes"])}
        judgments = [_make_judgment("run", relevance=3, diversity=2)]
        report = generate_autocomplete_report(
            checks,
            format="html",
            responses_by_prefix=responses,
            prefixes=prefixes,
            suggestion_judgments=judgments,
        )
        assert "Relevance: 3/3" in report
        assert "Diversity: 2/3" in report
