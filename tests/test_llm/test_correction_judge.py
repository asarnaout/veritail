"""Tests for CorrectionJudge."""

from __future__ import annotations

from unittest.mock import Mock

from veritail.llm.client import LLMClient, LLMResponse
from veritail.llm.judge import CorrectionJudge


def _make_mock_client(response_text: str) -> LLMClient:
    client = Mock(spec=LLMClient)
    client.complete.return_value = LLMResponse(
        content=response_text,
        model="test-model",
        input_tokens=80,
        output_tokens=30,
    )
    return client


class TestCorrectionJudge:
    def test_appropriate_verdict(self):
        client = _make_mock_client(
            "VERDICT: appropriate\n"
            "REASONING: Clear spelling fix from runnign to running."
        )
        judge = CorrectionJudge(client, "system prompt", "exp-1")
        cj = judge.judge("runnign shoes", "running shoes")
        assert cj.verdict == "appropriate"
        assert "spelling" in cj.reasoning
        assert cj.original_query == "runnign shoes"
        assert cj.corrected_query == "running shoes"
        assert cj.model == "test-model"
        assert cj.experiment == "exp-1"

    def test_inappropriate_verdict(self):
        client = _make_mock_client(
            "VERDICT: inappropriate\n"
            "REASONING: Cambro is a valid brand, not a misspelling."
        )
        judge = CorrectionJudge(client, "system prompt", "exp-1")
        cj = judge.judge("cambro", "camaro")
        assert cj.verdict == "inappropriate"
        assert "Cambro" in cj.reasoning

    def test_error_verdict_on_unparseable(self):
        client = _make_mock_client("I think this is appropriate.")
        judge = CorrectionJudge(client, "system prompt", "exp-1")
        cj = judge.judge("plats", "plates")
        assert cj.verdict == "error"

    def test_metadata_includes_tokens(self):
        client = _make_mock_client("VERDICT: appropriate\nREASONING: Good fix.")
        judge = CorrectionJudge(client, "system prompt", "exp-1")
        cj = judge.judge("foo", "bar")
        assert cj.metadata["input_tokens"] == 80
        assert cj.metadata["output_tokens"] == 30

    def test_case_insensitive_verdict(self):
        client = _make_mock_client("Verdict: Appropriate\nReasoning: Correct fix.")
        judge = CorrectionJudge(client, "system prompt", "exp-1")
        cj = judge.judge("foo", "bar")
        assert cj.verdict == "appropriate"

    def test_user_prompt_format(self):
        prompt = CorrectionJudge._format_user_prompt("plats", "plates")
        assert "plats" in prompt
        assert "plates" in prompt
        assert "Original Query" in prompt
        assert "Corrected Query" in prompt
