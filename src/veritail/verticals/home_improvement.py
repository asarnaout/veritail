"""Home improvement vertical context for LLM judge guidance."""

from veritail.prompts import load_prompt
from veritail.types import VerticalContext, VerticalOverlay

HOME_IMPROVEMENT = VerticalContext(
    core=load_prompt("verticals/home_improvement/core.md"),
    overlays={
        "electrical_lighting": VerticalOverlay(
            description=(
                "Electrical & Lighting — wiring (cables, conduit), outlets, switches, "
                "breakers, panels, and light fixtures (indoor/outdoor, bulbs)."
            ),
            content=load_prompt(
                "verticals/home_improvement/overlays/electrical_lighting.md"
            ),
        ),
        "plumbing": VerticalOverlay(
            description=(
                "Plumbing — pipes and fittings (PVC, CPVC, PEX, copper), valves, "
                "faucets, toilets, drains, water heaters, and pumps."
            ),
            content=load_prompt("verticals/home_improvement/overlays/plumbing.md"),
        ),
        "flooring": VerticalOverlay(
            description=(
                "Flooring — hardwood, engineered wood, laminate, luxury vinyl planks, "
                "vinyl sheet/tile, ceramic/porcelain tile, carpet, and area rugs."
            ),
            content=load_prompt("verticals/home_improvement/overlays/flooring.md"),
        ),
        "building_materials": VerticalOverlay(
            description=(
                "Building Materials — lumber (studs, beams, plywood, OSB), drywall, "
                "sheathing, siding, and framing hardware."
            ),
            content=load_prompt(
                "verticals/home_improvement/overlays/building_materials.md"
            ),
        ),
        "tools_equipment": VerticalOverlay(
            description=(
                "Tools — hand tools and power tools (drills, saws, wrenches, hammers, "
                "etc.), and related accessories (blades, bits, batteries, chargers)."
            ),
            content=load_prompt(
                "verticals/home_improvement/overlays/tools_equipment.md"
            ),
        ),
        "doors_windows": VerticalOverlay(
            description=(
                "Doors & Windows — interior/exterior doors (pre-hung or slab), door "
                "hardware, and window units (double-hung, casement, sliding), plus "
                "skylights."
            ),
            content=load_prompt("verticals/home_improvement/overlays/doors_windows.md"),
        ),
        "paint_finishes": VerticalOverlay(
            description=(
                "Paint & Finishes — interior/exterior paint, primer, stain, sealers, "
                "and painting tools/accessories."
            ),
            content=load_prompt(
                "verticals/home_improvement/overlays/paint_finishes.md"
            ),
        ),
        "hvac": VerticalOverlay(
            description=(
                "HVAC — heating, ventilation, and air conditioning equipment "
                "(furnaces, AC units, heat pumps), ducting, vents, filters, and "
                "thermostats."
            ),
            content=load_prompt("verticals/home_improvement/overlays/hvac.md"),
        ),
        "kitchen_bath": VerticalOverlay(
            description=(
                "Kitchen & Bath — kitchen appliances (refrigerators, ranges, "
                "dishwashers, ovens), sinks, faucets, cabinets, vanities, and bathroom "
                "fixtures (toilets, tubs, showers)."
            ),
            content=load_prompt("verticals/home_improvement/overlays/kitchen_bath.md"),
        ),
        "outdoor_garden": VerticalOverlay(
            description=(
                "Outdoor & Garden — grills, patio furniture, fencing, decking, lawn "
                "mowers, garden tools, outdoor lighting, and irrigation."
            ),
            content=load_prompt(
                "verticals/home_improvement/overlays/outdoor_garden.md"
            ),
        ),
    },
)
