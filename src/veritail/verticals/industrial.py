"""Industrial vertical context for LLM judge guidance."""

from veritail.prompts import load_prompt
from veritail.types import VerticalContext, VerticalOverlay

INDUSTRIAL = VerticalContext(
    core=load_prompt("verticals/industrial/core.md"),
    overlays={
        "fasteners": VerticalOverlay(
            description=(
                "Threaded fasteners: bolts, screws, nuts, washers, threaded rod, "
                "studs, anchors, rivets, retaining rings, pins — any item defined "
                "primarily by thread size, grade, and material"
            ),
            content=load_prompt("verticals/industrial/overlays/fasteners.md"),
        ),
        "bearings": VerticalOverlay(
            description=(
                "Bearings: ball bearings, roller bearings, needle bearings, thrust "
                "bearings, mounted bearings (pillow blocks, flanges), bearing inserts, "
                "linear bearings — any rotary or linear bearing product"
            ),
            content=load_prompt("verticals/industrial/overlays/bearings.md"),
        ),
        "power_transmission": VerticalOverlay(
            description=(
                "Power transmission: V-belts, timing belts, roller chains, sprockets, "
                "gears, sheaves/pulleys, couplings, keystock — mechanical drive "
                "components (not motors or drives)"
            ),
            content=load_prompt("verticals/industrial/overlays/power_transmission.md"),
        ),
        "hydraulic_fittings_hose": VerticalOverlay(
            description=(
                "Hydraulic fittings and hose: JIC fittings, SAE fittings, ORFS "
                "fittings, ORB fittings, hydraulic adapters, hydraulic hose "
                "assemblies, hose ends, quick-disconnect couplings for hydraulic "
                "systems (not pipe fittings or pneumatic)"
            ),
            content=load_prompt(
                "verticals/industrial/overlays/hydraulic_fittings_hose.md"
            ),
        ),
        "pneumatic": VerticalOverlay(
            description=(
                "Pneumatic components: push-to-connect fittings, pneumatic tubing, air "
                "cylinders, pneumatic valves (solenoid, manual), FRLs "
                "(filter-regulator-lubricators), air preparation, pneumatic "
                "quick-connect couplings (not hydraulic fittings)"
            ),
            content=load_prompt("verticals/industrial/overlays/pneumatic.md"),
        ),
        "electrical": VerticalOverlay(
            description=(
                "Electrical wire, cable, conduit, connectors, terminals, enclosures, "
                "fuses, circuit breakers, disconnect switches, relays, terminal "
                "blocks, and wiring accessories — electrical distribution and wiring "
                "components (not motors or drives)"
            ),
            content=load_prompt("verticals/industrial/overlays/electrical.md"),
        ),
        "motors_drives": VerticalOverlay(
            description=(
                "Electric motors, variable frequency drives (VFDs), motor starters, "
                "contactors, overload relays, soft starters, and servo motors/drives — "
                "rotating electrical machinery and motor control (not general "
                "electrical wiring or enclosures)"
            ),
            content=load_prompt("verticals/industrial/overlays/motors_drives.md"),
        ),
        "pipe_valves_fittings": VerticalOverlay(
            description=(
                "Pipe, valves, and pipe fittings: steel/stainless/PVC pipe, gate "
                "valves, ball valves, globe valves, check valves, butterfly valves, "
                "pipe fittings (elbows, tees, unions, couplings), flanges, strainers, "
                "and steam traps — piping system components (not hydraulic fittings)"
            ),
            content=load_prompt(
                "verticals/industrial/overlays/pipe_valves_fittings.md"
            ),
        ),
        "pumps": VerticalOverlay(
            description=(
                "Pumps: centrifugal pumps, positive displacement pumps (gear, "
                "diaphragm, peristaltic, piston), sump pumps, submersible pumps, "
                "booster pumps, chemical pumps, and pump accessories"
            ),
            content=load_prompt("verticals/industrial/overlays/pumps.md"),
        ),
        "ppe_head_eye_face": VerticalOverlay(
            description=(
                "Head, eye, and face PPE: hard hats, safety helmets, safety glasses, "
                "safety goggles, face shields, welding helmets, hearing protection "
                "(earplugs, earmuffs) — personal protective equipment for head, eyes, "
                "ears, and face"
            ),
            content=load_prompt("verticals/industrial/overlays/ppe_head_eye_face.md"),
        ),
        "ppe_hand": VerticalOverlay(
            description=(
                "Hand protection: cut-resistant gloves, chemical-resistant gloves, "
                "heat-resistant gloves, general-purpose work gloves, disposable gloves "
                "(nitrile, latex, vinyl), leather gloves — all work gloves (not "
                "electrical insulating gloves; see ppe_arc_flash_fr)"
            ),
            content=load_prompt("verticals/industrial/overlays/ppe_hand.md"),
        ),
        "ppe_arc_flash_fr": VerticalOverlay(
            description=(
                "Arc flash PPE, FR clothing, electrical safety: arc-rated suits, FR "
                "shirts/pants/coveralls, electrical insulating gloves (voltage-rated), "
                "arc flash face shields, electrical safety kits, hi-vis vests and "
                "garments — NFPA 70E and electrical PPE"
            ),
            content=load_prompt("verticals/industrial/overlays/ppe_arc_flash_fr.md"),
        ),
        "ppe_respiratory_foot": VerticalOverlay(
            description=(
                "Respiratory protection and safety footwear: N95 respirators, "
                "half-face and full-face respirators, PAPR systems, filter cartridges, "
                "safety-toe boots and shoes, metatarsal guards, EH-rated footwear"
            ),
            content=load_prompt(
                "verticals/industrial/overlays/ppe_respiratory_foot.md"
            ),
        ),
        "welding": VerticalOverlay(
            description=(
                "Welding: stick electrodes, MIG wire, TIG filler rod, flux-core wire, "
                "shielding gas, welding machines, welding helmets, welding "
                "accessories, solder — welding consumables, equipment, and supplies"
            ),
            content=load_prompt("verticals/industrial/overlays/welding.md"),
        ),
        "cutting_tools": VerticalOverlay(
            description=(
                "Cutting tools and toolholding: indexable inserts, drill bits, end "
                "mills, taps, reamers, saw blades, toolholders, collets, tool arbors — "
                "metalworking and machining tooling"
            ),
            content=load_prompt("verticals/industrial/overlays/cutting_tools.md"),
        ),
        "abrasives": VerticalOverlay(
            description=(
                "Abrasives: grinding wheels, cut-off wheels, flap discs, sanding "
                "discs, sanding belts, sandpaper, deburring tools, wire wheels — "
                "coated and bonded abrasive products"
            ),
            content=load_prompt("verticals/industrial/overlays/abrasives.md"),
        ),
        "adhesives_sealants": VerticalOverlay(
            description=(
                "Adhesives, sealants, and tapes: threadlockers, retaining compounds, "
                "epoxies, cyanoacrylates, silicone sealants, construction adhesives, "
                "thread sealant tape, pipe dope, gasket makers — bonding and sealing "
                "products (not o-rings or cut gaskets)"
            ),
            content=load_prompt("verticals/industrial/overlays/adhesives_sealants.md"),
        ),
        "lubrication": VerticalOverlay(
            description=(
                "Lubrication: grease, hydraulic oil, gear oil, machine oil, compressor "
                "oil, chain lubricant, penetrating oil, dry lubricant, grease guns, "
                "oil cans — lubricants and lubrication tools"
            ),
            content=load_prompt("verticals/industrial/overlays/lubrication.md"),
        ),
        "seals_gaskets_orings": VerticalOverlay(
            description=(
                "Seals, gaskets, and o-rings: o-rings (AS568 dash sizes), oil seals, "
                "shaft seals, mechanical seals, gasket material/sheets, spiral wound "
                "gaskets, packing, V-rings — sealing components (not adhesive sealants)"
            ),
            content=load_prompt(
                "verticals/industrial/overlays/seals_gaskets_orings.md"
            ),
        ),
        "material_handling": VerticalOverlay(
            description=(
                "Material handling: hoists, slings (wire rope, chain, synthetic), "
                "shackles, turnbuckles, casters, hand trucks, pallet jacks, shelving, "
                "workbenches, lifting magnets, come-alongs — lifting, rigging, "
                "transport, and storage equipment"
            ),
            content=load_prompt("verticals/industrial/overlays/material_handling.md"),
        ),
        "test_measurement": VerticalOverlay(
            description=(
                "Test and measurement: multimeters, clamp meters, pressure gauges, "
                "thermometers, calipers, micrometers, torque wrenches, calibration "
                "equipment, thermal cameras, vibration analyzers — measurement "
                "instruments and tools"
            ),
            content=load_prompt("verticals/industrial/overlays/test_measurement.md"),
        ),
        "raw_materials": VerticalOverlay(
            description=(
                "Raw materials and stock: steel bar/plate/sheet/tube, aluminum "
                "bar/plate/sheet/extrusions, stainless steel stock, brass/copper "
                "stock, plastic sheet/rod/tube (UHMW, Delrin, nylon, PTFE), rubber "
                "sheet — metal and plastic raw material stock"
            ),
            content=load_prompt("verticals/industrial/overlays/raw_materials.md"),
        ),
    },
)
