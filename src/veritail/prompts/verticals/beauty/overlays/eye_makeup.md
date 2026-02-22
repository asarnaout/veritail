### Eye Makeup & Brows — Scoring Guidance

This query involves eye makeup and brow products: mascara, eyeliner, eyeshadow, false lashes, lash adhesives, and brow products.

**Critical distinctions to enforce:**

- **Mascara subtypes matter.** "Tubing mascara" forms removable tubes and is typically removed with warm water — it is not interchangeable with traditional wax/oil-based formulas, and it behaves differently than "waterproof" mascara. If "tubing" or "waterproof" is specified, treat it as hard.
- **False lash types are not interchangeable.** Strip lashes, individuals, clusters, and extensions have different application workflows. If the query specifies a type (e.g., "clusters"), do not return strips.
- **Lash glue constraints.** "Latex-free" is a hard requirement when specified. Clear vs black adhesive can be a hard preference when the query is explicit.
- **Eyeliner form factor is a hard constraint.** Pencil/kohl, gel pot, liquid brush, felt-tip pen, and cake liners are distinct. "Kohl/kajal" often signals a smudgy pencil meant for the waterline or smoky looks — not a precise liquid wing liner.
- **Brow products are their own category.** Brow gel vs pencil vs pomade vs micro-tip pen are not interchangeable when specified, and tinted vs clear matters for gels/soaps.
- **Eye primer vs face primer.** Eye primers are formulated for lids and pigment adhesion. Do not return face primers for eye-primer queries.

**Terminology:**
- kohl = kajal (often used for smoky/waterline looks)
- tightline = applying liner at the lash line/waterline
- lash primer = base coat for mascara (not a lash serum)
