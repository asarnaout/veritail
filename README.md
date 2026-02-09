# veritail

Ecommerce search relevance evaluation tool. Evaluate and compare the quality of your search results using LLM-based relevance judgments, deterministic quality checks, and standard information retrieval metrics.

## What it does

veritail takes a set of search queries, runs them against your search implementation, and evaluates result quality through three complementary approaches:

1. **LLM-based relevance judgments** — Each query-product pair is scored 0-3 by Claude or GPT models using a structured rubric
2. **Deterministic quality checks** — Category alignment, text overlap, duplicate detection, price outlier detection, and attribute matching
3. **IR metrics** — NDCG@K, MRR, MAP, and Precision@K computed from the LLM scores

You can evaluate a single search configuration or compare two configurations side-by-side to detect regressions and improvements. Results are stored locally or in [Langfuse](https://langfuse.com) for experiment tracking.

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
  --top-k 10
```

This produces a terminal report with IR metrics, check summaries, and the worst-performing queries.

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

### `veritail report`

Generate a report from existing evaluation results.

```bash
# Single experiment report
veritail report --experiment baseline

# Comparison report
veritail report --experiment v2 --baseline v1

# HTML output
veritail report --experiment baseline --output report.html

# Include LLM-human agreement stats
veritail report --experiment baseline --include-human-agreement
```

### `veritail review`

Create a human review annotation queue by sampling from LLM judgments.

```bash
veritail review --experiment baseline --sample-rate 0.10 --strategy stratified
```

Sampling strategies:
- `random` — Uniform random sample
- `stratified` — Samples proportionally from each score level (0-3)

### `veritail agreement`

Compute inter-rater agreement (Cohen's kappa) between LLM and human scores.

```bash
veritail agreement --experiment baseline
```

## Relevance scoring

The default ecommerce rubric scores each query-product pair on a 0-3 scale:

| Score | Label | Meaning |
|---|---|---|
| 3 | Highly relevant | Exact match to query intent; shopper would likely purchase |
| 2 | Relevant | Reasonable match; may not be primary intent |
| 1 | Marginally relevant | Tangentially related; unlikely to be purchased |
| 0 | Irrelevant | No meaningful connection to the query |

Evaluation criteria (in order of importance): explicit intent match, implicit intent match, category alignment, attribute matching, commercial viability.

## Deterministic checks

These checks run before LLM judgments and can optionally skip LLM calls for results that fail:

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

Metrics are reported as aggregates, per-query breakdowns, and by query type.

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
    deterministic.jsonl
    review-sample.csv
    human-scores.csv
```

### Langfuse backend

Stores results as Langfuse traces with scores for experiment tracking.

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

## Human-in-the-loop workflow

1. Run an evaluation: `veritail run ...`
2. Create a review queue: `veritail review --experiment baseline --sample-rate 0.10 --strategy stratified`
3. Have human annotators fill in scores (via CSV for file backend, or Langfuse UI)
4. Compute agreement: `veritail agreement --experiment baseline`

Cohen's kappa calibration:
- **> 0.7** — LLM judgments are trustworthy
- **0.4 - 0.7** — Systematic biases present; consider rubric adjustments
- **< 0.4** — LLM judgments are unreliable; human review needed

## Development

```bash
git clone https://github.com/your-org/veritail.git
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
