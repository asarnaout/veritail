# CLI Reference

veritail provides four commands: `run` for evaluation, `init` for project scaffolding, `generate-queries` for LLM-based query generation, and `vertical` for inspecting built-in verticals. This page documents every flag, its default value, and the requirements for each mode.

> **Security note:** `--adapter`, `--checks`, and `--autocomplete-checks` all load local Python files and execute them directly. This is intentional — veritail is a developer tool designed to run your code. Only point these flags at files you trust, the same as you would with any Python script.

## `veritail run`

Run a single or dual-configuration evaluation.

| Option | Default | Description |
|---|---|---|
| `-v` / `--verbose` | off | Enable debug logging to stderr. Shows provider selection, token usage, classification results, judgment scores, check summaries, batch operations, and metric values. Does not interfere with Rich console output on stdout |
| `--queries` | *(optional)* | Path to query set (`.csv` or `.json`). Optional, but at least one of `--queries` or `--autocomplete` is required |
| `--autocomplete` | *(optional)* | Path to autocomplete prefix set (`.csv` or `.json`). Optional, but at least one of `--queries` or `--autocomplete` is required. The adapter must export a `suggest()` function when this flag is used |
| `--adapter` | *(required)* | Path to adapter module. Always required; pass up to 2 for dual-config comparison mode |
| `--config-name` | *(optional)* | Name for each configuration (up to 2). If omitted, names are auto-generated |
| `--llm-model` | *(conditional)* | LLM model for judgments (e.g. `gpt-4o`, `claude-sonnet-4-5`, `gemini-2.5-flash`). Required when `--queries` or `--autocomplete` is provided with a single adapter |
| `--llm-base-url` | *(none)* | Base URL for an OpenAI-compatible endpoint (e.g. `http://localhost:11434/v1` for Ollama) |
| `--llm-api-key` | *(none)* | API key override for the endpoint |
| `--backend` | `file` | Storage backend (`file` or `langfuse`) |
| `--output-dir` | `./eval-results` | Output directory (file backend) |
| `--top-k` | `10` | Maximum number of results to evaluate per query (must be `>= 1`) |
| `--open` | off | Open HTML report in browser |
| `--context` | *(none)* | Business context for LLM judge -- business identity, customer base, query interpretation guidance, and enterprise-specific evaluation rules (brand priorities, certification requirements, domain jargon). Accepts a string or a path to a text file (see [Enterprise Context](enterprise-context.md)) |
| `--vertical` | *(none)* | Built-in vertical (`automotive`, `beauty`, `electronics`, `fashion`, `foodservice`, `furniture`, `groceries`, `home-improvement`, `industrial`, `marketplace`, `medical`, `office-supplies`, `pet-supplies`, `sporting-goods`) or path to text file |
| `--checks` | *(none)* | Path to custom check module(s) with `check_*` functions for search evaluation (repeatable; see [Custom Checks](custom-checks.md)) |
| `--autocomplete-checks` | *(none)* | Path to custom check module(s) with `check_*` functions for autocomplete evaluation (repeatable) |
| `--sample` | *(none)* | Randomly sample N queries/prefixes for a faster evaluation (deterministic seed) |
| `--batch` | off | Use provider batch API for LLM calls (50% cheaper, slower). Works with both search and autocomplete evaluation. Supported for OpenAI, Anthropic, and Gemini. Not compatible with `--llm-base-url` |
| `--resume` | off | Resume a previously interrupted run. Requires `--config-name` to identify the previous run. In non-batch mode, skips queries already judged in `judgments.jsonl`. In batch mode, resumes polling for an in-flight batch from a saved checkpoint. `--llm-model` and `--top-k` must match the original run |

If `--config-name` is provided, pass one name per adapter.

### Flag requirements by mode

**Search evaluation** requires `--queries`, `--adapter`, and `--llm-model`:

```bash
veritail run --queries queries.csv --adapter adapter.py --llm-model gpt-4o
```

**Autocomplete evaluation** requires `--autocomplete`, `--adapter`, and `--llm-model`:

```bash
veritail run --autocomplete prefixes.csv --adapter adapter.py --llm-model gpt-4o
```

**Combined** requires `--queries`, `--autocomplete`, `--adapter`, and `--llm-model`. Both search and autocomplete are evaluated in a single run.

**Dual-config comparison** uses two `--adapter` and two `--config-name` flags:

```bash
veritail run --queries queries.csv \
  --adapter a1.py --config-name v1 \
  --adapter a2.py --config-name v2 \
  --llm-model gpt-4o
```

**Batch mode** (`--batch`) additionally requires a cloud provider model (OpenAI, Anthropic, or Gemini). Not compatible with `--llm-base-url`.

**Resume** (`--resume`) additionally requires `--config-name`. The experiment directory from the previous run must exist, and `--llm-model` and `--top-k` must match the original run. Not compatible with `--backend langfuse` (the Langfuse backend is write-only).

## `veritail init`

Scaffold starter files for a new project. Generates an adapter module, a query CSV, and a prefix CSV. By default, existing files are not overwritten.

| Option | Default | Description |
|---|---|---|
| `--dir` | `.` | Target directory for generated files |
| `--adapter-name` | `adapter.py` | Adapter filename (must end with `.py`) |
| `--queries-name` | `queries.csv` | Query set filename (must end with `.csv`) |
| `--force` | off | Overwrite existing files |

## `veritail generate-queries`

Generate evaluation queries with an LLM and save to CSV. At least one of `--vertical` or `--context` is required.

| Option | Default | Description |
|---|---|---|
| `--output` | `queries.csv` | Output CSV path (must end with `.csv`) |
| `--count` | `25` | Target number of queries to generate (max 50, approximate -- see note below) |
| `--vertical` | *(none)* | Built-in vertical name or path to text file |
| `--context` | *(none)* | Business context string or path to a text file |
| `--llm-model` | *(required)* | LLM model for generation (e.g. `gpt-4o`, `claude-sonnet-4-5`, `gemini-2.5-flash`) |
| `--llm-base-url` | *(none)* | Base URL for an OpenAI-compatible endpoint |
| `--llm-api-key` | *(none)* | API key override for the endpoint |
| `--append` | off | Add generated queries to an existing file (deduplicates automatically) |
| `--force` | off | Overwrite existing output file |
| `-v` / `--verbose` | off | Enable debug logging to stderr |

> **Note:** Query counts are approximate. LLMs may return slightly fewer or more queries than requested. The CLI will report the actual count generated. For larger query sets, run the command multiple times or curate queries manually.

## `veritail vertical list`

List all built-in verticals.

```bash
veritail vertical list
```

## `veritail vertical show`

Print the full text of a built-in vertical. Use this to inspect a vertical before customizing it, or to copy one as a starting point for your own.

```bash
# View a vertical
veritail vertical show home-improvement

# Copy to a file and customize
veritail vertical show home-improvement > my_vertical.txt
```
