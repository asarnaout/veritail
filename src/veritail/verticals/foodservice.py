"""Foodservice vertical context for LLM judge guidance."""

from veritail.types import VerticalContext, VerticalOverlay

FOODSERVICE = VerticalContext(
    core="""\
## Vertical: Foodservice

You are evaluating search results for a commercial foodservice equipment and \
supplies site serving professional operators. Unless the query explicitly \
signals residential or home use, assume commercial-grade, professional buyer \
intent throughout.

### Scoring considerations

The following scoring considerations are organized by priority tier — hard \
constraints first, then category and grade alignment, then domain context, \
and finally terminology equivalences.

### Hard Constraints

When a query specifies or implies any of the following, treat a mismatch as \
a major relevance failure regardless of how close the product category appears:

- **Electrical**: voltage (120 V, 208 V, 240 V), phase (single vs \
three-phase), amperage. 208 V and 240 V are distinct electrical services — equipment \
rated for one may underperform or fail on the other.
- **Gas type**: natural gas (NG) vs liquid propane (LP) require different \
orifices and pressures; they are not interchangeable without a conversion kit.
- **Dimensions and form factor**: "undercounter" means ≤ 34.5" height; \
specific widths (48-inch, 72-inch) and door/section counts are firm \
requirements, not preferences. Across all equipment categories, sub-type and \
form-factor distinctions represent fundamentally different products (e.g., \
undercounter vs conveyor dishwashers, reach-in vs undercounter refrigerators, \
modular vs self-contained ice machines) — mismatching form factor is a \
category-level error.
- **Temperature range**: refrigerator (33–41 °F) vs freezer vs dual-temp — \
confusing these is a critical error.
- **Certifications**: NSF/ANSI (2: food equipment, 4: commercial cooking, \
7: commercial refrigeration), UL/ETL safety listing, ENERGY STAR (hard \
requirement when query-specified — often mandated by institutional \
procurement), ADA compliance (≤ 34" serving surfaces for schools, hospitals, \
public facilities). When a query specifies a certification, treat it as a \
hard requirement.

### Category and Grade Alignment

- **Commercial-grade default**: Consumer-grade or residential products (home \
stand mixers, residential refrigerators) are weak matches against commercial \
queries. Key commercial signals: NSF listing, stainless steel construction, \
caster-ready legs, commercial warranty terms. A 5-quart home mixer is not a \
match for a "20 qt mixer" query.
- **Equipment vs parts vs accessories**: A query for equipment ("prep table", \
"reach-in refrigerator") should not return replacement parts (gaskets, \
thermostats, heating elements) or accessories (shelf clips, drip trays), and \
vice versa. A brand + model number pattern (e.g., "True T-49") typically \
signals a parts or exact-replacement search.
- **Pack-size alignment**: Commercial buyers purchase disposables, chemicals, \
and smallwares in case packs. Retail-size singles are weak matches for \
commercial-volume queries ("disposable gloves", "to-go containers"). Do not \
penalize individual-unit results when the query specifies a single item.

### Domain Context

- **Operator-segment fit**: Food truck buyers need compact, low-amperage, \
propane-ready, or ventless equipment. Institutional buyers (schools, \
hospitals, corrections) need ADA compliance, bid-spec documentation, and \
high-volume batch capacity. When the query signals a segment, align results \
with that segment's realistic constraints.
- **Brand equity**: When a query names a brand, prioritize it but still \
require spec alignment. When no brand is named, do not penalize lesser-known \
brands that match specs. ITW Food Equipment Group (Hobart, Vulcan, Traulsen, \
Baxter) and Ali Group (Scotsman, Beverage-Air) brands are parent-company \
siblings that buyers often cross-shop.
- **Installation dependencies**: Do not penalize core equipment for not \
bundling infrastructure (gas connectors, drain kits, ventilation hoods) \
unless the query asks for a complete installation package or kit.

### Terminology Equivalences

Foodservice uses dense trade jargon. Do not penalize lexical mismatches \
when intent aligns. The following cross-cutting equivalences apply across \
all product categories (category-specific terms are listed in the \
per-query domain guidance when present):

- hotel pan = steam table pan = GN container (but US and GN systems are \
physically incompatible)
- cambro = food storage container / insulated food pan carrier (genericized \
brand; the generic kitchen term usually means a large plastic container)
- speed rack = sheet pan rack = bun pan rack
- dunnage rack = floor rack (keeps items off floor per health code)
- bus tub = dish tub
- pan sizes: full, half, third, quarter, sixth, ninth (US hotel pan system)""",
    overlays={
        "beverage": VerticalOverlay(
            description=(
                "Coffee, espresso, fountain, frozen beverage, and draft beer equipment"
            ),
            content="""\
### Beverage Equipment — Scoring Guidance

This query involves coffee, espresso, fountain, frozen beverage, tea, or \
draft beer equipment.

**Critical distinctions to enforce:**

- **Espresso machines**: Group head count (1 vs 2 vs 3) determines volume \
capacity and is a hard spec. Boiler type — single, dual, heat exchanger — \
affects temperature stability and simultaneous steaming. Volumetric vs \
semi-automatic dosing are distinct control systems.
- **Coffee brewers**: Drip vs pour-over vs satellite vs airpot are different \
serving systems with different infrastructure needs (pour-over requires no \
plumbing). Gallon-per-batch capacity is a hard spec.
- **Carbonation / fountain**: Bag-in-box vs pre-mix vs post-mix are \
incompatible syrup delivery systems. Number of flavor valves is a hard spec. \
Carbonator included vs separate is a critical configuration distinction.
- **Frozen beverage**: Granita (non-carbonated slush, no dairy) vs frozen \
carbonated vs soft serve (dairy, different cleaning protocols) are completely \
different machines despite visual similarity — confusing them is a category \
error.
- **Draft beer**: Direct draw (short draw, no glycol) vs long-draw \
(glycol-cooled lines) are different systems. Number of taps and kegerator vs \
jockey box are hard specs.
- **Tea equipment**: Hot tea brewers vs iced tea brewers are different \
machines. Capacity (3 gal vs 5 gal) is a hard spec.
- **Bar blenders**: Sound-enclosed bar blenders (drink-specific programs) vs \
high-performance blenders (smoothie programs, power-focused) serve different \
operational needs.""",
        ),
        "cooking": VerticalOverlay(
            description=(
                "Cooking equipment: ovens, fryers, ranges, griddles, steamers, broilers"
            ),
            content="""\
### Cooking Equipment — Scoring Guidance

This query involves cooking equipment (ovens, fryers, griddles, ranges, \
broilers, steamers, or related accessories).

**Critical distinctions to enforce:**

- **Salamander vs cheese melter**: A salamander operates at 1500–1800 °F for \
finishing and browning; a cheese melter operates ≤ 550 °F for melting and \
holding. A salamander query must not return a cheese melter. A cheese melter \
query may accept a salamander as overpowered but functional (score 2 max).
- **Combi oven vs convection oven**: A combi oven provides both steam and \
convection modes; a standard convection oven does not inject steam. \
Returning a convection oven for a "combi oven" query is a category error.
- **Flat top / griddle vs flat top range**: A griddle is a standalone cooking \
surface; a flat top range is a range with a solid French-style plate. \
These are different product categories.
- **Fryer type**: Countertop vs floor model, tube vs open-pot vs flat-bottom \
are distinct designs suited to different volumes and oil management needs.
- **BTU / burner count**: When specified, these are hard requirements. A \
6-burner range is not interchangeable with a 4-burner + griddle combo \
unless the query is ambiguous.
- **Oven types**: Convection, combi, deck/stone-deck, conveyor/impinger, \
rotary/rack are fundamentally different cooking methods — each serves \
distinct menu applications and should not be conflated.

**Gas vs electric**: For cooking equipment, gas type (NG vs LP) and voltage/\
phase are especially critical. Restaurant kitchens are wired for specific \
services; mismatching can require costly electrical upgrades.

**Terminology equivalences** (do not penalize lexical mismatches when \
intent aligns):
- salamander = high-heat overhead broiler (1500–1800 °F, finishing/browning)
- combi / combi oven = combination oven (steam + convection)
- flat top = griddle — distinct from flat top range
- charbroiler = char grill = char
- impinger = conveyor oven (genericized from Lincoln brand)
- deck oven = stone-deck baking / pizza oven""",
        ),
        "food_prep": VerticalOverlay(
            description=(
                "Mixers, slicers, food processors, and powered preparation equipment"
            ),
            content="""\
### Food Preparation Equipment — Scoring Guidance

This query involves mixers, slicers, food processors, or other powered \
preparation equipment.

**Critical distinctions to enforce:**

- **Mixers**: Quart capacity is a hard spec (5 qt countertop, 20 qt light \
commercial, 30–60 qt floor, 80+ qt industrial). Planetary vs spiral are \
fundamentally different — planetary for batter/cream/dough versatility, \
spiral for dough-specific with rotating bowl. Confusing these is a category \
error.
- **Slicers**: Blade diameter (9", 10", 12", 13") determines max product \
size and is a hard spec. Manual vs automatic (auto-carriage) are distinct \
operating modes. Gravity feed vs vertical feed and belt-driven vs \
gear-driven are further distinctions.
- **Food processors**: Batch bowl (fixed capacity) vs continuous feed \
(unlimited throughput via chute) are different machines for different \
workflows. Bowl capacity is a hard spec for batch processors.
- **Vegetable prep**: Cut sizes (1/4", 3/8", 1/2") are hard requirements. \
Manual vs electric dicers and cutters are different product categories.
- **Meat processing**: Grinder plate size (#12, #22, #32) determines \
capacity and is a hard spec. Tenderizers, band saws, and grinders are \
distinct equipment categories.
- **Dough equipment**: Sheeters (countertop vs floor), dividers, and \
rounders are bakery-specific equipment — each serves a distinct step in \
dough processing.""",
        ),
        "refrigeration": VerticalOverlay(
            description=("Refrigeration, freezers, ice machines, and cold storage"),
            content="""\
### Refrigeration Equipment — Scoring Guidance

This query involves refrigeration, freezers, ice machines, or cold-storage \
equipment.

**Critical distinctions to enforce:**

- **Reach-in vs undercounter vs walk-in**: These are fundamentally different \
form factors and capacities. Undercounter units must be ≤ 34.5" height. \
Walk-in queries should not return reach-in units.
- **Ice machine configuration**: Three independent axes must all match: \
(1) ice type — cube, half-cube, nugget, flake are functionally distinct; \
(2) machine type — modular head-only vs self-contained undercounter; \
(3) cooling method — air-cooled vs water-cooled. Mismatching any single \
axis is a hard failure.
- **Temperature range**: Refrigerator (33–41 °F) vs freezer (−10–0 °F) vs \
dual-temp (convertible) — confusing these is a critical error. A "freezer" \
query must not return a refrigerator, even from the same product line.
- **Ice bin vs ice machine**: An ice bin is passive storage; an ice machine \
produces ice. Do not conflate them.
- **Prep table types**: Refrigerated prep tables (sandwich/salad prep) vs \
non-refrigerated work tables are different categories despite similar names.
- **Walk-in panels**: Insulation thickness, floor vs floorless, and door \
type (solid vs glass) are hard specs for walk-in cooler/freezer projects.
- **Blast chillers vs standard freezers**: Blast chillers perform rapid \
cooling for food safety compliance (HACCP); standard freezers are for \
long-term storage — these are distinct product categories.

**Daily production capacity**: For ice machines, lbs/day ratings at specific \
ambient temperatures (70 °F and 90 °F) are key specs. When a query specifies \
capacity, match the production range — a 500 lb/day machine is not a match \
for a "1000 lb ice machine" query.

**Terminology equivalences** (do not penalize lexical mismatches when \
intent aligns):
- lowboy = undercounter refrigerator / freezer
- reach-in = upright commercial refrigerator / freezer
- chef base = refrigerated equipment stand""",
        ),
        "serving_holding": VerticalOverlay(
            description=(
                "Holding cabinets, steam tables, food warmers, "
                "buffet, and display merchandisers"
            ),
            content="""\
### Serving and Holding Equipment — Scoring Guidance

This query involves holding cabinets, steam tables, food warmers, buffet \
equipment, or display merchandisers.

**Critical distinctions to enforce:**

- **Hot holding vs cold holding vs ambient display**: These are \
fundamentally different thermal systems — confusing them is a critical error.
- **Holding cabinets**: Full-size vs half-size vs undercounter are different \
form factors. Humidity-controlled (bread/pastry) vs dry heat cabinets serve \
different food types. Proofing cabinets (dough fermentation) look similar \
to holding cabinets but are a completely different product category — \
confusing them is a category error.
- **Steam tables**: Wet well (water bath) vs dry well (radiant heat) have \
different food safety characteristics. Number of wells and well size (full, \
half, third) are hard specs.
- **Buffet equipment**: Drop-in wells (require counter cutout) vs portable \
(self-contained) vs modular are different installation types — installation \
type is a hard constraint when specified.
- **Food merchandisers**: Heated (grab-and-go), refrigerated \
(beverages/pre-made), and ambient (bakery) are distinct thermal categories \
— returning the wrong thermal type is a critical error.
- **Serving counters**: Hot food vs cold food vs frost top \
(ice cream/gelato) are distinct product lines with different infrastructure.
- **Catering equipment**: Chafing dishes (fuel-heated) vs electric chafers \
vs induction warmers use different heat sources and have different \
operational requirements.

**Terminology equivalences** (do not penalize lexical mismatches when \
intent aligns):
- bain-marie = hot food well = steam table = food warmer""",
        ),
        "smallwares": VerticalOverlay(
            description=(
                "Pans, food storage, disposables, utensils, and kitchen hand tools"
            ),
            content="""\
### Smallwares and Disposables — Scoring Guidance

This query involves pans, food storage, disposables, utensils, or other \
smallwares and kitchen hand tools.

**Critical distinctions to enforce:**

- **Pan systems**: US hotel pans (full, half, third, quarter, sixth, ninth) \
and European GN pans (1/1, 1/2, 1/3, 2/3, etc.) are dimensionally \
incompatible — different corner radii and rim profiles. Do not cross-match \
hotel pan queries with GN products or vice versa.
- **Exact sizing for disposables**: "8 oz" means 8 oz; "6×6 clamshell" means \
6×6. Size is a hard constraint for disposables.
- **Material exclusivity**: Compostable and foam are mutually exclusive \
materials — returning foam for a "compostable" query is a hard failure, as \
foam is banned in many jurisdictions. Similarly, BPA-free is a hard \
requirement when specified.
- **Pan depth**: Steam table pans come in standard depths (2.5", 4", 6"). \
Depth is a hard requirement when specified — a 2.5" pan cannot substitute \
for a 6" pan.
- **Cutting board color-coding**: HACCP color protocols (green = produce, \
red = raw meat, blue = cooked meat, etc.) are food safety standards, not \
aesthetics — color is a hard requirement when specified.
- **Food storage containers**: Round vs square, capacity, and lid \
compatibility matter. Cambro and Carlisle container systems are not always \
interchangeable.

**Commercial pack sizing**: Disposables and chemicals are sold in case packs \
(e.g., 1000-count, 500-count). Retail-size packaging (10-count) is a weak \
match for commercial queries. Conversely, do not penalize single-unit results \
when the query specifies a single item.

**Terminology equivalences** (do not penalize lexical mismatches when \
intent aligns):
- lexan = clear polycarbonate food storage container (genericized brand)""",
        ),
        "tabletop": VerticalOverlay(
            description=(
                "Dinnerware, flatware, glassware, and barware for front-of-house"
            ),
            content="""\
### Tabletop — Scoring Guidance

This query involves dinnerware, flatware, glassware, or barware for \
front-of-house service.

**Critical distinctions to enforce:**

- **Dinnerware material**: Vitrified china (commercial standard) vs melamine \
(break-resistant, cannot microwave) vs stoneware vs bone china (fine dining) \
— material is a hard constraint when specified. Each material has distinct \
durability, presentation, and operational trade-offs.
- **Flatware grading**: 18/10 (highest corrosion resistance) vs 18/8 \
(standard commercial) vs 18/0 (no nickel, budget) — grade is a hard spec \
when specified. Weight class (heavy, medium, economy) is a separate \
dimension from grade.
- **Glassware**: Tempered vs non-tempered is a critical distinction \
(tempered required by many commercial operations for safety). Stemware vs \
tumblers are different categories. Capacity in oz is a hard spec.
- **Barware glass types**: Rocks, highball, pilsner, snifter, coupe, \
martini, wine, shot, pint are functionally distinct shapes for specific \
beverages — returning a pilsner glass for a "rocks glass" query is a \
category error.
- **Pattern / collection matching**: Operations buy to match existing table \
settings. Brand + collection (e.g., "Libbey Embassy", "Homer Laughlin \
Fiesta") identifies a specific pattern — returning a different collection \
from the same brand is a mismatch.
- **Serviceware sizing**: Charger plates, bread plates, dinner plates are \
distinct sizes — returning a 10" dinner plate for a "6 inch bread plate" \
query is a size error.""",
        ),
        "warewash": VerticalOverlay(
            description=(
                "Dishwashers, glasswashers, sanitation, and cleaning chemicals"
            ),
            content="""\
### Warewash and Sanitation — Scoring Guidance

This query involves commercial dishwashers, glasswashers, sanitizing \
equipment, or cleaning chemicals.

**Critical distinctions to enforce:**

- **Dishwasher type**: Undercounter, door-type (upright), conveyor, and \
flight-type are fundamentally different machines for different operation \
scales. A bar glasswasher is not a match for a "conveyor dishwasher" query.
- **High-temp vs low-temp**: High-temp machines sanitize with 180 °F+ rinse \
water; low-temp (chemical) machines use chemical sanitizer. These are \
different systems with different infrastructure requirements (high-temp needs \
a booster heater). When the query specifies a sanitation method, it is a \
hard requirement.
- **Rack size**: Standard 20×20 racks vs smaller glasswasher racks — rack \
compatibility is a hard constraint for door-type and conveyor machines.
- **Waste handling**: Trash compactors, pulpers, and waste disposers are \
distinct product categories. Grease traps vs grease interceptors differ in \
capacity and installation — GPM (gallons per minute) rating is a hard spec.
- **Sanitizer type**: Quat-based vs chlorine-based vs iodine-based \
sanitizers have different concentrations, material compatibility, and \
regulatory approvals — they are not interchangeable.

**Chemical compatibility**: Dishwasher detergents, rinse aids, and sanitizers \
are formulated for specific machine types. When a query specifies a machine \
brand or model, chemical results should be compatible with that system.""",
        ),
    },
)
