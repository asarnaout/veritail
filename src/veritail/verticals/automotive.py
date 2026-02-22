"""Automotive vertical context for LLM judge guidance."""

from veritail.prompts import load_prompt
from veritail.types import VerticalContext, VerticalOverlay

AUTOMOTIVE = VerticalContext(
    core=load_prompt("verticals/automotive/core.md"),
    overlays={
        "general": VerticalOverlay(
            description=(
                "Fallback / general automotive parts and accessories that do not "
                "cleanly fit a specialized overlay (still governed by core fitment "
                "rules)"
            ),
            content=load_prompt("verticals/automotive/overlays/general.md"),
        ),
        "oil_change": VerticalOverlay(
            description=(
                "Engine oil service and oil filters: engine oil viscosity grades "
                "(0W-20, 5W-30), API/ILSAC/dexos approvals, oil change kits/bundles, "
                "engine oil filters (spin-on or cartridge), filter part numbers (e.g., "
                "PF63), drain plug gaskets/washers"
            ),
            content=load_prompt("verticals/automotive/overlays/oil_change.md"),
        ),
        "fluids_and_chemicals": VerticalOverlay(
            description=(
                "Vehicle fluids and chemicals EXCEPT engine oil and oil filters: "
                "automatic transmission fluid (ATF), CVT fluid, gear oil (75W-90), "
                "differential/transfer-case fluid, coolant/antifreeze, brake fluid "
                "(DOT 3/4/5/5.1), power steering fluid, additives, sealers"
            ),
            content=load_prompt(
                "verticals/automotive/overlays/fluids_and_chemicals.md"
            ),
        ),
        "brakes_and_friction": VerticalOverlay(
            description=(
                "Brake system hardware and friction parts: brake pads, brake "
                "rotors/discs, brake calipers, brake drums, brake shoes, parking brake "
                "parts, brake kits (pad+rotor), brake lines/hoses (NOT brake fluid)"
            ),
            content=load_prompt("verticals/automotive/overlays/brakes_and_friction.md"),
        ),
        "wheels_tires_tpms": VerticalOverlay(
            description=(
                "Wheels and tires: tire sizes (e.g., 225/45R17), service description "
                "(load index + speed rating like 94W), wheel sizes, bolt patterns/PCD, "
                "offsets (ET), center bore, lug nuts/bolts, spacers, TPMS sensors "
                "(315MHz/433MHz), directional/asymmetrical tires, run-flat"
            ),
            content=load_prompt("verticals/automotive/overlays/wheels_tires_tpms.md"),
        ),
        "batteries_starting_charging": VerticalOverlay(
            description=(
                "Battery and starting/charging: 12V car batteries (BCI group sizes "
                "like 35, 24F, H6/H7), AGM/EFB/start-stop batteries, terminal types "
                "(top post/side post), cold cranking amps (CCA), reserve capacity "
                "(RC), starters, alternators, battery cables/terminals"
            ),
            content=load_prompt(
                "verticals/automotive/overlays/batteries_starting_charging.md"
            ),
        ),
        "lighting_and_visibility": VerticalOverlay(
            description=(
                "Lighting and visibility: headlight/fog/taillight bulbs (H11, "
                "9005/HB3, etc), headlamp assemblies, turn signal bulbs, "
                "LED/HID/halogen types, DOT/SAE street-legal requirements, wiper "
                "blades (length + connector), washer components"
            ),
            content=load_prompt(
                "verticals/automotive/overlays/lighting_and_visibility.md"
            ),
        ),
        "engine_ignition_and_sensors": VerticalOverlay(
            description=(
                "Engine ignition and sensors: spark plugs (gap/heat range), ignition "
                "coils (COP/coil pack), oxygen sensors (upstream/downstream, bank 1/2, "
                "sensor 1/2), air-fuel ratio sensors (wideband), MAF/MAP sensors, "
                "crank/cam sensors, knock sensors, fuel injectors, throttle body"
            ),
            content=load_prompt(
                "verticals/automotive/overlays/engine_ignition_and_sensors.md"
            ),
        ),
        "suspension_steering_and_hubs": VerticalOverlay(
            description=(
                "Suspension and steering: shocks, struts, complete/loaded strut "
                "assemblies, springs, control arms, ball joints, tie rods "
                "(inner/outer), sway bar links/bushings, wheel bearings, hub "
                "assemblies, axles/CV joints"
            ),
            content=load_prompt(
                "verticals/automotive/overlays/suspension_steering_and_hubs.md"
            ),
        ),
        "exhaust_and_emissions": VerticalOverlay(
            description=(
                "Exhaust and emissions: catalytic converters (CARB/50-state), exhaust "
                "manifolds, headers, pipes, mufflers, resonators, EGR parts, "
                "EVAP/charcoal canisters, emission-legal replacements"
            ),
            content=load_prompt(
                "verticals/automotive/overlays/exhaust_and_emissions.md"
            ),
        ),
        "hvac_air_conditioning": VerticalOverlay(
            description=(
                "HVAC and A/C: A/C compressors, condensers, evaporators, expansion "
                "valves/orifice tubes, refrigerant recharge kits, R-134a vs R-1234yf, "
                "A/C service fittings/quick couplers, A/C oils (PAG/POE), cabin "
                "climate parts"
            ),
            content=load_prompt(
                "verticals/automotive/overlays/hvac_air_conditioning.md"
            ),
        ),
        "body_collision_paint_glass": VerticalOverlay(
            description=(
                "Body, collision, and exterior fitment: bumpers, bumper covers, "
                "fenders, grilles, mirrors, door handles, trim, pre-painted parts, "
                "paint codes (EXT PNT), CAPA-certified collision parts, automotive "
                "glass/glazing (AS1/AS2/AS3, DOT markings)"
            ),
            content=load_prompt(
                "verticals/automotive/overlays/body_collision_paint_glass.md"
            ),
        ),
        "accessories_and_tools": VerticalOverlay(
            description=(
                "General accessories, interior/exterior add-ons, detailing, towing, "
                "and tools: floor mats/cargo liners, seat covers, roof racks, trailer "
                "hitches (receiver sizes 1-1/4, 2, 2-1/2, 3 inch), cargo carriers, "
                "OBD-II scan tools/code readers, jacks/garage tools, cleaning products"
            ),
            content=load_prompt(
                "verticals/automotive/overlays/accessories_and_tools.md"
            ),
        ),
    },
)
