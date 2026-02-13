"""Tests for the verticals module."""

from __future__ import annotations

import pytest

from veritail.verticals import (
    ELECTRONICS,
    FASHION,
    FOODSERVICE,
    INDUSTRIAL,
    _BUILTIN_VERTICALS,
    load_vertical,
)


class TestBuiltinVerticals:
    @pytest.mark.parametrize("name", ["foodservice", "industrial", "electronics", "fashion"])
    def test_builtin_loads(self, name):
        result = load_vertical(name)
        assert f"## Vertical:" in result
        assert "Scoring considerations" in result

    @pytest.mark.parametrize("name,constant", [
        ("foodservice", FOODSERVICE),
        ("industrial", INDUSTRIAL),
        ("electronics", ELECTRONICS),
        ("fashion", FASHION),
    ])
    def test_builtin_returns_constant(self, name, constant):
        assert load_vertical(name) is constant

    @pytest.mark.parametrize("name", ["foodservice", "industrial", "electronics", "fashion"])
    def test_builtin_min_length(self, name):
        assert len(load_vertical(name)) > 100

    def test_registry_has_all_four(self):
        assert set(_BUILTIN_VERTICALS.keys()) == {"foodservice", "industrial", "electronics", "fashion"}


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
        with pytest.raises(FileNotFoundError, match="electronics.*fashion.*foodservice.*industrial"):
            load_vertical("nonexistent")
