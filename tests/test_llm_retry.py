"""Tests for single-retry behaviour on synchronous LLM call sites."""

from __future__ import annotations

from unittest.mock import Mock

import pytest

from veritail.llm.client import LLMResponse
from veritail.types import SearchResult

# ── Helpers ──────────────────────────────────────────────────────


def _make_response(content: str) -> LLMResponse:
    return LLMResponse(
        content=content,
        model="test-model",
        input_tokens=10,
        output_tokens=5,
    )


def _make_client(*responses: LLMResponse | Exception) -> Mock:
    """Build a mock LLMClient whose .complete() yields *responses* in order."""
    client = Mock()
    effects: list[LLMResponse | Exception] = list(responses)
    client.complete = Mock(side_effect=effects)
    return client


def _search_result() -> SearchResult:
    return SearchResult(
        product_id="P1",
        title="Test Product",
        description="A test product",
        category="test",
        price=9.99,
        position=0,
    )


# ── classify_query_type ─────────────────────────────────────────


class TestClassifyQueryTypeRetry:
    def test_retries_on_api_error(self):
        client = _make_client(
            RuntimeError("timeout"),
            _make_response("QUERY_TYPE: broad"),
        )
        from veritail.llm.classifier import classify_query_type

        result = classify_query_type(client, "running shoes")
        assert result == "broad"
        assert client.complete.call_count == 2

    def test_retries_on_parse_failure(self):
        client = _make_client(
            _make_response("I think this is a general query"),
            _make_response("QUERY_TYPE: navigational"),
        )
        from veritail.llm.classifier import classify_query_type

        result = classify_query_type(client, "nike.com")
        assert result == "navigational"
        assert client.complete.call_count == 2

    def test_gives_up_after_two_failures(self):
        client = _make_client(
            RuntimeError("timeout"),
            RuntimeError("timeout again"),
        )
        from veritail.llm.classifier import classify_query_type

        result = classify_query_type(client, "shoes")
        assert result is None
        assert client.complete.call_count == 2

    def test_succeeds_on_first_attempt(self):
        client = _make_client(
            _make_response("QUERY_TYPE: attribute"),
        )
        from veritail.llm.classifier import classify_query_type

        result = classify_query_type(client, "red shoes size 10")
        assert result == "attribute"
        assert client.complete.call_count == 1


# ── classify_query (with overlay) ───────────────────────────────


class TestClassifyQueryRetry:
    def test_retries_on_parse_failure(self):
        client = _make_client(
            _make_response("hmm, not sure"),
            _make_response("QUERY_TYPE: broad\nOVERLAY: shoes"),
        )
        from veritail.llm.classifier import classify_query

        overlay_keys = {"shoes": "Footwear products"}
        qt, overlay = classify_query(client, "running shoes", overlay_keys=overlay_keys)
        assert qt == "broad"
        assert overlay == "shoes"
        assert client.complete.call_count == 2

    def test_retries_on_api_error(self):
        client = _make_client(
            RuntimeError("connection reset"),
            _make_response("QUERY_TYPE: long_tail\nOVERLAY: none"),
        )
        from veritail.llm.classifier import classify_query

        overlay_keys = {"shoes": "Footwear products"}
        qt, overlay = classify_query(
            client, "blue suede shoes size 9", overlay_keys=overlay_keys
        )
        assert qt == "long_tail"
        assert client.complete.call_count == 2

    def test_gives_up_after_two_parse_failures(self):
        client = _make_client(
            _make_response("dunno"),
            _make_response("still dunno"),
        )
        from veritail.llm.classifier import classify_query

        overlay_keys = {"shoes": "Footwear products"}
        qt, overlay = classify_query(client, "xyz", overlay_keys=overlay_keys)
        assert qt is None
        assert client.complete.call_count == 2


# ── RelevanceJudge ──────────────────────────────────────────────


class TestRelevanceJudgeRetry:
    def _make_judge(self, client: Mock) -> object:
        from veritail.llm.judge import RelevanceJudge

        return RelevanceJudge(
            client=client,
            system_prompt="You are a judge.",
            format_user_prompt=lambda q, r: f"Query: {q}\nResult: {r.title}",
            experiment="test-exp",
        )

    def test_retries_on_api_error(self):
        client = _make_client(
            RuntimeError("500 error"),
            _make_response("SCORE: 2\nATTRIBUTES: match\nREASONING: Good result"),
        )
        judge = self._make_judge(client)
        record = judge.judge("shoes", _search_result())
        assert record.score == 2
        assert client.complete.call_count == 2

    def test_retries_on_parse_failure(self):
        client = _make_client(
            _make_response("This looks like an A+ result!"),
            _make_response("SCORE: 3\nATTRIBUTES: match\nREASONING: Perfect match"),
        )
        judge = self._make_judge(client)
        record = judge.judge("shoes", _search_result())
        assert record.score == 3
        assert client.complete.call_count == 2

    def test_raises_after_two_failures(self):
        client = _make_client(
            _make_response("garbage"),
            _make_response("still garbage"),
        )
        judge = self._make_judge(client)
        with pytest.raises(ValueError, match="Could not parse score"):
            judge.judge("shoes", _search_result())
        assert client.complete.call_count == 2

    def test_succeeds_on_first_attempt(self):
        client = _make_client(
            _make_response("SCORE: 1\nATTRIBUTES: n/a\nREASONING: Low relevance"),
        )
        judge = self._make_judge(client)
        record = judge.judge("shoes", _search_result())
        assert record.score == 1
        assert client.complete.call_count == 1


# ── CorrectionJudge ─────────────────────────────────────────────


class TestCorrectionJudgeRetry:
    def _make_judge(self, client: Mock) -> object:
        from veritail.llm.judge import CorrectionJudge

        return CorrectionJudge(
            client=client,
            system_prompt="You judge corrections.",
            experiment="test-exp",
        )

    def test_retries_on_error_verdict(self):
        client = _make_client(
            _make_response("I'm not sure what to say"),
            _make_response("VERDICT: appropriate\nREASONING: Good correction"),
        )
        judge = self._make_judge(client)
        result = judge.judge("runnign shoes", "running shoes")
        assert result.verdict == "appropriate"
        assert client.complete.call_count == 2

    def test_retries_on_api_error(self):
        client = _make_client(
            RuntimeError("network timeout"),
            _make_response("VERDICT: inappropriate\nREASONING: Not a typo"),
        )
        judge = self._make_judge(client)
        result = judge.judge("running shoes", "jogging shoes")
        assert result.verdict == "inappropriate"
        assert client.complete.call_count == 2

    def test_raises_after_two_api_errors(self):
        client = _make_client(
            RuntimeError("fail 1"),
            RuntimeError("fail 2"),
        )
        judge = self._make_judge(client)
        with pytest.raises(RuntimeError):
            judge.judge("shoes", "boots")
        assert client.complete.call_count == 2

    def test_returns_error_verdict_after_two_parse_failures(self):
        client = _make_client(
            _make_response("no idea"),
            _make_response("still no idea"),
        )
        judge = self._make_judge(client)
        result = judge.judge("shoes", "boots")
        assert result.verdict == "error"
        assert client.complete.call_count == 2


# ── SuggestionJudge ─────────────────────────────────────────────


class TestSuggestionJudgeRetry:
    def _make_judge(self, client: Mock) -> object:
        from veritail.autocomplete.judge import SuggestionJudge

        return SuggestionJudge(
            client=client,
            system_prompt="You judge suggestions.",
            experiment="test-exp",
        )

    def test_retries_on_parse_failure(self):
        client = _make_client(
            _make_response("These look great!"),
            _make_response(
                "RELEVANCE: 2\nDIVERSITY: 3\nFLAGGED: none\nREASONING: Good variety"
            ),
        )
        judge = self._make_judge(client)
        result = judge.judge("sho", ["shoes", "shorts", "shopping"])
        assert result.relevance_score == 2
        assert result.diversity_score == 3
        assert client.complete.call_count == 2

    def test_retries_on_api_error(self):
        client = _make_client(
            RuntimeError("rate limited"),
            _make_response(
                "RELEVANCE: 1\nDIVERSITY: 1\nFLAGGED: none\nREASONING: Weak"
            ),
        )
        judge = self._make_judge(client)
        result = judge.judge("sho", ["shoes"])
        assert result.relevance_score == 1
        assert client.complete.call_count == 2

    def test_raises_after_two_failures(self):
        client = _make_client(
            _make_response("nope"),
            _make_response("still nope"),
        )
        judge = self._make_judge(client)
        with pytest.raises(ValueError, match="Could not parse relevance"):
            judge.judge("sho", ["shoes"])
        assert client.complete.call_count == 2


# ── generate_queries ─────────────────────────────────────────────


class TestGenerateQueriesRetry:
    def test_retries_on_parse_failure(self, tmp_path):
        from veritail.querygen import generate_queries

        client = _make_client(
            _make_response("Here are some queries for you!"),
            _make_response('["running shoes", "hiking boots", "sandals"]'),
        )
        output = tmp_path / "queries.csv"
        result = generate_queries(
            llm_client=client,
            output_path=output,
            count=3,
            instructions="Shoe store",
        )
        assert len(result) == 3
        assert client.complete.call_count == 2

    def test_retries_on_api_error(self, tmp_path):
        from veritail.querygen import generate_queries

        client = _make_client(
            RuntimeError("server error"),
            _make_response('["shoes", "boots"]'),
        )
        output = tmp_path / "queries.csv"
        result = generate_queries(
            llm_client=client,
            output_path=output,
            count=2,
            instructions="Shoe store",
        )
        assert len(result) == 2
        assert client.complete.call_count == 2

    def test_raises_after_two_failures(self, tmp_path):
        from veritail.querygen import generate_queries

        client = _make_client(
            RuntimeError("fail 1"),
            RuntimeError("fail 2"),
        )
        output = tmp_path / "queries.csv"
        with pytest.raises(RuntimeError):
            generate_queries(
                llm_client=client,
                output_path=output,
                count=3,
                instructions="Shoe store",
            )
        assert client.complete.call_count == 2


# ── generate_summary ─────────────────────────────────────────────


class TestGenerateSummaryRetry:
    def _make_metrics(self):
        from veritail.types import MetricResult

        return [
            MetricResult(metric_name="ndcg@10", value=0.75, per_query={"q1": 0.5}),
        ]

    def _make_checks(self):
        from veritail.types import CheckResult

        return [
            CheckResult(
                check_name="zero_results",
                query="q1",
                product_id=None,
                passed=True,
                detail="ok",
            ),
        ]

    def test_retries_on_empty_parse(self):
        from veritail.reporting.summary import generate_summary

        client = _make_client(
            _make_response("x"),  # too short, parse returns None
            _make_response(
                "- NDCG@10 of 0.75 indicates reasonable relevance.\n"
                "- Zero-result rate is healthy at 0%."
            ),
        )
        result = generate_summary(client, self._make_metrics(), self._make_checks())
        assert result is not None
        assert "NDCG" in result
        assert client.complete.call_count == 2

    def test_retries_on_api_error(self):
        from veritail.reporting.summary import generate_summary

        client = _make_client(
            RuntimeError("API down"),
            _make_response("- Good overall relevance with NDCG@10 of 0.75."),
        )
        result = generate_summary(client, self._make_metrics(), self._make_checks())
        assert result is not None
        assert client.complete.call_count == 2

    def test_does_not_retry_on_no_insights_sentinel(self):
        from veritail.reporting.summary import generate_summary

        client = _make_client(
            _make_response("__NO_INSIGHTS__"),
        )
        result = generate_summary(client, self._make_metrics(), self._make_checks())
        assert result is None
        assert client.complete.call_count == 1

    def test_returns_none_after_two_api_errors(self):
        from veritail.reporting.summary import generate_summary

        client = _make_client(
            RuntimeError("fail 1"),
            RuntimeError("fail 2"),
        )
        result = generate_summary(client, self._make_metrics(), self._make_checks())
        assert result is None
        assert client.complete.call_count == 2


# ── generate_comparison_summary ──────────────────────────────────


class TestGenerateComparisonSummaryRetry:
    def _make_metrics(self):
        from veritail.types import MetricResult

        return [
            MetricResult(
                metric_name="ndcg@10",
                value=0.75,
                per_query={"q1": 0.5},
            ),
        ]

    def test_retries_on_empty_parse(self):
        from veritail.reporting.summary import generate_comparison_summary

        client = _make_client(
            _make_response("too short"),
            _make_response(
                "- Config B shows a +5% improvement in NDCG@10 over Config A."
            ),
        )
        result = generate_comparison_summary(
            client,
            self._make_metrics(),
            self._make_metrics(),
            checks_a=None,
            checks_b=None,
            judgments_a=None,
            judgments_b=None,
            comparison_checks=[],
            config_a="A",
            config_b="B",
        )
        assert result is not None
        assert client.complete.call_count == 2

    def test_does_not_retry_on_no_insights_sentinel(self):
        from veritail.reporting.summary import generate_comparison_summary

        client = _make_client(
            _make_response("__NO_INSIGHTS__"),
        )
        result = generate_comparison_summary(
            client,
            self._make_metrics(),
            self._make_metrics(),
            checks_a=None,
            checks_b=None,
            judgments_a=None,
            judgments_b=None,
            comparison_checks=[],
            config_a="A",
            config_b="B",
        )
        assert result is None
        assert client.complete.call_count == 1
