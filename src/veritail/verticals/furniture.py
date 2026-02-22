"""Furniture vertical context for LLM judge guidance."""

from veritail.prompts import load_prompt
from veritail.types import VerticalContext, VerticalOverlay

FURNITURE = VerticalContext(
    core=load_prompt("verticals/furniture/core.md"),
    overlays={
        "sofas_sectionals": VerticalOverlay(
            description=(
                "Living-room upholstered seating: sofas/couches, loveseats, "
                "sectionals, modular sofas, chaises (stationary). Includes LAF/RAF and "
                "left/right chaise orientation, upholstery material terms, and "
                "abrasion/durability specs. Excludes recliners/lift chairs and sleeper "
                "mechanisms."
            ),
            content=load_prompt("verticals/furniture/overlays/sofas_sectionals.md"),
        ),
        "motion_seating": VerticalOverlay(
            description=(
                "Reclining and motion seating: recliners, power recliners, lift "
                "chairs, reclining sofas/sectionals, home-theater seating. Includes "
                "wall-hugger/zero-wall terminology, swivel/rocker/glider distinctions, "
                "and power-feature requirements."
            ),
            content=load_prompt("verticals/furniture/overlays/motion_seating.md"),
        ),
        "sleepers_daybeds_futons": VerticalOverlay(
            description=(
                "Convertible sleep furniture: sleeper sofas/sofa beds, futons, "
                "daybeds, trundles, Murphy beds, and replacement sofa-bed mattresses. "
                "Includes sleeper-mattress sizing quirks (e.g., many 'queen' sofa-bed "
                "mattresses are shorter than standard Queen)."
            ),
            content=load_prompt(
                "verticals/furniture/overlays/sleepers_daybeds_futons.md"
            ),
        ),
        "beds_frames_headboards": VerticalOverlay(
            description=(
                "Bed furniture (not mattresses): bed frames, platform beds, "
                "headboards/footboards, storage beds, canopy beds, rails, slats, and "
                "foundations/box springs. Includes bed-size dimension norms, and "
                "platform/no-box-spring vs box-spring-required distinctions."
            ),
            content=load_prompt(
                "verticals/furniture/overlays/beds_frames_headboards.md"
            ),
        ),
        "mattresses_toppers_bases": VerticalOverlay(
            description=(
                "Mattresses and sleep surfaces: mattresses by size/firmness/type, "
                "mattress toppers, mattress-in-a-box, and adjustable bases. Includes "
                "standard U.S. mattress size dimensions, U.S. flammability compliance "
                "language (16 CFR 1632/1633), and foam certification terms "
                "(CertiPUR-US, GREENGUARD Gold)."
            ),
            content=load_prompt(
                "verticals/furniture/overlays/mattresses_toppers_bases.md"
            ),
        ),
        "casegoods_storage": VerticalOverlay(
            description=(
                "Home storage and case goods: dressers, chests of drawers, "
                "armoires/wardrobes, nightstands, sideboards/credenzas, cabinets, "
                "entry storage. Includes tip-over safety and compliance terms (STURDY "
                "/ 16 CFR 1261 / ASTM F2057), plus TSCA Title VI / CARB Phase 2 "
                "composite-wood emissions labeling."
            ),
            content=load_prompt("verticals/furniture/overlays/casegoods_storage.md"),
        ),
        "dining_tables_sets": VerticalOverlay(
            description=(
                "Dining furniture: dining tables, kitchen tables, counter-height or "
                "bar-height dining sets, extendable tables, and table leaves "
                "(drop-leaf, butterfly/self-storing, removable). Includes "
                "seating-capacity sizing heuristics and the '24 inches per person' "
                "rule of thumb."
            ),
            content=load_prompt("verticals/furniture/overlays/dining_tables_sets.md"),
        ),
        "chairs_stools_benches": VerticalOverlay(
            description=(
                "Non-office seating: dining chairs, accent chairs, benches, bar "
                "stools, counter stools, and set-of-2 seating. Includes the common "
                "10–12 inch seat-to-counter clearance rule and typical seat-height "
                "ranges by counter/bar height."
            ),
            content=load_prompt(
                "verticals/furniture/overlays/chairs_stools_benches.md"
            ),
        ),
        "home_office": VerticalOverlay(
            description=(
                "Home office furniture: office chairs/task chairs, ergonomic chairs, "
                "gaming chairs, computer desks and standing desks. Includes BIFMA "
                "standard references (X5.1 chairs, X5.5 desks), standing-desk "
                "height-range expectations, and caster/floor matching (hard vs soft "
                "wheels)."
            ),
            content=load_prompt("verticals/furniture/overlays/home_office.md"),
        ),
        "outdoor_patio": VerticalOverlay(
            description=(
                "Outdoor/patio furniture: conversation sets, patio dining sets, "
                "loungers, Adirondack chairs, outdoor cushions and fabrics. Includes "
                "outdoor-material durability signals (teak, powder-coated aluminum, "
                "HDPE), solution-dyed acrylic fabric concepts, and "
                "quick-dry/reticulated foam."
            ),
            content=load_prompt("verticals/furniture/overlays/outdoor_patio.md"),
        ),
        "bathroom_vanities": VerticalOverlay(
            description=(
                "Bathroom sink vanities: vanity cabinets, vanity tops, integrated "
                "sinks, floating vs freestanding vanities, single vs double sink. "
                "Includes common vanity width buckets (24/30/36/42/48/60+), selling "
                "unit ('with top' vs 'cabinet only'), and faucet-hole spacing jargon "
                "(centerset 4-inch vs widespread 8-inch+ vs single hole). Excludes "
                "makeup/dressing vanities."
            ),
            content=load_prompt("verticals/furniture/overlays/bathroom_vanities.md"),
        ),
        "makeup_vanities_dressing_tables": VerticalOverlay(
            description=(
                "Makeup vanity tables and dressing tables (bedroom/closet): vanities "
                "with mirrors, Hollywood lighted vanities, vanity sets with stool. "
                "Includes mirror/lighting expectations. Excludes bathroom sink "
                "vanities."
            ),
            content=load_prompt(
                "verticals/furniture/overlays/makeup_vanities_dressing_tables.md"
            ),
        ),
        "media_consoles_tv_stands": VerticalOverlay(
            description=(
                "Media furniture: TV stands, media consoles, entertainment centers, "
                "fireplace TV stands, floating media cabinets. Includes TV-size math "
                "pitfalls (TV inches are diagonal), stand-width heuristics, and "
                "content about choosing consoles wider than the TV."
            ),
            content=load_prompt(
                "verticals/furniture/overlays/media_consoles_tv_stands.md"
            ),
        ),
        "rugs": VerticalOverlay(
            description=(
                "Rugs and mats: area rugs, runners, doormats, washable rugs, "
                "indoor/outdoor rugs, rug pads. Includes standard rug sizing "
                "vocabulary (5x8, 8x10, 9x12), pile-height categories (low < 1/4 "
                "inch), and indoor/outdoor material expectations."
            ),
            content=load_prompt("verticals/furniture/overlays/rugs.md"),
        ),
        "nursery_kids": VerticalOverlay(
            description=(
                "Kids and nursery furniture: cribs (full-size and non-full-size/mini), "
                "toddler beds, bunk beds, loft beds, changing tables. Includes U.S. "
                "safety standard concepts (CPSC 16 CFR 1219/1220 for cribs; 16 CFR "
                "1513 for bunk beds), slat-spacing constraints, and drop-side crib "
                "exclusion."
            ),
            content=load_prompt("verticals/furniture/overlays/nursery_kids.md"),
        ),
        "commercial_contract": VerticalOverlay(
            description=(
                "Commercial/contract-grade furniture for workplaces and public spaces: "
                "stacking/banquet chairs, training-room tables, lobby seating, "
                "restaurant seating, waiting-room furniture. Includes BIFMA "
                "references, GREENGUARD Gold language, TB117-2013 flammability "
                "labeling (smolder resistance), and legacy TB133/CAL 133 procurement "
                "references."
            ),
            content=load_prompt("verticals/furniture/overlays/commercial_contract.md"),
        ),
    },
)
