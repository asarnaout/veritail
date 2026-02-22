"""Medical supplies vertical context for LLM judge guidance."""

from veritail.types import VerticalContext, VerticalOverlay

MEDICAL = VerticalContext(
    core="""\
## Vertical: Medical Supplies

You are evaluating search results for a medical supplies and clinical \
products ecommerce site. Think like a composite buyer: a hospital \
procurement officer matching GPO contracts, a clinical administrator \
managing budgets, and a surgical technologist requiring exact \
specifications. In this industry, "close enough" can be a patient \
safety event or a regulatory violation.

### Scoring considerations

- **Sterility as an Absolute Constraint**: Sterile and non-sterile are \
never interchangeable. Surgical instruments, wound dressings, and \
invasive catheters must match the sterility requirement perfectly. A \
non-sterile result for a sterile query is a critical failure.
- **Dimensional and Scale Precision**: Medical sizing is clinical. \
French sizes (Fr), needle gauges (G), and suture sizes (e.g., 2-0 vs 3-0) \
are hard constraints. Note that many scales are inverse: a 30G needle \
is thinner than an 18G needle.
- **Proprietary Ecosystems**: Many items exist in closed systems. IV \
tubing must match the pump (Baxter vs Alaris), and glucose strips must \
match the specific meter brand/model (Contour vs OneTouch).
- **Regulatory and Billing Signals**: FDA Device Classification (I, II, III), \
510(k) clearance, and HCPCS billing codes (e.g., E0601 for CPAP) are \
primary relevance signals. Prescription-only (Rx) items cannot be \
substituted for OTC requests.
- **Latex/Allergen Status**: Facilities often mandate 100% latex-free \
environments. If a query specifies "latex-free," "nitrile," or "vinyl," \
any natural rubber latex result is a critical failure.
- **Unit of Measure (UOM) Alignment**: Institutional buyers order by \
the case or pallet; clinics order by the box or each. Align results \
with volume intent (e.g., "bulk," "sample," "box of 100").

### Industry Vocabulary and Conversions
- 1 French (Fr) = 0.33mm (outer diameter).
- $D (\text{mm}) = Fr / 3$.
- "Ought" sizing: 4-0 is pronounced "four-ought" and is thinner than 2-0.
- GPO = Group Purchasing Organization.
- DME = Durable Medical Equipment.
- UMDNS = Universal Medical Device Nomenclature System.""",
    overlays={
        "surgical_instruments": VerticalOverlay(
            description=(
                "Surgical instruments: forceps, scissors, scalpels, "
                "needle holders, retractors, and rongeurs. Focus on "
                "metallurgy, blade numbering, and pattern names."
            ),
            content="""\
### Surgical Instruments — Scoring Guidance

This query involves precision surgical tools used in sterile environments.

**Critical quirks and nuances:**

- **Gold Handles (Tungsten Carbide)**: Gold plating on handles/rings is the \
universal signal for Tungsten Carbide (TC) inserts. TC is harder than \
stainless steel and holds an edge longer. If a query implies "durability" \
or "TC," only gold-handled or TC-labeled results are highly relevant.
- **Blade Numbering**: Scalpel blades are shape-specific. #10 is for large \
incisions; #11 is for stabs; #15 is for delicate work. Do not treat different \
numbers as substitutes.
- **Pattern Specificity**: Pattern names (Mayo, Metzenbaum, Iris, Adson, \
Babcock) denote specific dimensions and curvatures. A Mayo scissor \
(tough tissue) is not a substitute for a Metzenbaum (delicate dissection).
- **Ratcheted vs. Non-Ratcheted**: Hemostats have "ratchets" to lock closed; \
standard forceps (pickups) do not. This is a functional class distinction.
- **Finishes**: Matte/Satin finish is preferred to reduce glare under OR \
lights. Mirror finish is highly polished. Mismatching finish is a minor \
penalty unless specified.
""",
        ),
        "respiratory_therapy": VerticalOverlay(
            description=(
                "Respiratory equipment: CPAP/BiPAP machines, oxygen "
                "concentrators, nebulizers, and specialized tubing."
            ),
            content="""\
### Respiratory Therapy — Scoring Guidance

This query involves assisted breathing and oxygen delivery equipment.

**Critical quirks and nuances:**

- **CPAP vs. BiPAP**: CPAP is Continuous (one pressure); BiPAP is Bilevel \
(IPAP/EPAP). They are clinically distinct; substituting one for the other \
is a functional error.
- **Tubing Diameter (15mm vs 19mm)**: 22mm is the standard "cuff" connector \
size for masks, but the inner hose diameter can be 19mm (standard) or \
15mm (slim). Most modern machines must be manually set to the correct \
diameter to maintain pressure accuracy.
- **Oxygen Flow Nuances**: Stationary concentrators provide continuous flow \
(often up to 5-10L/min); Portable Concentrators (POCs) often use "Pulse Dose" \
which only delivers oxygen upon inhalation. If a query says "Continuous Flow," \
a pulse-dose POC is a mismatch.
- **Heated Tubing**: Heated hoses (e.g., ClimateLine) are proprietary to \
specific machine models and are used to prevent "rainout" (condensation). \
Non-heated tubing is not a substitute if "heated" is specified.
""",
        ),
        "wound_care": VerticalOverlay(
            description=(
                "Wound dressings and management: alginates, hydrocolloids, "
                "foams, films, hydrogels, and silver-impregnated dressings."
            ),
            content="""\
### Wound Care — Scoring Guidance

This query involves dressings designed to manage the wound healing environment.

**Critical quirks and nuances:**

- **Moisture-Exudate Balance**:
    * *Alginates* (from seaweed) are for high-exudate wounds; they gel upon contact.
    * *Hydrocolloids* are occlusive and for low-to-moderate exudate.
    * *Hydrogels* donate moisture to dry/necrotic wounds.
    Mismatching these creates a clinical risk of maceration or desiccation.
- **MVTR (Moisture Vapor Transmission Rate)**: This is a critical technical \
spec. Dressings for wet wounds require high MVTR (breathability) to allow \
evaporation.
- **Silver (Ag) / Antimicrobial**: If "Silver" or "Ag" is requested, only \
dressings with impregnated silver (antimicrobial) are relevant. Standard \
versions are major mismatches for infected wounds.
- **Adhesion Classes**: "Silicone" or "Soft Silicone" (e.g., Mepilex) is \
specifically for "non-adherent" needs or fragile skin. Standard acrylic \
adhesives are not substitutes.
""",
        ),
        "ppe_hygiene": VerticalOverlay(
            description=(
                "Personal Protective Equipment: masks, gowns, gloves, and "
                "sanitation. Focus on barrier levels and AQL."
            ),
            content="""\
### PPE and Hygiene — Scoring Guidance

This query involves barrier protection for patients and staff.

**Critical quirks and nuances:**

- **AQL (Acceptable Quality Level)**: A statistical measure of pinholes in \
gloves. Surgical gloves require AQL 1.5 or lower. Standard exam gloves \
are AQL 2.5. Do not return AQL 2.5 gloves for "surgical" queries.
- **ASTM Mask Levels**: Level 1 (low fluid), Level 2 (moderate), and Level 3 \
(high fluid/spray). If a query specifies a level, it is a hard constraint.
- **AAMI Gown Levels**: Levels 1-4. Level 4 is the highest barrier and the \
only one considered impermeable to viral penetration (ASTM F1671).
- **N95 vs. Surgical N95**: A standard N95 is an industrial respirator; a \
"Surgical N95" is NIOSH-approved AND FDA-cleared for fluid resistance. \
For OR settings, only the Surgical N95 is a full match.
""",
        ),
        "urology_incontinence": VerticalOverlay(
            description=(
                "Urological supplies: catheters, drainage systems, and "
                "incontinence garments. Focus on tips and coatings."
            ),
            content="""\
### Urology and Incontinence — Scoring Guidance

This query involves urinary drainage and containment.

**Critical quirks and nuances:**

- **Coudé vs. Straight Tip**: Coudé catheters have a curved "elbow" tip \
specifically for navigating obstructions like an enlarged prostate (BPH). \
This is a clinical necessity; a straight tip is a major mismatch for a \
Coudé request.
- **The "Guide Stripe"**: Coudé catheters often have a colored stripe on the \
funnel; this must point "up" (toward the belly) during insertion. This is \
a key safety spec mentioned in professional catalogs.
- **Coatings**: "Hydrophilic" catheters have a polymer coating activated by \
water (low friction); "Silicone" is for long-term use and latex-free needs.
- **Intermittent vs. Foley**: Intermittent is for single-use drainage; \
Foley (indwelling) has a balloon to stay in the bladder. They are NOT \
interchangeable.
""",
        ),
        "diabetes_management": VerticalOverlay(
            description=(
                "Diabetes monitoring and delivery: meters, strips, lancets, "
                "CGMs, and insulin pumps."
            ),
            content="""\
### Diabetes Management — Scoring Guidance

This query involves blood glucose monitoring and insulin delivery.

**Critical quirks and nuances:**

- **Strip Compatibility**: Test strips are proprietary to specific meter \
platforms. Mismatching brands (e.g., Contour Next strips for a Verio meter) \
is a critical failure.
- **Lancet Gauge**: Higher gauge (30G, 33G) means a thinner needle for \
patient comfort. Lower gauge (21G, 26G) is for clinical "safety lancets" \
used for higher volume blood draws.
- **CGM "Therapeutic" Status**: Some CGMs (e.g., Dexcom G6) are "non-adjunctive," \
meaning they can be used for insulin dosing without fingerstick confirmation. \
This is a high-value relevance signal.
- **Control Solutions**: These are liquid "simulated blood" used to test \
meter accuracy. They are specific to the meter brand.
""",
        ),
        "dme_mobility_orthopedics": VerticalOverlay(
            description=(
                "Durable Medical Equipment: wheelchairs, walkers, and braces. "
                "Focus on HCPCS codes and fitting requirements."
            ),
            content="""\
### DME, Mobility, and Orthopedics — Scoring Guidance

This query involves large equipment and musculoskeletal supports.

**Critical quirks and nuances:**

- **OTS vs. Custom-Fitted**: "Off-the-shelf" (OTS) braces require minimal \
adjustment. "Custom-fitted" braces require expert modification (trimming/molding) \
by a certified professional. These have distinct HCPCS billing codes and \
are not substitutes.
- **Weight Capacity**: "Bariatric" or "Heavy Duty" indicates a weight limit \
(typically 350-500 lbs). Standard units are a safety mismatch for bariatric \
queries.
- **Wheelchair Classifications**: K0001 (standard) vs. K0005 (ultra-lightweight). \
The specific "K-code" denotes clinical and billing differences.
- **Rollator vs. Walker**: A rollator has 4 wheels, a seat, and hand brakes; \
a standard walker has 0 or 2 wheels and no seat. They are different categories.
""",
        ),
        "hypodermic_infusion": VerticalOverlay(
            description=(
                "Needles, syringes, IV sets, and infusion supplies. "
                "Focus on connectors and safety engineering."
            ),
            content="""\
### Hypodermic and Infusion — Scoring Guidance

This query involves the delivery or withdrawal of fluids via needle/tubing.

**Critical quirks and nuances:**

- **Luer Lock vs. Luer Slip**: Luer Lock has a threaded screw-on connection; \
Luer Slip is a friction-fit. Luer Lock is required for high-pressure or \
critical infusions to prevent disconnection.
- **Safety-Engineered Devices**: Modern clinical standards require needles \
with safety shields or retraction mechanisms. If "Safety" is requested, \
a standard "naked" needle is a major mismatch.
- **Insulin vs. TB Syringes**: Both are 1mL, but Insulin syringes use \
"Units" (e.g., U-100) and have permanent needles; Tuberculin (TB) syringes \
use "mL" and have detachable needles. They are NOT substitutes.
- **Dead Space**: Low dead-space (LDS) syringes reduce medication waste; \
highly relevant for expensive biologics or vaccines.
""",
        ),
    },
)
