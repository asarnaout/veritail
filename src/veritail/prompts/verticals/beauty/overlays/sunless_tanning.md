### Sunless Tanning & Bronzing — Scoring Guidance

This query involves sunless tanning / bronzing products.

**Critical distinctions to enforce:**

- **Self-tanner vs bronzer are different intents.**
  * Self-tanners typically use DHA (dihydroxyacetone) and develop over hours by reacting with skin proteins at the surface.
  * Bronzers are cosmetic color (immediate, often wash-off) and do not “develop” a tan.
  If the query requests "self tanner" or "DHA", do not return makeup bronzers.
- **Self-tanner is not SPF.** A self-tanner product does not substitute for sunscreen. If the query requests SPF, require a product that explicitly includes sunscreen protection.
- **Format is intent.** Drops (mix-in), mousse/foam, lotion, spray, and tanning wipes/mitts are not equivalent when specified.
- **Color depth is a constraint.** "Light", "medium", "dark", "ultra dark", and "olive" self-tanners are shade-like constraints; match them when specified.

**Terminology:**
- gradual tanner = buildable daily-use self-tanner
- express/1-hour indicates rapid-developing formulas (not a bronzer)
