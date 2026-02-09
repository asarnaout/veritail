"""Tests for LLM relevance judge."""

from __future__ import annotations

from unittest.mock import Mock

import pytest

from search_eval.llm.client import LLMClient, LLMResponse
from search_eval.llm.judge import RelevanceJudge
from search_eval.types import SearchResult


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
        client = _make_mock_client("SCORE: 3\nREASONING: Exact match for running shoes.")
        judge = RelevanceJudge(client, "system", _format_user_prompt, "exp-1")

        judgment = judge.judge("running shoes", _make_result())
        assert judgment.score == 3
        assert judgment.reasoning == "Exact match for running shoes."
        assert judgment.model == "test-model"
        assert judgment.experiment == "exp-1"
        assert judgment.query == "running shoes"

    def test_judge_score_0(self):
        client = _make_mock_client("SCORE: 0\nREASONING: Completely irrelevant product.")
        judge = RelevanceJudge(client, "system", _format_user_prompt, "exp-1")

        judgment = judge.judge("laptop stand", _make_result())
        assert judgment.score == 0

    def test_judge_with_extra_whitespace(self):
        client = _make_mock_client("SCORE:  2 \n REASONING:  Decent match  ")
        judge = RelevanceJudge(client, "system", _format_user_prompt, "exp-1")

        judgment = judge.judge("shoes", _make_result())
        assert judgment.score == 2
        assert judgment.reasoning == "Decent match"

    def test_judge_multiline_reasoning(self):
        response = "SCORE: 2\nREASONING: First line.\nSecond line.\nThird line."
        client = _make_mock_client(response)
        judge = RelevanceJudge(client, "system", _format_user_prompt, "exp-1")

        judgment = judge.judge("shoes", _make_result())
        assert judgment.score == 2
        assert "First line." in judgment.reasoning
        assert "Third line." in judgment.reasoning

    def test_judge_invalid_score(self):
        client = _make_mock_client("SCORE: 5\nREASONING: Out of range.")
        judge = RelevanceJudge(client, "system", _format_user_prompt, "exp-1")

        with pytest.raises(ValueError, match="Score must be 0, 1, 2, or 3"):
            judge.judge("shoes", _make_result())

    def test_judge_no_score(self):
        client = _make_mock_client("This product is relevant.")
        judge = RelevanceJudge(client, "system", _format_user_prompt, "exp-1")

        with pytest.raises(ValueError, match="Could not parse score"):
            judge.judge("shoes", _make_result())

    def test_judge_no_reasoning(self):
        client = _make_mock_client("SCORE: 2")
        judge = RelevanceJudge(client, "system", _format_user_prompt, "exp-1")

        judgment = judge.judge("shoes", _make_result())
        assert judgment.score == 2
        assert judgment.reasoning == ""

    def test_judge_metadata_includes_tokens(self):
        client = _make_mock_client("SCORE: 3\nREASONING: Perfect match.")
        judge = RelevanceJudge(client, "system", _format_user_prompt, "exp-1")

        judgment = judge.judge("shoes", _make_result())
        assert judgment.metadata["input_tokens"] == 100
        assert judgment.metadata["output_tokens"] == 50
