# Autocomplete Evaluation

veritail includes a standalone autocomplete (type-ahead) evaluation mode. It runs deterministic quality checks and LLM-based semantic evaluation against your suggestion engine. You can run autocomplete evaluation on its own, combine it with search evaluation in a single run, or compare two autocomplete configurations side by side.

## Prefix set format

Provide a CSV or JSON file with a `prefix` column. Prefix types are automatically inferred from character count, or you can provide an optional `type` column to override:

| Character count | Inferred type |
|---|---|
| 1-2 | `short_prefix` |
| 3-9 | `mid_prefix` |
| 10+ | `long_prefix` |

```csv
prefix
he
hea
headph
headphones w
```

## Suggest adapter

Add a `suggest` function to your adapter module. It receives a prefix string and returns an `AutocompleteResponse` or a bare `list[str]`:

```python
# adapter.py
from veritail import AutocompleteResponse


def suggest(prefix: str) -> AutocompleteResponse:
    results = my_autocomplete_api.suggest(prefix)
    return AutocompleteResponse(suggestions=results)
    # Or simply: return results  (a bare list[str] is also accepted)
```

If your adapter only defines `suggest()` without a `search()` function, search evaluation is skipped automatically.

## Quick start

```bash
veritail run \
  --autocomplete prefixes.csv \
  --adapter adapter.py \
  --llm-model gpt-4o \
  --open
```

## Built-in checks

All checks below are deterministic and run alongside the LLM evaluation. No additional configuration is needed.

| Check | What it catches |
|---|---|
| `empty_suggestions` | Prefix returned zero suggestions |
| `duplicate_suggestion` | Exact duplicate suggestions (case-insensitive) |
| `prefix_coherence` | Suggestion neither starts with the prefix nor shares a token with it |
| `offensive_content` | Suggestion contains a blocked term (requires blocklist) |
| `encoding_issues` | HTML entities, control characters, or leading/trailing whitespace |
| `length_anomaly` | Suggestion shorter than 2 characters or longer than 80 characters |
| `latency` | Adapter response time exceeds threshold (default 200 ms) |

## Comparison mode

Pass two adapters to run an A/B comparison:

```bash
veritail run \
  --autocomplete prefixes.csv \
  --adapter bm25_search_adapter.py --config-name bm25-baseline \
  --adapter semantic_search_adapter.py --config-name semantic-v2
```

In addition to per-adapter checks, comparison mode adds two cross-configuration checks:

- **suggestion_overlap** -- Jaccard index of normalized suggestions between configurations
- **rank_agreement** -- Spearman rank correlation for shared suggestions

## Custom checks

Add domain-specific checks with `--autocomplete-checks`. Each `check_*` function receives `(prefix: str, suggestions: list[str])` and returns `list[CheckResult]`:

```python
# my_autocomplete_checks.py
from veritail.types import CheckResult


def check_brand_prefix(prefix: str, suggestions: list[str]) -> list[CheckResult]:
    """Flag suggestions that don't preserve a known brand prefix."""
    checks = []
    for s in suggestions:
        if prefix.lower() in ("sony", "sam") and not s.lower().startswith(prefix.lower()):
            checks.append(
                CheckResult(
                    check_name="brand_prefix",
                    query=prefix,
                    passed=False,
                    detail=f"'{s}' does not start with brand prefix '{prefix}'",
                )
            )
    return checks
```

```bash
veritail run \
  --autocomplete prefixes.csv \
  --adapter adapter.py \
  --autocomplete-checks my_autocomplete_checks.py
```

Custom check results appear alongside built-in checks in reports.

## LLM-based semantic evaluation

In addition to deterministic checks, veritail automatically runs LLM-based semantic evaluation for single-adapter autocomplete runs. This evaluates whether suggestions are semantically relevant to the user's intent, diverse across shopping intents, and appropriate for the store's vertical.

```bash
# Autocomplete-only with LLM evaluation
veritail run \
  --autocomplete prefixes.csv \
  --adapter adapter.py \
  --llm-model gpt-4o

# With vertical and business context
veritail run \
  --autocomplete prefixes.csv \
  --adapter adapter.py \
  --llm-model gpt-4o \
  --vertical home-improvement \
  --context "Big-box home improvement retailer"

# Combined with search evaluation
veritail run \
  --queries queries.csv \
  --autocomplete prefixes.csv \
  --adapter adapter.py \
  --llm-model gpt-4o

# Batch mode (50% cheaper, slower)
veritail run \
  --autocomplete prefixes.csv \
  --adapter adapter.py \
  --llm-model gpt-4o --batch
```

### What it evaluates

Each prefix with non-empty suggestions receives one LLM call that scores:

- **Relevance (0-3)** -- Do suggestions match the likely shopping intent?
  - 3: All suggestions are plausible completions a real shopper would want
  - 2: Most suggestions make sense, one or two are tangential
  - 1: Several suggestions miss the likely intent
  - 0: Suggestions do not match any reasonable interpretation of the prefix
- **Diversity (0-3)** -- Do suggestions cover different categories and use cases?
  - 3: Suggestions span multiple product categories, brands, or use cases
  - 2: Some variety, but clustering around one category
  - 1: Most suggestions are near-duplicates or cover one narrow intent
  - 0: All suggestions are essentially the same item or intent
- **Flagged suggestions** -- Individual suggestions that are unrelated to the prefix, offensive or inappropriate, duplicative, or from the wrong product domain

### Cost

One LLM call per prefix. A run with 100 prefixes makes 100 calls. Prefixes with empty suggestions are skipped. Use `--batch` for 50% cost reduction with cloud providers (see [Batch Mode and Resume](batch-mode-and-resume.md)).

## Output

### Terminal report

- Check pass/fail summary table
- Failed checks detail
- LLM Suggestion Quality summary (average relevance, average diversity, flagged count)
- Flagged suggestions detail with reasoning
- Lowest relevance scores
- Per-prefix drill-down

### HTML report

Standalone report with per-prefix detail, including LLM scores and flagged suggestions. Open automatically with `--open`.

### Artifacts

- `suggestion-judgments.jsonl` -- Written alongside other evaluation artifacts in the experiment output directory

## Related docs

- [CLI Reference](cli-reference.md) -- Full list of `veritail run` options including `--autocomplete`, `--autocomplete-checks`, and `--sample`
- [Batch Mode and Resume](batch-mode-and-resume.md) -- Reducing cost with batch API and resuming interrupted runs
- [Supported LLM Providers](supported-llm-providers.md) -- Cloud and local model options
- [Custom Checks](custom-checks.md) -- Writing custom check modules for search evaluation
