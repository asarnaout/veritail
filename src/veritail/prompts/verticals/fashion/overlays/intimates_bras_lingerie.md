### Intimates, Bras, and Lingerie — Scoring Guidance

This query is about bras, underwear, lingerie sets, shapewear, and intimate apparel.

**Critical distinctions to enforce:**

- **Bra sizing is dual-parameter**: A bra size includes both band and cup (e.g., 34DD). Treat mismatching either component as a major relevance failure because returns are extremely likely.
- **International cup alphabets differ**: UK and US cup progressions diverge above D (e.g., UK uses DD, E, F, FF… while US often uses DD, DDD/F, G… depending on brand). If the query specifies UK/EU/US sizing, enforce that system; do not assume letters match across systems.
- **EU band sizes are centimeter-based**: EU-style bands (65, 70, 75, …) are not the same numbers as US/UK bands (30, 32, 34, …). If the query uses the EU system, prefer explicit EU sizing in results.
- **Sister sizes are not "close enough" unless the shopper signals flexibility**: Sister sizing keeps cup volume similar by trading band and cup (e.g., band up, cup down). If the query is precise (or includes "exact"), do not treat sister sizes as full matches.
- **Wire/structure features are functional**: Underwire vs wireless, strapless vs standard straps, padded vs unlined, and "minimizer/push-up" are not purely style attributes when specified.

**Terminology / jargon to interpret correctly:**

- "Bralette" usually implies lighter support and often S/M/L sizing; a molded-cup underwire bra is not a bralette.
- "G-string/thong" vs "brief" vs "boyshort" are distinct underwear cuts when called out.
- "Shapewear" implies compression/contouring intent; do not substitute ordinary underwear.
