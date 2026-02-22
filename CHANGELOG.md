# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

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

[Unreleased]: https://github.com/asarnaout/veritail/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/asarnaout/veritail/releases/tag/v0.1.0
