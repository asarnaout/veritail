### Fresh Produce — Scoring Guidance

This query targets fresh fruits/vegetables/herbs (produce department).

**Critical distinctions to enforce:**

- **Fresh vs frozen vs shelf-stable**: If the query is for fresh produce ("fresh", "produce", or the item is typically sold fresh like bananas), do not return frozen/canned/dried versions unless the query explicitly allows it.
- **Variety and type matter**: Many produce items have materially different culinary uses (e.g., russet vs Yukon potatoes; Roma/plum vs slicing tomatoes; limes vs lemons). If the query specifies a variety/type, treat it as hard.
- **Organic is a certification**: If the query says organic, only organic-labeled produce is relevant; do not substitute "natural" or "pesticide-free" language.
- **Unit-of-measure and pack format**:
  * Many produce items are **variable-measure** (priced per lb/kg). A query like     "2 lb apples" usually means *about* 2 lb (not a fixed 2.00 lb SKU).
  * "each" vs "bunch" vs "bag" are different purchase units. "1 bunch cilantro"     should not return "cilantro paste" or "dried cilantro".
  * "3 lb bag" or "5 ct" is a fixed pack; treat that as hard when stated.

**Common produce vocabulary** (treat as near-synonyms when context matches):
- scallions = green onions
- bell pepper = sweet pepper
- cilantro (US) = coriander leaves (UK); coriander seeds are not the same item
- baby spinach vs spinach: not interchangeable when query is explicit

**Common disqualifiers / critical errors**:
- Returning plants/seed packets for edible produce queries (unless query asks).
- Returning pre-cut fruit trays for "whole" produce queries, or vice versa.
