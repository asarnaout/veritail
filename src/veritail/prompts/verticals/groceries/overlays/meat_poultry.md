### Meat and Poultry — Scoring Guidance

This query targets meat/poultry (beef, pork, chicken, turkey, lamb; excluding fish/shellfish).

**Critical distinctions to enforce:**

- **Species + cut + form are hard**: Beef vs pork vs chicken vs turkey are not substitutes. Within a species, cut/form matters (ribeye vs chuck; breast vs thigh; ground vs whole muscle; bone-in vs boneless). If specified, treat as hard.
- **Fresh vs frozen (poultry nuance)**: For poultry, "fresh" is a specific labeling term meaning the product has never been held below 26°F. If the query says fresh poultry, do not return frozen/previously frozen.
- **"Natural" is not an animal-raising guarantee**: For FSIS-regulated meat and poultry, "natural" refers to no artificial ingredients/added color and minimal processing — it does not imply organic, no antibiotics, or pasture access.
- **Hormone claims nuance**: Federal regulations prohibit the use of hormones in pork and poultry production; "no hormones" claims on those products are typically accompanied by a disclaimer. Do not treat "hormone-free chicken" as a meaningful differentiator unless the query explicitly demands the label.
- **Ground meat ratios**: "80/20" vs "90/10" are different fat/lean blends. If the query specifies a ratio, treat it as hard.
- **Raw vs cooked**: raw vs cooked/smoked/breaded/seasoned are different products. Treat preparation state as hard when specified.

**Common disqualifiers / critical errors**:
- Returning deli lunchmeat for raw meat queries (and vice versa) unless query is broad.
