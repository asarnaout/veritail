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
     --llm-model claude-sonnet-4-5
   ```

3. **View results:**
   - Terminal will show a summary report with IR metrics
   - Detailed results are saved in `example/results/my-test/`
     - `judgments.jsonl` - All LLM judgments
     - `config.json` - Experiment configuration

## Files

- **`example_queries.csv`** - Sample query set with 4 queries
- **`example_adapter.py`** - Mock search adapter that returns fake products
- **`.env.example`** - Template for API keys (copy to `.env`)
- **`results/`** - Evaluation output (git-ignored)

## Customizing the Adapter

To connect to your real search engine, edit `example_adapter.py`:

```python
def search(query: str) -> list[SearchResult]:
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
    return results
```

## Supported LLM Models

**Claude (Anthropic):**
- `claude-sonnet-4-5` (recommended)
- `claude-opus-4`
- `claude-haiku-4-5`

**OpenAI:**
- `gpt-4o` (recommended)
- `gpt-4-turbo`
- `gpt-4`

The tool automatically detects which API to use based on the model name prefix.
