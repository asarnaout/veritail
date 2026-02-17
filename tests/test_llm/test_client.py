"""Tests for LLM client abstraction."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from veritail.llm.client import (
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
        mock_client = mock_anthropic_cls.return_value
        mock_client.messages.create.return_value = mock_response

        client = AnthropicClient(model="claude-sonnet-4-5")
        result = client.complete("system prompt", "user prompt")

        assert result.content == "SCORE: 2\nREASONING: Good match"
        assert result.model == "claude-sonnet-4-5"
        assert result.input_tokens == 100
        assert result.output_tokens == 50

    @patch("anthropic.Anthropic")
    def test_preflight_check_success(self, mock_anthropic_cls):
        client = AnthropicClient(model="claude-sonnet-4-5")
        # models.retrieve returns without error → no exception raised
        client.preflight_check()
        mock_anthropic_cls.return_value.models.retrieve.assert_called_once_with(
            model_id="claude-sonnet-4-5"
        )

    @patch("anthropic.Anthropic")
    def test_preflight_check_bad_key(self, mock_anthropic_cls):
        import anthropic

        mock_anthropic_cls.return_value.models.retrieve.side_effect = (
            anthropic.AuthenticationError(
                message="invalid key",
                response=MagicMock(status_code=401),
                body=None,
            )
        )
        client = AnthropicClient(model="claude-sonnet-4-5")
        with pytest.raises(RuntimeError, match="Anthropic API key is invalid"):
            client.preflight_check()

    @patch("anthropic.Anthropic")
    def test_preflight_check_bad_model(self, mock_anthropic_cls):
        import anthropic

        mock_anthropic_cls.return_value.models.retrieve.side_effect = (
            anthropic.NotFoundError(
                message="not found",
                response=MagicMock(status_code=404),
                body=None,
            )
        )
        client = AnthropicClient(model="claude-nonexistent")
        with pytest.raises(RuntimeError, match="not found on Anthropic"):
            client.preflight_check()


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
        mock_client = mock_openai_cls.return_value
        mock_client.chat.completions.create.return_value = mock_response

        client = OpenAIClient(model="gpt-4o")
        result = client.complete("system prompt", "user prompt")

        assert result.content == "SCORE: 3\nREASONING: Exact match"
        assert result.model == "gpt-4o"
        assert result.input_tokens == 200
        assert result.output_tokens == 80

    @patch("openai.OpenAI")
    def test_preflight_check_success(self, mock_openai_cls):
        client = OpenAIClient(model="gpt-4o")
        client.preflight_check()
        mock_openai_cls.return_value.models.retrieve.assert_called_once_with("gpt-4o")

    @patch("openai.OpenAI")
    def test_preflight_check_bad_key(self, mock_openai_cls):
        import openai

        mock_openai_cls.return_value.models.retrieve.side_effect = (
            openai.AuthenticationError(
                message="invalid key",
                response=MagicMock(status_code=401),
                body=None,
            )
        )
        client = OpenAIClient(model="gpt-4o")
        with pytest.raises(RuntimeError, match="OpenAI API key is invalid"):
            client.preflight_check()

    @patch("openai.OpenAI")
    def test_preflight_check_bad_model(self, mock_openai_cls):
        import openai

        mock_openai_cls.return_value.models.retrieve.side_effect = openai.NotFoundError(
            message="not found",
            response=MagicMock(status_code=404),
            body=None,
        )
        client = OpenAIClient(model="gpt-nonexistent")
        with pytest.raises(RuntimeError, match="not found on OpenAI"):
            client.preflight_check()

    @patch("openai.OpenAI")
    def test_preflight_check_skips_for_compatible_apis(self, mock_openai_cls):
        """OpenAI-compatible APIs may not implement /v1/models; don't fail."""
        mock_openai_cls.return_value.models.retrieve.side_effect = ConnectionError(
            "refused"
        )
        client = OpenAIClient(model="llama-3-70b")
        # Should not raise
        client.preflight_check()


class TestOpenAIClientBaseUrl:
    @patch("openai.OpenAI")
    def test_base_url_passed_to_sdk(self, mock_openai_cls):
        """base_url and api_key are forwarded to openai.OpenAI()."""
        OpenAIClient(
            model="qwen3:14b",
            base_url="http://localhost:11434/v1",
            api_key="not-needed",
        )
        mock_openai_cls.assert_called_once_with(
            base_url="http://localhost:11434/v1",
            api_key="not-needed",
        )

    @patch("openai.OpenAI")
    def test_base_url_defaults_to_none(self, mock_openai_cls):
        """Without explicit base_url/api_key the SDK falls back to env vars."""
        OpenAIClient(model="gpt-4o")
        mock_openai_cls.assert_called_once_with(base_url=None, api_key=None)

    @patch("openai.OpenAI")
    def test_complete_with_custom_base_url(self, mock_openai_cls):
        mock_choice = MagicMock()
        mock_choice.message.content = "SCORE: 2\nREASONING: Ok"
        mock_usage = MagicMock()
        mock_usage.prompt_tokens = 100
        mock_usage.completion_tokens = 40
        mock_response = MagicMock()
        mock_response.choices = [mock_choice]
        mock_response.usage = mock_usage
        mock_client = mock_openai_cls.return_value
        mock_client.chat.completions.create.return_value = mock_response

        client = OpenAIClient(
            model="llama3.1:8b",
            base_url="http://localhost:11434/v1",
            api_key="ollama",
        )
        result = client.complete("system prompt", "user prompt")

        assert result.content == "SCORE: 2\nREASONING: Ok"
        assert result.model == "llama3.1:8b"


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

    @patch("openai.OpenAI")
    def test_base_url_forwarded(self, mock_openai_cls):
        """create_llm_client passes base_url and api_key to OpenAIClient."""
        client = create_llm_client(
            "qwen3:14b",
            base_url="http://localhost:11434/v1",
            api_key="not-needed",
        )
        assert isinstance(client, OpenAIClient)
        mock_openai_cls.assert_called_once_with(
            base_url="http://localhost:11434/v1",
            api_key="not-needed",
        )

    @patch("anthropic.Anthropic")
    def test_claude_ignores_base_url(self, mock_anthropic_cls):
        """Claude models always use Anthropic — base_url is ignored."""
        client = create_llm_client(
            "claude-sonnet-4-5",
            base_url="http://localhost:11434/v1",
        )
        assert isinstance(client, AnthropicClient)
