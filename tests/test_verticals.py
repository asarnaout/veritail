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
    "beverage_equipment",
    "beverages",
    "cooking",
    "dairy_eggs",
    "disposables",
    "dry_goods",
    "food_prep",
    "furniture",
    "janitorial",
    "frozen_dessert_equipment",
    "prepared_foods",
    "produce",
    "proteins",
    "refrigeration",
    "serving_holding",
    "storage_transport",
    "smallwares",
    "tabletop",
    "ventilation",
    "warewash",
]


class TestFoodserviceOverlays:
    def test_foodservice_has_overlays(self):
        assert len(FOODSERVICE.overlays) == 20

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

    def test_beverage_equipment_mentions_espresso(self):
        assert "espresso" in FOODSERVICE.overlays["beverage_equipment"].content.lower()

    def test_food_prep_mentions_mixer(self):
        assert "mixer" in FOODSERVICE.overlays["food_prep"].content.lower()

    def test_serving_holding_mentions_holding(self):
        assert "holding" in FOODSERVICE.overlays["serving_holding"].content.lower()

    def test_tabletop_mentions_dinnerware(self):
        assert "dinnerware" in FOODSERVICE.overlays["tabletop"].content.lower()

    def test_ventilation_mentions_hood(self):
        assert "hood" in FOODSERVICE.overlays["ventilation"].content.lower()

    def test_frozen_dessert_equipment_mentions_soft_serve(self):
        content = FOODSERVICE.overlays["frozen_dessert_equipment"].content.lower()
        assert "soft serve" in content

    def test_furniture_mentions_booth(self):
        assert "booth" in FOODSERVICE.overlays["furniture"].content.lower()

    def test_beverage_equipment_does_not_mention_soft_serve(self):
        content = FOODSERVICE.overlays["beverage_equipment"].content.lower()
        assert "soft serve" not in content

    def test_proteins_mentions_imps(self):
        assert "imps" in FOODSERVICE.overlays["proteins"].content.lower()

    def test_proteins_mentions_usda(self):
        assert "usda" in FOODSERVICE.overlays["proteins"].content.lower()

    def test_prepared_foods_mentions_cn_label(self):
        assert "cn label" in FOODSERVICE.overlays["prepared_foods"].content.lower()

    def test_prepared_foods_mentions_parbaked(self):
        assert "parbaked" in FOODSERVICE.overlays["prepared_foods"].content.lower()

    def test_prepared_foods_mentions_rte(self):
        assert "ready-to-eat" in FOODSERVICE.overlays["prepared_foods"].content.lower()

    def test_dry_goods_mentions_flour(self):
        assert "flour" in FOODSERVICE.overlays["dry_goods"].content.lower()

    def test_disposables_mentions_clamshell(self):
        assert "clamshell" in FOODSERVICE.overlays["disposables"].content.lower()

    def test_smallwares_does_not_mention_disposables(self):
        assert "disposable" not in FOODSERVICE.overlays["smallwares"].content.lower()

    def test_core_has_cross_cutting_terminology(self):
        core = FOODSERVICE.core.lower()
        assert "hotel pan" in core
        assert "cambro" in core
        assert "speed rack" in core
        assert "dunnage rack" in core
        assert "pan sizes" in core

    def test_core_does_not_have_category_specific_terminology(self):
        core = FOODSERVICE.core.lower()
        assert "salamander" not in core
        assert "lowboy" not in core
        assert "bain-marie" not in core
        assert "lexan" not in core

    @pytest.mark.parametrize(
        "key,term",
        [
            ("cooking", "salamander"),
            ("cooking", "combi"),
            ("cooking", "charbroiler"),
            ("cooking", "impinger"),
            ("cooking", "deck oven"),
            ("refrigeration", "lowboy"),
            ("refrigeration", "reach-in"),
            ("refrigeration", "chef base"),
            ("serving_holding", "bain-marie"),
            ("smallwares", "lexan"),
            ("ventilation", "grease hood"),
            ("ventilation", "ansul"),
            ("frozen_dessert_equipment", "batch freezer"),
            ("frozen_dessert_equipment", "dipping cabinet"),
            ("furniture", "banquet chair"),
            ("dry_goods", "powdered sugar"),
            ("dry_goods", "#10"),
            ("dry_goods", "smoke point"),
            ("proteins", "filet mignon"),
            ("proteins", "imps"),
            ("proteins", "catch weight"),
            ("proteins", "iqf"),
            ("proteins", "ny strip"),
            ("produce", "plu"),
            ("produce", "iqf"),
            ("produce", "fresh-cut"),
            ("produce", "markon"),
            ("produce", "usda organic"),
            ("produce", "extra fancy"),
            ("produce", "count-per-case"),
            ("prepared_foods", "cn label"),
            ("prepared_foods", "parbaked"),
            ("prepared_foods", "soup base"),
            ("prepared_foods", "dough ball"),
            ("prepared_foods", "thaw-and-serve"),
            ("disposables", "clamshell"),
            ("disposables", "sterno"),
            ("janitorial", "quat"),
            ("janitorial", "ecolab"),
            ("janitorial", "haccp"),
            ("janitorial", "burnisher"),
            ("janitorial", "can liner"),
            ("janitorial", "j-fill"),
            ("storage_transport", "dunnage"),
            ("storage_transport", "nsf"),
            ("storage_transport", "camshelving"),
            ("storage_transport", "queen mary"),
            ("storage_transport", "camdolly"),
            ("storage_transport", "metromax"),
        ],
    )
    def test_category_terminology_in_overlay(self, key, term):
        assert term in FOODSERVICE.overlays[key].content.lower()


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
