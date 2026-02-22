### Pantry, Cooking, and Baking Staples — Scoring Guidance

This query targets shelf-stable pantry staples and cooking/baking ingredients.

**Critical distinctions to enforce:**

- **Ingredient identity is not fuzzy**: Similar items are not interchangeable (baking soda vs baking powder; cornstarch vs flour; soy sauce vs tamari). When specified, treat the exact ingredient type as hard.
- **Form factor matters**: whole vs ground (spices), diced vs whole peeled (canned tomatoes), dry pasta vs fresh pasta are not automatic substitutes.
- **San Marzano nuance**:
  * "DOP" / "PDO" in a San Marzano query indicates Protected Designation of     Origin. Require the result to explicitly show the DOP/PDO designation (or     the full protected name) rather than "San Marzano style" language.
  * If the query says "San Marzano style", then "style" products are acceptable.
- **Oil grade and style**: "extra virgin" vs "refined" olive oil are different; "spray" vs liquid is a different format. Treat grade/format as hard when stated.
- **Dietary variants**: "gluten-free pasta", "low-sodium broth", etc must match the dietary claim; do not assume.

**Common disqualifiers / critical errors**:
- Returning ready-to-eat meals/snacks for a pure ingredient query (and vice versa).
