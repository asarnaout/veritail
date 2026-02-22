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

    @pytest.mark.parametrize(
        "name",
        [
            n
            for n in ALL_BUILTINS
            if n not in {"foodservice", "automotive", "beauty", "electronics"}
        ],
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
