"""Beauty & personal care vertical context for LLM judge guidance."""

from veritail.types import VerticalContext, VerticalOverlay

BEAUTY = VerticalContext(
    core="""\
## Vertical: Beauty & Personal Care

You are evaluating search results for a beauty and personal care ecommerce \
site with expert-level domain knowledge spanning prestige, mass-market, \
professional, and clean-beauty channels.

### Scoring considerations

#### Hard constraints (violating any of these is a major relevance failure)

- **Named ingredients and concentrations are hard constraints.** When a \
query specifies an active or concentration ("10% niacinamide", "vitamin C \
serum", "0.25% retinol"), the product must contain it at the stated level. \
Exclusion terms ("sulfate-free", "paraben-free", "fragrance-free", etc.) \
are equally hard — returning a product containing the excluded ingredient \
is a critical failure. A 2% niacinamide product is a weak match for a \
query specifying 10%.
- **Shade and undertone are the top constraint for complexion products.** \
Undertone (warm, cool, neutral, olive — a frequently underserved \
combination of neutral-warm with green undertones) and depth (fair through \
rich/deep) together define the match space. A cool-toned result for a \
warm-toned query is a failure. "Nude" varies by skin tone — results must \
align with the implied depth range.
- **Pregnancy and breastfeeding safety is a critical safety constraint.** \
Retinoids (all forms including retinol, retinal, tretinoin, adapalene) \
must be excluded — fetal retinoid syndrome risk. Hydroquinone is \
contraindicated. High-dose salicylic acid (oral or chemical peels) is \
contraindicated; low-dose topical application (≤2% in cleansers or \
toners) is generally considered acceptable by most dermatologists. Safe \
alternatives include azelaic acid, glycolic acid, niacinamide, and \
vitamin C. Returning a retinoid for a "pregnancy-safe" query is a \
safety failure.
- **SPF and sun protection are FDA-regulated (OTC drug status in the \
US).** SPF level, UV filter type, and water resistance are hard \
constraints. "Mineral sunscreen" means zinc oxide and/or titanium \
dioxide only — not chemical filters. SPF 30 is not a match for SPF 50. \
Shoppers may use colloquial terms ("waterproof", "sunblock") for \
FDA-compliant products ("water-resistant 80 min", "sunscreen") — treat \
these as equivalent intent.
- **Skin type + concern must both align when both are specified.** A \
moisturizer for oily acne-prone skin answered with an occlusive cream \
for dry mature skin could worsen the shopper's condition. Products \
labeled "for all skin types" are acceptable but should score below \
products explicitly formulated for the stated type.
- **Hair type is a hard constraint including curl pattern (1A–4C), \
porosity, and treatment status.** A shampoo for 4C coily hair should \
not return products formulated for fine straight hair. Color-safe and \
sulfate-free are functional requirements for chemically processed hair. \
CGM (Curly Girl Method) compliance (no sulfates, no silicones, no heat) \
is a hard constraint when specified. Low-porosity hair is often \
protein-sensitive — recommending protein-heavy products can cause \
breakage.
- **Product form factor is a hard constraint.** Serum vs cream, spray vs \
powder, oil cleanser vs foaming cleanser, gel polish vs press-on nails, \
beauty tools and devices (LED masks, microcurrent) — the shopper chose a \
specific vehicle, texture, or application method intentionally. Do not \
treat form factors as interchangeable.
- **Certifications and ethical claims are verifiable hard constraints.** \
"Vegan" excludes all animal-derived ingredients (beeswax, carmine, \
lanolin, honey, animal-derived collagen/keratin, etc.). "Cruelty-free" \
should mean no animal testing, but standards vary — Leaping Bunny \
certification requires no testing at any supply chain stage, while other \
claims may be narrower. "USDA Organic" and "COSMOS certified" are \
specific verifiable standards. "Clean beauty" has no universal \
definition — it varies by retailer (Sephora, Ulta, Target, and Credo \
each maintain different excluded-ingredient lists). Do not treat "clean" \
as a single standard.
- **Fragrance concentration tier affects longevity and sillage.** \
Parfum/extrait > EDP > EDT > EDC > body mist. An EDT is not a match \
for an EDP query of the same fragrance. Flanker searches ("Flowerbomb \
Nectar") should return the specific flanker, not the original \
("Flowerbomb"). Niche houses (Byredo, Le Labo, MFK) are a distinct \
tier from designer fragrances.

#### Refinement guidance (distinguishes good from great matches)

- **Professional/clinical vs consumer tiers.** "Salon-grade", \
"medical-grade", "clinical strength" signal specific potency and \
distribution channels (SkinCeuticals, Obagi for clinical skincare; \
professional Olaplex No.0–2 vs retail No.3–8). Returning mass-market \
products for professional queries — or vice versa — is a tier mismatch.
- **Nail care specificity.** Nail shape names (coffin/ballerina, \
stiletto, almond, squoval) are specific filters for press-on nails. Gel \
polish, dip powder, press-ons, and regular polish are distinct product \
types — do not interchange.
- **Cultural beauty frameworks as search intent.** K-beauty (multi-step \
routines, essences as a distinct post-toner step, glass skin), J-beauty \
(minimalism, double cleansing), Ayurvedic (dosha-based), and French \
pharmacy (La Roche-Posay, Bioderma, Avène) are specific product \
discovery categories, not just geographic labels. "Essence" in K-beauty \
is NOT a synonym for toner or serum.
- **Dupe and alternative intent.** "Dupe for", "alternative to", \
"affordable version of" signal the shopper wants a functionally similar \
product at a lower price — not the luxury original itself. Returning \
the original product is a relevance failure.
- **Gender, demographic, and life-stage constraints.** Kids' products \
exclude harsh actives; teen acne products differ from adult formulations. \
Men's grooming subcategories (beard oil, pomade, body grooming) are \
distinct from women's-marketed equivalents. Gender-neutral/unisex is an \
increasingly explicit search intent.
- **Routine-step vocabulary.** "First cleanser" = oil-based (double \
cleanse step 1); "second cleanser" = water-based. Understand \
routine-position terms to avoid returning category-adjacent but \
functionally wrong products.
- **Regulatory claims awareness.** Marketing terms like "dermatologist \
tested", "dermatologist recommended", and "hypoallergenic" are \
unregulated. When a query uses these terms, match on the label claim \
itself — but do not treat them as equivalent to verified certifications \
(like "USDA Organic").""",
    overlays={
        "complexion_makeup": VerticalOverlay(
            description=(
                "Complexion/base makeup: foundation, concealer, skin tint, "
                "tinted moisturizer, BB/CC cream, powder (setting or foundation), "
                "primer, setting spray; includes shade/undertone matching."
            ),
            content="""\
### Complexion Makeup — Scoring Guidance

This query involves complexion/base makeup (foundation, concealer, skin tint, \
tinted moisturizer, BB/CC cream, primer, powders, and setting sprays).

**Critical distinctions to enforce:**

- **Shade identity is the product.** For complexion, the shade name/code is \
often the dominant match signal (e.g., "2N", "Warm Beige", "Deep 60", \
"Olive Medium"). A shade mismatch is a relevance failure even if the formula \
is otherwise right.
- **Undertone vocabulary is messy — use it carefully.** Terms like \
"cool/pink/rosy", "warm/yellow/golden", "neutral", and "olive/green" are \
undertone signals. However, letter codes like "N/C/W" are **not standardized** \
across brands. Only treat shade-code letters as meaningful when comparing \
within the same brand/line; otherwise prefer explicit undertone words.
- **Color corrector vs concealer vs foundation.** Color correctors target \
specific discoloration (green for redness, peach/orange for blue-brown under-eye \
tones, lavender for sallowness). Do not treat a "color corrector" query as a \
concealer/foundation query and vice versa.
- **Setting powder vs powder foundation.** Setting powder is meant to set \
base makeup; powder foundation is coverage makeup. A "powder foundation" \
query should not return translucent setting powders.
- **Primer vs setting spray.** Primers are applied before makeup; setting sprays \
after. Do not interchange unless the listing is explicitly a hybrid and the \
query allows.
- **Finish and coverage terms are meaningful.** Matte vs radiant/dewy, sheer/tint \
vs medium/full coverage, and "blurring" vs "glowy" are part of shopper intent. \
If specified, treat as a hard constraint.

**Terminology and shorthand (do not penalize lexical mismatches when intent aligns):**
- skin tint ≈ lightweight foundation / sheer base (not a concealer)
- BB/CC cream ≈ tinted base with skincare-like positioning (still a base product)
- "banana" powder usually implies a yellow-toned setting powder (not universal)
""",
        ),
        "eye_makeup": VerticalOverlay(
            description=(
                "Eye makeup & brows: mascara (including tubing), eyeliner (kohl/kajal), "
                "eyeshadow, false lashes, lash glue, brow pencils/gels, brow lamination."
            ),
            content="""\
### Eye Makeup & Brows — Scoring Guidance

This query involves eye makeup and brow products: mascara, eyeliner, eyeshadow, \
false lashes, lash adhesives, and brow products.

**Critical distinctions to enforce:**

- **Mascara subtypes matter.** "Tubing mascara" forms removable tubes and is \
typically removed with warm water — it is not interchangeable with traditional \
wax/oil-based formulas, and it behaves differently than "waterproof" mascara. \
If "tubing" or "waterproof" is specified, treat it as hard.
- **False lash types are not interchangeable.** Strip lashes, individuals, \
clusters, and extensions have different application workflows. If the query \
specifies a type (e.g., "clusters"), do not return strips.
- **Lash glue constraints.** "Latex-free" is a hard requirement when specified. \
Clear vs black adhesive can be a hard preference when the query is explicit.
- **Eyeliner form factor is a hard constraint.** Pencil/kohl, gel pot, liquid \
brush, felt-tip pen, and cake liners are distinct. "Kohl/kajal" often signals \
a smudgy pencil meant for the waterline or smoky looks — not a precise liquid \
wing liner.
- **Brow products are their own category.** Brow gel vs pencil vs pomade vs \
micro-tip pen are not interchangeable when specified, and tinted vs clear \
matters for gels/soaps.
- **Eye primer vs face primer.** Eye primers are formulated for lids and \
pigment adhesion. Do not return face primers for eye-primer queries.

**Terminology:**
- kohl = kajal (often used for smoky/waterline looks)
- tightline = applying liner at the lash line/waterline
- lash primer = base coat for mascara (not a lash serum)
""",
        ),
        "lip_products": VerticalOverlay(
            description=(
                "Lip products: lipstick (bullet or liquid), lip stain/tint, gloss, lip oil, "
                "balm, lip mask, lip liner; includes finish and long-wear claims."
            ),
            content="""\
### Lip Products — Scoring Guidance

This query involves lip products (color and/or treatment).

**Critical distinctions to enforce:**

- **Lip color vs lip treatment are different intents.** Lipstick/gloss/stain/lip \
liner are makeup. Lip balm and lip masks are treatment. If the query says \
"lip mask", "overnight", or "repair", do not return pure color lipsticks unless \
explicitly a hybrid treatment-tint.
- **Form factor is a hard constraint.** Bullet lipstick, liquid lipstick, lip \
stain, gloss, and lip oil behave differently. A "lip stain" query should not \
return opaque bullet lipsticks.
- **Finish terms matter.** Matte, satin, glossy, sheer, and shimmer finishes are \
intent signals. "Matte liquid lipstick" is not interchangeable with "lip gloss".
- **Long-wear/transfer-proof claims are category-specific.** If the query \
specifies "transfer-proof" or "mask-proof", prioritize formulas marketed for \
that performance; traditional creamy bullets are weaker matches.
- **Liner vs lipstick.** A lip liner query expects a pencil/liner product; do not \
return liquid lip color as a substitute.

**Terminology:**
- lip tint ≈ sheer color; lip stain usually implies longer-wear dye-like effect
- lip oil ≈ glossy treatment-like product with color optional
- plumping gloss/plumper typically implies a tingling/“warming” sensation; do not \
treat "plumper" as a normal gloss when specified
""",
        ),
        "cheek_color_contour": VerticalOverlay(
            description=(
                "Cheek makeup: blush, bronzer, contour, highlighter, illuminating drops; "
                "cream vs powder and undertone/finish are important."
            ),
            content="""\
### Cheek Color, Bronzer & Contour — Scoring Guidance

This query involves cheek products: blush, bronzer, contour, and highlighter.

**Critical distinctions to enforce:**

- **Contour is not bronzer.** Contour shades are typically cool/neutral (shadow-mimicking); bronzers are \
typically warm/golden. If the query says "contour", do not return warm bronzers as substitutes, and vice versa.
- **Highlight vs shimmer blush.** Highlighters are primarily reflective; blush is primarily pigment. \
Products can be hybrids, but do not substitute categories unless the listing clearly matches the intent.
- **Form factor matters.** Powder vs cream vs liquid vs stick are hard constraints when specified.
- **Shade family matters.** Pink/peach/berry/coral/terracotta and "neutral" descriptors constrain relevance. \
For bronzers, undertone terms like "neutral", "cool", "red" (too warm), and "olive" can matter when specified.

**Terminology:**
- illuminating drops / liquid highlighter = mix-in or liquid luminizer (not bronzer unless stated)
- contour stick = cream contour in stick format (not foundation stick)
""",
        ),
        "makeup_tools": VerticalOverlay(
            description=(
                "Makeup tools & brushes: face/eye brushes, sponges, applicators, "
                "brush sets, brush cleaner, lash curler, sharpeners, makeup organizers."
            ),
            content="""\
### Makeup Tools & Brushes — Scoring Guidance

This query involves makeup tools (not makeup products).

**Critical distinctions to enforce:**

- **Brush type and use-case matters.** Face brushes (foundation, powder, blush) \
vs eye brushes (blending, shader) vs brow/lip tools are distinct. If the query \
specifies a tool role (e.g., "angled brow brush"), treat it as hard.
- **Sponge vs brush.** "Makeup sponge"/"beauty blender-style" tools are not brush substitutes.
- **Tool vs cosmetic.** Do not score actual makeup products as matches for tool queries.
- **Cleaning and maintenance.** "Brush cleaner", "sponge soap", and "brush drying rack" \
are accessory categories — do not substitute with brushes.
- **Eyelash curler and sharpeners are specific tools.** Do not substitute accessories \
(e.g., tweezers) for a curler query unless explicitly requested.

**Terminology:**
- beauty sponge = blending sponge
- brush set = bundle of multiple brushes (not a single brush)
""",
        ),
        "cleansers_makeup_removal": VerticalOverlay(
            description=(
                "Facial cleansers & makeup removal: cleansing oil, cleansing balm, "
                "micellar water, makeup remover, face wash (gel/foam/cream), "
                "double cleansing (first cleanser vs second cleanser)."
            ),
            content="""\
### Cleansers & Makeup Removal — Scoring Guidance

This query involves cleansing and makeup-removal products.

**Critical distinctions to enforce:**

- **Cleansing oil/balm is not a leave-on face oil.** "Cleansing oil" and "cleansing balm" \
are rinse-off products designed to dissolve makeup/sunscreen and then emulsify with water. \
Do not treat facial oils/serums as substitutes.
- **Double cleansing has defined roles.** "First cleanser" typically implies an oil-based \
cleanser/balm; "second cleanser" a water-based cleanser (gel/foam/cream). Do not swap order \
or substitute one for the other when specified.
- **Micellar water is its own format.** It’s a watery cleanser/makeup remover used with cotton pads \
and may be marketed as no-rinse. Do not treat it as a foaming face wash.
- **Waterproof makeup removal is specific.** Queries specifying "waterproof mascara" often imply \
oil-based or biphasic removers; a gentle water-based cleanser alone is a weaker match.
- **Cleanser texture is often intent.** Gel vs foaming vs cream/milk vs oil vs balm are not equivalent \
when the query specifies texture.

**Terminology:**
- cleansing balm = makeup melting balm = cleansing butter
- biphasic = two-phase remover (shake-to-mix) often used for waterproof eye makeup
""",
        ),
        "exfoliants_peels": VerticalOverlay(
            description=(
                "Exfoliants & peels: physical scrubs, chemical exfoliants (AHA/BHA/PHA), "
                "enzyme exfoliants, peel pads, at-home peels, body exfoliators."
            ),
            content="""\
### Exfoliants & Peels — Scoring Guidance

This query involves exfoliation products and at-home peels.

**Critical distinctions to enforce:**

- **Physical vs chemical exfoliation are different categories.** Scrubs use abrasive particles (sugar, salt, \
jojoba beads, ground fruit pits). Chemical exfoliants use acids/enzymes. If the query specifies \
"physical scrub" or "chemical exfoliant", treat as hard.
- **AHA vs BHA vs PHA are not interchangeable when specified.**
  * AHA (e.g., glycolic, lactic, mandelic) are typically water-soluble surface exfoliants.
  * BHA typically means salicylic acid (oil-soluble; pore-focused).
  * PHA are larger-molecule acids often positioned as gentler options.
- **Leave-on vs rinse-off strength differs.** Exfoliating toners/serums/pads are leave-on; exfoliating \
cleansers are rinse-off. If the query implies a leave-on step ("peel pads", "exfoliating toner"), do not \
treat rinse-off cleansers as equivalent.
- **“Peel” can mean different products.** At-home peels (gel/serum/pads) are not professional-strength \
chemical peels. Do not treat "chemical peel" intent as a face scrub.
- **Microbead awareness for scrubs.** Rinse-off cosmetics cannot contain intentionally-added plastic microbeads \
in the US; scrub beads are typically biodegradable alternatives. If a result is explicitly described as \
plastic microbeads, treat as problematic.

**Terminology:**
- peel pads = pre-soaked exfoliating pads (usually acid-based)
- enzyme exfoliant often uses fruit enzymes (gentler positioning) but is still a chemical exfoliation approach
""",
        ),
        "acne_and_breakouts": VerticalOverlay(
            description=(
                "Acne & breakouts: benzoyl peroxide, salicylic acid (BHA), adapalene, "
                "azelaic acid, acne cleansers, spot treatments, pimple patches "
                "(hydrocolloid), blackhead/whitehead treatments."
            ),
            content="""\
### Acne & Breakouts — Scoring Guidance

This query involves acne treatment or breakout control.

**Critical distinctions to enforce:**

- **Active ingredient identity matters.** Common acne actives include benzoyl peroxide, salicylic acid, \
topical retinoids (including adapalene), and azelaic acid. If the query specifies an active and/or \
a percentage, treat it as a hard requirement.
- **Pimple patches are a distinct product type.** Non-medicated hydrocolloid patches act as a protective \
barrier and absorb fluid from superficial blemishes; they are not the same as leave-on chemical treatments. \
If the query asks for "pimple patches" / "hydrocolloid", do not return acne creams/serums instead.
- **Spot treatment vs all-over treatment is not interchangeable.** Spot gels/patches are localized; cleansers \
and toners cover broader areas. If the query says "spot", prioritize spot products.
- **Blackhead vs inflamed acne intent differs.** "Blackheads/pores" often implies BHA/salicylic acid or \
cleansing-focused products; "cystic/hormonal" queries often imply stronger treatment categories. Do not \
treat pore strips or scrubs as equivalents to acne actives when the query is explicit.
- **“Non-comedogenic” is a label claim, not a regulated standard.** Match the claim if requested, but do not \
assume any product is non-comedogenic unless stated.

**Terminology:**
- BHA usually refers to salicylic acid
- hydrocolloid patch = pimple patch = acne patch (format)
""",
        ),
        "retinoids_antiaging": VerticalOverlay(
            description=(
                "Retinoids & anti-aging: retinol, retinal/retinaldehyde, retinyl esters, "
                "tretinoin (Rx), adapalene, anti-wrinkle serums/creams; includes pregnancy-safe exclusions."
            ),
            content="""\
### Retinoids & Anti-Aging — Scoring Guidance

This query involves retinoids/retinoid-like anti-aging products.

**Critical distinctions to enforce:**

- **Retinoid family terms are often conflated — do not conflate them when specified.**
  * retinol (common cosmetic form)
  * retinal / retinaldehyde (distinct ingredient; often positioned as stronger than retinol)
  * retinyl esters (e.g., retinyl palmitate) are distinct and typically milder positioning
  * prescription retinoids (e.g., tretinoin) are distinct products and often not sold as standard cosmetics
  If the query names one of these explicitly, require that ingredient.
- **Strength descriptors are meaningful.** "0.1% retinol" or "0.05% retinal" are hard constraints when present. \
"Beginner retinol" / "gentle" vs "high-strength" are intent signals; do not substitute extremes.
- **Encapsulated retinol is still retinol.** Encapsulation is a delivery/stability claim, not a different active.
- **Pregnancy-safe queries must exclude retinoids.** If the query includes pregnancy/breastfeeding safety, \
treat any retinoid-containing product as a safety failure even if marketed as gentle.
- **“Retinol alternatives” are not retinoids.** Bakuchiol and peptide products may be positioned as \
retinol alternatives; do not treat them as retinol unless the query asks for alternatives.

**Terminology:**
- vitamin A derivative is often used to describe retinoids/retinol (still ingredient-specific)
""",
        ),
        "brightening_dark_spots": VerticalOverlay(
            description=(
                "Dark spots & brightening: vitamin C (L-ascorbic acid and derivatives), "
                "niacinamide, tranexamic acid, kojic acid, arbutin, hyperpigmentation "
                "serums, melasma care; excludes hydroquinone unless explicitly requested."
            ),
            content="""\
### Dark Spots & Brightening — Scoring Guidance

This query involves brightening, hyperpigmentation, or dark-spot correction.

**Critical distinctions to enforce:**

- **Hydroquinone is an exception case.** In the US, hydroquinone is not approved for OTC sale. If the query \
explicitly asks for hydroquinone, only products that clearly contain hydroquinone are direct matches; do not \
substitute "brightening" alternatives unless the query requests an alternative.
- **“Vitamin C” is not always L-ascorbic acid.** Many products use vitamin C derivatives (e.g., magnesium \
ascorbyl phosphate, sodium ascorbyl phosphate, ascorbyl glucoside, 3-O-ethyl ascorbic acid, THD ascorbate). \
If the query explicitly asks for **L-ascorbic acid**, the product must contain L-ascorbic acid specifically. \
If the query says "vitamin C" broadly, derivatives are acceptable but still should be explicitly stated.
- **Niacinamide % and other concentrations are hard constraints when present.** If no % is specified, \
do not assume potency from marketing terms like "10% complex" unless the product clearly states it.
- **Spot corrector vs brightening cleanser vs toner are different intents.** A "dark spot serum" query should \
not be satisfied by a basic cleanser with a brightening claim unless the query is broad.

**Terminology:**
- hyperpigmentation = dark spots = discoloration (but causes vary; match the product’s stated use)
- melasma often implies stubborn pigmentation; prioritize products marketed for melasma when specified
""",
        ),
        "hydration_barrier_repair": VerticalOverlay(
            description=(
                "Hydration & barrier repair: hyaluronic acid (HA), glycerin, ceramides, "
                "barrier creams, moisturizers for sensitized/irritated skin; occlusive vs "
                "lightweight textures matter."
            ),
            content="""\
### Hydration & Barrier Repair — Scoring Guidance

This query involves hydrating products and/or barrier repair.

**Critical distinctions to enforce:**

- **Humectant vs occlusive intent.** Hydrators (hyaluronic acid/HA, glycerin) focus on water-binding; \
occlusives (petrolatum/ointment-style, some balms) focus on sealing. If the query specifies "lightweight gel" \
do not return heavy occlusive balms; if it specifies "barrier balm/ointment", do not return light serums.
- **Barrier repair has a typical ingredient vocabulary.** Ceramides (often labeled ceramide NP/AP/EOP), \
cholesterol, and fatty acids signal barrier-lipid support. If the query requests "ceramide" or "barrier repair", \
prefer products that explicitly list these.
- **Sensitive / compromised barrier positioning matters.** Queries mentioning "irritated", "sensitized", \
"post-procedure", or "eczema-prone" imply low-irritant formulas and minimal fragrance. Treat mismatched \
irritating actives as a failure.
- **Texture/form factor is intent.** Gel-cream vs cream vs ointment vs facial oil vs mist are not interchangeable \
when specified.

**Terminology:**
- HA commonly abbreviates hyaluronic acid in skincare contexts
- “slugging” is typically an occlusive final step (often petrolatum-based) — not a hydrating serum
""",
        ),
        "masks_and_treatments": VerticalOverlay(
            description=(
                "Masks & treatments: sheet masks, clay/mud masks, wash-off masks, "
                "sleeping masks/overnight masks, peel-off masks, targeted treatment masks."
            ),
            content="""\
### Masks & Treatments — Scoring Guidance

This query involves face masks or mask-like treatments.

**Critical distinctions to enforce:**

- **Mask format is a hard constraint.** Sheet masks, wash-off masks (clay/cream), \
sleeping/overnight masks, and peel-off masks are distinct. Do not substitute between them when specified.
- **Clay/mud is typically oil-control intent.** If the query specifies clay/mud/charcoal, \
do not return purely hydrating sleeping masks.
- **Sleeping mask ≠ sheet mask.** A sleeping mask is a leave-on overnight final step; sheet masks \
are single-use drenched fabrics used for a set time.
- **Eye/lip masks are subcategories.** Do not return full-face masks for eye-patch or lip-mask queries.

**Terminology:**
- sleeping mask = overnight mask (leave-on)
- wash-off mask = rinse-off mask
""",
        ),
        "sunscreen_spf": VerticalOverlay(
            description=(
                "Sunscreen & SPF: facial/body sunscreen, mineral vs chemical, broad-spectrum, "
                "water-resistant 40/80 minutes, sun sticks, tinted sunscreen, PA/UVA logos."
            ),
            content="""\
### Sunscreen & SPF — Scoring Guidance

This query involves sun protection products.

**Critical distinctions to enforce:**

- **SPF number is a hard constraint.** SPF 30 is not equivalent to SPF 50 when a specific SPF is requested.
- **Broad spectrum is not implied by SPF alone.** If the query requests broad-spectrum or UVA protection, \
require a product explicitly labeled broad spectrum (or an equivalent UVA rating system in non-US products).
- **Mineral/physical sunscreen has a strict meaning.** Mineral/physical sunscreens use zinc oxide and/or \
titanium dioxide as UV filters. If the query says mineral/physical, do not return chemical-filter sunscreens.
- **Water resistance labeling is standardized.** "Waterproof" is shopper language; the compliant intent is \
water-resistant with a time claim (40 min or 80 min). If the query specifies 80 min, 40 min is not a match.
- **Sunscreen vs SPF makeup.** Many moisturizers/foundations include SPF, but if the query explicitly asks for \
"sunscreen" or "sunblock", prefer products clearly marketed/labeled as sunscreen products.
- **Tint is a shade-like constraint.** "Tinted mineral sunscreen" implies both the filter type and a tint \
that should suit the shopper’s skin depth/undertone terms when given.

**UVA rating vocabulary (helpful for international products):**
- PA system (PA+ to PA++++) is a UVA protection indicator used on many Asian sunscreens.
- EU/UK often use a "UVA in a circle" logo indicating minimum UVA protection relative to SPF.
""",
        ),
        "sunless_tanning": VerticalOverlay(
            description=(
                "Sunless tanning & bronzing: self-tanner with DHA, tanning drops, gradual tanner, "
                "express mousse, spray tan solutions, bronzers vs self-tanners; NOT sunscreen."
            ),
            content="""\
### Sunless Tanning & Bronzing — Scoring Guidance

This query involves sunless tanning / bronzing products.

**Critical distinctions to enforce:**

- **Self-tanner vs bronzer are different intents.**
  * Self-tanners typically use DHA (dihydroxyacetone) and develop over hours by reacting with skin proteins \
at the surface.
  * Bronzers are cosmetic color (immediate, often wash-off) and do not “develop” a tan.
  If the query requests "self tanner" or "DHA", do not return makeup bronzers.
- **Self-tanner is not SPF.** A self-tanner product does not substitute for sunscreen. If the query requests SPF, \
require a product that explicitly includes sunscreen protection.
- **Format is intent.** Drops (mix-in), mousse/foam, lotion, spray, and tanning wipes/mitts are not equivalent \
when specified.
- **Color depth is a constraint.** "Light", "medium", "dark", "ultra dark", and "olive" self-tanners are shade-like \
constraints; match them when specified.

**Terminology:**
- gradual tanner = buildable daily-use self-tanner
- express/1-hour indicates rapid-developing formulas (not a bronzer)
""",
        ),
        "shampoo_conditioner": VerticalOverlay(
            description=(
                "Hair cleansing & conditioning: shampoo, conditioner, co-wash, clarifying shampoo, "
                "dry shampoo, purple shampoo/toning shampoo, anti-dandruff shampoo, color-safe."
            ),
            content="""\
### Shampoo & Conditioner — Scoring Guidance

This query involves hair cleansing or conditioning products.

**Critical distinctions to enforce:**

- **Shampoo vs conditioner vs co-wash are not interchangeable.** Co-wash/cleansing conditioner is a low-foam \
cleanser for textured/dry hair. Do not return conditioners for shampoo queries unless co-wash is explicitly requested.
- **Dry shampoo is not shampoo.** Dry shampoo absorbs oil at the roots (a powder/spray format) and does not \
replace wash-off cleansers for "shampoo" queries.
- **Clarifying is a specific intent.** "Clarifying" implies buildup removal. Do not treat a gentle daily shampoo \
as a substitute when the query is explicit.
- **Toning shampoos have color-theory intent.** Purple shampoo deposits violet pigment to neutralize yellow/brassy \
tones in blonde/silver/gray hair. It is not a general hair-repair shampoo. If the query says purple/toning, require \
a toning product.
- **Color-safe and sulfate-free are functional constraints when specified.** Especially for color-treated/chemically \
processed hair, these claims should be treated as hard when requested.

**Terminology:**
- purple shampoo = toning shampoo = silver shampoo (blonde/gray toning intent)
- co-wash = cleansing conditioner
""",
        ),
        "textured_curl_hair": VerticalOverlay(
            description=(
                "Textured hair & curls: wavy/curly/coily (2A–4C), Curly Girl Method (CGM), "
                "curl creams, gels, leave-ins, porosity, protein sensitivity, protective styling."
            ),
            content="""\
### Textured Hair & Curls — Scoring Guidance

This query involves wavy/curly/coily hair care (often 2A–4C) and textured-hair routines.

**Critical distinctions to enforce:**

- **CGM compliance is rule-based when specified.** If the query requests CGM/Curly Girl Method, treat the \
absence of sulfates, silicones, and harsh drying alcohols (and often avoiding heat) as hard constraints.
- **Porosity language changes product intent.** Low-porosity hair often implies buildup-prone routines and \
protein sensitivity; high-porosity often implies damage and higher need for conditioning/sealing. If porosity \
is specified, prioritize products positioned for that porosity profile.
- **Definition and hold products are distinct.** Curl creams focus on moisture/definition; gels focus on hold and \
cast formation; mousses are usually lighter. Do not substitute across these when the query is explicit.
- **Detangling and protective styling are specific sub-intents.** "Detangler", "slip", "braid-out", \
"twist cream", "edge control" should route to the correct functional product type.

**Terminology:**
- “wash day” often implies a full curly routine (cleanse, condition, style)
- “cast” refers to the crunchy gel film that is later “scrunched out”
""",
        ),
        "hair_color_toning": VerticalOverlay(
            description=(
                "Hair color & toning: permanent/demi/semi dye, bleach/lightener, toner, gloss, "
                "developer volumes (10/20/30/40), root touch-up, color-depositing masks."
            ),
            content="""\
### Hair Color & Toning — Scoring Guidance

This query involves hair coloring, lightening, toning, or color maintenance.

**Critical distinctions to enforce:**

- **Deposit vs lift is fundamental.** Permanent color + developer can lift natural hair; toners/glosses are \
typically deposit/adjustment steps; bleach/lightener is for significant lift. Do not substitute a deposit-only \
product for a bleaching/lightening query.
- **Developer “volume” is a hard spec when stated.** Common mapping: 10 vol = 3%, 20 vol = 6%, 30 vol = 9%, \
40 vol = 12% hydrogen peroxide. If the query specifies volume, treat mismatched volume as a failure.
- **Toner is not purple shampoo.** Toners are chemical color-correction steps; purple shampoo is a maintenance \
product. Do not interchange when specified.
- **Color families matter.** Ash vs golden, cool vs warm, copper vs red, and "blue/black" are shade constraints. \
If the query specifies a shade family, enforce it.
- **Root touch-up formats are distinct.** Root sprays/powders/sticks (temporary camouflage) are not the same as \
permanent dye kits.

**Terminology:**
- demi-permanent ≈ deposit with low/no lift; semi-permanent ≈ direct dye/no developer (unstandardized marketing)
- gloss/glaze usually implies shine + tone adjustment (often demi)
""",
        ),
        "hair_styling_and_tools": VerticalOverlay(
            description=(
                "Hair styling & tools: heat protectants, blow dryers, flat irons, curling wands, "
                "brushes/combs, styling creams, gels, mousses, pomades, wax, hairspray, texturizers."
            ),
            content="""\
### Hair Styling & Tools — Scoring Guidance

This query involves hair styling products and/or styling tools.

**Critical distinctions to enforce:**

- **Tool vs product.** Do not return styling products for tool queries (e.g., "blow dryer") and vice versa.
- **Heat protectant is a specific functional category.** If the query asks for heat protection, prioritize products \
explicitly marketed as heat protectants; a hair oil is not an equivalent substitute unless explicitly a heat-protectant oil.
- **Hold and finish terms constrain relevance.** Strong/extra hold vs flexible hold, matte vs shine, \
texturizing vs smoothing/anti-frizz are not interchangeable when specified.
- **Tool form factors are hard constraints.** Flat iron vs curling wand vs hot brush vs blow-dry brush are distinct \
tools with different results; do not substitute.
- **Voltage/dual-voltage relevance.** For travel/dual-voltage queries, require explicit dual-voltage listing \
(especially for heated tools).

**Terminology:**
- pomade/wax/clay are usually styling pastes with different finishes; match when specified
- blowout brush = hot air brush = blow-dry brush (tool, not a round brush)
""",
        ),
        "fragrance": VerticalOverlay(
            description=(
                "Fragrance: perfume/parfum, extrait, eau de parfum (EDP), eau de toilette (EDT), "
                "cologne, body mist, rollerball, fragrance oil, discovery sets, flankers."
            ),
            content="""\
### Fragrance — Scoring Guidance

This query involves fragrance products (not skincare).

**Critical distinctions to enforce:**

- **Concentration tier is a hard constraint when specified.** Parfum/extrait, EDP, EDT, and EDC/body mist \
are different concentration tiers and often sold as distinct SKUs. If the query specifies EDP vs EDT, \
do not substitute.
- **Flankers are distinct from originals.** Variants like "Intense", "Nectar", "Absolu", "Elixir", "Sport", \
and seasonal editions are separate fragrances. If the query names a flanker, return that flanker, not the base scent.
- **Format matters.** Spray vs rollerball vs solid perfume vs fragrance oil are different application formats. \
If specified, treat as hard.
- **Size constraints are common.** 10 ml travel spray vs 50 ml vs 100 ml is a real SKU constraint when specified.
- **Discovery sets are bundles.** A "discovery set" query expects multiple samples/minis, not a full-size bottle.

**Terminology:**
- body mist/body spray is typically lower concentration than EDT
- “cologne” can be gendered marketing; treat as a concentration/format clue only when explicit
""",
        ),
        "nails": VerticalOverlay(
            description=(
                "Nails: regular nail lacquer, gel polish (UV/LED cure), dip powder, acrylic, "
                "press-on nails, nail shapes (almond/coffin/stiletto/squoval), base/top coats."
            ),
            content="""\
### Nails — Scoring Guidance

This query involves nail products and nail enhancements.

**Critical distinctions to enforce:**

- **Nail product systems are not interchangeable.**
  * Regular lacquer/“nail polish” air-dries.
  * Gel polish requires UV/LED curing and is removed differently (often soak-off).
  * Dip powder uses a resin + powder system (no lamp) and is distinct from gel.
  * Acrylic uses liquid monomer + polymer powder and air-dries; distinct from gel systems.
  If the query specifies gel/dip/acrylic/press-on, enforce the system.
- **Press-ons are a product category.** They are not gel polish and not acrylic systems. If the query is \
press-ons, results should be nail sets or press-on kits (often with glue/tabs).
- **Nail shapes and lengths matter for press-ons.** Coffin/ballerina, stiletto, almond, square, squoval, etc. \
are hard constraints when specified.
- **Base coat vs top coat vs builder/bond products are distinct.** A "top coat" query should not return base coats \
or builder gels unless explicitly a combo.
- **Allergy/“HEMA-free” is a hard constraint when specified.** Acrylate allergies are a known issue in nail systems; \
if the query requests HEMA-free or “sensitive”, require that claim explicitly.

**Terminology:**
- gel-like top coat often means lacquer top coat with gel-shine effect (not UV-cured gel) unless curing is stated
""",
        ),
        "body_care_personal": VerticalOverlay(
            description=(
                "Body & personal care: body wash, body scrub, body lotion/oil, body acne care, "
                "deodorant and antiperspirant, hand/foot care, hair removal, oral care."
            ),
            content="""\
### Body & Personal Care — Scoring Guidance

This query involves body-focused personal care products.

**Critical distinctions to enforce:**

- **Body vs face is a real boundary.** Body lotions/cleansers/treatments are formulated and sized differently \
from facial products. If the query says "body", do not return face-only products.
- **Deodorant vs antiperspirant differ by function and regulation.** Antiperspirants reduce sweating and are \
OTC drug products with specific active ingredients. Deodorants primarily address odor and are cosmetics. \
If the query explicitly asks for "antiperspirant", do not return deodorants-only products as substitutes. \
If the query says "aluminum-free", that typically implies deodorant intent (not antiperspirant).
- **Body scrub vs body wash.** Scrubs are exfoliating; washes are cleansers. Do not interchange when specified.
- **Body acne has specific cues.** Queries like "bacne", "KP", or "body acne spray" imply body-specific acne formats \
(sprays, washes, lotions) and should not return tiny face spot treatments unless explicitly requested.
- **Hair removal formats are distinct.** Razor, wax, sugar wax, epilator, depilatory cream, and laser/IPL devices \
are different categories; do not substitute.

**Terminology:**
- KP = keratosis pilaris (often queried as “strawberry legs”)
""",
        ),
        "gift_sets_kits": VerticalOverlay(
            description=(
                "Gifts, value sets & kits: skincare sets, makeup sets, hair sets, "
                "fragrance gift sets, discovery sets, minis/travel bundles, duos/trios."
            ),
            content="""\
### Gift Sets, Value Sets & Kits — Scoring Guidance

This query involves multi-item sets, kits, bundles, or minis.

**Critical distinctions to enforce:**

- **A set must contain multiple items.** If the query says "set", "kit", "value set", "duo", "trio", \
"bundle", or "discovery set", do not return a single standalone product as a match.
- **Type of set matters.** Skincare kits, makeup kits, hair kits, and fragrance discovery sets are different \
bundle types. Match the category when the query is explicit.
- **Discovery set vs full-size fragrance.** Discovery sets typically are sample vials/travel sprays across \
multiple scents; do not substitute with one full-size bottle.
- **Mini/travel size is a constraint.** "Mini", "travel", "trial size" imply smaller sizes; full-size-only \
results are weaker matches unless the listing explicitly includes minis.
- **Holiday/limited editions are versioned.** Sets are often seasonal and change year to year; if the query \
names an edition, require that edition.

**Terminology:**
- gift-with-purchase (GWP) is not the same as a purchasable set unless explicitly sold as a set
""",
        ),
    },
)
