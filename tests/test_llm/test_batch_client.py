"""Tests for LLM batch client methods."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, Mock, patch

import pytest

from veritail.llm.client import (
    AnthropicClient,
    BatchRequest,
    GeminiClient,
    OpenAIClient,
)


def _make_batch_requests() -> list[BatchRequest]:
    return [
        BatchRequest(
            custom_id="req-0",
            system_prompt="You are a judge.",
            user_prompt="Rate this product.",
            max_tokens=512,
        ),
        BatchRequest(
            custom_id="req-1",
            system_prompt="You are a judge.",
            user_prompt="Rate this other product.",
            max_tokens=512,
        ),
    ]


class TestOpenAIBatchClient:
    def _make_client(self, base_url: str | None = None) -> OpenAIClient:
        with patch("openai.OpenAI"):
            client = OpenAIClient(model="gpt-4o", base_url=base_url)
        client._client = MagicMock()
        return client

    def test_supports_batch_true_without_base_url(self):
        client = self._make_client(base_url=None)
        assert client.supports_batch() is True

    def test_supports_batch_false_with_base_url(self):
        client = self._make_client(base_url="http://localhost:11434/v1")
        assert client.supports_batch() is False

    def test_submit_batch_creates_file_and_batch(self):
        client = self._make_client()
        client._client.files.create.return_value = Mock(id="file-123")
        client._client.batches.create.return_value = Mock(id="batch-456")

        batch_id = client.submit_batch(_make_batch_requests())

        assert batch_id == "batch-456"
        client._client.files.create.assert_called_once()
        call_kwargs = client._client.files.create.call_args[1]
        assert call_kwargs["purpose"] == "batch"

        # Verify JSONL content
        file_obj = call_kwargs["file"]
        content = file_obj.read().decode("utf-8")
        lines = [json.loads(line) for line in content.strip().split("\n")]
        assert len(lines) == 2
        assert lines[0]["custom_id"] == "req-0"
        assert lines[0]["body"]["model"] == "gpt-4o"
        assert lines[0]["method"] == "POST"
        assert lines[0]["url"] == "/v1/chat/completions"
        assert lines[1]["custom_id"] == "req-1"

        client._client.batches.create.assert_called_once_with(
            input_file_id="file-123",
            endpoint="/v1/chat/completions",
            completion_window="24h",
        )

    def test_poll_batch_in_progress(self):
        client = self._make_client()
        client._client.batches.retrieve.return_value = Mock(
            status="in_progress",
            request_counts=Mock(total=10, completed=3, failed=1),
        )

        status, completed, total = client.poll_batch("batch-456")
        assert status == "in_progress"
        assert completed == 4  # 3 completed + 1 failed
        assert total == 10

    def test_poll_batch_completed(self):
        client = self._make_client()
        client._client.batches.retrieve.return_value = Mock(
            status="completed",
            request_counts=Mock(total=10, completed=10, failed=0),
        )

        status, completed, total = client.poll_batch("batch-456")
        assert status == "completed"
        assert completed == 10
        assert total == 10

    def test_poll_batch_failed(self):
        client = self._make_client()
        client._client.batches.retrieve.return_value = Mock(
            status="failed",
            request_counts=Mock(total=10, completed=5, failed=5),
        )

        status, completed, total = client.poll_batch("batch-456")
        assert status == "failed"

    def test_retrieve_batch_results_success(self):
        client = self._make_client()

        client._client.batches.retrieve.return_value = Mock(
            output_file_id="file-out-789"
        )

        jsonl_lines = [
            json.dumps(
                {
                    "custom_id": "req-0",
                    "response": {
                        "status_code": 200,
                        "body": {
                            "choices": [
                                {"message": {"content": "SCORE: 3\nREASONING: Good"}}
                            ],
                            "usage": {"prompt_tokens": 100, "completion_tokens": 50},
                        },
                    },
                }
            ),
            json.dumps(
                {
                    "custom_id": "req-1",
                    "response": {
                        "status_code": 200,
                        "body": {
                            "choices": [
                                {"message": {"content": "SCORE: 2\nREASONING: OK"}}
                            ],
                            "usage": {"prompt_tokens": 90, "completion_tokens": 40},
                        },
                    },
                }
            ),
        ]
        client._client.files.content.return_value = Mock(text="\n".join(jsonl_lines))

        results = client.retrieve_batch_results("batch-456")
        assert len(results) == 2
        assert results[0].custom_id == "req-0"
        assert results[0].response is not None
        assert results[0].response.content == "SCORE: 3\nREASONING: Good"
        assert results[0].response.input_tokens == 100
        assert results[0].error is None
        assert results[1].custom_id == "req-1"
        assert results[1].response is not None
        assert results[1].response.content == "SCORE: 2\nREASONING: OK"

    def test_retrieve_batch_results_mixed_errors(self):
        client = self._make_client()

        client._client.batches.retrieve.return_value = Mock(
            output_file_id="file-out-789"
        )

        jsonl_lines = [
            json.dumps(
                {
                    "custom_id": "req-0",
                    "response": {
                        "status_code": 200,
                        "body": {
                            "choices": [{"message": {"content": "SCORE: 3"}}],
                            "usage": {"prompt_tokens": 100, "completion_tokens": 50},
                        },
                    },
                }
            ),
            json.dumps(
                {
                    "custom_id": "req-1",
                    "error": {"message": "Rate limit exceeded"},
                }
            ),
        ]
        client._client.files.content.return_value = Mock(text="\n".join(jsonl_lines))

        results = client.retrieve_batch_results("batch-456")
        assert len(results) == 2
        assert results[0].response is not None
        assert results[1].response is None
        assert results[1].error is not None

    def test_retrieve_batch_results_no_output_file(self):
        client = self._make_client()
        client._client.batches.retrieve.return_value = Mock(output_file_id=None)

        results = client.retrieve_batch_results("batch-456")
        assert results == []


class TestAnthropicBatchClient:
    def _make_client(self) -> AnthropicClient:
        with patch("anthropic.Anthropic"):
            client = AnthropicClient(model="claude-sonnet-4-5")
        client._client = MagicMock()
        return client

    def test_supports_batch_true(self):
        client = self._make_client()
        assert client.supports_batch() is True

    def test_submit_batch(self):
        client = self._make_client()
        client._client.messages.batches.create.return_value = Mock(id="msgbatch-123")

        batch_id = client.submit_batch(_make_batch_requests())

        assert batch_id == "msgbatch-123"
        call_kwargs = client._client.messages.batches.create.call_args[1]
        requests = call_kwargs["requests"]
        assert len(requests) == 2
        assert requests[0]["custom_id"] == "req-0"
        assert requests[0]["params"]["model"] == "claude-sonnet-4-5"

    def test_poll_batch_in_progress(self):
        client = self._make_client()
        client._client.messages.batches.retrieve.return_value = Mock(
            processing_status="in_progress",
            request_counts=Mock(
                processing=5, succeeded=3, errored=0, canceled=0, expired=0
            ),
        )

        status, completed, total = client.poll_batch("msgbatch-123")
        assert status == "in_progress"
        assert completed == 3
        assert total == 8

    def test_poll_batch_ended(self):
        client = self._make_client()
        client._client.messages.batches.retrieve.return_value = Mock(
            processing_status="ended",
            request_counts=Mock(
                processing=0, succeeded=8, errored=2, canceled=0, expired=0
            ),
        )

        status, completed, total = client.poll_batch("msgbatch-123")
        assert status == "completed"
        assert completed == 10
        assert total == 10

    def test_retrieve_results_succeeded(self):
        client = self._make_client()

        mock_result = Mock()
        mock_result.custom_id = "req-0"
        mock_result.result.type = "succeeded"
        mock_result.result.message.content = [Mock(text="SCORE: 3\nREASONING: Good")]
        mock_result.result.message.usage = Mock(input_tokens=100, output_tokens=50)

        client._client.messages.batches.results.return_value = [mock_result]

        results = client.retrieve_batch_results("msgbatch-123")
        assert len(results) == 1
        assert results[0].custom_id == "req-0"
        assert results[0].response is not None
        assert results[0].response.content == "SCORE: 3\nREASONING: Good"
        assert results[0].error is None

    def test_retrieve_results_errored(self):
        client = self._make_client()

        mock_result = Mock()
        mock_result.custom_id = "req-0"
        mock_result.result.type = "errored"

        client._client.messages.batches.results.return_value = [mock_result]

        results = client.retrieve_batch_results("msgbatch-123")
        assert len(results) == 1
        assert results[0].response is None
        assert results[0].error == "Request errored"


class TestGeminiBatchClient:
    def test_supports_batch_false(self):
        pytest.importorskip("google.genai")
        client = GeminiClient(model="gemini-2.5-flash")
        assert client.supports_batch() is False
