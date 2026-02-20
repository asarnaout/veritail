# Autocorrect Evaluation

When your search engine corrects queries (autocorrect / "did you mean"), veritail automatically evaluates correction quality. No opt-in flag is needed -- return `corrected_query` from your adapter and veritail handles the rest.

## How it works

1. Your adapter returns `SearchResponse(results=..., corrected_query="corrected text")`
2. veritail runs two deterministic checks per corrected query (no LLM calls required):
   - **correction_vocabulary** -- Are the corrected tokens actually present in result titles and descriptions? Catches phantom corrections where the engine rewrites a query into terms that don't appear anywhere in the results (e.g., "plats" corrected to "planes" in a foodservice context where "plats" means plates).
   - **unnecessary_correction** -- Do the original tokens still appear in the results? Catches over-correction where the engine changes a valid catalog term (e.g., "Cambro" corrected to "Camaro" when results already contain Cambro products).
3. veritail makes one LLM call per corrected query to judge whether the correction was appropriate or inappropriate. The LLM evaluates whether the correction preserved the shopper's original intent, using criteria such as whether it fixed a genuine spelling mistake vs. altered a valid brand name, model number, or industry jargon.
4. Result-level LLM prompts include both the original and corrected queries, giving the relevance judge richer context for scoring individual products.

## Adapter setup

Return a `SearchResponse` with `corrected_query` set to the corrected text:

```python
from veritail import SearchResponse, SearchResult


def search(query: str) -> SearchResponse:
    results = my_search_api.query(query)
    items = [
        SearchResult(
            product_id=r["id"],
            title=r["title"],
            description=r["description"],
            category=r["category"],
            price=r["price"],
            position=i,
            in_stock=r.get("in_stock", True),
            attributes=r.get("attributes", {}),
        )
        for i, r in enumerate(results)
    ]
    return SearchResponse(results=items, corrected_query="corrected text")
```

If the search engine did not correct a given query, omit `corrected_query` or set it to `None`. veritail only evaluates corrections for queries where `corrected_query` is returned.

## Output

- **Console**: Separate progress bar for correction evaluations, summary with call count
- **Terminal report**: "Query Corrections" table with verdict and reasoning per corrected query
- **HTML report**: Correction summary table and per-query drill-down showing `original -> corrected (verdict)`
- **`corrections.jsonl`**: Written alongside `metrics.json` in the experiment output directory

## Cost

One extra LLM call per corrected query (not per result). If your adapter corrects 15 out of 50 queries, that's 15 additional calls on top of the relevance judgments. The two deterministic checks run for free on every corrected query.

## Related docs

- [Evaluation Model](evaluation-model.md) -- Deterministic checks reference including correction-level checks
- [CLI Reference](cli-reference.md) -- Full list of `veritail run` options
- [Batch Mode and Resume](batch-mode-and-resume.md) -- Reducing cost with batch API and resuming interrupted runs
