"""Office supplies vertical context for LLM judge guidance."""

from veritail.prompts import load_prompt
from veritail.types import VerticalContext, VerticalOverlay

OFFICE_SUPPLIES = VerticalContext(
    core=load_prompt("verticals/office_supplies/core.md"),
    overlays={
        "ink_and_toner": VerticalOverlay(
            description=(
                "Printer consumables: OEM and compatible ink cartridges, laser toner, "
                "drum units, fusers, and maintenance kits."
            ),
            content=load_prompt("verticals/office_supplies/overlays/ink_and_toner.md"),
        ),
        "paper_and_media": VerticalOverlay(
            description=(
                "Printable media: Copy paper, cardstock, photo paper, resume paper, "
                "and large format rolls."
            ),
            content=load_prompt(
                "verticals/office_supplies/overlays/paper_and_media.md"
            ),
        ),
        "writing_instruments": VerticalOverlay(
            description=(
                "Writing and art tools: Pens, mechanical pencils, replacement leads, "
                "markers, highlighters, and school art supplies."
            ),
            content=load_prompt(
                "verticals/office_supplies/overlays/writing_instruments.md"
            ),
        ),
        "office_furniture": VerticalOverlay(
            description=(
                "Office seating, desks, tables, standing desk converters, and "
                "ergonomic commercial workspace furniture."
            ),
            content=load_prompt(
                "verticals/office_supplies/overlays/office_furniture.md"
            ),
        ),
        "shredders_and_data_destruction": VerticalOverlay(
            description="Paper shredders, media destroyers, and data security devices.",
            content=load_prompt(
                "verticals/office_supplies/overlays/shredders_and_data_destruction.md"
            ),
        ),
        "mailing_and_packaging": VerticalOverlay(
            description=(
                "Envelopes, corrugated boxes, bubble mailers, packing tape, and "
                "shipping supplies."
            ),
            content=load_prompt(
                "verticals/office_supplies/overlays/mailing_and_packaging.md"
            ),
        ),
        "binding_and_presentation": VerticalOverlay(
            description=(
                "Document binding machines, presentation covers, combs, coils, wire-O, "
                "and laminating pouches."
            ),
            content=load_prompt(
                "verticals/office_supplies/overlays/binding_and_presentation.md"
            ),
        ),
        "filing_and_organization": VerticalOverlay(
            description=(
                "Filing cabinets, hanging folders, manila folders, binders, and "
                "indexing systems."
            ),
            content=load_prompt(
                "verticals/office_supplies/overlays/filing_and_organization.md"
            ),
        ),
        "thermal_printers_and_labels": VerticalOverlay(
            description=(
                "Thermal label printers, direct thermal labels, thermal transfer, and "
                "Avery-style laser/inkjet sheets."
            ),
            content=load_prompt(
                "verticals/office_supplies/overlays/thermal_printers_and_labels.md"
            ),
        ),
        "janitorial_and_breakroom": VerticalOverlay(
            description=(
                "Facility paper products, commercial dispensers, trash liners, and "
                "breakroom supplies."
            ),
            content=load_prompt(
                "verticals/office_supplies/overlays/janitorial_and_breakroom.md"
            ),
        ),
    },
)
