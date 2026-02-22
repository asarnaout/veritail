"""Fashion vertical context for LLM judge guidance."""

from veritail.types import VerticalContext, VerticalOverlay

FASHION = VerticalContext(
    core="""\
## Vertical: Fashion

You are evaluating search results for a fashion and apparel site. Judge whether each \
result satisfies the shopper's intent with the eye of a fashion buyer who understands \
fit, style, and the return risk that comes from getting either one wrong.

### Scoring considerations

- **Gender and demographic alignment is a hard gate**: If a query specifies or \
strongly implies a gender (men's, women's, boys', girls'), returning the wrong gender \
is a critical relevance failure. "Unisex" items may satisfy unconstrained queries, but \
unisex apparel often runs larger on women since it may follow men's proportions. Kids' \
sizing is an entirely separate system — baby (by months), toddler (2T-5T), kids \
(XS-XL or numerical) — and must never be mixed with adult results. Gender-neutral or \
non-binary queries seek products explicitly designed or marketed without gender \
designation; returning gendered products is a partial mismatch even if the item could \
physically be worn by anyone.
- **Size system and fit profile are hard requirements**: When a query specifies a size \
system (US, UK, EU, Asian), a size value, or a fit descriptor (petite, plus, big & tall, \
slim, relaxed, oversized), treat these as non-negotiable constraints. Women's apparel \
numerical sizes often convert roughly (e.g., US 8 ≈ UK 12 ≈ EU 40), but conversions vary \
by brand and product type; do not treat a number from one system as a match for another \
without explicit conversion context. For shoes, half-size precision and width \
designations (narrow, wide, extra-wide) are often critical because shoe fit tolerance \
is much tighter than apparel. Note that brand-to-brand sizing variance is significant \
in fashion.
- **Inclusive and specialty sizing are hard constraints**: Plus-size, petite, tall, \
maternity, and adaptive clothing queries name specific fit requirements that standard-\
size results cannot satisfy. Adaptive fashion features (magnetic closures, seated-fit \
cuts, sensory-friendly fabrics) are functional requirements, not style preferences — \
treat them like compatibility constraints. Conversely, maternity-specific products \
should not score highly for non-maternity queries unless explicitly marketed as \
dual-purpose.
- **Occasion, style, and modesty intent carry implicit constraints**: Terms like \
"wedding guest", "business casual", "cocktail", "black tie", or "modest" encode \
strong expectations about formality, silhouette, coverage, and often price tier. \
"Wedding guest" implicitly excludes white. Occasion queries are high-stakes because \
the shopper has a specific event and timeline.
- **Color, pattern, and material are explicit constraints when stated**: When a query \
names a specific color, match it precisely — near-synonym shades (navy vs dark blue) \
are partial matches, not exact. Material queries ("silk blouse", "cashmere sweater", \
"leather jacket") treat composition as central to intent; faux or synthetic \
alternatives should score lower unless the query signals openness ("vegan leather") \
or the product clearly discloses the substitution. Performance claims in the query \
(waterproof, stretch, breathable, wrinkle-free, compression) are functional \
requirements, not soft preferences.
- **Sustainability and ethical attributes are hard constraints when stated**: "Vegan \
leather boots" returning genuine leather is a hard fail regardless of other \
attributes. "Organic cotton" is commonly used as a certification claim; conventional \
cotton is not a match. Terms like recycled, fair trade, and cruelty-free are explicit \
constraints that must be satisfied by the product. Greenwashing (vague "eco-friendly" \
claims without specifics) is a weaker match than verified certifications.
- **Category boundary and item type must match shopper intent**: If a query names a \
primary wearable category ("blazer", "jeans", "ankle boots"), returning non-wearable \
adjacent items (care kits, stuffing/forms, shoe trees) is irrelevant. If a query names \
an accessory type ("silk scarf", "belt", "handbag"), do not return primary garments. \
Treat "replacement strap", "shoe care", and "bag charm" as accessory/part queries, not \
the main item.
- **Brand and price-tier signals encode quality expectations**: Brand names and tier \
cues ("designer", "luxury", "budget", "affordable") signal expectations about \
materials, craftsmanship, and price range. Returning fast-fashion results for a luxury \
query — or vice versa — is a relevance mismatch. For navigational queries containing a \
specific brand name, wrong-brand results are a hard fail.
- **Trend and aesthetic vocabulary encodes attribute bundles**: Fashion shoppers use \
aesthetic terms ("quiet luxury", "dark academia", "coquette", "streetwear") that \
encode expectations about silhouette, palette, fabric quality, branding visibility, \
and price tier. Era terms ("Y2K", "90s") similarly encode specific style expectations. \
A result that matches the garment category but misses the aesthetic entirely is a poor \
match.
- **Seasonality and inventory recency**: Basic climate appropriateness applies — do \
not return wool coats for summer queries or linen for winter queries unless the query \
explicitly asks for off-season items. Beyond climate, fashion-specific timing matters: \
"new arrivals" or "this season" queries should return current-season inventory, not \
prior-season clearance.
- **Condition and resale context**: For secondhand or resale queries, condition \
grading (mint, excellent, good) and authenticity signals are meaningful attributes. \
"Vintage", "pre-owned", and "deadstock" are distinct conditions with different shopper \
expectations. Era terms in resale contexts can be both aesthetic and temporal \
descriptors.
""",
    overlays={
        "sneakers_athletic_shoes": VerticalOverlay(
            description=(
                "Sneakers, trainers, and athletic shoes (running, walking, training, basketball, "
                "tennis, skate, trail). Includes shoe sizing scales (men/women/kids) and widths."
            ),
            content="""\
### Sneakers and Athletic Shoes — Scoring Guidance

This query is about sneakers/trainers or sport-oriented athletic shoes (running, walking, \
training, basketball, tennis, skate, trail).

**Critical distinctions to enforce:**

- **Sport/use-case terms are not interchangeable**: "running shoes" vs "basketball \
shoes" vs "skate shoes" vs "cleats" imply different constructions and should not be \
treated as generic substitutes.
- **Men’s vs women’s size scales differ**: A common rule of thumb is women’s US size ≈ \
men’s US size + 1.5, but conversions are approximate and brand-dependent. Do not treat \
a men’s size as a direct match for the same number in women’s sizing (or vice versa) \
unless the listing explicitly provides the conversion or indicates unisex sizing.
- **Width codes matter**: Letter/number widths depend on the gendered scale. Many \
catalogs treat men’s "D" as standard while women’s "B" is standard; women’s "D" often \
indicates wide. If the query specifies narrow/wide/2E/4E/etc., treat width as a hard \
constraint, not a preference.
- **Kids shoe notation is distinct**: Kids sizing often uses "C" (child) and "Y" \
(youth) markers, or ranges like "Little Kids" and "Big Kids". Do not score adult sizes \
as matches for kids queries (or vice versa) even when the numeric value overlaps.
- **Model-name heavy queries are navigational**: If the query includes a specific shoe \
model name/colorway/collab/release nickname, wrong-model results are near-zero.

**Terminology / jargon to interpret correctly:**

- "trainer" is often used as a synonym for sneaker in UK usage, but can also mean a \
"training shoe" (gym/cross-training). Use surrounding terms (running/gym/lifting) to \
decide.
- "deadstock"/"DS" in sneaker resale contexts implies new/unworn condition; do not \
treat "worn once" as deadstock.

**Common scoring pitfalls:**

- Treating lifestyle sneakers as adequate for explicit performance queries (e.g., \
trail-running, court sports) without the stated feature set.
- Ignoring width constraints or kids/adult scale mismatches, which are high-return \
drivers for footwear.
""",
        ),
        "boots": VerticalOverlay(
            description=(
                "Boots (ankle, chelsea, combat, hiking, work, rain, snow, knee-high, over-the-knee). "
                "Covers shaft height, calf width, and weatherproofing terms."
            ),
            content="""\
### Boots — Scoring Guidance

This query is about boots (ankle, chelsea, combat, hiking, cowboy/western, work, \
rain, snow, knee-high, over-the-knee).

**Critical distinctions to enforce:**

- **Boot height is a product-defining attribute**: "ankle boots" vs "mid-calf" vs \
"knee-high" vs "over-the-knee" are not interchangeable. If the query specifies a height \
class, treat mismatched heights as a major failure even if "boot" matches.
- **Calf/shaft fit terms are hard constraints**: "wide calf", "extra wide calf", \
"WC/XWC", or a shaft-circumference measurement exists because standard shafts won't fit. \
Do not score standard-calf boots highly for a wide-calf query (and vice versa).
- **Weatherproofing terminology must match claimed intent**: If the query says \
"waterproof" or references heavy weather use (snow/rain), treat "water-resistant" only \
as a partial match unless the listing explicitly claims waterproof construction.
- **Functional subtype matters**: Hiking boots, work boots, rain boots, and fashion \
boots are not direct substitutes when the query specifies use-case-driven terms like \
"steel toe", "non-slip", "insulated", or "rain boot".

**Terminology / jargon to interpret correctly:**

- "Chelsea boot" usually implies elastic side gussets and pull tabs (slip-on boot).
- "Duck boot" often implies a rubber lower with a leather/nylon upper and wet-weather \
intent; do not substitute with fashion ankle boots.
- "Insulated" (e.g., winter/snow boots) is a functional requirement, not a style cue.
""",
        ),
        "sandals_slides": VerticalOverlay(
            description=(
                "Sandals and slides (flip-flops/thongs, slides, strappy sandals, wedges, espadrilles, "
                "open-back mules). Warm-weather open footwear."
            ),
            content="""\
### Sandals and Slides — Scoring Guidance

This query is about open footwear: sandals, slides, flip-flops/thongs, mules (open-back), \
espadrilles, wedges, and similar warm-weather shoes.

**Critical distinctions to enforce:**

- **Slide vs flip-flop vs strappy sandal are distinct**: A "slide" is typically a \
single (or few) strap(s) with no toe post; a "flip-flop/thong" has a toe post. If the \
query specifies one, do not treat the others as direct matches.
- **Heel profile matters when specified**: Flat vs wedge vs platform vs heeled sandal \
are not interchangeable when the query calls out heel type or height.
- **Water use vs street use**: "Pool slide", "shower slide", and "water sandal" imply \
materials and traction intended for wet surfaces; do not score fashion leather sandals \
highly for those intents unless the listing explicitly claims water suitability.
- **Support/comfort claims are functional**: If the query specifies arch support, \
orthopedic/comfort, or similar, treat it as a functional requirement, not marketing \
fluff.

**Terminology / jargon to interpret correctly:**

- "Espadrille" implies a jute/rope-style midsole construction; do not substitute with \
generic wedges when the material signal is explicit.
""",
        ),
        "heels_and_dress_shoes": VerticalOverlay(
            description=(
                "Dress shoes and heels (pumps, stilettos, platforms, flats like ballet/Mary Jane, "
                "loafers, oxfords/derbies). Heel height and toe shape matter."
            ),
            content="""\
### Heels and Dress Shoes — Scoring Guidance

This query is about dressier footwear: pumps, stilettos, kitten heels, platforms, \
dress flats (ballet flats, mary janes), loafers, oxfords, derbies, and occasion shoes.

**Critical distinctions to enforce:**

- **Heel height/type are hard constraints when specified**: "kitten heel", "stiletto", \
"block heel", and "platform" describe structurally different shoes. If heel height is \
called out in inches/mm, treat it as a hard spec, not a style suggestion.
- **Toe shape can be decisive**: Pointed vs square vs round-toe may be explicitly \
requested and should not be ignored.
- **Occasion terms tighten constraints**: "wedding heels", "bridal shoes", "office \
loafers", or "black tie shoes" imply appropriate formality; overly casual sneakers or \
rubber slides should score near-zero even if the color matches.
- **Men’s dress shoe types are not just aesthetics**: "Oxford" (more formal) vs "derby" \
(more casual) and "loafer" (slip-on) can be meaningful when the query specifies them.

**Terminology / jargon to interpret correctly:**

- "Pumps" usually implies a closed-toe, closed-heel shoe with a heel; open-toe sandals \
are not pumps.
- "Mary Jane" usually implies a strap across the instep; do not substitute with plain \
ballet flats when the strap detail is central.
""",
        ),
        "denim_jeans": VerticalOverlay(
            description=(
                "Denim and jeans (raw/dry denim, selvedge, stretch, washes; skinny/straight/bootcut/"
                "wide-leg). Often uses waist×inseam sizing."
            ),
            content="""\
### Denim and Jeans — Scoring Guidance

This query is about denim garments, especially jeans (and sometimes denim jackets/skirts \
when explicitly requested).

**Critical distinctions to enforce:**

- **Raw/dry denim vs washed denim**: "Raw", "dry", or "unwashed" denim refers to denim \
that has not been pre-washed/processed. Washed, heavily distressed, or "pre-faded" jeans \
are poor matches for raw denim queries.
- **Selvedge denim is about how the fabric is woven**: "Selvedge/selvage" indicates a \
self-finished edge from shuttle-loom weaving. Selvedge is not synonymous with raw; \
enforce the exact term that the shopper used.
- **Sanforized vs unsanforized (shrink-to-fit) matters**: If the query signals \
"shrink-to-fit" or unsanforized denim, expect shrink after wash; treat standard \
pre-shrunk denim as a mismatch when the shopper explicitly wants shrink-to-fit behavior.
- **Denim weight ("oz") is not decorative**: Ounce weight refers to fabric weight; \
when specified (e.g., 12oz, 16oz), treat it as a quality/feel constraint.
- **Size notation is often waist × inseam**: Queries like "W32 L34" or "32x34" are \
usually waist (inches) and inseam (inches). Treat mismatched inseam as a meaningful \
relevance failure for shoppers who care about length.

**Terminology / jargon to interpret correctly:**

- "Rigid" denim typically means little/no stretch; "stretch" implies elastane and \
a softer fit tolerance.
- "Rise" cues where the waistband sits; "low/mid/high rise" are meaningful fit \
constraints when specified.
- "Leg opening" / "taper" matters for fits like straight vs slim vs skinny vs bootcut \
vs wide-leg; do not treat these as interchangeable when the query is explicit.

**Common scoring pitfalls:**

- Treating "black jeans" and "dark wash indigo" as equivalent; wash/color are primary \
for denim shoppers.
- Returning jeggings or coated pants for a denim query unless the query signals openness.
""",
        ),
        "intimates_bras_lingerie": VerticalOverlay(
            description=(
                "Intimates: bras, underwear, lingerie sets, shapewear. Band+cup sizing, international "
                "size-system differences, and support features."
            ),
            content="""\
### Intimates, Bras, and Lingerie — Scoring Guidance

This query is about bras, underwear, lingerie sets, shapewear, and intimate apparel.

**Critical distinctions to enforce:**

- **Bra sizing is dual-parameter**: A bra size includes both band and cup (e.g., 34DD). \
Treat mismatching either component as a major relevance failure because returns are \
extremely likely.
- **International cup alphabets differ**: UK and US cup progressions diverge above D \
(e.g., UK uses DD, E, F, FF… while US often uses DD, DDD/F, G… depending on brand). \
If the query specifies UK/EU/US sizing, enforce that system; do not assume letters match \
across systems.
- **EU band sizes are centimeter-based**: EU-style bands (65, 70, 75, …) are not the \
same numbers as US/UK bands (30, 32, 34, …). If the query uses the EU system, prefer \
explicit EU sizing in results.
- **Sister sizes are not "close enough" unless the shopper signals flexibility**: \
Sister sizing keeps cup volume similar by trading band and cup (e.g., band up, cup down). \
If the query is precise (or includes "exact"), do not treat sister sizes as full matches.
- **Wire/structure features are functional**: Underwire vs wireless, strapless vs \
standard straps, padded vs unlined, and "minimizer/push-up" are not purely style \
attributes when specified.

**Terminology / jargon to interpret correctly:**

- "Bralette" usually implies lighter support and often S/M/L sizing; a molded-cup \
underwire bra is not a bralette.
- "G-string/thong" vs "brief" vs "boyshort" are distinct underwear cuts when called out.
- "Shapewear" implies compression/contouring intent; do not substitute ordinary underwear.
""",
        ),
        "activewear_athleisure": VerticalOverlay(
            description=(
                "Activewear/athleisure (leggings, yoga/gym/running gear, sports bras, performance layers). "
                "Performance claims like moisture-wicking and support levels."
            ),
            content="""\
### Activewear and Athleisure — Scoring Guidance

This query is about activewear/athleisure (leggings, yoga pants, gym tops, running \
gear, sports bras, performance layers).

**Critical distinctions to enforce:**

- **Performance claims are functional constraints**: If the query says moisture-wicking, \
quick-dry, breathable, compression, squat-proof, or anti-odor, treat these as functional \
requirements, not aesthetic preferences.
- **Moisture-wicking is not "any synthetic"**: Moisture-wicking implies moving sweat to \
the fabric surface and drying quickly; a generic cotton tee is a poor match for explicit \
wicking/quick-dry intent.
- **Sports bra support level should match activity when specified**: "High impact" \
implies running/jumping/HIIT support; low-impact bras are mismatches for high-impact \
queries unless the shopper explicitly prioritizes comfort over support.
- **Activity-specific terms tighten constraints**: "Running tights" vs "yoga leggings" \
vs "cycling shorts" imply different construction details (pockets, compression, seams, \
chafe control). Treat cross-activity substitutions as partial matches at best.
- **Thermal layering words are meaningful**: "Base layer", "midlayer", "thermal", \
"fleece-lined" imply warmth and layering use; do not treat them as generic tops.

**Terminology / jargon to interpret correctly:**

- "Athleisure" refers to athletic-inspired clothing intended for both exercise and \
everyday wear; treat explicit athleisure queries as balancing performance + style.
- "Compression" is sometimes used loosely in fashion; when the query is medical-grade \
(compression stockings in mmHg), require an explicit pressure rating.
""",
        ),
        "outerwear_rain_down": VerticalOverlay(
            description=(
                "Outerwear for weather and warmth (coats, puffers, parkas, rain jackets, shells). "
                "Waterproof vs water-resistant, down fill power, and 3-in-1 systems."
            ),
            content="""\
### Outerwear: Coats, Puffers, Rainwear — Scoring Guidance

This query is about outerwear used for warmth and/or weather protection (coats, \
jackets, puffers, parkas, rain jackets, shells).

**Critical distinctions to enforce:**

- **Waterproof vs water-resistant is not interchangeable**: "Water-resistant" usually \
means light/short rain protection; "waterproof" implies sustained rain protection. \
If the query says waterproof, treat water-resistant-only products as partial matches.
- **Down "fill power" is quality, not total warmth**: Fill power measures loft per \
ounce of down (efficiency). Warmth also depends on how much insulation is used (fill \
weight) and construction. Do not assume "800-fill" is warmer than "650-fill" without \
considering the amount of insulation and the intended temperature range.
- **Insulation type matters when specified**: Down vs synthetic insulation are \
different performance profiles (especially in wet conditions). If the query specifies \
down/synthetic, enforce it.
- **3-in-1 jackets are multi-piece systems**: A "3-in-1" typically includes an outer \
shell plus an inner insulating layer that can be worn together or separately. Do not \
treat a single insulated jacket as a 3-in-1.
- **Form-factor and silhouette are functional for outerwear**: "Trench coat", "parka", \
"bomber", "pea coat" are distinct product types; do not collapse them into "jacket".

**Terminology / jargon to interpret correctly:**

- "Shell" usually means an uninsulated outer layer meant for weather protection or \
wind; a puffer is not a shell.
- "DWR" (durable water repellent) is a surface treatment that helps water bead; it \
does not automatically mean the garment is fully waterproof.
""",
        ),
        "tailored_menswear": VerticalOverlay(
            description=(
                "Tailored menswear and formalwear (suits, blazers, tuxedos, dress shirts, dress trousers). "
                "40R sizing, drop, and dress-code terminology."
            ),
            content="""\
### Tailored Menswear: Suits, Dress Shirts, Formalwear — Scoring Guidance

This query is about tailored menswear: suits, blazers/sport coats, tuxedos, dress shirts, \
dress trousers, and formal dress-code items.

**Critical distinctions to enforce:**

- **Suit jacket sizes use chest + length code**: Sizes like "40R" mean a chest size with \
a jacket length (Short/Regular/Long). Treat wrong length codes (S/R/L) as meaningful \
fit mismatches when specified.
- **"Drop" links jacket and trouser waist in many suit listings**: A "drop" describes \
the difference between jacket chest size and trouser waist size (often a fixed pairing \
off-the-rack). If the query specifies a drop or a trouser waist, enforce it.
- **Tuxedo vs suit is a category boundary**: A tuxedo (black tie) is not just a black \
suit. If the query is black tie/tuxedo, do not score ordinary suits highly.
- **Dress shirt numerical sizing is neck × sleeve**: Sizes like "15/32" (or "15 32/33") \
encode neck (inches) and sleeve length. If the query specifies this format, treat it as \
a hard requirement rather than mapping it loosely to S/M/L.
- **Event dress codes imply formality levels**: "Black tie optional" allows tuxedo or \
formal suit; "black tie" implies tuxedo-level formality. Treat under-formal items as \
poor matches even if color is correct.

**Terminology / jargon to interpret correctly:**

- "Sport coat"/"blazer" are distinct from a full suit, but are still tailored \
outer layers; do not substitute casual jackets.
- "Morning suit", "white tie" are higher-formality categories; only match if explicitly \
requested.
""",
        ),
        "swimwear_upf": VerticalOverlay(
            description=(
                "Swimwear and sun-protective swim apparel (bikinis, one-pieces, tankinis, swim trunks, "
                "boardshorts, rash guards). UPF terms and coverage intent."
            ),
            content="""\
### Swimwear and Sun-Protective Swim — Scoring Guidance

This query is about swimwear (bikinis, one-pieces, tankinis, swim trunks, boardshorts) \
and/or sun-protective swim apparel (rash guards, UPF swim shirts).

**Critical distinctions to enforce:**

- **UPF is a specific protection rating when stated**: UPF indicates how much UV \
radiation passes through fabric. If the query specifies UPF (e.g., UPF 50/50+), require \
an explicit UPF rating; do not treat a generic "swim shirt" as a full match.
- **Rash guards are purpose-built**: A rash guard is typically a close-fitting swim top \
designed to reduce chafing and provide sun protection; treat it as distinct from casual \
t-shirts.
- **Boardshorts vs swim trunks differ**: Boardshorts commonly have a fixed waist and \
longer cut; swim trunks often use an elastic waist and may include a mesh liner. If the \
query specifies one, do not substitute the other.
- **Two-piece styles are not interchangeable**: A tankini (tank-style top + bottoms) \
is different from a bikini top. If the query asks for tankini/modest coverage, enforce \
that coverage intent.

**Terminology / jargon to interpret correctly:**

- "Surf suit"/"swim leggings" and other coverage swimwear are functional for sun and \
water sport use; do not substitute standard swim pieces when coverage is explicit.
""",
        ),
        "kids_baby_apparel": VerticalOverlay(
            description=(
                "Kids and baby apparel sizing (preemie/NB/3M-24M, 2T-5T, kids 6X, youth ranges/XS-XL; "
                "regular/slim/husky/plus)."
            ),
            content="""\
### Kids and Baby Apparel — Scoring Guidance

This query is about baby/toddler/kids apparel (and sometimes kids shoes when explicitly \
stated). Treat kids sizing systems as distinct from adult sizing.

**Critical distinctions to enforce:**

- **Baby sizing uses months and fit-for-diaper proportions**: Labels like NB, 3M, 6M, \
12M, 24M are age/month signals. 24M and 2T can both correspond to "two years", but \
they may be cut differently (e.g., room for diapers vs more "toddler" proportions). \
Do not treat them as guaranteed equivalents when the query is specific.
- **Toddler sizing uses the "T" system**: 2T–5T is its own range; do not substitute \
adult XS/S or older kids numeric sizing when the query is clearly toddler.
- **Kids "in-between" and fit codes matter**: 6X (between 6 and 7), and fit codes like \
regular/slim/husky/plus exist because body proportions differ. If the query specifies \
these, treat them as hard constraints.
- **Youth sizing can be numeric or XS–XL**: When the query uses numeric youth ranges \
(e.g., 10–12, 14–16) or alpha sizes, enforce that system rather than mapping loosely \
to adult sizing.

**Terminology / jargon to interpret correctly:**

- P = preemie, NB = newborn, M = months, T = toddler (common label conventions).
- "Husky" in kids apparel typically signals a wider fit; do not ignore when specified.

**Common scoring pitfalls:**

- Mixing "kids" and "adult" items because a numeric size overlaps.
- Treating "unisex" as permission to return adult items for kids queries.
""",
        ),
        "jewelry_precious_metals": VerticalOverlay(
            description=(
                "Jewelry (rings, necklaces, bracelets, earrings, watches). Metal/purity/plating terms "
                "(karat vs carat, vermeil, gold-filled) and size constraints."
            ),
            content="""\
### Jewelry and Precious Metals — Scoring Guidance

This query is about jewelry (rings, necklaces, bracelets, earrings, watches) where \
metal type, plating, and size are often the shopper's primary constraints.

**Critical distinctions to enforce:**

- **Karat vs carat are different units**: Karat (K) describes gold purity (e.g., 14K, \
18K). Carat (ct) is gemstone weight. Do not confuse them when the query specifies one.
- **Gold coating terms are regulated and not interchangeable**: Terms like "gold filled", \
"gold plate(d)", "gold electroplate", and "vermeil" imply specific constructions. If \
the query specifies one, require that exact term/value rather than a generic "gold tone".
- **Vermeil has a specific base-metal expectation**: In regulatory usage, "vermeil" \
means gold plating over a sterling silver base. Do not treat brass-based gold plating \
as vermeil.
- **Size is functional for jewelry**: Ring sizes (and bracelet/necklace lengths) are \
fit constraints. If the query specifies a size system (US/UK/EU) or an exact size, \
treat mismatches as major failures.

**Terminology / jargon to interpret correctly:**

- "Sterling silver" usually implies 925 silver; avoid substituting generic "silver tone".
- "Gold tone" typically signals a non-precious coating without a guaranteed karat value.
- "Nickel-free" is often a sensitivity constraint; treat it as hard if stated.
""",
        ),
        "resale_vintage": VerticalOverlay(
            description=(
                "Resale/vintage/pre-owned: condition grading and acronyms (NWT/NWOT/EUC), vintage vs retro, "
                "and 'deadstock/DS' terminology."
            ),
            content="""\
### Resale, Vintage, and Pre-Owned — Scoring Guidance

This query is about secondhand resale, vintage, or pre-owned fashion where condition and \
authenticity signals materially change shopper intent.

**Critical distinctions to enforce:**

- **Condition acronyms are meaningful**: NWT (new with tags), NWOT (new without tags), \
and EUC (excellent used condition) are not interchangeable. If the query specifies \
one, require matching condition language or equivalent evidence.
- **"Vintage", "archival", and "antique" are distinct concepts**: "Vintage" often implies \
decades-old pieces and carries expectations of era-appropriate construction and sizing. \
Do not treat "vintage style" (new retro-inspired items) as vintage when the query asks \
for actual vintage.
- **"Deadstock" is context-sensitive**: In sneaker/resale contexts, "deadstock/DS" \
commonly means brand new, unworn condition with original packaging expectations. Do not \
treat lightly used items as deadstock.
- **Authentication intent is a hard constraint when stated**: If the query says authentic, \
original, or includes high-counterfeit-risk brands/categories, require explicit \
authentication/guarantee signals in the listing.

**Terminology / jargon to interpret correctly:**

- "Pre-owned" and "used" are broad; look for stated condition grade and flaws.
- "New old stock" can mean older inventory preserved in new condition; do not confuse \
with "dead stock" as in obsolete unsellable inventory unless context supports it.

**Common scoring pitfalls:**

- Scoring modern mass-produced items highly for vintage-era queries that imply provenance.
- Ignoring condition qualifiers ("minor scuffs", "missing box") that are central to resale value.
""",
        ),
    },
)
