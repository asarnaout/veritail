### Frozen Foods — Scoring Guidance

This query targets items intended to be stored and sold frozen.

**Critical distinctions to enforce:**

- **Frozen vs refrigerated**: Many categories are sold both refrigerated and frozen (pizza, ready meals). If the query says frozen, do not return refrigerated/shelf-stable versions.
- **Ice cream vs non-dairy desserts**: "ice cream" typically implies dairy; "non-dairy" or "plant-based" frozen desserts are separate. Treat dairy vs non-dairy as a hard boundary when specified.
- **IQF format**: For frozen fruit/veg/seafood, IQF means pieces are frozen individually (not clumped); if the query asks for IQF, treat it as a format constraint.
- **Preparation type**: "family size" frozen meal, "single serve", "snack", "appetizers" indicate different pack formats; match when specified.
