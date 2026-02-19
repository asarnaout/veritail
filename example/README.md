# Example Usage

This folder contains working examples for a **home improvement** retailer to help you get started with veritail. The mock adapters return hardcoded product data — replace them with real API calls to your search endpoint.

## Quick Start

1. **Set up API keys:**
   ```bash
   cp example/.env.example example/.env
   # Edit .env and add your actual API keys
   ```

2. **Run the search evaluation:**
   ```bash
   # From the project root
   veritail run \
     --queries example/queries.csv \
     --adapter example/adapter.py \
     --vertical home-improvement \
     --config-name "home-improvement-test" \
     --llm-model gpt-4o
   ```

3. **Run the autocomplete evaluation:**
   ```bash
   veritail run \
     --autocomplete example/prefixes.csv \
     --adapter example/adapter.py \
     --config-name "suggest-test" \
     --open
   ```

4. **View results:**
   - Terminal will show a summary report with IR metrics and check results
   - Detailed results are saved in `eval-results/<config-name>/`
     - `judgments.jsonl` - All LLM judgments
     - `config.json` - Experiment configuration
     - `metrics.json` - Computed IR metrics
     - `report.html` - Detailed HTML report

## Files

- **`queries.csv`** - 25 home improvement queries across 4 types (broad, navigational, attribute, long_tail). The `type` and `category` columns are optional; when omitted, types are auto-classified by the LLM.
- **`adapter.py`** - Mock adapter with both `search()` and `suggest()` functions, realistic home improvement product data (5 results per query) and autocomplete suggestions
- **`prefixes.csv`** - 18 autocomplete prefixes across 3 length tiers (short, mid, long). The `type` column is optional; when omitted, types are inferred from prefix length.
- **`.env.example`** - Template for API keys (copy to `.env`)

## What the Example Covers

The mock catalog spans major home improvement categories:

- **Electrical** — wire (Romex), GFCI outlets, ceiling fans, LED recessed lights, exhaust fans
- **Plumbing** — faucets, toilets, PEX tubing, copper fittings, PVC cement
- **Tools** — drills, circular saws, tile saws, PEX crimp tools
- **Lumber** — pressure-treated posts
- **Fasteners** — deck screws, drywall anchors, structural hardware (Simpson Strong-Tie)
- **Building Materials** — insulation, vinyl plank flooring
- **Paint** — interior paint, exterior deck stain
- **Hardware** — cabinet pulls

Each query returns 5 products, including intentional relevance signals for the LLM judge to evaluate:
- **Near misses** (e.g., wrong size, wrong finish color)
- **Wrong category** (e.g., a roller cover returned for an "interior paint" query)
- **Competitor brand** for navigational queries (e.g., Milwaukee result for a "dewalt 20v drill" query)
- **Accessory vs primary product** confusion (e.g., a blade returned for a "tile saw" query)
- **Out-of-stock items** in results

## Supported LLM Models

**OpenAI:**
- `gpt-4o` (recommended)
- `gpt-4o-mini`

**Claude (Anthropic)** — `pip install veritail[anthropic]`:
- `claude-sonnet-4-5`
- `claude-haiku-4-5`

**Gemini (Google)** — `pip install veritail[gemini]`:
- `gemini-2.5-flash`
- `gemini-2.5-pro`

**Local models** via any OpenAI-compatible server (Ollama, vLLM, LM Studio, etc.):
```bash
veritail run \
  --queries example/queries.csv \
  --adapter example/adapter.py \
  --vertical home-improvement \
  --llm-model qwen3:14b \
  --llm-base-url http://localhost:11434/v1 \
  --llm-api-key not-needed
```

The tool automatically detects which API to use based on the model name prefix.
