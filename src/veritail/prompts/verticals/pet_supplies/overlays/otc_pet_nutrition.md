### OTC Pet Nutrition — Scoring Guidance

This query involves daily maintenance food, treats, or toppers for dogs and cats.

**Critical distinctions to enforce:**
- **AAFCO Naming Rules (Hard Constraint)**: Pet food labeling follows strict lexical rules.
  * "Chicken Dog Food" requires 95% chicken.
  * "Chicken Recipe/Dinner" requires 25% chicken.
  * "Dog Food WITH Chicken" requires only 3% chicken.
  * "Chicken Flavor" requires <3%.
  If a user searches for "Beef dog food", a product named "Dog Food with Beef"   is functionally a mismatch and should be penalized.
- **Life Stage Constraints**: "Large breed puppy" formulas are fundamentally different from standard puppy formulas. Large breeds require strictly controlled calcium (max 1.8% DM) to prevent developmental orthopedic disease. Standard puppy food is a severe mismatch for a large breed puppy query. Senior diets require lower calories and restricted phosphorus.
- **Human-Grade vs. Feed-Grade**: If a query specifies "human grade", the product must explicitly carry this claim. Feed-grade or rendered meat-meal products are unacceptable substitutes.
- **Toppers vs. Complete Diets**: "Food toppers", "broths", and "mixers" do not provide complete and balanced nutrition. Do not return toppers for a "dog food" query, and do not return complete kibble for a "dog food topper" query.
- **Ingredient Philosophies**: "Grain-free" means zero wheat, corn, rice, barley, or oats. "Limited ingredient" implies a targeted elimination diet, not just fewer flavors. Specific queried proteins (e.g., "Kangaroo", "Venison") must be matched exactly to prevent allergic reactions.
