### Fragrance — Scoring Guidance

This query involves fragrance products (not skincare).

**Critical distinctions to enforce:**

- **Concentration tier is a hard constraint when specified.** Parfum/extrait, EDP, EDT, and EDC/body mist are different concentration tiers and often sold as distinct SKUs. If the query specifies EDP vs EDT, do not substitute.
- **Flankers are distinct from originals.** Variants like "Intense", "Nectar", "Absolu", "Elixir", "Sport", and seasonal editions are separate fragrances. If the query names a flanker, return that flanker, not the base scent.
- **Format matters.** Spray vs rollerball vs solid perfume vs fragrance oil are different application formats. If specified, treat as hard.
- **Size constraints are common.** 10 ml travel spray vs 50 ml vs 100 ml is a real SKU constraint when specified.
- **Discovery sets are bundles.** A "discovery set" query expects multiple samples/minis, not a full-size bottle.

**Terminology:**
- body mist/body spray is typically lower concentration than EDT
- “cologne” can be gendered marketing; treat as a concentration/format clue only when explicit
