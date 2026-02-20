# Supported LLM Providers

veritail works with cloud LLM APIs and any OpenAI-compatible local model server. This page covers provider setup, local model configuration, and model quality guidance.

## Requirements

- Python >= 3.9
- An LLM provider -- one of:
  - [OpenAI](https://platform.openai.com/) API key (included with base install)
  - [Anthropic](https://console.anthropic.com/) API key (`pip install veritail[anthropic]`)
  - [Google Gemini](https://ai.google.dev/) API key (`pip install veritail[gemini]`)
  - A running OpenAI-compatible local model server (no extra install needed -- see [Local models](#local-models-via-openai-compatible-servers) below)

## Cloud providers (recommended)

| Provider | Example `--llm-model` | API key env var | Install |
|---|---|---|---|
| **OpenAI** | `gpt-4o`, `gpt-4o-mini`, `o3-mini` | `OPENAI_API_KEY` | included |
| **Anthropic** (Claude) | `claude-sonnet-4-5`, `claude-haiku-4-5` | `ANTHROPIC_API_KEY` | `pip install veritail[anthropic]` |
| **Google Gemini** | `gemini-2.5-flash`, `gemini-2.5-pro` | `GEMINI_API_KEY` or `GOOGLE_API_KEY` | `pip install veritail[gemini]` |

Cloud models provide the highest evaluation quality and are recommended for production use.

### Provider detection

veritail selects the provider based on the model name passed to `--llm-model`:

- Names starting with `claude` use the **Anthropic** API.
- Names starting with `gemini` use the **Google Gemini** API.
- All other names use the **OpenAI** API (this also covers OpenAI-compatible local servers).

### Batch API support

OpenAI, Anthropic, and Gemini all support batch evaluation via `veritail run --batch`. Batch mode submits all judgments in a single API call and polls for results, which can reduce costs and rate-limit pressure. For OpenAI, batch mode is only available when using the default OpenAI endpoint (not when `--llm-base-url` is set).

## Local models via OpenAI-compatible servers

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

### Environment variable alternative

You can set environment variables instead of passing CLI flags:

```bash
export OPENAI_BASE_URL=http://localhost:11434/v1
export OPENAI_API_KEY=not-needed
veritail run --queries queries.csv --adapter my_adapter.py --llm-model qwen3:14b
```

### Tested local servers

| Server | Default port | Docs |
|---|---|---|
| [Ollama](https://ollama.com/) | `11434` | [OpenAI compatibility](https://ollama.com/blog/openai-compatibility) |
| [vLLM](https://docs.vllm.ai/) | `8000` | [OpenAI-compatible server](https://docs.vllm.ai/en/stable/serving/openai_compatible_server/) |
| [LM Studio](https://lmstudio.ai/) | `1234` | [API docs](https://lmstudio.ai/docs/developer/openai-compat) |
| [LocalAI](https://localai.io/) | `8080` | [Features](https://localai.io/features/) |
| [llama.cpp server](https://github.com/ggml-org/llama.cpp) | `8080` | [Server docs](https://github.com/ggml-org/llama.cpp/blob/master/examples/server/README.md) |
| [SGLang](https://docs.sglang.io/) | varies | [Docs](https://docs.sglang.io/) |

## Model quality guidance

veritail computes aggregate IR metrics (NDCG, MRR, MAP) from LLM relevance scores. The reliability of these metrics depends on the LLM's ability to follow instructions and produce consistent judgments.

| Model tier | Examples | Metric reliability |
|---|---|---|
| Frontier cloud models | Claude Sonnet/Opus, GPT-4o, GPT-o3 | High -- recommended for production evaluation |
| Large local models (70B+) | Llama 4 Maverick, Qwen 3 72B, DeepSeek V3 | Good -- comparable to cloud models with sufficient hardware |
| Mid-size local models (14B-30B) | Qwen 3 14B/30B, Phi-4 14B, Mistral 7x8B | Adequate -- some scoring noise; suitable for rapid iteration |
| Small local models (<=8B) | Llama 3.2 3B, Phi-4-mini, Gemma 3 4B | Noisy -- scores may be inconsistent and affect metric reliability |

For reliable metrics that can inform production search decisions, we recommend frontier cloud models or 70B+ parameter local models. Smaller models are useful for fast, low-cost iteration during development but their scores should be interpreted with caution.

## See also

- [Backends](backends.md) -- storage backend options
- [Development](development.md) -- contributing and running tests
