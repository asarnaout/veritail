# Evaluation Model

This document describes how veritail evaluates search quality. The evaluation model has three layers: LLM relevance judgments that score each query-result pair, deterministic quality checks that catch structural issues without an LLM, and IR metrics computed from the LLM scores.

## LLM relevance judgments

Each query-result pair is evaluated by an LLM judge that returns three fields:

- **SCORE**: `0` to `3` (graded relevance)
  - `3` = Highly relevant -- exact match to query intent; shopper would likely purchase
  - `2` = Relevant -- reasonable match; may not be primary intent but worth considering
  - `1` = Marginally relevant -- tangentially related; shopper unlikely to purchase
  - `0` = Irrelevant -- no meaningful connection to the query
- **ATTRIBUTES**: `match | partial | mismatch | n/a`
  - `match` -- all query-specified attributes (color, size, brand, material, etc.) are satisfied
  - `partial` -- some but not all query-specified attributes are satisfied
  - `mismatch` -- the product contradicts one or more query-specified attributes
  - `n/a` -- the query does not specify any filterable attributes
- **REASONING**: concise justification grounded in the evaluation criteria (1-3 sentences)

### Rubric criteria

The rubric evaluates each pair against these criteria, in order of importance:

1. **Explicit intent match** -- Does the product match what the query literally asks for? ("red running shoes" should return red running shoes.)
2. **Implicit intent match** -- Does the product match what the shopper probably means, given the business context? Enterprise-specific guidance (brand priorities, certification requirements, domain jargon) is applied here.
3. **Category alignment** -- Is the product in the right product category? ("laptop stand" should return laptop stands, not laptops or standing desks.)
4. **Attribute matching** -- When the query specifies attributes (color, size, brand, material), does the product match them?
5. **Commercial viability** -- Is this something a shopper would actually buy? Out-of-stock items, discontinued products, or accessories without the main product score lower.

When an adapter returns `corrected_query`, the LLM prompt includes both the original and corrected queries so the judge can reason about correction impact.

## Deterministic checks

Deterministic checks run alongside LLM evaluation and catch structural quality issues without making any API calls. They are free and always enabled.

### Query-level

| Check | What it catches | Severity |
|---|---|---|
| `zero_results` | Query returned zero results | fail |
| `result_count` | Query returned fewer than 3 results | warning |

### Result-level

| Check | What it catches | Severity |
|---|---|---|
| `text_overlap` | Low token overlap (Jaccard similarity) between query and result text (title, category, description) | warning |
| `price_outlier` | Price far outside the result set norm, detected via IQR method (below Q1 - 1.5*IQR or above Q3 + 1.5*IQR) | warning |
| `duplicate` | Near-duplicate results detected by title similarity (SequenceMatcher ratio >= 0.85) | warning |
| `title_length` | Title shorter than 10 characters or longer than 120 characters | info |
| `out_of_stock_prominence` | Out-of-stock product at position 1 (fail) or positions 2-5 (warning) | fail / warning |

### Correction-level

These checks run only when the adapter returns `corrected_query`:

| Check | What it catches | Severity |
|---|---|---|
| `correction_vocabulary` | Tokens introduced by the correction do not appear in any result title or description (phantom correction) | warning |
| `unnecessary_correction` | Tokens removed by the correction still appear in results, suggesting the original was a valid catalog term | warning |

### Comparison-level

These checks run only in dual-config comparison mode (two adapters):

| Check | What it catches |
|---|---|
| `result_overlap` | Result set overlap between configurations (Jaccard index of product IDs) |
| `rank_correlation` | Spearman rank correlation for shared products between configurations |
| `position_shift` | Products that moved 3 or more positions between configurations |

You can add domain-specific checks with `--checks`. See [Custom Checks](custom-checks.md) for details.

## IR metrics

IR (Information Retrieval) metrics are computed from the LLM relevance scores to give aggregate quality measurements. All metrics are averaged across queries, with per-query and per-query-type breakdowns available in the output.

| Metric | Description |
|---|---|
| `ndcg@5` | Normalized Discounted Cumulative Gain at 5 (uses graded 0-3 scores) |
| `ndcg@10` | Normalized Discounted Cumulative Gain at 10 |
| `mrr` | Mean Reciprocal Rank (first result with score >= 2) |
| `map` | Mean Average Precision (results with score >= 2 are considered relevant) |
| `p@5` | Precision at 5 (fraction of top-5 results with score >= 2) |
| `p@10` | Precision at 10 (fraction of top-10 results with score >= 2) |
| `attribute_match@5` | Fraction of top-5 results with `match` or `partial` attribute verdict (queries with all `n/a` verdicts are excluded) |
| `attribute_match@10` | Fraction of top-10 results with `match` or `partial` attribute verdict |

**Relevance threshold:** MRR, MAP, and Precision treat results with score >= 2 as "relevant". This means a result must be at least "Relevant" (not just "Marginally relevant") to count as a hit.

**Attribute match exclusion:** `attribute_match@K` excludes queries where all results have an `n/a` attribute verdict (i.e., the query did not specify filterable attributes), so the metric only reflects queries where attribute matching is meaningful.

## Related docs

- [Enterprise Context](enterprise-context.md) -- business-specific evaluation rules
- [Custom Checks](custom-checks.md) -- add domain-specific deterministic checks
- [LLM Usage & Cost](llm-usage-and-cost.md) -- understanding API call volume
