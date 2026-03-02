"""Tests for LLM-powered report summary generation."""

from __future__ import annotations

from unittest.mock import MagicMock

from veritail.llm.client import LLMClient, LLMResponse
from veritail.reporting.summary import (
    _build_comparison_payload,
    _build_single_payload,
    _parse_summary_response,
    generate_comparison_summary,
    generate_summary,
    summary_bullets_to_html,
)
from veritail.types import (
    CheckResult,
    CorrectionJudgment,
    JudgmentRecord,
    MetricResult,
    SearchResult,
)

# ── Fixtures ─────────────────────────────────────────────────────


def _product(position: int = 0, product_id: str = "SKU-1") -> SearchResult:
    return SearchResult(
        product_id=product_id,
        title="Test Product",
        description="A product",
        category="shoes",
        price=49.99,
        position=position,
    )


def _make_metrics() -> list[MetricResult]:
    return [
        MetricResult(
            metric_name="ndcg@10",
            value=0.75,
            per_query={"shoes": 0.9, "laptop": 0.5, "socks": 0.85},
            by_query_type={"broad": 0.80, "navigational": 0.70},
            ci_lower=0.65,
            ci_upper=0.85,
        ),
        MetricResult(
            metric_name="mrr",
            value=0.72,
            per_query={"shoes": 0.8, "laptop": 0.6, "socks": 0.75},
            by_query_type={"broad": 0.75, "navigational": 0.69},
        ),
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
            check_name="text_overlap",
            query="laptop",
            product_id="SKU-1",
            passed=False,
            detail="Low keyword overlap: 10%",
        ),
        CheckResult(
            check_name="price_outlier",
            query="laptop",
            product_id="SKU-2",
            passed=False,
            detail="Price $999 is 3.5x the median ($285)",
        ),
    ]


def _make_judgments() -> list[JudgmentRecord]:
    return [
        JudgmentRecord(
            query="shoes",
            product=_product(0, "SKU-1"),
            score=3,
            reasoning="Highly relevant running shoes.",
            model="gpt-4o",
            experiment="test",
            query_type="broad",
        ),
        JudgmentRecord(
            query="shoes",
            product=_product(1, "SKU-2"),
            score=2,
            reasoning="Partially relevant.",
            model="gpt-4o",
            experiment="test",
            query_type="broad",
        ),
        JudgmentRecord(
            query="laptop",
            product=_product(0, "SKU-3"),
            score=1,
            reasoning="Low relevance laptop case.",
            model="gpt-4o",
            experiment="test",
            query_type="navigational",
        ),
        JudgmentRecord(
            query="laptop",
            product=_product(1, "SKU-4"),
            score=0,
            reasoning="Irrelevant monitor stand.",
            model="gpt-4o",
            experiment="test",
            query_type="navigational",
        ),
        JudgmentRecord(
            query="socks",
            product=_product(0, "SKU-5"),
            score=3,
            reasoning="Perfect match.",
            model="gpt-4o",
            experiment="test",
            query_type="broad",
        ),
    ]


def _make_corrections() -> list[CorrectionJudgment]:
    return [
        CorrectionJudgment(
            original_query="laptp",
            corrected_query="laptop",
            verdict="appropriate",
            reasoning="Clear typo correction.",
            model="gpt-4o",
            experiment="test",
        ),
    ]


def _mock_client(response_text: str) -> LLMClient:
    client = MagicMock(spec=LLMClient)
    client.complete.return_value = LLMResponse(
        content=response_text,
        model="gpt-4o",
        input_tokens=100,
        output_tokens=50,
    )
    return client


# ── _parse_summary_response ──────────────────────────────────────


class TestParseSummaryResponse:
    def test_returns_none_for_empty_string(self):
        assert _parse_summary_response("") is None

    def test_returns_none_for_whitespace(self):
        assert _parse_summary_response("   \n  ") is None

    def test_returns_none_for_no_insights_sentinel(self):
        assert _parse_summary_response("__NO_INSIGHTS__") is None

    def test_returns_none_for_sentinel_with_surrounding_text(self):
        assert _parse_summary_response("Nothing found.\n__NO_INSIGHTS__") is None

    def test_returns_none_for_short_text(self):
        assert _parse_summary_response("Too short.") is None

    def test_returns_valid_summary(self):
        text = "- This is a meaningful insight about the search quality data."
        result = _parse_summary_response(text)
        assert result == text

    def test_strips_whitespace(self):
        text = "  - Insight about data patterns.\n- Another insight.  "
        result = _parse_summary_response(text)
        assert result == text.strip()


# ── summary_bullets_to_html ──────────────────────────────────────


class TestSummaryBulletsToHtml:
    def test_converts_bullets_to_list(self):
        text = "- First bullet\n- Second bullet"
        result = summary_bullets_to_html(text)
        assert "<ul>" in result
        assert "<li>First bullet</li>" in result
        assert "<li>Second bullet</li>" in result
        assert "</ul>" in result

    def test_escapes_html_in_bullets(self):
        text = "- Contains <script>alert('xss')</script> in text"
        result = summary_bullets_to_html(text)
        assert "<script>" not in result
        assert "&lt;script&gt;" in result

    def test_non_bullet_lines_become_paragraphs(self):
        text = "Some header text\n- A bullet"
        result = summary_bullets_to_html(text)
        assert "<p>Some header text</p>" in result
        assert "<li>A bullet</li>" in result

    def test_empty_lines_close_list(self):
        text = "- First group\n\n- Second group"
        result = summary_bullets_to_html(text)
        # Should have two separate <ul> blocks
        assert result.count("<ul>") == 2
        assert result.count("</ul>") == 2

    def test_empty_input(self):
        result = summary_bullets_to_html("")
        assert result == ""

    def test_mixed_content(self):
        text = "Header\n- Bullet 1\n- Bullet 2\nFooter"
        result = summary_bullets_to_html(text)
        assert "<p>Header</p>" in result
        assert "<li>Bullet 1</li>" in result
        assert "<li>Bullet 2</li>" in result
        assert "<p>Footer</p>" in result

    def test_bold_markdown_converted_to_strong(self):
        text = "- **Important:** this is a key insight."
        result = summary_bullets_to_html(text)
        assert "<strong>Important:</strong> this is a key insight." in result
        assert "**" not in result

    def test_bold_xss_still_escaped(self):
        text = '- **<script>alert("xss")</script>** bold attack'
        result = summary_bullets_to_html(text)
        assert "<script>" not in result
        assert "<strong>&lt;script&gt;" in result

    def test_three_or_fewer_bullets_no_collapse(self):
        text = "- First.\n- Second.\n- Third."
        result = summary_bullets_to_html(text)
        assert "<details" not in result
        assert result.count("<li>") == 3

    def test_more_than_three_bullets_collapsed(self):
        text = "- One.\n- Two.\n- Three.\n- Four.\n- Five."
        result = summary_bullets_to_html(text)
        assert result.count("<li>") == 5
        assert '<details class="summary-more">' in result
        assert "Show more" in result
        # First 3 bullets in the visible <ul>
        first_details = result.index("<details")
        assert result.index("<li>One.</li>") < first_details
        assert result.index("<li>Three.</li>") < first_details
        # Bullets 4-5 inside <details>
        assert result.index("<li>Four.</li>") > first_details
        assert result.index("<li>Five.</li>") > first_details

    def test_blank_lines_between_bullets_stay_collapsed(self):
        """LLMs typically separate bullets with blank lines."""
        text = "- One.\n\n- Two.\n\n- Three.\n\n- Four.\n\n- Five."
        result = summary_bullets_to_html(text)
        assert result.count("<li>") == 5
        assert '<details class="summary-more">' in result
        # Both overflow bullets must be inside <details>
        first_details = result.index("<details")
        last_details_close = result.rindex("</details>")
        assert result.index("<li>Four.</li>") > first_details
        assert result.index("<li>Five.</li>") > first_details
        assert result.index("<li>Five.</li>") < last_details_close


class TestParseTruncation:
    def test_drops_truncated_last_bullet(self):
        text = "- Complete insight about the data.\n- This one is cut off mid-sen"
        result = _parse_summary_response(text)
        assert result is not None
        assert "Complete insight" in result
        assert "cut off" not in result

    def test_keeps_complete_bullets(self):
        text = "- First insight about patterns.\n- Second insight about queries."
        result = _parse_summary_response(text)
        assert result is not None
        assert "First insight" in result
        assert "Second insight" in result

    def test_returns_none_if_all_bullets_truncated(self):
        text = "- Cut off"
        assert _parse_summary_response(text) is None


# ── _build_single_payload ────────────────────────────────────────


class TestBuildSinglePayload:
    def test_includes_score_distribution(self):
        payload = _build_single_payload(
            _make_metrics(),
            _make_checks(),
            _make_judgments(),
            None,
            None,
        )
        assert "Score Distribution" in payload
        assert "5 judgments" in payload

    def test_includes_metrics(self):
        payload = _build_single_payload(
            _make_metrics(),
            _make_checks(),
            None,
            None,
            None,
        )
        assert "ndcg@10: 0.7500" in payload
        assert "CI: 0.6500-0.8500" in payload

    def test_includes_by_query_type(self):
        payload = _build_single_payload(
            _make_metrics(),
            [],
            None,
            None,
            None,
        )
        assert "broad: 0.8000" in payload
        assert "navigational: 0.7000" in payload

    def test_includes_check_summary(self):
        payload = _build_single_payload(
            _make_metrics(),
            _make_checks(),
            None,
            None,
            None,
        )
        assert "Check Summary" in payload
        assert "text_overlap" in payload
        assert "price_outlier" in payload

    def test_includes_worst_queries(self):
        payload = _build_single_payload(
            _make_metrics(),
            _make_checks(),
            _make_judgments(),
            None,
            None,
        )
        assert "Worst 5 Queries" in payload
        assert '"laptop"' in payload

    def test_includes_high_variance(self):
        payload = _build_single_payload(
            _make_metrics(),
            _make_checks(),
            _make_judgments(),
            None,
            None,
        )
        # laptop has scores [0, 1] which has higher variance than others
        assert "Mixed-Relevance Queries" in payload

    def test_includes_position_decay(self):
        payload = _build_single_payload(
            _make_metrics(),
            _make_checks(),
            _make_judgments(),
            None,
            None,
        )
        assert "Average Score by Position" in payload
        assert "Position 1" in payload

    def test_includes_check_failure_samples(self):
        payload = _build_single_payload(
            _make_metrics(),
            _make_checks(),
            None,
            None,
            None,
        )
        assert "Check Failure Samples" in payload
        assert "Low keyword overlap" in payload

    def test_includes_corrections(self):
        payload = _build_single_payload(
            _make_metrics(),
            _make_checks(),
            None,
            _make_corrections(),
            None,
        )
        assert "Corrections" in payload
        assert '"laptp"' in payload
        assert "appropriate" in payload

    def test_empty_payload_returns_empty_string(self):
        payload = _build_single_payload([], [], None, None, None)
        assert payload == ""

    def test_worst_queries_with_disambiguated_keys(self):
        """Disambiguated keys like 'shoes [1]' should resolve to raw query data."""
        metrics = [
            MetricResult(
                metric_name="ndcg@10",
                value=0.50,
                per_query={"shoes [1]": 0.3, "shoes [2]": 0.4, "laptop": 0.8},
            ),
        ]
        judgments = [
            JudgmentRecord(
                query="shoes",
                product=_product(0, "SKU-1"),
                score=2,
                reasoning="Decent match.",
                model="gpt-4o",
                experiment="test",
                query_type="broad",
            ),
            JudgmentRecord(
                query="shoes",
                product=_product(1, "SKU-2"),
                score=1,
                reasoning="Weak match.",
                model="gpt-4o",
                experiment="test",
                query_type="broad",
            ),
            JudgmentRecord(
                query="laptop",
                product=_product(0, "SKU-3"),
                score=3,
                reasoning="Great match.",
                model="gpt-4o",
                experiment="test",
                query_type="navigational",
            ),
        ]
        checks = [
            CheckResult(
                check_name="text_overlap",
                query="shoes",
                product_id="SKU-1",
                passed=False,
                detail="Low overlap",
            ),
        ]
        payload = _build_single_payload(metrics, checks, judgments, None, None)
        # Disambiguated key should appear in display
        assert '"shoes [1]"' in payload
        # Raw-query lookup should find the type
        assert "type=broad" in payload
        # Raw-query lookup should find score data
        assert "pos1=" in payload
        # Raw-query lookup should find failed checks
        assert "text_overlap" in payload

    def test_no_judgments_skips_judgment_sections(self):
        payload = _build_single_payload(
            _make_metrics(),
            _make_checks(),
            None,
            None,
            None,
        )
        assert "Score Distribution" not in payload
        assert "Worst 5 Queries" not in payload
        assert "Mixed-Relevance" not in payload


# ── _build_comparison_payload ────────────────────────────────────


class TestBuildComparisonPayload:
    def test_includes_aggregate_metrics(self):
        metrics_a = _make_metrics()
        metrics_b = [
            MetricResult(
                metric_name="ndcg@10",
                value=0.80,
                per_query={"shoes": 0.95, "laptop": 0.55, "socks": 0.90},
                by_query_type={"broad": 0.85},
            ),
            MetricResult(
                metric_name="mrr",
                value=0.78,
                per_query={"shoes": 0.85, "laptop": 0.65, "socks": 0.84},
            ),
        ]
        payload = _build_comparison_payload(
            metrics_a, metrics_b, None, None, None, None, [], "A", "B", None, None
        )
        assert "Aggregate Metrics" in payload
        assert "A=0.7500" in payload
        assert "B=0.8000" in payload

    def test_includes_metric_deltas(self):
        metrics_a = _make_metrics()
        metrics_b = [
            MetricResult(metric_name="ndcg@10", value=0.80),
            MetricResult(metric_name="mrr", value=0.78),
        ]
        payload = _build_comparison_payload(
            metrics_a, metrics_b, None, None, None, None, [], "A", "B", None, None
        )
        assert "Metric Deltas" in payload
        assert "+0.0500" in payload

    def test_includes_win_loss_tie(self):
        metrics_a = [
            MetricResult(
                metric_name="ndcg@10",
                value=0.75,
                per_query={"shoes": 0.9, "laptop": 0.5},
            ),
        ]
        metrics_b = [
            MetricResult(
                metric_name="ndcg@10",
                value=0.80,
                per_query={"shoes": 0.95, "laptop": 0.5},
            ),
        ]
        payload = _build_comparison_payload(
            metrics_a, metrics_b, None, None, None, None, [], "A", "B", None, None
        )
        assert "Win/Loss/Tie" in payload

    def test_includes_check_deltas(self):
        checks_a = [
            CheckResult(
                check_name="text_overlap",
                query="q1",
                product_id="p1",
                passed=False,
                detail="fail",
            ),
        ]
        checks_b = [
            CheckResult(
                check_name="text_overlap",
                query="q1",
                product_id="p1",
                passed=True,
                detail="ok",
            ),
        ]
        payload = _build_comparison_payload(
            _make_metrics(),
            _make_metrics(),
            checks_a,
            checks_b,
            None,
            None,
            [],
            "A",
            "B",
            None,
            None,
        )
        assert "Check Failure Deltas" in payload

    def test_includes_query_type_metrics(self):
        payload = _build_comparison_payload(
            _make_metrics(),
            _make_metrics(),
            None,
            None,
            None,
            None,
            [],
            "A",
            "B",
            None,
            None,
        )
        assert "Metrics by Query Type" in payload

    def test_includes_result_overlap(self):
        comparison_checks = [
            CheckResult(
                check_name="result_overlap",
                query="shoes",
                product_id=None,
                passed=True,
                detail="Result overlap: 0.60 (6/10 shared)",
            ),
            CheckResult(
                check_name="result_overlap",
                query="laptop",
                product_id=None,
                passed=True,
                detail="Result overlap: 0.40 (4/10 shared)",
            ),
        ]
        payload = _build_comparison_payload(
            _make_metrics(),
            _make_metrics(),
            None,
            None,
            None,
            None,
            comparison_checks,
            "A",
            "B",
            None,
            None,
        )
        assert "Result Overlap" in payload
        assert "Mean Jaccard: 0.50" in payload

    def test_includes_position_shifts(self):
        comparison_checks = [
            CheckResult(
                check_name="position_shift",
                query="shoes",
                product_id="SKU-1",
                passed=False,
                detail="Moved 3 positions (1 -> 4)",
            ),
        ]
        payload = _build_comparison_payload(
            _make_metrics(),
            _make_metrics(),
            None,
            None,
            None,
            None,
            comparison_checks,
            "A",
            "B",
            None,
            None,
        )
        assert "Position Shifts" in payload
        assert "3 positions" in payload

    def test_includes_score_distributions(self):
        payload = _build_comparison_payload(
            _make_metrics(),
            _make_metrics(),
            None,
            None,
            _make_judgments(),
            _make_judgments(),
            [],
            "A",
            "B",
            None,
            None,
        )
        assert "Score Distribution: A" in payload
        assert "Score Distribution: B" in payload

    def test_includes_significance_data(self):
        metrics_a = [
            MetricResult(
                metric_name="ndcg@10",
                value=0.50,
                per_query={"q1": 0.3, "q2": 0.5, "q3": 0.7},
            ),
        ]
        metrics_b = [
            MetricResult(
                metric_name="ndcg@10",
                value=0.80,
                per_query={"q1": 0.7, "q2": 0.8, "q3": 0.9},
            ),
        ]
        payload = _build_comparison_payload(
            metrics_a,
            metrics_b,
            None,
            None,
            None,
            None,
            [],
            "A",
            "B",
            None,
            None,
        )
        assert "p=" in payload


# ── generate_summary ─────────────────────────────────────────────


class TestGenerateSummary:
    def test_returns_summary_on_success(self):
        client = _mock_client(
            "- Navigational queries underperform broad queries by 10 points."
        )
        result = generate_summary(
            client,
            _make_metrics(),
            _make_checks(),
            judgments=_make_judgments(),
        )
        assert result is not None
        assert "Navigational" in result
        client.complete.assert_called_once()

    def test_returns_none_on_no_insights(self):
        client = _mock_client("__NO_INSIGHTS__")
        result = generate_summary(client, _make_metrics(), _make_checks())
        assert result is None

    def test_returns_none_on_empty_payload(self):
        client = _mock_client("some text")
        result = generate_summary(client, [], [])
        assert result is None
        client.complete.assert_not_called()

    def test_returns_none_on_exception(self):
        client = MagicMock(spec=LLMClient)
        client.complete.side_effect = RuntimeError("API error")
        result = generate_summary(client, _make_metrics(), _make_checks())
        assert result is None


# ── generate_comparison_summary ──────────────────────────────────


class TestGenerateComparisonSummary:
    def test_returns_summary_on_success(self):
        client = _mock_client(
            "- Config B improves broad queries but regresses navigational ones."
        )
        result = generate_comparison_summary(
            client,
            _make_metrics(),
            _make_metrics(),
            checks_a=_make_checks(),
            checks_b=_make_checks(),
            judgments_a=_make_judgments(),
            judgments_b=_make_judgments(),
            comparison_checks=[],
            config_a="baseline",
            config_b="experiment",
        )
        assert result is not None
        assert "Config B" in result

    def test_returns_none_on_no_insights(self):
        client = _mock_client("__NO_INSIGHTS__")
        result = generate_comparison_summary(
            client,
            _make_metrics(),
            _make_metrics(),
            checks_a=None,
            checks_b=None,
            judgments_a=None,
            judgments_b=None,
            comparison_checks=[],
            config_a="A",
            config_b="B",
        )
        assert result is None

    def test_returns_none_on_exception(self):
        client = MagicMock(spec=LLMClient)
        client.complete.side_effect = RuntimeError("API error")
        result = generate_comparison_summary(
            client,
            _make_metrics(),
            _make_metrics(),
            checks_a=None,
            checks_b=None,
            judgments_a=None,
            judgments_b=None,
            comparison_checks=[],
            config_a="A",
            config_b="B",
        )
        assert result is None


# ── Report integration ───────────────────────────────────────────


class TestReportIntegration:
    def test_single_terminal_includes_summary(self):
        from veritail.reporting.single import generate_single_report

        report = generate_single_report(
            _make_metrics(),
            _make_checks(),
            summary="- Key insight about search quality patterns.",
        )
        assert "AI Summary" in report
        assert "Key insight" in report

    def test_single_terminal_omits_summary_when_none(self):
        from veritail.reporting.single import generate_single_report

        report = generate_single_report(
            _make_metrics(),
            _make_checks(),
            summary=None,
        )
        assert "AI Summary" not in report

    def test_single_html_includes_summary(self):
        from veritail.reporting.single import generate_single_report

        report = generate_single_report(
            _make_metrics(),
            _make_checks(),
            format="html",
            summary="- HTML insight about patterns.",
        )
        assert 'class="summary-card"' in report
        assert "AI Summary" in report
        assert "HTML insight about patterns." in report

    def test_single_html_omits_summary_when_none(self):
        from veritail.reporting.single import generate_single_report

        report = generate_single_report(
            _make_metrics(),
            _make_checks(),
            format="html",
            summary=None,
        )
        assert 'class="summary-card"' not in report

    def test_comparison_terminal_includes_summary(self):
        from veritail.reporting.comparison import generate_comparison_report

        report = generate_comparison_report(
            _make_metrics(),
            _make_metrics(),
            [],
            "A",
            "B",
            summary="- Comparison insight about configs.",
        )
        assert "AI Summary" in report
        assert "Comparison insight" in report

    def test_comparison_terminal_omits_summary_when_none(self):
        from veritail.reporting.comparison import generate_comparison_report

        report = generate_comparison_report(
            _make_metrics(),
            _make_metrics(),
            [],
            "A",
            "B",
            summary=None,
        )
        assert "AI Summary" not in report

    def test_comparison_html_includes_summary(self):
        from veritail.reporting.comparison import generate_comparison_report

        report = generate_comparison_report(
            _make_metrics(),
            _make_metrics(),
            [],
            "A",
            "B",
            format="html",
            summary="- HTML comparison insight.",
        )
        assert 'class="summary-card"' in report
        assert "AI Summary" in report

    def test_comparison_html_omits_summary_when_none(self):
        from veritail.reporting.comparison import generate_comparison_report

        report = generate_comparison_report(
            _make_metrics(),
            _make_metrics(),
            [],
            "A",
            "B",
            format="html",
            summary=None,
        )
        assert 'class="summary-card"' not in report

    def test_summary_html_escapes_xss(self):
        from veritail.reporting.summary import summary_bullets_to_html

        malicious = '- Contains <script>alert("xss")</script> injection.'
        html = summary_bullets_to_html(malicious)
        # The converted HTML should escape dangerous content
        assert "<script>" not in html
        assert "&lt;script&gt;" in html

        # Also verify it renders safely in the full report
        from veritail.reporting.single import generate_single_report

        report = generate_single_report(
            _make_metrics(),
            _make_checks(),
            format="html",
            summary=malicious,
        )
        # The summary-content div should not contain raw <script>
        import re

        summary_match = re.search(
            r'class="summary-content">(.*?)</div>',
            report,
            re.DOTALL,
        )
        assert summary_match is not None
        summary_html = summary_match.group(1)
        assert "<script>" not in summary_html
        assert "&lt;script&gt;" in summary_html

    def test_summary_nav_link_present_in_single_html(self):
        from veritail.reporting.single import generate_single_report

        report = generate_single_report(
            _make_metrics(),
            _make_checks(),
            format="html",
            summary="- An insight.",
        )
        assert 'href="#section-summary"' in report
        assert ">Summary<" in report

    def test_summary_nav_link_absent_when_no_summary(self):
        from veritail.reporting.single import generate_single_report

        report = generate_single_report(
            _make_metrics(),
            _make_checks(),
            format="html",
            summary=None,
        )
        assert 'href="#section-summary"' not in report
