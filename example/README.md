# Example Usage

This folder contains working examples to help you get started with veritail.

## Quick Start

1. **Set up API keys:**
   ```bash
   cp .env.example .env
   # Edit .env and add your actual API keys
   ```

2. **Run the evaluation:**
   ```bash
   # From the project root
   veritail run \
     --queries example/example_queries.csv \
     --adapter example/example_adapter.py \
     --config-name "my-test" \
     --llm-model gpt-4o
   ```

3. **View results:**
   - Terminal will show a summary report with IR metrics
   - Detailed results are saved in `eval-results/my-test/`
     - `judgments.jsonl` - All LLM judgments
     - `config.json` - Experiment configuration
     - `report.html` - Detailed HTML report

## Files

- **`example_queries.csv`** - Sample query set with 4 queries
- **`example_adapter.py`** - Mock search adapter that returns fake products
- **`.env.example`** - Template for API keys (copy to `.env`)

## Customizing the Adapter

To connect to your real search engine, edit `example_adapter.py`:

```python
from veritail.types import SearchResponse, SearchResult

def search(query: str) -> SearchResponse:
    # Replace mock data with actual API calls
    response = requests.get(f"https://your-api.com/search?q={query}")
    products = response.json()

    # Convert to SearchResult objects
    results = []
    for i, product in enumerate(products):
        results.append(SearchResult(
            product_id=product["id"],
            title=product["title"],
            description=product["description"],
            category=product["category"],
            price=product["price"],
            position=i,
            attributes=product.get("attributes", {}),
            in_stock=product.get("in_stock", True),
        ))
    return SearchResponse(results=results)
```

## Supported LLM Models

**OpenAI:**
- `gpt-4o` (recommended)
- `gpt-4o-mini`
- `gpt-4-turbo`

**Claude (Anthropic)** — `pip install veritail[anthropic]`:
- `claude-sonnet-4-5`
- `claude-haiku-4-5`

**Gemini (Google)** — `pip install veritail[gemini]`:
- `gemini-2.5-flash`
- `gemini-2.5-pro`

**Local models** via any OpenAI-compatible server (Ollama, vLLM, LM Studio, etc.):
```bash
veritail run \
  --queries example/example_queries.csv \
  --adapter example/example_adapter.py \
  --llm-model qwen3:14b \
  --llm-base-url http://localhost:11434/v1 \
  --llm-api-key not-needed
```

The tool automatically detects which API to use based on the model name prefix.
