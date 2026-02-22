### Coffee and Tea — Scoring Guidance

This query targets coffee or tea products (not machines).

**Critical distinctions to enforce:**

- **Form is hard**: whole bean vs ground vs instant are not equivalent when specified. Espresso grind vs drip grind can be functionally wrong if the query is explicit.
- **Pods/capsule compatibility is hard**:
  * Keurig "K-Cup" pods are a specific format.
  * Nespresso Original and Nespresso Vertuo systems use different capsules that     are not interchangeable; if the query specifies one, do not return the other.
  Do not assume compatibility unless the product explicitly states it.
- **Caffeinated vs decaf**: treat "decaf" as hard.
- **Tea format**: bags vs loose leaf vs bottled RTD are distinct; match when specified.
- **Type and flavor**: "Earl Grey" vs "English Breakfast"; "green" vs "black"; "herbal" (often caffeine-free) vs caffeinated tea are hard when specified.

**Common disqualifiers / critical errors**:
- Returning coffee creamers/sweeteners for coffee-beans/pods queries (unless asked).
