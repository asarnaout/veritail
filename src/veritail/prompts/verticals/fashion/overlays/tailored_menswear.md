### Tailored Menswear: Suits, Dress Shirts, Formalwear — Scoring Guidance

This query is about tailored menswear: suits, blazers/sport coats, tuxedos, dress shirts, dress trousers, and formal dress-code items.

**Critical distinctions to enforce:**

- **Suit jacket sizes use chest + length code**: Sizes like "40R" mean a chest size with a jacket length (Short/Regular/Long). Treat wrong length codes (S/R/L) as meaningful fit mismatches when specified.
- **"Drop" links jacket and trouser waist in many suit listings**: A "drop" describes the difference between jacket chest size and trouser waist size (often a fixed pairing off-the-rack). If the query specifies a drop or a trouser waist, enforce it.
- **Tuxedo vs suit is a category boundary**: A tuxedo (black tie) is not just a black suit. If the query is black tie/tuxedo, do not score ordinary suits highly.
- **Dress shirt numerical sizing is neck × sleeve**: Sizes like "15/32" (or "15 32/33") encode neck (inches) and sleeve length. If the query specifies this format, treat it as a hard requirement rather than mapping it loosely to S/M/L.
- **Event dress codes imply formality levels**: "Black tie optional" allows tuxedo or formal suit; "black tie" implies tuxedo-level formality. Treat under-formal items as poor matches even if color is correct.

**Terminology / jargon to interpret correctly:**

- "Sport coat"/"blazer" are distinct from a full suit, but are still tailored outer layers; do not substitute casual jackets.
- "Morning suit", "white tie" are higher-formality categories; only match if explicitly requested.
