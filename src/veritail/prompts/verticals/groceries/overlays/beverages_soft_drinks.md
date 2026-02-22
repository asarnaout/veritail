### Beverages (Non-Alcohol) — Scoring Guidance

This query targets non-alcoholic drinks and drink mixes.

**Critical distinctions to enforce:**

- **Diet vs zero vs regular**: "Diet" and "Zero Sugar" are distinct SKUs; do not substitute unless the query is broad.
- **Caffeinated vs caffeine-free**: If the query specifies caffeine-free or decaf, treat it as hard (important for sensitivity/medical reasons).
- **Packaging format is hard**: cans vs bottles; single vs multipack; "12 x 12 oz" is not equivalent to "6 x 16.9 oz" even if total volume is close.
- **Sparkling water vocabulary**:
  * seltzer/sparkling water: carbonated water (often no sweetener)
  * club soda: carbonated water with minerals (mixer positioning)
  * tonic water: contains quinine and is usually sweetened; not a seltzer substitute
  If the query says tonic, do not return seltzer (and vice versa).
- **Powder / liquid drink mixes**: "electrolyte powder" vs RTD bottled drink are not interchangeable unless the query is broad.

**Common disqualifiers / critical errors**:
- Confusing alcoholic seltzer/RTD cocktails with non-alcoholic seltzer when the query is non-alcoholic (and vice versa).
