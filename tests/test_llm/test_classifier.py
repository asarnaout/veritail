"""Tests for LLM query type classifier."""

from __future__ import annotations

from unittest.mock import Mock

from veritail.llm.classifier import (
    CLASSIFICATION_SYSTEM_PROMPT,
    build_classification_system_prompt,
    classify_query,
    classify_query_type,
    parse_classification_response,
    parse_classification_with_overlay,
)
from veritail.llm.client import LLMClient, LLMResponse


def _make_client(content: str) -> LLMClient:
    client = Mock(spec=LLMClient)
    client.complete.return_value = LLMResponse(
        content=content, model="test", input_tokens=10, output_tokens=10
    )
    return client


class TestClassifyQueryType:
    def test_navigational(self) -> None:
        client = _make_client("QUERY_TYPE: navigational")
        assert classify_query_type(client, "nike air max 90") == "navigational"

    def test_broad(self) -> None:
        client = _make_client("QUERY_TYPE: broad")
        assert classify_query_type(client, "running shoes") == "broad"

    def test_long_tail(self) -> None:
        client = _make_client("QUERY_TYPE: long_tail")
        assert classify_query_type(client, "gfci outlet 20 amp white") == "long_tail"

    def test_attribute(self) -> None:
        client = _make_client("QUERY_TYPE: attribute")
        assert classify_query_type(client, "red running shoes") == "attribute"

    def test_case_insensitive_parsing(self) -> None:
        client = _make_client("query_type: Broad")
        assert classify_query_type(client, "shoes") == "broad"

    def test_invalid_type_returns_none(self) -> None:
        client = _make_client("QUERY_TYPE: unknown_type")
        assert classify_query_type(client, "shoes") is None

    def test_unparseable_response_returns_none(self) -> None:
        client = _make_client("I think this is a broad query.")
        assert classify_query_type(client, "shoes") is None

    def test_llm_error_returns_none(self) -> None:
        client = Mock(spec=LLMClient)
        client.complete.side_effect = RuntimeError("API down")
        assert classify_query_type(client, "shoes") is None

    def test_context_included_in_prompt(self) -> None:
        client = _make_client("QUERY_TYPE: broad")
        classify_query_type(client, "shoes", context="BBQ restaurant")
        system_prompt = client.complete.call_args[0][0]
        assert "BBQ restaurant" in system_prompt
        assert CLASSIFICATION_SYSTEM_PROMPT in system_prompt

    def test_vertical_included_in_prompt(self) -> None:
        client = _make_client("QUERY_TYPE: broad")
        classify_query_type(client, "shoes", vertical="## Vertical: Foodservice")
        system_prompt = client.complete.call_args[0][0]
        assert "Foodservice" in system_prompt

    def test_max_tokens_is_96(self) -> None:
        client = _make_client("QUERY_TYPE: broad")
        classify_query_type(client, "shoes")
        call_kwargs = client.complete.call_args
        assert call_kwargs[1]["max_tokens"] == 96


class TestParseClassificationResponse:
    def test_valid_types(self) -> None:
        result = parse_classification_response("QUERY_TYPE: navigational")
        assert result == "navigational"
        assert parse_classification_response("QUERY_TYPE: broad") == "broad"
        assert parse_classification_response("QUERY_TYPE: long_tail") == "long_tail"
        assert parse_classification_response("QUERY_TYPE: attribute") == "attribute"

    def test_case_insensitive(self) -> None:
        assert parse_classification_response("query_type: BROAD") == "broad"

    def test_invalid_type(self) -> None:
        assert parse_classification_response("QUERY_TYPE: unknown") is None

    def test_no_match(self) -> None:
        assert parse_classification_response("This is broad.") is None


class TestBuildClassificationSystemPrompt:
    def test_no_context_or_vertical(self) -> None:
        prompt = build_classification_system_prompt()
        assert prompt == CLASSIFICATION_SYSTEM_PROMPT

    def test_context_prepended(self) -> None:
        prompt = build_classification_system_prompt(context="BBQ supplier")
        assert prompt.startswith("## Business Context\nBBQ supplier")
        assert CLASSIFICATION_SYSTEM_PROMPT in prompt

    def test_vertical_prepended(self) -> None:
        prompt = build_classification_system_prompt(vertical="## Vertical: Food")
        assert "## Vertical: Food" in prompt
        assert CLASSIFICATION_SYSTEM_PROMPT in prompt

    def test_context_before_vertical(self) -> None:
        prompt = build_classification_system_prompt(
            context="BBQ supplier", vertical="## Vertical: Food"
        )
        ctx_pos = prompt.index("BBQ supplier")
        vert_pos = prompt.index("## Vertical: Food")
        assert ctx_pos < vert_pos


_OVERLAY_KEYS = {
    "hot_side": "Cooking equipment: ovens, fryers, griddles",
    "cold_side": "Refrigeration and ice machines",
}


class TestParseClassificationWithOverlay:
    def test_both_type_and_overlay(self) -> None:
        content = "QUERY_TYPE: broad\nOVERLAY: hot_side"
        qtype, overlay = parse_classification_with_overlay(content, _OVERLAY_KEYS)
        assert qtype == "broad"
        assert overlay == "hot_side"

    def test_type_only_no_overlay_keys(self) -> None:
        content = "QUERY_TYPE: navigational"
        qtype, overlay = parse_classification_with_overlay(content, None)
        assert qtype == "navigational"
        assert overlay is None

    def test_invalid_overlay_key(self) -> None:
        content = "QUERY_TYPE: broad\nOVERLAY: nonexistent"
        qtype, overlay = parse_classification_with_overlay(content, _OVERLAY_KEYS)
        assert qtype == "broad"
        assert overlay is None

    def test_overlay_case_insensitive(self) -> None:
        content = "QUERY_TYPE: broad\noverlay: Cold_Side"
        qtype, overlay = parse_classification_with_overlay(content, _OVERLAY_KEYS)
        assert overlay == "cold_side"

    def test_none_overlay_returns_none(self) -> None:
        content = "QUERY_TYPE: broad\nOVERLAY: none"
        qtype, overlay = parse_classification_with_overlay(content, _OVERLAY_KEYS)
        assert qtype == "broad"
        assert overlay is None

    def test_no_type_but_overlay_present(self) -> None:
        content = "I think this is hot side"
        qtype, overlay = parse_classification_with_overlay(content, _OVERLAY_KEYS)
        assert qtype is None
        assert overlay is None


class TestClassifyQuery:
    def test_without_overlay_keys_delegates(self) -> None:
        client = _make_client("QUERY_TYPE: broad")
        qtype, overlay = classify_query(client, "shoes")
        assert qtype == "broad"
        assert overlay is None

    def test_with_overlay_keys(self) -> None:
        client = _make_client("QUERY_TYPE: broad\nOVERLAY: hot_side")
        qtype, overlay = classify_query(
            client, "commercial fryer", overlay_keys=_OVERLAY_KEYS
        )
        assert qtype == "broad"
        assert overlay == "hot_side"

    def test_overlay_section_in_prompt(self) -> None:
        client = _make_client("QUERY_TYPE: broad\nOVERLAY: hot_side")
        classify_query(client, "fryer", overlay_keys=_OVERLAY_KEYS)
        system_prompt = client.complete.call_args[0][0]
        assert "## Overlay Classification" in system_prompt
        assert "hot_side" in system_prompt
        assert "cold_side" in system_prompt

    def test_overlay_prompt_includes_none_with_bias(self) -> None:
        client = _make_client("QUERY_TYPE: broad\nOVERLAY: none")
        classify_query(client, "restaurant insurance", overlay_keys=_OVERLAY_KEYS)
        system_prompt = client.complete.call_args[0][0]
        assert "|none>" in system_prompt
        assert "partially related" in system_prompt

    def test_overlay_none_returns_none(self) -> None:
        client = _make_client("QUERY_TYPE: broad\nOVERLAY: none")
        qtype, overlay = classify_query(
            client, "restaurant insurance", overlay_keys=_OVERLAY_KEYS
        )
        assert qtype == "broad"
        assert overlay is None

    def test_llm_error_returns_none_none(self) -> None:
        client = Mock(spec=LLMClient)
        client.complete.side_effect = RuntimeError("API down")
        qtype, overlay = classify_query(client, "fryer", overlay_keys=_OVERLAY_KEYS)
        assert qtype is None
        assert overlay is None
