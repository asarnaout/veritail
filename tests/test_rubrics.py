"""Tests for rubric content and expectations."""

from veritail.rubrics.ecommerce_default import SYSTEM_PROMPT, format_user_prompt
from veritail.types import SearchResult


def test_default_rubric_requires_brief_justification():
    assert "REASONING: <your concise justification in 1-3 sentences>" in SYSTEM_PROMPT
    assert "Do not include chain-of-thought." in SYSTEM_PROMPT


def _make_result() -> SearchResult:
    return SearchResult(
        product_id="SKU-001",
        title="Running Shoes",
        description="Classic running shoes",
        category="Shoes > Running",
        price=129.99,
        position=0,
    )


def test_format_user_prompt_without_correction():
    prompt = format_user_prompt("running shoes", _make_result())
    assert "## Search Query" in prompt
    assert "running shoes" in prompt
    assert "Original Search Query" not in prompt
    assert "Corrected Search Query" not in prompt


def test_format_user_prompt_with_correction():
    prompt = format_user_prompt(
        "runnign shoes",
        _make_result(),
        corrected_query="running shoes",
    )
    assert "## Original Search Query" in prompt
    assert "runnign shoes" in prompt
    assert "## Corrected Search Query (used for retrieval)" in prompt
    assert "running shoes" in prompt
    # Should NOT have the plain "## Search Query" header
    assert "## Search Query\n" not in prompt


def test_format_user_prompt_with_overlay():
    prompt = format_user_prompt(
        "commercial fryer",
        _make_result(),
        overlay="Ovens, fryers, and griddles for commercial kitchens.",
    )
    assert "## Domain-Specific Scoring Guidance" in prompt
    assert "Ovens, fryers, and griddles" in prompt
    # Overlay section should appear before Product section
    overlay_pos = prompt.index("## Domain-Specific Scoring Guidance")
    product_pos = prompt.index("## Product")
    assert overlay_pos < product_pos


def test_format_user_prompt_without_overlay():
    prompt = format_user_prompt("running shoes", _make_result())
    assert "## Domain-Specific Scoring Guidance" not in prompt


def test_format_user_prompt_with_correction_and_overlay():
    prompt = format_user_prompt(
        "runnign shoes",
        _make_result(),
        corrected_query="running shoes",
        overlay="Footwear scoring guidance.",
    )
    assert "## Original Search Query" in prompt
    assert "## Domain-Specific Scoring Guidance" in prompt
    assert "Footwear scoring guidance." in prompt
