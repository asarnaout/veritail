"""Tests for the verticals module."""

from __future__ import annotations

import pytest

from veritail.verticals import (
    AUTOMOTIVE,
    BEAUTY,
    ELECTRONICS,
    FASHION,
    FOODSERVICE,
    GROCERIES,
    INDUSTRIAL,
    MARKETPLACE,
    MEDICAL,
    _BUILTIN_VERTICALS,
    load_vertical,
)


ALL_BUILTINS = [
    "automotive",
    "beauty",
    "electronics",
    "fashion",
    "foodservice",
    "groceries",
    "industrial",
    "marketplace",
    "medical",
]


class TestBuiltinVerticals:
    @pytest.mark.parametrize("name", ALL_BUILTINS)
    def test_builtin_loads(self, name):
        result = load_vertical(name)
        assert f"## Vertical:" in result
        assert "Scoring considerations" in result

    @pytest.mark.parametrize("name,constant", [
        ("automotive", AUTOMOTIVE),
        ("beauty", BEAUTY),
        ("electronics", ELECTRONICS),
        ("fashion", FASHION),
        ("foodservice", FOODSERVICE),
        ("groceries", GROCERIES),
        ("industrial", INDUSTRIAL),
        ("marketplace", MARKETPLACE),
        ("medical", MEDICAL),
    ])
    def test_builtin_returns_constant(self, name, constant):
        assert load_vertical(name) is constant

    @pytest.mark.parametrize("name", ALL_BUILTINS)
    def test_builtin_min_length(self, name):
        assert len(load_vertical(name)) > 100

    @pytest.mark.parametrize("name", [
        "Automotive", "BEAUTY", "Electronics", "FASHION", "Foodservice",
        "GROCERIES", "Industrial", "MARKETPLACE", "Medical",
    ])
    def test_builtin_case_insensitive(self, name):
        result = load_vertical(name)
        assert "## Vertical:" in result

    def test_registry_has_all_nine(self):
        assert set(_BUILTIN_VERTICALS.keys()) == set(ALL_BUILTINS)


class TestCustomVertical:
    def test_load_from_file(self, tmp_path):
        custom = tmp_path / "my_vertical.txt"
        custom.write_text("## Vertical: Custom\nCustom scoring guidance.", encoding="utf-8")

        result = load_vertical(str(custom))
        assert "Custom scoring guidance" in result

    def test_file_trailing_whitespace_stripped(self, tmp_path):
        custom = tmp_path / "v.txt"
        custom.write_text("content\n\n\n", encoding="utf-8")

        result = load_vertical(str(custom))
        assert result == "content"


class TestUnknownVertical:
    def test_unknown_raises_file_not_found(self):
        with pytest.raises(FileNotFoundError, match="Unknown vertical 'nonexistent'"):
            load_vertical("nonexistent")

    def test_error_lists_available(self):
        with pytest.raises(FileNotFoundError, match="automotive.*beauty.*electronics.*fashion.*foodservice.*groceries.*industrial.*marketplace.*medical"):
            load_vertical("nonexistent")
