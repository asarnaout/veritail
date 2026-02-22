### Deli, Cheese Counters, and Prepared Foods — Scoring Guidance

This query targets deli-counter items, deli meats/cheeses, or ready-to-eat/heat prepared foods.

**Critical distinctions to enforce:**

- **Deli counter vs pre-packaged**: "deli sliced", "thin sliced", "shaved", or "from the deli" implies sliced-to-order service items (variable weight, per lb). Do not treat a fixed-weight pre-packaged item as equivalent unless the query is broad.
- **Variable weight is normal**: Many deli meats/cheeses/salads are priced per lb/kg and filled to an approximate weight. A "1 lb" query may mean *about* 1 lb unless a fixed-weight pack is clearly specified in the result.
- **Preparation level**:
  * Ingredient intent ("deli turkey", "provolone") should not return a composed     sandwich or meal kit unless the query asks for it.
  * Meal intent ("ready-to-eat", "heat and serve", "prepared meal", "rotisserie")     should not return raw ingredients.
- **Cheese format**: block vs sliced vs shredded vs deli-sliced are distinct; match the requested format when specified.

**Common disqualifiers / critical errors**:
- Returning shelf-stable "snack packs" for deli-counter per-lb queries, or vice versa.
