# Custom Rubrics & Enterprise Context

veritail ships with a default ecommerce relevance rubric (`ecommerce-default`) that works well for most use cases. When you need domain-specific scoring criteria or enterprise evaluation rules, you can provide a custom rubric module, inject business context via `--context`, or both.

## Custom Rubric Module

A custom rubric is a Python file that defines two things:

- `SYSTEM_PROMPT: str` -- the system prompt sent to the LLM judge
- `format_user_prompt(query: str, result: SearchResult) -> str` -- a function that formats each query-result pair into a user prompt

```python
# my_rubric.py
from veritail.types import SearchResult

SYSTEM_PROMPT = """You are an expert relevance judge for..."""


def format_user_prompt(query: str, result: SearchResult) -> str:
    return f"Query: {query}\nProduct: {result.title}\n..."
```

Then run with:

```bash
veritail run --queries queries.csv --adapter my_adapter.py --rubric my_rubric.py --llm-model gpt-4o
```

The rubric loader validates that both `SYSTEM_PROMPT` and `format_user_prompt` are present in the module. If either is missing, veritail raises an error at startup.

### Extending the Default Rubric

For cases where you need to add scoring criteria without rewriting the entire rubric from scratch, you can import and extend the built-in rubric:

```python
# my_rubric.py
from veritail.rubrics.ecommerce_default import (
    SYSTEM_PROMPT as BASE_PROMPT,
    format_user_prompt,
)

SYSTEM_PROMPT = BASE_PROMPT + """

## Additional Scoring Criteria
- When the query specifies a dietary restriction (gluten-free, vegan, kosher),
  treat it as a hard attribute constraint with the same weight as brand or size.
"""
```

```bash
veritail run --queries queries.csv --adapter adapter.py --rubric my_rubric.py --llm-model gpt-4o
```

This preserves the full default rubric (scale definitions, evaluation criteria, response format) while appending your own rules. You can also override `format_user_prompt` if you need to change how product data is presented to the judge.

## Enterprise Context

`--context` accepts a short business description or a detailed file with enterprise-specific evaluation guidance. Use a file when your business has domain rules, brand priorities, or jargon that the LLM judge should consider during scoring.

The context is injected into the LLM system prompt alongside the vertical and rubric. Enterprise rules refine scoring within the existing framework -- they guide how the judge interprets queries and weighs product attributes, but they do not override the scoring scale.

### Inline context

Pass a short string directly:

```bash
veritail run \
  --queries queries.csv \
  --adapter adapter.py \
  --context "Pro contractor supplier. Queries for lumber should always prioritize pressure-treated options." \
  --llm-model gpt-4o
```

### Context from a file

For detailed guidance, point `--context` at a text file. veritail reads the file contents automatically when the value is a valid file path.

Example `context.txt` for a home improvement retailer:

```text
BuildRight Supply is a home improvement retailer serving both professional contractors
and DIY homeowners.

Key evaluation guidance:
- Lumber queries should always prioritize pressure-treated options unless the query
  explicitly specifies untreated or kiln-dried.
- "PEX" always means cross-linked polyethylene tubing for plumbing, not any other
  type of flexible tubing. Queries for PEX should never return garden hoses or vinyl tubing.
- For power tool queries, corded and cordless are distinct categories. A query for
  "cordless drill" should not return corded drills, even from the same brand.
- "Romex" is an industry shorthand for NM-B (non-metallic sheathed) electrical cable.
  Treat them as equivalent in search.
- Fastener queries (e.g., "deck screws", "lag bolts") should prioritize
  exterior-rated or stainless steel options over interior-only fasteners.
```

```bash
veritail run \
  --queries queries.csv \
  --adapter adapter.py \
  --vertical home-improvement \
  --context context.txt \
  --llm-model gpt-4o
```

### Combining context with verticals

`--context` and `--vertical` work together. The vertical provides general domain scoring guidance (e.g., what matters in home improvement search), while the context adds your specific business rules. Both are included in the system prompt sent to the LLM judge.

```bash
veritail run \
  --queries queries.csv \
  --adapter adapter.py \
  --vertical home-improvement \
  --context "Big-box retailer targeting both contractors and DIY homeowners" \
  --llm-model gpt-4o
```

See the [CLI Reference](cli-reference.md) for the full list of `--vertical` options.
