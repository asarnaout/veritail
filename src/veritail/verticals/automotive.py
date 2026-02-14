"""Automotive vertical context for LLM judge guidance."""

AUTOMOTIVE = """\
## Vertical: Automotive Parts

You are evaluating search results for an automotive parts and accessories \
ecommerce site. Think like a composite buyer spanning the professional \
mechanic sourcing an OEM replacement during a teardown, the collision-repair \
estimator matching CAPA-certified body panels to an insurance supplement, \
the fleet manager cross-referencing interchange numbers across a mixed-make \
fleet, and the DIY enthusiast upgrading brakes on a weekend project. In \
automotive parts, fitment is everything — a part that does not fit the \
buyer's exact vehicle is not a close match, it is a return, a core charge \
dispute, or a car stranded on a lift. Year, make, model, and sub-model \
precision outweighs brand preference, price, or cosmetic similarity.

### Scoring considerations

- **Year/Make/Model fitment as the primary hard gate**: When the query \
specifies or strongly implies a vehicle application — by YMM ("2019 Honda \
Civic"), platform code ("FK7"), or generation ("10th gen Civic") — every \
result must fit that exact application or receive a major relevance penalty. \
Sub-model and trim matter: a Civic Si uses different suspension and brake \
components than a base Civic. Engine and transmission options within the \
same model year create further splits — a 2019 Civic 1.5T needs different \
motor mounts than the 2.0L. Treat YMM mismatches with the same severity \
that industrial supply treats wrong thread pitch — an immediate disqualifier.
- **Part number precision and cross-reference validity**: Exact OEM part \
number matches are the strongest relevance signal. Automotive has a dense \
web of numbering — OEM numbers (Honda 45022-TBA-A01), aftermarket catalog \
numbers (Raybestos EHT1578H), interchange numbers, and supersession chains. \
Near-miss part numbers (wrong suffix, different revision) are usually \
different parts — a suffix change often signals revised material, updated \
connector, or changed mounting point. Cross-referenced equivalents are \
acceptable only when explicitly validated as direct replacements.
- **VIN-level specificity and option-package sensitivity**: Within a single \
YMM, production options create dozens of part variations. Engine code \
(2.0L vs 5.7L HEMI), transmission type (manual vs auto vs CVT), drive \
configuration (2WD vs 4WD/AWD), brake package (standard vs Brembo), \
suspension type (standard vs MagneRide vs air), body style, and \
production-date splits (mid-year running changes) all determine fitment. \
When a query includes engine codes, RPO codes, or transmission identifiers, \
treat these as hard constraints with the same weight as YMM.
- **OEM vs aftermarket vs remanufactured distinction**: These represent \
different product tiers with different buyer intents. OEM parts carry \
exact-fit assurance. OE-supplier brands (Denso, Bosch, Aisin, ZF) that \
manufacture for automakers are near-OEM quality. Aftermarket ranges from \
premium (Moog, Raybestos, ACDelco Professional) to economy (Dorman, \
house brands) with varying fitment precision. Remanufactured parts \
(alternators, starters, calipers, steering racks) are rebuilt cores. When \
a query specifies "OEM" or "genuine," aftermarket results are relevance \
penalties. When a query signals budget intent, OEM parts at 3x the price \
are poor matches. Remanufactured parts match replacement intent but not \
new-OEM intent.
- **Side-specific and directional disambiguation**: Many automotive parts \
are handed — left (driver side, LH) vs right (passenger side, RH) for \
US-market vehicles. Headlights, fenders, mirrors, control arms, axle \
shafts, and tie rod ends are commonly side-specific. Returning a right-side \
headlight for a left-side query is the wrong part entirely. Upper vs lower \
(control arms, radiator hoses, ball joints) and front vs rear (brake pads, \
shocks, sway bar links) are equally critical directional constraints. When \
the query specifies position, treat it as a hard filter.
- **Emissions compliance and regulatory constraints**: Catalytic converters, \
oxygen sensors, and EGR valves are subject to CARB and EPA regulations. \
CARB-compliant ("50-state legal") parts are required in California and \
Section 177 states; federal-only parts are illegal there. Queries mentioning \
California, CARB, or 50-state legality require CARB-EO-numbered results. \
Performance parts (headers, intakes, tunes) carry similar distinctions — a \
cold-air intake with a CARB EO number is materially different from one \
without. DOT compliance for lighting and FMVSS compliance for safety glass \
are additional hard regulatory constraints.
- **Vehicle system and component-level disambiguation**: Automotive systems \
contain many distinct components sharing category keywords. "Brakes" could \
mean pads, rotors, calipers, lines, master cylinder, or a complete kit. \
"Suspension" could mean struts, shocks, springs, control arms, ball joints, \
or sway bar links. When the query specifies a component, other components \
in the same system are weak matches. When the query uses only the system \
name, the most commonly replaced wear component (pads for brakes, plugs \
for ignition) is the strongest default, but results should not be dominated \
by tangential parts like ABS sensors or brake fluid reservoirs.
- **Certification and quality-tier signals**: Collision and safety parts \
carry certifications that function as hard constraints for professional \
buyers. CAPA certification is required by many insurers for aftermarket \
body panels. NSF certification applies to aftermarket brake components. DOT \
markings are legally required for on-road lighting. FMVSS 205 governs \
safety glass. SAE ratings apply to oils, coolants, and brake fluids. \
Professional shops searching for certified parts expect results carrying \
those certifications — uncertified alternatives are weaker matches even at \
lower prices.
- **Kit vs individual component intent**: A "brake job kit" or "timing belt \
kit" query expects a bundled set (pads + rotors, or belt + tensioner + \
water pump + idler pulleys). Returning only pads for a kit query is \
incomplete. Conversely, "front brake pads" expects pads only — a full kit \
at 3x the price over-serves the buyer. Gasket sets vs individual gaskets, \
tune-up kits vs individual plugs, and seal kits vs individual seals follow \
the same pattern. Match the query's scope precisely.
- **Professional installer vs DIY intent signals**: Professionals search by \
part number, OEM reference, or terse category-plus-application queries \
("water pump 5.3 Silverado"), expect case pricing, and value torque specs \
and connector pinouts. DIY buyers use plain-language descriptions and value \
installation guides and difficulty indicators. When the query signals \
professional intent (part numbers, trade abbreviations like "LCA" for lower \
control arm, "PS pump" for power steering pump), prioritize specification \
depth over consumer-friendly presentation.
- **Brand hierarchy as specification, not preference**: In automotive, brand \
encodes quality tier and engineering origin. OE-supplier brands (Denso, \
Bosch, NGK, Aisin, ZF, Brembo, KYB) manufactured the original part for \
the automaker. Professional-grade aftermarket (Moog, Raybestos, ACDelco, \
Motorcraft, Mopar) carries strong trade reputation. Economy brands may \
differ in materials, tolerances, or included hardware. When a query names \
a brand alongside a part category, treat it as a hard constraint. When \
brand is omitted, do not penalize any tier — but do not rank a budget part \
equally with an OE-supplier part when both match fitment.
- **Superseded, discontinued, and NLA part handling**: Automotive parts are \
frequently superseded, discontinued by the OEM, or NLA (No Longer \
Available). When a query references a superseded part number, the current \
replacement is a strong match if identified as the direct supersession. \
Aftermarket equivalents for discontinued OEM parts are valid when fitment \
is confirmed. For classic and vintage vehicles, NLA OEM status is expected \
— reproduction, NOS (New Old Stock), and quality aftermarket alternatives \
are all valid, and results should not be penalized solely for being \
non-OEM on vehicles whose OEM parts no longer exist."""
