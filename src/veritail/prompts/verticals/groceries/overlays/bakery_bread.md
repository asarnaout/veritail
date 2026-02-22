### Bakery and Bread — Scoring Guidance

This query targets bread and bakery items (ready to eat), not baking ingredients.

**Critical distinctions to enforce:**

- **Item type**: Bread loaves, buns, rolls, bagels, tortillas/wraps are different products. Match the product type when specified.
- **Fresh bakery vs packaged**: If the query signals "fresh bakery" or "from the bakery", prefer bakery items over shelf-stable packaged bread.
- **Count and size**: "6 bagels" vs "12 rolls" vs "mini" vs "slider" buns are hard when specified.
- **Dietary variants**: gluten-free, keto, low-carb, or vegan bakery is a hard constraint when specified; do not substitute conventional bread.

**Common disqualifiers / critical errors**:
- Returning baking flour/yeast for "bread" or "bagels" queries (unless query is about baking supplies).
