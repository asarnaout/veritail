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
    def complete(self, system_prompt: str, user_prompt: str) -> LLMResponse:
        """Send a prompt to the LLM and get a response."""
        ...


class AnthropicClient(LLMClient):
    """LLM client using the Anthropic API (Claude models)."""

    def __init__(self, model: str = "claude-sonnet-4-5") -> None:
        import anthropic

        self._client = anthropic.Anthropic()
        self._model = model

    def complete(self, system_prompt: str, user_prompt: str) -> LLMResponse:
        response = self._client.messages.create(
            model=self._model,
            max_tokens=1024,
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


class OpenAIClient(LLMClient):
    """LLM client using the OpenAI API (GPT models or OpenAI-compatible APIs)."""

    def __init__(self, model: str = "gpt-4o") -> None:
        import openai

        self._client = openai.OpenAI()
        self._model = model

    def complete(self, system_prompt: str, user_prompt: str) -> LLMResponse:
        response = self._client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=1024,
        )
        choice = response.choices[0]
        usage = response.usage
        return LLMResponse(
            content=choice.message.content or "",
            model=self._model,
            input_tokens=usage.prompt_tokens if usage else 0,
            output_tokens=usage.completion_tokens if usage else 0,
        )


def create_llm_client(model: str) -> LLMClient:
    """Create an LLM client based on the model name.

    Models starting with 'claude' use the Anthropic API.
    All other models use the OpenAI API
    (also works with OpenAI-compatible local models).
    """
    if model.startswith("claude"):
        return AnthropicClient(model=model)
    return OpenAIClient(model=model)
