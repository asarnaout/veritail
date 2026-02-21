# Backends

veritail supports pluggable storage backends for evaluation results. You choose a backend with the `--backend` CLI flag (default: `file`).

## File backend (default)

The file backend requires no external services. All evaluation artifacts are written to a local directory tree under `eval-results/`:

```text
eval-results/
  <experiment-name>/
    config.json
    judgments.jsonl
    metrics.json
    report.html
```

| File | Contents |
|---|---|
| `config.json` | Experiment configuration (model, adapter, checks, etc.) |
| `judgments.jsonl` | One JSON object per LLM judgment |
| `metrics.json` | Computed IR metrics (NDCG, MRR, MAP, etc.) |
| `report.html` | Interactive HTML report |

No extra install or configuration is needed -- the file backend is included with the base package.

> **Tip:** Add `eval-results/` (or your custom `--output-dir`) to `.gitignore` to avoid accidentally committing catalog data to version control.

## Langfuse backend

[Langfuse](https://langfuse.com/) provides a richer experience with trace-level visibility, built-in annotation queues, and experiment versioning.

### Install

```bash
pip install veritail[langfuse]
```

### Configuration

Set the required environment variables:

```bash
export LANGFUSE_PUBLIC_KEY=pk-...
export LANGFUSE_SECRET_KEY=sk-...
# Optional: point at a self-hosted instance
# export LANGFUSE_HOST=https://your-langfuse.example.com
```

### Usage

Pass `--backend langfuse` when running an evaluation:

```bash
veritail run \
  --queries queries.csv \
  --adapter my_adapter.py \
  --backend langfuse \
  --llm-model gpt-4o
```

Each LLM judgment is stored as a Langfuse trace with full prompt/response details and a `relevance` score, making it straightforward to review, annotate, and compare experiments in the Langfuse UI.

### Limitations

The Langfuse backend is **write-only** — it sends judgments, scores, and traces to Langfuse but cannot read them back. This means:

- `--resume` is not supported with `--backend langfuse`. Use the file backend for resumable evaluation runs.
- Metrics, reports, and `judgments.jsonl` are not persisted locally. The file backend handles these automatically.

If you need both local persistence and Langfuse observability, run with the file backend and export results to Langfuse separately via the [Langfuse REST API](https://langfuse.com/docs/api).

## See also

- [Supported LLM Providers](supported-llm-providers.md) -- provider setup and model guidance
- [Development](development.md) -- contributing and running tests
