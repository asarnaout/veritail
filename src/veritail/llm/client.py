"""LLM client abstraction for multiple providers."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass
class LLMResponse:
    """Raw response from an LLM provider."""

    content: str
    model: str
    input_tokens: int
    output_tokens: int


@dataclass
class BatchRequest:
    """A single request to include in a batch submission."""

    custom_id: str
    system_prompt: str
    user_prompt: str
    max_tokens: int = 1024


@dataclass
class BatchResult:
    """Result for a single request from a completed batch."""

    custom_id: str
    response: LLMResponse | None  # None if request failed
    error: str | None = None


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

    def supports_batch(self) -> bool:
        """Return True if this provider supports batch operations."""
        return False

    def submit_batch(self, requests: list[BatchRequest]) -> str:
        """Submit a batch of requests. Returns a batch ID."""
        raise NotImplementedError("This provider does not support batch operations.")

    def poll_batch(self, batch_id: str) -> tuple[str, int, int]:
        """Poll batch status. Returns (status, completed_count, total_count).

        Status is one of: "in_progress", "completed", "failed", "expired".
        """
        raise NotImplementedError("This provider does not support batch operations.")

    def retrieve_batch_results(self, batch_id: str) -> list[BatchResult]:
        """Retrieve results from a completed batch."""
        raise NotImplementedError("This provider does not support batch operations.")


class AnthropicClient(LLMClient):
    """LLM client using the Anthropic API (Claude models).

    Requires the ``anthropic`` package::

        pip install veritail[anthropic]
    """

    def __init__(self, model: str = "claude-sonnet-4-5") -> None:
        try:
            import anthropic
        except ImportError:
            raise ImportError(
                "The anthropic package is required for Claude models. "
                "Install it with: pip install veritail[anthropic]"
            ) from None

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

    def supports_batch(self) -> bool:
        return True

    def submit_batch(self, requests: list[BatchRequest]) -> str:
        request_dicts = [
            {
                "custom_id": req.custom_id,
                "params": {
                    "model": self._model,
                    "max_tokens": req.max_tokens,
                    "system": [
                        {
                            "type": "text",
                            "text": req.system_prompt,
                            "cache_control": {"type": "ephemeral"},
                        }
                    ],
                    "messages": [{"role": "user", "content": req.user_prompt}],
                },
            }
            for req in requests
        ]
        batch = self._client.messages.batches.create(requests=request_dicts)  # type: ignore[arg-type]
        return batch.id

    def poll_batch(self, batch_id: str) -> tuple[str, int, int]:
        batch = self._client.messages.batches.retrieve(batch_id)
        raw_status = batch.processing_status
        if raw_status == "ended":
            status = "completed"
        else:
            status = "in_progress"
        counts = batch.request_counts
        completed = counts.succeeded + counts.errored + counts.canceled + counts.expired
        total = completed + counts.processing
        return status, completed, total

    def retrieve_batch_results(self, batch_id: str) -> list[BatchResult]:
        results: list[BatchResult] = []
        for entry in self._client.messages.batches.results(batch_id):
            custom_id = entry.custom_id
            result = entry.result
            if result.type == "succeeded":
                message = result.message
                text = message.content[0].text if message.content else ""  # type: ignore[union-attr]
                usage = message.usage
                results.append(
                    BatchResult(
                        custom_id=custom_id,
                        response=LLMResponse(
                            content=text,
                            model=self._model,
                            input_tokens=usage.input_tokens if usage else 0,
                            output_tokens=usage.output_tokens if usage else 0,
                        ),
                    )
                )
            else:
                results.append(
                    BatchResult(
                        custom_id=custom_id,
                        response=None,
                        error=f"Request {result.type}",
                    )
                )
        return results


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
        self._base_url = base_url

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

    def supports_batch(self) -> bool:
        return self._base_url is None

    def submit_batch(self, requests: list[BatchRequest]) -> str:
        import io
        import json

        lines = []
        for req in requests:
            line = json.dumps(
                {
                    "custom_id": req.custom_id,
                    "method": "POST",
                    "url": "/v1/chat/completions",
                    "body": {
                        "model": self._model,
                        "messages": [
                            {"role": "system", "content": req.system_prompt},
                            {"role": "user", "content": req.user_prompt},
                        ],
                        "max_tokens": req.max_tokens,
                    },
                }
            )
            lines.append(line)

        jsonl_bytes = ("\n".join(lines) + "\n").encode("utf-8")
        file_obj = io.BytesIO(jsonl_bytes)
        file_obj.name = "batch_input.jsonl"

        uploaded = self._client.files.create(file=file_obj, purpose="batch")
        batch = self._client.batches.create(
            input_file_id=uploaded.id,
            endpoint="/v1/chat/completions",
            completion_window="24h",
        )
        return batch.id

    def poll_batch(self, batch_id: str) -> tuple[str, int, int]:
        batch = self._client.batches.retrieve(batch_id)
        raw_status = batch.status
        if raw_status in ("validating", "in_progress", "finalizing"):
            status = "in_progress"
        elif raw_status == "completed":
            status = "completed"
        elif raw_status in ("failed", "cancelled", "cancelling"):
            status = "failed"
        elif raw_status == "expired":
            status = "expired"
        else:
            status = "in_progress"

        counts = batch.request_counts
        if counts:
            completed = (counts.completed or 0) + (counts.failed or 0)
            total = counts.total or 0
        else:
            completed = 0
            total = 0
        return status, completed, total

    def retrieve_batch_results(self, batch_id: str) -> list[BatchResult]:
        import json

        batch = self._client.batches.retrieve(batch_id)
        if not batch.output_file_id:
            return []

        content = self._client.files.content(batch.output_file_id)
        results: list[BatchResult] = []
        for line in content.text.strip().split("\n"):
            if not line.strip():
                continue
            entry = json.loads(line)
            custom_id = entry["custom_id"]
            error_body = entry.get("error")
            response_body = entry.get("response")

            if error_body:
                results.append(
                    BatchResult(
                        custom_id=custom_id,
                        response=None,
                        error=str(error_body),
                    )
                )
                continue

            if response_body and response_body.get("status_code") == 200:
                body = response_body["body"]
                choice = body["choices"][0]
                usage = body.get("usage", {})
                results.append(
                    BatchResult(
                        custom_id=custom_id,
                        response=LLMResponse(
                            content=choice["message"]["content"] or "",
                            model=self._model,
                            input_tokens=usage.get("prompt_tokens", 0),
                            output_tokens=usage.get("completion_tokens", 0),
                        ),
                    )
                )
            else:
                status_code = (
                    response_body.get("status_code") if response_body else None
                )
                results.append(
                    BatchResult(
                        custom_id=custom_id,
                        response=None,
                        error=f"Request failed with status {status_code}",
                    )
                )

        return results


class GeminiClient(LLMClient):
    """LLM client using the Google Gemini API.

    Requires the ``google-genai`` package::

        pip install veritail[gemini]

    The API key is read from the ``GEMINI_API_KEY`` or ``GOOGLE_API_KEY``
    environment variable, or can be passed explicitly.
    """

    def __init__(self, model: str = "gemini-2.5-flash") -> None:
        try:
            from google import genai
        except ImportError:
            raise ImportError(
                "The google-genai package is required for Gemini models. "
                "Install it with: pip install veritail[gemini]"
            ) from None

        self._genai: Any = genai
        self._client: Any = genai.Client()
        self._model = model

    def complete(
        self, system_prompt: str, user_prompt: str, *, max_tokens: int = 1024
    ) -> LLMResponse:
        from google.genai import types

        response = self._client.models.generate_content(
            model=self._model,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                max_output_tokens=max_tokens,
            ),
            contents=user_prompt,
        )
        text: str = response.text or ""
        usage = response.usage_metadata
        return LLMResponse(
            content=text,
            model=self._model,
            input_tokens=usage.prompt_token_count if usage else 0,
            output_tokens=usage.candidates_token_count if usage else 0,
        )

    def preflight_check(self) -> None:
        try:
            self._client.models.get(
                model=self._model,
            )
        except Exception as exc:
            msg = str(exc).lower()
            if "api key not valid" in msg or "401" in msg:
                raise RuntimeError(
                    "Gemini API key is invalid. "
                    "Check your GEMINI_API_KEY or GOOGLE_API_KEY "
                    "environment variable."
                ) from exc
            if "not found" in msg or "404" in msg:
                raise RuntimeError(
                    f"Model '{self._model}' not found on Gemini. "
                    "Check the --llm-model value."
                ) from exc
            raise RuntimeError(f"Gemini preflight check failed: {exc}") from exc

    def supports_batch(self) -> bool:
        return False


def create_llm_client(
    model: str,
    base_url: str | None = None,
    api_key: str | None = None,
) -> LLMClient:
    """Create an LLM client based on the model name.

    Models starting with 'claude' use the Anthropic API.
    Models starting with 'gemini' use the Google Gemini API.
    All other models use the OpenAI API
    (also works with OpenAI-compatible local models).

    When *base_url* is provided, the OpenAI client is pointed at that
    endpoint regardless of model name (unless it starts with 'claude'
    or 'gemini').  This allows connecting to Ollama, vLLM, LM Studio,
    or any other OpenAI-compatible server.
    """
    if model.startswith("claude"):
        return AnthropicClient(model=model)
    if model.startswith("gemini"):
        return GeminiClient(model=model)
    return OpenAIClient(model=model, base_url=base_url, api_key=api_key)
