# Batch Mode & Resuming Interrupted Runs

This document covers two features that work together to make large evaluation runs practical: **batch mode** for cutting LLM costs in half, and **resume** for recovering from interruptions without re-evaluating completed queries.

## Batch Mode (50% cost reduction)

Use `--batch` to send all LLM judgment calls through the provider's batch API instead of making individual requests. This reduces cost by 50% but takes longer (typically minutes for small batches, longer for large ones).

Batch mode works with both search relevance judgments and autocomplete LLM evaluation. Query type classification is also batched when `--batch` is enabled.

```bash
veritail run --queries queries.csv --adapter adapter.py \
    --llm-model gpt-4o --batch
```

After submitting a batch, veritail polls the provider for completion every 60 seconds. These polling calls are free management API requests and do not consume tokens or incur additional charges.

**Supported providers:** OpenAI, Anthropic, and Google Gemini.

**Not supported** with local models (`--llm-base-url`). Batch mode requires a cloud provider model.

When corrections are present (adapter returns `corrected_query`), veritail submits the relevance batch and correction batch together and polls both concurrently.

## Resuming Interrupted Runs

Use `--resume` to pick up where a previous run left off. This is useful when a run is interrupted by a network error, timeout, or Ctrl+C -- you don't have to re-evaluate queries that already completed.

```bash
veritail run --queries queries.csv --adapter adapter.py \
    --llm-model gpt-4o --config-name my-eval --resume
```

`--resume` requires `--config-name` so veritail can locate the previous run's experiment directory under `--output-dir` (default `./eval-results`). The directory must already exist from a prior run.

### Config mismatch detection

On resume, veritail checks the saved `config.json` and rejects the run if `--llm-model`, `--rubric`, or `--top-k` differ from the original. This prevents silently mixing results from different configurations.

### How it works -- non-batch mode

In non-batch mode (`--resume` without `--batch`), veritail reads the existing `judgments.jsonl` file and identifies which query indices have already been judged. Completed queries are skipped and their judgments are reloaded into memory. New judgments are appended to the same file. Correction evaluations are only run for queries processed in the current resumption, not for previously completed queries.

### How it works -- batch mode

In batch mode (`--resume --batch`), veritail saves a `checkpoint.json` to the experiment directory immediately after submitting a batch. The checkpoint records:

- The batch ID
- All request context (queries, results, deterministic checks)
- Provider-specific state (e.g. Gemini custom ID ordering)
- Correction batch ID and context (when corrections are present)

On resume, if a checkpoint exists, veritail skips adapter calls and batch submission entirely and jumps straight to polling for the in-flight batch. If the batch has already completed, results are retrieved immediately.

If a batch fails (e.g. provider error or expiration), the checkpoint is automatically cleared and the error message instructs you to re-run without `--resume` to start a fresh batch. If only the correction batch fails, the relevance results are preserved and you can re-run with `--resume` to retrieve them and re-submit corrections.

Autocomplete LLM evaluation uses a separate checkpoint (`ac-checkpoint.json`) with the same resume semantics.

### Dual-config mode

`--resume` works with dual-config comparison runs. Each configuration's experiment directory is checked independently, and each resumes from its own progress.

```bash
veritail run --queries queries.csv \
    --adapter a1.py --config-name v1 \
    --adapter a2.py --config-name v2 \
    --llm-model gpt-4o --resume
```

## Related docs

- [CLI Reference](cli-reference.md) -- full flag documentation for `--batch` and `--resume`
- [LLM Usage & Cost](llm-usage-and-cost.md) -- understanding API call volume and cost controls
