### Lip Products — Scoring Guidance

This query involves lip products (color and/or treatment).

**Critical distinctions to enforce:**

- **Lip color vs lip treatment are different intents.** Lipstick/gloss/stain/lip liner are makeup. Lip balm and lip masks are treatment. If the query says "lip mask", "overnight", or "repair", do not return pure color lipsticks unless explicitly a hybrid treatment-tint.
- **Form factor is a hard constraint.** Bullet lipstick, liquid lipstick, lip stain, gloss, and lip oil behave differently. A "lip stain" query should not return opaque bullet lipsticks.
- **Finish terms matter.** Matte, satin, glossy, sheer, and shimmer finishes are intent signals. "Matte liquid lipstick" is not interchangeable with "lip gloss".
- **Long-wear/transfer-proof claims are category-specific.** If the query specifies "transfer-proof" or "mask-proof", prioritize formulas marketed for that performance; traditional creamy bullets are weaker matches.
- **Liner vs lipstick.** A lip liner query expects a pencil/liner product; do not return liquid lip color as a substitute.

**Terminology:**
- lip tint ≈ sheer color; lip stain usually implies longer-wear dye-like effect
- lip oil ≈ glossy treatment-like product with color optional
- plumping gloss/plumper typically implies a tingling/“warming” sensation; do not treat "plumper" as a normal gloss when specified
