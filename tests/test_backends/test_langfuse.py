"""Tests for LangfuseBackend (mocked)."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from veritail.types import JudgmentRecord, SearchResult

HAS_LANGFUSE = False
_langfuse_skip_reason = "langfuse not installed"

try:
    import langfuse  # noqa: F401

    HAS_LANGFUSE = True
except ImportError:
    pass
except Exception as _exc:
    _langfuse_skip_reason = (
        f"langfuse import failed: {_exc}. "
        "This is likely a Langfuse SDK incompatibility with your Python version."
    )

pytestmark = pytest.mark.skipif(
    not HAS_LANGFUSE,
    reason=_langfuse_skip_reason,
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


@patch("veritail.backends.langfuse.Langfuse")
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

    # Verify full product data is stored in trace metadata
    trace_call = mock_client.trace.call_args
    product_data = trace_call.kwargs["metadata"]["product"]
    assert product_data["product_id"] == "SKU-001"
    assert product_data["title"] == "Nike Running Shoes"
    assert product_data["description"] == "Classic shoes"
    assert product_data["category"] == "Shoes"
    assert product_data["price"] == 129.99
    assert product_data["position"] == 0


@patch("veritail.backends.langfuse.Langfuse")
def test_log_experiment(mock_langfuse_cls):
    from veritail.backends.langfuse import LangfuseBackend

    mock_client = mock_langfuse_cls.return_value
    backend = LangfuseBackend()
    backend.log_experiment("test-exp", {"llm_model": "claude-sonnet-4-5"})

    mock_client.trace.assert_called_once()


@patch("veritail.backends.langfuse.Langfuse")
def test_get_judgments_skips_bad_trace(mock_langfuse_cls):
    """A trace that raises during processing is skipped; others still load."""
    import warnings

    from veritail.backends.langfuse import LangfuseBackend

    mock_client = mock_langfuse_cls.return_value

    # Two traces: first is good, second has bad metadata that causes an error
    good_trace = MagicMock()
    good_trace.id = "trace-1"
    good_trace.metadata = {
        "query": "shoes",
        "product": {
            "product_id": "SKU-1",
            "title": "Shoes",
            "description": "desc",
            "category": "Shoes",
            "price": 50.0,
            "position": 0,
        },
        "attribute_verdict": "match",
        "model": "test",
    }

    bad_trace = MagicMock()
    bad_trace.id = "trace-2"
    bad_trace.metadata = {"query": "broken", "product": "not-a-dict"}

    traces_response = MagicMock()
    traces_response.data = [good_trace, bad_trace]
    mock_client.fetch_traces.return_value = traces_response

    # Set up scores for the good trace
    good_score = MagicMock()
    good_score.name = "relevance"
    good_score.value = 3
    good_score.comment = "Great match"
    good_scores_response = MagicMock()
    good_scores_response.data = [good_score]

    bad_scores_response = MagicMock()
    bad_scores_response.data = []

    mock_client.fetch_scores.side_effect = [good_scores_response, bad_scores_response]

    backend = LangfuseBackend()

    with warnings.catch_warnings(record=True):
        warnings.simplefilter("always")
        judgments = backend.get_judgments("test-exp")

    # Good trace loaded, bad trace skipped
    assert len(judgments) == 1
    assert judgments[0].query == "shoes"
    assert judgments[0].score == 3
