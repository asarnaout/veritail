"""Furniture vertical context for LLM judge guidance."""

from __future__ import annotations

from veritail.types import VerticalContext, VerticalOverlay

FURNITURE = VerticalContext(
    core="""\
## Vertical: Furniture

You are evaluating search results for a furniture and home-furnishings ecommerce site.

Assume the shopper is trying to **buy a physical product** unless the query clearly
asks for something else (e.g., "how to", "ideas", "inspiration", "DIY", "repair",
"reviews"). When the query is ambiguous, prefer the most common retail intent.

### Scoring approach

Score relevance by prioritizing **hard constraints first**. A result that violates
a hard constraint is not a close match, even if it is aesthetically similar.

### Hard constraints (must match)

- **Correct product class and function**: Match the requested furniture class
  (e.g., sofa vs bed frame vs rug vs vanity). Adjacent categories that look similar
  are not substitutes unless the query is clearly exploratory.
- **Fitment and dimensions dominate when present**: If the query includes
  measurements, size labels (e.g., Queen), TV size (e.g., "for 65-inch TV"), room
  constraints (e.g., "narrow hallway"), or quantity of seats, treat fit as a hard gate.
- **Indoor vs outdoor**: Outdoor/patio intent requires outdoor-rated materials and
  construction; indoor intent should not be satisfied by utilitarian patio furniture.
- **Material / finish / grade when specified**: If the query specifies a material
  (solid wood vs engineered wood), upholstery (top-grain leather vs bonded/faux),
  hardware finish (matte black vs brushed nickel), or grade (commercial/contract),
  treat it as a hard requirement.
- **Quantity / bundle intent**: "Set of 2", "pair", "5-piece set", "sectional 3-piece"
  implies a specific selling unit. Do not treat a single piece as a match for a set.
- **Assembly and delivery constraints when specified**: "No assembly", "fully
  assembled", "white glove delivery", "RTA/flat-pack" are purchase-decision constraints.
- **Compliance / safety / certification claims when specified**: If the query names
  a safety standard, emissions label, or certification, only match results that
  explicitly satisfy it (do not infer compliance).

### Soft constraints (helpful but secondary)

- Style family (modern, farmhouse, mid-century), color/finish family when not
  explicitly specified, reversible/convertible features when not requested,
  and price-tier alignment are useful signals but should not override hard fitment.

### Common disqualifiers

- Obvious category mismatch (e.g., returning decor, tools, or replacement parts).
- Wrong environment (indoor-only item for outdoor query, or the reverse).
- Wrong size label or explicit measurement mismatch.
""",
    overlays={
        "sofas_sectionals": VerticalOverlay(
            description=(
                "Living-room upholstered seating: sofas/couches, loveseats, sectionals, "
                "modular sofas, chaises (stationary). Includes LAF/RAF and left/right chaise "
                "orientation, upholstery material terms, and abrasion/durability specs. "
                "Excludes recliners/lift chairs and sleeper mechanisms."
            ),
            content="""\
### Sofas & Sectionals — Scoring Guidance

This query is about **stationary upholstered seating** sold as sofas/couches, loveseats,
sectionals, modular sofas, and attached chaises.

#### Critical distinctions to enforce

- **Sectional orientation is easy to misread**:
  - LAF/RAF = *Left/Right Arm Facing* is determined when you are **standing in front of the sofa
    facing it**, not sitting on it. If the query specifies LAF/RAF or "left-facing/right-facing",
    treat it as a hard constraint and do not invert it.
  - "Left chaise" / "right chaise" is also typically described from the *facing* perspective.
  - "Reversible chaise" means it can be configured left or right; accept either side only if the
    listing explicitly says reversible.
- **Chaise vs ottoman vs corner wedge are different**:
  - An *attached chaise* is part of the sofa footprint and changes the sectional configuration.
  - An *ottoman* is movable and is not the same as an attached chaise unless the query explicitly
    allows an ottoman substitute.
  - A *corner wedge* (or "corner") is not interchangeable with an end chaise.
- **Modular vs fixed sectional**:
  - "Modular" implies reconfigurable pieces (often armless units + corner units) and sometimes
    multiple acceptable layouts. If the query specifies modular, require explicit modularity.
- **Stationary vs reclining**:
  - If the query says "reclining", a stationary sofa is not a match (route to motion seating logic).
- **Leather terminology is a frequent source of returns**:
  - If the query requires **full-grain** or **top-grain** leather, do not treat bonded leather,
    PU, PVC/vinyl, or "leather match" as a match unless the query explicitly allows those.
  - "Genuine leather" is ambiguous in marketing; only treat it as satisfying a leather constraint
    when the listing clearly indicates real hide leather in relevant seating surfaces.
- **Abrasion ratings / "double rubs" vs "Martindale"**:
  - Upholstery durability may be listed as Wyzenbeek *double rubs* or Martindale cycles. These are
    different tests; treat the provided rating as the authoritative signal rather than trying to
    convert between them.
  - When the query asks for contract/commercial upholstery, treat 15,000+ Wyzenbeek double rubs or
    ~30,000+ Martindale as the typical minimum signals (enforce explicit numbers when specified).
- **Slipcover vs upholstered**:
  - "Slipcovered" implies a removable fitted cover; do not treat fixed upholstery as equivalent
    when the query is strict about washability.

#### Vocabulary and equivalences (do not penalize lexical variation)

- sofa = couch
- loveseat = 2-seat sofa
- sectional = sometimes modular, but only treat as modular when the listing explicitly says modular
- chaise sofa = sofa with attached chaise

#### Common disqualifiers

- Returning outdoor patio seating (resin wicker, aluminum frames) for an indoor sofa query.
- Confusing sofa tables / console tables with sofas ("sofa table" is a table).
""",
        ),
        "motion_seating": VerticalOverlay(
            description=(
                "Reclining and motion seating: recliners, power recliners, lift chairs, "
                "reclining sofas/sectionals, home-theater seating. Includes wall-hugger/zero-wall "
                "terminology, swivel/rocker/glider distinctions, and power-feature requirements."
            ),
            content="""\
### Recliners & Motion Seating — Scoring Guidance

This query is about **motion seating**: recliners, power recliners, lift chairs,
reclining sofas/sectionals, or home-theater seating.

#### Critical distinctions to enforce

- **Power vs manual is a hard constraint when stated**:
  - "Power recliner" must have powered motion (and typically a power source + control).
  - "Manual" / "push-back" should not return powered-only items unless the query allows.
- **Lift chairs are not regular recliners**:
  - "Lift chair" implies a powered lift-assist mechanism to help the user stand. A standard
    recliner without lift is a mismatch.
- **Wall-hugger / zero-wall / zero-clearance**:
  - These terms signal a recliner designed to operate with minimal rear clearance. If the
    query specifies it, require an explicit match (do not infer from photos).
- **Swivel / glider / rocker are different motion types**:
  - "Swivel recliner" must swivel; "rocker recliner" must rock; "glider" glides.
  - Do not substitute between them unless the query is exploratory.
- **Home-theater seating is its own class**:
  - Queries mentioning "theater seating", "row", "console", "cupholders", or "power headrest"
    imply cinema-style seating. A standard living-room recliner is usually not a match.
- **Control features may be hard constraints when specified**:
  - Power headrest, power lumbar, USB, battery pack, and "each seat reclines" can be decisive
    for multi-seat products.

#### Common disqualifiers

- Returning a stationary sofa/chair for an explicit recliner query.
- Returning an ottoman for a recliner query (ottomans do not provide reclining motion).
""",
        ),
        "sleepers_daybeds_futons": VerticalOverlay(
            description=(
                "Convertible sleep furniture: sleeper sofas/sofa beds, futons, daybeds, trundles, "
                "Murphy beds, and replacement sofa-bed mattresses. Includes sleeper-mattress sizing "
                "quirks (e.g., many 'queen' sofa-bed mattresses are shorter than standard Queen)."
            ),
            content="""\
### Sleepers, Daybeds & Futons — Scoring Guidance

This query is about furniture that **converts into a bed** (or uses a bed mattress as the seat),
including sleeper sofas/sofa beds, futons, daybeds, trundles, Murphy beds, and sofa-bed
replacement mattresses.

#### Critical distinctions to enforce

- **Product type matters**:
  - *Sleeper sofa / sofa bed*: a couch that opens to a bed via a pull-out or fold-out mechanism.
  - *Futon*: a fold-flat frame designed to work with a **bendable futon mattress**.
  - *Daybed*: usually a twin-size bed used as seating, often with back/arms; may include a trundle.
  - *Trundle*: a secondary bed stored under the main bed/daybed (may be pop-up).
  - *Murphy bed*: wall bed that folds vertically into a cabinet.
  Do not substitute across these types when the query is explicit.
- **Sleeper mattress sizes are often NOT standard bed sizes**:
  - Many "queen" sofa-bed mattresses are closer to **60" × 72"** rather than a standard queen
    **60" × 80"**. If the query mentions sheets, tall sleepers, or replacement mattress dimensions,
    require the exact stated size.
  - Sofa-bed replacement mattresses are typically thin (often ~4–5") to fit folding mechanisms;
    do not return a standard 10–14" bed mattress for a replacement sofa-bed mattress query.
- **Mechanism and clearance**:
  - Pull-out sleepers require forward clearance to open. If the query signals a tight space
    or "wall-hugging sleeper", require explicit space-saving mechanism language.
- **Two-twin-to-king claims require explicit support**:
  - Some daybed + pop-up trundle systems can form a larger combined sleeping surface, but only
    when the listing explicitly supports the configuration (equal height, designed to connect).

#### Common disqualifiers

- Returning a regular sofa for an explicit sleeper query.
- Returning a standard bed mattress for a sofa-bed replacement mattress query.
- Confusing "futon cover" with a futon mattress or futon frame.
""",
        ),
        "beds_frames_headboards": VerticalOverlay(
            description=(
                "Bed furniture (not mattresses): bed frames, platform beds, headboards/footboards, "
                "storage beds, canopy beds, rails, slats, and foundations/box springs. Includes bed-size "
                "dimension norms, and platform/no-box-spring vs box-spring-required distinctions."
            ),
            content="""\
### Bed Frames, Headboards & Foundations — Scoring Guidance

This query is about **bed structures** (frames, headboards, platforms, storage beds, rails, slats,
foundations/box springs), not the mattress itself.

#### Critical distinctions to enforce

- **Bed size is a hard gate** (common U.S. mattress sizes):
  - Twin: 38"×75"
  - Twin XL: 38"×80"
  - Full: 54"×75"
  - Queen: 60"×80"
  - King: 76"×80"
  - California King: 72"×84"
  Sizes are not interchangeable; require an exact size match when specified.
- **Headboard-only vs complete bed vs bed frame**:
  - Many listings sell only a headboard (or headboard + footboard) and require separate side rails
    or a separate metal frame. If the query is "bed frame" or "complete bed", headboard-only is
    incomplete.
- **Platform vs panel/box-spring-required**:
  - A *platform bed* supports a mattress with slats or a solid deck and is often marketed as
    "no box spring required".
  - Many traditional frames/panel beds assume a box spring or foundation for proper height/support.
  If the query specifies "no box spring", require explicit platform/no-box-spring language.
- **Support-system constraints (when the query signals support/warranty concerns)**:
  - Many mattress warranties specify support requirements such as **center support** for Queen/King/
    Cal King and limit allowed slat gaps (often around ~3"). If the query mentions "for memory foam",
    "for warranty", "slat spacing", or "center support", require explicit support details rather than
    guessing from photos.
- **Storage beds**:
  - Drawer storage beds vs lift-up hydraulic storage are distinct. If the query specifies drawers
    or "lift-up", enforce the mechanism.
- **Adjustable base compatibility**:
  - "Adjustable base compatible" (or "zero clearance") should only match frames explicitly designed
    for adjustable foundations.

#### Common disqualifiers

- Returning mattresses for bed-frame queries.
- Returning headboards for a "bed frame" query (unless the query explicitly asks for headboard).
""",
        ),
        "mattresses_toppers_bases": VerticalOverlay(
            description=(
                "Mattresses and sleep surfaces: mattresses by size/firmness/type, mattress toppers, "
                "mattress-in-a-box, and adjustable bases. Includes standard U.S. mattress size dimensions, "
                "U.S. flammability compliance language (16 CFR 1632/1633), and foam certification terms "
                "(CertiPUR-US, GREENGUARD Gold)."
            ),
            content="""\
### Mattresses, Toppers & Adjustable Bases — Scoring Guidance

This query is about **sleep surfaces** (mattresses, toppers, adjustable bases), not bed frames.

#### Critical distinctions to enforce

- **Size is a hard gate** (common U.S. mattress sizes):
  - Twin: 38"×75"
  - Twin XL: 38"×80"
  - Full: 54"×75"
  - Queen: 60"×80"
  - King: 76"×80"
  - California King: 72"×84"
  If the query names a size, results must match exactly.
- **Mattress vs topper vs protector**:
  - A topper (2–4" add-on) is not a mattress. A protector/cover is neither.
- **Construction type is not substitutable when specified**:
  - Memory foam, innerspring, hybrid, latex, and airbeds have different feel/performance.
  - If the query specifies a type (e.g., "hybrid"), do not return a different construction unless
    the query explicitly allows alternatives.
- **Firmness claims are relative and brand-specific**:
  - "Firm", "medium", "plush" have no universal scale. However, when the query is explicit
    ("extra firm", "plush"), avoid clearly opposite listings.
- **Adjustable-base compatibility**:
  - If the query specifies adjustable-base compatibility, require a mattress explicitly described
    as compatible (many foam/latex/hybrids are; some traditional innersprings may not be).
- **Safety/compliance terms (U.S.)**:
  - 16 CFR 1632: smoldering (cigarette ignition) resistance testing for mattresses/mattress pads.
  - 16 CFR 1633: open-flame flammability performance for mattress sets.
  If the query mentions 1632/1633, require explicit matching compliance language.
- **What CertiPUR-US means (when the query asks for it)**:
  - CertiPUR-US applies to flexible polyurethane foam and is about content/emissions/durability
    criteria verified by testing; it does not certify an entire mattress brand.

#### Common disqualifiers

- Returning a bed frame/foundation for a "mattress" query unless explicitly requested.
- Returning a mattress for a "toppers" query.
""",
        ),
        "casegoods_storage": VerticalOverlay(
            description=(
                "Home storage and case goods: dressers, chests of drawers, armoires/wardrobes, "
                "nightstands, sideboards/credenzas, cabinets, entry storage. Includes tip-over safety "
                "and compliance terms (STURDY / 16 CFR 1261 / ASTM F2057), plus TSCA Title VI / CARB Phase 2 "
                "composite-wood emissions labeling."
            ),
            content="""\
### Case Goods & Storage — Scoring Guidance

This query is about **storage furniture**: dressers, chests, armoires/wardrobes, nightstands,
sideboards/credenzas, cabinets, and similar case goods.

#### Critical distinctions to enforce

- **Dresser/chest configuration matters when specified**:
  - "Double dresser" / "wide dresser" implies a low, wide form factor.
  - "Chest" / "tall dresser" implies a taller, narrower form factor.
  Retailers sometimes mix terms, so rely on dimensions + drawer layout if the query is about fit.
- **Wardrobe/armoire vs dresser**:
  - Wardrobes/armoires typically include doors and a hanging rod (sometimes shelves/drawers). Do not
    return a dresser for a wardrobe query unless the query explicitly calls for drawers-only storage.
- **Tip-over safety / anti-tip compliance (U.S.)**:
  - The STURDY rule (16 CFR part 1261) is a consumer product safety standard intended to reduce
    tip-over-related death/injury to children up to 72 months of age.
  - CPSC guidance notes that some **fabric dressers with drawers** can qualify as clothing storage units
    under the rule when they meet defined criteria (e.g., free-standing, >=27" tall, >=30 lb mass, and
    >=3.2 ft³ enclosed storage volume).
  - If the query mentions "anti-tip", "tip-over", "STURDY", "ASTM F2057", or "16 CFR 1261", treat it
    as a hard constraint: require explicit compliance language and/or an included anti-tip kit.
  - Do not assume that a tall dresser is compliant without an explicit statement.
- **Composite-wood emissions labels (when specified)**:
  - TSCA Title VI / CARB Phase 2 are formaldehyde-emissions regimes for composite wood (hardwood
    plywood, MDF, particleboard) and finished goods containing those panels. If the query asks for
    those labels, require explicit claims.

#### Common disqualifiers

- Confusing a "sofa table" (a table) with a storage cabinet.
- Returning wall shelves for a freestanding dresser/cabinet query unless the query allows wall-mount.
""",
        ),
        "dining_tables_sets": VerticalOverlay(
            description=(
                "Dining furniture: dining tables, kitchen tables, counter-height or bar-height dining sets, "
                "extendable tables, and table leaves (drop-leaf, butterfly/self-storing, removable). "
                "Includes seating-capacity sizing heuristics and the '24 inches per person' rule of thumb."
            ),
            content="""\
### Dining Tables & Dining Sets — Scoring Guidance

This query is about dining/kitchen tables and dining bundles.

#### Critical distinctions to enforce

- **Table height class is a hard constraint when specified**:
  - Standard dining tables are typically ~28–30" high.
  - Counter-height dining tables are typically ~34–36" high.
  - Bar-height tables are typically ~40–42" high.
  Do not substitute across height classes when the query is explicit.
- **Set completeness**:
  - "5-piece dining set" usually means a table + 4 chairs; "7-piece" often means table + 6 chairs.
  If the query expects a set, a table-only product is incomplete unless the listing is clearly a set.
- **Seating capacity should be backed by dimensions**:
  - Retail guidance often uses ~24" of table edge per seated person as a sizing rule of thumb.
  If the query says "seats 8", require explicit "seats 8" language OR dimensions consistent with it,
  instead of trusting photos.
- **Leaf / extension mechanisms are distinct**:
  - Drop-leaf, butterfly/self-storing leaf, and removable leaves are different ownership experiences.
  If the query specifies "butterfly leaf" or "self-storing", enforce it.

#### Vocabulary

- kitchen table is often synonymous with dining table in ecommerce; use height + size context.
- counter-height dining set implies stools or tall chairs, not standard dining chairs.

#### Common disqualifiers

- Returning bar stools for a dining table query (unless the query is for a set including stools).
- Returning a coffee table or console table for a dining table query.
""",
        ),
        "chairs_stools_benches": VerticalOverlay(
            description=(
                "Non-office seating: dining chairs, accent chairs, benches, bar stools, counter stools, "
                "and set-of-2 seating. Includes the common 10–12 inch seat-to-counter clearance rule and "
                "typical seat-height ranges by counter/bar height."
            ),
            content="""\
### Chairs, Stools & Benches — Scoring Guidance

This query is about seating that is **not primarily an office chair**: dining chairs,
accent chairs, benches, bar stools, and counter stools.

#### Critical distinctions to enforce

- **Counter stool vs bar stool is a frequent fitment trap**:
  - Counter surfaces are commonly ~34–36" high; typical counter stool seat height ~24–27".
  - Bar surfaces are commonly ~40–42" high; typical bar stool seat height ~28–32".
  If the query specifies "counter" or "bar" height, enforce the correct height class.
- **The clearance rule is the ergonomic constraint**:
  - Many seating guides recommend roughly **10–12"** of vertical space between the top of the seat
    and the underside/top of the counter/table for comfortable leg clearance.
  If the query gives both counter height and desired clearance, enforce it.
- **Seat height vs overall height**:
  - Listings often show overall height; for fitment, seat height is the hard spec.
  If the query includes seat-height numbers, enforce them.
- **Dining chair vs accent chair**:
  - Dining chairs are proportioned for table seating and are frequently sold in sets.
  - Accent chairs are lounge seating; do not substitute unless the query is exploratory.
- **Bench intent**:
  - Dining bench vs entry bench vs storage bench are different. Storage benches must include storage
    explicitly if required.
- **Quantity is a hard constraint when stated**:
  - "Set of 2", "pair", "set of 4" should match the selling unit.

#### Common disqualifiers

- Returning an office chair for a dining chair query.
- Returning a bar stool for a counter stool query (and vice versa).
""",
        ),
        "home_office": VerticalOverlay(
            description=(
                "Home office furniture: office chairs/task chairs, ergonomic chairs, gaming chairs, "
                "computer desks and standing desks. Includes BIFMA standard references (X5.1 chairs, X5.5 desks), "
                "standing-desk height-range expectations, and caster/floor matching (hard vs soft wheels)."
            ),
            content="""\
### Home Office — Scoring Guidance

This query is about **office chairs** and **desks**, including standing desks and gaming setups.

#### Critical distinctions to enforce

- **Office-chair standards often matter when named**:
  - ANSI/BIFMA X5.1 is a common standard reference for general-purpose office seating. If the query
    specifies BIFMA/X5.1, require an explicit compliance/certification claim.
- **Desk/table standards may appear in commercialish home-office queries**:
  - ANSI/BIFMA X5.5 is commonly referenced for desk/table products. Treat explicit X5.5 mentions
    as a hard constraint.
- **Caster / floor compatibility**:
  - Hard wheels are often marketed for carpet; soft/PU wheels are often marketed to protect hard floors.
  If the query specifies "hard floor casters" or "for carpet", require an explicit match and do not guess.
- **Ergonomic adjustability is not generic**:
  - If the query requires specific adjustments (lumbar support, headrest, 4D arms, seat depth),
    treat missing adjustments as a major relevance penalty.
- **Standing desks: height range is the fitment spec**:
  - Many standing desks market a height adjustment range roughly in the ~24"–50" neighborhood.
  If the query specifies a minimum/maximum height (or "BIFMA height range"), require explicit specs.
- **Desk size and monitor count**:
  - If the query specifies desktop size (e.g., 60"×30"), corner/L-shape, or multi-monitor setups,
    treat size/shape as a hard requirement.

#### Common disqualifiers

- Returning dining chairs for an office-chair query.
- Returning desk accessories (cable trays, monitor arms) for a desk query unless explicitly requested.
""",
        ),
        "outdoor_patio": VerticalOverlay(
            description=(
                "Outdoor/patio furniture: conversation sets, patio dining sets, loungers, Adirondack chairs, "
                "outdoor cushions and fabrics. Includes outdoor-material durability signals (teak, powder-coated aluminum, HDPE), "
                "solution-dyed acrylic fabric concepts, and quick-dry/reticulated foam."
            ),
            content="""\
### Outdoor & Patio Furniture — Scoring Guidance

This query is about furniture intended to live outdoors (patio, deck, balcony, poolside).

#### Critical distinctions to enforce

- **Outdoor-rated frame materials** (when the query is explicit about durability):
  - Teak (weather- and moisture-resistant hardwood), powder-coated aluminum, stainless steel,
    HDPE resin lumber, and outdoor-rated resin wicker (often PE over an aluminum frame) are common
    outdoor materials.
  - Plain steel frames without corrosion protection are higher risk for rust; "powder-coated",
    "galvanized", and "rust-resistant" claims matter when specified.
- **Outdoor fabrics are not interchangeable**:
  - Solution-dyed acrylic is a specific outdoor performance fabric class where color pigments are
    integrated into the fiber before spinning, improving fade resistance.
  - If the query names a fabric brand/spec (Sunbrella, solution-dyed acrylic), treat it as a hard constraint.
- **Cushion fill matters outdoors**:
  - Outdoor quick-dry cushions may use reticulated (open-cell) foam designed to drain and dry faster.
  If the query specifies "quick dry" / "reticulated foam" / "drains fast", require explicit mention.
- **Indoor/outdoor vs outdoor-only**:
  - "Indoor/outdoor" rugs and cushions are meant to tolerate outdoor conditions, but if the query
    says "marine/salt air" or "poolside", prefer corrosion- and UV-specific language.
- **Set vs piece intent**:
  - Outdoor conversation sets, patio dining sets, and sectional sets have different implied bundles.
  Match the bundle completeness when specified.

#### Common disqualifiers

- Returning indoor upholstered furniture for a patio query.
- Returning decorative outdoor pillows for an "outdoor sectional set" query.
""",
        ),
        "bathroom_vanities": VerticalOverlay(
            description=(
                "Bathroom sink vanities: vanity cabinets, vanity tops, integrated sinks, floating vs freestanding vanities, "
                "single vs double sink. Includes common vanity width buckets (24/30/36/42/48/60+), selling unit ('with top' vs 'cabinet only'), "
                "and faucet-hole spacing jargon (centerset 4-inch vs widespread 8-inch+ vs single hole). Excludes makeup/dressing vanities."
            ),
            content="""\
### Bathroom Vanities — Scoring Guidance

This query is about **bathroom sink vanities** (not makeup/dressing tables).

#### Critical distinctions to enforce

- **Vanity cabinet vs vanity top vs full vanity**:
  - Some listings are *cabinet only* (no top/sink included).
  - Some are *vanity tops* (countertop with/without sink cutout) meant to be paired with a base.
  - Some are a complete vanity (base + top, sometimes sink/faucet).
  If the query explicitly says "with top" or "cabinet only", enforce it.
- **Width is the primary fitment spec**:
  - Buyers shop vanities in discrete width buckets (commonly 24", 30", 36", 42", 48", 60"+).
  If the query specifies width, enforce it tightly.
- **Single vs double sink**:
  - A 60" vanity could be single or double; do not assume. If the query says double, require a
    double-sink configuration.
- **Floating (wall-mounted) vs freestanding**:
  - A floating vanity is wall-mounted and changes installation/plumbing clearance. If the query
    specifies floating/wall-mounted, freestanding is a mismatch.
- **Faucet-hole spacing terms**:
  - "Centerset" commonly means a 3-hole configuration on **4" on-center** spacing.
  - "Widespread" typically starts at **8"** and can vary wider (because the spout/handles are separate).
  - "Single-hole" requires one hole (often with an optional deck plate to cover extra holes).
  If the query specifies centerset/widespread/single-hole, require that configuration.
- **Sink style may be a hard constraint when specified**:
  - Vessel sinks sit on top of the counter and often require a vessel-height faucet.
  - Undermount/integrated sinks are different installation styles. Enforce when specified.

#### Common disqualifiers

- Confusing a bathroom vanity with a bedroom makeup vanity.
- Returning a vanity mirror or faucet for a vanity-cabinet query unless explicitly requested.
""",
        ),
        "makeup_vanities_dressing_tables": VerticalOverlay(
            description=(
                "Makeup vanity tables and dressing tables (bedroom/closet): vanities with mirrors, "
                "Hollywood lighted vanities, vanity sets with stool. Includes mirror/lighting expectations. "
                "Excludes bathroom sink vanities."
            ),
            content="""\
### Makeup Vanities & Dressing Tables — Scoring Guidance

This query is about **bedroom/closet grooming furniture**: vanity tables, dressing tables,
and makeup stations (often with mirror and/or lighting).

#### Critical distinctions to enforce

- **Bathroom vanity vs makeup vanity**:
  - Bathroom vanities have a sink/top and plumbing intent.
  - Makeup/dressing vanities are desk-like and may include mirrors, drawers, and seating.
  If the query mentions sinks, faucet holes, plumbing, or "bathroom", it is not this overlay.
- **Vanity vs dressing table nuance**:
  - Many buyers expect a "vanity table" to be makeup-oriented and often paired with a mirror.
  A "dressing table" may be similar but is often referenced as a general grooming surface.
  If the query is strict about a mirror, require the mirror included.
- **Mirror and lighting as hard constraints when specified**:
  - "Vanity with mirror" implies the mirror is included (not just a table).
  - "Hollywood vanity" strongly implies a large mirror with integrated bulbs/LED lighting.
- **Vanity set completeness**:
  - Many vanity "sets" include a matching stool/bench. If the query expects a set, table-only is
    incomplete.

#### Common disqualifiers

- Returning a bathroom sink vanity for a makeup vanity query.
- Returning a wall mirror alone for a "vanity set" query.
""",
        ),
        "media_consoles_tv_stands": VerticalOverlay(
            description=(
                "Media furniture: TV stands, media consoles, entertainment centers, fireplace TV stands, "
                "floating media cabinets. Includes TV-size math pitfalls (TV inches are diagonal), stand-width heuristics, "
                "and content about choosing consoles wider than the TV."
            ),
            content="""\
### TV Stands & Media Consoles — Scoring Guidance

This query is about furniture designed to support a TV and media components.

#### Critical distinctions to enforce

- **TV size numbers are diagonal, not width**:
  - "65-inch TV" refers to diagonal. A typical 65" 16:9 TV is about ~56–57" wide.
  If the query is "for 65-inch TV", require a console explicitly rated for 65" or with width
  that plausibly accommodates the TV.
- **Stand width should exceed TV width**:
  - Many buying guides recommend a console at least a few inches wider than the TV for stability and
    visual balance. If the query is precise ("stand must be 70 inches wide"), enforce exact width.
- **Floating vs freestanding**:
  - Floating media consoles are wall-mounted and have different install requirements. If the query
    specifies floating/wall-mounted, require it.
- **Fireplace TV stands are a special subtype**:
  - If the query includes "fireplace", require a unit that includes an electric fireplace insert or
    dedicated fireplace opening sized for it.
- **Storage type matters**:
  - Open-shelf (ventilation for consoles) vs closed-door storage vs soundbar shelf are functional
    constraints when specified.

#### Common disqualifiers

- Returning wall-mount brackets or TV mounts for a "TV stand" query.
- Returning a narrow console table (decor piece) for a large-TV media console query.
""",
        ),
        "rugs": VerticalOverlay(
            description=(
                "Rugs and mats: area rugs, runners, doormats, washable rugs, indoor/outdoor rugs, rug pads. "
                "Includes standard rug sizing vocabulary (5x8, 8x10, 9x12), pile-height categories (low < 1/4 inch), "
                "and indoor/outdoor material expectations."
            ),
            content="""\
### Rugs & Rug Pads — Scoring Guidance

This query is about area rugs, runners, doormats, and rug pads.

#### Critical distinctions to enforce

- **Exact size is often the hard gate**:
  - If the query specifies 5'×8', 8'×10', 9'×12', runner length, or a specific shape (round), require
    an exact (or extremely close) match.
- **Pile height affects usability**:
  - Low pile is commonly defined as under ~0.25" pile and is preferred for high-traffic areas and
    under doors/dining chairs.
  - High pile/shag rugs are plush but harder to vacuum and typically worse for heavy traffic.
  If the query specifies low/high pile, enforce it.
- **Indoor vs indoor/outdoor**:
  - "Indoor/outdoor" rugs are typically polypropylene or similar synthetics designed to tolerate
    moisture and UV; if the query says outdoor/patio, require indoor/outdoor or outdoor-rated.
- **Rug pad intent**:
  - If the query is for a rug pad for hardwood, prioritize non-slip pads intended for hard surfaces.
  Avoid adhesive pads unless the query asks for adhesive.

#### Common disqualifiers

- Returning carpet tiles or wall-to-wall carpet services for an area rug query.
- Returning a bath mat for a living-room area rug query (and vice versa) unless the query is ambiguous.
""",
        ),
        "nursery_kids": VerticalOverlay(
            description=(
                "Kids and nursery furniture: cribs (full-size and non-full-size/mini), toddler beds, bunk beds, loft beds, "
                "changing tables. Includes U.S. safety standard concepts (CPSC 16 CFR 1219/1220 for cribs; "
                "16 CFR 1513 for bunk beds), slat-spacing constraints, and drop-side crib exclusion."
            ),
            content="""\
### Kids & Nursery Furniture — Scoring Guidance

This query is about **children's furniture** where safety standards and product class
definitions matter.

#### Critical distinctions to enforce

- **Crib classes and standards (U.S.)**:
  - Full-size baby cribs are regulated under 16 CFR part 1219 (incorporating ASTM F1169).
  - Non-full-size/mini cribs are regulated under 16 CFR part 1220 (incorporating ASTM F406).
  If the query asks for a specific crib class, do not substitute.
- **Drop-side cribs are not acceptable**:
  - Do not treat "drop-side crib" listings as relevant for generic "crib" queries.
- **Slat spacing / entrapment safety (when the query signals safety)**:
  - If the query mentions safety standards, enforce explicit compliance claims. Crib slat spacing
    and entrapment are not "nice to have"; they are safety-critical.
- **Bunk/loft bed safety (U.S.)**:
  - Bunk bed guardrail/entrapment requirements exist in 16 CFR part 1513. If the query is for bunk
    beds, do not accept products that obviously lack required guardrails unless the listing clearly
    indicates compliance for the intended user age group.
- **Conversion features are not universal**:
  - "Convertible crib" (to toddler bed/daybed/full bed) requires the appropriate conversion design
    and may require a conversion kit; do not assume included kits unless stated.

#### Common disqualifiers

- Returning a crib mattress for a crib query unless explicitly requested.
- Returning a toy/play tent for a bunk bed or crib query.
""",
        ),
        "commercial_contract": VerticalOverlay(
            description=(
                "Commercial/contract-grade furniture for workplaces and public spaces: stacking/banquet chairs, training-room tables, "
                "lobby seating, restaurant seating, waiting-room furniture. Includes BIFMA references, GREENGUARD Gold language, "
                "TB117-2013 flammability labeling (smolder resistance), and legacy TB133/CAL 133 procurement references."
            ),
            content="""\
### Commercial & Contract Furniture — Scoring Guidance

This query is about furniture intended for **commercial or institutional use**
(offices, hotels, restaurants, schools, healthcare, conference facilities).

#### Critical distinctions to enforce

- **Contract-grade is not just aesthetics**:
  - If the query specifies "commercial", "contract", a weight rating, or stacking count, require
    explicit contract durability/testing claims (do not infer from photos).
- **BIFMA standards (common procurement shorthand)**:
  - ANSI/BIFMA X5.1 is a common reference for general-purpose office chairs.
  - ANSI/BIFMA X5.5 is commonly referenced for desk/table products.
  If the query names any BIFMA standard, require explicit compliance/certification language.
- **Stacking / nesting / ganging**:
  - Stacking chairs must specify stack count; nesting chairs fold/store differently; ganging
    connectors/linking features are often required for rows of event seating. Enforce when specified.
- **Fire and emissions compliance language (when specified)**:
  - TB117-2013 is a smolder-resistance flammability standard for upholstered furniture materials;
    procurement may request it explicitly. Treat explicit mention as a hard requirement.
  - GREENGUARD / GREENGUARD Gold: low-VOC emissions certification; treat explicit mention as hard.
  - CAL 133 / TB133 may appear in legacy public-occupancy procurement; treat it as a hard requirement
    when explicitly specified, but do not assume it for general queries.
- **Cleaning and upholstery**:
  - Commercial seating often requires cleanable vinyl or healthcare-grade upholstery. If the query
    specifies healthcare/antimicrobial/wipeable, require explicit suitability language.

#### Common disqualifiers

- Returning residential-only furniture for an explicit contract-grade query.
- Returning decorative dining chairs for stacking banquet-chair queries.
""",
        ),
    },
)
