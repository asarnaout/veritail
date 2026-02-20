# LLM Usage & Cost

This document explains exactly how many LLM API calls a veritail run makes, what each call type does, and how to control costs.

## Call types and volume

A full evaluation run may make several types of LLM calls:

| Call type | Volume | When it runs |
|---|---|---|
| Query type classification | 1 per query | Skipped when the `type` column is provided in the CSV |
| Relevance judgment | 1 per query-result pair (queries x `--top-k`) | Always (this is the core evaluation) |
| Autocorrect judgment | 1 per corrected query | Only when adapter returns `corrected_query` |
| Autocomplete judgment | 1 per prefix with non-empty suggestions | Only with `--autocomplete` |

### Calculating your call count

For a typical search evaluation:

- **50 queries, `--top-k 10`, no type column, no corrections:** 50 classification + 500 relevance = **550 calls**
- **50 queries, `--top-k 10`, type column provided, 15 corrections:** 0 classification + 500 relevance + 15 correction = **515 calls**
- **50 queries, `--top-k 5`, type column provided, no corrections:** 0 classification + 250 relevance = **250 calls**

For autocomplete evaluation, the call count equals the number of prefixes with non-empty suggestions (one call per prefix).

## Controlling costs

### Reduce call volume

- **`--top-k`** (default: `10`): Evaluate fewer results per query. `--top-k 5` halves the relevance judgment calls compared to the default.
- **`--sample N`**: Randomly sample N queries from the full set. Use this for quick iterations during development -- you can run the full set later for production evaluation.
- **Provide the `type` column**: Add a `type` column to your query CSV (`navigational`, `broad`, `long_tail`, `attribute`) to skip classification calls entirely.

### Reduce cost per call

- **`--batch`**: Use the provider's batch API for a 50% cost reduction. Takes longer (minutes instead of seconds) but cuts costs in half. Supported for OpenAI, Anthropic, and Gemini. See [Batch Mode & Resuming Interrupted Runs](batch-mode-and-resume.md) for details.
- **Prompt caching**: veritail supports prompt caching -- the shared system prompt is reused across all calls, reducing input token costs on providers that support it (OpenAI, Anthropic, Gemini). No configuration needed; it works automatically.
- **Use a local model**: Connect to a local model server (Ollama, vLLM, LM Studio) via `--llm-base-url` for zero API costs. See [Supported LLM Providers](supported-llm-providers.md) for setup instructions.

### Iteration workflow

A practical workflow for managing costs during development:

1. Start with `--sample 10` to validate your adapter and check that judgments look reasonable
2. Expand to `--sample 25` for broader coverage
3. Run the full query set with `--batch` for the final evaluation

## Data privacy

Product data (titles, descriptions, prices, attributes, etc.) is sent to the configured LLM provider for judging. If your product data must stay on-premise, use a [local model](supported-llm-providers.md) instead of a cloud provider.

## Related docs

- [Batch Mode & Resuming Interrupted Runs](batch-mode-and-resume.md) -- batch API details and resume support
- [CLI Reference](cli-reference.md) -- full flag documentation for `--top-k`, `--sample`, `--batch`
- [Supported LLM Providers](supported-llm-providers.md) -- cloud and local model options
