"""Office supplies vertical context for LLM judge guidance."""

from __future__ import annotations

from veritail.types import VerticalContext, VerticalOverlay

OFFICE_SUPPLIES = VerticalContext(
    core="""\
## Vertical: Office Supplies

You are evaluating search results for an office supplies ecommerce site. \
Think like a composite buyer spanning the corporate procurement specialist \
matching items against a contracted supplier catalog, the small-business \
owner restocking a workspace on a budget, and the home-office worker \
searching for an exact replacement item.

In office supplies, compatibility is the silent deal-breaker. Device and \
system compatibility outweighs brand preference, price, or cosmetic similarity.

### Scoring considerations

- **Device and machine compatibility as the primary hard gate**: When a query \
specifies or strongly implies a target device (e.g., a specific printer, \
label maker, laminator, shredder, or dispenser), every consumable result must be \
confirmed compatible with that exact device or receive a major relevance \
penalty. Treat device mismatch with the same severity that automotive \
treats Year/Make/Model fitment failure — an immediate disqualifier.
- **Corporate procurement vs. individual buyer signals**: Office supply \
buyers span a wide spectrum from individual consumers to enterprise \
procurement departments. Corporate signals include bulk quantity references \
("case of," "10 reams," "144-count"), specific catalog/SKU numbers, and \
terse category-plus-spec queries. Individual signals include plain-language \
descriptions and single-unit intent. Matching the quantity tier and \
purchasing context to the buyer signal is a primary relevance driver.
- **Quantity and packaging tiers**: Office supplies are sold across sharply \
different packaging tiers (each, box, case, pallet). When the query signals \
quantity intent — "box of," "case of," "single," "bulk," or a specific count \
— results at the wrong packaging tier drastically reduce relevance.
- **Environmental certifications**: Office supply buyers increasingly require \
verified environmental credentials. FSC (Forest Stewardship Council) and SFI \
certify paper. Recycled content percentage (e.g., 30% or 100% PCW) is a \
hard specification. EPEAT certifies electronics lifecycle impact, and \
ENERGY STAR certifies energy efficiency. When a query specifies an eco-label, \
uncertified alternatives are strict relevance penalties.
- **Safety and compliance**: Ergonomic equipment (OSHA), First-aid kits \
(ANSI Z308.1), and chemical cleaners (SDS sheets) carry regulatory weight. \
When a query references a safety standard, non-compliant alternatives are \
relevance penalties regardless of functional similarity.
- **Brand as a System**: In office supplies, a brand name often implies a \
proprietary system rather than a casual preference. Treat brand-plus-model \
queries as hard constraints.""",
    overlays={
        "ink_and_toner": VerticalOverlay(
            description=(
                "Printer consumables: OEM and compatible ink cartridges, laser toner, "
                "drum units, fusers, and maintenance kits."
            ),
            content="""\
### Ink and Toner — Scoring Guidance

This query involves printer consumables, focusing heavily on brand tiers and page yields.

**Critical distinctions to enforce:**

- **The Three-Tier Market (OEM vs. Compatible vs. Remanufactured)**:
  * *OEM (Original Equipment Manufacturer)* cartridges carry manufacturer warranty and exact fitment.
  * *Compatible* cartridges are newly built by third parties at a lower cost.
  * *Remanufactured* cartridges are recycled OEM shells refilled and tested.
  If a query specifies "genuine," "OEM," or pairs the manufacturer name with the cartridge number (e.g., "HP 58A"), compatible and remanufactured items are strict relevance penalties. If the query asks for "compatible" or "generic," expensive OEM cartridges are poor matches.
- **Standard vs. High Yield**: Cartridges ending in "X" or "XL" designate high yield. A buyer searching for a high-yield cartridge should not receive a standard-yield equivalent as a perfect match.
- **ISO Page Yields (Do not penalize based on assumed real-world yield)**: Page yields are standardized by ISO/IEC 19752 (monochrome laser), ISO/IEC 19798 (color laser), and ISO/IEC 24711 (inkjet). These tests are strictly based on a 5% page coverage standard (equivalent to a sparse business letter header). Do not penalize a product's relevance if user reviews complain about "low page yields," as real-world use frequently exceeds 5% coverage causing faster depletion. Rely solely on the stated ISO standard yield for specification matching.
""",
        ),
        "paper_and_media": VerticalOverlay(
            description=(
                "Printable media: Copy paper, cardstock, photo paper, "
                "resume paper, and large format rolls."
            ),
            content="""\
### Paper and Printable Media — Scoring Guidance

This query involves office paper and specialized printable media.

**Critical distinctions to enforce:**

- **Paper Weight (LBS vs. GSM Trap)**: U.S. basis weights (lbs) differ completely by category (Bond, Text, Cover, Index). A 65 lb. Cover stock is substantially thicker and heavier than an 80 lb. Text stock.
  * Do **not** assume a higher poundage means a thicker paper unless the categories are identical.
  * Use GSM (Grams per Square Meter) as the universal metric. For reference: 20 lb Bond ≈ 75 GSM; 65 lb Cover ≈ 175 GSM. When weight is specified, treat mismatches as major penalties.
- **Brightness vs. Whiteness**:
  * *Brightness* measures the reflection of blue light (often on a 0-100 scale, with standard at 92 and premium at 96+), often enhanced by Optical Brightening Agents (OBAs).
  * *Whiteness* (CIE Whiteness) measures the reflection of all colors of light. Do not treat these specifications interchangeably if the query explicitly distinguishes them.
- **Laser vs. Inkjet Formulations**: Paper finishes dictate printer compatibility. Photo paper for inkjet uses absorption layers, whereas laser media uses heat-resistant coatings to survive the fuser. Returning inkjet-only media for a "laser printer paper" query is a functional failure.
- **Dimensions**: Letter (8.5x11"), Legal (8.5x14"), Tabloid (11x17"), and A4 (210x297mm) are hard constraints.
""",
        ),
        "writing_instruments": VerticalOverlay(
            description=(
                "Writing and art tools: Pens, mechanical pencils, replacement leads, "
                "markers, highlighters, and school art supplies."
            ),
            content="""\
### Writing Instruments and Art Supplies — Scoring Guidance

This query involves pens, mechanical pencils, replacement leads, refills, and art supplies.

**Critical distinctions to enforce:**

- **Documentary vs. General Use Inks**: If a query specifies "archival," "documentary," "fraud-resistant," or "legal" ink, it implies ISO 12757-2 (ballpoint) or ISO 14145-2 (rollerball) compliance. These inks resist erasure, ethanol, and bleach. Standard general-use inks (ISO 12757-1) are penalties for these specific queries.
- **Refill Ecosystems**: Pen refills follow strict form factors. A Parker-style G2 (ISO 12757-2) refill is not interchangeable with a Pilot G2 gel refill. Enforce strict compatibility with the target pen barrel.
- **Mechanical Pencil Leads**:
  * *Diameter*: 0.5mm, 0.7mm, and 0.9mm are fixed hardware constraints.
  * *Hardness*: The U.S. #2 pencil is equivalent to HB. 2B is softer/darker; 2H is harder/lighter. Hardness is a firm functional requirement when specified, as 2B and 2H serve opposite purposes (shading vs. technical drafting).
- **Toxicological Safety (Art Supplies)**: The ASTM D-4236 (LHAMA) label merely indicates the product has been evaluated for chronic hazards and labeled appropriately; it does **not** mean the product is non-toxic. If a query explicitly requires "non-toxic" (especially for children), look for the ACMI "AP Seal" or explicit non-toxic claims.
""",
        ),
        "office_furniture": VerticalOverlay(
            description=(
                "Office seating, desks, tables, standing desk converters, "
                "and ergonomic commercial workspace furniture."
            ),
            content="""\
### Office Furniture and Ergonomics — Scoring Guidance

This query involves commercial office furniture, defined by strict safety, weight, and dimensional standards.

**Critical distinctions to enforce:**

- **BIFMA / Commercial Grade Certification**: Commercial furniture relies on ANSI/BIFMA testing for safety and durability.
  * *ANSI/BIFMA X5.1*: Covers general-purpose office chairs for users up to 253 lbs.
  * *ANSI/BIFMA X5.11*: Covers large occupant (heavy duty/bariatric) office chairs for users up to 400 lbs. If a query asks for "heavy duty" or "400 lb capacity," X5.1 chairs are a critical safety penalty.
  * *ANSI/BIFMA X5.4*: Covers lounge and public seating.
  * *ANSI/BIFMA X5.5*: Covers desks, tables, and monitor arms.
- **Fire Safety Standards**:
  * *CAL 117*: The standard smolder/flammability test for upholstery foam and fabric.
  * *CAL 133*: A much stricter open-flame test for entire furniture pieces in public spaces. Though largely repealed, if a procurement query explicitly demands CAL 133, a CAL 117-only product is a hard failure.
- **Ergonomic Adjustability**: If a query specifies a feature (e.g., 4D armrests, seat slider, lumbar depth adjustment, sit-stand height ranges), treat it as a hard constraint.
""",
        ),
        "shredders_and_data_destruction": VerticalOverlay(
            description=(
                "Paper shredders, media destroyers, and data security devices."
            ),
            content="""\
### Shredders and Data Destruction — Scoring Guidance

This query involves document destruction equipment, which is heavily regulated by international data security standards.

**Critical distinctions to enforce:**

- **DIN 66399 P-Levels (Hard Constraints)**: Shredders are classified by particle size maximums.
  * *P-1 / P-2*: Basic strip-cut (low security).
  * *P-3 / P-4*: Cross-cut (moderate security). P-4 is the minimum standard for general confidential business documents.
  * *P-5*: Micro-cut (high security). Required for highly confidential, personal, or medical (HIPAA) data. Do not return P-3 or P-4 cross-cut shredders for "micro-cut" queries.
  * *P-6 / P-7*: Extremely high security. P-7 is the NSA/CSS standard for Top Secret classified government documents (particles ≤ 5 mm²). If a query requests "NSA approved" or "Top Secret," P-5 and P-6 are critical compliance failures.
- **Sheet Capacity vs. Duty Cycle**: "10-sheet capacity" refers to a single pass, whereas "duty cycle" or "continuous run time" dictates how long the motor can run before cool-down. Match the capacity needs requested by the buyer.
""",
        ),
        "mailing_and_packaging": VerticalOverlay(
            description=(
                "Envelopes, corrugated boxes, bubble mailers, packing tape, "
                "and shipping supplies."
            ),
            content="""\
### Mailing, Packaging, and Shipping — Scoring Guidance

This query involves supplies for mailing, postage, and package transit.

**Critical distinctions to enforce:**

- **Envelope Dimensions**:
  * *#10*: Standard business envelope (4 1/8 x 9 1/2 inches).
  * *A2*: RSVP/small note cards (4 3/8 x 5 3/4 inches).
  * *A7*: Standard greeting cards/invitations (5 1/4 x 7 1/4 inches).
  * Treat envelope sizing and window placement (e.g., USPS standard 5/8 inch from bottom, single vs. double window) as hard physical constraints.
- **Corrugated Box Fluting**: Flutes determine box strength and printing suitability.
  * *A-Flute*: Thickest, maximum cushioning.
  * *C-Flute*: Standard shipping box (most common, 80% of market).
  * *B-Flute*: Medium thickness, good for inner packaging.
  * *E-Flute / F-Flute*: Micro-thin, designed for high-quality retail printing and die-cutting, not for heavy shipping. Returning an E-flute box for a heavy-duty shipping query is a transit failure.
- **Tape Formulations**: Acrylic packing tape (long-term storage, UV resistant) vs. Hot Melt tape (high initial tack, good for shipping cartons). Treat specified tape types as functional requirements.
""",
        ),
        "binding_and_presentation": VerticalOverlay(
            description=(
                "Document binding machines, presentation covers, combs, "
                "coils, wire-O, and laminating pouches."
            ),
            content="""\
### Binding and Presentation Systems — Scoring Guidance

This query involves equipment and supplies for assembling professional documents.

**Critical distinctions to enforce:**

- **Binding Method Incompatibilities**: Binding machines use specific hole-punch geometries. Supplies are entirely non-interchangeable.
  * *Comb Binding*: Rectangular holes. Allows for document editing (opening/closing), lays flat, but cannot turn 360 degrees.
  * *Coil / Spiral Binding*: Round holes. Allows 360-degree page turning.
  * *Wire-O (Twin Loop)*: Professional metal finish. Sold in specific pitch ratios (e.g., 3:1 or 2:1). Pitch is a hard constraint.
  * *VeloBind (Strip Binding)*: Punches small holes and melts/welds a plastic strip. It is tamper-proof and highly secure, predominantly used in legal and accounting fields. Returning a comb binder for a VeloBind query is a critical security failure.
- **Laminating Thickness**: Pouch thickness is measured in mils (e.g., 3 mil, 5 mil, 10 mil). The pouch thickness must not exceed the specified laminator machine's maximum capacity.
""",
        ),
        "filing_and_organization": VerticalOverlay(
            description=(
                "Filing cabinets, hanging folders, manila folders, "
                "binders, and indexing systems."
            ),
            content="""\
### Filing and Organization — Scoring Guidance

This query involves spatial organization and document storage hardware.

**Critical distinctions to enforce:**

- **Lateral vs. Vertical Cabinets**: These represent fundamentally different physical footprints and access styles.
  * *Lateral File Cabinets*: Wider than they are tall. Files are stored side-to-side. Often used in high-traffic shared spaces and can accommodate both letter and legal sizes simultaneously.
  * *Vertical File Cabinets*: Taller than they are wide. Files are stored front-to-back. Highly space-efficient for narrow areas but require more physical strain to access. Do not substitute lateral for vertical when explicitly queried, as this is a physical space constraint.
- **Folder Dimensions and Hardware**: Letter-size (8.5x11") folders cannot fit in legal-size (8.5x14") cabinet drawers and vice-versa. Hanging folders require compatible lateral or vertical rails.
- **Tab Cuts**: 1/3-cut, 1/5-cut, and straight-cut refer to the size and visibility of the folder tab. Treat tab specifications as hard workflow constraints.
""",
        ),
        "thermal_printers_and_labels": VerticalOverlay(
            description=(
                "Thermal label printers, direct thermal labels, thermal transfer, "
                "and Avery-style laser/inkjet sheets."
            ),
            content="""\
### Thermal Printers and Specialized Labeling — Scoring Guidance

This query involves barcode printing, shipping labels, and address labels.

**Critical distinctions to enforce:**

- **The Dymo 550 DRM Constraint (Crucial Rule)**: Dymo LabelWriter 550, 550 Turbo, and 5XL models feature firmware and an RFID/ALR chip reader that completely blocks third-party and custom labels. If the query specifies the Dymo 550 series, **only** OEM Dymo branded labels with the recognition chip are relevant. Generic "compatible" thermal labels are a strict failure for the 550 series.
- **Laser vs. Thermal Destruction Hazard**: Avery 5160 labels are engineered for Laser printers, while Avery 8160 labels are for Inkjet printers. Furthermore, feeding direct thermal label paper into a laser printer will melt the leuco dye coating and adhesive onto the fuser, destroying the printer hardware. Thermal labels and laser labels are completely incompatible.
- **Direct Thermal vs. Thermal Transfer**: Direct thermal requires no ribbon (fades over time, good for shipping). Thermal transfer requires a wax/resin ribbon (durable, archivable). Do not mix these up.
""",
        ),
        "janitorial_and_breakroom": VerticalOverlay(
            description=(
                "Facility paper products, commercial dispensers, trash liners, "
                "and breakroom supplies."
            ),
            content="""\
### Janitorial Paper and Breakroom Dispensers — Scoring Guidance

This query involves facility management supplies and commercial paper products.

**Critical distinctions to enforce:**

- **Paper Towel Folds (Dispenser Compatibility)**: Commercial folded towels must match the wall dispenser type and hygiene intent.
  * *Z-Fold (Interfold / Multifold)*: Towels are interlocked. Pulling one dispenses the edge of the next. Used for touchless, high-hygiene single-sheet dispensing.
  * *C-Fold*: Towels are stacked but not interlocked. Requires users to pinch and pull, often leading to multiple towels dispensing at once.
  * Returning a C-Fold towel for a strict Z-Fold/Interfold query violates hygiene and waste-reduction intent.
- **Roll Towels**: Hardwound roll towels vs. Centerpull towels. Centerpull dispenses from the bottom core (highly sanitary). Ensure roll core diameter matches the target dispenser.
- **Trash Can Liners**: Specified by dimensions, gauge (thickness in mils or microns), and density (High Density/HDPE for wet heavy trash vs. Low Density/LLDPE for sharp objects). Treat thickness and density as hard specifications.
""",
        ),
    },
)
