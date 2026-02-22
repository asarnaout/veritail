"""Automotive vertical context for LLM judge guidance."""

from veritail.types import VerticalContext, VerticalOverlay

AUTOMOTIVE = VerticalContext(
    core="""\
## Vertical: Automotive Parts

You are evaluating search results for an automotive parts and accessories \
ecommerce site. In automotive parts, a product that does not fit the \
buyer's exact vehicle is irrelevant regardless of how similar it appears \
— it is a return, a safety risk, or a car stranded on a lift. Fitment \
precision is the dominant evaluation signal and outweighs brand, price, \
or cosmetic similarity.

### Scoring considerations

#### Hard gates (any mismatch is an immediate disqualifier)

- **YMM fitment**: When the query specifies or implies a vehicle — by \
Year/Make/Model ("2019 Honda Civic"), platform code ("FK7"), or \
generation ("10th gen Civic") — the result must fit that exact \
application. Sub-model and trim matter: a Civic Si uses different \
brake and suspension components than a base Civic. Engine and \
transmission splits within the same model year (1.5T vs 2.0L) further \
constrain fitment. Production-date splits ("built after 03/2019") are \
equally hard boundaries — many parts have mid-year revisions that \
create incompatible variants within the same model year.
- **Part number precision**: Exact OEM or aftermarket part number match \
is the strongest relevance signal. Near-miss part numbers (wrong \
suffix, different revision) are usually different parts — a suffix \
change often signals revised material, updated connector, or changed \
mounting point. Accept cross-references and supersessions only when \
the result explicitly identifies itself as a direct replacement.
- **Side, position, and direction**: Left/driver (LH) vs right/passenger \
(RH), upper vs lower, front vs rear are hard constraints. A right-side \
headlight for a left-side query is the wrong part. When the query \
specifies position, treat any mismatch as a disqualifier.
- **Regulatory compliance (when requested)**: Some products require \
explicit compliance claims or identifiers in order to be legal or safe. \
Examples include CARB compliance (often shown via a CARB Executive \
Order / EO number) for emissions parts in jurisdictions that require it, \
DOT/SAE markings for lighting, and FMVSS 205-relevant markings for \
automotive glazing (AS1/AS2/AS3, DOT mark). When the query explicitly \
calls out a compliance regime ("CARB", "50-state legal", "DOT", "SAE", \
"FMVSS", "AS1"), treat missing compliance evidence as a disqualifier.
- **Fluid and chemical specifications (when requested)**: Oil viscosity \
(0W-20 vs 5W-30), OEM approvals (dexos, ILSAC GF-6), transmission \
fluid type (ATF+4 vs Mercon LV vs CVT fluid), coolant chemistry \
(IAT vs OAT vs HOAT), and brake fluid grade (DOT 3 vs DOT 4 vs DOT 5) \
are hard constraints when specified. Mismatches can damage systems or \
violate service requirements.
- **Dimensional specifications**: Tire size (225/45R17), wheel bolt \
pattern (5x114.3), center bore, offset, and load/speed ratings are \
physical hard constraints — a wrong bolt pattern will not mount. \
Thread pitch for fasteners (M10x1.25 vs M10x1.5) and hardware grade \
(Grade 8 vs Grade 5) are similarly non-interchangeable.

#### Significant penalties (apply a major relevance penalty)

- **Universal vs direct-fit mismatch**: Universal-fit parts (catalytic \
converters, mufflers, CV boots) require cutting, welding, or \
fabrication and are not bolt-on replacements. When a query implies \
direct-fit intent (vehicle-specific search), a universal result is a \
significantly weaker match. Conversely, when a query specifies \
universal dimensions ("2.5 inch universal muffler"), vehicle-specific \
results are irrelevant.
- **OEM/aftermarket tier mismatch**: When the query says "OEM" or \
"genuine," aftermarket results are penalized. When the query signals \
budget intent, OEM parts at 3x the price are poor matches. \
Remanufactured parts match replacement intent but not new-OEM intent.
- **Component vs system scope mismatch**: When the query names a specific \
component ("front brake pads"), other parts in the same system (rotors, \
calipers, ABS sensors) are weak matches. When the query says "kit" \
or "set," returning only one component is incomplete.
- **VIN-level option mismatch**: Engine code, transmission type (manual \
vs CVT), drive configuration (2WD vs 4WD), brake package, suspension \
type, and body style create fitment splits within the same YMM. \
When the query includes these identifiers, treat them as constraints \
on par with YMM.
- **Paint code for collision parts**: Body panels, bumper covers, and \
mirrors are often sold pre-painted or paint-to-match. Paint codes \
(e.g., Toyota 1F7, Ford UX) are hard constraints for pre-painted \
parts. An unpainted result when the query specifies a paint code, or \
the wrong color, is a significant mismatch.

#### Soft signals (use for tiebreaking, not major penalties)

- **Brand as specification**: When the query names a brand alongside a \
part, treat it as a hard constraint. When brand is omitted, do not \
penalize any tier, but recognize that OE-supplier brands (Denso, \
Bosch, NGK, Aisin) carry stronger fitment assurance than economy \
aftermarket.
- **Superseded and discontinued parts**: When a query references a \
superseded part number, the current replacement is a strong match. \
For classic/vintage vehicles, reproduction, NOS, and quality \
aftermarket are all valid — do not penalize non-OEM when OEM parts \
no longer exist.
- **Engine-first search patterns**: Heavy-duty, diesel, and commercial \
vehicle queries often identify by engine model ("Cummins ISX15") or \
component manufacturer rather than vehicle YMM. Treat engine/component \
identifiers as the primary fitment constraint for these queries.

#### Calibration examples

Query: "2019 Honda Civic front brake pads"
Result: "Ceramic front brake pad set, fits 2016–2021 Honda Civic"
→ Highly relevant (correct vehicle range, correct position, correct component)

Query: "2019 Honda Civic front brake pads"
Result: "Front brake pad set for 2019 Honda Accord"
→ Irrelevant (wrong vehicle model — Accord is not Civic; YMM mismatch \
is a hard disqualifier regardless of part similarity)""",
    overlays={
        "general": VerticalOverlay(
            description=(
                "Fallback / general automotive parts and accessories that do not "
                "cleanly fit a specialized overlay (still governed by core fitment rules)"
            ),
            content="""\
### General Automotive — Minimal Additional Guidance

Use this overlay when the query is automotive-related but does not strongly map to other overlays.

**Reinforce core priorities**:
- Exact fitment (YMM, engine/trans, position/side) and exact part numbers dominate.
- When a query specifies a hard spec (dimension, connector type, certification, chemistry), treat mismatches as disqualifiers.
""",
        ),
        "oil_change": VerticalOverlay(
            description=(
                "Engine oil service and oil filters: engine oil viscosity grades (0W-20, 5W-30), "
                "API/ILSAC/dexos approvals, oil change kits/bundles, engine oil filters (spin-on or cartridge), "
                "filter part numbers (e.g., PF63), drain plug gaskets/washers"
            ),
            content="""\
### Oil Change (Engine Oil + Oil Filter) — Scoring Guidance

This query involves engine oil, engine oil filters, or oil-change bundles/kits.

**Hard constraints (when present in the query):**

- **Viscosity grade is not optional**: If the query specifies a viscosity (e.g., 0W-20, 5W-30), results must match exactly.
- **Specification / approval codes are requirements**: If the query specifies an API category, ILSAC GF-6A/GF-6B, or an OEM approval (e.g., dexos), the product must explicitly claim that approval. Do not assume equivalency.
  - **GF-6B is a special case**: GF-6B applies only to SAE 0W-16 oils and is not a generic synonym for GF-6A.
- **Packaging and quantity**: 1 quart, 5-quart jug, gallon, case packs, and "oil change kit" are different buying intents. If the query asks for a kit/bundle, a result that includes only oil (or only a filter) is incomplete.

**Oil filter-specific fitment (treat as hard when the query is an oil filter):**

- **Exact filter part number dominates** (OEM or aftermarket). Close numbers often indicate different gaskets, bypass settings, or thread specs.
- **Spin-on vs cartridge**: These are different physical formats. If the query calls for a cartridge style (filter element + cap O-ring), a spin-on canister is wrong and vice versa.
- **Thread & gasket compatibility**: When the result provides thread size and gasket diameter, they must match the intended application. A mismatch can cause leaks, stripped threads, or no seal.
- **Anti-drainback valve (ADBV)**:
  - The ADBV prevents oil from draining out of the filter when the engine is off in many designs (often important when filters mount sideways or upside-down).
  - Treat ADBV as a hard constraint only when the query explicitly asks for it (or asks for an OE filter known for that feature). Otherwise, do not speculate.
- **Bypass valve**:
  - The bypass valve exists to protect the engine from oil starvation if the filter media is restricted.
  - Bypass can open when oil is cold/thick or the filter is clogged/restricted.
  - Treat bypass specification as a hard constraint only when the query explicitly calls it out (PSI) or when a specific OE filter spec is requested.

**Common category pitfalls (disqualify):**

- Returning oil additives or stop-leak products for a motor oil query (unless the query explicitly asks for additives).
- Returning transmission fluid, gear oil, or power steering fluid for an engine oil query.

**Terminology** (do not penalize synonym usage):
- "motor oil" = engine oil
- "full synthetic" vs "synthetic blend" vs "conventional" are distinct and should be enforced only when specified.
""",
        ),
        "fluids_and_chemicals": VerticalOverlay(
            description=(
                "Vehicle fluids and chemicals EXCEPT engine oil and oil filters: automatic transmission fluid (ATF), "
                "CVT fluid, gear oil (75W-90), differential/transfer-case fluid, coolant/antifreeze, brake fluid (DOT 3/4/5/5.1), "
                "power steering fluid, additives, sealers"
            ),
            content="""\
### Fluids and Chemicals (Non-Engine-Oil) — Scoring Guidance

This query involves vehicle fluids, chemicals, or service consumables other than engine oil/oil filters.

**Hard constraints (mismatches are disqualifiers):**

- **Exact fluid specification is the product**: If the query names a fluid spec (ATF+4, Dexron VI, Mercon LV, Toyota WS, CVT fluid, gear oil 75W-90, DOT 4, etc.), results must explicitly meet that same spec. Do not assume "multi-vehicle" fluids are compatible unless they explicitly list the requested spec.
- **CVT / DCT / manual vs conventional ATF**: CVT fluids and DCT fluids are not interchangeable with standard ATF. Confusing these is a hard failure.
- **Gear oil vs engine oil scales**: Gear oils (SAE J306, e.g., 75W-90) and engine oils (SAE J300, e.g., 5W-30) use different grade systems. Do not treat them as equivalent based on the numbers.
- **API GL ratings and friction modifiers (when specified)**:
  - If the query specifies API GL-4 vs GL-5 (or limited-slip / LS friction modifier), treat that as a hard requirement. Do not silently substitute.
- **Coolant must match the correct chemistry/spec**:
  - Coolant color is not a reliable compatibility guarantee.
  - If the query specifies an OEM spec (e.g., Ford WSS-...), a technology family (IAT/OAT/HOAT), or an OE brand family, results must explicitly match.
  - Concentrate vs 50/50 pre-diluted is a format constraint when specified.
- **Brake fluid DOT class is safety-critical**:
  - DOT 3 / DOT 4 / DOT 5.1 are glycol-based families; DOT 5 is silicone-based.
  - Do not treat DOT 5 as mixable/interchangeable with DOT 3/4/5.1.
  - If the query specifies DOT class, it is a hard requirement.

**Significant penalties:**

- **Generic / "universal" claims without the requested spec**: A generic "multi-vehicle ATF" that does not explicitly list the required spec is a poor match for a spec-request query.
- **Wrong intent**: Stop-leak, flush chemicals, and additives are not substitutes for the actual required fluid unless the query explicitly asks for them.

**Terminology notes (useful for classification and tiebreaking):**
- ATF = automatic transmission fluid
- "diff fluid" = differential gear oil (often 75W-90/75W-140, but follow the exact spec in query)
- "antifreeze" = coolant (still must match OEM spec, not just color)
""",
        ),
        "brakes_and_friction": VerticalOverlay(
            description=(
                "Brake system hardware and friction parts: brake pads, brake rotors/discs, brake calipers, "
                "brake drums, brake shoes, parking brake parts, brake kits (pad+rotor), brake lines/hoses "
                "(NOT brake fluid)"
            ),
            content="""\
### Brakes and Friction — Scoring Guidance

This query involves brake parts (pads, rotors, calipers, drums/shoes, parking brake parts, brake kits).

**Hard constraints:**

- **Disc vs drum is a category boundary**: Pads go with rotors (disc brakes). Shoes go with drums (drum brakes). Do not substitute across these.
- **Axle/position matters**: Front vs rear, left vs right (where applicable), and inner vs outer pads (in some caliper designs) are hard constraints when specified.
- **Brake package splits are common**: Rotor diameter, vented vs solid rotors, and caliper/bracket variants can differ within the same YMM (e.g., base vs sport trim, towing package). If the query includes rotor size, "big brake" wording, or a specific trim/package, enforce it.
- **Kit integrity**: A "pad + rotor kit" query expects both pads and rotors for the specified axle. Returning only pads or only rotors is incomplete.
- **Parking brake style**: Many rear rotors are "drum-in-hat" with an internal parking brake shoe. If the query calls out parking brake shoes/hardware, do not return disc pads.

**Brake-lining identification quirks (high-value signals if present in the query):**

- **Friction rating (two-letter code)**: Some pads carry a friction coefficient code such as EE/FF/GG. The two letters reflect "cold" and "hot" friction behavior. If the query includes a friction code, treat it as a constraint.
- **Pad shape codes (FMSI / D-number)**: A pad shape number like "D154" is an industry shape identifier. If the query includes it, matching that shape is a strong relevance signal.

**Significant penalties:**

- **Missing hardware vs hardware-included mismatch**: If the query says "hardware included" or "with clips/shims", prefer results that include the hardware kit. If the query is only for pads, do not penalize a pad-only listing.
- **Performance compound mismatches**: "Ceramic", "semi-metallic", "track", and "low-dust" are meaningful when specified. Do not treat them as interchangeable when explicitly requested.

**Common disqualifiers / critical errors:**

- Returning brake fluid for a pads/rotors query (unless the query explicitly asks for brake fluid).
- Returning "universal" racing pads for a street OEM pad query when the query clearly expects an OEM-style direct replacement.

**Terminology**:
- rotor = brake disc
- caliper bracket = mounting bracket / anchor bracket (often sold separately; match query scope)
""",
        ),
        "wheels_tires_tpms": VerticalOverlay(
            description=(
                "Wheels and tires: tire sizes (e.g., 225/45R17), service description (load index + speed rating like 94W), "
                "wheel sizes, bolt patterns/PCD, offsets (ET), center bore, lug nuts/bolts, spacers, TPMS sensors (315MHz/433MHz), "
                "directional/asymmetrical tires, run-flat"
            ),
            content="""\
### Wheels, Tires, and TPMS — Scoring Guidance

This query involves wheels/rims, tires, lug hardware, spacers, or TPMS sensors.

**Hard constraints (physical fitment):**

- **Tire size must match**: A tire size like 225/45R17 encodes width, aspect ratio, and wheel diameter. Mismatching any of these is wrong unless the query explicitly asks for alternatives ("plus size", "similar diameter").
- **Service description (load index + speed rating)**:
  - If the query specifies a service description (e.g., 94W) or minimum load/speed rating, enforce it. These relate to how much load a tire can carry and its tested maximum speed category.
- **Wheel bolt pattern / PCD**: 5x114.3 vs 5x112 are not compatible. Treat mismatch as disqualifying.
- **Center bore and hub-centricity**: A wheel must match the hub bore directly or explicitly include a centering ring solution. If the query specifies hub bore or "hub-centric", enforce it.
- **Offset/backspacing**: Offset controls clearance and steering/suspension geometry. If the query specifies offset/backspacing (common in fitment-focused wheel queries), enforce it.
- **Wheel diameter and width**: A 17x8 wheel is not a 17x7 wheel. When wheel size is specified, enforce both diameter and width.
- **Lug hardware thread pitch/seat type (when specified)**: E.g., M12x1.5 vs M12x1.25 and conical vs ball seat matter; treat mismatches as disqualifying when specified.

**Tire construction and orientation (enforce when specified):**

- **Directional tires**: Usually marked with an arrow / "rotation". They must be oriented correctly.
- **Asymmetrical tires**: Marked "inside/outside" and must be mounted with the correct side facing out.
- **Run-flat / XL / load range (SL vs XL vs LT)**: These are meaningful constraints when stated.

**TPMS-specific constraints:**

- **Frequency matters**: TPMS sensors commonly transmit at 315MHz or 433MHz. If the query specifies frequency, it is a hard requirement; the wrong frequency can prevent relearn/programming.
- **Direct-fit vs programmable**: OE-direct-fit sensors vs universal programmable sensors are different product intents. If the query asks for OE-direct-fit, treat "universal programmable" as a weaker match unless it explicitly supports the vehicle.

**Common disqualifiers:**

- Returning tires for a wheel query (or wheels for a tire query) unless the query asks for a wheel+tire package.
- Returning lug nuts/bolts with the wrong thread pitch or seat type when the query specifies them.

**Terminology**:
- PCD = bolt pattern
- offset is often written ET (e.g., ET35)
""",
        ),
        "batteries_starting_charging": VerticalOverlay(
            description=(
                "Battery and starting/charging: 12V car batteries (BCI group sizes like 35, 24F, H6/H7), "
                "AGM/EFB/start-stop batteries, terminal types (top post/side post), cold cranking amps (CCA), "
                "reserve capacity (RC), starters, alternators, battery cables/terminals"
            ),
            content="""\
### Batteries, Starting, and Charging — Scoring Guidance

This query involves a vehicle battery, starter, alternator, or battery/charging accessories.

**Hard constraints (battery fitment):**

- **BCI group size is physical fit + terminal layout**: Group size standardizes battery dimensions and terminal placement. A wrong group size is commonly a non-fit or unsafe cable routing.
- **Terminal type and orientation**:
  - Top-post vs side-post is a hard boundary when specified.
  - Terminal orientation matters; reversed orientation can cause cables not to reach or can create polarity hazards.
- **Battery chemistry/type when specified (especially start-stop)**:
  - Many start-stop vehicles are equipped with EFB or AGM batteries.
  - If the query specifies AGM or EFB, results must match that type. Do not downgrade AGM → flooded or AGM → EFB unless the query explicitly allows it.

**Hard constraints (electrical performance when specified):**

- **CCA rating**: If the query specifies a minimum CCA, enforce it. Higher CCA is generally acceptable as long as physical fitment and terminal layout match.
- **Voltage**: Automotive SLI batteries are typically 12V; if the query specifies 6V or 24V (special applications), it is a hard constraint.

**Starting/charging parts:**

- **Starter vs alternator**: These are not interchangeable categories. Do not score an alternator as relevant for a starter query or vice versa.
- **Remanufactured vs new**: If the query specifies new vs reman, enforce.

**Common disqualifiers / critical errors:**

- Returning a battery charger/jump starter for a "replacement battery" query (unless explicitly requested).
- Returning a battery with the wrong post type (side vs top) when the query is explicit.

**Terminology**:
- SLI = starting, lighting, ignition (standard 12V vehicle battery use case)
- AGM = absorbent glass mat (sealed lead-acid design, high cycle capability)
- EFB = enhanced flooded battery (improved cycle capability vs standard flooded; common for some start-stop systems)
- CCA is a standardized cold-start performance rating at low temperature
""",
        ),
        "lighting_and_visibility": VerticalOverlay(
            description=(
                "Lighting and visibility: headlight/fog/taillight bulbs (H11, 9005/HB3, etc), headlamp assemblies, "
                "turn signal bulbs, LED/HID/halogen types, DOT/SAE street-legal requirements, wiper blades (length + "
                "connector), washer components"
            ),
            content="""\
### Lighting and Visibility — Scoring Guidance

This query involves lighting products (bulbs, assemblies) and/or visibility items (wiper blades, washer parts).

**Lighting — hard constraints:**

- **Bulb type codes behave like part numbers**: Codes like H11, 9005, 9006, HB3 describe a specific base/connector and electrical spec. Treat mismatch as wrong.
  - **Equivalence note**: Some bulbs have recognized alternate designations (e.g., 9005 is commonly referenced as HB3). When the query uses either designation, a result using the equivalent naming is acceptable.
- **Location matters**: Low beam vs high beam vs fog vs DRL vs turn signal are different applications. If the query specifies location, enforce it.
- **Technology matters when specified**: Halogen vs HID vs LED are not interchangeable if explicitly requested.
- **Street legal / DOT / SAE claims (when requested)**:
  - If the query asks for DOT/SAE compliance or "street legal", require explicit compliance claims.
  - "Off-road only" results are not acceptable matches for legality-focused queries.

**Wiper blades — hard constraints:**

- **Length and position**: Driver vs passenger vs rear blade sizes differ. If the query specifies length (inches/mm) or position, enforce.
- **Attachment style**: Modern vehicles use multiple connector styles. If the query specifies connector type or "exact fit", universal-fit blades are weaker matches.
- **Beam vs conventional vs winter**: Treat as a preference unless the query explicitly requests a type.

**Common disqualifiers:**

- Returning a full headlamp assembly for a bulb-only query (or returning a bulb when the query is for a full headlight housing) unless the query is ambiguous.
- Returning unrelated "appearance lighting" (underglow, interior LED strips) for an OEM replacement bulb query.

**Terminology**:
- headlamp housing = headlight assembly = headlamp assembly (may include lens/reflector/projector; bulbs may be separate)
- DRL = daytime running light
""",
        ),
        "engine_ignition_and_sensors": VerticalOverlay(
            description=(
                "Engine ignition and sensors: spark plugs (gap/heat range), ignition coils (COP/coil pack), "
                "oxygen sensors (upstream/downstream, bank 1/2, sensor 1/2), air-fuel ratio sensors (wideband), "
                "MAF/MAP sensors, crank/cam sensors, knock sensors, fuel injectors, throttle body"
            ),
            content="""\
### Engine Ignition and Sensors — Scoring Guidance

This query involves spark plugs, ignition coils, engine management sensors, oxygen/air-fuel sensors, or related engine control components.

**Hard constraints:**

- **Exact part numbers dominate**: Sensors and ignition components are connector- and calibration-sensitive. If a query includes an OEM or aftermarket part number, enforce exact match or an explicit cross-reference.
- **Oxygen sensor position notation is not optional**:
  - **Upstream vs downstream**: Upstream is before the catalyst; downstream is after the catalyst in usual naming.
  - **Sensor 1 vs sensor 2**: Sensor 1 is typically upstream; sensor 2 is typically downstream.
  - **Bank 1 vs bank 2**: Bank 1 refers to the cylinder bank containing cylinder #1; bank 2 is the opposite bank.
  If the query specifies bank/sensor position (e.g., Bank 1 Sensor 2), returning a different position is wrong.
- **A/F ratio (wideband) vs conventional O2**:
  - Some vehicles use wideband air/fuel ratio sensors (often in the upstream position). Do not assume a conventional narrowband O2 sensor is interchangeable with an A/F ratio sensor when the query is explicit.
- **Spark plug specification (when specified)**:
  - **Heat range**: Heat range numbers are manufacturer-specific but meaningful. Enforce if the query specifies heat range or the exact plug part number.
  - **Gap**: If the query specifies a gap, treat it as a hard requirement; otherwise do not invent a gap spec and do not penalize "pre-gapped" listings.
- **Ignition architecture**: Coil-on-plug (COP) boots/individual coils are different from multi-output coil packs. Match the requested part class.

**Significant penalties:**

- Returning "universal" sensors that require splicing when the query implies a direct-fit plug-and-play sensor (vehicle-specific intent).
- Returning a different connector style or harness length when the query explicitly specifies it.

**Common disqualifiers:**

- Returning "downstream" sensor results for "upstream" queries (or vice versa).
- Returning unrelated exhaust parts (catalytic converters, mufflers) for a sensor query unless the query is broad and the result explicitly matches that intent.

**Terminology**:
- COP = coil-on-plug
- A/F sensor = air-fuel ratio sensor (often wideband)
- B1S1/B1S2 shorthand = Bank 1 Sensor 1 / Bank 1 Sensor 2
""",
        ),
        "suspension_steering_and_hubs": VerticalOverlay(
            description=(
                "Suspension and steering: shocks, struts, complete/loaded strut assemblies, springs, control arms, "
                "ball joints, tie rods (inner/outer), sway bar links/bushings, wheel bearings, hub assemblies, "
                "axles/CV joints"
            ),
            content="""\
### Suspension, Steering, and Hubs — Scoring Guidance

This query involves suspension/steering components or wheel-end hardware.

**Hard constraints:**

- **Shock vs strut is a category boundary**: Shocks and struts are different parts and are not interchangeable. If the query says strut, a shock absorber result is wrong and vice versa.
- **Loaded/complete strut assembly vs bare strut**: A complete/loaded strut assembly includes the coil spring and mount hardware. If the query asks for a complete/loaded assembly, a bare strut is incomplete.
- **Handed and position-specific parts**: Left vs right control arms, knuckles, hubs, CV axles, and some tie rods are side-specific. Enforce LH/RH and front/rear when specified.
- **Control arm vs ball joint scope**:
  - A control arm assembly may include bushings and sometimes a ball joint.
  - A ball joint alone is not a control arm.
  If the query asks for the full arm, returning only the ball joint is a scope mismatch.
- **Wheel bearing vs hub assembly scope**:
  - "Hub assembly" commonly means a complete unit (bearing + hub flange, and may incorporate ABS encoder features).
  - A press-in bearing is not the same as a full hub assembly.
  Match the query’s scope.
- **ABS encoder / tone ring compatibility (when specified)**:
  - Some wheel-end parts integrate or depend on a tone ring/encoder for ABS. If the query specifies ABS compatibility or sensor/encoder presence, enforce it.

**Significant penalties:**

- "Universal" coilover/aftermarket performance kits for an OEM replacement strut query unless the query clearly wants performance/adjustability.
- Missing included hardware when the query specifies mounts, bushings, or "with ball joint".

**Common disqualifiers:**

- Returning an alignment service kit or tools for a hard-parts query (unless explicitly requested).
- Returning sway-bar links for a control arm query (system-adjacent but wrong part).

**Terminology**:
- strut assembly = loaded strut = complete strut (typically includes spring + top mount)
- tie rod end usually means outer tie rod end; inner tie rod is a different part class
""",
        ),
        "exhaust_and_emissions": VerticalOverlay(
            description=(
                "Exhaust and emissions: catalytic converters (CARB/50-state), exhaust manifolds, headers, "
                "pipes, mufflers, resonators, EGR parts, EVAP/charcoal canisters, emission-legal replacements"
            ),
            content="""\
### Exhaust and Emissions — Scoring Guidance

This query involves exhaust hardware and/or emissions-control components.

**Hard constraints:**

- **Emissions legality (when specified)**:
  - If the query says CARB, California, or 50-state legal, the result must explicitly indicate CARB legality (commonly via a CARB Executive Order / EO reference).
  - "49-state legal" is not a match for a CARB/California query.
- **CARB converter application specificity**:
  - CARB-legal aftermarket catalytic converters are approved for specific vehicle applications. Treat "CARB EO present" as necessary but not sufficient: results should also be for the correct make/class/model-year range when the query is vehicle-specific.
  - When a product exposes label details, look for: EO number + converter part number + production date markings.
- **Direct-fit vs universal catalytic converters**:
  - Direct-fit converters are application-specific and typically match the OE connector/flange geometry.
  - Universal converters require welding/fabrication.
  Enforce direct-fit vs universal intent based on query wording.
- **Exhaust configuration constraints**: Pipe diameter, inlet/outlet orientation, and sensor port (O2 bung) locations are application-specific. If the query specifies any of these, treat mismatch as a disqualifier.
- **Upstream vs downstream emissions hardware scope**:
  - Catalytic converter is not an oxygen sensor.
  - Muffler/resonator is not a catalytic converter.
  Mixing these categories is a critical error.

**Significant penalties:**

- Mismatching "front" vs "rear" converter on multi-cat systems when the query is explicit.
- Returning "test pipe" or off-road-only parts for a street-legal/certified query.

**Common disqualifiers:**

- Returning a universal muffler for an OEM-direct-fit muffler query (unless the query explicitly asks for universal size).
- Returning emissions defeat devices or "O2 simulator" products for legality-focused queries.

**Terminology**:
- cat = catalytic converter
- EO = Executive Order (emissions exemption documentation in some contexts)
""",
        ),
        "hvac_air_conditioning": VerticalOverlay(
            description=(
                "HVAC and A/C: A/C compressors, condensers, evaporators, expansion valves/orifice tubes, "
                "refrigerant recharge kits, R-134a vs R-1234yf, A/C service fittings/quick couplers, "
                "A/C oils (PAG/POE), cabin climate parts"
            ),
            content="""\
### HVAC and Air Conditioning — Scoring Guidance

This query involves automotive HVAC / air conditioning parts or refrigerants.

**Hard constraints:**

- **Refrigerant type**: R-134a vs R-1234yf is a hard boundary. If the query specifies one, results for the other are wrong.
- **Unique service fittings / compatibility**:
  - Refrigerant systems use different service fittings/quick couplers to reduce the risk of cross-contamination.
  - If the query specifies a refrigerant system type (R-134a vs R-1234yf), require matching fittings/compatibility claims in service tools/hoses/adapters.
- **Component category matters**:
  - compressor ≠ condenser ≠ evaporator ≠ accumulator/drier ≠ expansion valve/orifice tube
  Do not treat adjacent components as substitutes.
- **Compressor oil type (when specified)**: PAG vs POE vs other specified oils are not interchangeable when explicitly requested (especially in hybrid/electric compressor contexts).

**Significant penalties:**

- "Universal" hoses or fittings that require custom fabrication when the query implies an OE-direct-fit replacement.
- Returning stop-leak products for a refrigerant query unless explicitly asked.

**Common disqualifiers:**

- Returning a refrigerant can for a mechanical component query and vice versa unless the query explicitly asks for both.
""",
        ),
        "body_collision_paint_glass": VerticalOverlay(
            description=(
                "Body, collision, and exterior fitment: bumpers, bumper covers, fenders, grilles, mirrors, "
                "door handles, trim, pre-painted parts, paint codes (EXT PNT), CAPA-certified collision parts, "
                "automotive glass/glazing (AS1/AS2/AS3, DOT markings)"
            ),
            content="""\
### Body, Collision, Paint, and Glass — Scoring Guidance

This query involves body panels, exterior trim, mirrors, paint-matched parts, or automotive glazing.

**Hard constraints:**

- **Paint state and paint code**:
  - Pre-painted, primed, and raw/unpainted parts are different products. Match the query’s requested finish.
  - If a query specifies a paint code (or implies OEM color match), a different paint code/color is wrong.
- **CAPA / certified collision parts (when specified)**:
  - If the query explicitly asks for CAPA-certified parts, require explicit CAPA certification evidence; do not assume "CAPA" from generic marketing language.
- **Mirror feature splits**: Heated vs non-heated, power fold, memory, blind-spot indicator, turn signal, puddle light, and camera features are hard constraints when specified.
- **Glazing classifications and markings**:
  - If the query specifies AS1/AS2/AS3 or DOT markings for glazing, enforce them.
  - Windshields are a special case: if the query is explicitly for a windshield and requires a particular AS marking, enforce it strictly.

**Significant penalties:**

- Missing required included hardware (clips, brackets) when the query is explicit. Do not penalize missing hardware when the listing is clearly panel-only and the query did not ask for hardware.
- OEM vs aftermarket: When the query says OEM/genuine, penalize aftermarket panels; when the query is cost-focused, do not overvalue OEM.

**Common disqualifiers:**

- Returning an unrelated cosmetic accessory (stickers, universal trim) for a structural collision part query.
- Returning a different body style panel (sedan vs hatchback vs wagon) when the query implies a body style.

**Terminology**:
- bumper cover = bumper fascia (often plastic outer skin; may not include reinforcement)
- grille assembly may include emblem mounts and camera provisions; treat such features as hard when specified
""",
        ),
        "accessories_and_tools": VerticalOverlay(
            description=(
                "General accessories, interior/exterior add-ons, detailing, towing, and tools: floor mats/cargo liners, "
                "seat covers, roof racks, trailer hitches (receiver sizes 1-1/4, 2, 2-1/2, 3 inch), cargo carriers, "
                "OBD-II scan tools/code readers, jacks/garage tools, cleaning products"
            ),
            content="""\
### Accessories and Tools — Scoring Guidance

This query involves automotive accessories, towing hardware, tools/garage items, or detailing products.

**Hard constraints (when specified):**

- **Vehicle-specific vs universal fit**:
  - Many accessories are custom-fit (floor mats, seat covers, window deflectors, roof racks, many hitches).
  - If the query includes a Y/M/M or a specific vehicle, treat "custom-fit" compatibility as critical. Universal-fit accessories are weaker unless the query explicitly wants universal.
- **Scope of a set**: "Front row only" vs "full set" vs "cargo liner" are different. If the query specifies row coverage or cargo area coverage, treat mismatches as major errors.

**Towing / hitch-specific constraints:**

- **Receiver size is a hard boundary**: Standard trailer hitch receiver sizes include 1-1/4", 2", 2-1/2" and 3". If the query specifies receiver size, enforce it.
- **Hitch class and capacity (when specified)**: Class and tongue weight / GTW ratings matter. Do not treat a lower class hitch as a match for a higher-capacity intent.
- **Adapters change capacity**: If the query includes an adapter (e.g., 1-1/4" to 2"), reduced capacity and torque limitations are part of the intent; prefer results that explicitly address these constraints.

**Tools / diagnostics constraints:**

- **OBD-II compatibility is not just a plug shape**:
  - OBD-II vehicles can use multiple communication protocols (e.g., SAE J1850 PWM/VPW, ISO 9141-2, ISO 14230-4, and ISO 15765-4 CAN).
  - If the query specifies OBD-II support or specific protocols, require explicit support claims.
- **Consumable vs tool**: Do not return a tool for a consumable query or vice versa (e.g., detailing chemicals vs polishing machine) unless ambiguity exists.

**Common disqualifiers:**

- Returning decorative items for functional tool queries (or vice versa).
- Returning trailer balls / ball mounts when the query is for a receiver hitch, unless the query explicitly asks for the full towing setup.

**Terminology**:
- GTW = gross trailer weight
- TW = tongue weight
""",
        ),
    },
)
