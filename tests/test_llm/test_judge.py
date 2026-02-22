"""Tests for LLM relevance judge."""

from __future__ import annotations

from unittest.mock import Mock

import pytest

from veritail.llm.client import BatchRequest, LLMClient, LLMResponse
from veritail.llm.judge import CORRECTION_SYSTEM_PROMPT, CorrectionJudge, RelevanceJudge
from veritail.types import SearchResult


def _make_mock_client(response_text: str) -> LLMClient:
    client = Mock(spec=LLMClient)
    client.complete.return_value = LLMResponse(
        content=response_text,
        model="test-model",
        input_tokens=100,
        output_tokens=50,
    )
    return client


def _make_result() -> SearchResult:
    return SearchResult(
        product_id="SKU-001",
        title="Nike Running Shoes",
        description="Classic running shoes",
        category="Shoes > Running",
        price=129.99,
        position=0,
        attributes={"color": "black", "brand": "Nike"},
    )


def _format_user_prompt(query: str, result: SearchResult) -> str:
    return f"Query: {query}\nProduct: {result.title}"


class TestRelevanceJudge:
    def test_judge_score_3(self):
        client = _make_mock_client(
            "SCORE: 3\nATTRIBUTES: match\nREASONING: Exact match for running shoes."
        )
        judge = RelevanceJudge(client, "system", _format_user_prompt, "exp-1")

        judgment = judge.judge("running shoes", _make_result())
        assert judgment.score == 3
        assert judgment.attribute_verdict == "match"
        assert judgment.reasoning == "Exact match for running shoes."
        assert judgment.model == "test-model"
        assert judgment.experiment == "exp-1"
        assert judgment.query == "running shoes"

    def test_judge_score_0(self):
        client = _make_mock_client(
            "SCORE: 0\nATTRIBUTES: mismatch\nREASONING: Completely irrelevant product."
        )
        judge = RelevanceJudge(client, "system", _format_user_prompt, "exp-1")

        judgment = judge.judge("laptop stand", _make_result())
        assert judgment.score == 0
        assert judgment.attribute_verdict == "mismatch"

    def test_judge_with_extra_whitespace(self):
        client = _make_mock_client(
            "SCORE:  2 \nATTRIBUTES: partial\n REASONING:  Decent match  "
        )
        judge = RelevanceJudge(client, "system", _format_user_prompt, "exp-1")

        judgment = judge.judge("shoes", _make_result())
        assert judgment.score == 2
        assert judgment.attribute_verdict == "partial"
        assert judgment.reasoning == "Decent match"

    def test_judge_multiline_reasoning(self):
        response = (
            "SCORE: 2\nATTRIBUTES: n/a\n"
            "REASONING: First line.\nSecond line.\nThird line."
        )
        client = _make_mock_client(response)
        judge = RelevanceJudge(client, "system", _format_user_prompt, "exp-1")

        judgment = judge.judge("shoes", _make_result())
        assert judgment.score == 2
        assert judgment.attribute_verdict == "n/a"
        assert "First line." in judgment.reasoning
        assert "Third line." in judgment.reasoning

    def test_judge_invalid_score(self):
        client = _make_mock_client(
            "SCORE: 5\nATTRIBUTES: n/a\nREASONING: Out of range."
        )
        judge = RelevanceJudge(client, "system", _format_user_prompt, "exp-1")

        with pytest.raises(ValueError, match="Score must be 0, 1, 2, or 3"):
            judge.judge("shoes", _make_result())

    def test_judge_no_score(self):
        client = _make_mock_client("This product is relevant.")
        judge = RelevanceJudge(client, "system", _format_user_prompt, "exp-1")

        with pytest.raises(ValueError, match="Could not parse score"):
            judge.judge("shoes", _make_result())

    def test_judge_no_reasoning(self):
        client = _make_mock_client("SCORE: 2\nATTRIBUTES: match")
        judge = RelevanceJudge(client, "system", _format_user_prompt, "exp-1")

        judgment = judge.judge("shoes", _make_result())
        assert judgment.score == 2
        assert judgment.attribute_verdict == "match"
        assert judgment.reasoning == ""

    def test_judge_attributes_label_case_insensitive(self):
        client = _make_mock_client(
            "SCORE: 2\nattributes: mismatch\nREASONING: Attribute mismatch."
        )
        judge = RelevanceJudge(client, "system", _format_user_prompt, "exp-1")

        judgment = judge.judge("shoes", _make_result())
        assert judgment.score == 2
        assert judgment.attribute_verdict == "mismatch"

    def test_judge_reasoning_label_case_insensitive(self):
        client = _make_mock_client(
            "SCORE: 2\nATTRIBUTES: match\nReasoning: Mixed-case label works."
        )
        judge = RelevanceJudge(client, "system", _format_user_prompt, "exp-1")

        judgment = judge.judge("shoes", _make_result())
        assert judgment.score == 2
        assert judgment.attribute_verdict == "match"
        assert judgment.reasoning == "Mixed-case label works."

    def test_judge_metadata_includes_tokens(self):
        client = _make_mock_client(
            "SCORE: 3\nATTRIBUTES: match\nREASONING: Perfect match."
        )
        judge = RelevanceJudge(client, "system", _format_user_prompt, "exp-1")

        judgment = judge.judge("shoes", _make_result())
        assert judgment.metadata["input_tokens"] == 100
        assert judgment.metadata["output_tokens"] == 50

    def test_judge_passes_query_type(self):
        client = _make_mock_client(
            "SCORE: 3\nATTRIBUTES: match\nREASONING: Perfect match."
        )
        judge = RelevanceJudge(client, "system", _format_user_prompt, "exp-1")

        judgment = judge.judge("shoes", _make_result(), query_type="broad")
        assert judgment.query_type == "broad"

    def test_judge_query_type_defaults_to_none(self):
        client = _make_mock_client(
            "SCORE: 3\nATTRIBUTES: match\nREASONING: Perfect match."
        )
        judge = RelevanceJudge(client, "system", _format_user_prompt, "exp-1")

        judgment = judge.judge("shoes", _make_result())
        assert judgment.query_type is None

    def test_judge_attributes_match(self):
        client = _make_mock_client(
            "SCORE: 3\nATTRIBUTES: match\nREASONING: Color and brand match."
        )
        judge = RelevanceJudge(client, "system", _format_user_prompt, "exp-1")

        judgment = judge.judge("black nike shoes", _make_result())
        assert judgment.attribute_verdict == "match"

    def test_judge_attributes_missing(self):
        """Responses without ATTRIBUTES line should default to n/a."""
        client = _make_mock_client("SCORE: 2\nREASONING: Decent match.")
        judge = RelevanceJudge(client, "system", _format_user_prompt, "exp-1")

        judgment = judge.judge("shoes", _make_result())
        assert judgment.attribute_verdict == "n/a"
        assert judgment.reasoning == "Decent match."

    def test_judge_passes_overlay_to_format(self):
        """Overlay kwarg is forwarded to format_user_prompt."""
        calls: list[dict] = []

        def fmt(query, result, *, overlay=None):
            calls.append({"overlay": overlay})
            return f"Query: {query}\nProduct: {result.title}"

        client = _make_mock_client("SCORE: 3\nATTRIBUTES: match\nREASONING: Perfect.")
        judge = RelevanceJudge(client, "system", fmt, "exp-1")
        judge.judge("fryer", _make_result(), overlay="Hot-side equipment guidance.")
        assert calls[0]["overlay"] == "Hot-side equipment guidance."

    def test_judge_overlay_fallback_for_incompatible_format_func(self):
        """When format_user_prompt doesn't accept overlay, falls back gracefully."""
        client = _make_mock_client("SCORE: 2\nATTRIBUTES: n/a\nREASONING: Fallback.")
        # _format_user_prompt doesn't accept overlay kwarg
        judge = RelevanceJudge(client, "system", _format_user_prompt, "exp-1")
        judgment = judge.judge(
            "fryer", _make_result(), overlay="Hot-side equipment guidance."
        )
        assert judgment.score == 2


class TestRelevanceJudgeBatch:
    def test_prepare_request_basic(self):
        client = _make_mock_client("unused")
        judge = RelevanceJudge(client, "system prompt", _format_user_prompt, "exp-1")

        req = judge.prepare_request("req-0", "running shoes", _make_result())

        assert isinstance(req, BatchRequest)
        assert req.custom_id == "req-0"
        assert req.system_prompt == "system prompt"
        assert "running shoes" in req.user_prompt
        assert "Nike Running Shoes" in req.user_prompt

    def test_prepare_request_with_corrected_query(self):
        """When format_user_prompt accepts corrected_query, it is passed through."""

        def fmt(query, result, *, corrected_query=None):
            if corrected_query:
                return f"Query: {query} (corrected: {corrected_query})"
            return f"Query: {query}"

        client = _make_mock_client("unused")
        judge = RelevanceJudge(client, "system", fmt, "exp-1")

        req = judge.prepare_request(
            "req-0",
            "runnign shoes",
            _make_result(),
            corrected_query="running shoes",
        )
        assert "corrected: running shoes" in req.user_prompt

    def test_parse_batch_result_success(self):
        client = _make_mock_client("unused")
        judge = RelevanceJudge(client, "system", _format_user_prompt, "exp-1")

        response = LLMResponse(
            content="SCORE: 3\nATTRIBUTES: match\nREASONING: Great match.",
            model="test-model",
            input_tokens=100,
            output_tokens=50,
        )
        judgment = judge.parse_batch_result(
            response, "running shoes", _make_result(), query_type="broad"
        )

        assert judgment.score == 3
        assert judgment.attribute_verdict == "match"
        assert judgment.reasoning == "Great match."
        assert judgment.query == "running shoes"
        assert judgment.model == "test-model"
        assert judgment.experiment == "exp-1"
        assert judgment.query_type == "broad"
        assert judgment.metadata["input_tokens"] == 100

    def test_prepare_request_with_overlay(self):
        """Overlay kwarg is forwarded to format_user_prompt in batch mode."""

        def fmt(query, result, *, overlay=None):
            if overlay:
                return f"Query: {query}\nOverlay: {overlay}\nProduct: {result.title}"
            return f"Query: {query}\nProduct: {result.title}"

        client = _make_mock_client("unused")
        judge = RelevanceJudge(client, "system", fmt, "exp-1")

        req = judge.prepare_request(
            "req-0",
            "commercial fryer",
            _make_result(),
            overlay="Hot-side scoring guidance.",
        )
        assert "Overlay: Hot-side scoring guidance." in req.user_prompt

    def test_prepare_request_overlay_fallback(self):
        """When format_user_prompt doesn't accept overlay, falls back gracefully."""
        client = _make_mock_client("unused")
        judge = RelevanceJudge(client, "system", _format_user_prompt, "exp-1")

        req = judge.prepare_request(
            "req-0",
            "fryer",
            _make_result(),
            overlay="Hot-side scoring guidance.",
        )
        assert "fryer" in req.user_prompt

    def test_parse_batch_result_bad_score_raises(self):
        client = _make_mock_client("unused")
        judge = RelevanceJudge(client, "system", _format_user_prompt, "exp-1")

        response = LLMResponse(
            content="SCORE: 5\nREASONING: Out of range",
            model="test-model",
            input_tokens=10,
            output_tokens=10,
        )

        with pytest.raises(ValueError, match="Score must be 0, 1, 2, or 3"):
            judge.parse_batch_result(response, "shoes", _make_result())


class TestCorrectionJudgeBatch:
    def test_correction_prepare_request(self):
        client = _make_mock_client("unused")
        judge = CorrectionJudge(client, CORRECTION_SYSTEM_PROMPT, "exp-1")

        req = judge.prepare_request("corr-0", "runnign shoes", "running shoes")

        assert isinstance(req, BatchRequest)
        assert req.custom_id == "corr-0"
        assert req.system_prompt == CORRECTION_SYSTEM_PROMPT
        assert "runnign shoes" in req.user_prompt
        assert "running shoes" in req.user_prompt

    def test_correction_parse_batch_result(self):
        client = _make_mock_client("unused")
        judge = CorrectionJudge(client, CORRECTION_SYSTEM_PROMPT, "exp-1")

        response = LLMResponse(
            content="VERDICT: appropriate\nREASONING: Spelling fix.",
            model="test-model",
            input_tokens=80,
            output_tokens=30,
        )
        cj = judge.parse_batch_result(response, "runnign shoes", "running shoes")

        assert cj.verdict == "appropriate"
        assert cj.reasoning == "Spelling fix."
        assert cj.original_query == "runnign shoes"
        assert cj.corrected_query == "running shoes"
        assert cj.model == "test-model"
        assert cj.metadata["input_tokens"] == 80
