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
- Foodservice vertical split into core + 12 category overlays: beverage, cooking, disposables, food_prep, furniture, ice_cream, refrigeration, serving_holding, smallwares, tabletop, ventilation, warewash
- Foodservice terminology equivalences split between core (cross-cutting terms) and overlays (category-specific terms) to reduce context dilution
- 4 new foodservice category overlays: ventilation (exhaust hoods, makeup air, fire suppression), ice_cream (soft serve, batch freezers, gelato cases), furniture (seating, tables, booths), disposables (cups, to-go containers, paper products, gloves)

### Changed

- Beverage overlay: soft serve moved to new ice_cream overlay; beverage now focuses on drink equipment (coffee, fountain, frozen drinks, tea, draft beer)
- Smallwares overlay: disposables moved to new disposables overlay; smallwares now focuses on durable kitchen tools, pans, and food storage

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
