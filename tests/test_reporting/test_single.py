"""Tests for single-configuration report generation."""

from __future__ import annotations

import re

from veritail.reporting.single import generate_single_report
from veritail.types import (
    CheckResult,
    CorrectionJudgment,
    JudgmentRecord,
    MetricResult,
    SearchResult,
)


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
        CheckResult(
            check_name="zero_results",
            query="shoes",
            product_id=None,
            passed=True,
            detail="OK",
        ),
        CheckResult(
            check_name="zero_results",
            query="laptop",
            product_id=None,
            passed=True,
            detail="OK",
        ),
        CheckResult(
            check_name="text_overlap",
            query="shoes",
            product_id="SKU-1",
            passed=True,
            detail="OK",
        ),
        CheckResult(
            check_name="text_overlap",
            query="shoes",
            product_id="SKU-2",
            passed=False,
            detail="Low overlap",
        ),
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
        assert "text_overlap" in report

    def test_duplicate_check_displays_as_failure_only_in_terminal(self):
        checks = [
            CheckResult(
                check_name="duplicate",
                query="shoes",
                product_id="SKU-1",
                passed=False,
                detail="Near-duplicate titles",
            ),
        ]
        report = generate_single_report(_make_metrics(), checks)
        assert "duplicate (flagged pairs)" in report
        assert "n/a" in report

    def test_terminal_report_worst_queries(self):
        report = generate_single_report(_make_metrics(), _make_checks())
        assert "laptop" in report  # lower NDCG query

    def test_html_report(self):
        report = generate_single_report(_make_metrics(), _make_checks(), format="html")
        assert "<html" in report
        assert "ndcg@10" in report
        assert "0.8500" in report

    def test_html_report_includes_run_metadata_footer(self):
        report = generate_single_report(
            _make_metrics(),
            _make_checks(),
            format="html",
            run_metadata={
                "generated_at_utc": "2026-02-13T12:00:00Z",
                "llm_model": "claude-sonnet-4-5",
                "rubric": "ecommerce-default",
                "vertical": "foodservice",
                "top_k": 10,
                "adapter_path": "adapter.py",
            },
        )
        assert "Timestamp (UTC)" in report
        assert "2026-02-13T12:00:00Z" in report
        assert "claude-sonnet-4-5" in report
        assert "ecommerce-default" in report
        assert "foodservice" in report
        assert "adapter.py" in report

    def test_duplicate_check_displays_as_failure_only_in_html(self):
        checks = [
            CheckResult(
                check_name="duplicate",
                query="shoes",
                product_id="SKU-1",
                passed=False,
                detail="Near-duplicate titles",
            ),
        ]
        report = generate_single_report(_make_metrics(), checks, format="html")
        assert "duplicate (flagged pairs)" in report
        assert ">n/a<" in report
        assert ">1<" in report

    def test_html_check_tooltips(self):
        report = generate_single_report(_make_metrics(), _make_checks(), format="html")
        assert 'data-tip="Fails when a query returns no results at all"' in report
        assert 'data-tip="Measures keyword overlap' in report

    def test_terminal_report_corrections_table(self):
        corrections = [
            CorrectionJudgment(
                original_query="plats",
                corrected_query="plates",
                verdict="appropriate",
                reasoning="Spelling fix",
                model="test",
                experiment="exp",
            ),
            CorrectionJudgment(
                original_query="cambro",
                corrected_query="camaro",
                verdict="inappropriate",
                reasoning="Valid brand",
                model="test",
                experiment="exp",
            ),
        ]
        report = generate_single_report(
            _make_metrics(),
            _make_checks(),
            correction_judgments=corrections,
        )
        assert "Query Corrections" in report
        assert "plats" in report
        assert "plates" in report
        assert "appropriate" in report
        assert "inappropriate" in report

    def test_terminal_report_no_corrections_no_table(self):
        report = generate_single_report(_make_metrics(), _make_checks())
        assert "Query Corrections" not in report

    def test_html_report_corrections_section(self):
        corrections = [
            CorrectionJudgment(
                original_query="plats",
                corrected_query="plates",
                verdict="appropriate",
                reasoning="Spelling fix",
                model="test",
                experiment="exp",
            ),
        ]
        report = generate_single_report(
            _make_metrics(),
            _make_checks(),
            format="html",
            correction_judgments=corrections,
        )
        assert "Query Corrections" in report
        assert "plats" in report
        assert "plates" in report
        assert "appropriate" in report

    def test_html_report_correction_in_judgment_drilldown(self):
        judgment = JudgmentRecord(
            query="plats",
            product=SearchResult(
                product_id="SKU-1",
                title="Plates",
                description="Dinner plates",
                category="Kitchen",
                price=10.0,
                position=0,
            ),
            score=3,
            reasoning="Good match",
            attribute_verdict="n/a",
            model="test",
            experiment="exp",
        )
        corrections = [
            CorrectionJudgment(
                original_query="plats",
                corrected_query="plates",
                verdict="appropriate",
                reasoning="Spelling fix",
                model="test",
                experiment="exp",
            ),
        ]
        report = generate_single_report(
            _make_metrics(),
            _make_checks(),
            format="html",
            judgments=[judgment],
            correction_judgments=corrections,
        )
        # The drill-down should show "plats → plates (appropriate)"
        assert "plates" in report
        assert "appropriate" in report

    def test_terminal_report_attribute_match_na_when_no_queries(self):
        metrics = _make_metrics() + [
            MetricResult(
                metric_name="attribute_match@5",
                value=0.0,
                query_count=0,
                total_queries=5,
            ),
        ]
        report = generate_single_report(metrics, _make_checks())
        assert "N/A" in report
        assert "no queries with attribute constraints" in report

    def test_terminal_report_attribute_match_annotation_when_partial(self):
        metrics = _make_metrics() + [
            MetricResult(
                metric_name="attribute_match@5",
                value=0.85,
                query_count=3,
                total_queries=10,
            ),
        ]
        report = generate_single_report(metrics, _make_checks())
        assert "0.8500" in report
        assert "n=3 of 10 queries" in report

    def test_terminal_report_attribute_match_no_annotation_when_all(self):
        metrics = _make_metrics() + [
            MetricResult(
                metric_name="attribute_match@5",
                value=0.85,
                query_count=10,
                total_queries=10,
            ),
        ]
        report = generate_single_report(metrics, _make_checks())
        assert "0.8500" in report
        assert "(n=" not in report
        assert "N/A" not in report

    def test_html_report_attribute_match_na(self):
        metrics = _make_metrics() + [
            MetricResult(
                metric_name="attribute_match@5",
                value=0.0,
                query_count=0,
                total_queries=5,
            ),
        ]
        report = generate_single_report(metrics, _make_checks(), format="html")
        assert "N/A" in report
        assert "no queries with attribute constraints" in report

    def test_html_report_attribute_match_annotation(self):
        metrics = _make_metrics() + [
            MetricResult(
                metric_name="attribute_match@5",
                value=0.85,
                query_count=3,
                total_queries=10,
            ),
        ]
        report = generate_single_report(metrics, _make_checks(), format="html")
        assert "0.8500" in report
        assert "n=3 of 10 queries" in report

    def test_html_score_distribution(self):
        judgments = [
            JudgmentRecord(
                query="shoes",
                product=SearchResult(
                    product_id=f"SKU-{i}",
                    title=f"Product {i}",
                    description="Desc",
                    category="Shoes",
                    price=10.0,
                    position=i,
                ),
                score=score,
                reasoning="ok",
                attribute_verdict="n/a",
                model="test",
                experiment="exp",
            )
            for i, score in enumerate([3, 3, 2, 2, 2, 1, 0])
        ]
        report = generate_single_report(
            _make_metrics(),
            _make_checks(),
            format="html",
            judgments=judgments,
        )
        assert "Score Distribution" in report
        assert "7 judgments across all queries" in report
        # Check all score levels are present in the legend
        assert "(28.6%)" in report  # 2/7 for score 3
        assert "(42.9%)" in report  # 3/7 for score 2
        assert "(14.3%)" in report  # 1/7 for score 1 and 0

    def test_html_score_distribution_absent_without_judgments(self):
        report = generate_single_report(_make_metrics(), _make_checks(), format="html")
        assert "Score Distribution" not in report

    def test_html_ndcg_stats(self):
        judgments = [
            JudgmentRecord(
                query="shoes",
                product=SearchResult(
                    product_id="SKU-1",
                    title="Shoe",
                    description="A shoe",
                    category="Shoes",
                    price=10.0,
                    position=0,
                ),
                score=3,
                reasoning="ok",
                attribute_verdict="n/a",
                model="test",
                experiment="exp",
            ),
        ]
        report = generate_single_report(
            _make_metrics(),
            _make_checks(),
            format="html",
            judgments=judgments,
        )
        assert "NDCG@10 spread" in report
        assert "min=0.8000" in report
        assert "max=0.9000" in report

    def test_html_ndcg_stats_absent_with_single_query(self):
        metrics = [
            MetricResult(
                metric_name="ndcg@10",
                value=0.9,
                per_query={"shoes": 0.9},
            ),
        ]
        report = generate_single_report(metrics, _make_checks(), format="html")
        assert "NDCG@10 spread" not in report

    def test_html_metrics_by_query_type(self):
        report = generate_single_report(_make_metrics(), _make_checks(), format="html")
        assert "Metrics by Query Type" in report
        assert "broad" in report
        assert "0.8500" in report

    def test_html_metrics_by_query_type_absent_when_no_types(self):
        metrics = [
            MetricResult(metric_name="ndcg@10", value=0.85),
            MetricResult(metric_name="mrr", value=0.72),
        ]
        report = generate_single_report(metrics, _make_checks(), format="html")
        assert "Metrics by Query Type" not in report

    def test_terminal_score_distribution(self):
        judgments = [
            JudgmentRecord(
                query="shoes",
                product=SearchResult(
                    product_id=f"SKU-{i}",
                    title=f"Product {i}",
                    description="Desc",
                    category="Shoes",
                    price=10.0,
                    position=i,
                ),
                score=score,
                reasoning="ok",
                attribute_verdict="n/a",
                model="test",
                experiment="exp",
            )
            for i, score in enumerate([3, 2, 1, 0])
        ]
        report = generate_single_report(
            _make_metrics(), _make_checks(), judgments=judgments
        )
        assert "Score Distribution" in report
        assert "3/3" in report
        assert "0/3" in report

    def test_terminal_score_distribution_absent_without_judgments(self):
        report = generate_single_report(_make_metrics(), _make_checks())
        assert "Score Distribution" not in report

    def test_terminal_ndcg_stats(self):
        report = generate_single_report(_make_metrics(), _make_checks())
        # Strip ANSI escape codes since Rich inserts formatting within text
        plain = re.sub(r"\x1b\[[0-9;]*m", "", report)
        assert "NDCG@10 spread:" in plain
        assert "min=0.8000" in plain
        assert "max=0.9000" in plain

    def test_html_judgments_sorted_worst_first(self):
        judgments = [
            JudgmentRecord(
                query="great query",
                product=SearchResult(
                    product_id="SKU-1",
                    title="Perfect Match",
                    description="Desc",
                    category="Shoes",
                    price=10.0,
                    position=0,
                ),
                score=3,
                reasoning="Excellent",
                attribute_verdict="match",
                model="test",
                experiment="exp",
            ),
            JudgmentRecord(
                query="bad query",
                product=SearchResult(
                    product_id="SKU-2",
                    title="Wrong Product",
                    description="Desc",
                    category="Electronics",
                    price=99.0,
                    position=0,
                ),
                score=0,
                reasoning="Irrelevant",
                attribute_verdict="mismatch",
                model="test",
                experiment="exp",
            ),
        ]
        report = generate_single_report(
            _make_metrics(),
            _make_checks(),
            format="html",
            judgments=judgments,
        )
        bad_pos = report.index("bad query")
        great_pos = report.index("great query")
        assert bad_pos < great_pos, "Worst queries should appear before best"

    def test_html_escapes_untrusted_judgment_content(self):
        judgment = JudgmentRecord(
            query="<script>alert('query')</script>",
            product=SearchResult(
                product_id="SKU-XSS",
                title="<img src=x onerror=alert('title')>",
                description="Desc",
                category="Shoes",
                price=10.0,
                position=0,
            ),
            score=1,
            reasoning="<script>alert('reason')</script>",
            attribute_verdict="n/a",
            model="test-model",
            experiment="test-exp",
        )

        report = generate_single_report(
            _make_metrics(),
            _make_checks(),
            format="html",
            judgments=[judgment],
        )

        assert "<script>alert('reason')</script>" not in report
        assert "<img src=x onerror=alert('title')>" not in report
        assert "&lt;script&gt;alert" in report
        assert "&lt;img src=x onerror=alert" in report
