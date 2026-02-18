"""Tests for autocomplete report generation."""

from __future__ import annotations

from veritail.autocomplete.reporting import (
    generate_autocomplete_comparison_report,
    generate_autocomplete_report,
)
from veritail.types import (
    AutocompleteResponse,
    CheckResult,
    MetricResult,
    PrefixEntry,
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


def _make_metric(name: str, value: float) -> MetricResult:
    return MetricResult(
        metric_name=name,
        value=value,
        per_query={"run": value},
        by_query_type={"short_prefix": value},
    )


class TestGenerateAutocompleteReport:
    def test_terminal_format(self) -> None:
        metrics = [_make_metric("mrr", 0.75)]
        checks = [_make_check("empty_suggestions", "run", True)]
        report = generate_autocomplete_report(metrics, checks, format="terminal")
        assert "Autocomplete Evaluation Report" in report
        assert "mrr" in report

    def test_terminal_with_prefix_details(self) -> None:
        metrics = [_make_metric("mrr", 0.75)]
        checks = [_make_check("empty_suggestions", "run", True)]
        prefixes = [PrefixEntry(prefix="run", target_query="running shoes")]
        responses = {0: AutocompleteResponse(suggestions=["running shoes"])}
        report = generate_autocomplete_report(
            metrics,
            checks,
            format="terminal",
            responses_by_prefix=responses,
            prefixes=prefixes,
        )
        assert "Per-Prefix" in report
        assert "running shoes" in report

    def test_html_format(self) -> None:
        metrics = [_make_metric("mrr", 0.75)]
        checks = [_make_check("empty_suggestions", "run", True)]
        report = generate_autocomplete_report(metrics, checks, format="html")
        assert "<html" in report
        assert "Autocomplete Evaluation Report" in report
        assert "mrr" in report

    def test_html_with_prefix_details(self) -> None:
        metrics = [_make_metric("mrr", 0.75)]
        checks = [_make_check("empty_suggestions", "run", True)]
        prefixes = [PrefixEntry(prefix="run", target_query="running shoes")]
        responses = {0: AutocompleteResponse(suggestions=["running shoes"])}
        report = generate_autocomplete_report(
            metrics,
            checks,
            format="html",
            responses_by_prefix=responses,
            prefixes=prefixes,
        )
        assert "Per-Prefix" in report
        assert "running shoes" in report


class TestGenerateAutocompleteComparisonReport:
    def test_terminal_format(self) -> None:
        metrics_a = [_make_metric("mrr", 0.5)]
        metrics_b = [_make_metric("mrr", 0.8)]
        comparison_checks = [
            _make_check("suggestion_overlap", "run", True),
        ]
        report = generate_autocomplete_comparison_report(
            metrics_a,
            metrics_b,
            comparison_checks,
            "config_a",
            "config_b",
            format="terminal",
        )
        assert "Comparison" in report
        assert "config_a" in report
        assert "config_b" in report

    def test_html_format(self) -> None:
        metrics_a = [_make_metric("mrr", 0.5)]
        metrics_b = [_make_metric("mrr", 0.8)]
        comparison_checks = [
            _make_check("suggestion_overlap", "run", True),
        ]
        report = generate_autocomplete_comparison_report(
            metrics_a,
            metrics_b,
            comparison_checks,
            "config_a",
            "config_b",
            format="html",
        )
        assert "<html" in report
        assert "Comparison" in report
