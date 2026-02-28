# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed

- `--output` flag in `veritail generate-queries` now defaults to `queries.csv` instead of being required.
- `veritail generate-queries` now refuses to overwrite an existing file by default. Use `--append` to merge new queries into an existing file (with automatic deduplication) or `--force` to replace it.

## [0.3.0] - 2026-02-28

### Changed

- `veritail generate-queries` now outputs a single-column CSV with only the `query` column. The `type`, `category`, and `source` columns have been removed — query types are automatically classified by the LLM during evaluation, making pre-generated types redundant.
- Edge case query generation now covers metric units, non-standard measurements, negations, qualifier words, and accessory-for-product queries.

## [0.2.2] - 2026-02-23

### Added

- Static landing page served via GitHub Pages from `docs/`

### Changed

- Metric names in reports now use proper casing: NDCG@5, NDCG@10, MRR, MAP, P@5, P@10, Attribute Match@5, Attribute Match@10
- Query type labels in reports now use title case: Attribute, Broad, Long-Tail, Navigational
- Deterministic check names in reports now use human-friendly labels (e.g. "Keyword Coverage", "Near-Duplicate Products", "Product Title Length") — applies to both search and autocomplete reports
- Comparison report: removed redundant Delta column from metrics table (% Change is sufficient) and replaced Delta with % Change in metrics-by-query-type tables
- Comparison report: query names in Biggest Improvements/Regressions tables are now clickable to expand side-by-side results (replaces separate "Show results side-by-side" row)

## [0.2.1] - 2026-02-22

### Fixed

- Price outlier detection now works correctly for small result sets (3-7 results) using Modified Z-Score (MAD), and uses properly interpolated quartiles for IQR (8+ results)
- Reusing a `--config-name` no longer silently overwrites previous results. The CLI now auto-appends a `.2`, `.3`, … suffix when the experiment directory already exists and warns the user. `--resume` is unaffected and continues to reuse the existing directory as before.

## [0.2.0] - 2026-02-22

### Changed

- Externalized all LLM prompt strings (5 system prompts + 14 vertical cores + 232 overlay contents) from inline Python to standalone markdown files under `src/veritail/prompts/`. Python modules now load prompts via `load_prompt()` with LRU caching. No behavioral change — loaded content is identical to the previous inline strings.

### Breaking Changes

- Removed `--rubric` CLI flag and custom rubric support. The built-in ecommerce relevance rubric is now always used. The `rubric` field has been removed from `ExperimentConfig` and run metadata. Resume config mismatch checks no longer include rubric.

### Removed

- `--rubric` CLI option
- `load_rubric()` dynamic rubric loader from `veritail.rubrics`
- `rubric` field from `ExperimentConfig`
- `docs/custom-rubrics.md` replaced by `docs/enterprise-context.md` (enterprise context documentation preserved)

### Added

- `--verbose` / `-v` CLI flag enables debug logging to stderr for pipeline tracing, LLM provider selection, token usage, classification results, judgment scores, check summaries, batch operations, and metric values
- Tiered vertical overlays: verticals support a core system prompt plus category-specific overlays injected per-query into the user prompt, reducing context rot and cost for deep domain knowledge
- New types: `VerticalOverlay` and `VerticalContext` for structured vertical definitions
- `QueryEntry.overlay` field for classified overlay keys in query CSV/JSON files
- Classifier determines query type and overlay key in a single LLM call (zero extra cost)
- Overlay classifier supports `none` option for queries outside all domain overlays, with bias-toward-matching to prevent overuse
- Foodservice vertical split into core + 26 category overlays: beverage_equipment, beverages, cooking, dairy_eggs, disposables, dry_goods, food_prep, furniture, ice_machines, janitorial, frozen_dessert_equipment, plumbing, prepared_foods, produce, proteins, refrigeration, replacement_parts, serving_holding, smallwares, storage_transport, tabletop, underbar, ventilation, warewash, waste_reduction, water_filtration
- Foodservice terminology equivalences split between core (cross-cutting terms) and overlays (category-specific terms) to reduce context dilution
- 6 new foodservice category overlays: ice_machines (ice makers, bins, dispensers — split from refrigeration), underbar (bar workstations, ice bins, speed rails, blender stations), water_filtration (commercial water filters for equipment protection), replacement_parts (OEM parts, repair kits, maintenance items), plumbing (sinks, faucets, pre-rinse units, grease traps), waste_reduction (garbage disposers, pulpers, compactors, oil disposal)
- Automotive vertical split into core + 13 category overlays: general, oil_change, fluids_and_chemicals, brakes_and_friction, wheels_tires_tpms, batteries_starting_charging, lighting_and_visibility, engine_ignition_and_sensors, suspension_steering_and_hubs, exhaust_and_emissions, hvac_air_conditioning, body_collision_paint_glass, accessories_and_tools
- Beauty vertical split into core + 22 category overlays: complexion_makeup, eye_makeup, lip_products, cheek_color_contour, makeup_tools, cleansers_makeup_removal, exfoliants_peels, acne_and_breakouts, retinoids_antiaging, brightening_dark_spots, hydration_barrier_repair, masks_and_treatments, sunscreen_spf, sunless_tanning, shampoo_conditioner, textured_curl_hair, hair_color_toning, hair_styling_and_tools, fragrance, nails, body_care_personal, gift_sets_kits
- Electronics vertical split into core + 31 category overlays: gaming_desktop_pcs, office_desktops_workstations_aio_mini, gaming_laptops, productivity_laptops_ultrabooks, macbooks, tablets_and_ereaders, wearables, pc_cpus, pc_gpus, motherboards, memory_ram, storage_internal, external_storage, memory_cards_and_flash, power_supplies, pc_cases_and_cooling, monitors, tvs_and_projectors, headphones_and_earbuds, home_audio, networking, smart_home, smartphones, device_specific_protection, charging_cables_and_adapters, cameras_and_kits, camera_lenses, printers_and_scanners, printer_ink_and_toner, gaming_consoles, vr_headsets
- Fashion vertical split into core + 13 category overlays: sneakers_athletic_shoes, boots, sandals_slides, heels_and_dress_shoes, denim_jeans, intimates_bras_lingerie, activewear_athleisure, outerwear_rain_down, tailored_menswear, swimwear_upf, kids_baby_apparel, jewelry_precious_metals, resale_vintage
- Furniture vertical split into core + 16 category overlays: sofas_sectionals, motion_seating, sleepers_daybeds_futons, beds_frames_headboards, mattresses_toppers_bases, casegoods_storage, dining_tables_sets, chairs_stools_benches, home_office, outdoor_patio, bathroom_vanities, makeup_vanities_dressing_tables, media_consoles_tv_stands, rugs, nursery_kids, commercial_contract
- Groceries vertical split into core + 20 category overlays: nutrition_free_from, produce_fresh, meat_poultry, seafood_shellfish, deli_prepared, dairy_eggs, bakery_bread, frozen_foods, pantry_cooking, snacks_candy, beverages_soft_drinks, coffee_tea, cleaning_disinfectants, laundry, paper_disposables_trash, health_otc_vitamins, personal_care_beauty, baby_care, pet_supplies, adult_beverages_alcohol
- Home improvement vertical split into core + 10 category overlays: electrical_lighting, plumbing, flooring, building_materials, tools_equipment, doors_windows, paint_finishes, hvac, kitchen_bath, outdoor_garden
- Industrial vertical split into core + 22 category overlays: fasteners, bearings, power_transmission, hydraulic_fittings_hose, pneumatic, electrical, motors_drives, pipe_valves_fittings, pumps, ppe_head_eye_face, ppe_hand, ppe_arc_flash_fr, ppe_respiratory_foot, welding, cutting_tools, abrasives, adhesives_sealants, lubrication, seals_gaskets_orings, material_handling, test_measurement, raw_materials
- Medical vertical split into core + 8 category overlays: surgical_instruments, respiratory_therapy, wound_care, ppe_hygiene, urology_incontinence, diabetes_management, dme_mobility_orthopedics, hypodermic_infusion
- Marketplace vertical split into core + 13 category overlays: automotive_parts, refurbished_electronics, graded_collectibles, luxury_goods, fine_jewelry, power_tools, apparel_and_footwear, physical_media, baby_and_juvenile, health_and_supplements, video_games, heavy_goods_and_logistics, sports_safety_equipment
- Office supplies vertical split into core + 10 category overlays: ink_and_toner, paper_and_media, writing_instruments, office_furniture, shredders_and_data_destruction, mailing_and_packaging, binding_and_presentation, filing_and_organization, thermal_printers_and_labels, janitorial_and_breakroom
- Pet supplies vertical split into core + 12 category overlays: otc_pet_nutrition, veterinary_prescription_diets, pharmacy_and_parasiticides, dog_training_and_walking_gear, grooming_equipment, feline_habitat_and_litter, aquarium_hardware_and_filtration, aquatic_livestock_and_medications, reptile_husbandry_and_habitat, avian_habitat_and_safety, small_mammal_husbandry, equine_tack_and_feed
- Sporting goods vertical split into core + 17 category overlays: golf_clubs_and_wedges, cycling_drivetrains_and_components, winter_sports_hardgoods, fishing_rods_and_reels, archery_bows_and_arrows, racket_and_paddle_sports, field_sports_footwear, team_licensed_jerseys, hockey_skates_and_sticks, watersports_flotation, camping_shelter_and_sleep, lacrosse_heads, volleyball_equipment, competitive_swimwear, climbing_and_mountaineering, baseball_and_softball_gloves, fitness_and_strength_training

### Changed

- Beverage equipment overlay renamed from `beverage` to `beverage_equipment` to distinguish from new `beverages` consumable overlay; soft serve moved to new frozen_dessert_equipment overlay
- Smallwares overlay: disposables moved to new disposables overlay; smallwares now focuses on durable kitchen tools, pans, and food storage
- All foodservice overlay content rewritten to be more concise and focused on hard constraints; verbose terminology glossaries replaced with short key-term lists
- Ice machines split out of the `refrigeration` overlay into a dedicated `ice_machines` overlay
- Automotive vertical core rewritten with tiered scoring structure (hard gates, significant penalties, soft signals, calibration examples); regulatory and fluid constraints tightened to "when requested" phrasing

- `load_vertical()` returns `VerticalContext` instead of `str`; custom file verticals are wrapped automatically
- Classification pre-pass runs for all queries when overlays are available (to assign overlay keys), preserving pre-existing query types
- Batch checkpoint expanded to include overlay key (backward compatible with old checkpoints)

## [0.1.1] - 2026-02-20

### Fixed

- `.env` file was not loaded when veritail was installed from PyPI. `load_dotenv()` was searching from the package directory in `site-packages` instead of the user's current working directory.

## [0.1.0] - 2026-02-20

### Added

**Core evaluation pipeline**
- LLM-as-a-judge relevance scoring on a 0–3 scale for query-result pairs
- IR metrics: NDCG@5/10, MRR, MAP, P@5/10, and Attribute Match Rate@5/10
- Per-query and per-query-type metric breakdowns (navigational, broad, long-tail, attribute)
- Automatic query type classification when types are not provided

**Deterministic checks**
- Zero results, result count, text overlap, price outliers, duplicate products, title length, and out-of-stock prominence checks
- Custom check support via `--checks` for user-provided deterministic logic

**Query correction evaluation**
- Detects when a search engine returns results for a corrected query
- LLM judge evaluates whether each correction was appropriate or unnecessary

**Autocomplete evaluation**
- Deterministic prefix checks (completions must start with the prefix, no duplicates, etc.)
- Optional LLM semantic evaluation scoring suggestion relevance and diversity on a 0–3 scale

**Dual-config (A/B) comparison**
- Side-by-side evaluation of two search configurations
- Result set overlap, rank correlation, and per-query NDCG delta
- Winners/losers tables and position-shift analysis

**Batch API support**
- `--batch` flag to use provider batch APIs (OpenAI, Anthropic, Gemini) for ~50% cost reduction
- `--resume` flag to recover interrupted batch runs from a checkpoint

**LLM providers**
- OpenAI (default, also supports any OpenAI-compatible endpoint via `--llm-base-url`)
- Anthropic Claude (optional dependency, with prompt caching)
- Google Gemini (optional dependency)

**Domain verticals**
- 14 built-in domain-specific judge contexts: automotive, beauty, electronics, fashion, foodservice, furniture, groceries, home improvement, industrial, marketplace, medical, office supplies, pet supplies, sporting goods
- `veritail vertical list` and `veritail vertical show` commands
- Custom vertical support via file path

**Reporting**
- HTML reports with judgment drill-down, score distribution, NDCG histogram, and position chart
- Comparison HTML reports with scatter plots, score distribution comparison, and correction tables
- Text summary output to console

**Backends**
- File backend: stores judgments as JSONL in a local directory
- Langfuse backend: traces judgments, corrections, and autocomplete suggestions for observability

**Developer experience**
- `veritail init` scaffolding command generates a starter adapter and query files
- `veritail generate-queries` generates evaluation queries via LLM
- `--context` flag for injecting business-specific rules into the LLM judge
- `--sample N` to evaluate a random subset of queries
- `--open` to open the HTML report in a browser after evaluation
- Preflight check validates LLM credentials before running
- `veritail init` and the first `veritail run` (file backend) print a tip reminding users to add the output directory to `.gitignore`

[Unreleased]: https://github.com/asarnaout/veritail/compare/v0.3.0...HEAD
[0.3.0]: https://github.com/asarnaout/veritail/compare/v0.2.2...v0.3.0
[0.2.2]: https://github.com/asarnaout/veritail/compare/v0.2.1...v0.2.2
[0.2.1]: https://github.com/asarnaout/veritail/compare/v0.2.0...v0.2.1
[0.2.0]: https://github.com/asarnaout/veritail/compare/v0.1.1...v0.2.0
[0.1.1]: https://github.com/asarnaout/veritail/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/asarnaout/veritail/releases/tag/v0.1.0
