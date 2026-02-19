"""Tests for SuggestionJudge."""

from __future__ import annotations

from unittest.mock import Mock

import pytest

from veritail.autocomplete.judge import SuggestionJudge
from veritail.llm.client import LLMClient, LLMResponse


def _make_mock_client(response_text: str) -> LLMClient:
    client = Mock(spec=LLMClient)
    client.complete.return_value = LLMResponse(
        content=response_text,
        model="test-model",
        input_tokens=100,
        output_tokens=40,
    )
    return client


class TestSuggestionJudge:
    def test_valid_parsing(self):
        client = _make_mock_client(
            "RELEVANCE: 3\n"
            "DIVERSITY: 2\n"
            "FLAGGED: none\n"
            "REASONING: All suggestions are relevant completions."
        )
        judge = SuggestionJudge(client, "system prompt", "exp-1")
        sj = judge.judge("run", ["running shoes", "runner", "run fast"])
        assert sj.relevance_score == 3
        assert sj.diversity_score == 2
        assert sj.flagged_suggestions == []
        assert "relevant" in sj.reasoning
        assert sj.prefix == "run"
        assert sj.suggestions == ["running shoes", "runner", "run fast"]
        assert sj.model == "test-model"
        assert sj.experiment == "exp-1"

    def test_flagged_extraction(self):
        client = _make_mock_client(
            "RELEVANCE: 1\n"
            "DIVERSITY: 2\n"
            "FLAGGED: deck of cards, playing cards\n"
            "REASONING: Two suggestions are unrelated to home improvement."
        )
        judge = SuggestionJudge(client, "system prompt", "exp-1")
        sj = judge.judge("deck", ["deck boards", "deck of cards", "playing cards"])
        assert sj.relevance_score == 1
        assert sj.flagged_suggestions == ["deck of cards", "playing cards"]

    def test_missing_relevance_raises(self):
        client = _make_mock_client("DIVERSITY: 2\nFLAGGED: none\nREASONING: ok")
        judge = SuggestionJudge(client, "system prompt", "exp-1")
        with pytest.raises(ValueError, match="relevance"):
            judge.judge("run", ["running shoes"])

    def test_missing_diversity_raises(self):
        client = _make_mock_client("RELEVANCE: 2\nFLAGGED: none\nREASONING: ok")
        judge = SuggestionJudge(client, "system prompt", "exp-1")
        with pytest.raises(ValueError, match="diversity"):
            judge.judge("run", ["running shoes"])

    def test_invalid_relevance_score_raises(self):
        client = _make_mock_client(
            "RELEVANCE: 5\nDIVERSITY: 2\nFLAGGED: none\nREASONING: ok"
        )
        judge = SuggestionJudge(client, "system prompt", "exp-1")
        with pytest.raises(ValueError, match="Relevance score must be"):
            judge.judge("run", ["running shoes"])

    def test_invalid_diversity_score_raises(self):
        client = _make_mock_client(
            "RELEVANCE: 2\nDIVERSITY: 7\nFLAGGED: none\nREASONING: ok"
        )
        judge = SuggestionJudge(client, "system prompt", "exp-1")
        with pytest.raises(ValueError, match="Diversity score must be"):
            judge.judge("run", ["running shoes"])

    def test_case_insensitive_labels(self):
        client = _make_mock_client(
            "relevance: 2\ndiversity: 1\nflagged: none\nreasoning: ok"
        )
        judge = SuggestionJudge(client, "system prompt", "exp-1")
        sj = judge.judge("run", ["running shoes"])
        assert sj.relevance_score == 2
        assert sj.diversity_score == 1

    def test_user_prompt_format(self):
        prompt = SuggestionJudge._format_user_prompt(
            "head", ["headphones", "headband", "headset"]
        )
        assert "head" in prompt
        assert "1. headphones" in prompt
        assert "2. headband" in prompt
        assert "3. headset" in prompt
        assert "Prefix" in prompt
        assert "Suggestions" in prompt

    def test_metadata_includes_tokens(self):
        client = _make_mock_client(
            "RELEVANCE: 2\nDIVERSITY: 2\nFLAGGED: none\nREASONING: Fine."
        )
        judge = SuggestionJudge(client, "system prompt", "exp-1")
        sj = judge.judge("run", ["running shoes"])
        assert sj.metadata["input_tokens"] == 100
        assert sj.metadata["output_tokens"] == 40

    def test_batch_prepare_request(self):
        client = _make_mock_client("")
        judge = SuggestionJudge(client, "my-system-prompt", "exp-1")
        req = judge.prepare_request("id-1", "run", ["running shoes", "runner"])
        assert req.custom_id == "id-1"
        assert req.system_prompt == "my-system-prompt"
        assert "run" in req.user_prompt
        assert "running shoes" in req.user_prompt

    def test_batch_parse_result(self):
        client = _make_mock_client("")
        judge = SuggestionJudge(client, "system prompt", "exp-1")
        response = LLMResponse(
            content="RELEVANCE: 3\nDIVERSITY: 2\nFLAGGED: none\nREASONING: Great.",
            model="batch-model",
            input_tokens=90,
            output_tokens=35,
        )
        sj = judge.parse_batch_result(response, "run", ["running shoes", "runner"])
        assert sj.relevance_score == 3
        assert sj.diversity_score == 2
        assert sj.model == "batch-model"
        assert sj.metadata["input_tokens"] == 90

    def test_equals_sign_separator(self):
        client = _make_mock_client(
            "RELEVANCE= 2\nDIVERSITY= 3\nFLAGGED= none\nREASONING= ok"
        )
        judge = SuggestionJudge(client, "system prompt", "exp-1")
        sj = judge.judge("run", ["running shoes"])
        assert sj.relevance_score == 2
        assert sj.diversity_score == 3
