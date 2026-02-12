"""Tests for LangfuseBackend (mocked)."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

try:
    import langfuse
    HAS_LANGFUSE = True
except ImportError:
    HAS_LANGFUSE = False

from veritail.types import JudgmentRecord, SearchResult


pytestmark = pytest.mark.skipif(
    not HAS_LANGFUSE,
    reason="langfuse not installed",
)


def _make_judgment() -> JudgmentRecord:
    return JudgmentRecord(
        query="running shoes",
        product=SearchResult(
            product_id="SKU-001",
            title="Nike Running Shoes",
            description="Classic shoes",
            category="Shoes",
            price=129.99,
            position=0,
        ),
        score=3,
        reasoning="Great match",
        attribute_verdict="match",
        model="claude-sonnet-4-5",
        experiment="test-exp",
        metadata={"input_tokens": 100, "output_tokens": 50},
    )


@patch("langfuse.Langfuse")
def test_log_judgment(mock_langfuse_cls):
    from veritail.backends.langfuse import LangfuseBackend

    mock_client = mock_langfuse_cls.return_value
    mock_trace = MagicMock()
    mock_client.trace.return_value = mock_trace

    backend = LangfuseBackend()
    backend.log_judgment(_make_judgment())

    mock_client.trace.assert_called_once()
    mock_trace.generation.assert_called_once()
    mock_trace.score.assert_called_once()

    # Verify score value
    score_call = mock_trace.score.call_args
    assert score_call.kwargs["value"] == 3
    assert score_call.kwargs["name"] == "relevance"


@patch("langfuse.Langfuse")
def test_log_experiment(mock_langfuse_cls):
    from veritail.backends.langfuse import LangfuseBackend

    mock_client = mock_langfuse_cls.return_value
    backend = LangfuseBackend()
    backend.log_experiment("test-exp", {"llm_model": "claude-sonnet-4-5"})

    mock_client.trace.assert_called_once()
