"""LLM client abstraction for multiple providers."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class LLMResponse:
    """Raw response from an LLM provider."""

    content: str
    model: str
    input_tokens: int
    output_tokens: int


class LLMClient(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    def complete(
        self, system_prompt: str, user_prompt: str, *, max_tokens: int = 1024
    ) -> LLMResponse:
        """Send a prompt to the LLM and get a response."""
        ...

    @abstractmethod
    def preflight_check(self) -> None:
        """Validate API key and model availability.

        Raises ``RuntimeError`` with a user-friendly message on failure.
        """
        ...


class AnthropicClient(LLMClient):
    """LLM client using the Anthropic API (Claude models)."""

    def __init__(self, model: str = "claude-sonnet-4-5") -> None:
        import anthropic

        self._client = anthropic.Anthropic()
        self._model = model

    def complete(
        self, system_prompt: str, user_prompt: str, *, max_tokens: int = 1024
    ) -> LLMResponse:
        response = self._client.messages.create(
            model=self._model,
            max_tokens=max_tokens,
            system=[
                {
                    "type": "text",
                    "text": system_prompt,
                    "cache_control": {"type": "ephemeral"},
                }
            ],
            messages=[{"role": "user", "content": user_prompt}],
        )
        return LLMResponse(
            content=response.content[0].text,  # type: ignore[union-attr]
            model=self._model,
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
        )

    def preflight_check(self) -> None:
        import anthropic

        try:
            self._client.models.retrieve(model_id=self._model)
        except anthropic.AuthenticationError as exc:
            raise RuntimeError(
                "Anthropic API key is invalid. "
                "Check your ANTHROPIC_API_KEY environment variable."
            ) from exc
        except anthropic.NotFoundError as exc:
            raise RuntimeError(
                f"Model '{self._model}' not found on Anthropic. "
                "Check the --llm-model value."
            ) from exc


class OpenAIClient(LLMClient):
    """LLM client using the OpenAI API (GPT models or OpenAI-compatible APIs).

    Works with any OpenAI-compatible endpoint by setting ``base_url``.
    This includes local model servers such as Ollama, vLLM, and LM Studio.
    """

    def __init__(
        self,
        model: str = "gpt-4o",
        base_url: str | None = None,
        api_key: str | None = None,
    ) -> None:
        import openai

        self._client = openai.OpenAI(base_url=base_url, api_key=api_key)
        self._model = model

    def complete(
        self, system_prompt: str, user_prompt: str, *, max_tokens: int = 1024
    ) -> LLMResponse:
        response = self._client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=max_tokens,
        )
        choice = response.choices[0]
        usage = response.usage
        return LLMResponse(
            content=choice.message.content or "",
            model=self._model,
            input_tokens=usage.prompt_tokens if usage else 0,
            output_tokens=usage.completion_tokens if usage else 0,
        )

    def preflight_check(self) -> None:
        import openai

        try:
            self._client.models.retrieve(self._model)
        except openai.AuthenticationError as exc:
            raise RuntimeError(
                "OpenAI API key is invalid. "
                "Check your OPENAI_API_KEY environment variable."
            ) from exc
        except openai.NotFoundError as exc:
            raise RuntimeError(
                f"Model '{self._model}' not found on OpenAI. "
                "Check the --llm-model value."
            ) from exc
        except Exception:
            # OpenAI-compatible APIs may not implement the models endpoint;
            # skip validation and let the first real call surface errors.
            pass


def create_llm_client(
    model: str,
    base_url: str | None = None,
    api_key: str | None = None,
) -> LLMClient:
    """Create an LLM client based on the model name.

    Models starting with 'claude' use the Anthropic API.
    All other models use the OpenAI API
    (also works with OpenAI-compatible local models).

    When *base_url* is provided, the OpenAI client is pointed at that
    endpoint regardless of model name (unless it starts with 'claude').
    This allows connecting to Ollama, vLLM, LM Studio, or any other
    OpenAI-compatible server.
    """
    if model.startswith("claude"):
        return AnthropicClient(model=model)
    return OpenAIClient(model=model, base_url=base_url, api_key=api_key)
