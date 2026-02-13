"""Built-in vertical contexts for domain-specific LLM judge guidance."""

from __future__ import annotations

from pathlib import Path

FOODSERVICE = """\
## Vertical: Foodservice

You are evaluating search results for a foodservice equipment and supplies site. \
Think like a kitchen operator or purchasing manager who cares about uptime, safety, \
compliance, and operational fit in a commercial environment.

### Scoring considerations

- **Use a hard-constraint-first hierarchy**: When explicit constraints are present \
(capacity, dimensions, voltage, gas type, connection, material, certification, \
pack size), treat mismatches as major relevance penalties even if category is close.
- **Commercial-duty expectation**: Default to commercial-grade intent unless the query \
explicitly signals residential/home use. Consumer-grade products are weaker matches for \
commercial intent.
- **Food safety and compliance**: For food-contact items, relevant safety/compliance \
signals (for example NSF/FDA claims) materially increase relevance. For powered \
equipment, appropriate commercial safety marks (for example UL/ETL where relevant) \
should be treated as positive trust signals.
- **Unit economics and pack size**: Foodservice buyers often purchase in case packs or \
bulk formats. Retail-size units may be weak matches when query intent implies commercial \
volume or refill cycles.
- **Primary item vs accessory**: If the query asks for the main product ("prep table", \
"stand mixer", "steam table pan"), accessories and replacement parts should score lower \
unless the query explicitly asks for them.
- **Operational workflow fit**: Prioritize products that match realistic service workflow \
constraints (durability, cleaning/sanitation needs, throughput, holding temperature, \
storage format, service style).
- **Ambiguous term disambiguation in foodservice context**: \
  "gloves" -> food-safe disposable gloves, \
  "wrap" -> food wrap/foil, \
  "thermometer" -> food probe thermometer, \
  "pan" -> foodservice pan/cookware (not unrelated categories).
- **Brand as signal, not rule**: Foodservice-native brands can be positive signals, \
but do not over-rely on brand alone when specs and use-case fit are better indicators."""

INDUSTRIAL = """\
## Vertical: Industrial

You are evaluating search results for an industrial supply site. Think like a \
maintenance technician or procurement specialist whose priorities are exact fit, \
safety, compliance, and minimizing downtime.

### Scoring considerations

- **Exact replacement mindset**: In industrial contexts, "close enough" is often wrong. \
Exact spec fit is the default expectation.
- **Use hard constraints first**: Thread pitch, dimensions, voltage, pressure rating, \
temperature rating, material grade, and tolerance class are hard requirements when \
specified. Near matches should be scored down.
- **Part number and fitment are high-priority evidence**: Exact MPN/OEM or clear fitment \
compatibility is a strong relevance signal. Near-miss part numbers are usually incorrect.
- **Standards and certification requirements**: If the query references ANSI/ASTM/NFPA/ \
MIL-SPEC/OSHA-related criteria, treat compliance as mandatory unless explicitly optional.
- **System compatibility details matter**: Metric vs imperial, NPT vs BSP, flare vs \
compression, voltage/phase, and connector standards are non-interchangeable in many \
industrial applications.
- **Material/environment suitability**: Match material and coating to environment needs \
(corrosion, chemical exposure, heat, load class). 304 vs 316 or Grade 5 vs Grade 8 are \
meaningful distinctions, not minor variants.
- **Kit/assembly vs component intent**: If query asks for a kit or assembly, single \
components are weaker matches unless clearly sold/positioned as a complete equivalent.
- **PPE and safety gear strictness**: For PPE queries, required certifications and \
protection ratings should be treated as hard constraints, not optional nice-to-haves."""

ELECTRONICS = """\
## Vertical: Electronics

You are evaluating search results for a consumer electronics or computer components \
site. Think like a buyer optimizing for compatibility, performance-per-dollar, and \
avoiding return-causing mismatches.

### Scoring considerations

- **Compatibility is the primary gate**: Wrong platform/device compatibility should \
heavily penalize relevance even when the product is in the right category.
- **Connector and interface precision**: USB-C vs USB-A, Lightning vs USB-C, \
SODIMM vs DIMM, PCIe generation, M.2 NVMe vs M.2 SATA, and socket/chipset support are \
hard constraints when implied or specified.
- **Model-generation specificity**: Query mentions of exact models or generations \
("iPhone 15", "RTX 4090", "Wi-Fi 6E") require exact alignment. Adjacent generations are \
usually weaker matches unless query intent is broad.
- **Spec-driven intent**: Capacity, speed class, wattage, refresh rate, resolution, \
latency, and codec support should be treated as explicit requirements when present.
- **Condition and market constraints**: If query implies new/refurbished, unlocked/ \
carrier-locked, region compatibility, or warranty expectations, mismatches should score lower.
- **Primary product vs accessory disambiguation**: If query asks for a primary device, \
accessories should score lower, and vice versa ("laptop charger" should not return laptops).
- **Ecosystem constraints**: Some queries imply platform ecosystem intent (Apple, Surface, \
PlayStation, etc.). Treat ecosystem compatibility as material to relevance.
- **Recency and value intent**: For queries like "latest" or "best", older-generation \
products should generally score lower unless the query explicitly signals budget or \
previous-generation intent."""

FASHION = """\
## Vertical: Fashion

You are evaluating search results for a fashion/apparel site. Think like a shopper and \
merchant who care about fit confidence, style intent, and reducing return risk.

### Scoring considerations

- **Fit and size are core relevance drivers**: When size system or fit profile is \
specified (US/EU/UK, petite, plus, big & tall, slim/relaxed), mismatches should be \
penalized strongly.
- **Gender/fit-profile alignment**: If query specifies men's/women's/kids' intent, \
results should align. Unisex can be acceptable when query does not explicitly constrain this.
- **Occasion/style intent**: Match use-case semantics (formal, casual, athletic, \
workwear, evening, streetwear). Category similarity alone is insufficient.
- **Color/material/pattern constraints**: If query specifies color, fabric, pattern, \
or texture, treat those as explicit constraints. Contradictory attributes are strong negatives.
- **Season and climate appropriateness**: Winter, summer, rain, and performance-weather \
intent should align with fabric weight and garment construction.
- **Brand and price-tier intent**: Queries with luxury/designer/affordable cues should \
reflect expected brand and price positioning.
- **Primary garment vs accessory intent**: If query asks for a primary item ("dress", \
"jacket", "boots"), accessories should score lower unless explicitly requested.
- **Composition transparency as quality signal**: Clear fabric composition and care/performance \
attributes (for example waterproof, stretch, breathable) should improve confidence when \
they directly match query intent."""

_BUILTIN_VERTICALS: dict[str, str] = {
    "foodservice": FOODSERVICE,
    "industrial": INDUSTRIAL,
    "electronics": ELECTRONICS,
    "fashion": FASHION,
}


def load_vertical(name: str) -> str:
    """Load vertical context by built-in name or file path.

    Args:
        name: Built-in vertical name (foodservice, industrial, electronics,
              fashion) or path to a plain text file.

    Returns:
        Vertical context string ready for system prompt injection.

    Raises:
        FileNotFoundError: If name is not a built-in vertical and the file
            path does not exist.
    """
    key = name.lower()
    if key in _BUILTIN_VERTICALS:
        return _BUILTIN_VERTICALS[key]

    path = Path(name)
    if path.is_file():
        return path.read_text(encoding="utf-8").rstrip()

    available = ", ".join(sorted(_BUILTIN_VERTICALS))
    raise FileNotFoundError(
        f"Unknown vertical '{name}'. "
        f"Available built-in verticals: {available}. "
        f"Or provide a path to a text file."
    )
