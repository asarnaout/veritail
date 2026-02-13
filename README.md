# veritail

Ecommerce search relevance evaluation tool. Evaluate and compare the quality of your search results using LLM-based relevance judgments, deterministic quality checks, and standard information retrieval metrics.

## What it does

veritail takes a set of search queries, runs them against your search implementation, and evaluates result quality through three complementary approaches:

1. **LLM-based relevance judgments** — Each query-product pair is scored 0-3 by Claude or GPT models using a structured rubric
2. **Deterministic quality checks** — Category alignment, text overlap, duplicate detection, price outlier detection, and attribute matching
3. **IR metrics** — NDCG@K, MRR, MAP, Precision@K, and Attribute Match Rate@K computed from the LLM scores

You can evaluate a single search configuration or compare two configurations side-by-side to detect regressions and improvements. Results are stored locally or in [Langfuse](https://langfuse.com) for experiment tracking and human annotation.

## Installation

```bash
pip install veritail
```

With Langfuse support:

```bash
pip install veritail[langfuse]
```

## Quick start

### 1. Prepare a query set

Create a CSV or JSON file with your test queries:

```csv
query,type,category
red running shoes,attribute,Shoes
wireless earbuds,broad,Electronics
nike air max 90,navigational,Shoes
```

Query types (`navigational`, `broad`, `long_tail`, `attribute`) are optional but enable per-type metric breakdowns.

### 2. Write a search adapter

Create a Python file that defines a `search` function returning your results in veritail's format:

```python
# my_adapter.py
from veritail import SearchResult

def search(query: str) -> list[SearchResult]:
    # Call your search API here
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

### 3. Run an evaluation

```bash
export ANTHROPIC_API_KEY=sk-...

veritail run \
  --queries queries.csv \
  --adapter my_adapter.py \
  --config-name baseline \
  --llm-model claude-sonnet-4-5 \
  --top-k 10 \
  --open
```

This produces a terminal report with IR metrics and check summaries, and writes an HTML report and `metrics.json` to the output directory. The `--open` flag opens the HTML report in your browser. The HTML report includes per-query judgment drill-downs, metric tooltips, and check failure details.

### 4. Compare two configurations

```bash
veritail run \
  --queries queries.csv \
  --adapter adapter_v1.py --config-name v1 \
  --adapter adapter_v2.py --config-name v2
```

The comparison report shows metric deltas, result overlap (Jaccard index), rank correlation (Spearman), and position shifts between configurations.

## CLI commands

### `veritail run`

Run a single or dual-configuration evaluation.

| Option | Default | Description |
|---|---|---|
| `--queries` | *(required)* | Path to query set (CSV or JSON) |
| `--adapter` | *(required)* | Path to search adapter module (up to 2) |
| `--config-name` | *(required)* | Name for each configuration (up to 2) |
| `--llm-model` | `claude-sonnet-4-5` | LLM model for relevance judgments |
| `--rubric` | `ecommerce-default` | Rubric name or path to custom rubric module |
| `--backend` | `file` | Storage backend (`file` or `langfuse`) |
| `--output-dir` | `./eval-results` | Output directory (file backend) |
| `--top-k` | `10` | Number of results to evaluate per query |
| `--open` | off | Open the HTML report in the browser when complete |
| `--skip-on-check-fail` | off | Skip LLM judgment when a deterministic check fails (default: always run LLM) |
| `--context` | *(none)* | Business context for the LLM judge (e.g. `'B2B industrial kitchen equipment supplier'`) |
| `--vertical` | *(none)* | Domain-specific scoring guidance (built-in: `foodservice`, `industrial`, `electronics`, `fashion`; or path to a text file) |

## Relevance scoring

The default ecommerce rubric scores each query-product pair on a 0-3 scale:

| Score | Label | Meaning |
|---|---|---|
| 3 | Highly relevant | Exact match to query intent; shopper would likely purchase |
| 2 | Relevant | Reasonable match; may not be primary intent |
| 1 | Marginally relevant | Tangentially related; unlikely to be purchased |
| 0 | Irrelevant | No meaningful connection to the query |

Evaluation criteria (in order of importance): explicit intent match, implicit intent match (informed by `--context` and `--vertical` when provided), category alignment, attribute matching, commercial viability.

## Vertical context

The `--vertical` flag injects domain-specific scoring guidance into the LLM judge's system prompt. This helps the judge interpret ambiguous queries and apply domain-appropriate relevance standards.

### Built-in verticals

| Vertical | Description |
|---|---|
| `foodservice` | Commercial kitchen equipment and supplies — pack size, NSF/UL certs, foodservice brand signals, cross-category intent (e.g. "gloves" = food-safe disposable) |
| `industrial` | MRO and industrial supply — spec matching (thread, voltage, grade), compliance codes (ANSI, ASTM), PPE certification, material grades |
| `electronics` | Consumer electronics and components — compatibility constraints, model/generation specificity, spec-driven queries, ecosystem awareness |
| `fashion` | Apparel and accessories — gender targeting, occasion/style, size systems, brand/price tier, material requirements |

### Usage

```bash
# Built-in vertical
veritail run \
  --queries queries.csv \
  --adapter my_adapter.py \
  --config-name baseline \
  --vertical foodservice

# Custom vertical from a text file
veritail run \
  --queries queries.csv \
  --adapter my_adapter.py \
  --config-name baseline \
  --vertical ./my_vertical.txt

# Compose vertical with business context
veritail run \
  --queries queries.csv \
  --adapter my_adapter.py \
  --config-name baseline \
  --vertical foodservice \
  --context "B2B supplier specializing in BBQ restaurant equipment"
```

`--vertical` provides structural domain knowledge (what makes a result relevant in this industry), while `--context` provides specific business identity (who the customers are). They compose: context appears first in the system prompt, followed by the vertical, then the rubric.

## Deterministic checks

These checks run alongside LLM judgments. By default the LLM always runs, but you can use `--skip-on-check-fail` to skip LLM calls for results that fail a check. Check failures are always recorded in judgment metadata and displayed in the HTML report regardless of skip behavior.

**Query-level:**
- Zero results detection
- Low result count warning (< 3 results)

**Result-level:**
- Category alignment against expected/majority category
- Attribute matching (e.g., color extracted from query)
- Text overlap (Jaccard similarity between query and title)
- Price outlier detection (IQR method)
- Near-duplicate detection (title similarity > 0.85)

**Comparison checks** (dual-config only):
- Result overlap (Jaccard index of product IDs)
- Rank correlation (Spearman) for shared products
- Position shift detection (moves of 3+ ranks)

## IR metrics

All metrics are computed from the 0-3 LLM relevance scores:

| Metric | Description |
|---|---|
| NDCG@5, NDCG@10 | Normalized Discounted Cumulative Gain |
| MRR | Mean Reciprocal Rank (relevance threshold: 2) |
| MAP | Mean Average Precision (relevance threshold: 2) |
| P@5, P@10 | Precision at K (relevance threshold: 2) |
| Attribute Match@5, @10 | Fraction of results where LLM-judged attributes match the query (queries without attribute constraints are excluded) |

Metrics are reported as aggregates, per-query breakdowns, and by query type. The HTML report includes info tooltips explaining each metric.

## HTML report

`veritail run` always writes a standalone HTML report to the output directory. Use `--open` to also open it in the browser. The report includes:

- IR metrics table with tooltip descriptions
- Deterministic check pass/fail summary
- Worst-performing queries ranked by NDCG@10
- Per-query judgment drill-down with product scores and LLM reasoning
- Check failure annotations on products that failed deterministic checks
- Visual indicators for skipped judgments (when using `--skip-on-check-fail`)

## Custom rubrics

Create a Python module with a `SYSTEM_PROMPT` string and a `format_user_prompt` function:

```python
# my_rubric.py
from veritail.types import SearchResult

SYSTEM_PROMPT = """You are an expert relevance judge for..."""

def format_user_prompt(query: str, result: SearchResult) -> str:
    return f"Query: {query}\nProduct: {result.title}\n..."
```

Then pass it with `--rubric my_rubric.py`.

## Backends

### File backend (default)

Stores results locally under `--output-dir`:

```
eval-results/
  baseline/
    config.json
    judgments.jsonl
    metrics.json
    report.html
```

### Langfuse backend

Stores results as Langfuse traces with scores for experiment tracking. Use Langfuse's built-in annotation queues and scoring UI for human review.

```bash
pip install veritail[langfuse]

export LANGFUSE_PUBLIC_KEY=pk-...
export LANGFUSE_SECRET_KEY=sk-...

veritail run \
  --queries queries.csv \
  --adapter my_adapter.py \
  --config-name baseline \
  --backend langfuse
```

## Development

```bash
git clone https://github.com/asarnaout/veritail.git
cd veritail
pip install -e ".[dev]"
```

Run tests:

```bash
pytest
```

Lint and type check:

```bash
ruff check src tests
mypy src
```

## Requirements

- Python >= 3.9
- An API key for [Anthropic](https://console.anthropic.com/) or [OpenAI](https://platform.openai.com/)

## License

MIT
