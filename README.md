# veritail

Evaluate ecommerce search relevance with one command.

veritail runs three evaluation layers together:
- LLM relevance judgments (0-3)
- Deterministic quality checks
- IR metrics (NDCG, MRR, MAP, Precision, attribute match)

It is built for practical search iteration: run baseline vs candidate, inspect regressions, and ship with confidence.

## Why veritail

- **One run, full signal**: combines qualitative LLM judgments and quantitative IR metrics.
- **Adapter-first integration**: plug in your existing search API with a small Python function.
- **Ecommerce-aware defaults**: built-in rubric plus domain vertical guidance for foodservice, industrial, electronics, and fashion.
- **Actionable output**: terminal summary + standalone HTML report with per-query drill-down.

## Quick Start

### 1. Install

```bash
pip install veritail
```

With Langfuse support:

```bash
pip install veritail[langfuse]
```

### 2. Create a query set

```csv
query,type,category
red running shoes,attribute,Shoes
wireless earbuds,broad,Electronics
nike air max 90,navigational,Shoes
```

`type` and `category` are optional, but they improve analysis quality.

### 3. Create an adapter

```python
# my_adapter.py
from veritail import SearchResult


def search(query: str) -> list[SearchResult]:
    results = my_search_api.query(query)
    return [
        SearchResult(
            product_id=r["id"],
            title=r["title"],
            description=r["description"],
            category=r["category"],
            price=r["price"],
            position=i,
            in_stock=r.get("in_stock", True),
            attributes=r.get("attributes", {}),
        )
        for i, r in enumerate(results)
    ]
```

### 4. Run evaluation

```bash
export ANTHROPIC_API_KEY=sk-...

veritail run \
  --queries queries.csv \
  --adapter my_adapter.py \
  --llm-model claude-sonnet-4-5 \
  --top-k 10 \
  --open
```

<p align="center">
  <img src="assets/report-1.png" alt="IR metrics and deterministic checks" width="720">
</p>

If you omit `--config-name`, veritail auto-generates one from adapter filename + UTC timestamp.

Outputs are written under:

```text
eval-results/<generated-or-custom-config-name>/
```

### 5. Compare two search configurations

```bash
veritail run \
  --queries queries.csv \
  --adapter adapter_v1.py --config-name v1 \
  --adapter adapter_v2.py --config-name v2
```

The comparison report shows metric deltas, overlap, rank correlation, and position shifts.

## Evaluation Model

### LLM relevance judgments

Each query-result pair gets:
- `SCORE`: `0` to `3`
- `ATTRIBUTES`: `match | partial | mismatch | n/a`
- `REASONING`: concise justification

Default rubric criteria:
- explicit intent match
- implicit intent match
- category alignment
- attribute matching
- commercial viability

### Deterministic checks

**Query-level**
- zero results
- low result count warning (`< 3`)

**Result-level**
- category alignment
- text overlap (Jaccard)
- price outlier detection (IQR)
- near-duplicate detection (title similarity threshold)

**Comparison-level** (dual-config only)
- result overlap (Jaccard)
- rank correlation (Spearman)
- position shift detection

### IR metrics

Computed from LLM scores:
- `ndcg@5`, `ndcg@10`
- `mrr`
- `map`
- `p@5`, `p@10`
- `attribute_match@5`, `attribute_match@10`

## CLI Reference

### `veritail run`

Run a single or dual-configuration evaluation.

| Option | Default | Description |
|---|---|---|
| `--queries` | *(required)* | Path to query set (`.csv` or `.json`) |
| `--adapter` | *(required)* | Path to adapter module (up to 2) |
| `--config-name` | *(optional)* | Name for each configuration (up to 2). If omitted, names are auto-generated |
| `--llm-model` | `claude-sonnet-4-5` | LLM model for judgments |
| `--rubric` | `ecommerce-default` | Rubric name or custom rubric file path |
| `--backend` | `file` | Storage backend (`file` or `langfuse`) |
| `--output-dir` | `./eval-results` | Output directory (file backend) |
| `--top-k` | `10` | Maximum number of results to evaluate per query (must be `>= 1`) |
| `--open` | off | Open HTML report in browser |
| `--skip-on-check-fail` | off | Skip LLM call when a deterministic fail check is present |
| `--context` | *(none)* | Business context string for LLM judge |
| `--vertical` | *(none)* | Built-in vertical (`foodservice`, `industrial`, `electronics`, `fashion`) or path to text file |

If `--config-name` is provided, pass one name per adapter.

## Vertical Guidance

`--vertical` injects domain-specific scoring guidance into the judge prompt.

Built-in verticals:

| Vertical | Focus |
|---|---|
| `foodservice` | pack size, certifications, commercial-grade intent |
| `industrial` | specs, standards/compliance, compatibility constraints |
| `electronics` | model compatibility, generation/spec precision |
| `fashion` | gender/style/size/material intent |

Examples:

```bash
# Built-in vertical
veritail run \
  --queries queries.csv \
  --adapter my_adapter.py \
  --vertical foodservice

# Custom vertical text file
veritail run \
  --queries queries.csv \
  --adapter my_adapter.py \
  --vertical ./my_vertical.txt

# Vertical + business context
veritail run \
  --queries queries.csv \
  --adapter my_adapter.py \
  --vertical foodservice \
  --context "B2B supplier specializing in BBQ restaurant equipment"
```

## HTML Report

`veritail run` always writes a standalone HTML report.

It includes:
- IR metric summary
- deterministic check summary
- worst queries by `ndcg@10`
- per-query result drill-down
- score + attribute verdict + reasoning per result
- deterministic failure annotations

<p align="center">
  <img src="assets/report-2.png" alt="Per-query judgment drill-down with LLM reasoning" width="720">
</p>

## Custom Rubrics

Provide a Python module with:
- `SYSTEM_PROMPT: str`
- `format_user_prompt(query: str, result: SearchResult) -> str`

```python
# my_rubric.py
from veritail.types import SearchResult

SYSTEM_PROMPT = """You are an expert relevance judge for..."""


def format_user_prompt(query: str, result: SearchResult) -> str:
    return f"Query: {query}\nProduct: {result.title}\n..."
```

Then run with:

```bash
veritail run --queries queries.csv --adapter my_adapter.py --rubric my_rubric.py
```

## Backends

### File backend (default)

Stores local artifacts under:

```text
eval-results/
  <config-name>/
    config.json
    judgments.jsonl
    metrics.json
    report.html
```

### Langfuse backend

```bash
pip install veritail[langfuse]

export LANGFUSE_PUBLIC_KEY=pk-...
export LANGFUSE_SECRET_KEY=sk-...

veritail run \
  --queries queries.csv \
  --adapter my_adapter.py \
  --backend langfuse
```

## Development

```bash
git clone https://github.com/asarnaout/veritail.git
cd veritail
pip install -e ".[dev]"
```

Run checks:

```bash
pytest
ruff check src tests
mypy src
```

## Requirements

- Python >= 3.9
- API key for [Anthropic](https://console.anthropic.com/) or [OpenAI](https://platform.openai.com/)

## License

MIT
