# veritail

Evaluate ecommerce search relevance with one command.

veritail runs three evaluation layers together:
- LLM relevance judgments (0-3)
- Deterministic quality checks (e.g., low result count, near-identical results, and out-of-stock ranking issues)
- IR metrics (NDCG, MRR, MAP, Precision, attribute match)

It includes 14 built-in ecommerce verticals (automotive, beauty, electronics, fashion, foodservice, furniture, groceries, home improvement, industrial, marketplace, medical, office supplies, pet supplies, and sporting goods) for domain-aware LLM judging, and supports custom vertical context and rubrics.
Built for rapid search iteration: compare baseline vs candidate, inspect regressions, and decide from per-query evidence.

## Preview

Example output from a real run:

<p align="center">
  <img src="assets/report-1.png" alt="IR metrics and deterministic checks overview" width="900">
</p>
<p align="center">
  <em>Overview report: IR metrics, deterministic checks, and worst-performing queries.</em>
</p>
<p align="center">
  <em>See the detailed per-query drill-down screenshot in the <a href="#html-report">HTML Report</a> section below.</em>
</p>

## Quick Start

### 1. Install

```bash
pip install veritail
```

With Langfuse support:

```bash
pip install veritail[langfuse]
```

### 2. Bootstrap starter files (recommended)

```bash
veritail init
```

This generates:
- `adapter.py` with a real HTTP request skeleton (endpoint, auth header, timeout, JSON parsing, mapping to `SearchResult`)
- `queries.csv` with all four query types (`broad`, `navigational`, `long_tail`, `attribute`)

By default, existing files are not overwritten. Use `--force` to overwrite.

### 3. Create a query set (manual option)

```csv
query,type,category
red running shoes,attribute,Shoes
wireless earbuds,broad,Electronics
nike air max 90,navigational,Shoes
```

`type` and `category` are optional, but they improve analysis quality.

### 4. Generate queries with an LLM (alternative)

If you don't have query logs yet, let an LLM generate a starter set:

```bash
# From a built-in vertical
veritail generate-queries --vertical electronics --output queries.csv

# From business context
veritail generate-queries --context "B2B industrial fastener distributor" --output queries.csv

# Both vertical and context, custom count
veritail generate-queries \
  --vertical foodservice \
  --context "BBQ restaurant equipment supplier" \
  --output queries.csv \
  --count 50
```

This writes a CSV with `query`, `type`, `category`, and `source` columns. Review and edit the generated queries before running an evaluation — the file is designed for human-in-the-loop review.

**Cost note:** Query generation makes a single LLM call (a fraction of a cent with `claude-sonnet-4-5`).

### 5. Create an adapter (manual option)

```python
# my_adapter.py
from veritail import SearchResponse, SearchResult


def search(query: str) -> SearchResponse:
    results = my_search_api.query(query)
    items = [
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
    return SearchResponse(results=items)
    # To report autocorrect / "did you mean" corrections:
    # return SearchResponse(results=items, corrected_query="corrected text")
```

Adapters can return either `SearchResponse` or a bare `list[SearchResult]` (backward compatible). Use `SearchResponse` when your search engine returns autocorrect information.

### 6. Run evaluation

```bash
export ANTHROPIC_API_KEY=sk-...

veritail run \
  --queries queries.csv \
  --adapter my_adapter.py \
  --llm-model claude-sonnet-4-5 \
  --top-k 10 \
  --open
```

**Cost note:** Each query-result pair requires one LLM API call. A run with 50 queries and `--top-k 10` makes ~500 calls. With `claude-sonnet-4-5`, this typically costs a few dollars. Larger query sets or more expensive models will cost more. Use `--top-k` to control results per query and `--sample N` to evaluate a random subset of queries. Prompt caching is supported — the shared system prompt is reused across all calls, reducing input token costs on providers that support it.

Outputs are written under:

```text
eval-results/<generated-or-custom-config-name>/
```

### 7. Compare two search configurations

```bash
veritail run \
  --queries queries.csv \
  --adapter adapter_v1.py --config-name v1 \
  --adapter adapter_v2.py --config-name v2
```

The comparison report shows metric deltas, overlap, rank correlation, and position shifts.

## Vertical Guidance

`--vertical` injects domain-specific scoring guidance into the judge prompt. Each vertical teaches the LLM judge what matters most in a particular ecommerce domain — the hard constraints, industry jargon, certification requirements, and category-specific nuances that generic relevance scoring would miss.

Choose the vertical that best matches the ecommerce site you are evaluating.

| Vertical | Description | Example retailers |
|---|---|---|
| `automotive` | Aftermarket, OEM, and remanufactured parts for cars, trucks, and light vehicles | RockAuto, AutoZone, FCP Euro |
| `beauty` | Skincare, cosmetics, haircare, fragrance, and body care | Sephora, Ulta Beauty, Dermstore |
| `electronics` | Consumer electronics and computer components | Best Buy, Newegg, B&H Photo |
| `fashion` | Clothing, shoes, and accessories | Nordstrom, ASOS, Zappos |
| `foodservice` | Commercial kitchen equipment and supplies for restaurants, cafeterias, and catering | WebstaurantStore, Katom, TigerChef |
| `furniture` | Furniture and home furnishings for residential, commercial, and contract use | Wayfair, Pottery Barn, IKEA |
| `groceries` | Online grocery retail covering food, beverages, and household essentials | Instacart, Amazon Fresh, FreshDirect |
| `home-improvement` | Building materials, hardware, plumbing, electrical, and tools for contractors and DIY | Home Depot, Lowe's, Menards |
| `industrial` | Industrial supply and MRO (Maintenance, Repair, and Operations) | Grainger, McMaster-Carr, Fastenal |
| `marketplace` | Multi-seller marketplace platforms | Amazon, eBay, Etsy |
| `medical` | Medical and surgical supplies for hospitals, clinics, and home health | Henry Schein, Medline, McKesson |
| `office-supplies` | Office products, ink/toner, paper, and workspace equipment | Staples, Office Depot, W.B. Mason |
| `pet-supplies` | Pet food, treats, toys, health products, and habitat equipment across all species | Chewy, PetSmart, Petco |
| `sporting-goods` | Athletic equipment, apparel, and accessories across all sports and outdoor activities | Dick's Sporting Goods, REI, Academy Sports |

You can also provide a custom vertical as a plain text file with `--vertical ./my_vertical.txt`. Use the built-in verticals in `src/veritail/verticals/` as templates.

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

# Vertical + detailed business context from a file
veritail run \
  --queries queries.csv \
  --adapter my_adapter.py \
  --vertical home-improvement \
  --context context.txt
```

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
- out-of-stock prominence (position 1 = fail, positions 2-5 = warning)

**Correction-level** (when adapter returns `corrected_query`)
- correction vocabulary (do corrected terms appear in results?)
- unnecessary correction (do original terms still appear in results?)

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

## Autocorrect Evaluation

When your search engine corrects queries (autocorrect / "did you mean"), veritail automatically evaluates correction quality. No opt-in flag needed — return `corrected_query` from your adapter and veritail handles the rest.

**How it works:**

1. Your adapter returns `SearchResponse(results=..., corrected_query="corrected text")`
2. veritail runs two free deterministic checks per corrected query:
   - **correction_vocabulary**: Are the corrected terms actually present in result titles/descriptions? (Catches phantom corrections like "plats" → "planes" in foodservice)
   - **unnecessary_correction**: Do the original terms still appear in results? (Catches over-correction like "Cambro" → "Camaro" when results contain Cambro products)
3. veritail makes one LLM call per corrected query to judge whether the correction was appropriate or inappropriate
4. Result-level LLM prompts include both original and corrected queries for richer reasoning

**Output:**
- Console: separate progress bar for correction evaluations, summary with call count
- Terminal report: "Query Corrections" table with verdict and reasoning
- HTML report: correction summary table + per-query drill-down showing `original → corrected (verdict)`
- `corrections.jsonl` written alongside `metrics.json`

**Cost:** One extra LLM call per corrected query (not per result). If your adapter corrects 15 of 50 queries, that's 15 extra calls.

## CLI Reference

### `veritail run`

Run a single or dual-configuration evaluation.

| Option | Default | Description |
|---|---|---|
| `--queries` | *(required)* | Path to query set (`.csv` or `.json`) |
| `--adapter` | *(required)* | Path to adapter module (up to 2) |
| `--config-name` | *(optional)* | Name for each configuration (up to 2). If omitted, names are auto-generated |
| `--llm-model` | `claude-sonnet-4-5` | LLM model for judgments |
| `--llm-base-url` | *(none)* | Base URL for an OpenAI-compatible endpoint (e.g. `http://localhost:11434/v1` for Ollama) |
| `--llm-api-key` | *(none)* | API key override for the endpoint |
| `--rubric` | `ecommerce-default` | Rubric name or custom rubric file path |
| `--backend` | `file` | Storage backend (`file` or `langfuse`) |
| `--output-dir` | `./eval-results` | Output directory (file backend) |
| `--top-k` | `10` | Maximum number of results to evaluate per query (must be `>= 1`) |
| `--open` | off | Open HTML report in browser |
| `--context` | *(none)* | Business context for LLM judge — business identity, customer base, query interpretation guidance. Accepts a string or a path to a text file |
| `--vertical` | *(none)* | Built-in vertical (`automotive`, `beauty`, `electronics`, `fashion`, `foodservice`, `furniture`, `groceries`, `home-improvement`, `industrial`, `marketplace`, `medical`, `office-supplies`, `pet-supplies`, `sporting-goods`) or path to text file |
| `--checks` | *(none)* | Path to custom check module(s) with `check_*` functions (repeatable) |
| `--sample` | *(none)* | Randomly sample N queries for a faster evaluation (deterministic seed) |

If `--config-name` is provided, pass one name per adapter.

### `veritail init`

Scaffold starter files for a new project.

| Option | Default | Description |
|---|---|---|
| `--dir` | `.` | Target directory for generated files |
| `--adapter-name` | `adapter.py` | Adapter filename (must end with `.py`) |
| `--queries-name` | `queries.csv` | Query set filename (must end with `.csv`) |
| `--force` | off | Overwrite existing files |

### `veritail generate-queries`

Generate evaluation queries with an LLM and save to CSV. At least one of `--vertical` or `--context` is required.

| Option | Default | Description |
|---|---|---|
| `--output` | *(required)* | Output CSV path (must end with `.csv`) |
| `--count` | `25` | Number of queries to generate |
| `--vertical` | *(none)* | Built-in vertical name or path to text file |
| `--context` | *(none)* | Business context string or path to a text file |
| `--llm-model` | `claude-sonnet-4-5` | LLM model for generation |
| `--llm-base-url` | *(none)* | Base URL for an OpenAI-compatible endpoint |
| `--llm-api-key` | *(none)* | API key override for the endpoint |

### `veritail vertical list`

List all built-in verticals.

### `veritail vertical show <name>`

Print the full text of a built-in vertical. Use this to inspect a vertical before customizing it, or to copy one as a starting point for your own:

```bash
# View a vertical
veritail vertical show home-improvement

# Copy to a file and customize
veritail vertical show home-improvement > my_vertical.txt
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
- run metadata footer (timestamp, model, rubric, vertical, top-k, adapter path)

<p align="center">
  <img src="assets/report-2.png" alt="Per-query judgment drill-down with LLM reasoning" width="900">
</p>
<p align="center">
  <em>Drill-down report: per-query product scores, attribute verdicts, and LLM reasoning.</em>
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

## Custom Checks

Add domain-specific deterministic checks without modifying veritail itself. A check module is a Python file containing one or more `check_*` functions:

```python
# my_checks.py
from veritail.types import CheckResult, QueryEntry, SearchResult


def check_species_mismatch(
    query: QueryEntry, results: list[SearchResult]
) -> list[CheckResult]:
    """Flag cross-species results in pet supply searches."""
    checks = []
    for r in results:
        species = r.attributes.get("species")
        if species and species.lower() not in query.query.lower():
            checks.append(
                CheckResult(
                    check_name="species_mismatch",
                    query=query.query,
                    product_id=r.product_id,
                    passed=False,
                    detail=f"Query mentions no '{species}' but result is for {species}",
                )
            )
    return checks
```

Each `check_*` function must:
- Accept `(QueryEntry, list[SearchResult])`
- Return `list[CheckResult]`

Non-callable names starting with `check_` (e.g., `check_threshold = 0.5`) are skipped. Helper functions without the `check_` prefix are ignored.

Run with one or more `--checks` flags:

```bash
veritail run \
  --queries queries.csv \
  --adapter my_adapter.py \
  --checks my_checks.py \
  --checks more_checks.py
```

Custom check results appear alongside built-in checks in reports.

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

## Supported LLM Providers

veritail works with cloud LLM APIs and any OpenAI-compatible local model server.

### Cloud providers (recommended)

| Provider | Example `--llm-model` | API key env var |
|---|---|---|
| **Anthropic** (Claude) | `claude-sonnet-4-5`, `claude-haiku-4-5` | `ANTHROPIC_API_KEY` |
| **OpenAI** | `gpt-4o`, `gpt-4o-mini`, `o3-mini` | `OPENAI_API_KEY` |

Cloud models provide the highest evaluation quality and are recommended for production use.

### Local models via OpenAI-compatible servers

veritail connects to any server that exposes the [OpenAI chat completions API](https://platform.openai.com/docs/api-reference/chat) (`POST /v1/chat/completions`). Pass `--llm-base-url` to point at a local endpoint:

```bash
# Ollama
ollama pull qwen3:14b
veritail run \
  --queries queries.csv \
  --adapter my_adapter.py \
  --llm-model qwen3:14b \
  --llm-base-url http://localhost:11434/v1 \
  --llm-api-key not-needed

# vLLM
veritail run \
  --queries queries.csv \
  --adapter my_adapter.py \
  --llm-model meta-llama/Llama-4-Scout \
  --llm-base-url http://localhost:8000/v1 \
  --llm-api-key not-needed

# LM Studio
veritail run \
  --queries queries.csv \
  --adapter my_adapter.py \
  --llm-model local-model \
  --llm-base-url http://localhost:1234/v1 \
  --llm-api-key lm-studio
```

`--llm-base-url` and `--llm-api-key` also work with `veritail generate-queries`.

Alternatively, you can set environment variables instead of passing CLI flags:

```bash
export OPENAI_BASE_URL=http://localhost:11434/v1
export OPENAI_API_KEY=not-needed
veritail run --queries queries.csv --adapter my_adapter.py --llm-model qwen3:14b
```

**Tested local servers:**

| Server | Default port | Docs |
|---|---|---|
| [Ollama](https://ollama.com/) | `11434` | [OpenAI compatibility](https://ollama.com/blog/openai-compatibility) |
| [vLLM](https://docs.vllm.ai/) | `8000` | [OpenAI-compatible server](https://docs.vllm.ai/en/stable/serving/openai_compatible_server/) |
| [LM Studio](https://lmstudio.ai/) | `1234` | [API docs](https://lmstudio.ai/docs/developer/openai-compat) |
| [LocalAI](https://localai.io/) | `8080` | [Features](https://localai.io/features/) |
| [llama.cpp server](https://github.com/ggml-org/llama.cpp) | `8080` | [Server docs](https://github.com/ggml-org/llama.cpp/blob/master/examples/server/README.md) |
| [SGLang](https://docs.sglang.io/) | varies | [Docs](https://docs.sglang.io/) |

### Model quality guidance

veritail computes aggregate IR metrics (NDCG, MRR, MAP) from LLM relevance scores. The reliability of these metrics depends on the LLM's ability to follow instructions and produce consistent judgments.

| Model tier | Examples | Metric reliability |
|---|---|---|
| Frontier cloud models | Claude Sonnet/Opus, GPT-4o, GPT-o3 | High — recommended for production evaluation |
| Large local models (70B+) | Llama 4 Maverick, Qwen 3 72B, DeepSeek V3 | Good — comparable to cloud models with sufficient hardware |
| Mid-size local models (14B–30B) | Qwen 3 14B/30B, Phi-4 14B, Mistral 7x8B | Adequate — some scoring noise; suitable for rapid iteration |
| Small local models (≤8B) | Llama 3.2 3B, Phi-4-mini, Gemma 3 4B | Noisy — scores may be inconsistent and affect metric reliability |

For reliable metrics that can inform production search decisions, we recommend frontier cloud models or 70B+ parameter local models. Smaller models are useful for fast, low-cost iteration during development but their scores should be interpreted with caution.

## Requirements

- Python >= 3.9
- One of:
  - API key for [Anthropic](https://console.anthropic.com/) or [OpenAI](https://platform.openai.com/)
  - A running OpenAI-compatible local model server (see [Local models](#local-models-via-openai-compatible-servers) above)

## Disclaimer

veritail uses large language models to generate relevance judgments. LLM outputs can be inaccurate, inconsistent, or misleading. All scores, reasoning, and reports produced by this tool should be reviewed by a qualified human before informing production decisions. veritail is an evaluation aid, not a substitute for human judgment. The authors are not liable for any decisions made based on its output.

## License

MIT
