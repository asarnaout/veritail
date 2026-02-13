"""Tests for comparison report generation."""

from __future__ import annotations

from veritail.reporting.comparison import generate_comparison_report
from veritail.types import CheckResult, MetricResult


def _make_metrics_a() -> list[MetricResult]:
    return [
        MetricResult(
            metric_name="ndcg@10",
            value=0.75,
            per_query={"shoes": 0.8, "laptop": 0.7},
            by_query_type={"broad": 0.75},
        ),
        MetricResult(metric_name="mrr", value=0.65),
    ]


def _make_metrics_b() -> list[MetricResult]:
    return [
        MetricResult(
            metric_name="ndcg@10",
            value=0.85,
            per_query={"shoes": 0.9, "laptop": 0.8},
            by_query_type={"broad": 0.85},
        ),
        MetricResult(metric_name="mrr", value=0.72),
    ]


def _make_comparison_checks() -> list[CheckResult]:
    return [
        CheckResult(
            check_name="result_overlap",
            query="shoes",
            product_id=None,
            passed=True,
            detail="Result overlap: 0.60 (6/10 shared products)",
        ),
        CheckResult(
            check_name="position_shift",
            query="shoes",
            product_id="SKU-1",
            passed=True,
            detail="'Nike Shoes' dropped 5 positions (#1 -> #6)",
        ),
    ]


class TestGenerateComparisonReport:
    def test_terminal_report_contains_both_configs(self):
        report = generate_comparison_report(
            _make_metrics_a(), _make_metrics_b(),
            _make_comparison_checks(), "baseline", "experiment",
        )
        assert "baseline" in report
        assert "experiment" in report

    def test_terminal_report_contains_deltas(self):
        report = generate_comparison_report(
            _make_metrics_a(), _make_metrics_b(),
            _make_comparison_checks(), "baseline", "experiment",
        )
        assert "ndcg@10" in report
        # Should show improvement
        assert "+0.1000" in report

    def test_terminal_report_contains_position_shifts(self):
        report = generate_comparison_report(
            _make_metrics_a(), _make_metrics_b(),
            _make_comparison_checks(), "baseline", "experiment",
        )
        assert "Position Shift" in report

    def test_html_report(self):
        report = generate_comparison_report(
            _make_metrics_a(), _make_metrics_b(),
            _make_comparison_checks(), "baseline", "experiment",
            format="html",
        )
        assert "<html" in report
        assert "baseline" in report
        assert "experiment" in report

    def test_html_report_includes_run_metadata_footer(self):
        report = generate_comparison_report(
            _make_metrics_a(),
            _make_metrics_b(),
            _make_comparison_checks(),
            "baseline",
            "experiment",
            format="html",
            run_metadata={
                "generated_at_utc": "2026-02-13T12:00:00Z",
                "llm_model": "claude-sonnet-4-5",
                "rubric": "ecommerce-default",
                "vertical": "industrial",
                "top_k": 10,
                "adapter_path_a": "adapter_a.py",
                "adapter_path_b": "adapter_b.py",
            },
        )
        assert "Timestamp (UTC)" in report
        assert "2026-02-13T12:00:00Z" in report
        assert "claude-sonnet-4-5" in report
        assert "ecommerce-default" in report
        assert "industrial" in report
        assert "adapter_a.py" in report
        assert "adapter_b.py" in report

    def test_regression_detection(self):
        metrics_a = [MetricResult(
            metric_name="ndcg@10", value=0.9,
            per_query={"shoes": 0.9, "laptop": 0.9},
        )]
        metrics_b = [MetricResult(
            metric_name="ndcg@10", value=0.7,
            per_query={"shoes": 0.5, "laptop": 0.9},  # shoes regressed
        )]
        report = generate_comparison_report(
            metrics_a, metrics_b, [], "v1", "v2",
        )
        assert "Regression" in report
        assert "shoes" in report

    def test_html_escapes_untrusted_comparison_content(self):
        checks = [
            CheckResult(
                check_name="position_shift",
                query="<script>alert('query')</script>",
                product_id="SKU-1",
                passed=True,
                detail="<img src=x onerror=alert('detail')>",
            ),
        ]
        report = generate_comparison_report(
            _make_metrics_a(),
            _make_metrics_b(),
            checks,
            "<script>alert('cfg-a')</script>",
            "experiment",
            format="html",
        )

        assert "<script>alert('cfg-a')</script>" not in report
        assert "<script>alert('query')</script>" not in report
        assert "<img src=x onerror=alert('detail')>" not in report
        assert "&lt;script&gt;alert" in report
        assert "&lt;img src=x onerror=alert" in report
