"""Tests for LLM client abstraction."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

try:
    import anthropic  # noqa: F401

    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False

try:
    from google import genai  # noqa: F401

    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False

from veritail.llm.client import (
    OpenAIClient,
    create_llm_client,
)


@pytest.mark.skipif(not HAS_ANTHROPIC, reason="anthropic not installed")
class TestAnthropicClient:
    @patch("anthropic.Anthropic")
    def test_complete(self, mock_anthropic_cls):
        from veritail.llm.client import AnthropicClient

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
        from veritail.llm.client import AnthropicClient

        client = AnthropicClient(model="claude-sonnet-4-5")
        # models.retrieve returns without error → no exception raised
        client.preflight_check()
        mock_anthropic_cls.return_value.models.retrieve.assert_called_once_with(
            model_id="claude-sonnet-4-5"
        )

    @patch("anthropic.Anthropic")
    def test_preflight_check_bad_key(self, mock_anthropic_cls):
        import anthropic

        from veritail.llm.client import AnthropicClient

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

        from veritail.llm.client import AnthropicClient

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


@pytest.mark.skipif(not HAS_GENAI, reason="google-genai not installed")
class TestGeminiClient:
    @patch("google.genai.Client")
    def test_complete(self, mock_genai_client_cls):
        from veritail.llm.client import GeminiClient

        mock_response = MagicMock()
        mock_response.text = "SCORE: 2\nREASONING: Relevant"
        mock_usage = MagicMock()
        mock_usage.prompt_token_count = 150
        mock_usage.candidates_token_count = 60
        mock_response.usage_metadata = mock_usage

        mock_client = mock_genai_client_cls.return_value
        mock_client.models.generate_content.return_value = mock_response

        client = GeminiClient(model="gemini-2.5-flash")
        result = client.complete("system prompt", "user prompt")

        assert result.content == "SCORE: 2\nREASONING: Relevant"
        assert result.model == "gemini-2.5-flash"
        assert result.input_tokens == 150
        assert result.output_tokens == 60

        # Verify generate_content was called with correct args
        call_kwargs = mock_client.models.generate_content.call_args
        assert call_kwargs.kwargs["model"] == "gemini-2.5-flash"
        assert call_kwargs.kwargs["contents"] == "user prompt"

    @patch("google.genai.Client")
    def test_complete_handles_none_text(self, mock_genai_client_cls):
        """response.text can be None when blocked by safety filters."""
        from veritail.llm.client import GeminiClient

        mock_response = MagicMock()
        mock_response.text = None
        mock_response.usage_metadata = None

        mock_client = mock_genai_client_cls.return_value
        mock_client.models.generate_content.return_value = mock_response

        client = GeminiClient(model="gemini-2.5-flash")
        result = client.complete("system", "user")

        assert result.content == ""
        assert result.input_tokens == 0
        assert result.output_tokens == 0

    @patch("google.genai.Client")
    def test_preflight_check_success(self, mock_genai_client_cls):
        from veritail.llm.client import GeminiClient

        client = GeminiClient(model="gemini-2.5-flash")
        client.preflight_check()
        mock_genai_client_cls.return_value.models.get.assert_called_once_with(
            model="gemini-2.5-flash",
        )

    @patch("google.genai.Client")
    def test_preflight_check_bad_key(self, mock_genai_client_cls):
        from veritail.llm.client import GeminiClient

        mock_genai_client_cls.return_value.models.get.side_effect = Exception(
            "API key not valid. Please pass a valid API key. [401]"
        )
        client = GeminiClient(model="gemini-2.5-flash")
        with pytest.raises(RuntimeError, match="Gemini API key is invalid"):
            client.preflight_check()

    @patch("google.genai.Client")
    def test_preflight_check_bad_model(self, mock_genai_client_cls):
        from veritail.llm.client import GeminiClient

        mock_genai_client_cls.return_value.models.get.side_effect = Exception(
            "models/gemini-nonexistent is not found [404]"
        )
        client = GeminiClient(model="gemini-nonexistent")
        with pytest.raises(RuntimeError, match="not found on Gemini"):
            client.preflight_check()

    @patch("google.genai.Client")
    def test_preflight_check_generic_error(self, mock_genai_client_cls):
        from veritail.llm.client import GeminiClient

        mock_genai_client_cls.return_value.models.get.side_effect = Exception(
            "network timeout"
        )
        client = GeminiClient(model="gemini-2.5-flash")
        with pytest.raises(RuntimeError, match="preflight check failed"):
            client.preflight_check()


@pytest.mark.skipif(HAS_ANTHROPIC, reason="anthropic is installed")
def test_anthropic_import_error_without_package():
    """AnthropicClient raises helpful ImportError when anthropic is missing."""
    from veritail.llm.client import AnthropicClient

    with pytest.raises(ImportError, match="pip install veritail\\[anthropic\\]"):
        AnthropicClient(model="claude-sonnet-4-5")


@pytest.mark.skipif(HAS_GENAI, reason="google-genai is installed")
def test_gemini_import_error_without_package():
    """GeminiClient raises helpful ImportError when google-genai is missing."""
    from veritail.llm.client import GeminiClient

    with pytest.raises(ImportError, match="pip install veritail\\[gemini\\]"):
        GeminiClient(model="gemini-2.5-flash")


class TestCreateLLMClient:
    @pytest.mark.skipif(not HAS_ANTHROPIC, reason="anthropic not installed")
    @patch("anthropic.Anthropic")
    def test_claude_model(self, mock_anthropic_cls):
        from veritail.llm.client import AnthropicClient

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

    @pytest.mark.skipif(not HAS_ANTHROPIC, reason="anthropic not installed")
    @patch("anthropic.Anthropic")
    def test_claude_ignores_base_url(self, mock_anthropic_cls):
        """Claude models always use Anthropic — base_url is ignored."""
        from veritail.llm.client import AnthropicClient

        client = create_llm_client(
            "claude-sonnet-4-5",
            base_url="http://localhost:11434/v1",
        )
        assert isinstance(client, AnthropicClient)

    @pytest.mark.skipif(not HAS_GENAI, reason="google-genai not installed")
    @patch("google.genai.Client")
    def test_gemini_model(self, mock_genai_client_cls):
        from veritail.llm.client import GeminiClient

        client = create_llm_client("gemini-2.5-flash")
        assert isinstance(client, GeminiClient)

    @pytest.mark.skipif(not HAS_GENAI, reason="google-genai not installed")
    @patch("google.genai.Client")
    def test_gemini_ignores_base_url(self, mock_genai_client_cls):
        """Gemini models always use native SDK — base_url is ignored."""
        from veritail.llm.client import GeminiClient

        client = create_llm_client(
            "gemini-2.5-flash",
            base_url="http://localhost:11434/v1",
        )
        assert isinstance(client, GeminiClient)
