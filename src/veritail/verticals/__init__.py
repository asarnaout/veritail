"""Built-in vertical contexts for domain-specific LLM judge guidance."""

from __future__ import annotations

from pathlib import Path

FOODSERVICE = """\
## Vertical: Foodservice

You are evaluating search results for a foodservice equipment and supplies site. \
Shoppers are restaurant owners, caterers, institutional kitchen managers, and \
food-truck operators buying commercial-grade products for professional use.

### Scoring considerations

- **Pack size and unit relevance**: Foodservice buyers purchase in bulk. A single \
retail-size item when commercial cases or bulk packs are expected should score lower. \
Conversely, a bulk pack of a relevant item is a strong signal.
- **Commercial-grade expectations**: Results should be commercial/NSF-rated equipment \
unless the query specifically targets consumer-grade. A residential blender returned \
for "commercial blender" is a poor match.
- **Food-safety certifications**: Products requiring food contact (pans, prep surfaces, \
gloves, utensils) should carry NSF, UL-certified, or FDA-compliant designations when \
applicable. Absence of expected certification is a negative signal.
- **Foodservice brand interpretation**: Brands like Cambro, Vollrath, True, Beverage Air, \
and Avantco are foodservice-specific. Their presence is a positive relevance signal. \
Consumer brands (KitchenAid, Cuisinart) may indicate a residential product.
- **Cross-category intent**: Queries like "gloves" mean food-safe disposable gloves \
(vinyl, nitrile), not medical exam gloves or winter gloves. "Wrap" means plastic food \
wrap or foil, not gift wrap. "Thermometer" means a food probe thermometer, not a \
medical or ambient thermometer. Interpret ambiguous terms through foodservice context.
- **Equipment specifications**: Voltage (120V vs 208-240V), gas type (natural vs LP), \
and plug configuration matter for commercial kitchens. A mismatch on these specs for \
equipment queries is a significant negative signal."""

INDUSTRIAL = """\
## Vertical: Industrial

You are evaluating search results for an industrial supply site. Shoppers are \
maintenance technicians, procurement specialists, and facility managers buying \
MRO (maintenance, repair, and operations) supplies, safety equipment, and \
industrial components.

### Scoring considerations

- **Precise specification matching**: Industrial buyers search by exact specs \
(thread size, voltage, material grade, tensile strength). A product that matches \
the category but not the spec (e.g., 1/2"-13 bolt when 1/2"-20 was queried) is \
a poor match despite surface similarity.
- **Compliance and standards codes**: Queries referencing ANSI, ASTM, NFPA, or \
MIL-SPEC standards require products that meet those standards. A product without \
the referenced certification should score low.
- **Compatibility requirements**: Fasteners, fittings, and replacement parts must \
be compatible with the referenced system. Metric vs imperial, pipe thread vs \
machine thread, and flare vs compression fittings are not interchangeable.
- **PPE certification**: Safety products must carry appropriate certifications \
(ANSI Z87.1 for eye protection, ANSI/ISEA 105 for cut resistance, NFPA 70E for \
arc flash). Uncertified alternatives are not acceptable substitutes.
- **Material grade significance**: In industrial contexts, "stainless steel" is \
not generic — 304 vs 316 vs 410 matters. Similarly, Grade 5 vs Grade 8 bolts \
serve different load requirements. When a specific grade is queried, only that \
grade is a strong match.
- **Cross-category intent**: "Tape" means industrial adhesive tape (duct, \
electrical, masking), not office tape. "Markers" means industrial paint markers, \
not writing instruments. "Gloves" means work gloves (leather, cut-resistant, \
chemical-resistant), not disposable exam gloves."""

ELECTRONICS = """\
## Vertical: Electronics

You are evaluating search results for a consumer electronics or computer \
components site. Shoppers range from everyday consumers to IT professionals \
and enthusiasts buying devices, accessories, and components.

### Scoring considerations

- **Compatibility as hard constraint**: Electronics accessories and components \
must be compatible with the referenced device, platform, or standard. A USB-A \
cable returned for a "USB-C cable" query is irrelevant regardless of other \
attributes. A DDR4 RAM module for a "DDR5" query is a mismatch.
- **Model and generation specificity**: Queries referencing a specific model \
(e.g., "iPhone 15 case", "RTX 4090") require exact model matches. A case for \
iPhone 14 or a listing for RTX 4080 is not a strong match even though the \
category is correct.
- **Recency expectations**: For fast-moving categories (phones, GPUs, laptops), \
previous-generation products returned for generic queries (e.g., "best laptop") \
should score lower unless explicitly searching for older models.
- **Spec-driven queries**: When queries include specs (wattage, capacity, speed \
class, resolution), those specs are hard requirements. A "1TB NVMe SSD" query \
should not return 500GB drives. A "4K monitor" query should not return 1080p \
displays.
- **Brand and ecosystem**: Some queries imply ecosystem constraints. "AirPods \
case" means Apple AirPods, not generic earbuds. "Surface keyboard" means \
Microsoft Surface-compatible. Ecosystem context should inform relevance.
- **Accessory vs primary product**: A query for "laptop charger" wants the \
charger, not a laptop that comes with one. A query for "monitor" wants the \
display, not a monitor arm or cable."""

FASHION = """\
## Vertical: Fashion

You are evaluating search results for a fashion or apparel site. Shoppers are \
consumers buying clothing, footwear, and accessories for personal use.

### Scoring considerations

- **Gender targeting**: Fashion queries often imply or state a gender. "Men's \
running shoes" must return men's products. Unisex items are acceptable when the \
query does not specify gender. Returning women's products for a men's query (or \
vice versa) is a strong negative signal.
- **Occasion and style context**: "Dress shoes" implies formal; "casual sneakers" \
implies everyday wear. A hiking boot for "dress shoes" is irrelevant despite being \
footwear. A cocktail dress for "casual dress" is a weak match.
- **Size system awareness**: Queries may reference specific size systems (US, EU, \
UK) or size categories (plus size, petite, big & tall). Results should be available \
in the relevant size system or category when specified.
- **Brand and price tier**: Fashion shoppers are often brand- and tier-conscious. \
A query for "designer handbag" expects luxury brands, not mass-market alternatives. \
"Affordable running shoes" should not return $300 premium models.
- **Material and fabric requirements**: When a query specifies material ("silk \
blouse", "leather jacket", "cotton t-shirt"), the product must match that material. \
Faux leather for "leather jacket" is a weaker match. Polyester for "cotton t-shirt" \
is irrelevant.
- **Seasonal and trend relevance**: "Winter coat" should not return lightweight \
spring jackets. "Swimsuit" should return swimwear, not cover-ups or beach towels. \
Interpret seasonal terms through their standard fashion meaning."""

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
    if name in _BUILTIN_VERTICALS:
        return _BUILTIN_VERTICALS[name]

    path = Path(name)
    if path.is_file():
        return path.read_text(encoding="utf-8").rstrip()

    available = ", ".join(sorted(_BUILTIN_VERTICALS))
    raise FileNotFoundError(
        f"Unknown vertical '{name}'. "
        f"Available built-in verticals: {available}. "
        f"Or provide a path to a text file."
    )
