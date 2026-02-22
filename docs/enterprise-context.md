# Enterprise Context

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
