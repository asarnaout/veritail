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
        assert (
            "Scoring considerations" in result.core or "Scoring approach" in result.core
        )

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
    "ice_machines",
    "janitorial",
    "frozen_dessert_equipment",
    "plumbing",
    "prepared_foods",
    "produce",
    "proteins",
    "refrigeration",
    "replacement_parts",
    "serving_holding",
    "storage_transport",
    "smallwares",
    "tabletop",
    "underbar",
    "ventilation",
    "warewash",
    "waste_reduction",
    "water_filtration",
]


class TestFoodserviceOverlays:
    def test_foodservice_has_overlays(self):
        assert len(FOODSERVICE.overlays) == 26

    def test_overlay_keys(self):
        assert set(FOODSERVICE.overlays.keys()) == set(FOODSERVICE_OVERLAY_KEYS)

    @pytest.mark.parametrize("key", FOODSERVICE_OVERLAY_KEYS)
    def test_overlay_content_non_empty(self, key):
        overlay = FOODSERVICE.overlays[key]
        assert len(overlay.content) > 50
        assert len(overlay.description) > 10

    @pytest.mark.parametrize("name", ALL_BUILTINS)
    def test_all_verticals_have_overlays(self, name):
        vertical = load_vertical(name)
        assert len(vertical.overlays) > 0

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

    def test_tabletop_mentions_serviceware(self):
        assert "serviceware" in FOODSERVICE.overlays["tabletop"].content.lower()

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

    def test_proteins_mentions_cut(self):
        assert "cut" in FOODSERVICE.overlays["proteins"].content.lower()

    def test_proteins_mentions_seafood(self):
        assert "seafood" in FOODSERVICE.overlays["proteins"].content.lower()

    def test_prepared_foods_mentions_frozen(self):
        assert "frozen" in FOODSERVICE.overlays["prepared_foods"].content.lower()

    def test_prepared_foods_mentions_par_cooked(self):
        assert "par-cooked" in FOODSERVICE.overlays["prepared_foods"].content.lower()

    def test_prepared_foods_mentions_rte(self):
        assert "ready-to-eat" in FOODSERVICE.overlays["prepared_foods"].content.lower()

    def test_dry_goods_mentions_flour(self):
        assert "flour" in FOODSERVICE.overlays["dry_goods"].content.lower()

    def test_disposables_mentions_compostable(self):
        assert "compostable" in FOODSERVICE.overlays["disposables"].content.lower()

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
            ("cooking", "combi"),
            ("cooking", "fryer"),
            ("cooking", "convection"),
            ("cooking", "btu"),
            ("refrigeration", "lowboy"),
            ("refrigeration", "reach-in"),
            ("refrigeration", "chef base"),
            ("refrigeration", "blast chiller"),
            ("refrigeration", "pizza prep"),
            ("serving_holding", "holding"),
            ("serving_holding", "steam table"),
            ("smallwares", "hotel pan"),
            ("smallwares", "gn pan"),
            ("smallwares", "cambro"),
            ("ventilation", "type i"),
            ("ventilation", "cfm"),
            ("ventilation", "fire suppression"),
            ("frozen_dessert_equipment", "soft serve"),
            ("frozen_dessert_equipment", "granita"),
            ("furniture", "booth"),
            ("furniture", "bifma"),
            ("dry_goods", "#10"),
            ("dry_goods", "flour"),
            ("dry_goods", "baking powder"),
            ("proteins", "ribeye"),
            ("proteins", "catch weight"),
            ("proteins", "shrimp"),
            ("produce", "organic"),
            ("produce", "fresh"),
            ("prepared_foods", "ready-to-eat"),
            ("prepared_foods", "par-cooked"),
            ("disposables", "compostable"),
            ("disposables", "bpi"),
            ("janitorial", "quat"),
            ("janitorial", "haccp"),
            ("janitorial", "rtu"),
            ("storage_transport", "sheet pan rack"),
            ("storage_transport", "chrome"),
            ("beverage_equipment", "espresso"),
            ("beverage_equipment", "bag-in-box"),
            ("beverages", "bib"),
            ("beverages", "rtd"),
            ("ice_machines", "nugget"),
            ("ice_machines", "flake"),
            ("ice_machines", "modular"),
            ("underbar", "cocktail station"),
            ("underbar", "speed rail"),
            ("water_filtration", "cartridge"),
            ("water_filtration", "scale"),
            ("replacement_parts", "gasket"),
            ("replacement_parts", "oem"),
            ("plumbing", "pre-rinse"),
            ("plumbing", "grease trap"),
            ("waste_reduction", "pulper"),
            ("waste_reduction", "compactor"),
            ("warewash", "glasswasher"),
            ("warewash", "conveyor"),
        ],
    )
    def test_category_terminology_in_overlay(self, key, term):
        assert term in FOODSERVICE.overlays[key].content.lower()


AUTOMOTIVE_OVERLAY_KEYS = [
    "accessories_and_tools",
    "batteries_starting_charging",
    "body_collision_paint_glass",
    "brakes_and_friction",
    "engine_ignition_and_sensors",
    "exhaust_and_emissions",
    "fluids_and_chemicals",
    "general",
    "hvac_air_conditioning",
    "lighting_and_visibility",
    "oil_change",
    "suspension_steering_and_hubs",
    "wheels_tires_tpms",
]


class TestAutomotiveOverlays:
    def test_automotive_has_overlays(self):
        assert len(AUTOMOTIVE.overlays) == 13

    def test_overlay_keys(self):
        assert set(AUTOMOTIVE.overlays.keys()) == set(AUTOMOTIVE_OVERLAY_KEYS)

    @pytest.mark.parametrize("key", AUTOMOTIVE_OVERLAY_KEYS)
    def test_overlay_content_non_empty(self, key):
        overlay = AUTOMOTIVE.overlays[key]
        assert len(overlay.content) > 50
        assert len(overlay.description) > 10

    def test_oil_change_mentions_viscosity(self):
        assert "viscosity" in AUTOMOTIVE.overlays["oil_change"].content.lower()

    def test_brakes_mentions_rotor(self):
        assert "rotor" in AUTOMOTIVE.overlays["brakes_and_friction"].content.lower()

    def test_wheels_mentions_bolt_pattern(self):
        content = AUTOMOTIVE.overlays["wheels_tires_tpms"].content.lower()
        assert "bolt pattern" in content

    def test_batteries_mentions_cca(self):
        content = AUTOMOTIVE.overlays["batteries_starting_charging"].content
        assert "cca" in content.lower()

    def test_lighting_mentions_bulb(self):
        content = AUTOMOTIVE.overlays["lighting_and_visibility"].content
        assert "bulb" in content.lower()

    def test_exhaust_mentions_catalytic(self):
        content = AUTOMOTIVE.overlays["exhaust_and_emissions"].content
        assert "catalytic" in content.lower()

    def test_hvac_mentions_refrigerant(self):
        content = AUTOMOTIVE.overlays["hvac_air_conditioning"].content
        assert "r-134a" in content.lower()

    def test_body_mentions_paint_code(self):
        content = AUTOMOTIVE.overlays["body_collision_paint_glass"].content
        assert "paint code" in content.lower()

    def test_suspension_mentions_strut(self):
        content = AUTOMOTIVE.overlays["suspension_steering_and_hubs"].content
        assert "strut" in content.lower()

    def test_engine_sensors_mentions_spark_plug(self):
        content = AUTOMOTIVE.overlays["engine_ignition_and_sensors"].content
        assert "spark plug" in content.lower()

    def test_accessories_mentions_hitch(self):
        assert "hitch" in AUTOMOTIVE.overlays["accessories_and_tools"].content.lower()

    def test_fluids_mentions_coolant(self):
        assert "coolant" in AUTOMOTIVE.overlays["fluids_and_chemicals"].content.lower()

    def test_general_mentions_fitment(self):
        assert "fitment" in AUTOMOTIVE.overlays["general"].content.lower()

    def test_core_has_ymm_fitment(self):
        core = AUTOMOTIVE.core.lower()
        assert "ymm" in core
        assert "fitment" in core

    def test_core_has_calibration_examples(self):
        core = AUTOMOTIVE.core.lower()
        assert "honda civic" in core

    @pytest.mark.parametrize(
        "key,term",
        [
            ("oil_change", "viscosity"),
            ("oil_change", "motor oil"),
            ("oil_change", "spin-on"),
            ("oil_change", "cartridge"),
            ("oil_change", "anti-drainback"),
            ("fluids_and_chemicals", "atf"),
            ("fluids_and_chemicals", "coolant"),
            ("fluids_and_chemicals", "brake fluid"),
            ("fluids_and_chemicals", "gear oil"),
            ("fluids_and_chemicals", "cvt"),
            ("brakes_and_friction", "pad"),
            ("brakes_and_friction", "rotor"),
            ("brakes_and_friction", "caliper"),
            ("brakes_and_friction", "drum"),
            ("brakes_and_friction", "ceramic"),
            ("wheels_tires_tpms", "bolt pattern"),
            ("wheels_tires_tpms", "tpms"),
            ("wheels_tires_tpms", "pcd"),
            ("wheels_tires_tpms", "offset"),
            ("wheels_tires_tpms", "run-flat"),
            ("batteries_starting_charging", "cca"),
            ("batteries_starting_charging", "agm"),
            ("batteries_starting_charging", "efb"),
            ("batteries_starting_charging", "group size"),
            ("batteries_starting_charging", "alternator"),
            ("lighting_and_visibility", "h11"),
            ("lighting_and_visibility", "halogen"),
            ("lighting_and_visibility", "wiper"),
            ("lighting_and_visibility", "drl"),
            ("engine_ignition_and_sensors", "spark plug"),
            ("engine_ignition_and_sensors", "oxygen sensor"),
            ("engine_ignition_and_sensors", "coil-on-plug"),
            ("engine_ignition_and_sensors", "cop"),
            ("suspension_steering_and_hubs", "strut"),
            ("suspension_steering_and_hubs", "shock"),
            ("suspension_steering_and_hubs", "control arm"),
            ("suspension_steering_and_hubs", "ball joint"),
            ("suspension_steering_and_hubs", "hub assembly"),
            ("exhaust_and_emissions", "catalytic converter"),
            ("exhaust_and_emissions", "carb"),
            ("exhaust_and_emissions", "muffler"),
            ("exhaust_and_emissions", "eo"),
            ("hvac_air_conditioning", "r-134a"),
            ("hvac_air_conditioning", "r-1234yf"),
            ("hvac_air_conditioning", "compressor"),
            ("hvac_air_conditioning", "condenser"),
            ("hvac_air_conditioning", "pag"),
            ("body_collision_paint_glass", "paint code"),
            ("body_collision_paint_glass", "capa"),
            ("body_collision_paint_glass", "bumper"),
            ("body_collision_paint_glass", "grille"),
            ("body_collision_paint_glass", "glazing"),
            ("accessories_and_tools", "floor mat"),
            ("accessories_and_tools", "hitch"),
            ("accessories_and_tools", "obd-ii"),
            ("accessories_and_tools", "gtw"),
            ("general", "fitment"),
        ],
    )
    def test_category_terminology_in_overlay(self, key, term):
        assert term in AUTOMOTIVE.overlays[key].content.lower()


BEAUTY_OVERLAY_KEYS = [
    "acne_and_breakouts",
    "body_care_personal",
    "brightening_dark_spots",
    "cheek_color_contour",
    "cleansers_makeup_removal",
    "complexion_makeup",
    "exfoliants_peels",
    "eye_makeup",
    "fragrance",
    "gift_sets_kits",
    "hair_color_toning",
    "hair_styling_and_tools",
    "hydration_barrier_repair",
    "lip_products",
    "makeup_tools",
    "masks_and_treatments",
    "nails",
    "retinoids_antiaging",
    "shampoo_conditioner",
    "sunless_tanning",
    "sunscreen_spf",
    "textured_curl_hair",
]


class TestBeautyOverlays:
    def test_beauty_has_overlays(self):
        assert len(BEAUTY.overlays) == 22

    def test_overlay_keys(self):
        assert set(BEAUTY.overlays.keys()) == set(BEAUTY_OVERLAY_KEYS)

    @pytest.mark.parametrize("key", BEAUTY_OVERLAY_KEYS)
    def test_overlay_content_non_empty(self, key):
        overlay = BEAUTY.overlays[key]
        assert len(overlay.content) > 50
        assert len(overlay.description) > 10

    def test_complexion_mentions_shade(self):
        content = BEAUTY.overlays["complexion_makeup"].content.lower()
        assert "shade" in content

    def test_eye_makeup_mentions_mascara(self):
        content = BEAUTY.overlays["eye_makeup"].content.lower()
        assert "mascara" in content

    def test_lip_products_mentions_lipstick(self):
        content = BEAUTY.overlays["lip_products"].content.lower()
        assert "lipstick" in content

    def test_fragrance_mentions_edp(self):
        content = BEAUTY.overlays["fragrance"].content.lower()
        assert "edp" in content

    def test_sunscreen_mentions_spf(self):
        content = BEAUTY.overlays["sunscreen_spf"].content.lower()
        assert "spf" in content

    def test_nails_mentions_gel(self):
        content = BEAUTY.overlays["nails"].content.lower()
        assert "gel" in content

    def test_retinoids_mentions_retinol(self):
        content = BEAUTY.overlays["retinoids_antiaging"].content.lower()
        assert "retinol" in content

    def test_acne_mentions_benzoyl_peroxide(self):
        content = BEAUTY.overlays["acne_and_breakouts"].content.lower()
        assert "benzoyl peroxide" in content

    def test_shampoo_mentions_conditioner(self):
        content = BEAUTY.overlays["shampoo_conditioner"].content.lower()
        assert "conditioner" in content

    def test_body_care_mentions_deodorant(self):
        content = BEAUTY.overlays["body_care_personal"].content.lower()
        assert "deodorant" in content

    def test_core_has_hard_constraints(self):
        core = BEAUTY.core.lower()
        assert "hard constraint" in core
        assert "shade" in core
        assert "spf" in core

    def test_core_has_pregnancy_safety(self):
        core = BEAUTY.core.lower()
        assert "pregnancy" in core
        assert "retinoid" in core

    @pytest.mark.parametrize(
        "key,term",
        [
            ("complexion_makeup", "shade"),
            ("complexion_makeup", "undertone"),
            ("complexion_makeup", "foundation"),
            ("complexion_makeup", "concealer"),
            ("complexion_makeup", "primer"),
            ("eye_makeup", "mascara"),
            ("eye_makeup", "eyeliner"),
            ("eye_makeup", "false lash"),
            ("eye_makeup", "brow"),
            ("eye_makeup", "kohl"),
            ("lip_products", "lipstick"),
            ("lip_products", "lip gloss"),
            ("lip_products", "lip stain"),
            ("lip_products", "matte"),
            ("cheek_color_contour", "blush"),
            ("cheek_color_contour", "bronzer"),
            ("cheek_color_contour", "contour"),
            ("cheek_color_contour", "highlighter"),
            ("makeup_tools", "brush"),
            ("makeup_tools", "sponge"),
            ("cleansers_makeup_removal", "cleansing oil"),
            ("cleansers_makeup_removal", "micellar"),
            ("cleansers_makeup_removal", "double cleansing"),
            ("exfoliants_peels", "aha"),
            ("exfoliants_peels", "bha"),
            ("exfoliants_peels", "scrub"),
            ("acne_and_breakouts", "benzoyl peroxide"),
            ("acne_and_breakouts", "salicylic acid"),
            ("acne_and_breakouts", "pimple patch"),
            ("retinoids_antiaging", "retinol"),
            ("retinoids_antiaging", "retinal"),
            ("retinoids_antiaging", "pregnancy"),
            ("brightening_dark_spots", "vitamin c"),
            ("brightening_dark_spots", "niacinamide"),
            ("brightening_dark_spots", "hyperpigmentation"),
            ("hydration_barrier_repair", "hyaluronic acid"),
            ("hydration_barrier_repair", "ceramide"),
            ("hydration_barrier_repair", "barrier"),
            ("masks_and_treatments", "sheet mask"),
            ("masks_and_treatments", "clay"),
            ("masks_and_treatments", "sleeping mask"),
            ("sunscreen_spf", "spf"),
            ("sunscreen_spf", "mineral"),
            ("sunscreen_spf", "broad spectrum"),
            ("sunless_tanning", "self-tanner"),
            ("sunless_tanning", "dha"),
            ("shampoo_conditioner", "shampoo"),
            ("shampoo_conditioner", "dry shampoo"),
            ("shampoo_conditioner", "purple shampoo"),
            ("textured_curl_hair", "cgm"),
            ("textured_curl_hair", "porosity"),
            ("textured_curl_hair", "curl"),
            ("hair_color_toning", "developer"),
            ("hair_color_toning", "toner"),
            ("hair_color_toning", "bleach"),
            ("hair_styling_and_tools", "heat protectant"),
            ("hair_styling_and_tools", "flat iron"),
            ("hair_styling_and_tools", "pomade"),
            ("fragrance", "edp"),
            ("fragrance", "edt"),
            ("fragrance", "flanker"),
            ("nails", "gel polish"),
            ("nails", "press-on"),
            ("nails", "dip powder"),
            ("body_care_personal", "deodorant"),
            ("body_care_personal", "antiperspirant"),
            ("body_care_personal", "body wash"),
            ("gift_sets_kits", "discovery set"),
            ("gift_sets_kits", "bundle"),
        ],
    )
    def test_category_terminology_in_overlay(self, key, term):
        assert term in BEAUTY.overlays[key].content.lower()


ELECTRONICS_OVERLAY_KEYS = [
    "camera_lenses",
    "cameras_and_kits",
    "charging_cables_and_adapters",
    "device_specific_protection",
    "external_storage",
    "gaming_consoles",
    "gaming_desktop_pcs",
    "gaming_laptops",
    "headphones_and_earbuds",
    "home_audio",
    "macbooks",
    "memory_cards_and_flash",
    "memory_ram",
    "monitors",
    "motherboards",
    "networking",
    "office_desktops_workstations_aio_mini",
    "pc_cases_and_cooling",
    "pc_cpus",
    "pc_gpus",
    "power_supplies",
    "printer_ink_and_toner",
    "printers_and_scanners",
    "productivity_laptops_ultrabooks",
    "smart_home",
    "smartphones",
    "storage_internal",
    "tablets_and_ereaders",
    "tvs_and_projectors",
    "vr_headsets",
    "wearables",
]


class TestElectronicsOverlays:
    def test_electronics_has_overlays(self):
        assert len(ELECTRONICS.overlays) == 31

    def test_overlay_keys(self):
        assert set(ELECTRONICS.overlays.keys()) == set(ELECTRONICS_OVERLAY_KEYS)

    @pytest.mark.parametrize("key", ELECTRONICS_OVERLAY_KEYS)
    def test_overlay_content_non_empty(self, key):
        overlay = ELECTRONICS.overlays[key]
        assert len(overlay.content) > 50
        assert len(overlay.description) > 10

    def test_gaming_desktops_mentions_prebuilt(self):
        content = ELECTRONICS.overlays["gaming_desktop_pcs"].content.lower()
        assert "prebuilt" in content

    def test_gaming_laptops_mentions_gpu(self):
        content = ELECTRONICS.overlays["gaming_laptops"].content.lower()
        assert "gpu" in content

    def test_pc_cpus_mentions_socket(self):
        content = ELECTRONICS.overlays["pc_cpus"].content.lower()
        assert "socket" in content

    def test_pc_gpus_mentions_vram(self):
        content = ELECTRONICS.overlays["pc_gpus"].content.lower()
        assert "vram" in content

    def test_motherboards_mentions_chipset(self):
        content = ELECTRONICS.overlays["motherboards"].content.lower()
        assert "chipset" in content

    def test_memory_ram_mentions_ddr(self):
        content = ELECTRONICS.overlays["memory_ram"].content.lower()
        assert "ddr4" in content
        assert "ddr5" in content

    def test_storage_internal_mentions_nvme(self):
        content = ELECTRONICS.overlays["storage_internal"].content.lower()
        assert "nvme" in content

    def test_monitors_mentions_refresh_rate(self):
        content = ELECTRONICS.overlays["monitors"].content.lower()
        assert "refresh rate" in content

    def test_networking_mentions_wifi(self):
        content = ELECTRONICS.overlays["networking"].content.lower()
        assert "wi-fi" in content

    def test_smartphones_mentions_unlocked(self):
        content = ELECTRONICS.overlays["smartphones"].content.lower()
        assert "unlocked" in content

    def test_headphones_mentions_anc(self):
        content = ELECTRONICS.overlays["headphones_and_earbuds"].content
        assert "ANC" in content

    def test_core_has_compatibility_gate(self):
        core = ELECTRONICS.core.lower()
        assert "compatibility" in core
        assert "connector" in core

    def test_core_has_form_factor(self):
        core = ELECTRONICS.core.lower()
        assert "form factor" in core

    @pytest.mark.parametrize(
        "key,term",
        [
            ("gaming_desktop_pcs", "prebuilt"),
            ("gaming_desktop_pcs", "gpu"),
            ("gaming_desktop_pcs", "barebones"),
            ("office_desktops_workstations_aio_mini", "all-in-one"),
            ("office_desktops_workstations_aio_mini", "mini pc"),
            ("office_desktops_workstations_aio_mini", "workstation"),
            ("gaming_laptops", "tgp"),
            ("gaming_laptops", "refresh rate"),
            ("gaming_laptops", "thunderbolt"),
            ("productivity_laptops_ultrabooks", "chromebook"),
            ("productivity_laptops_ultrabooks", "2-in-1"),
            ("productivity_laptops_ultrabooks", "ultrabook"),
            ("macbooks", "apple silicon"),
            ("macbooks", "magsafe"),
            ("macbooks", "unified memory"),
            ("tablets_and_ereaders", "cellular"),
            ("tablets_and_ereaders", "e-reader"),
            ("tablets_and_ereaders", "stylus"),
            ("wearables", "gps"),
            ("wearables", "ecg"),
            ("pc_cpus", "socket"),
            ("pc_cpus", "boxed"),
            ("pc_cpus", "suffix"),
            ("pc_gpus", "vram"),
            ("pc_gpus", "12vhpwr"),
            ("pc_gpus", "workstation"),
            ("motherboards", "ddr4"),
            ("motherboards", "wi-fi"),
            ("motherboards", "m.2"),
            ("memory_ram", "ddr4"),
            ("memory_ram", "so-dimm"),
            ("memory_ram", "ecc"),
            ("storage_internal", "nvme"),
            ("storage_internal", "sata"),
            ("storage_internal", "2280"),
            ("external_storage", "thunderbolt"),
            ("external_storage", "portable"),
            ("memory_cards_and_flash", "microsd"),
            ("memory_cards_and_flash", "v30"),
            ("memory_cards_and_flash", "uhs"),
            ("power_supplies", "atx"),
            ("power_supplies", "sfx"),
            ("power_supplies", "modular"),
            ("pc_cases_and_cooling", "radiator"),
            ("pc_cases_and_cooling", "thermal paste"),
            ("monitors", "refresh rate"),
            ("monitors", "ultrawide"),
            ("monitors", "hdr"),
            ("tvs_and_projectors", "oled"),
            ("tvs_and_projectors", "hdmi"),
            ("tvs_and_projectors", "projector"),
            ("headphones_and_earbuds", "noise cancellation"),
            ("headphones_and_earbuds", "bluetooth"),
            ("home_audio", "soundbar"),
            ("home_audio", "subwoofer"),
            ("home_audio", "earc"),
            ("networking", "mesh"),
            ("networking", "docsis"),
            ("networking", "router"),
            ("smart_home", "matter"),
            ("smart_home", "zigbee"),
            ("smart_home", "z-wave"),
            ("smartphones", "unlocked"),
            ("smartphones", "carrier"),
            ("device_specific_protection", "magsafe"),
            ("device_specific_protection", "screen protector"),
            ("charging_cables_and_adapters", "thunderbolt"),
            ("charging_cables_and_adapters", "usb-c"),
            ("charging_cables_and_adapters", "power delivery"),
            ("cameras_and_kits", "mirrorless"),
            ("cameras_and_kits", "body only"),
            ("camera_lenses", "mount"),
            ("camera_lenses", "focal length"),
            ("printers_and_scanners", "laser"),
            ("printers_and_scanners", "inkjet"),
            ("printer_ink_and_toner", "cartridge"),
            ("printer_ink_and_toner", "drum"),
            ("gaming_consoles", "ps5"),
            ("gaming_consoles", "microsd"),
            ("vr_headsets", "steamvr"),
            ("vr_headsets", "standalone"),
        ],
    )
    def test_category_terminology_in_overlay(self, key, term):
        assert term in ELECTRONICS.overlays[key].content.lower()


FASHION_OVERLAY_KEYS = [
    "activewear_athleisure",
    "boots",
    "denim_jeans",
    "heels_and_dress_shoes",
    "intimates_bras_lingerie",
    "jewelry_precious_metals",
    "kids_baby_apparel",
    "outerwear_rain_down",
    "resale_vintage",
    "sandals_slides",
    "sneakers_athletic_shoes",
    "swimwear_upf",
    "tailored_menswear",
]


class TestFashionOverlays:
    def test_fashion_has_overlays(self):
        assert len(FASHION.overlays) == 13

    def test_overlay_keys(self):
        assert set(FASHION.overlays.keys()) == set(FASHION_OVERLAY_KEYS)

    @pytest.mark.parametrize("key", FASHION_OVERLAY_KEYS)
    def test_overlay_content_non_empty(self, key):
        overlay = FASHION.overlays[key]
        assert len(overlay.content) > 50
        assert len(overlay.description) > 10

    def test_sneakers_mentions_running(self):
        content = FASHION.overlays["sneakers_athletic_shoes"].content.lower()
        assert "running" in content

    def test_boots_mentions_waterproof(self):
        content = FASHION.overlays["boots"].content.lower()
        assert "waterproof" in content

    def test_denim_mentions_selvedge(self):
        content = FASHION.overlays["denim_jeans"].content.lower()
        assert "selvedge" in content

    def test_intimates_mentions_underwire(self):
        content = FASHION.overlays["intimates_bras_lingerie"].content.lower()
        assert "underwire" in content

    def test_activewear_mentions_moisture_wicking(self):
        content = FASHION.overlays["activewear_athleisure"].content.lower()
        assert "moisture-wicking" in content

    def test_outerwear_mentions_fill_power(self):
        content = FASHION.overlays["outerwear_rain_down"].content.lower()
        assert "fill power" in content

    def test_tailored_mentions_tuxedo(self):
        content = FASHION.overlays["tailored_menswear"].content.lower()
        assert "tuxedo" in content

    def test_swimwear_mentions_upf(self):
        content = FASHION.overlays["swimwear_upf"].content.lower()
        assert "upf" in content

    def test_kids_mentions_toddler(self):
        content = FASHION.overlays["kids_baby_apparel"].content.lower()
        assert "toddler" in content

    def test_jewelry_mentions_karat(self):
        content = FASHION.overlays["jewelry_precious_metals"].content.lower()
        assert "karat" in content

    def test_resale_mentions_vintage(self):
        content = FASHION.overlays["resale_vintage"].content.lower()
        assert "vintage" in content

    def test_heels_mentions_stiletto(self):
        content = FASHION.overlays["heels_and_dress_shoes"].content.lower()
        assert "stiletto" in content

    def test_sandals_mentions_espadrille(self):
        content = FASHION.overlays["sandals_slides"].content.lower()
        assert "espadrille" in content

    def test_core_has_gender_alignment(self):
        core = FASHION.core.lower()
        assert "gender" in core
        assert "unisex" in core

    def test_core_has_size_system(self):
        core = FASHION.core.lower()
        assert "size system" in core
        assert "petite" in core

    @pytest.mark.parametrize(
        "key,term",
        [
            ("sneakers_athletic_shoes", "running"),
            ("sneakers_athletic_shoes", "basketball"),
            ("sneakers_athletic_shoes", "width"),
            ("sneakers_athletic_shoes", "deadstock"),
            ("sneakers_athletic_shoes", "trainer"),
            ("sneakers_athletic_shoes", "skate"),
            ("boots", "ankle"),
            ("boots", "chelsea"),
            ("boots", "wide calf"),
            ("boots", "waterproof"),
            ("boots", "steel toe"),
            ("boots", "duck boot"),
            ("boots", "insulated"),
            ("sandals_slides", "slide"),
            ("sandals_slides", "flip-flop"),
            ("sandals_slides", "espadrille"),
            ("sandals_slides", "wedge"),
            ("sandals_slides", "arch support"),
            ("heels_and_dress_shoes", "stiletto"),
            ("heels_and_dress_shoes", "kitten heel"),
            ("heels_and_dress_shoes", "pumps"),
            ("heels_and_dress_shoes", "oxford"),
            ("heels_and_dress_shoes", "mary jane"),
            ("heels_and_dress_shoes", "block heel"),
            ("denim_jeans", "selvedge"),
            ("denim_jeans", "raw"),
            ("denim_jeans", "sanforized"),
            ("denim_jeans", "rise"),
            ("denim_jeans", "bootcut"),
            ("denim_jeans", "shrink-to-fit"),
            ("denim_jeans", "inseam"),
            ("intimates_bras_lingerie", "band"),
            ("intimates_bras_lingerie", "cup"),
            ("intimates_bras_lingerie", "underwire"),
            ("intimates_bras_lingerie", "bralette"),
            ("intimates_bras_lingerie", "shapewear"),
            ("intimates_bras_lingerie", "strapless"),
            ("activewear_athleisure", "moisture-wicking"),
            ("activewear_athleisure", "compression"),
            ("activewear_athleisure", "sports bra"),
            ("activewear_athleisure", "base layer"),
            ("activewear_athleisure", "athleisure"),
            ("activewear_athleisure", "quick-dry"),
            ("outerwear_rain_down", "waterproof"),
            ("outerwear_rain_down", "fill power"),
            ("outerwear_rain_down", "3-in-1"),
            ("outerwear_rain_down", "dwr"),
            ("outerwear_rain_down", "parka"),
            ("outerwear_rain_down", "shell"),
            ("tailored_menswear", "40r"),
            ("tailored_menswear", "drop"),
            ("tailored_menswear", "tuxedo"),
            ("tailored_menswear", "dress shirt"),
            ("tailored_menswear", "black tie"),
            ("tailored_menswear", "sport coat"),
            ("swimwear_upf", "upf"),
            ("swimwear_upf", "rash guard"),
            ("swimwear_upf", "boardshort"),
            ("swimwear_upf", "tankini"),
            ("kids_baby_apparel", "toddler"),
            ("kids_baby_apparel", "2t"),
            ("kids_baby_apparel", "husky"),
            ("kids_baby_apparel", "newborn"),
            ("kids_baby_apparel", "preemie"),
            ("kids_baby_apparel", "youth"),
            ("jewelry_precious_metals", "karat"),
            ("jewelry_precious_metals", "vermeil"),
            ("jewelry_precious_metals", "sterling silver"),
            ("jewelry_precious_metals", "nickel-free"),
            ("jewelry_precious_metals", "gold filled"),
            ("resale_vintage", "nwt"),
            ("resale_vintage", "deadstock"),
            ("resale_vintage", "vintage"),
            ("resale_vintage", "pre-owned"),
            ("resale_vintage", "euc"),
            ("resale_vintage", "nwot"),
            ("resale_vintage", "authentication"),
        ],
    )
    def test_category_terminology_in_overlay(self, key, term):
        assert term in FASHION.overlays[key].content.lower()


FURNITURE_OVERLAY_KEYS = [
    "bathroom_vanities",
    "beds_frames_headboards",
    "casegoods_storage",
    "chairs_stools_benches",
    "commercial_contract",
    "dining_tables_sets",
    "home_office",
    "makeup_vanities_dressing_tables",
    "mattresses_toppers_bases",
    "media_consoles_tv_stands",
    "motion_seating",
    "nursery_kids",
    "outdoor_patio",
    "rugs",
    "sleepers_daybeds_futons",
    "sofas_sectionals",
]


class TestFurnitureOverlays:
    def test_furniture_has_overlays(self):
        assert len(FURNITURE.overlays) == 16

    def test_overlay_keys(self):
        assert set(FURNITURE.overlays.keys()) == set(FURNITURE_OVERLAY_KEYS)

    @pytest.mark.parametrize("key", FURNITURE_OVERLAY_KEYS)
    def test_overlay_content_non_empty(self, key):
        overlay = FURNITURE.overlays[key]
        assert len(overlay.content) > 50
        assert len(overlay.description) > 10

    def test_sofas_mentions_sectional(self):
        content = FURNITURE.overlays["sofas_sectionals"].content.lower()
        assert "sectional" in content

    def test_motion_mentions_lift_chair(self):
        content = FURNITURE.overlays["motion_seating"].content.lower()
        assert "lift chair" in content

    def test_sleepers_mentions_futon(self):
        content = FURNITURE.overlays["sleepers_daybeds_futons"].content.lower()
        assert "futon" in content

    def test_beds_mentions_platform(self):
        content = FURNITURE.overlays["beds_frames_headboards"].content.lower()
        assert "platform" in content

    def test_mattresses_mentions_hybrid(self):
        content = FURNITURE.overlays["mattresses_toppers_bases"].content.lower()
        assert "hybrid" in content

    def test_casegoods_mentions_dresser(self):
        content = FURNITURE.overlays["casegoods_storage"].content.lower()
        assert "dresser" in content

    def test_dining_mentions_counter_height(self):
        content = FURNITURE.overlays["dining_tables_sets"].content.lower()
        assert "counter-height" in content

    def test_chairs_mentions_bar_stool(self):
        content = FURNITURE.overlays["chairs_stools_benches"].content.lower()
        assert "bar stool" in content

    def test_home_office_mentions_bifma(self):
        content = FURNITURE.overlays["home_office"].content.lower()
        assert "bifma" in content

    def test_outdoor_mentions_teak(self):
        content = FURNITURE.overlays["outdoor_patio"].content.lower()
        assert "teak" in content

    def test_bathroom_vanities_mentions_centerset(self):
        content = FURNITURE.overlays["bathroom_vanities"].content.lower()
        assert "centerset" in content

    def test_makeup_vanities_mentions_hollywood(self):
        content = FURNITURE.overlays["makeup_vanities_dressing_tables"].content.lower()
        assert "hollywood" in content

    def test_media_consoles_mentions_fireplace(self):
        content = FURNITURE.overlays["media_consoles_tv_stands"].content.lower()
        assert "fireplace" in content

    def test_rugs_mentions_pile(self):
        content = FURNITURE.overlays["rugs"].content.lower()
        assert "pile" in content

    def test_nursery_mentions_crib(self):
        content = FURNITURE.overlays["nursery_kids"].content.lower()
        assert "crib" in content

    def test_commercial_mentions_stacking(self):
        content = FURNITURE.overlays["commercial_contract"].content.lower()
        assert "stacking" in content

    def test_core_has_hard_constraints(self):
        core = FURNITURE.core.lower()
        assert "hard constraint" in core
        assert "indoor" in core
        assert "outdoor" in core

    def test_core_has_fitment(self):
        core = FURNITURE.core.lower()
        assert "dimension" in core
        assert "assembly" in core

    @pytest.mark.parametrize(
        "key,term",
        [
            ("sofas_sectionals", "laf/raf"),
            ("sofas_sectionals", "sectional"),
            ("sofas_sectionals", "modular"),
            ("sofas_sectionals", "top-grain"),
            ("sofas_sectionals", "bonded leather"),
            ("sofas_sectionals", "double rubs"),
            ("sofas_sectionals", "slipcovered"),
            ("sofas_sectionals", "chaise"),
            ("sofas_sectionals", "martindale"),
            ("motion_seating", "power recliner"),
            ("motion_seating", "lift chair"),
            ("motion_seating", "wall-hugger"),
            ("motion_seating", "swivel"),
            ("motion_seating", "glider"),
            ("motion_seating", "theater seating"),
            ("motion_seating", "power headrest"),
            ("sleepers_daybeds_futons", "sleeper sofa"),
            ("sleepers_daybeds_futons", "futon"),
            ("sleepers_daybeds_futons", "daybed"),
            ("sleepers_daybeds_futons", "trundle"),
            ("sleepers_daybeds_futons", "murphy bed"),
            ("sleepers_daybeds_futons", "sofa-bed"),
            ("sleepers_daybeds_futons", "pull-out"),
            ("beds_frames_headboards", "platform"),
            ("beds_frames_headboards", "headboard"),
            ("beds_frames_headboards", "box spring"),
            ("beds_frames_headboards", "california king"),
            ("beds_frames_headboards", "storage bed"),
            ("beds_frames_headboards", "adjustable base"),
            ("beds_frames_headboards", "slat"),
            ("mattresses_toppers_bases", "memory foam"),
            ("mattresses_toppers_bases", "innerspring"),
            ("mattresses_toppers_bases", "hybrid"),
            ("mattresses_toppers_bases", "certipur"),
            ("mattresses_toppers_bases", "1633"),
            ("mattresses_toppers_bases", "topper"),
            ("mattresses_toppers_bases", "firmness"),
            ("casegoods_storage", "dresser"),
            ("casegoods_storage", "armoire"),
            ("casegoods_storage", "nightstand"),
            ("casegoods_storage", "anti-tip"),
            ("casegoods_storage", "sturdy"),
            ("casegoods_storage", "carb phase 2"),
            ("casegoods_storage", "tip-over"),
            ("dining_tables_sets", "counter-height"),
            ("dining_tables_sets", "bar-height"),
            ("dining_tables_sets", "butterfly"),
            ("dining_tables_sets", "drop-leaf"),
            ("dining_tables_sets", "seats 8"),
            ("chairs_stools_benches", "counter stool"),
            ("chairs_stools_benches", "bar stool"),
            ("chairs_stools_benches", "accent chair"),
            ("chairs_stools_benches", "dining chair"),
            ("chairs_stools_benches", "seat height"),
            ("chairs_stools_benches", "clearance"),
            ("home_office", "bifma"),
            ("home_office", "standing desk"),
            ("home_office", "caster"),
            ("home_office", "lumbar"),
            ("home_office", "x5.1"),
            ("outdoor_patio", "teak"),
            ("outdoor_patio", "powder-coated"),
            ("outdoor_patio", "hdpe"),
            ("outdoor_patio", "solution-dyed acrylic"),
            ("outdoor_patio", "reticulated"),
            ("outdoor_patio", "quick-dry"),
            ("bathroom_vanities", "centerset"),
            ("bathroom_vanities", "widespread"),
            ("bathroom_vanities", "single-hole"),
            ("bathroom_vanities", "floating"),
            ("bathroom_vanities", "vessel"),
            ("bathroom_vanities", "undermount"),
            ("makeup_vanities_dressing_tables", "makeup"),
            ("makeup_vanities_dressing_tables", "mirror"),
            ("makeup_vanities_dressing_tables", "hollywood"),
            ("makeup_vanities_dressing_tables", "dressing table"),
            ("makeup_vanities_dressing_tables", "stool"),
            ("media_consoles_tv_stands", "diagonal"),
            ("media_consoles_tv_stands", "fireplace"),
            ("media_consoles_tv_stands", "floating"),
            ("media_consoles_tv_stands", "soundbar"),
            ("rugs", "pile"),
            ("rugs", "runner"),
            ("rugs", "rug pad"),
            ("rugs", "polypropylene"),
            ("rugs", "indoor/outdoor"),
            ("nursery_kids", "crib"),
            ("nursery_kids", "16 cfr"),
            ("nursery_kids", "drop-side"),
            ("nursery_kids", "bunk bed"),
            ("nursery_kids", "slat"),
            ("nursery_kids", "convertible crib"),
            ("commercial_contract", "bifma"),
            ("commercial_contract", "stacking"),
            ("commercial_contract", "tb117"),
            ("commercial_contract", "greenguard"),
            ("commercial_contract", "cal 133"),
            ("commercial_contract", "ganging"),
        ],
    )
    def test_category_terminology_in_overlay(self, key, term):
        assert term in FURNITURE.overlays[key].content.lower()


GROCERIES_OVERLAY_KEYS = [
    "adult_beverages_alcohol",
    "baby_care",
    "bakery_bread",
    "beverages_soft_drinks",
    "cleaning_disinfectants",
    "coffee_tea",
    "dairy_eggs",
    "deli_prepared",
    "frozen_foods",
    "health_otc_vitamins",
    "laundry",
    "meat_poultry",
    "nutrition_free_from",
    "pantry_cooking",
    "paper_disposables_trash",
    "personal_care_beauty",
    "pet_supplies",
    "produce_fresh",
    "seafood_shellfish",
    "snacks_candy",
]


class TestGroceriesOverlays:
    def test_groceries_has_overlays(self):
        assert len(GROCERIES.overlays) == 20

    def test_overlay_keys(self):
        assert set(GROCERIES.overlays.keys()) == set(GROCERIES_OVERLAY_KEYS)

    @pytest.mark.parametrize("key", GROCERIES_OVERLAY_KEYS)
    def test_overlay_content_non_empty(self, key):
        overlay = GROCERIES.overlays[key]
        assert len(overlay.content) > 50
        assert len(overlay.description) > 10

    def test_nutrition_mentions_gluten(self):
        content = GROCERIES.overlays["nutrition_free_from"].content.lower()
        assert "gluten-free" in content

    def test_produce_mentions_organic(self):
        content = GROCERIES.overlays["produce_fresh"].content.lower()
        assert "organic" in content

    def test_meat_mentions_ribeye(self):
        content = GROCERIES.overlays["meat_poultry"].content.lower()
        assert "ribeye" in content

    def test_seafood_mentions_iqf(self):
        content = GROCERIES.overlays["seafood_shellfish"].content.lower()
        assert "iqf" in content

    def test_deli_mentions_rotisserie(self):
        content = GROCERIES.overlays["deli_prepared"].content.lower()
        assert "rotisserie" in content

    def test_dairy_mentions_lactose(self):
        content = GROCERIES.overlays["dairy_eggs"].content.lower()
        assert "lactose-free" in content

    def test_bakery_mentions_bagels(self):
        content = GROCERIES.overlays["bakery_bread"].content.lower()
        assert "bagels" in content

    def test_frozen_mentions_iqf(self):
        content = GROCERIES.overlays["frozen_foods"].content.lower()
        assert "iqf" in content

    def test_pantry_mentions_san_marzano(self):
        content = GROCERIES.overlays["pantry_cooking"].content.lower()
        assert "san marzano" in content

    def test_snacks_mentions_jerky(self):
        content = GROCERIES.overlays["snacks_candy"].content.lower()
        assert "jerky" in content

    def test_beverages_mentions_tonic(self):
        content = GROCERIES.overlays["beverages_soft_drinks"].content.lower()
        assert "tonic" in content

    def test_coffee_mentions_nespresso(self):
        content = GROCERIES.overlays["coffee_tea"].content.lower()
        assert "nespresso" in content

    def test_cleaning_mentions_epa(self):
        content = GROCERIES.overlays["cleaning_disinfectants"].content.lower()
        assert "epa" in content

    def test_laundry_mentions_pods(self):
        content = GROCERIES.overlays["laundry"].content.lower()
        assert "pods" in content

    def test_paper_mentions_trash_bag(self):
        content = GROCERIES.overlays["paper_disposables_trash"].content.lower()
        assert "trash bag" in content

    def test_health_mentions_gummy(self):
        content = GROCERIES.overlays["health_otc_vitamins"].content.lower()
        assert "gummy" in content

    def test_personal_care_mentions_spf(self):
        content = GROCERIES.overlays["personal_care_beauty"].content.lower()
        assert "spf" in content

    def test_baby_mentions_diaper(self):
        content = GROCERIES.overlays["baby_care"].content.lower()
        assert "diaper" in content

    def test_pet_mentions_kibble(self):
        content = GROCERIES.overlays["pet_supplies"].content.lower()
        assert "kibble" in content

    def test_alcohol_mentions_abv(self):
        content = GROCERIES.overlays["adult_beverages_alcohol"].content.lower()
        assert "abv" in content

    def test_core_has_allergen_gate(self):
        core = GROCERIES.core.lower()
        assert "allergen" in core
        assert "hard constraint" in core

    def test_core_has_storage_class(self):
        core = GROCERIES.core.lower()
        assert "frozen" in core
        assert "shelf-stable" in core

    @pytest.mark.parametrize(
        "key,term",
        [
            ("nutrition_free_from", "gluten-free"),
            ("nutrition_free_from", "allergen"),
            ("nutrition_free_from", "kosher"),
            ("nutrition_free_from", "halal"),
            ("nutrition_free_from", "sugar-free"),
            ("nutrition_free_from", "keto"),
            ("nutrition_free_from", "dairy-free"),
            ("produce_fresh", "organic"),
            ("produce_fresh", "fresh"),
            ("produce_fresh", "scallions"),
            ("produce_fresh", "variable-measure"),
            ("meat_poultry", "ribeye"),
            ("meat_poultry", "bone-in"),
            ("meat_poultry", "ground meat"),
            ("meat_poultry", "80/20"),
            ("seafood_shellfish", "iqf"),
            ("seafood_shellfish", "wild-caught"),
            ("seafood_shellfish", "shrimp"),
            ("seafood_shellfish", "21/25"),
            ("deli_prepared", "rotisserie"),
            ("deli_prepared", "sliced-to-order"),
            ("deli_prepared", "variable weight"),
            ("dairy_eggs", "lactose-free"),
            ("dairy_eggs", "shredded"),
            ("dairy_eggs", "oat"),
            ("bakery_bread", "bagels"),
            ("bakery_bread", "tortillas"),
            ("frozen_foods", "iqf"),
            ("frozen_foods", "ice cream"),
            ("pantry_cooking", "san marzano"),
            ("pantry_cooking", "baking soda"),
            ("pantry_cooking", "baking powder"),
            ("pantry_cooking", "extra virgin"),
            ("snacks_candy", "jerky"),
            ("snacks_candy", "multipack"),
            ("beverages_soft_drinks", "tonic"),
            ("beverages_soft_drinks", "seltzer"),
            ("beverages_soft_drinks", "club soda"),
            ("beverages_soft_drinks", "caffeine-free"),
            ("coffee_tea", "nespresso"),
            ("coffee_tea", "k-cup"),
            ("coffee_tea", "decaf"),
            ("coffee_tea", "whole bean"),
            ("coffee_tea", "loose leaf"),
            ("cleaning_disinfectants", "epa"),
            ("cleaning_disinfectants", "disinfectant"),
            ("cleaning_disinfectants", "bleach"),
            ("laundry", "pods"),
            ("laundry", "free & clear"),
            ("laundry", "fabric softener"),
            ("paper_disposables_trash", "trash bag"),
            ("paper_disposables_trash", "ply"),
            ("paper_disposables_trash", "compostable"),
            ("health_otc_vitamins", "gummy"),
            ("health_otc_vitamins", "d3"),
            ("health_otc_vitamins", "tablet"),
            ("personal_care_beauty", "spf"),
            ("personal_care_beauty", "antiperspirant"),
            ("personal_care_beauty", "fragrance-free"),
            ("baby_care", "diaper"),
            ("baby_care", "infant formula"),
            ("baby_care", "wipes"),
            ("baby_care", "pull-ups"),
            ("pet_supplies", "grain-free"),
            ("pet_supplies", "kibble"),
            ("pet_supplies", "litter"),
            ("pet_supplies", "puppy"),
            ("adult_beverages_alcohol", "abv"),
            ("adult_beverages_alcohol", "ipa"),
            ("adult_beverages_alcohol", "non-alcoholic"),
            ("adult_beverages_alcohol", "hard seltzer"),
        ],
    )
    def test_category_terminology_in_overlay(self, key, term):
        assert term in GROCERIES.overlays[key].content.lower()


HOME_IMPROVEMENT_OVERLAY_KEYS = [
    "building_materials",
    "doors_windows",
    "electrical_lighting",
    "flooring",
    "hvac",
    "kitchen_bath",
    "outdoor_garden",
    "paint_finishes",
    "plumbing",
    "tools_equipment",
]


class TestHomeImprovementOverlays:
    def test_home_improvement_has_overlays(self):
        assert len(HOME_IMPROVEMENT.overlays) == 10

    def test_overlay_keys(self):
        assert set(HOME_IMPROVEMENT.overlays.keys()) == set(
            HOME_IMPROVEMENT_OVERLAY_KEYS
        )

    @pytest.mark.parametrize("key", HOME_IMPROVEMENT_OVERLAY_KEYS)
    def test_overlay_content_non_empty(self, key):
        overlay = HOME_IMPROVEMENT.overlays[key]
        assert len(overlay.content) > 50
        assert len(overlay.description) > 10

    def test_electrical_mentions_gfci(self):
        content = HOME_IMPROVEMENT.overlays["electrical_lighting"].content.lower()
        assert "gfci" in content

    def test_plumbing_mentions_pex(self):
        content = HOME_IMPROVEMENT.overlays["plumbing"].content.lower()
        assert "pex" in content

    def test_flooring_mentions_laminate(self):
        content = HOME_IMPROVEMENT.overlays["flooring"].content.lower()
        assert "laminate" in content

    def test_building_materials_mentions_plywood(self):
        content = HOME_IMPROVEMENT.overlays["building_materials"].content.lower()
        assert "plywood" in content

    def test_tools_mentions_drill(self):
        content = HOME_IMPROVEMENT.overlays["tools_equipment"].content.lower()
        assert "drill" in content

    def test_doors_windows_mentions_prehung(self):
        content = HOME_IMPROVEMENT.overlays["doors_windows"].content.lower()
        assert "prehung" in content

    def test_paint_mentions_primer(self):
        content = HOME_IMPROVEMENT.overlays["paint_finishes"].content.lower()
        assert "primer" in content

    def test_hvac_mentions_seer(self):
        content = HOME_IMPROVEMENT.overlays["hvac"].content.lower()
        assert "seer" in content

    def test_kitchen_bath_mentions_faucet(self):
        content = HOME_IMPROVEMENT.overlays["kitchen_bath"].content.lower()
        assert "faucet" in content

    def test_outdoor_mentions_grill(self):
        content = HOME_IMPROVEMENT.overlays["outdoor_garden"].content.lower()
        assert "grill" in content

    def test_core_has_code_compliance(self):
        core = HOME_IMPROVEMENT.core.lower()
        assert "nec" in core
        assert "gfci" in core

    def test_core_has_material_compatibility(self):
        core = HOME_IMPROVEMENT.core.lower()
        assert "pex" in core
        assert "cpvc" in core

    @pytest.mark.parametrize(
        "key,term",
        [
            ("electrical_lighting", "gfci"),
            ("electrical_lighting", "afci"),
            ("electrical_lighting", "nm-b"),
            ("electrical_lighting", "conduit"),
            ("electrical_lighting", "led"),
            ("electrical_lighting", "240v"),
            ("electrical_lighting", "dimmer"),
            ("plumbing", "pex"),
            ("plumbing", "cpvc"),
            ("plumbing", "copper"),
            ("plumbing", "sharkbite"),
            ("plumbing", "ball valve"),
            ("plumbing", "solvent cement"),
            ("plumbing", "gas"),
            ("flooring", "laminate"),
            ("flooring", "luxury vinyl"),
            ("flooring", "hardwood"),
            ("flooring", "tile"),
            ("flooring", "underlayment"),
            ("flooring", "pei"),
            ("building_materials", "plywood"),
            ("building_materials", "osb"),
            ("building_materials", "drywall"),
            ("building_materials", "lvl"),
            ("building_materials", "pressure-treated"),
            ("building_materials", "joist hanger"),
            ("tools_equipment", "drill"),
            ("tools_equipment", "impact driver"),
            ("tools_equipment", "circular saw"),
            ("tools_equipment", "battery"),
            ("tools_equipment", "milwaukee"),
            ("doors_windows", "prehung"),
            ("doors_windows", "slab"),
            ("doors_windows", "double-hung"),
            ("doors_windows", "tempered"),
            ("doors_windows", "casement"),
            ("doors_windows", "low-e"),
            ("paint_finishes", "primer"),
            ("paint_finishes", "stain"),
            ("paint_finishes", "eggshell"),
            ("paint_finishes", "semi-gloss"),
            ("paint_finishes", "latex"),
            ("hvac", "btu"),
            ("hvac", "seer"),
            ("hvac", "furnace"),
            ("hvac", "thermostat"),
            ("hvac", "merv"),
            ("hvac", "r410a"),
            ("kitchen_bath", "faucet"),
            ("kitchen_bath", "dishwasher"),
            ("kitchen_bath", "countertop"),
            ("kitchen_bath", "range hood"),
            ("kitchen_bath", "rough-in"),
            ("outdoor_garden", "grill"),
            ("outdoor_garden", "propane"),
            ("outdoor_garden", "composite"),
            ("outdoor_garden", "irrigation"),
            ("outdoor_garden", "solar"),
            ("outdoor_garden", "mower"),
        ],
    )
    def test_category_terminology_in_overlay(self, key, term):
        assert term in HOME_IMPROVEMENT.overlays[key].content.lower()


INDUSTRIAL_OVERLAY_KEYS = [
    "abrasives",
    "adhesives_sealants",
    "bearings",
    "cutting_tools",
    "electrical",
    "fasteners",
    "hydraulic_fittings_hose",
    "lubrication",
    "material_handling",
    "motors_drives",
    "pipe_valves_fittings",
    "pneumatic",
    "ppe_arc_flash_fr",
    "ppe_hand",
    "ppe_head_eye_face",
    "ppe_respiratory_foot",
    "pumps",
    "raw_materials",
    "seals_gaskets_orings",
    "test_measurement",
    "welding",
    "power_transmission",
]


class TestIndustrialOverlays:
    def test_industrial_has_overlays(self):
        assert len(INDUSTRIAL.overlays) == 22

    def test_overlay_keys(self):
        assert set(INDUSTRIAL.overlays.keys()) == set(INDUSTRIAL_OVERLAY_KEYS)

    @pytest.mark.parametrize("key", INDUSTRIAL_OVERLAY_KEYS)
    def test_overlay_content_non_empty(self, key):
        overlay = INDUSTRIAL.overlays[key]
        assert len(overlay.content) > 50
        assert len(overlay.description) > 10

    def test_fasteners_mentions_unc(self):
        assert "unc" in INDUSTRIAL.overlays["fasteners"].content.lower()

    def test_bearings_mentions_pillow_block(self):
        assert "pillow block" in INDUSTRIAL.overlays["bearings"].content.lower()

    def test_power_transmission_mentions_v_belt(self):
        content = INDUSTRIAL.overlays["power_transmission"].content.lower()
        assert "v-belt" in content

    def test_hydraulic_mentions_jic(self):
        assert "jic" in INDUSTRIAL.overlays["hydraulic_fittings_hose"].content.lower()

    def test_pneumatic_mentions_push_to_connect(self):
        assert "push-to-connect" in INDUSTRIAL.overlays["pneumatic"].content.lower()

    def test_electrical_mentions_conduit(self):
        assert "conduit" in INDUSTRIAL.overlays["electrical"].content.lower()

    def test_motors_drives_mentions_vfd(self):
        assert "vfd" in INDUSTRIAL.overlays["motors_drives"].content.lower()

    def test_pipe_valves_mentions_schedule(self):
        assert "schedule" in INDUSTRIAL.overlays["pipe_valves_fittings"].content.lower()

    def test_pumps_mentions_centrifugal(self):
        assert "centrifugal" in INDUSTRIAL.overlays["pumps"].content.lower()

    def test_ppe_head_eye_face_mentions_z87(self):
        assert "z87" in INDUSTRIAL.overlays["ppe_head_eye_face"].content.lower()

    def test_ppe_hand_mentions_cut(self):
        assert "cut" in INDUSTRIAL.overlays["ppe_hand"].content.lower()

    def test_ppe_arc_flash_mentions_nfpa(self):
        assert "nfpa" in INDUSTRIAL.overlays["ppe_arc_flash_fr"].content.lower()

    def test_ppe_respiratory_foot_mentions_n95(self):
        assert "n95" in INDUSTRIAL.overlays["ppe_respiratory_foot"].content.lower()

    def test_welding_mentions_e7018(self):
        assert "e7018" in INDUSTRIAL.overlays["welding"].content.lower()

    def test_cutting_tools_mentions_insert(self):
        assert "insert" in INDUSTRIAL.overlays["cutting_tools"].content.lower()

    def test_abrasives_mentions_grinding(self):
        assert "grinding" in INDUSTRIAL.overlays["abrasives"].content.lower()

    def test_adhesives_mentions_threadlocker(self):
        content = INDUSTRIAL.overlays["adhesives_sealants"].content.lower()
        assert "threadlocker" in content

    def test_lubrication_mentions_nlgi(self):
        assert "nlgi" in INDUSTRIAL.overlays["lubrication"].content.lower()

    def test_seals_mentions_o_ring(self):
        assert "o-ring" in INDUSTRIAL.overlays["seals_gaskets_orings"].content.lower()

    def test_material_handling_mentions_sling(self):
        assert "sling" in INDUSTRIAL.overlays["material_handling"].content.lower()

    def test_test_measurement_mentions_multimeter(self):
        assert "multimeter" in INDUSTRIAL.overlays["test_measurement"].content.lower()

    def test_raw_materials_mentions_stainless(self):
        assert "stainless" in INDUSTRIAL.overlays["raw_materials"].content.lower()

    def test_core_has_part_number_precision(self):
        core = INDUSTRIAL.core.lower()
        assert "part number" in core

    def test_core_has_system_compatibility(self):
        core = INDUSTRIAL.core.lower()
        assert "npt" in core
        assert "bsp" in core

    @pytest.mark.parametrize(
        "key,term",
        [
            ("fasteners", "unc"),
            ("fasteners", "unf"),
            ("fasteners", "grade 5"),
            ("fasteners", "grade 8"),
            ("fasteners", "18-8"),
            ("fasteners", "hex cap screw"),
            ("bearings", "6205"),
            ("bearings", "pillow block"),
            ("bearings", "2rs"),
            ("bearings", "abec"),
            ("power_transmission", "v-belt"),
            ("power_transmission", "timing belt"),
            ("power_transmission", "roller chain"),
            ("power_transmission", "sheave"),
            ("hydraulic_fittings_hose", "jic"),
            ("hydraulic_fittings_hose", "orfs"),
            ("hydraulic_fittings_hose", "npt"),
            ("hydraulic_fittings_hose", "dash size"),
            ("pneumatic", "push-to-connect"),
            ("pneumatic", "frl"),
            ("pneumatic", "5/2"),
            ("electrical", "thhn"),
            ("electrical", "emt"),
            ("electrical", "nema"),
            ("electrical", "awg"),
            ("motors_drives", "vfd"),
            ("motors_drives", "tefc"),
            ("motors_drives", "frame"),
            ("motors_drives", "nema"),
            ("pipe_valves_fittings", "schedule 40"),
            ("pipe_valves_fittings", "gate valve"),
            ("pipe_valves_fittings", "ball valve"),
            ("pipe_valves_fittings", "flange"),
            ("pumps", "centrifugal"),
            ("pumps", "npsh"),
            ("pumps", "mechanical seal"),
            ("ppe_head_eye_face", "z87"),
            ("ppe_head_eye_face", "nrr"),
            ("ppe_head_eye_face", "hard hat"),
            ("ppe_hand", "cut level"),
            ("ppe_hand", "nitrile"),
            ("ppe_hand", "en 388"),
            ("ppe_arc_flash_fr", "nfpa 70e"),
            ("ppe_arc_flash_fr", "cal/cm"),
            ("ppe_arc_flash_fr", "hi-vis"),
            ("ppe_respiratory_foot", "n95"),
            ("ppe_respiratory_foot", "papr"),
            ("ppe_respiratory_foot", "steel toe"),
            ("welding", "e7018"),
            ("welding", "er70s-6"),
            ("welding", "flux-core"),
            ("welding", "shielding gas"),
            ("cutting_tools", "insert"),
            ("cutting_tools", "cat40"),
            ("cutting_tools", "end mill"),
            ("cutting_tools", "tap"),
            ("abrasives", "grinding wheel"),
            ("abrasives", "flap disc"),
            ("abrasives", "aluminum oxide"),
            ("adhesives_sealants", "threadlocker"),
            ("adhesives_sealants", "loctite"),
            ("adhesives_sealants", "ptfe"),
            ("adhesives_sealants", "epoxy"),
            ("lubrication", "nlgi"),
            ("lubrication", "iso vg"),
            ("lubrication", "hydraulic oil"),
            ("lubrication", "grease"),
            ("seals_gaskets_orings", "o-ring"),
            ("seals_gaskets_orings", "viton"),
            ("seals_gaskets_orings", "buna-n"),
            ("seals_gaskets_orings", "durometer"),
            ("material_handling", "sling"),
            ("material_handling", "shackle"),
            ("material_handling", "caster"),
            ("material_handling", "grade 80"),
            ("test_measurement", "multimeter"),
            ("test_measurement", "cat iii"),
            ("test_measurement", "torque wrench"),
            ("test_measurement", "caliper"),
            ("raw_materials", "1018"),
            ("raw_materials", "304"),
            ("raw_materials", "6061"),
            ("raw_materials", "uhmw"),
        ],
    )
    def test_category_terminology_in_overlay(self, key, term):
        assert term in INDUSTRIAL.overlays[key].content.lower()


MEDICAL_OVERLAY_KEYS = [
    "diabetes_management",
    "dme_mobility_orthopedics",
    "hypodermic_infusion",
    "ppe_hygiene",
    "respiratory_therapy",
    "surgical_instruments",
    "urology_incontinence",
    "wound_care",
]


class TestMedicalOverlays:
    def test_medical_has_overlays(self):
        assert len(MEDICAL.overlays) == 8

    def test_overlay_keys(self):
        assert set(MEDICAL.overlays.keys()) == set(MEDICAL_OVERLAY_KEYS)

    @pytest.mark.parametrize("key", MEDICAL_OVERLAY_KEYS)
    def test_overlay_content_non_empty(self, key):
        overlay = MEDICAL.overlays[key]
        assert len(overlay.content) > 50
        assert len(overlay.description) > 10

    def test_surgical_mentions_scalpel(self):
        assert "scalpel" in MEDICAL.overlays["surgical_instruments"].content.lower()

    def test_respiratory_mentions_cpap(self):
        assert "cpap" in MEDICAL.overlays["respiratory_therapy"].content.lower()

    def test_wound_care_mentions_alginate(self):
        assert "alginate" in MEDICAL.overlays["wound_care"].content.lower()

    def test_ppe_hygiene_mentions_aql(self):
        assert "aql" in MEDICAL.overlays["ppe_hygiene"].content.lower()

    def test_urology_mentions_coude(self):
        content = MEDICAL.overlays["urology_incontinence"].content.lower()
        assert "coud" in content

    def test_diabetes_mentions_cgm(self):
        assert "cgm" in MEDICAL.overlays["diabetes_management"].content.lower()

    def test_dme_mentions_wheelchair(self):
        content = MEDICAL.overlays["dme_mobility_orthopedics"].content.lower()
        assert "wheelchair" in content

    def test_hypodermic_mentions_luer(self):
        assert "luer" in MEDICAL.overlays["hypodermic_infusion"].content.lower()

    def test_core_has_sterility(self):
        core = MEDICAL.core.lower()
        assert "sterile" in core

    def test_core_has_french_sizing(self):
        core = MEDICAL.core.lower()
        assert "french" in core

    @pytest.mark.parametrize(
        "key,term",
        [
            ("surgical_instruments", "scalpel"),
            ("surgical_instruments", "tungsten carbide"),
            ("surgical_instruments", "mayo"),
            ("surgical_instruments", "metzenbaum"),
            ("surgical_instruments", "hemostat"),
            ("respiratory_therapy", "cpap"),
            ("respiratory_therapy", "bipap"),
            ("respiratory_therapy", "oxygen"),
            ("respiratory_therapy", "pulse dose"),
            ("wound_care", "alginate"),
            ("wound_care", "hydrocolloid"),
            ("wound_care", "hydrogel"),
            ("wound_care", "silver"),
            ("ppe_hygiene", "aql"),
            ("ppe_hygiene", "n95"),
            ("ppe_hygiene", "astm"),
            ("ppe_hygiene", "aami"),
            ("urology_incontinence", "foley"),
            ("urology_incontinence", "hydrophilic"),
            ("urology_incontinence", "intermittent"),
            ("diabetes_management", "test strip"),
            ("diabetes_management", "lancet"),
            ("diabetes_management", "cgm"),
            ("dme_mobility_orthopedics", "wheelchair"),
            ("dme_mobility_orthopedics", "rollator"),
            ("dme_mobility_orthopedics", "bariatric"),
            ("hypodermic_infusion", "luer lock"),
            ("hypodermic_infusion", "luer slip"),
            ("hypodermic_infusion", "insulin"),
            ("hypodermic_infusion", "safety"),
        ],
    )
    def test_category_terminology_in_overlay(self, key, term):
        assert term in MEDICAL.overlays[key].content.lower()


MARKETPLACE_OVERLAY_KEYS = [
    "apparel_and_footwear",
    "automotive_parts",
    "baby_and_juvenile",
    "fine_jewelry",
    "graded_collectibles",
    "health_and_supplements",
    "heavy_goods_and_logistics",
    "luxury_goods",
    "physical_media",
    "power_tools",
    "refurbished_electronics",
    "sports_safety_equipment",
    "video_games",
]


class TestMarketplaceOverlays:
    def test_marketplace_has_overlays(self):
        assert len(MARKETPLACE.overlays) == 13

    def test_overlay_keys(self):
        assert set(MARKETPLACE.overlays.keys()) == set(MARKETPLACE_OVERLAY_KEYS)

    @pytest.mark.parametrize("key", MARKETPLACE_OVERLAY_KEYS)
    def test_overlay_content_non_empty(self, key):
        overlay = MARKETPLACE.overlays[key]
        assert len(overlay.content) > 50
        assert len(overlay.description) > 10

    def test_automotive_parts_mentions_fitment(self):
        content = MARKETPLACE.overlays["automotive_parts"].content.lower()
        assert "fitment" in content

    def test_refurbished_mentions_grade(self):
        content = MARKETPLACE.overlays["refurbished_electronics"].content.lower()
        assert "grade a" in content

    def test_graded_collectibles_mentions_psa(self):
        content = MARKETPLACE.overlays["graded_collectibles"].content.lower()
        assert "psa" in content

    def test_luxury_goods_mentions_gray_market(self):
        content = MARKETPLACE.overlays["luxury_goods"].content.lower()
        assert "gray market" in content

    def test_fine_jewelry_mentions_lab_grown(self):
        content = MARKETPLACE.overlays["fine_jewelry"].content.lower()
        assert "lab-grown" in content

    def test_power_tools_mentions_brushless(self):
        content = MARKETPLACE.overlays["power_tools"].content.lower()
        assert "brushless" in content

    def test_apparel_mentions_vanity_sizing(self):
        content = MARKETPLACE.overlays["apparel_and_footwear"].content.lower()
        assert "vanity sizing" in content

    def test_physical_media_mentions_goldmine(self):
        content = MARKETPLACE.overlays["physical_media"].content.lower()
        assert "goldmine" in content

    def test_baby_mentions_cpsc(self):
        content = MARKETPLACE.overlays["baby_and_juvenile"].content.lower()
        assert "cpsc" in content

    def test_health_mentions_nsf(self):
        content = MARKETPLACE.overlays["health_and_supplements"].content.lower()
        assert "nsf" in content

    def test_video_games_mentions_region_locked(self):
        content = MARKETPLACE.overlays["video_games"].content.lower()
        assert "region-locked" in content

    def test_heavy_goods_mentions_ltl(self):
        content = MARKETPLACE.overlays["heavy_goods_and_logistics"].content.lower()
        assert "ltl" in content

    def test_sports_safety_mentions_nocsae(self):
        content = MARKETPLACE.overlays["sports_safety_equipment"].content.lower()
        assert "nocsae" in content

    def test_core_has_offer_level_relevance(self):
        core = MARKETPLACE.core.lower()
        assert "offer" in core
        assert "seller" in core

    def test_core_has_condition_alignment(self):
        core = MARKETPLACE.core.lower()
        assert "condition" in core
        assert "refurbished" in core

    @pytest.mark.parametrize(
        "key,term",
        [
            ("automotive_parts", "fitment"),
            ("automotive_parts", "aces"),
            ("automotive_parts", "core charge"),
            ("automotive_parts", "oem"),
            ("automotive_parts", "universal"),
            ("refurbished_electronics", "grade a"),
            ("refurbished_electronics", "open-box"),
            ("refurbished_electronics", "renewed"),
            ("refurbished_electronics", "warranty"),
            ("graded_collectibles", "psa"),
            ("graded_collectibles", "bgs"),
            ("graded_collectibles", "cgc"),
            ("graded_collectibles", "universal"),
            ("graded_collectibles", "restored"),
            ("graded_collectibles", "coverless"),
            ("luxury_goods", "gray market"),
            ("luxury_goods", "date code"),
            ("luxury_goods", "nwt"),
            ("luxury_goods", "euc"),
            ("luxury_goods", "guc"),
            ("fine_jewelry", "lab-grown"),
            ("fine_jewelry", "gia"),
            ("fine_jewelry", "igi"),
            ("fine_jewelry", "grading report"),
            ("fine_jewelry", "4cs"),
            ("power_tools", "20v max"),
            ("power_tools", "brushless"),
            ("power_tools", "bare tool"),
            ("apparel_and_footwear", "vanity sizing"),
            ("apparel_and_footwear", "nwt"),
            ("apparel_and_footwear", "euc"),
            ("physical_media", "goldmine"),
            ("physical_media", "dead wax"),
            ("physical_media", "matrix number"),
            ("physical_media", "first edition"),
            ("baby_and_juvenile", "cpsc"),
            ("baby_and_juvenile", "astm"),
            ("baby_and_juvenile", "jpma"),
            ("health_and_supplements", "nsf"),
            ("health_and_supplements", "usp"),
            ("health_and_supplements", "fefo"),
            ("video_games", "ntsc"),
            ("video_games", "pal"),
            ("video_games", "region-locked"),
            ("heavy_goods_and_logistics", "flat-pack"),
            ("heavy_goods_and_logistics", "ltl"),
            ("heavy_goods_and_logistics", "liftgate"),
            ("heavy_goods_and_logistics", "white-glove"),
            ("sports_safety_equipment", "nocsae"),
            ("sports_safety_equipment", "sei"),
        ],
    )
    def test_category_terminology_in_overlay(self, key, term):
        assert term in MARKETPLACE.overlays[key].content.lower()


OFFICE_SUPPLIES_OVERLAY_KEYS = [
    "binding_and_presentation",
    "filing_and_organization",
    "ink_and_toner",
    "janitorial_and_breakroom",
    "mailing_and_packaging",
    "office_furniture",
    "paper_and_media",
    "shredders_and_data_destruction",
    "thermal_printers_and_labels",
    "writing_instruments",
]


class TestOfficeSuppliesOverlays:
    def test_office_supplies_has_overlays(self):
        assert len(OFFICE_SUPPLIES.overlays) == 10

    def test_overlay_keys(self):
        assert set(OFFICE_SUPPLIES.overlays.keys()) == set(OFFICE_SUPPLIES_OVERLAY_KEYS)

    @pytest.mark.parametrize("key", OFFICE_SUPPLIES_OVERLAY_KEYS)
    def test_overlay_content_non_empty(self, key):
        overlay = OFFICE_SUPPLIES.overlays[key]
        assert len(overlay.content) > 50
        assert len(overlay.description) > 10

    def test_ink_and_toner_mentions_oem(self):
        content = OFFICE_SUPPLIES.overlays["ink_and_toner"].content.lower()
        assert "oem" in content

    def test_paper_mentions_gsm(self):
        content = OFFICE_SUPPLIES.overlays["paper_and_media"].content.lower()
        assert "gsm" in content

    def test_writing_instruments_mentions_refill(self):
        content = OFFICE_SUPPLIES.overlays["writing_instruments"].content.lower()
        assert "refill" in content

    def test_office_furniture_mentions_bifma(self):
        content = OFFICE_SUPPLIES.overlays["office_furniture"].content.lower()
        assert "bifma" in content

    def test_shredders_mentions_din(self):
        overlay = OFFICE_SUPPLIES.overlays["shredders_and_data_destruction"]
        assert "din 66399" in overlay.content.lower()

    def test_mailing_mentions_corrugated(self):
        content = OFFICE_SUPPLIES.overlays["mailing_and_packaging"].content.lower()
        assert "corrugated" in content

    def test_binding_mentions_wire_o(self):
        content = OFFICE_SUPPLIES.overlays["binding_and_presentation"].content.lower()
        assert "wire-o" in content

    def test_filing_mentions_lateral(self):
        content = OFFICE_SUPPLIES.overlays["filing_and_organization"].content.lower()
        assert "lateral" in content

    def test_thermal_printers_mentions_dymo(self):
        overlay = OFFICE_SUPPLIES.overlays["thermal_printers_and_labels"]
        assert "dymo" in overlay.content.lower()

    def test_janitorial_mentions_z_fold(self):
        content = OFFICE_SUPPLIES.overlays["janitorial_and_breakroom"].content.lower()
        assert "z-fold" in content

    def test_core_has_device_compatibility(self):
        core = OFFICE_SUPPLIES.core.lower()
        assert "compatibility" in core
        assert "device" in core

    def test_core_has_packaging_tiers(self):
        core = OFFICE_SUPPLIES.core.lower()
        assert "case" in core
        assert "box" in core

    @pytest.mark.parametrize(
        "key,term",
        [
            ("ink_and_toner", "oem"),
            ("ink_and_toner", "compatible"),
            ("ink_and_toner", "remanufactured"),
            ("ink_and_toner", "high yield"),
            ("ink_and_toner", "iso"),
            ("paper_and_media", "gsm"),
            ("paper_and_media", "brightness"),
            ("paper_and_media", "laser"),
            ("paper_and_media", "inkjet"),
            ("paper_and_media", "legal"),
            ("paper_and_media", "tabloid"),
            ("writing_instruments", "refill"),
            ("writing_instruments", "archival"),
            ("writing_instruments", "mechanical pencil"),
            ("writing_instruments", "hb"),
            ("writing_instruments", "ap seal"),
            ("office_furniture", "bifma"),
            ("office_furniture", "x5.1"),
            ("office_furniture", "x5.11"),
            ("office_furniture", "cal 117"),
            ("office_furniture", "cal 133"),
            ("shredders_and_data_destruction", "din 66399"),
            ("shredders_and_data_destruction", "p-4"),
            ("shredders_and_data_destruction", "micro-cut"),
            ("shredders_and_data_destruction", "nsa"),
            ("shredders_and_data_destruction", "hipaa"),
            ("mailing_and_packaging", "#10"),
            ("mailing_and_packaging", "corrugated"),
            ("mailing_and_packaging", "c-flute"),
            ("mailing_and_packaging", "e-flute"),
            ("mailing_and_packaging", "acrylic"),
            ("binding_and_presentation", "comb binding"),
            ("binding_and_presentation", "wire-o"),
            ("binding_and_presentation", "velobind"),
            ("binding_and_presentation", "laminating"),
            ("filing_and_organization", "lateral"),
            ("filing_and_organization", "vertical"),
            ("filing_and_organization", "hanging folder"),
            ("filing_and_organization", "1/3-cut"),
            ("thermal_printers_and_labels", "dymo"),
            ("thermal_printers_and_labels", "direct thermal"),
            ("thermal_printers_and_labels", "thermal transfer"),
            ("thermal_printers_and_labels", "avery"),
            ("janitorial_and_breakroom", "z-fold"),
            ("janitorial_and_breakroom", "c-fold"),
            ("janitorial_and_breakroom", "centerpull"),
            ("janitorial_and_breakroom", "hdpe"),
        ],
    )
    def test_category_terminology_in_overlay(self, key, term):
        assert term in OFFICE_SUPPLIES.overlays[key].content.lower()


PET_SUPPLIES_OVERLAY_KEYS = [
    "aquarium_hardware_and_filtration",
    "aquatic_livestock_and_medications",
    "avian_habitat_and_safety",
    "dog_training_and_walking_gear",
    "equine_tack_and_feed",
    "feline_habitat_and_litter",
    "grooming_equipment",
    "otc_pet_nutrition",
    "pharmacy_and_parasiticides",
    "reptile_husbandry_and_habitat",
    "small_mammal_husbandry",
    "veterinary_prescription_diets",
]


class TestPetSuppliesOverlays:
    def test_pet_supplies_has_overlays(self):
        assert len(PET_SUPPLIES.overlays) == 12

    def test_overlay_keys(self):
        assert set(PET_SUPPLIES.overlays.keys()) == set(PET_SUPPLIES_OVERLAY_KEYS)

    @pytest.mark.parametrize("key", PET_SUPPLIES_OVERLAY_KEYS)
    def test_overlay_content_non_empty(self, key):
        overlay = PET_SUPPLIES.overlays[key]
        assert len(overlay.content) > 50
        assert len(overlay.description) > 10

    def test_otc_nutrition_mentions_aafco(self):
        content = PET_SUPPLIES.overlays["otc_pet_nutrition"].content.lower()
        assert "aafco" in content

    def test_veterinary_diets_mentions_prescription(self):
        overlay = PET_SUPPLIES.overlays["veterinary_prescription_diets"]
        assert "prescription" in overlay.content.lower()

    def test_pharmacy_mentions_permethrin(self):
        overlay = PET_SUPPLIES.overlays["pharmacy_and_parasiticides"]
        assert "permethrin" in overlay.content.lower()

    def test_dog_training_mentions_martingale(self):
        overlay = PET_SUPPLIES.overlays["dog_training_and_walking_gear"]
        assert "martingale" in overlay.content.lower()

    def test_grooming_mentions_clipper(self):
        content = PET_SUPPLIES.overlays["grooming_equipment"].content.lower()
        assert "clipper" in content

    def test_feline_mentions_bentonite(self):
        content = PET_SUPPLIES.overlays["feline_habitat_and_litter"].content.lower()
        assert "bentonite" in content

    def test_aquarium_mentions_par(self):
        overlay = PET_SUPPLIES.overlays["aquarium_hardware_and_filtration"]
        assert "par" in overlay.content.lower()

    def test_aquatic_mentions_copper(self):
        overlay = PET_SUPPLIES.overlays["aquatic_livestock_and_medications"]
        assert "copper" in overlay.content.lower()

    def test_reptile_mentions_uvb(self):
        overlay = PET_SUPPLIES.overlays["reptile_husbandry_and_habitat"]
        assert "uvb" in overlay.content.lower()

    def test_avian_mentions_ptfe(self):
        content = PET_SUPPLIES.overlays["avian_habitat_and_safety"].content.lower()
        assert "ptfe" in content

    def test_small_mammal_mentions_vitamin_c(self):
        content = PET_SUPPLIES.overlays["small_mammal_husbandry"].content.lower()
        assert "vitamin c" in content

    def test_equine_mentions_western(self):
        content = PET_SUPPLIES.overlays["equine_tack_and_feed"].content.lower()
        assert "western" in content

    def test_core_has_species_gate(self):
        core = PET_SUPPLIES.core.lower()
        assert "species" in core

    def test_core_has_breed_size(self):
        core = PET_SUPPLIES.core.lower()
        assert "breed size" in core

    @pytest.mark.parametrize(
        "key,term",
        [
            ("otc_pet_nutrition", "aafco"),
            ("otc_pet_nutrition", "large breed puppy"),
            ("otc_pet_nutrition", "human-grade"),
            ("otc_pet_nutrition", "grain-free"),
            ("otc_pet_nutrition", "topper"),
            ("veterinary_prescription_diets", "k/d"),
            ("veterinary_prescription_diets", "renal"),
            ("veterinary_prescription_diets", "royal canin"),
            ("veterinary_prescription_diets", "hydrolyzed"),
            ("pharmacy_and_parasiticides", "permethrin"),
            ("pharmacy_and_parasiticides", "isoxazoline"),
            ("pharmacy_and_parasiticides", "bravecto"),
            ("pharmacy_and_parasiticides", "mcg"),
            ("dog_training_and_walking_gear", "girth"),
            ("dog_training_and_walking_gear", "martingale"),
            ("dog_training_and_walking_gear", "head halter"),
            ("dog_training_and_walking_gear", "front-clip"),
            ("grooming_equipment", "#40"),
            ("grooming_equipment", "#10"),
            ("grooming_equipment", "a-5"),
            ("grooming_equipment", "spm"),
            ("feline_habitat_and_litter", "bentonite"),
            ("feline_habitat_and_litter", "silica"),
            ("feline_habitat_and_litter", "enzymatic"),
            ("feline_habitat_and_litter", "sisal"),
            ("aquarium_hardware_and_filtration", "mechanical"),
            ("aquarium_hardware_and_filtration", "biological"),
            ("aquarium_hardware_and_filtration", "par"),
            ("aquarium_hardware_and_filtration", "protein skimmer"),
            ("aquatic_livestock_and_medications", "copper"),
            ("aquatic_livestock_and_medications", "ammonia"),
            ("aquatic_livestock_and_medications", "nitrogen cycle"),
            ("aquatic_livestock_and_medications", "reef safe"),
            ("reptile_husbandry_and_habitat", "uvb"),
            ("reptile_husbandry_and_habitat", "metabolic bone disease"),
            ("reptile_husbandry_and_habitat", "impaction"),
            ("reptile_husbandry_and_habitat", "gut-loading"),
            ("avian_habitat_and_safety", "ptfe"),
            ("avian_habitat_and_safety", "zinc"),
            ("avian_habitat_and_safety", "bar spacing"),
            ("avian_habitat_and_safety", "macaw"),
            ("small_mammal_husbandry", "vitamin c"),
            ("small_mammal_husbandry", "guinea pig"),
            ("small_mammal_husbandry", "cedar"),
            ("small_mammal_husbandry", "timothy"),
            ("small_mammal_husbandry", "alfalfa"),
            ("equine_tack_and_feed", "western"),
            ("equine_tack_and_feed", "english"),
            ("equine_tack_and_feed", "snaffle"),
            ("equine_tack_and_feed", "curb"),
            ("equine_tack_and_feed", "senior"),
        ],
    )
    def test_category_terminology_in_overlay(self, key, term):
        assert term in PET_SUPPLIES.overlays[key].content.lower()


SPORTING_GOODS_OVERLAY_KEYS = [
    "archery_bows_and_arrows",
    "baseball_and_softball_gloves",
    "camping_shelter_and_sleep",
    "climbing_and_mountaineering",
    "competitive_swimwear",
    "cycling_drivetrains_and_components",
    "field_sports_footwear",
    "fishing_rods_and_reels",
    "fitness_and_strength_training",
    "golf_clubs_and_wedges",
    "hockey_skates_and_sticks",
    "lacrosse_heads",
    "racket_and_paddle_sports",
    "team_licensed_jerseys",
    "volleyball_equipment",
    "watersports_flotation",
    "winter_sports_hardgoods",
]


class TestSportingGoodsOverlays:
    def test_sporting_goods_has_overlays(self):
        assert len(SPORTING_GOODS.overlays) == 17

    def test_overlay_keys(self):
        assert set(SPORTING_GOODS.overlays.keys()) == set(SPORTING_GOODS_OVERLAY_KEYS)

    @pytest.mark.parametrize("key", SPORTING_GOODS_OVERLAY_KEYS)
    def test_overlay_content_non_empty(self, key):
        overlay = SPORTING_GOODS.overlays[key]
        assert len(overlay.content) > 50
        assert len(overlay.description) > 10

    def test_golf_mentions_bounce(self):
        content = SPORTING_GOODS.overlays["golf_clubs_and_wedges"].content.lower()
        assert "bounce" in content

    def test_cycling_mentions_shimano(self):
        key = "cycling_drivetrains_and_components"
        assert "shimano" in SPORTING_GOODS.overlays[key].content.lower()

    def test_winter_sports_mentions_din(self):
        content = SPORTING_GOODS.overlays["winter_sports_hardgoods"].content.lower()
        assert "din" in content

    def test_fishing_mentions_baitcasting(self):
        content = SPORTING_GOODS.overlays["fishing_rods_and_reels"].content.lower()
        assert "baitcasting" in content

    def test_archery_mentions_spine(self):
        content = SPORTING_GOODS.overlays["archery_bows_and_arrows"].content.lower()
        assert "spine" in content

    def test_racket_mentions_swingweight(self):
        content = SPORTING_GOODS.overlays["racket_and_paddle_sports"].content.lower()
        assert "swingweight" in content

    def test_field_sports_mentions_fg(self):
        content = SPORTING_GOODS.overlays["field_sports_footwear"].content.lower()
        assert "fg" in content

    def test_jerseys_mentions_elite(self):
        content = SPORTING_GOODS.overlays["team_licensed_jerseys"].content.lower()
        assert "elite" in content

    def test_hockey_mentions_flex(self):
        content = SPORTING_GOODS.overlays["hockey_skates_and_sticks"].content.lower()
        assert "flex" in content

    def test_watersports_mentions_uscg(self):
        content = SPORTING_GOODS.overlays["watersports_flotation"].content.lower()
        assert "uscg" in content

    def test_camping_mentions_r_value(self):
        content = SPORTING_GOODS.overlays["camping_shelter_and_sleep"].content.lower()
        assert "r-value" in content

    def test_lacrosse_mentions_offensive(self):
        content = SPORTING_GOODS.overlays["lacrosse_heads"].content.lower()
        assert "offensive" in content

    def test_volleyball_mentions_indoor(self):
        content = SPORTING_GOODS.overlays["volleyball_equipment"].content.lower()
        assert "indoor" in content

    def test_swimwear_mentions_fina(self):
        content = SPORTING_GOODS.overlays["competitive_swimwear"].content.lower()
        assert "fina" in content

    def test_climbing_mentions_uiaa(self):
        overlay = SPORTING_GOODS.overlays["climbing_and_mountaineering"]
        assert "uiaa" in overlay.content.lower()

    def test_baseball_mentions_kip(self):
        overlay = SPORTING_GOODS.overlays["baseball_and_softball_gloves"]
        assert "kip" in overlay.content.lower()

    def test_fitness_mentions_flywheel(self):
        overlay = SPORTING_GOODS.overlays["fitness_and_strength_training"]
        assert "flywheel" in overlay.content.lower()

    def test_core_has_sport_gate(self):
        core = SPORTING_GOODS.core.lower()
        assert "sport" in core

    def test_core_has_certification(self):
        core = SPORTING_GOODS.core.lower()
        assert "certification" in core
        assert "nocsae" in core

    @pytest.mark.parametrize(
        "key,term",
        [
            ("golf_clubs_and_wedges", "bounce"),
            ("golf_clubs_and_wedges", "grind"),
            ("golf_clubs_and_wedges", "shaft flex"),
            ("golf_clubs_and_wedges", "pitching wedge"),
            ("golf_clubs_and_wedges", "lob wedge"),
            ("cycling_drivetrains_and_components", "shimano"),
            ("cycling_drivetrains_and_components", "sram"),
            ("cycling_drivetrains_and_components", "campagnolo"),
            ("cycling_drivetrains_and_components", "dura-ace"),
            ("cycling_drivetrains_and_components", "di2"),
            ("winter_sports_hardgoods", "gripwalk"),
            ("winter_sports_hardgoods", "din"),
            ("winter_sports_hardgoods", "mondopoint"),
            ("winter_sports_hardgoods", "iso 5355"),
            ("fishing_rods_and_reels", "baitcasting"),
            ("fishing_rods_and_reels", "spinning"),
            ("fishing_rods_and_reels", "saltwater"),
            ("fishing_rods_and_reels", "ultra-light"),
            ("archery_bows_and_arrows", "spine"),
            ("archery_bows_and_arrows", "ilf"),
            ("archery_bows_and_arrows", "amo"),
            ("archery_bows_and_arrows", "crossbow"),
            ("racket_and_paddle_sports", "swingweight"),
            ("racket_and_paddle_sports", "grip size"),
            ("racket_and_paddle_sports", "nomex"),
            ("racket_and_paddle_sports", "pickleball"),
            ("field_sports_footwear", "fg"),
            ("field_sports_footwear", "ag"),
            ("field_sports_footwear", "sg"),
            ("field_sports_footwear", "toe stud"),
            ("team_licensed_jerseys", "elite"),
            ("team_licensed_jerseys", "swingman"),
            ("team_licensed_jerseys", "replica"),
            ("team_licensed_jerseys", "screen-printed"),
            ("hockey_skates_and_sticks", "fit 1"),
            ("hockey_skates_and_sticks", "flex"),
            ("hockey_skates_and_sticks", "kickpoint"),
            ("hockey_skates_and_sticks", "low-kick"),
            ("watersports_flotation", "uscg"),
            ("watersports_flotation", "type iii"),
            ("watersports_flotation", "type iv"),
            ("watersports_flotation", "inflatable"),
            ("camping_shelter_and_sleep", "comfort rating"),
            ("camping_shelter_and_sleep", "r-value"),
            ("camping_shelter_and_sleep", "hypothermia"),
            ("lacrosse_heads", "offensive"),
            ("lacrosse_heads", "defensive"),
            ("lacrosse_heads", "face shape"),
            ("lacrosse_heads", "throat"),
            ("volleyball_equipment", "indoor"),
            ("volleyball_equipment", "outdoor"),
            ("volleyball_equipment", "leather"),
            ("volleyball_equipment", "pressure"),
            ("competitive_swimwear", "fina"),
            ("competitive_swimwear", "technical suit"),
            ("competitive_swimwear", "bonded"),
            ("climbing_and_mountaineering", "uiaa"),
            ("climbing_and_mountaineering", "iso 9001"),
            ("baseball_and_softball_gloves", "kip"),
            ("baseball_and_softball_gloves", "steerhide"),
            ("baseball_and_softball_gloves", "cowhide"),
            ("baseball_and_softball_gloves", "break-in"),
            ("fitness_and_strength_training", "flywheel"),
            ("fitness_and_strength_training", "power cage"),
            ("fitness_and_strength_training", "squat stand"),
            ("fitness_and_strength_training", "spin bike"),
        ],
    )
    def test_category_terminology_in_overlay(self, key, term):
        assert term in SPORTING_GOODS.overlays[key].content.lower()


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
