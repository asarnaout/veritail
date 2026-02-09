"""Tests for LLM client abstraction."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from search_eval.llm.client import (
    AnthropicClient,
    OpenAIClient,
    create_llm_client,
)


class TestAnthropicClient:
    @patch("anthropic.Anthropic")
    def test_complete(self, mock_anthropic_cls):
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="SCORE: 2\nREASONING: Good match")]
        mock_response.usage.input_tokens = 100
        mock_response.usage.output_tokens = 50
        mock_anthropic_cls.return_value.messages.create.return_value = mock_response

        client = AnthropicClient(model="claude-sonnet-4-5")
        result = client.complete("system prompt", "user prompt")

        assert result.content == "SCORE: 2\nREASONING: Good match"
        assert result.model == "claude-sonnet-4-5"
        assert result.input_tokens == 100
        assert result.output_tokens == 50


class TestOpenAIClient:
    @patch("openai.OpenAI")
    def test_complete(self, mock_openai_cls):
        mock_choice = MagicMock()
        mock_choice.message.content = "SCORE: 3\nREASONING: Exact match"
        mock_usage = MagicMock()
        mock_usage.prompt_tokens = 200
        mock_usage.completion_tokens = 80
        mock_response = MagicMock()
        mock_response.choices = [mock_choice]
        mock_response.usage = mock_usage
        mock_openai_cls.return_value.chat.completions.create.return_value = mock_response

        client = OpenAIClient(model="gpt-4o")
        result = client.complete("system prompt", "user prompt")

        assert result.content == "SCORE: 3\nREASONING: Exact match"
        assert result.model == "gpt-4o"
        assert result.input_tokens == 200
        assert result.output_tokens == 80


class TestCreateLLMClient:
    @patch("anthropic.Anthropic")
    def test_claude_model(self, mock_anthropic_cls):
        client = create_llm_client("claude-sonnet-4-5")
        assert isinstance(client, AnthropicClient)

    @patch("openai.OpenAI")
    def test_openai_model(self, mock_openai_cls):
        client = create_llm_client("gpt-4o")
        assert isinstance(client, OpenAIClient)

    @patch("openai.OpenAI")
    def test_local_model(self, mock_openai_cls):
        # Local models use OpenAI-compatible API
        client = create_llm_client("llama-3-70b")
        assert isinstance(client, OpenAIClient)
