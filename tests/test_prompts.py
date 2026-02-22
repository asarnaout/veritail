"""Tests for the prompt loading utility."""

from __future__ import annotations

import pytest

from veritail.prompts import load_prompt


class TestLoadPrompt:
    """Tests for load_prompt()."""

    def test_loads_existing_prompt(self) -> None:
        """load_prompt returns stripped string content."""
        # Use any prompt file that will exist after extraction
        content = load_prompt("rubrics/ecommerce_default.md")
        assert isinstance(content, str)
        assert len(content) > 0

    def test_content_is_stripped(self) -> None:
        """Loaded content has no leading/trailing whitespace."""
        content = load_prompt("rubrics/ecommerce_default.md")
        assert content == content.strip()

    def test_missing_file_raises(self) -> None:
        """load_prompt raises FileNotFoundError for missing files."""
        with pytest.raises(FileNotFoundError):
            load_prompt("nonexistent/file.md")

    def test_caching(self) -> None:
        """Repeated calls return the same object (lru_cache)."""
        a = load_prompt("rubrics/ecommerce_default.md")
        b = load_prompt("rubrics/ecommerce_default.md")
        assert a is b
