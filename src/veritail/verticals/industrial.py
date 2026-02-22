"""Industrial vertical context for LLM judge guidance."""

from veritail.types import VerticalContext, VerticalOverlay

INDUSTRIAL = VerticalContext(
    core="""\
## Vertical: Industrial

You are evaluating search results for an industrial supply / MRO \
(Maintenance, Repair, and Operations) ecommerce site. Think like a \
maintenance technician searching by exact part number during an emergency \
breakdown, a procurement specialist matching items against an approved \
vendor list, or an engineer specifying components for a new installation. \
In this domain, a wrong part can shut down a production line, create a \
safety hazard, or fail a compliance audit — so precision outweighs \
breadth and "close enough" is almost never acceptable.

### Scoring considerations

- **Hard-constraint-first hierarchy**: When the query specifies thread \
pitch, bore/OD dimensions, pressure rating, temperature rating, voltage/ \
phase/amperage, material grade, tolerance class, pipe schedule, or \
connection standard, treat every mismatch as a major relevance penalty. \
A 1/4"-20 UNC bolt is not a 1/4"-28 UNF bolt; a Schedule 40 pipe is not \
a Schedule 80 pipe; 304 stainless is not 316 stainless. These are not \
minor variants — they are different products for different applications.
- **Part number precision**: Exact MPN, OEM number, or cross-referenced \
part number matches are the strongest possible relevance signal. Near-miss \
part numbers (transposed digits, wrong suffix, different revision letter) \
are almost always wrong parts and should score very low. Superseded or \
equivalent part numbers are acceptable only when the result explicitly \
identifies itself as a direct replacement or cross-reference.
- **System compatibility is non-negotiable**: Metric and imperial are not \
interchangeable. NPT threads cannot mate with BSP threads. Flare fittings \
are not compression fittings. Single-phase motors do not run on three-phase \
power. JIC, SAE, and ORFS hydraulic fittings have different sealing \
geometries. A result in the right product category but the wrong connection \
standard, thread system, or electrical configuration should score very low.
- **Material, coating, and chemical compatibility**: Match the material and \
finish to the intended environment. Buna-N (nitrile) o-rings fail in \
ketone or ozone exposure where Viton or EPDM is needed. Zinc-plated \
fasteners corrode in marine environments where 316 stainless or \
hot-dip galvanized is required. Brass fittings dezincify in certain \
water chemistries. These are safety-critical distinctions.
- **Standards and certification compliance**: When a query references ANSI, \
ASTM, ASME, NFPA, MIL-SPEC, UL, CSA, FM, ISO, or OSHA-related standards, \
treat compliance as mandatory. A valve that lacks FM approval cannot \
substitute for one that requires it. Arc-flash-rated PPE categories \
(NFPA 70E) and voltage-rated glove classes (ASTM D120) are not \
interchangeable across rating levels.
- **PPE and safety gear strictness**: For PPE queries, protection ratings \
are absolute hard constraints. ANSI Z87.1 impact ratings, ANSI/ISEA 105 \
cut levels, arc flash cal/cm² ratings, voltage class for insulated \
gloves, and NFPA 70E PPE categories must match or exceed the queried level. \
Downgrading protection level is never acceptable.
- **Exact replacement vs. upgrade intent**: Industrial buyers searching \
by part number or exact spec almost always need a drop-in replacement — \
same form, fit, and function. Do not reward "upgraded" or "premium" \
alternatives unless the query explicitly signals openness to alternatives. \
A maintenance tech replacing a failed component at 2 AM needs the exact \
part, not a catalog of options.
- **Kit, assembly, and component-level intent**: If the query asks for a \
repair kit, seal kit, or assembly, individual loose components are weak \
matches. Conversely, if the query asks for a single o-ring, gasket, or \
bearing, returning a full rebuild kit is a poor match unless explicitly \
positioned as containing the needed item.
- **Quantity, packaging, and unit-of-measure awareness**: Industrial buyers \
may search for items sold per-each, per-box, per-hundred, or per-thousand. \
A query for "1/4-20 hex nut" likely expects individual or small-box \
quantities, while "1/4-20 hex nuts" (plural) or queries mentioning "box" \
or "bulk" signal volume intent. Mismatched UOM (selling a 100-pack when \
one piece is needed, or vice versa) reduces relevance.
- **Downtime urgency and in-stock bias**: MRO searches frequently occur \
under time pressure — a broken machine on a production floor. Results \
that are clearly in-stock, ship-same-day, or available from local \
branches are materially more relevant than special-order or long-lead-time \
items when the query context suggests urgency or the product category is \
typically a maintenance/replacement item.
- **Brand and manufacturer as specification, not preference**: In \
industrial, brand often encodes engineering specification. A query for \
"Parker hydraulic fitting" or "3M Scotch-Brite" is usually specifying a \
manufacturer's system or a particular product formulation, not expressing \
casual brand loyalty. Treat manufacturer names as hard constraints when \
they appear alongside a part number, and as strong signals when they \
appear with a product category.""",
    overlays={
        "fasteners": VerticalOverlay(
            description=(
                "Threaded fasteners: bolts, screws, nuts, washers, threaded rod, "
                "studs, anchors, rivets, retaining rings, pins — any item defined "
                "primarily by thread size, grade, and material"
            ),
            content="""\
### Fasteners — Scoring Guidance

This query involves threaded fasteners, nuts, washers, or related \
hardware (anchors, rivets, pins, retaining rings, threaded rod, studs).

**Critical distinctions to enforce:**

- **Thread system incompatibility**: UNC (coarse) and UNF (fine) threads \
of the same nominal diameter are incompatible — a 1/2"-13 UNC bolt will \
not thread into a 1/2"-20 UNF nut. Metric ISO threads (e.g., M10×1.5) \
are incompatible with imperial despite dangerously close size overlaps \
(M10 ≈ 3/8", M8 ≈ 5/16", M12 ≈ 1/2"). If the query specifies UNC, UNF, \
or a metric thread pitch, treat it as a hard constraint with zero tolerance.
- **Grade vs property class**: SAE Grade 2/5/8 (imperial) and ISO Property \
Class 4.8/8.8/10.9/12.9 (metric) are two completely separate grading \
systems. Grade 5 (120 ksi) is *roughly* equivalent to Class 8.8, and \
Grade 8 (150 ksi) is *roughly* equivalent to Class 10.9, but they are \
not interchangeable in specification-controlled applications. If the query \
specifies one system, do not substitute the other. The metric property \
class number is mathematically meaningful: first digit × 100 = minimum \
tensile in MPa; second digit × 10 = yield-to-tensile ratio percentage \
(so 10.9 = 1040 MPa tensile, 936 MPa yield).
- **"18-8 stainless" is not a specification**: 18-8 is a composition \
shorthand covering 302, 303, 304, 305, and XM7. A fastener marketed as \
"18-8" may not meet full 304 chemistry. More critically, stainless \
fasteners are 35-40% weaker than same-size carbon steel — never treat \
stainless as equivalent to Grade 5 or 8 without noting the strength gap. \
Metric stainless uses A2-70 (≈304, 700 MPa) and A4-80 (≈316, 800 MPa). \
A2 vs A4 is a hard constraint in corrosive environments.
- **Structural bolt specifications**: ASTM A325 and A490 (now consolidated \
under ASTM F3125) are structural-specific. A490 bolts cannot be hot-dip \
galvanized due to hydrogen embrittlement risk. Do not substitute A307 \
(general purpose, 60 ksi) for A325 (structural, 120 ksi).
- **Coating is not cosmetic**: Zinc electroplating (5-25 μm, 24-96 hr salt \
spray) and hot-dip galvanizing (43-100+ μm, 1000+ hr salt spray) are \
vastly different. Hot-dip galvanized bolts require oversize-tapped nuts \
because the coating adds thread thickness — standard nuts will not fit. \
High-strength fasteners (≥Grade 8 / ≥10.9) require baking after \
electroplating to prevent hydrogen embrittlement.
- **Hex cap screw ≠ hex bolt**: A hex cap screw has a washer face under the \
head and tighter body tolerances than a hex bolt. Different thread length \
formulas apply. These are distinct products in specification-controlled \
procurement.
- **Set screw point types are not interchangeable**: Cup, cone, flat, dog, \
and half-dog point set screws serve different retention purposes. If the \
query specifies a point type, treat as hard.
- **DIN vs ISO bolt dimensions**: DIN 931/933 and ISO 4014/4017 differ in \
width-across-flats at M10, M12, M14, and M22, meaning different wrench \
sizes at those four sizes. If the query references DIN or ISO specifically, \
do not cross-substitute at those sizes.

**Terminology**:
- cap screw = hex cap screw (NOT socket head cap screw unless "socket" is stated)
- SHCS = socket head cap screw
- BHCS = button head cap screw
- FHCS = flat head cap screw (countersunk)
- lag screw = lag bolt (wood threads, not machine threads)
- nyloc = nylon insert lock nut
- jam nut = thin nut (approximately half height of standard)
""",
        ),
        "bearings": VerticalOverlay(
            description=(
                "Bearings: ball bearings, roller bearings, needle bearings, thrust "
                "bearings, mounted bearings (pillow blocks, flanges), bearing "
                "inserts, linear bearings — any rotary or linear bearing product"
            ),
            content="""\
### Bearings — Scoring Guidance

This query involves bearings — ball, roller, needle, thrust, spherical, \
mounted units (pillow blocks, flanges), or linear motion bearings.

**Critical distinctions to enforce:**

- **Bearing number decoding**: Standard designations encode type, series, \
and bore. Example: 6205-2RS-C3 → 6 = deep groove ball, 2 = light width \
series, 05 = 25mm bore, 2RS = double rubber seal, C3 = increased \
clearance. The bore code is intuitive for 04+ (multiply by 5: 04=20mm, \
05=25mm, 06=30mm), but is irregular below 04: 00=10mm, 01=12mm, \
02=15mm, 03=17mm. Treat the complete bearing designation including all \
suffixes as a single hard-match identifier.
- **Suffix codes change the product fundamentally**:
  * 2RS (rubber contact seal) vs ZZ (metal shield) — 2RS provides better \
contamination protection but generates more friction/heat. Not interchangeable \
in high-speed or high-temp applications.
  * C3 (increased radial clearance) vs C0/unmarked (normal clearance) — C3 \
is required for interference shaft fits or high temperature differentials. \
Using C3 on a slip fit unnecessarily reduces bearing life. Clearance \
progression: C2 (reduced) → C0 (normal) → C3 → C4 → C5 (maximum).
  * If the query specifies any suffix, treat it as hard.
- **ABEC tolerance is NOT a quality ladder**: ABEC 1 (= ISO P0) is the \
standard normal class, not "low quality." ABEC 1 is sufficient for the \
vast majority of industrial applications. ABEC 5+ is for machine tool \
spindles and precision instruments. The ABEC scale (1,3,5,7,9) maps to \
ISO classes that run in the OPPOSITE direction (P0, P6, P5, P4, P2). \
ABEC controls bore/OD tolerances and runout but does NOT control \
internal clearance, lubrication, ball grade, noise level, or cage type. \
Do not treat higher ABEC as universally "better."
- **Mounted bearing designations**: A pillow block is a HOUSING type, not \
a bearing type. UCP205 = UC205 insert bearing in a P205 pillow block \
housing. UCF205 = same insert in an F205 four-bolt flange. The insert \
mounting method (set screw vs eccentric collar) is NOT interchangeable. \
If the query specifies UCP, UCF, UCFL, UCFC, or similar, the housing \
type is a hard constraint.
- **Bearing type substitution**: Deep groove ball, angular contact, \
cylindrical roller, tapered roller, spherical roller, and needle \
bearings serve fundamentally different load cases (radial, axial, \
combined, self-aligning). Do not substitute across bearing types even \
if bore/OD/width match.

**Terminology**:
- pillow block = plummer block (UK term)
- 2RS = 2RSR = DDU = LLU (brand-specific suffix for double rubber seal)
- ZZ = 2Z = DD (brand-specific suffix for double metal shield)
- bearing insert = housed bearing inner unit
""",
        ),
        "power_transmission": VerticalOverlay(
            description=(
                "Power transmission: V-belts, timing belts, roller chains, "
                "sprockets, gears, sheaves/pulleys, couplings, keystock — "
                "mechanical drive components (not motors or drives)"
            ),
            content="""\
### Power Transmission — Scoring Guidance

This query involves mechanical power transmission components: belts, \
chains, gears, sprockets, sheaves/pulleys, couplings, or keystock.

**Critical distinctions to enforce:**

- **V-belt cross-section designations are separate systems**: Classical \
(A, B, C, D, E) and narrow/wedge (3V, 5V, 8V) are different profile \
families. Metric V-belts (SPZ, SPA, SPB, SPC) do NOT directly correspond \
to classical sections. An "A" belt sheave will not accept a "3V" belt. If \
the query specifies a cross-section, it is a hard constraint.
- **Timing belt tooth profiles are NOT cross-compatible**: Classical \
profiles (XL, L, H, XH, XXH defined by pitch) use trapezoidal teeth. \
Curvilinear profiles (HTD, GT2/PowerGrip GT, GT3/PowerGrip GT3) use \
rounded teeth. A GT2 belt will NOT run on an HTD sprocket even at the \
same pitch because the tooth geometry differs. If the query specifies a \
tooth profile, it is a hard constraint.
- **Roller chain: ANSI ≠ ISO/BS despite same pitch**: ANSI chain (#35, \
#40, #50, #60, #80) and ISO/BS chain (06B, 08B, 10B, 12B, 16B) share \
the same pitch but differ in roller diameter and plate dimensions. An \
ANSI #40 chain (1/2" pitch) will not run properly on an 08B sprocket. \
The ANSI number encodes pitch: divide by 8 for pitch in inches \
(#40 = 4/8" = 1/2", #60 = 6/8" = 3/4"). If the query includes a chain \
number, match the exact standard (ANSI or ISO/BS).
- **Gear pitch systems — diametral pitch vs module**: Imperial gears use \
diametral pitch (DP = teeth per inch of pitch diameter). Metric gears use \
module (M = pitch diameter in mm / number of teeth). These are reciprocal \
(Module = 25.4/DP) but gears must match EXACTLY. A 20-DP gear will NOT \
mesh with a Module 1.25 gear despite being mathematically close. Pressure \
angle (14.5° legacy vs 20° standard) must also match between mating gears. \
If either pitch system or pressure angle is specified, treat as hard.
- **Coupling types are application-specific**: Jaw couplings, disc \
couplings, gear couplings, and grid couplings handle different levels of \
misalignment, torque, and speed. Jaw coupling spider (insert) hardness \
determines flexibility and damping. Bore size and keyway are hard physical \
constraints.

**Terminology**:
- sheave = V-belt pulley
- toothed pulley = timing pulley = synchronous sprocket
- keystock = key stock = key bar (square or rectangular drive key material)
- #40 chain = ANSI 40 chain = 40-1 (single strand) or 40-2 (duplex)
""",
        ),
        "hydraulic_fittings_hose": VerticalOverlay(
            description=(
                "Hydraulic fittings and hose: JIC fittings, SAE fittings, ORFS "
                "fittings, ORB fittings, hydraulic adapters, hydraulic hose "
                "assemblies, hose ends, quick-disconnect couplings for hydraulic "
                "systems (not pipe fittings or pneumatic)"
            ),
            content="""\
### Hydraulic Fittings and Hose — Scoring Guidance

This query involves hydraulic fittings, adapters, hose, or couplings \
used in hydraulic power systems operating at high pressure (typically \
1,000-10,000 PSI).

**Critical distinctions to enforce:**

- **Fitting standard confusion is the most dangerous trap in industrial \
MRO**: The following fitting types share thread sizes on multiple dash \
sizes, meaning they will physically thread together but create leak paths \
or catastrophic failures at hydraulic pressures:
  * JIC 37° flare (SAE J514) — metal-to-metal 37° cone seal, UNF threads
  * SAE 45° flare (SAE J512) — 45° cone seal, same UNF threads as JIC on \
dash sizes -02 through -10. VISUALLY SIMILAR to JIC but 8° seat \
difference guarantees a leak.
  * O-Ring Boss / ORB (SAE J1926) — straight UNF thread with o-ring at \
base. Same threads as JIC but completely different sealing mechanism.
  * O-Ring Face Seal / ORFS (SAE J1453) — flat face with o-ring groove, \
UNF thread. Highest leak-free reliability.
  * NPT/NPTF — tapered 60° pipe thread, seals by thread deformation. \
PTFE tape is used on NPT but must NEVER be used on o-ring fittings.
  * BSPP (ISO 228) — parallel 55° Whitworth thread, seals with o-ring or \
bonded washer. NOT compatible with NPT despite both being "pipe thread."
  * BSPT (ISO 7) — tapered 55° Whitworth thread. NOT compatible with NPT \
(different thread angle: 55° vs 60°).
  If the query specifies or implies a fitting standard (JIC, SAE 45°, \
ORFS, ORB, NPT, BSP), treat it as an absolute hard constraint.
- **Dash size means different things in different contexts**: For hoses, \
dash size = ID in sixteenths of an inch (-4 = 1/4" ID, -8 = 1/2" ID). \
For tube fittings, dash size = OD in sixteenths (-4 = 1/4" OD). For \
fitting port threads, dash maps to a UNF thread that follows neither \
rule simply. An LLM must not conflate these three meanings.
- **Hose construction determines pressure rating**: SAE 100R1 (1-wire \
braid) handles ~2,750 PSI; R2 (2-wire braid) handles ~5,000 PSI; R12 \
(4-spiral wire) handles ~4,000 PSI constant. The standard burst-to-\
working pressure safety factor is 4:1. EN 853 1SN/2SN are European \
equivalents of R1/R2 but are NOT identical specs. If the query specifies \
an SAE or EN hose series, match it.
- **Quick-disconnect body size and type**: ISO A, ISO B, flat-face, and \
various OEM-specific styles (Pioneer, Parker 60/71 series) are NOT \
cross-compatible. If a brand or series is specified, treat as hard.

**Terminology**:
- JIC = Joint Industry Council (37° flare standard)
- ORFS = O-Ring Face Seal
- ORB = O-Ring Boss
- dash size = "-4", "-6", "-8", "-10", "-12", "-16" (size designation)
- SAE 45° = inverted flare (automotive/refrigeration, NOT hydraulic)
""",
        ),
        "pneumatic": VerticalOverlay(
            description=(
                "Pneumatic components: push-to-connect fittings, pneumatic tubing, "
                "air cylinders, pneumatic valves (solenoid, manual), FRLs (filter-"
                "regulator-lubricators), air preparation, pneumatic quick-connect "
                "couplings (not hydraulic fittings)"
            ),
            content="""\
### Pneumatic Components — Scoring Guidance

This query involves pneumatic (compressed air) fittings, tubing, \
cylinders, valves, or air preparation equipment.

**Critical distinctions to enforce:**

- **Push-to-connect fitting sizes**: Metric (4mm, 6mm, 8mm, 10mm, 12mm \
OD) and imperial (1/8", 5/32", 1/4", 3/8", 1/2" OD) tube sizes are NOT \
interchangeable. A 6mm PTC fitting will not seal on 1/4" (6.35mm) tubing. \
If the query specifies metric or imperial tube OD, treat as hard.
- **Thread port vs tube size**: Pneumatic fittings have two specifications \
— the port thread (typically NPT, BSPT, BSPP, or metric) and the tube \
OD they accept. Both must match. A "1/4 NPT × 6mm" fitting has 1/4" NPT \
port thread and accepts 6mm OD tubing — these are independent dimensions.
- **Pneumatic valve notation**: "5/2 valve" means 5 ports, 2 positions — \
this is standard ISO nomenclature. "5/3 valve" = 5 ports, 3 positions \
(with a center/neutral position). "3/2" = 3 ports, 2 positions. The \
notation describes the valve function and is a hard constraint. Actuation \
type (solenoid, pilot, manual, spring-return) is also a hard constraint \
when specified.
- **Cylinder bore and stroke**: Pneumatic cylinders are specified by bore \
diameter (force) and stroke length (travel). Both are hard constraints. \
Mounting style (tie-rod, round body, compact, guided) and rod thread \
determine physical compatibility.
- **FRL (Filter-Regulator-Lubricator)**: These are often sold as \
assemblies or individual units. A "filter regulator" query expects the \
combo; a "coalescing filter" is a specific high-efficiency type for \
removing oil aerosols, NOT a standard particulate filter. Port size and \
flow capacity (SCFM at a given pressure drop) must match when specified.

**Terminology**:
- PTC = push-to-connect = push-in = instant fitting
- FRL = filter-regulator-lubricator = air preparation unit
- SCFM = standard cubic feet per minute (flow at standard conditions)
- 5/2 = five-port, two-position (valve configuration)
""",
        ),
        "electrical": VerticalOverlay(
            description=(
                "Electrical wire, cable, conduit, connectors, terminals, "
                "enclosures, fuses, circuit breakers, disconnect switches, "
                "relays, terminal blocks, and wiring accessories — electrical "
                "distribution and wiring components (not motors or drives)"
            ),
            content="""\
### Electrical Components — Scoring Guidance

This query involves electrical distribution, wiring, protection, or \
enclosure components — wire, cable, conduit, connectors, fuses, breakers, \
enclosures, relays, or terminal blocks.

**Critical distinctions to enforce:**

- **AWG is inverse**: Smaller AWG number = larger wire. 10 AWG is larger \
than 14 AWG. This counter-intuitive convention means "larger gauge" is \
ambiguous — clarify by actual AWG number. Key ampacity values (NEC \
Table 310.16, copper, 75°C column): 14 AWG = 20A, 12 AWG = 25A, \
10 AWG = 35A, 8 AWG = 50A, 6 AWG = 65A. However, NEC 240.4(D) limits \
overcurrent protection to 15A for 14 AWG, 20A for 12 AWG, and 30A for \
10 AWG, regardless of actual ampacity.
- **Wire insulation types are not interchangeable**: THHN (thermoplastic, \
high heat 90°C dry, nylon jacket) is the most common building wire. Most \
modern THHN is dual-rated THHN/THWN-2, approved for 90°C wet and dry. \
XHHW-2 is cross-linked polyethylene rated 90°C wet/dry, preferred for \
larger sizes. THHN is not rated for direct burial; UF (underground feeder) \
or USE-2 is required. If the query specifies an insulation type, match it.
- **Conduit trade sizes are nominal**: 1/2" EMT has an OD of ~0.840" and \
an ID of ~0.706" — NOT 0.500". Trade sizes are labels with no direct \
dimensional meaning. EMT, IMC, and rigid (RMC) conduit in the same trade \
size have different wall thicknesses and therefore different IDs. Conduit \
type (EMT, IMC, rigid, PVC, FMC, LFMC) is a hard constraint — they use \
different fittings and have different code applications.
- **NEMA enclosure ratings ≠ IP ratings**: NEMA includes tests for \
corrosion, icing, oil, and gasket aging that IP does not. A NEMA-rated \
enclosure meets or exceeds the mapped IP rating, but an IP-rated \
enclosure does NOT necessarily meet the corresponding NEMA standard. Key \
mappings: NEMA 1 ≈ IP10 (indoor), NEMA 3R ≈ IP14 (outdoor rain), NEMA 4 \
≈ IP66 (watertight), NEMA 4X ≈ IP66 + corrosion resistance, NEMA 12 ≈ \
IP52 (dust/drip). NEMA numbering is non-linear — NEMA 12 provides LESS \
water protection than NEMA 4.
- **Fuse classes are physical rejection features**: Class J, RK1, RK5, CC, \
and T fuses have different physical dimensions to prevent incorrect \
insertion. Class J provides highest current-limiting performance. RK1 \
and RK5 share dimensions with non-current-limiting Class H, but R-type \
rejection holders prevent insertion of Class H. If a specification \
requires a specific fuse class, it is a hard constraint — often tied to \
equipment UL listing.
- **Circuit breaker frame and trip**: Breaker frame size determines \
physical dimensions and maximum amperage. Trip rating is the actual \
overcurrent setpoint. Both frame and trip must match. Bolt-on, plug-in, \
and DIN-rail mount are physically incompatible form factors.

**Terminology**:
- EMT = electrical metallic tubing (thin-wall conduit)
- IMC = intermediate metal conduit
- RMC = rigid metal conduit
- FMC = flexible metal conduit ("Greenfield")
- LFMC = liquid-tight flexible metal conduit ("Sealtite")
- NEMA 4X = outdoor watertight + corrosion resistant (stainless/fiberglass)
""",
        ),
        "motors_drives": VerticalOverlay(
            description=(
                "Electric motors, variable frequency drives (VFDs), motor starters, "
                "contactors, overload relays, soft starters, and servo motors/drives "
                "— rotating electrical machinery and motor control (not general "
                "electrical wiring or enclosures)"
            ),
            content="""\
### Motors and Drives — Scoring Guidance

This query involves electric motors, VFDs, motor starters, or servo \
systems.

**Critical distinctions to enforce:**

- **NEMA frame size encodes shaft height**: The first two digits ÷ 4 = \
shaft centerline height in inches. Frame 143T = 3.50" height. Frame \
256T = 6.25". The "T" suffix indicates current NEMA standardized \
dimensions — pre-1964 "U" frame motors have DIFFERENT dimensions for \
the same HP. A replacement motor must match the frame designation, not \
just horsepower. Frame size is a hard constraint.
- **Five hard constraints for motor replacement**: voltage (115/208/230/\
460V), phase (single/three), frame size, speed (RPM = synchronous speed \
× (1 - slip)), and enclosure type (ODP, TEFC, XPRF). All five must \
match or the motor is not a valid replacement. A 3-phase motor will NOT \
run on single-phase power. A 230V motor on 208V service will run but \
underperforms (~15% torque reduction) and may overheat.
- **NEMA Design type determines torque characteristics**: Design B is the \
industry default (general purpose — fans, pumps, blowers). Design C \
provides high starting torque (loaded conveyors, compressors). Design D \
provides very high starting torque with 5-13% slip (punch presses, \
hoists). These are NOT interchangeable for the same application. If the \
query specifies a NEMA Design letter, treat as hard.
- **NEMA vs IEC motors**: IEC frame sizes (e.g., 90, 100, 112) use mm \
shaft height. IEC 90 (90mm) is close to NEMA 143T (88.9mm) but mounting \
dimensions differ. IEC motors carry no service factor (rated continuous \
S1 duty); NEMA motors typically carry 1.15 SF. IEC efficiency classes \
(IE1/IE2/IE3/IE4) roughly map to NEMA standard/energy efficient/premium \
but test methods differ. NEMA and IEC frames are NOT directly \
interchangeable on the same base plate without modification.
- **VFD-rated (inverter duty) vs standard motors**: VFD-rated motors have \
reinforced insulation (withstands PWM voltage spikes), may include \
insulated bearings and shaft grounding rings, and often have independent \
cooling fans for low-speed constant-torque operation. Running a standard \
motor on a VFD for constant-torque loads risks overheating and insulation \
failure. If the query specifies "inverter duty" or "VFD rated," standard \
motors are a poor match.
- **VFD sizing**: VFDs are sized by HP and voltage class. Input vs output \
voltage ratings differ — a "480V drive" expects 480V input 3-phase and \
outputs 480V 3-phase to the motor. Single-phase input VFDs driving \
3-phase motors must be derated, typically by 50%. Communication protocol \
(Modbus, EtherNet/IP, PROFINET) and enclosure rating matter when specified.

**Terminology**:
- ODP = Open Drip Proof (indoor, clean environment)
- TEFC = Totally Enclosed Fan Cooled (dusty/wet environments)
- XPRF = Explosion Proof (hazardous locations)
- SF = Service Factor (1.15 means motor can sustain 115% of rated load)
- VFD = Variable Frequency Drive = inverter = AC drive
""",
        ),
        "pipe_valves_fittings": VerticalOverlay(
            description=(
                "Pipe, valves, and pipe fittings: steel/stainless/PVC pipe, gate "
                "valves, ball valves, globe valves, check valves, butterfly valves, "
                "pipe fittings (elbows, tees, unions, couplings), flanges, strainers, "
                "and steam traps — piping system components (not hydraulic fittings)"
            ),
            content="""\
### Pipe, Valves, and Fittings — Scoring Guidance

This query involves piping system components: pipe, pipe fittings, \
valves, flanges, strainers, or steam traps.

**Critical distinctions to enforce:**

- **NPS (Nominal Pipe Size) does NOT equal any actual dimension for sizes \
1/8" through 12"**: NPS 1/2 pipe has an OD of 0.840", NOT 0.500". NPS 1 \
= 1.315" OD. NPS 2 = 2.375" OD. For NPS 14+, nominal equals actual OD. \
The OD is fixed for each NPS; pipe schedule changes the wall thickness \
(and therefore the ID) while OD remains constant. Schedule 40 is "standard \
wall" for most sizes; Schedule 80 is "extra heavy." This equivalence \
breaks down above NPS 10 (Sch 40 ≠ STD wall for large pipe).
- **Pipe size ≠ tube size**: Tube OD IS the actual outside diameter — a \
1/2" tube has 0.500" OD. A 1/2" NPS pipe has 0.840" OD. Pipe fittings \
and tube fittings are physically incompatible despite the same nominal \
size. This is one of the most common confusion errors.
- **Valve pressure class is NOT a direct PSI value**: Class 150, 300, 600, \
900, 1500, 2500 are dimensionless designators. Class 150 WCB carbon steel \
is rated to 285 PSIG at ambient temperature, decreasing with temperature. \
"150#", "Class 150", and "150 Lb" are all synonymous. If the query \
specifies a pressure class, it is a hard constraint.
- **Valve type determines function**:
  * Gate valves: on/off isolation ONLY — NOT for throttling (partial opening \
causes erosion and vibration).
  * Globe valves: designed for throttling and flow regulation.
  * Ball valves: quarter-turn on/off. Full-port vs standard (reduced) port \
affects flow restriction significantly.
  * Check valves: swing, lift, wafer, and dual-plate types serve different \
flow/pressure conditions.
  * Butterfly valves: wafer, lug, and double-flanged mounting types are NOT \
interchangeable. Lug-style allows dead-end service; wafer does not.
  Do not substitute across valve types unless the query is generic.
- **Flange face types are safety-critical**: Raised Face (RF), Flat Face \
(FF), and Ring-Type Joint (RTJ) are NOT interchangeable. Using a raised-\
face gasket against a flat-face cast iron flange creates a bending moment \
that can crack the flange — this is a code violation per ASME B31.
- **Valve body materials**: WCB = carbon steel (most common), CF8M = 316 \
stainless, CF8 = 304 stainless, LCC = low-temp carbon steel, WC6 = \
chrome-moly. These casting codes are different from wrought specs (A105, \
F316). If the query specifies material, match the correct standard.
- **Fitting classes**: Threaded fittings: 150# and 300# for cast (ASME \
B16.3/B16.4), and 2000#/3000#/6000# for forged (ASME B16.11). Socket \
weld fittings: 3000# or 6000#. Butt weld fittings (ASME B16.9) match \
pipe schedule. "Malleable iron" vs "cast iron" vs "ductile iron" are \
three different materials — malleable is impact-resistant; gray cast iron \
is brittle; ductile iron is strongest.

**Terminology**:
- NPT = National Pipe Thread (tapered, self-sealing with sealant)
- NPS = Nominal Pipe Size (dimension system, NOT thread)
- Sch 40 = Schedule 40 = standard wall (for most sizes)
- 150# = Class 150 = 150 Lb (flange/valve pressure class)
- RF = raised face, FF = flat face, RTJ = ring-type joint (flange faces)
- WCB = cast carbon steel (ASTM A216 Grade WCB)
""",
        ),
        "pumps": VerticalOverlay(
            description=(
                "Pumps: centrifugal pumps, positive displacement pumps (gear, "
                "diaphragm, peristaltic, piston), sump pumps, submersible pumps, "
                "booster pumps, chemical pumps, and pump accessories"
            ),
            content="""\
### Pumps — Scoring Guidance

This query involves pumps of any type — centrifugal, positive \
displacement, submersible, or specialty pumps.

**Critical distinctions to enforce:**

- **Head is NOT pressure**: Centrifugal pump head is measured in feet of \
water (or meters). The conversion is 2.31 feet of water = 1 PSI (for \
water). A pump rated for 100 feet of head produces ~43 PSI with water \
but a different pressure with fluids of different specific gravity. Do \
not conflate "feet of head" with PSI in search matching.
- **NPSH is the most misunderstood spec**: NPSHr (required, a pump \
characteristic) must be exceeded by NPSHa (available, an installation \
characteristic) to prevent cavitation. NPSHr is a product spec; NPSHa \
is the buyer's responsibility. If the query references NPSH, ensure the \
result provides NPSHr data.
- **ANSI B73.1 vs API 610**: ANSI B73.1 chemical process pumps are \
dimensionally standardized across manufacturers — all sizes are \
interchangeable footprint and piping connections. API 610 pumps are \
custom-engineered with higher construction standards, centerline mounting, \
and a mandated 20-year design life. These are fundamentally different \
product categories despite both being "centrifugal pumps." If the query \
specifies ANSI or API, treat as hard.
- **Pump type determines application**: Centrifugal pumps handle clean, \
low-viscosity fluids. Positive displacement pumps (gear, diaphragm, \
peristaltic, progressive cavity, piston) are required for high-viscosity \
fluids, precise metering, self-priming, or shear-sensitive products. Do \
not substitute PD for centrifugal or vice versa when the query specifies \
a type.
- **Seal type matters**: Mechanical seals vs packing vs sealless \
(magnetic-drive or canned-motor) pumps have completely different \
maintenance profiles and fluid compatibility. Sealless pumps eliminate \
leak paths for hazardous fluids. If specified, treat as hard.
- **Port size and connection type**: Pump inlet and outlet sizes (e.g., \
2" × 1.5") with flanged, threaded, or cam-lock connections are hard specs.

**Terminology**:
- BEP = Best Efficiency Point (optimal operating region on pump curve)
- TDH = Total Dynamic Head (total head the pump must overcome)
- GPM = gallons per minute (flow rate)
- mag-drive = magnetic drive (sealless pump)
""",
        ),
        "ppe_head_eye_face": VerticalOverlay(
            description=(
                "Head, eye, and face PPE: hard hats, safety helmets, safety "
                "glasses, safety goggles, face shields, welding helmets, hearing "
                "protection (earplugs, earmuffs) — personal protective equipment "
                "for head, eyes, ears, and face"
            ),
            content="""\
### Head, Eye, Face, and Hearing PPE — Scoring Guidance

This query involves personal protective equipment for head, eyes, face, \
or hearing protection.

**Critical distinctions to enforce:**

- **Hard hat Type and Class are independent ratings**:
  * Type I = top-of-head impact protection ONLY.
  * Type II = top AND lateral (side/front/back) impact protection.
  * Class E (Electrical) = tested to 20,000V.
  * Class G (General) = tested to 2,200V.
  * Class C (Conductive) = zero electrical protection.
  Type and Class are independent — a hat can be Type I Class E or Type II \
Class G, etc. Vented hard hats CANNOT be rated Class E or G because the \
vents compromise electrical insulation. If the query specifies Type or \
Class, treat as hard. Historical name change: old "Class A" → current \
"Class G"; old "Class B" → current "Class E."
- **Z87.1 impact marking — the plus sign is critical**:
  * "Z87" (without plus) = basic impact only.
  * "Z87+" (with plus) = HIGH IMPACT rated (tested to a steel ball at \
~102 mph for spectacles, ~170 mph for goggles).
  Both markings must appear on BOTH frames AND lenses. If the query asks \
for "Z87+" or "high impact," the plus sign is a hard requirement.
- **Additional Z87.1 lens codes**: "D3" = splash/droplet, "D4" = dust, \
"D5" = fine dust, "W" + shade number = welding filter shade. If the query \
includes these codes, enforce them.
- **Welding shade numbers are application-specific**: Shade 10-14 for arc \
welding (higher amperage = darker shade), Shade 3-5 for cutting/brazing. \
Auto-darkening helmets have a resting shade (typically 3-4) and a welding \
shade range (typically 9-13). If a specific shade is queried, treat as hard.
- **Hearing protection — NRR is not additive**: NRR (Noise Reduction \
Rating) is derated in practice. OSHA uses (NRR - 7) / 2 for real-world \
estimation. Dual protection (plugs + muffs) adds only ~5 dB, not the sum. \
Earplugs (in-ear) and earmuffs (over-ear) are different product types — \
do not substitute when specified. Band-mounted (cap-mount) hearing \
protection attaches to hard hat slots and is NOT compatible with all \
hard hat brands.

**Terminology**:
- hard hat = safety helmet (note: "safety helmet" increasingly refers to \
climbing-style Type II helmets with chin straps)
- NRR = Noise Reduction Rating (EPA-mandated, in decibels)
- Z87+ = ANSI Z87.1 high-impact rated
""",
        ),
        "ppe_hand": VerticalOverlay(
            description=(
                "Hand protection: cut-resistant gloves, chemical-resistant gloves, "
                "heat-resistant gloves, general-purpose work gloves, disposable "
                "gloves (nitrile, latex, vinyl), leather gloves — all work gloves "
                "(not electrical insulating gloves; see ppe_arc_flash_fr)"
            ),
            content="""\
### Hand Protection / Work Gloves — Scoring Guidance

This query involves work gloves — cut-resistant, chemical-resistant, \
heat-resistant, general-purpose, or disposable.

**Critical distinctions to enforce:**

- **ANSI/ISEA 105 old vs new cut levels — this is the single most \
confusing PPE standard transition**: The 2011 edition used 5 cut levels \
(1-5) based on the CPPT ("coup test") rotating blade. The 2016+ edition \
uses 9 cut levels (A1-A9) based on the TDM-100 straight-blade test with \
gram-force thresholds. The old levels DO NOT map directly to the new \
levels because the test methods are fundamentally different. When a \
product references "ANSI Cut Level A4," it uses the new standard. When \
a product says "Cut Level 4," it may reference the old standard. \
"Level 4" (old) and "A4" (new) are NOT the same rating — old Level 4 \
covered ~1500-3500 grams; new A4 covers 1500-2199 grams specifically. \
If the query specifies a cut level, match the standard edition carefully.
- **EN 388 (European) is a completely different system**: EN 388 uses four \
performance digits (abrasion, cut/coup test, tear, puncture) plus an \
optional TDM cut letter (A-F) and an optional impact protection mark (P). \
EN 388 cut letters A-F do NOT directly equal ANSI A1-A6. If the query \
references EN 388, do not convert to ANSI levels.
- **Chemical resistance is chemical-specific**: "Chemical-resistant gloves" \
is meaningless without specifying the chemical. Nitrile resists oils and \
fuels but fails against ketones. Neoprene handles acids and caustics. \
Butyl rubber resists ketones and esters. PVA resists aromatics but \
dissolves in water. If the query specifies a chemical class, the glove \
material must be compatible.
- **Disposable glove materials**: Nitrile (most common, latex-free, chemical \
resistance), latex (best fit/feel, allergen risk), vinyl (cheapest, lowest \
protection). Thickness (mil) determines durability: exam-grade ~3-5 mil, \
industrial ~5-8 mil, heavy-duty ~8-15 mil. Powder-free vs powdered is a \
hard constraint when specified. If the query specifies material or \
thickness, enforce it.
- **Glove sizing and dexterity vs protection**: Higher cut resistance \
generally reduces dexterity. Gauge (13-gauge, 15-gauge, 18-gauge knit) \
affects thickness and feel — higher gauge = thinner/more dexterous. If \
gauge is specified, treat as hard.

**Terminology**:
- ANSI A4 = ANSI/ISEA 105-2016 (or later) Cut Level A4
- "Cut Level 4" = potentially old ANSI/ISEA 105-2011 Level 4 (different!)
- mil = thousandths of an inch (glove thickness)
- nitrile = NBR = acrylonitrile-butadiene rubber
""",
        ),
        "ppe_arc_flash_fr": VerticalOverlay(
            description=(
                "Arc flash PPE, FR clothing, electrical safety: arc-rated suits, "
                "FR shirts/pants/coveralls, electrical insulating gloves (voltage-"
                "rated), arc flash face shields, electrical safety kits, hi-vis "
                "vests and garments — NFPA 70E and electrical PPE"
            ),
            content="""\
### Arc Flash, FR Clothing, and Electrical PPE — Scoring Guidance

This query involves flame-resistant (FR) clothing, arc-flash-rated (AR) \
PPE, electrical insulating gloves, or hi-vis safety garments.

**Critical distinctions to enforce:**

- **NFPA 70E PPE Categories define minimum arc ratings**:
  * Category 1 = minimum 4 cal/cm²
  * Category 2 = minimum 8 cal/cm²
  * Category 3 = minimum 25 cal/cm²
  * Category 4 = minimum 40 cal/cm²
  Above 40 cal/cm², energized work must NOT be performed. The old term \
"Hazard Risk Category (HRC)" is obsolete — current standard uses "PPE \
Category." If the query uses HRC, it is equivalent to PPE Category. \
Category level is a hard constraint — a Cat 2 garment cannot substitute \
for Cat 3.
- **Arc-rated vs flame-resistant**: ALL arc-rated (AR) clothing IS \
flame-resistant (FR), but NOT all FR clothing is arc-rated. FR clothing \
without an arc rating (cal/cm² value) is not suitable for electrical \
arc flash hazard — it only means the fabric self-extinguishes. This is \
a critical distinction: a query for "arc-rated" or a specific cal/cm² \
value requires AR garments, not just FR. A query for "FR" without arc \
specifications may accept either.
- **Arc rating measurement**: The arc rating is expressed as ATPV (Arc \
Thermal Performance Value) or EBT (Energy Breakopen Threshold) in \
cal/cm². ATPV is the more common measure; when both are tested, the \
lower value is reported as the arc rating. These are NOT interchangeable \
with PPE Category — a garment rated 12 cal/cm² meets Cat 2 (8 cal/cm²) \
but not Cat 3 (25 cal/cm²).
- **Electrical insulating gloves (ASTM D120) — voltage classes**:
  * Class 00 = 500V AC max use / 2,500V proof test
  * Class 0 = 1,000V AC max use / 5,000V proof test
  * Class 1 = 7,500V AC max use / 10,000V proof test
  * Class 2 = 17,000V AC max use / 20,000V proof test
  * Class 3 = 26,500V AC max use / 30,000V proof test
  * Class 4 = 36,000V AC max use / 40,000V proof test
  Voltage class is an absolute hard constraint — NEVER downgrade. \
Electrical gloves must ALWAYS be worn with leather protector gloves \
over them (unless protectorless-rated). Electrical gloves require \
periodic retesting per ASTM D120/OSHA 1910.137.
- **Hi-vis classifications (ANSI/ISEA 107)**: Type O (off-road), Type R \
(roadway), Type P (public safety). Performance Classes 1, 2, 3 define \
minimum square inches of background and retroreflective material. Class 3 \
provides the highest visibility. If the query specifies a class, treat \
as hard.

**Terminology**:
- FR = flame-resistant (fabric self-extinguishes)
- AR = arc-rated (has a tested cal/cm² value)
- HRC = Hazard Risk Category (obsolete term for PPE Category)
- cal/cm² = calories per square centimeter (arc energy unit)
- ATPV = Arc Thermal Performance Value
""",
        ),
        "ppe_respiratory_foot": VerticalOverlay(
            description=(
                "Respiratory protection and safety footwear: N95 respirators, "
                "half-face and full-face respirators, PAPR systems, filter "
                "cartridges, safety-toe boots and shoes, metatarsal guards, "
                "EH-rated footwear"
            ),
            content="""\
### Respiratory Protection and Safety Footwear — Scoring Guidance

This query involves respirators, dust masks, respiratory cartridges/\
filters, safety-toe boots/shoes, or protective footwear.

**Critical distinctions to enforce (Respiratory):**

- **NIOSH filter designation system**: The letter indicates oil resistance; \
the number indicates filtration efficiency:
  * N = Not oil-resistant (most common for dust/particles)
  * R = somewhat oil-Resistant (single shift use in oil environments)
  * P = oil-Proof (extended use in oil-laden atmospheres)
  * 95 = 95% filtration, 99 = 99%, 100 = 99.97% (HEPA-equivalent)
  N95 blocks 95% of particles without oil resistance. P100 blocks 99.97% \
and resists oil. These are not interchangeable — an N95 will degrade in \
oil mist environments where a P100 is needed.
- **Respirator type determines protection factor**:
  * Filtering facepiece (N95 mask): APF 10 (protects up to 10× PEL)
  * Half-face respirator: APF 10
  * Full-face respirator: APF 50
  * PAPR (Powered Air Purifying Respirator): APF 25-1000 depending on type
  If the query specifies half-face vs full-face vs PAPR, it is a hard \
constraint tied to the required protection factor.
- **Cartridge type is hazard-specific**: OV (organic vapor), AG (acid gas), \
AM (ammonia/methylamine), P100 (particulate), and combination cartridges \
each address specific hazards. An OV cartridge provides zero protection \
against acid gas. Multi-gas cartridges (OV/AG/P100) exist but must be \
explicitly rated for each hazard.
- **Fit testing is size-dependent**: Respirators come in S/M/L or universal \
sizes. OSHA requires annual fit testing for tight-fitting respirators — \
the size must match the user's face. If the query specifies a size, it is \
not a preference.

**Critical distinctions to enforce (Footwear):**

- **ASTM F2413 performance codes**:
  * I/75 or I (Impact) = 75 ft-lbs impact protection on the toe
  * C/75 or C (Compression) = 2,500 lbs compression protection on the toe
  * Mt (Metatarsal) = metatarsal impact protection
  * EH (Electrical Hazard) = insulated sole/heel, tested to 18,000V
  * SD (Static Dissipative) = dissipates static gradually (prevents sparks)
  * CD (Conductive) = maximum conductivity (prevents static on person)
  SD and CD serve OPPOSITE purposes and are NOT interchangeable. SD \
prevents spark ignition; CD prevents static buildup.
- **Safety toe material**: Steel toe (heaviest, thinnest profile, conducts \
temperature), composite toe (non-metallic, lighter, does not conduct \
cold/heat, passes metal detectors), alloy toe (aluminum, lighter than \
steel, thinner than composite). If the query specifies toe material, \
treat as hard.

**Terminology**:
- APF = Assigned Protection Factor
- PEL = Permissible Exposure Limit (OSHA)
- PAPR = Powered Air Purifying Respirator
- OV = organic vapor, AG = acid gas (cartridge types)
- EH = Electrical Hazard (boot rating)
""",
        ),
        "welding": VerticalOverlay(
            description=(
                "Welding: stick electrodes, MIG wire, TIG filler rod, flux-core "
                "wire, shielding gas, welding machines, welding helmets, welding "
                "accessories, solder — welding consumables, equipment, and supplies"
            ),
            content="""\
### Welding — Scoring Guidance

This query involves welding consumables, equipment, or accessories.

**Critical distinctions to enforce:**

- **Stick electrode classification (AWS A5.1/A5.5)**: E7018 decodes as: \
E = electrode, 70 = 70,000 PSI minimum tensile strength, 1 = all-position \
capable, 8 = low-hydrogen potassium coating with iron powder, AC or DCEP. \
The third digit encodes position capability: "1" = all-position (flat, \
horizontal, vertical, overhead); "2" = flat and horizontal only. The last \
two digits together encode coating type and polarity:
  * "10" = cellulose sodium, DCEP only (E6010 for pipe root passes)
  * "11" = cellulose potassium, AC or DCEP (E6011 = AC version of E6010)
  * "18" = low-hydrogen potassium/iron powder, AC or DCEP (E7018)
  **E6010 will NOT run on AC welding power** — E6011 is the AC equivalent. \
This polarity constraint is hard. E7018 is the most common structural \
electrode and must be stored in rod ovens (250-300°F) after opening — \
moisture contamination causes hydrogen cracking in welds.
- **MIG wire classification (AWS A5.18)**: ER70S-6 = ER (electrode/rod) + \
70 (70 ksi tensile) + S (solid wire) + 6 (high deoxidizer chemistry). \
The "-6" has the highest Mn/Si deoxidizer content, ideal for slightly \
dirty base metals. ER70S-2 and ER70S-3 have less deoxidizer and require \
cleaner base metals. Wire diameter (0.023", 0.030", 0.035", 0.045") is a \
hard constraint determined by material thickness and machine capability.
- **Flux-core wire — gas-shielded vs self-shielded**: E71T-1 = \
gas-shielded flux-core ("dual shield") — requires external shielding gas. \
E71T-8 and E71T-11 = self-shielded ("innershield") — no external gas \
needed. These require completely different setups. If the query specifies \
gas-shielded or self-shielded flux-core, treat as hard.
- **Shielding gas is NOT interchangeable across processes**: MIG carbon \
steel: 75% Ar / 25% CO₂ ("C25") is standard; 100% CO₂ is cheaper with \
deeper penetration but more spatter. MIG stainless: requires different gas \
(typically 98% Ar / 2% CO₂ or tri-mix). TIG: 100% argon for most \
applications. If the query specifies a gas mixture, match it.
- **Process terminology**: SMAW = Stick, GMAW = MIG = wire-feed (with gas), \
GTAW = TIG, FCAW = Flux-Core. "Wire feed welder" is ambiguous — could \
be MIG (solid wire + gas) or flux-core (tubular wire ± gas). Match the \
specific process when identified.
- **Welding machine type**: Stick-only, MIG-only, TIG-only, and multi-\
process machines are different products. Input power (120V vs 240V vs \
dual-voltage) and output amperage range are hard specs.

**Terminology**:
- DCEP = DC Electrode Positive (= DC Reverse Polarity)
- DCEN = DC Electrode Negative (= DC Straight Polarity)
- C25 = 75% Argon / 25% CO₂ shielding gas blend
- E7018 = low-hydrogen all-position stick electrode, 70 ksi
- ER70S-6 = solid MIG wire, 70 ksi, high deoxidizer
""",
        ),
        "cutting_tools": VerticalOverlay(
            description=(
                "Cutting tools and toolholding: indexable inserts, drill bits, "
                "end mills, taps, reamers, saw blades, toolholders, collets, "
                "tool arbors — metalworking and machining tooling"
            ),
            content="""\
### Cutting Tools and Toolholding — Scoring Guidance

This query involves metalworking cutting tools, inserts, drills, end \
mills, taps, or toolholding systems.

**Critical distinctions to enforce:**

- **ISO insert designation (ISO 1832)**: CNMG 120408 decodes as: C = 80° \
diamond shape, N = 0° clearance (negative rake, enables double-sided use), \
M = medium tolerance class, G = hole with chipbreaker both faces. Dimensions: \
12 = 12.70mm IC (inscribed circle), 04 = 4.76mm thickness, 08 = 0.8mm \
nose radius. The ANSI equivalent (CNMG 432) uses 1/8" IC increments, \
1/16" thickness, and 1/64" nose radius. A CNMG insert CANNOT go in a \
WNMG holder — the shape letter must match the toolholder's pocket geometry. \
Every element of the designation is a hard constraint.
- **Carbide grade ISO application ranges**: P (steel) = blue, M (stainless) \
= yellow, K (cast iron) = red, N (non-ferrous) = green, S (superalloys) \
= brown, H (hardened steel) = grey. Each manufacturer (Sandvik, Kennametal, \
Iscar, Seco) has proprietary grade designations within these ranges that \
do NOT cross-reference directly. If the query specifies a manufacturer \
grade (e.g., "Sandvik GC4325"), treat as a hard constraint.
- **Coating type matters**: CVD coatings (TiCN/Al₂O₃/TiN multilayer) are \
thicker and better for roughing at moderate speeds. PVD coatings (TiAlN, \
AlCrN) are thinner and better for finishing, interrupted cuts, and \
non-ferrous materials. Uncoated is preferred for aluminum (coated edges \
promote built-up edge). If coating is specified, treat as hard.
- **Toolholder taper systems are NOT interchangeable**: CAT40 and BT40 \
have the same taper angle but different flange geometry — CAT uses a \
V-flange, BT uses a different flange common in Japanese machines. HSK \
(hollow shank taper) is a completely different system. Morse taper (MT), \
R8 (Bridgeport mills), 5C (collet systems) are all incompatible. If \
the query specifies a taper system, it is a hard constraint.
- **Drill bit sizing systems overlap**: Fractional (1/16" increments), \
letter (A=0.234" through Z=0.413"), number (#1=0.228" through #80=0.0135"), \
and metric (0.1mm increments) all overlap. A 1/4" drill, an E letter \
drill (0.250"), and a 6.35mm drill are the same size. Point angle matters: \
118° for soft materials; 135° split-point for harder materials and \
self-centering. If point angle is specified, enforce it.
- **Tap types**: Taper (starting tap), plug (general purpose), bottoming \
(threads close to bottom of blind hole) serve different functions. Thread \
specification (size, pitch, UNC/UNF/metric) must match exactly. Form taps \
(roll taps) vs cutting taps produce threads by different methods.

**Terminology**:
- IC = inscribed circle (insert size)
- CNMG = insert designation (shape-clearance-tolerance-chipbreaker)
- CAT40 = V-flange taper, 40 taper size (most common US CNC)
- BT40 = Japanese-style taper, 40 taper size
- HSK = Hollow Shank Taper (high-speed/precision)
""",
        ),
        "abrasives": VerticalOverlay(
            description=(
                "Abrasives: grinding wheels, cut-off wheels, flap discs, sanding "
                "discs, sanding belts, sandpaper, deburring tools, wire wheels — "
                "coated and bonded abrasive products"
            ),
            content="""\
### Abrasives — Scoring Guidance

This query involves bonded abrasives (grinding/cut-off wheels), coated \
abrasives (sandpaper, sanding discs, belts, flap discs), or wire wheels.

**Critical distinctions to enforce:**

- **CAMI vs FEPA grit systems diverge above 220**: CAMI (US, plain numbers: \
80, 120, 220, 400) and FEPA (European, P-prefix: P80, P120, P220, P400) \
are approximately equivalent through 220 grit but diverge significantly \
above that. P400 FEPA has a particle size of ~35 μm; CAMI 400 has ~23.6 μm \
— P400 is roughly 50% coarser than CAMI 400. At P600 (25.75 μm) vs \
CAMI 600 (16 μm), the gap widens further. Do NOT treat "P400" and \
"400 grit" as identical for finishing applications. If the query includes \
a "P" prefix or specifies FEPA/CAMI, match the correct system.
- **Grinding wheel marking system**: Standard marking example "A 60-K-5-V" \
decodes as: A = aluminum oxide abrasive, 60 = grit, K = medium bond \
hardness, 5 = medium structure, V = vitrified bond. "Hardness" in grinding \
wheels means BOND hardness (resistance to grain release), NOT abrasive \
hardness. A "hard" wheel (P-Z) holds grains longer and suits soft \
materials; a "soft" wheel (D-G) releases grains readily and suits hard \
materials. This is counterintuitive — do not reverse it.
- **Grinding wheel speed ratings are safety-critical**: Maximum RPM (or \
SFPM) is printed on every wheel. Exceeding it risks catastrophic wheel \
burst. If the query specifies a grinder size (4.5", 7", 9") or RPM, \
the wheel must be rated for that speed/size.
- **Wheel type designations**: Type 1 = flat/straight disc, Type 27 = \
depressed center (for angle grinders), Type 41 = thin cut-off disc. \
These have different mounting and use characteristics.
- **Abrasive material selection**: Aluminum oxide = steel/ferrous metals. \
Silicon carbide = non-ferrous metals, stone, glass. Zirconia alumina and \
ceramic alumina = heavy stock removal on steel. Diamond and CBN = \
hardened steel, carbide, ceramics. If the query specifies the abrasive \
material or the workpiece material, enforce compatibility.
- **Flap disc grit and type**: Flap discs use Type 27 (flat) or Type 29 \
(conical) configurations. Type 29 is more aggressive for grinding; Type 27 \
is better for finishing/blending. If specified, treat as hard.

**Terminology**:
- A/O = aluminum oxide
- S/C = silicon carbide
- ZA = zirconia alumina
- CBN = cubic boron nitride
- SFPM = surface feet per minute (wheel speed)
""",
        ),
        "adhesives_sealants": VerticalOverlay(
            description=(
                "Adhesives, sealants, and tapes: threadlockers, retaining compounds, "
                "epoxies, cyanoacrylates, silicone sealants, construction adhesives, "
                "thread sealant tape, pipe dope, gasket makers — bonding and sealing "
                "products (not o-rings or cut gaskets)"
            ),
            content="""\
### Adhesives, Sealants, and Tapes — Scoring Guidance

This query involves adhesives, sealants, thread sealants, or specialty \
tapes used for bonding, sealing, or locking.

**Critical distinctions to enforce:**

- **Loctite threadlocker color/number system**: Purple 222 = low strength \
(adjustment screws, small fasteners ≤1/4"). Blue 242/243 = medium strength \
removable (general purpose). Green 290 = medium wicking grade for \
pre-assembled joints (post-assembly application). Red 262/271/272 = high \
strength permanent (requires 500°F heat for removal). These strength \
grades are NOT interchangeable — using red where blue is needed makes \
future disassembly destructive. If the query specifies a color or number, \
treat as hard.
- **Threadlocker vs retaining compound vs thread sealant**: All are \
anaerobic but serve different functions. Threadlockers (242, 271) prevent \
fastener loosening. Retaining compounds (680, 620) bond cylindrical \
assemblies (bearings in bores, pins in holes) — NOT for threads. Thread \
sealants (545, 565) seal pipe threads — NOT for locking. Loctite 680 is \
a retaining compound, NOT a threadlocker. Do not confuse these categories.
- **Adhesive chemistry determines application**:
  * Anaerobic: metal-to-metal only, cures without air, needs close fit
  * Cyanoacrylate (super glue): instant bond, poor heat resistance \
(max ~180°F), poor chemical resistance
  * Epoxy (two-part): highest structural strength (5,000-6,000 PSI), \
excellent gap-filling, temperature resistant (200°C+)
  * Silicone: flexible, wide temp range (-75°F to 500°F), poor structural \
strength, good for gasket-making and sealing
  * Polyurethane: flexible, paintable, good outdoor resistance
  These chemistries are NOT interchangeable. If the query specifies a \
chemistry type (or a clear application implying one), enforce it.
- **PTFE / Teflon tape types**: Standard white (general plumbing), yellow \
(gas-rated per UL/CSA), pink (high-density for larger pipe). Yellow gas \
tape is a hard constraint for gas pipe — white tape is not code-compliant \
for gas. PTFE tape must NEVER be used on o-ring-sealed fittings (ORB, \
ORFS, BSPP) — fragments damage the o-ring.
- **Pipe thread sealant (pipe dope) vs tape**: Both seal NPT threads but \
are different products. Some sealants are rated for specific services \
(gas, oxygen, potable water, steam). If the query specifies a service, \
the product must be rated for it.

**Terminology**:
- threadlocker = thread-locking adhesive
- retaining compound = bearing adhesive = cylindrical bonding adhesive
- pipe dope = thread sealant compound
- RTV = Room Temperature Vulcanizing (silicone sealant/gasket maker)
""",
        ),
        "lubrication": VerticalOverlay(
            description=(
                "Lubrication: grease, hydraulic oil, gear oil, machine oil, "
                "compressor oil, chain lubricant, penetrating oil, dry lubricant, "
                "grease guns, oil cans — lubricants and lubrication tools"
            ),
            content="""\
### Lubrication — Scoring Guidance

This query involves lubricants (grease, oil, dry lubricant) or \
lubrication application tools.

**Critical distinctions to enforce:**

- **ISO VG numbers are NOT the same as SAE numbers**: ISO VG (Viscosity \
Grade) is kinematic viscosity in centistokes at 40°C per ISO 3448. \
ISO VG 32, 46, and 68 are the most common hydraulic oil grades. Each \
grade spans ±10% of its midpoint. The SAE viscosity system (automotive) \
and AGMA (gear) systems are completely separate — ISO VG 32 ≈ SAE 10W, \
ISO VG 68 ≈ SAE 20, ISO VG 150 ≈ SAE 40, but these are approximate \
cross-references only. If the query specifies ISO VG, do not substitute \
SAE grades.
- **NLGI grease grade is consistency, NOT performance**: The scale runs \
from 000 (semi-fluid) through 6 (very hard, block-like). NLGI 2 is the \
standard for most general bearing applications. NLGI 1 is used for \
centralized lubrication systems; NLGI 3 for vertical shafts or \
high-speed bearings. The number says nothing about base oil type, \
additive package, temperature range, or load capacity. If the query \
specifies an NLGI grade, it is a hard constraint.
- **Grease thickener compatibility is critical**: Mixing incompatible \
thickener types causes softening or hardening and bearing failure. \
Lithium + lithium complex = compatible. Lithium + polyurea = INCOMPATIBLE. \
Calcium sulfonate + lithium complex = questionable. If the query specifies \
a thickener type (lithium, polyurea, calcium sulfonate, etc.), enforce it.
- **Oil types are application-specific**: Hydraulic oil (AW = anti-wear), \
gear oil (EP = extreme pressure), compressor oil (specific to compressor \
type — rotary screw vs reciprocating), way oil (slideway lubricant with \
tackifier), and spindle oil (very low viscosity) are NOT interchangeable. \
EP additives in gear oil can corrode yellow metals (bronze bushings) in \
hydraulic systems. If the query specifies an oil type, match it.
- **Food-grade lubricants**: NSF H1 = incidental food contact. NSF H2 = \
no food contact. NSF H3 = soluble oils for direct food contact (rare). \
H1 and H2 are NOT interchangeable when food contact is a requirement.

**Terminology**:
- AW = Anti-Wear (hydraulic oil additive type)
- EP = Extreme Pressure (gear oil additive type)
- ISO VG = ISO Viscosity Grade (centistokes at 40°C)
- NLGI = National Lubricating Grease Institute (consistency grade)
- cSt = centistokes (kinematic viscosity unit)
""",
        ),
        "seals_gaskets_orings": VerticalOverlay(
            description=(
                "Seals, gaskets, and o-rings: o-rings (AS568 dash sizes), oil seals, "
                "shaft seals, mechanical seals, gasket material/sheets, spiral wound "
                "gaskets, packing, V-rings — sealing components (not adhesive sealants)"
            ),
            content="""\
### Seals, Gaskets, and O-Rings — Scoring Guidance

This query involves sealing components: o-rings, oil/shaft seals, \
gaskets, packing, or mechanical seals.

**Critical distinctions to enforce:**

- **O-ring sizing (AS568 dash numbers)**: Dash numbers encode ID and \
cross-section. They are grouped by cross-section series:
  * -001 to -049 = 1/16" cross-section
  * -102 to -178 = 3/32" cross-section
  * -201 to -284 = 1/8" cross-section
  * -309 to -395 = 3/16" cross-section
  * -425 to -475 = 1/4" cross-section
  Both the dash number AND the material must match. A -210 Viton o-ring \
is a different product from a -210 Buna-N o-ring. Metric o-ring sizes \
(ID × CS in mm) do NOT map directly to AS568 dash numbers.
- **O-ring material compatibility is the hardest constraint**:
  * Buna-N / Nitrile / NBR: petroleum, hydraulic oil, fuels — the \
general-purpose material. FAILS in ketones, ozone, esters.
  * Viton / FKM: broad chemical resistance, high temp (400°F), but NOT \
compatible with ketones, esters, ammonia, or hot water/steam.
  * EPDM: water, steam, brake fluids, phosphate esters — but DESTROYED \
by petroleum products. Using EPDM in a hydraulic system is catastrophic.
  * Silicone: wide temp range (-100°F to 450°F) but poor abrasion \
resistance and incompatible with most petroleum products.
  * PTFE: near-universal chemical compatibility but NO elasticity — used \
as backup rings, not primary sealing elements.
  * Kalrez / FFKM: near-universal resistance at extreme temps — very \
expensive ($50-500+ per o-ring).
  If the query specifies a material, it is a hard constraint driven by \
the service environment. Do not substitute materials.
- **Durometer (Shore A hardness)**: Standard is 70A. 90A is for \
high-pressure applications. 50A is for vacuum service. If specified, \
treat as hard.
- **Oil seal / shaft seal specifications**: ID (shaft size), OD (bore \
size), width, lip material, and spring-loaded vs springless are all \
constraining. Single-lip seals retain lubricant; double-lip seals also \
exclude contaminants. If any dimension is specified, it is hard.
- **Gasket types are not interchangeable**: Spiral wound (ASME B16.20, \
for flanged pipe joints), sheet gasket (cut to fit), ring joint (RTJ, \
high pressure), and compressed fiber gaskets serve different pressure/\
temperature classes.

**Terminology**:
- Buna-N = nitrile = NBR (same material, different names)
- Viton = FKM (Viton is a Chemours/DuPont brand name)
- Kalrez = FFKM (Kalrez is a DuPont brand name)
- TC = double-lip oil seal (common Chinese/metric designation)
- dash number = AS568 size designation (e.g., -210, -214)
""",
        ),
        "material_handling": VerticalOverlay(
            description=(
                "Material handling: hoists, slings (wire rope, chain, synthetic), "
                "shackles, turnbuckles, casters, hand trucks, pallet jacks, "
                "shelving, workbenches, lifting magnets, come-alongs — lifting, "
                "rigging, transport, and storage equipment"
            ),
            content="""\
### Material Handling — Scoring Guidance

This query involves lifting, rigging, transport, or storage equipment.

**Critical distinctions to enforce:**

- **Working Load Limit (WLL) is a legal maximum**: Slings, shackles, \
hoists, and rigging hardware have rated WLLs per OSHA 29 CFR 1910.179 \
and ASME B30 standards. Exceeding WLL is a federal violation. If the \
query specifies a capacity, the product WLL must meet or exceed it.
- **Sling angle dramatically affects capacity**: A sling's WLL applies \
at a straight vertical hitch. In a basket hitch at 60° from horizontal, \
effective capacity is 87% per leg; at 45° it is 71%; at 30° it is only \
50%. Choker hitch = 75-80% of vertical WLL. If the query implies a \
specific hitch type, the rated WLL for that configuration must be met.
- **Sling material determines application**: Wire rope slings handle high \
temperatures and abrasion but are heavy. Synthetic (nylon/polyester) web \
slings are lightweight and non-marring but degrade above 180-194°F and \
must NOT contact sharp edges without protection. Chain slings handle the \
highest temperatures (400°F+ for alloy chain) and are most durable but \
heaviest. Sling type is a hard constraint when specified.
- **Alloy chain grades**: Grade 80 and Grade 100 are rated for overhead \
lifting. Grade 30 (proof coil) and Grade 43 (high test) are for \
tie-down/binding ONLY — using them for overhead lifting is an OSHA \
violation and a life-safety hazard. Chain grade is a hard constraint.
- **Caster capacity ratings assume ideal conditions**: Published load \
ratings assume level, smooth floors at walking speed. Shock loads, \
uneven surfaces, and speeds over 3 MPH require 50%+ derating. Swivel \
vs rigid casters are not interchangeable in sets. Wheel material \
(polyurethane, rubber, nylon, cast iron, phenolic) determines floor \
protection, noise, and actual load capacity. Stem/plate mounting type \
is a hard physical constraint.
- **Shelving load ratings**: Per-shelf capacity vs total unit capacity \
are different specs. Wire shelving, solid steel, and boltless/rivet \
shelving have different load characteristics. NSF-certified shelving is \
required in food-related environments.

**Terminology**:
- WLL = Working Load Limit (not "safe working load" — that term is \
deprecated per ASME)
- SWL = Safe Working Load (older, deprecated term for WLL)
- Grade 80 = alloy chain rated for overhead lifting
- come-along = lever hoist = lever chain puller
""",
        ),
        "test_measurement": VerticalOverlay(
            description=(
                "Test and measurement: multimeters, clamp meters, pressure gauges, "
                "thermometers, calipers, micrometers, torque wrenches, calibration "
                "equipment, thermal cameras, vibration analyzers — measurement "
                "instruments and tools"
            ),
            content="""\
### Test and Measurement — Scoring Guidance

This query involves measurement instruments, gauges, precision \
measuring tools, or calibration equipment.

**Critical distinctions to enforce:**

- **Multimeter CAT ratings are NOT cumulative**: CAT (measurement \
category) ratings define safety against transient voltage spikes:
  * CAT I = electronic circuits (lowest transient energy)
  * CAT II = single-phase receptacle outlets
  * CAT III = distribution panels, branch circuits
  * CAT IV = utility entrance, service drops (highest transient energy)
  A CAT II 1000V meter is NOT safer than a CAT III 600V meter for panel \
work — CAT III requires much higher transient withstand capability. The \
CAT level matters more than the voltage rating for safety. If the query \
specifies a CAT rating, treat as hard.
- **Pressure gauge accuracy classes (ASME B40.100)**: Grade 4A = ±0.1%, \
3A = ±0.25%, 2A = ±0.5%, 1A = ±1%, A = ±2%, B = ±3%, D = ±5%. \
Accuracy is percentage of FULL SCALE, not of reading — a 100 PSI gauge \
with Grade A accuracy is ±2 PSI across its entire range, meaning at \
10 PSI the actual error could be 20% of reading. If accuracy class is \
specified, match it.
- **Calibration certificate types are not equivalent**: "Certificate of \
Conformance" (non-specific) ≠ "Certificate of Calibration" (with data) \
≠ "ISO 17025 Accredited Calibration Certificate" (third-party verified). \
"NIST-traceable" means an unbroken chain of comparisons to a national \
standard — it does NOT mean calibrated BY NIST. If the query specifies \
calibration type, enforce it.
- **Precision measuring tools**: Calipers and micrometers have resolution \
(smallest readable increment: 0.001", 0.0001") and accuracy (conformance \
to true value) as separate specs. Digital vs dial vs vernier are different \
reading methods with different capabilities. If resolution or accuracy \
is specified, treat as hard.
- **Torque wrench types**: Click, beam, dial, and electronic torque \
wrenches have different accuracy specs (±4% clockwise is typical per \
ASME B107.300). Drive size (1/4", 3/8", 1/2", 3/4", 1") and torque \
range are both hard constraints.

**Terminology**:
- CAT III = measurement category III (distribution panel level)
- DMM = digital multimeter
- NIST-traceable = traceable calibration chain (not calibrated by NIST)
- ISO 17025 = accredited calibration laboratory standard
""",
        ),
        "raw_materials": VerticalOverlay(
            description=(
                "Raw materials and stock: steel bar/plate/sheet/tube, aluminum "
                "bar/plate/sheet/extrusions, stainless steel stock, brass/copper "
                "stock, plastic sheet/rod/tube (UHMW, Delrin, nylon, PTFE), "
                "rubber sheet — metal and plastic raw material stock"
            ),
            content="""\
### Raw Materials — Scoring Guidance

This query involves metal or plastic raw material stock (bar, plate, \
sheet, tube, rod, extrusion, or rubber/gasket sheet).

**Critical distinctions to enforce:**

- **Steel grade specifies chemistry and properties**: AISI/SAE grades \
encode alloy system (first two digits) and carbon content (last two \
digits in hundredths of %). 1018 = plain carbon, 0.18% C (low carbon, \
easily machinable and weldable). 4140 = chrome-moly, 0.40% C (much \
harder, requires preheat for welding). A36 = structural steel (36 ksi \
yield). A572 Grade 50 = HSLA (50 ksi yield). A500 = specifically for \
hollow structural sections (HSS tube), NOT interchangeable with A36 \
plate. If the query specifies a grade, it is a hard constraint.
- **Stainless steel types**: 304 (18-8, general purpose, good corrosion \
resistance), 316 (marine/chemical resistance, contains molybdenum), \
303 (free-machining, reduced corrosion resistance), 410 (martensitic, \
hardenable, magnetic), 17-4PH (precipitation hardening, aerospace). \
These are NOT interchangeable — 304 vs 316 can be the difference between \
corrosion failure and success in chloride environments. The "L" suffix \
(304L, 316L) indicates low carbon for weld corrosion resistance.
- **Aluminum temper designations are critical**: T6 = solution heat \
treated + artificially aged (maximum hardness but residual stress). \
T651 = T6 + stretching for stress relief — REQUIRED for plate stock to \
prevent warping during machining. T6511 = T6 + stretching + straightening \
— preferred for extruded bar/rod. 6061-T6 (45 ksi UTS) is general \
purpose and readily weldable. 7075-T6 (83 ksi UTS) is aerospace-grade \
and essentially NON-weldable by conventional methods. If temper is \
specified, it is a hard constraint.
- **Form factor matters**: Round bar, hex bar, flat bar, plate, sheet, \
tube (seamless vs welded), pipe (different from tube — see pipe_valves_\
fittings overlay), angle, channel, and I-beam are all distinct products. \
"Hot-rolled" vs "cold-rolled" vs "cold-drawn" affect dimensional \
tolerance, surface finish, and mechanical properties. If the query \
specifies a form or condition, treat as hard.
- **Plastic types are NOT interchangeable**: Delrin/acetal/POM (high \
strength, low friction), UHMW polyethylene (impact/abrasion resistant, \
FDA), Nylon PA6 vs PA66 (different moisture absorption and temp limits), \
PEEK (high-performance, high-cost, high-temp), PTFE/Teflon (low \
friction, chemical resistant, poor structural strength). Each serves \
specific engineering requirements. If the query names a specific plastic, \
enforce it.

**Terminology**:
- CRS = Cold Rolled Steel
- HRS = Hot Rolled Steel
- HR = Hot Rolled (surface condition)
- CF = Cold Finished (= cold drawn, tighter tolerances)
- HSS = Hollow Structural Section (steel tube, NOT High Speed Steel)
- Delrin = acetal = POM (DuPont brand name for polyoxymethylene)
- UHMW = Ultra-High Molecular Weight Polyethylene
""",
        ),
    },
)
