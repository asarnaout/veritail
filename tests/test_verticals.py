"""Tests for the verticals module."""

from __future__ import annotations

import pytest

from veritail.types import VerticalContext
from veritail.verticals import (
    _BUILTIN_VERTICALS,
    AUTOMOTIVE,
    BEAUTY,
    ELECTRONICS,
    FASHION,
    FOODSERVICE,
    FURNITURE,
    GROCERIES,
    HOME_IMPROVEMENT,
    INDUSTRIAL,
    MARKETPLACE,
    MEDICAL,
    OFFICE_SUPPLIES,
    PET_SUPPLIES,
    SPORTING_GOODS,
    load_vertical,
)

ALL_BUILTINS = [
    "automotive",
    "beauty",
    "electronics",
    "fashion",
    "foodservice",
    "furniture",
    "groceries",
    "home-improvement",
    "industrial",
    "marketplace",
    "medical",
    "office-supplies",
    "pet-supplies",
    "sporting-goods",
]


class TestBuiltinVerticals:
    @pytest.mark.parametrize("name", ALL_BUILTINS)
    def test_builtin_loads(self, name):
        result = load_vertical(name)
        assert isinstance(result, VerticalContext)
        assert "## Vertical:" in result.core
        assert "Scoring considerations" in result.core

    @pytest.mark.parametrize(
        "name,constant",
        [
            ("automotive", AUTOMOTIVE),
            ("beauty", BEAUTY),
            ("electronics", ELECTRONICS),
            ("fashion", FASHION),
            ("foodservice", FOODSERVICE),
            ("furniture", FURNITURE),
            ("groceries", GROCERIES),
            ("home-improvement", HOME_IMPROVEMENT),
            ("industrial", INDUSTRIAL),
            ("marketplace", MARKETPLACE),
            ("medical", MEDICAL),
            ("office-supplies", OFFICE_SUPPLIES),
            ("pet-supplies", PET_SUPPLIES),
            ("sporting-goods", SPORTING_GOODS),
        ],
    )
    def test_builtin_returns_constant(self, name, constant):
        assert load_vertical(name) is constant

    @pytest.mark.parametrize("name", ALL_BUILTINS)
    def test_builtin_min_length(self, name):
        assert len(load_vertical(name).core) > 100

    @pytest.mark.parametrize(
        "name",
        [
            "Automotive",
            "BEAUTY",
            "Electronics",
            "FASHION",
            "Foodservice",
            "FURNITURE",
            "GROCERIES",
            "Home-Improvement",
            "Industrial",
            "MARKETPLACE",
            "Medical",
            "Office-Supplies",
            "Pet-Supplies",
            "Sporting-Goods",
        ],
    )
    def test_builtin_case_insensitive(self, name):
        result = load_vertical(name)
        assert isinstance(result, VerticalContext)
        assert "## Vertical:" in result.core

    def test_registry_has_all_fourteen(self):
        assert set(_BUILTIN_VERTICALS.keys()) == set(ALL_BUILTINS)

    @pytest.mark.parametrize("name", ALL_BUILTINS)
    def test_builtin_is_vertical_context(self, name):
        assert isinstance(_BUILTIN_VERTICALS[name], VerticalContext)


FOODSERVICE_OVERLAY_KEYS = [
    "beverage",
    "cooking",
    "food_prep",
    "refrigeration",
    "serving_holding",
    "smallwares",
    "tabletop",
    "warewash",
]


class TestFoodserviceOverlays:
    def test_foodservice_has_overlays(self):
        assert len(FOODSERVICE.overlays) == 8

    def test_overlay_keys(self):
        assert set(FOODSERVICE.overlays.keys()) == set(FOODSERVICE_OVERLAY_KEYS)

    @pytest.mark.parametrize("key", FOODSERVICE_OVERLAY_KEYS)
    def test_overlay_content_non_empty(self, key):
        overlay = FOODSERVICE.overlays[key]
        assert len(overlay.content) > 50
        assert len(overlay.description) > 10

    @pytest.mark.parametrize(
        "name",
        [n for n in ALL_BUILTINS if n != "foodservice"],
    )
    def test_other_verticals_have_no_overlays(self, name):
        vertical = load_vertical(name)
        assert vertical.overlays == {}

    def test_cooking_mentions_cooking(self):
        assert "cooking" in FOODSERVICE.overlays["cooking"].content.lower()

    def test_refrigeration_mentions_refrigeration(self):
        assert "refriger" in FOODSERVICE.overlays["refrigeration"].content.lower()

    def test_beverage_mentions_espresso(self):
        assert "espresso" in FOODSERVICE.overlays["beverage"].content.lower()

    def test_food_prep_mentions_mixer(self):
        assert "mixer" in FOODSERVICE.overlays["food_prep"].content.lower()

    def test_serving_holding_mentions_holding(self):
        assert "holding" in FOODSERVICE.overlays["serving_holding"].content.lower()

    def test_tabletop_mentions_dinnerware(self):
        assert "dinnerware" in FOODSERVICE.overlays["tabletop"].content.lower()


class TestCustomVertical:
    def test_load_from_file(self, tmp_path):
        custom = tmp_path / "my_vertical.txt"
        custom.write_text(
            "## Vertical: Custom\nCustom scoring guidance.",
            encoding="utf-8",
        )

        result = load_vertical(str(custom))
        assert isinstance(result, VerticalContext)
        assert "Custom scoring guidance" in result.core
        assert result.overlays == {}

    def test_file_trailing_whitespace_stripped(self, tmp_path):
        custom = tmp_path / "v.txt"
        custom.write_text("content\n\n\n", encoding="utf-8")

        result = load_vertical(str(custom))
        assert result.core == "content"


class TestUnknownVertical:
    def test_unknown_raises_file_not_found(self):
        with pytest.raises(FileNotFoundError, match="Unknown vertical 'nonexistent'"):
            load_vertical("nonexistent")

    def test_error_lists_available(self):
        pattern = (
            "automotive.*beauty.*electronics.*fashion"
            ".*foodservice.*furniture.*groceries.*home-improvement"
            ".*industrial.*marketplace.*medical"
            ".*office-supplies.*pet-supplies.*sporting-goods"
        )
        with pytest.raises(FileNotFoundError, match=pattern):
            load_vertical("nonexistent")
