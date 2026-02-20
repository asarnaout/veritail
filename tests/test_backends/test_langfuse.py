"""Tests for LangfuseBackend (mocked)."""

from __future__ import annotations

import warnings
from unittest.mock import MagicMock, patch

import pytest

from veritail.types import (
    CorrectionJudgment,
    JudgmentRecord,
    SearchResult,
    SuggestionJudgment,
)

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
def test_log_judgment(mock_langfuse_cls: MagicMock) -> None:
    from veritail.backends.langfuse import LangfuseBackend

    mock_client = mock_langfuse_cls.return_value
    mock_span = MagicMock()
    mock_generation = MagicMock()
    mock_client.start_span.return_value = mock_span
    mock_span.start_generation.return_value = mock_generation

    backend = LangfuseBackend()
    backend.log_judgment(_make_judgment())

    # Root span is created with product metadata
    mock_client.start_span.assert_called_once()
    span_call = mock_client.start_span.call_args
    assert span_call.kwargs["name"] == "veritail-judgment"
    product_data = span_call.kwargs["metadata"]["product"]
    assert product_data["product_id"] == "SKU-001"
    assert product_data["title"] == "Nike Running Shoes"
    assert product_data["description"] == "Classic shoes"
    assert product_data["category"] == "Shoes"
    assert product_data["price"] == 129.99
    assert product_data["position"] == 0

    # Generation is nested under the span and ended
    mock_span.start_generation.assert_called_once()
    gen_call = mock_span.start_generation.call_args
    assert gen_call.kwargs["name"] == "relevance-judgment"
    assert gen_call.kwargs["model"] == "claude-sonnet-4-5"
    assert gen_call.kwargs["output"] == "Great match"
    mock_generation.end.assert_called_once()
    mock_span.end.assert_called_once()

    # Trace-level input/output are set
    mock_span.update_trace.assert_called_once()
    trace_call = mock_span.update_trace.call_args
    assert trace_call.kwargs["input"] == {
        "query": "running shoes",
        "product_id": "SKU-001",
    }
    assert trace_call.kwargs["output"] == 3

    # Score is created
    mock_client.create_score.assert_called_once()
    score_call = mock_client.create_score.call_args
    assert score_call.kwargs["name"] == "relevance"
    assert score_call.kwargs["value"] == 3.0
    assert score_call.kwargs["comment"] == "Great match"


@patch("veritail.backends.langfuse.Langfuse")
def test_log_experiment(mock_langfuse_cls: MagicMock) -> None:
    from veritail.backends.langfuse import LangfuseBackend

    mock_client = mock_langfuse_cls.return_value
    mock_span = MagicMock()
    mock_client.start_span.return_value = mock_span

    backend = LangfuseBackend()
    backend.log_experiment("test-exp", {"llm_model": "claude-sonnet-4-5"})

    mock_client.start_span.assert_called_once()
    span_call = mock_client.start_span.call_args
    assert span_call.kwargs["name"] == "experiment-test-exp"
    assert span_call.kwargs["metadata"]["type"] == "experiment_registration"

    # Trace-level input is the config
    mock_span.update_trace.assert_called_once()
    trace_call = mock_span.update_trace.call_args
    assert trace_call.kwargs["input"] == {"llm_model": "claude-sonnet-4-5"}
    mock_span.end.assert_called_once()


@patch("veritail.backends.langfuse.Langfuse")
def test_get_judgments_returns_empty_with_warning(mock_langfuse_cls: MagicMock) -> None:
    """get_judgments emits a warning since Langfuse v3 removed fetch_traces."""
    from veritail.backends.langfuse import LangfuseBackend

    backend = LangfuseBackend()

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        judgments = backend.get_judgments("test-exp")

    assert judgments == []
    assert len(w) == 1
    assert "not supported" in str(w[0].message)


@patch("veritail.backends.langfuse.Langfuse")
def test_log_correction_judgment(mock_langfuse_cls: MagicMock) -> None:
    from veritail.backends.langfuse import LangfuseBackend

    mock_client = mock_langfuse_cls.return_value
    mock_span = MagicMock()
    mock_client.start_span.return_value = mock_span

    correction = CorrectionJudgment(
        original_query="runing shoes",
        corrected_query="running shoes",
        verdict="appropriate",
        reasoning="Fixed typo",
        model="claude-sonnet-4-5",
        experiment="test-exp",
    )

    backend = LangfuseBackend()
    backend.log_correction_judgment(correction)

    mock_client.start_span.assert_called_once()
    span_call = mock_client.start_span.call_args
    assert span_call.kwargs["metadata"]["verdict"] == "appropriate"

    # Trace-level input/output are set
    mock_span.update_trace.assert_called_once()
    trace_call = mock_span.update_trace.call_args
    assert trace_call.kwargs["input"] == {
        "original_query": "runing shoes",
        "corrected_query": "running shoes",
    }
    assert trace_call.kwargs["output"] == "appropriate"
    mock_span.end.assert_called_once()

    mock_client.create_score.assert_called_once()
    score_call = mock_client.create_score.call_args
    assert score_call.kwargs["name"] == "correction_appropriate"
    assert score_call.kwargs["value"] == 1.0


def _make_suggestion_judgment() -> SuggestionJudgment:
    return SuggestionJudgment(
        prefix="run",
        suggestions=["running shoes", "running shorts", "runner's watch"],
        relevance_score=3,
        diversity_score=2,
        flagged_suggestions=[],
        reasoning="Good suggestions",
        model="claude-sonnet-4-5",
        experiment="test-exp",
        metadata={"input_tokens": 80, "output_tokens": 40},
    )


@patch("veritail.backends.langfuse.Langfuse")
def test_log_suggestion_judgment(mock_langfuse_cls: MagicMock) -> None:
    from veritail.backends.langfuse import LangfuseBackend

    mock_client = mock_langfuse_cls.return_value
    mock_span = MagicMock()
    mock_generation = MagicMock()
    mock_client.start_span.return_value = mock_span
    mock_span.start_generation.return_value = mock_generation

    backend = LangfuseBackend()
    backend.log_suggestion_judgment(_make_suggestion_judgment())

    # Root span created with suggestion metadata
    mock_client.start_span.assert_called_once()
    span_call = mock_client.start_span.call_args
    assert span_call.kwargs["name"] == "veritail-suggestion-judgment"
    assert span_call.kwargs["metadata"]["prefix"] == "run"
    assert span_call.kwargs["metadata"]["suggestions"] == [
        "running shoes",
        "running shorts",
        "runner's watch",
    ]

    # Generation nested under span
    mock_span.start_generation.assert_called_once()
    gen_call = mock_span.start_generation.call_args
    assert gen_call.kwargs["name"] == "suggestion-judgment"
    assert gen_call.kwargs["model"] == "claude-sonnet-4-5"
    assert gen_call.kwargs["output"] == "Good suggestions"
    mock_generation.end.assert_called_once()
    mock_span.end.assert_called_once()

    # Trace-level input/output are set
    mock_span.update_trace.assert_called_once()
    trace_call = mock_span.update_trace.call_args
    assert trace_call.kwargs["input"] == {
        "prefix": "run",
        "suggestions": ["running shoes", "running shorts", "runner's watch"],
    }
    assert trace_call.kwargs["output"] == {
        "relevance_score": 3,
        "diversity_score": 2,
    }

    # Two scores created: relevance and diversity
    assert mock_client.create_score.call_count == 2
    score_calls = mock_client.create_score.call_args_list
    score_names = {c.kwargs["name"] for c in score_calls}
    assert score_names == {"autocomplete_relevance", "autocomplete_diversity"}

    for call in score_calls:
        if call.kwargs["name"] == "autocomplete_relevance":
            assert call.kwargs["value"] == 3.0
        elif call.kwargs["name"] == "autocomplete_diversity":
            assert call.kwargs["value"] == 2.0


@patch("veritail.backends.langfuse.Langfuse")
def test_log_experiment_sets_session_id(mock_langfuse_cls: MagicMock) -> None:
    from veritail.backends.langfuse import LangfuseBackend

    mock_client = mock_langfuse_cls.return_value
    mock_span = MagicMock()
    mock_client.start_span.return_value = mock_span

    backend = LangfuseBackend()

    # Before log_experiment, span.update_trace should not be called
    mock_span.update_trace.assert_not_called()

    backend.log_experiment("my-session", {"llm_model": "claude-sonnet-4-5"})

    # After log_experiment, span.update_trace is called with session_id
    mock_span.update_trace.assert_called_once()
    assert mock_span.update_trace.call_args.kwargs["session_id"] == "my-session"


@patch("veritail.backends.langfuse.Langfuse")
def test_suggestion_judgment_with_session_id(mock_langfuse_cls: MagicMock) -> None:
    from veritail.backends.langfuse import LangfuseBackend

    mock_client = mock_langfuse_cls.return_value
    mock_span = MagicMock()
    mock_generation = MagicMock()
    mock_client.start_span.return_value = mock_span
    mock_span.start_generation.return_value = mock_generation

    backend = LangfuseBackend()
    backend.log_experiment("ac-session", {"type": "autocomplete"})
    mock_span.update_trace.reset_mock()

    backend.log_suggestion_judgment(_make_suggestion_judgment())

    mock_span.update_trace.assert_called_once()
    assert mock_span.update_trace.call_args.kwargs["session_id"] == "ac-session"


@patch("veritail.backends.langfuse.Langfuse")
def test_correction_judgment_with_session_id(mock_langfuse_cls: MagicMock) -> None:
    from veritail.backends.langfuse import LangfuseBackend

    mock_client = mock_langfuse_cls.return_value
    mock_span = MagicMock()
    mock_client.start_span.return_value = mock_span

    correction = CorrectionJudgment(
        original_query="runing shoes",
        corrected_query="running shoes",
        verdict="appropriate",
        reasoning="Fixed typo",
        model="claude-sonnet-4-5",
        experiment="test-exp",
    )

    backend = LangfuseBackend()
    backend.log_experiment("corr-session", {"type": "search"})
    mock_span.update_trace.reset_mock()

    backend.log_correction_judgment(correction)

    mock_span.update_trace.assert_called_once()
    assert mock_span.update_trace.call_args.kwargs["session_id"] == "corr-session"
