"""Medical supplies vertical context for LLM judge guidance."""

from veritail.prompts import load_prompt
from veritail.types import VerticalContext, VerticalOverlay

MEDICAL = VerticalContext(
    core=load_prompt("verticals/medical/core.md"),
    overlays={
        "surgical_instruments": VerticalOverlay(
            description=(
                "Surgical instruments: forceps, scissors, scalpels, needle holders, "
                "retractors, and rongeurs. Focus on metallurgy, blade numbering, and "
                "pattern names."
            ),
            content=load_prompt("verticals/medical/overlays/surgical_instruments.md"),
        ),
        "respiratory_therapy": VerticalOverlay(
            description=(
                "Respiratory equipment: CPAP/BiPAP machines, oxygen concentrators, "
                "nebulizers, and specialized tubing."
            ),
            content=load_prompt("verticals/medical/overlays/respiratory_therapy.md"),
        ),
        "wound_care": VerticalOverlay(
            description=(
                "Wound dressings and management: alginates, hydrocolloids, foams, "
                "films, hydrogels, and silver-impregnated dressings."
            ),
            content=load_prompt("verticals/medical/overlays/wound_care.md"),
        ),
        "ppe_hygiene": VerticalOverlay(
            description=(
                "Personal Protective Equipment: masks, gowns, gloves, and sanitation. "
                "Focus on barrier levels and AQL."
            ),
            content=load_prompt("verticals/medical/overlays/ppe_hygiene.md"),
        ),
        "urology_incontinence": VerticalOverlay(
            description=(
                "Urological supplies: catheters, drainage systems, and incontinence "
                "garments. Focus on tips and coatings."
            ),
            content=load_prompt("verticals/medical/overlays/urology_incontinence.md"),
        ),
        "diabetes_management": VerticalOverlay(
            description=(
                "Diabetes monitoring and delivery: meters, strips, lancets, CGMs, and "
                "insulin pumps."
            ),
            content=load_prompt("verticals/medical/overlays/diabetes_management.md"),
        ),
        "dme_mobility_orthopedics": VerticalOverlay(
            description=(
                "Durable Medical Equipment: wheelchairs, walkers, and braces. Focus on "
                "HCPCS codes and fitting requirements."
            ),
            content=load_prompt(
                "verticals/medical/overlays/dme_mobility_orthopedics.md"
            ),
        ),
        "hypodermic_infusion": VerticalOverlay(
            description=(
                "Needles, syringes, IV sets, and infusion supplies. Focus on "
                "connectors and safety engineering."
            ),
            content=load_prompt("verticals/medical/overlays/hypodermic_infusion.md"),
        ),
    },
)
