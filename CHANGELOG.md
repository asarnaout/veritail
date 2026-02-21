# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- `veritail init` and the first `veritail run` (file backend) now print a tip reminding users to add the output directory to `.gitignore`

### Fixed

- `--config-name` values containing path separators (`/`, `\`) or parent references (`..`) are now rejected with a clear error, preventing potential directory traversal outside the output directory

### Changed

- Langfuse backend docstring and docs now clearly document its write-only nature and limitations

### Fixed

- `--resume` with `--backend langfuse` now fails fast with a clear error instead of silently re-running all queries

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

[Unreleased]: https://github.com/asarnaout/veritail/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/asarnaout/veritail/releases/tag/v0.1.0
