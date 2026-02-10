"""Tests for single-configuration report generation."""

from __future__ import annotations

from veritail.reporting.single import generate_single_report
from veritail.types import CheckResult, MetricResult


def _make_metrics() -> list[MetricResult]:
    return [
        MetricResult(
            metric_name="ndcg@10",
            value=0.85,
            per_query={"shoes": 0.9, "laptop": 0.8},
            by_query_type={"broad": 0.85},
        ),
        MetricResult(metric_name="mrr", value=0.72),
        MetricResult(metric_name="map", value=0.68),
        MetricResult(metric_name="p@5", value=0.80),
    ]


def _make_checks() -> list[CheckResult]:
    return [
        CheckResult(check_name="zero_results", query="shoes", product_id=None, passed=True, detail="OK"),
        CheckResult(check_name="zero_results", query="laptop", product_id=None, passed=True, detail="OK"),
        CheckResult(check_name="category_alignment", query="shoes", product_id="SKU-1", passed=True, detail="OK"),
        CheckResult(check_name="category_alignment", query="shoes", product_id="SKU-2", passed=False, detail="Mismatch"),
    ]


class TestGenerateSingleReport:
    def test_terminal_report_contains_metrics(self):
        report = generate_single_report(_make_metrics(), _make_checks())
        assert "ndcg@10" in report
        assert "0.8500" in report
        assert "mrr" in report

    def test_terminal_report_contains_checks(self):
        report = generate_single_report(_make_metrics(), _make_checks())
        assert "zero_results" in report
        assert "category_alignment" in report

    def test_terminal_report_worst_queries(self):
        report = generate_single_report(_make_metrics(), _make_checks())
        assert "laptop" in report  # lower NDCG query

    def test_html_report(self):
        report = generate_single_report(_make_metrics(), _make_checks(), format="html")
        assert "<html" in report
        assert "ndcg@10" in report
        assert "0.8500" in report

