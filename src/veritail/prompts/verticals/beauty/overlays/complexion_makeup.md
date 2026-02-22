### Complexion Makeup — Scoring Guidance

This query involves complexion/base makeup (foundation, concealer, skin tint, tinted moisturizer, BB/CC cream, primer, powders, and setting sprays).

**Critical distinctions to enforce:**

- **Shade identity is the product.** For complexion, the shade name/code is often the dominant match signal (e.g., "2N", "Warm Beige", "Deep 60", "Olive Medium"). A shade mismatch is a relevance failure even if the formula is otherwise right.
- **Undertone vocabulary is messy — use it carefully.** Terms like "cool/pink/rosy", "warm/yellow/golden", "neutral", and "olive/green" are undertone signals. However, letter codes like "N/C/W" are **not standardized** across brands. Only treat shade-code letters as meaningful when comparing within the same brand/line; otherwise prefer explicit undertone words.
- **Color corrector vs concealer vs foundation.** Color correctors target specific discoloration (green for redness, peach/orange for blue-brown under-eye tones, lavender for sallowness). Do not treat a "color corrector" query as a concealer/foundation query and vice versa.
- **Setting powder vs powder foundation.** Setting powder is meant to set base makeup; powder foundation is coverage makeup. A "powder foundation" query should not return translucent setting powders.
- **Primer vs setting spray.** Primers are applied before makeup; setting sprays after. Do not interchange unless the listing is explicitly a hybrid and the query allows.
- **Finish and coverage terms are meaningful.** Matte vs radiant/dewy, sheer/tint vs medium/full coverage, and "blurring" vs "glowy" are part of shopper intent. If specified, treat as a hard constraint.

**Terminology and shorthand (do not penalize lexical mismatches when intent aligns):**
- skin tint ≈ lightweight foundation / sheer base (not a concealer)
- BB/CC cream ≈ tinted base with skincare-like positioning (still a base product)
- "banana" powder usually implies a yellow-toned setting powder (not universal)
