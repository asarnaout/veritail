### Alcohol (Beer, Wine, Spirits, RTD) — Scoring Guidance

This query targets beverage alcohol sold on grocery platforms that carry it.

**Critical distinctions to enforce:**

- **Alcoholic vs non-alcoholic is a hard boundary**: Many categories have NA versions. If the query says non-alcoholic/0.0, do not return alcoholic and vice versa.
- **Type and style**:
  * Beer style matters (IPA vs lager vs stout).
  * Wine varietal/style matters (Cabernet vs Pinot; red vs white; sparkling vs still).
  * Spirits type matters (vodka vs gin vs rum vs tequila; flavored vs unflavored).
- **Strength terminology**:
  * ABV is the alcohol by volume percentage.
  * Proof (US) is twice the ethanol % by volume; if the query specifies proof/ABV,     treat mismatches as errors.
- **Pack format**: single vs 6-pack vs 12-pack vs case; cans vs bottles; "750 mL" vs "1.75 L" are hard when specified.
- **Hard seltzer vs seltzer water**: hard seltzer is alcoholic; seltzer water is non-alcoholic. Do not confuse them.

**Note**: Some gluten-free labeling rules differ between FDA-regulated foods and TTB-regulated alcohol products; when the query specifies gluten-free alcohol, require explicit gluten-free labeling rather than assumptions.
