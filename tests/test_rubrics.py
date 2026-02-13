"""Tests for rubric content and expectations."""

from veritail.rubrics.ecommerce_default import SYSTEM_PROMPT


def test_default_rubric_requires_brief_justification():
    assert "REASONING: <your concise justification in 1-3 sentences>" in SYSTEM_PROMPT
    assert "Do not include chain-of-thought." in SYSTEM_PROMPT
