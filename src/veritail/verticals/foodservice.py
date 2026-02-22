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
constraints first. Hard constraints are the most important and should dominate \
the score, even if other attributes appear relevant. Prefer higher-score \
results when they satisfy more hard constraints and avoid critical errors.

### Hard constraints (must match)

- **Commercial intent**: If query includes "commercial", "restaurant", "NSF", \
"ETL", brand/model numbers, voltage, gas type, or capacities typical for \
professional kitchens, treat it as commercial.
- **Correct product category**: Equipment vs supplies vs food. Do not return \
food items for equipment queries or vice versa unless the query is clearly \
ambiguous and the result is plausibly relevant.
- **Brand/model specificity**: If the query specifies a brand and/or model \
(e.g., True T-49, Hobart AM15), the result must match that brand/model. \
Do not treat similar products from other brands as substitutes unless the \
query explicitly allows equivalents.
- **Compatible power/fuel**: Voltage (120V vs 208/240V vs 480V; single-phase vs \
three-phase), amperage. 208 V and 240 V are distinct electrical services — equipment \
rated for one may underperform or fail on the other.
- **Gas type**: natural gas (NG) vs liquid propane (LP) require different \
orifices and pressures; they are not interchangeable without a conversion kit.
- **Dimensions and form factor**: "undercounter" usually means a unit designed to fit \
under standard counters (commonly ~34–35" tall; ADA / low-profile units may be \
≤32"). Specific widths (48-inch, 72-inch) and door/section counts are firm \
requirements, not preferences. Across all equipment categories, sub-type and \
form-factor distinctions represent fundamentally different products (e.g., \
undercounter vs conveyor dishwashers, reach-in vs undercounter refrigerators, \
modular vs self-contained ice machines) — mismatching form factor is a \
category-level error.
- **Temperature range**: refrigerator (33–41 °F) vs freezer vs dual-temp — \
confusing these is a critical error.
- **Certifications**: NSF/ANSI standards vary by equipment category (common: 2 food equipment; 3 \
commercial warewashing; 4 cooking / rethermalization / powered hot holding; 7 \
commercial refrigeration; 8 powered food prep; 12 ice making; 13 refuse \
processors), UL/ETL safety listing, ENERGY STAR (hard \
requirement when query-specified — often mandated by institutional \
procurement), ADA compliance (≤ 34" serving surfaces for schools, hospitals, \
public facilities). When a query specifies a certification, treat it as a \
hard requirement.

### Installation dependencies (must be plausible)

- **Plumbing**: Many commercial units require water supply and drains (ice makers, \
dishwashers, steamers, espresso machines). Do not penalize a result for missing \
plumbing accessories unless the query explicitly asks for a complete kit.
- **Ventilation**: Cooking equipment may require hoods, fire suppression, and \
gas connections. Do not penalize the product for not including these unless \
the query asks for a complete system.
- **Refrigeration**: Walk-ins and remote condenser systems have distinct \
installation needs (refrigeration systems, line sets). Do not assume a walk-in \
"box" includes a condensing unit unless explicitly stated.
- **Parts vs equipment**: Replacement parts (gaskets, thermostats, motors) should \
not be scored as matches for "buy a unit" queries and vice versa.

### Common disqualifiers / critical errors

- Returning residential appliances (home refrigerators, consumer espresso machines) \
for commercial queries unless the query explicitly asks for home/residential.
- Confusing foam cups with paper cups, or returning non-microwavable containers \
for microwave-safe queries.
- Returning incompatible consumables (e.g., Nespresso pods for Keurig queries).
- Returning the wrong sanitary category (disinfectant vs food-contact sanitizer).

### Terminology and cross-cutting vocabulary

Foodservice search often uses multiple names for the same thing. Do not penalize \
a result for different terminology if the underlying item matches and industry \
intent aligns. The following cross-cutting equivalences apply across \
all product categories (category-specific terms are listed in the \
per-query domain guidance when present):

- hotel pan = steam table pan (US fractional pan system). GN / gastronorm \
pans are a different standard; do **not** treat GN as a synonym for hotel pans. \
If a query uses "GN", match GN sizing; otherwise assume US fractional pans.
- cambro = food storage container / insulated food pan carrier (genericized \
brand; the generic kitchen term usually means a large plastic container)
- speed rack = sheet pan rack = bun pan rack (kitchen context). Bar context \
may use "speed rail" / "speed rack" to mean a liquor bottle rail.
- dunnage rack = floor rack (keeps items off floor per health code)
- bus tub = dish tub
- pan sizes: full, half, third, quarter, sixth, ninth (US hotel pan system)""",
    overlays={
        "beverage_equipment": VerticalOverlay(
            description=(
                "Beverage EQUIPMENT — coffee machines, espresso machines, "
                "fountain dispensers, frozen drink machines, tea brewers, "
                "draft beer systems (NOT consumable drink products)"
            ),
            content="""\
### Beverage Equipment — Scoring Guidance

This query involves coffee, espresso, fountain, frozen drinks, tea, or \
draft beer equipment.

**Critical distinctions to enforce:**

- **Espresso machines**: Single vs double boiler vs heat-exchanger are distinct \
technical classes; group head count and water line connection (plumbed vs \
pour-over) are hard requirements.
- **Coffee brewers**: Airpot vs urn vs pod machines are different. Bunn-style \
commercial brewers use specific basket/sprayhead formats. Plumbed vs pourover \
differs in installation.
- **Fountain systems**: Bag-in-box vs pre-mix vs post-mix are incompatible. \
Number of valves is a hard spec. Carbonator included vs separate matters.
- **Draft beer systems**: Direct draw vs long draw (glycol) differ. Number of \
taps, tower type, and keg coupler/sankey compatibility (D vs S) are relevant.
- **Ice dispensers**: See ice_machines overlay; dispensers are not bins.

**Terminology**:
- BIB = bag-in-box syrup
- post-mix = syrup + carbonated water mixed at dispenser
- pre-mix = already mixed beverage in a container
""",
        ),
        "underbar": VerticalOverlay(
            description=(
                "Bar undercounter & workstation hardware: underbar cocktail stations, "
                "ice bins, bar sinks, speed rails, blender stations "
                "(not beverage dispensing machines)"
            ),
            content="""\
### Underbar and Bar Workstations — Scoring Guidance

This query involves stainless underbar workstations and components used behind the bar \
(e.g., cocktail stations, underbar sink modules, ice bins, speed rails, bottle wells, \
dump sinks, drainboards, and blender stations).

**Critical distinctions to enforce:**

- **Ice bin / ice sink vs ice machine**: Underbar ice bins / ice sinks STORE ice and drain meltwater. \
They do **not** make ice. Do not treat an "ice bin" query as an ice maker query.
- **Speed rail vs speed rack**: In bar context, "speed rail" (sometimes called a speed rack) is a \
liquor bottle rail. In kitchen context, "speed rack" usually means a sheet pan rack. Use \
bar/kitchen context clues to avoid category errors.
- **Modular components vs all-in-one stations**: Cocktail stations may be complete workstations \
or may be sold as modular pieces (ice bin only, sink only, drainboard only). Match the query’s \
scope: a "cocktail station" query expects a workstation; an "ice bin" query expects a bin.
- **Left vs right configuration**: Many underbar units are handed (sink left/right, drainboard left/right). \
If the query specifies left/right, it is a hard requirement.
- **Drain style**: Gravity drain vs pumped drain (or "no drain" for some portable bars) can be decisive \
for tight installs. When specified, treat as hard.

**Bar-specific terminology** (do not penalize lexical mismatches when intent aligns):
- cocktail station = bartender workstation = bar station
- dump sink = bar dump sink (used for draining melted ice / rinsing tins) — not a hand sink
- bottle well = bottle bin = bottle trough
""",
        ),
        "water_filtration": VerticalOverlay(
            description=(
                "Water filters and filtration systems for ice machines, coffee/espresso, "
                "steamers, beverage dispensers, and equipment protection"
            ),
            content="""\
### Water Filtration — Scoring Guidance

This query involves commercial water filters, filtration cartridges, filter heads/manifolds, \
and water-treatment accessories used to improve beverage taste and protect water-using \
equipment from scale.

**Critical distinctions to enforce:**

- **System vs cartridge vs parts**: Many listings are *cartridge-only* and require a compatible \
filter head/manifold. A "complete system" query expects head + cartridge(s); a "replacement \
cartridge" query expects the exact cartridge line/series. Head ↔ cartridge compatibility is \
often brand/series-specific.
- **Application-specific filters**: Filters marketed for ice machines, espresso/coffee, or steamers \
can differ (flow needs, scale inhibition, taste/odor reduction). Match the stated application \
when the query is explicit.
- **Hard specs when present**: Flow rate (GPM), capacity (gallons), connection size/type, and \
cartridge model number are hard constraints when specified. A 0–5 GPM steamer filter is not a \
match for a 10+ GPM requirement.
- **Scale control vs taste/odor**: Some products focus on scale inhibition (equipment protection) \
while others focus on contaminant reduction (chlorine/chloramine, sediment). Do not assume one \
substitutes for the other when the query calls it out.
- **Operator-driven replacements**: If the query contains a specific OEM filter part number or \
references an equipment brand/model (e.g., "for Hoshizaki"), treat compatibility \
as the primary relevance signal.

**Terminology**:
- filter head = manifold head = mounting head
- inline filter = in-line filter (often single-cartridge, quick-connect installs)
""",
        ),
        "replacement_parts": VerticalOverlay(
            description=(
                "Replacement parts, repair kits, and maintenance items for commercial "
                "foodservice equipment (not whole equipment units)"
            ),
            content="""\
### Replacement Parts — Scoring Guidance

This query involves replacement parts, repair parts, preventive maintenance items, \
or OEM part numbers for commercial foodservice equipment.

**Critical distinctions to enforce:**

- **Part vs whole unit**: If the query clearly asks for a *part* (gasket, thermostat, control board, \
igniter, probe, belt, caster, spray arm, pump, valve, knob, hinge), do not treat whole equipment units \
as relevant—even if they share the same brand/model.
- **Exact identifiers dominate**: When a query includes a part number (manufacturer part #, OEM #, \
or distributor cross-reference), matching that identifier is the strongest signal of relevance.
- **Compatibility is the product**: Parts are only relevant if they fit the target manufacturer/model/series. \
If the query specifies a model (e.g., a specific reach-in or fryer model), results must explicitly list \
compatibility with that model/series or with the exact part number.
- **Handed / versioned parts**: Left-hand vs right-hand, door size, voltage, gas type, and revision suffixes \
can change the correct part. If the query specifies LH/RH, voltage, gas type, or a suffix, treat it as hard.
- **OEM vs universal**: Many parts are universal (casters, some knobs, some shelving clips), but many are \
OEM-specific (boards, probes, gaskets, condenser fans). If the query says OEM/genuine, prioritize OEM; \
if it says universal, allow generic fitment but still enforce dimensions/specs.

**Common patterns**:
- Queries containing "OEM", "part #", "replacement", "gasket", "thermostat", "probe", "board", "kit" \
should be routed here.
""",
        ),
        "beverages": VerticalOverlay(
            description=(
                "Consumable drinks: coffee, tea, soda syrups, juices, water, "
                "beer/wine (NOT equipment)"
            ),
            content="""\
### Beverages (Consumables) — Scoring Guidance

This query involves consumable beverages (not machines).

**Critical distinctions to enforce:**

- **Concentrate vs ready-to-drink**: Syrup concentrates (BIB, bag-in-box) are \
not drinks; they are for dispensing systems. If query requests "BIB" or \
"soda syrup", do not return bottled soda.
- **Coffee format**: Whole bean vs ground vs pods; roast profile; decaf vs regular \
are hard requirements when specified. Espresso grind vs drip grind mismatch \
is a functional error.
- **Tea format**: Iced tea bags, loose leaf, and RTD are distinct. Sweetened vs \
unsweetened and flavor (peach, lemon) are hard constraints when specified.
- **Alcohol**: If query includes beer/wine/kegs, match packaging (keg size, \
bottle/can) and style (IPA vs lager). Do not return NA products for alcoholic \
queries and vice versa.

**Terminology**:
- BIB = bag-in-box syrup
- RTD = ready-to-drink
""",
        ),
        "cooking": VerticalOverlay(
            description=(
                "Cooking equipment: ranges, ovens, fryers, griddles, grills, "
                "steamers, kettles, warmers (not ventilation)"
            ),
            content="""\
### Cooking Equipment — Scoring Guidance

This query involves hot-side cooking equipment.

**Critical distinctions to enforce:**

- **Heat source**: Gas vs electric is a hard requirement when specified. \
LP vs NG is also hard.
- **Oven type**: Convection, combi, deck, conveyor, and pizza ovens are \
different categories. Do not substitute.
- **Fryer type**: Floor vs countertop, split pot vs full pot, tube vs open pot, \
and gas vs electric are key.
- **Power and BTU**: Burner counts and BTU/hr are hard when specified.
- **Holding vs cooking**: Warmers and holding cabinets are not ovens. \
Hot holding does not bake/roast.
""",
        ),
        "dairy_eggs": VerticalOverlay(
            description=(
                "Dairy & eggs: milk, cream, cheese, butter, eggs, "
                "yogurt, dairy alternatives"
            ),
            content="""\
### Dairy & Eggs — Scoring Guidance

This query involves dairy and egg products.

**Critical distinctions to enforce:**

- **Form**: Liquid vs powdered vs frozen. Liquid egg products differ from \
shell eggs; powdered milk differs from fluid milk.
- **Fat %**: Whole vs 2% vs skim; cream types (half-and-half, heavy cream) \
are hard constraints when specified.
- **Cheese format**: Shredded vs sliced vs block vs sauce. Cheese blend \
composition matters when specified (mozzarella vs cheddar blend).
- **Case pack / foodservice sizing**: Gallons, pints, #10 cans, or \
bulk blocks are common; match size when specified.
""",
        ),
        "dry_goods": VerticalOverlay(
            description=(
                "Dry pantry goods: flour, sugar, salt, spices, canned goods, "
                "rice, pasta, oils, sauces, baking supplies"
            ),
            content="""\
### Dry Goods — Scoring Guidance

This query involves shelf-stable pantry goods and ingredients.

**Critical distinctions to enforce:**

- **Package type**: #10 cans vs pouches vs jars; bulk bags (25 lb flour) \
vs retail boxes are not substitutes.
- **Ingredient identity**: Similar items are not interchangeable (e.g., \
baking powder vs baking soda; corn starch vs flour).
- **Foodservice sizing**: Case packs and bulk weights are hard when specified.
""",
        ),
        "disposables": VerticalOverlay(
            description=(
                "Single-use and disposable items: cups, lids, takeout containers, "
                "cutlery, gloves, film/foil, napkins, paper goods"
            ),
            content="""\
### Disposables — Scoring Guidance

This query involves disposable, single-use service items (not reusable tabletop).

**Critical distinctions to enforce:**

- **Lid and container compatibility**: Lid fit is brand and series specific \
(e.g., Solo vs Dart). Do not assume a "universal" lid fits all.
- **Hot vs cold**: Cup and lid materials differ by temperature. PET cold cups \
are not hot cups. Foam vs paper vs PLA have different constraints.
- **Material constraints — regulatory**: Expanded polystyrene (EPS/foam) \
foodserviceware is restricted/banned in multiple US jurisdictions and policies \
change over time. For evaluation, treat foam as a mismatch when the query \
explicitly signals compliance (e.g., "foam-free", "compostable", "BPI \
certified") or names a jurisdiction with EPS restrictions (e.g., California, \
New York). If the query explicitly asks for foam/EPS, matching foam is allowed.
- **Compostable certifications**: BPI Certified Compostable (ASTM D6400 \
for products, ASTM D6868 for coated items) is the US commercial standard. \
Compostable vs biodegradable are not synonyms.
""",
        ),
        "food_prep": VerticalOverlay(
            description=(
                "Food prep equipment: mixers, slicers, processors, scales, "
                "cutters, prep stations (not cookware/smallwares)"
            ),
            content="""\
### Food Prep — Scoring Guidance

This query involves powered food preparation equipment.

**Critical distinctions to enforce:**

- **Machine type**: Mixer vs food processor vs slicer vs chopper are different \
categories.
- **Capacity and size**: Quart capacity, bowl size, blade diameter, and \
throughput are hard constraints when specified.
- **Voltage and phase**: Many larger machines require 208/240V or three-phase.
""",
        ),
        "furniture": VerticalOverlay(
            description=(
                "Restaurant seating, tables, booths, bar stools, "
                "and dining room furniture"
            ),
            content="""\
### Furniture — Scoring Guidance

This query involves restaurant seating and dining room furniture.

**Critical distinctions to enforce:**

- **Outdoor vs indoor**: Outdoor-rated materials (UV, rust resistance) \
are required when query specifies outdoor/patio.
- **Table height**: Standard dining (~29-30"), counter (24–26"), \
bar (28–30") — hard constraint, must match table or counter height. A "bar \
stool" query must not return dining-height chairs.
- **Commercial vs residential grade**: Commercial furniture must withstand \
100+ seatings per day. BIFMA durability standards such as ANSI/BIFMA X5.4 (public/lounge seating) \
and ANSI/BIFMA X5.5 (tables) indicate commercial durability. Welded steel frames, high-density foam (1.8+ lb/ft³), \
commercial-grade upholstery. Residential furniture fails within months at \
restaurant traffic levels.
- **Booth seating**: Single vs double, wall-mounted vs floor-mounted, \
and booth length are hard constraints when specified.
- **Upholstery**: Vinyl vs fabric vs leather differ in cleanliness and \
durability. "Antimicrobial" or "easy clean" claims matter if specified.
""",
        ),
        "janitorial": VerticalOverlay(
            description=(
                "Facility cleaning: sanitizers, floor care, mops, "
                "can liners, paper dispensers, dilution systems"
            ),
            content="""\
### Janitorial and Facility Cleaning — Scoring Guidance

This query involves facility cleaning, sanitation, and janitorial supplies \
(not dishwashing equipment; see warewash overlay for dishmachines).

**Critical distinctions to enforce:**

- **EPA-registered claims and label use**: Sanitizer/disinfectant claims are \
EPA-registered and must be used per label directions ("the label is the law"). \
Food-contact surface sanitizers are distinct from general disinfectants. When a \
query specifies "food-contact", "no-rinse", or "sanitizer" (vs "disinfectant"), \
require the matching claim type—do not substitute a general disinfectant.
- **Sanitizer concentrations (follow label)**: Food-contact sanitizer solutions are \
commonly verified with test strips and specified in ppm ranges (e.g., chlorine \
~50–100 ppm; iodine ~12.5–25 ppm; quats often in the ~200–400 ppm range, \
depending on formulation). When a query specifies sanitizer type or ppm, treat it \
as a hard requirement.
- **Sanitizer test strips are product-specific**: Chlorine vs quat vs iodine \
strips are not interchangeable.
- **Concentrate vs RTU (ready-to-use)**: Concentrates require dilution \
equipment or dilution control systems; RTU is pre-diluted and spray-ready. \
Returning a concentrate for an RTU query is a format mismatch.
- **HACCP / zone color-coded cleaning tools**: Many operations use color-coded \
brushes, squeegees, and cloths to separate tasks/areas, but the exact color \
mapping varies by program. If the query specifies a color, treat the color as a \
hard requirement; do not assume a universal red/yellow/blue/green mapping.
- **Chemical compatibility hazards**: Chlorine bleach + ammonia = toxic \
chloramine gas. Chlorine + acids = chlorine gas release. These are \
safety-critical constraints.

**Terminology**:
- RTU = ready-to-use
- quat = quaternary ammonium sanitizer
""",
        ),
        "frozen_dessert_equipment": VerticalOverlay(
            description=(
                "Frozen dessert equipment: soft serve machines, shake machines, "
                "ice cream dipping cabinets, gelato machines"
            ),
            content="""\
### Frozen Dessert Equipment — Scoring Guidance

This query involves frozen dessert production/holding equipment.

**Critical distinctions to enforce:**

- **Soft serve vs shake vs slush/granita**: Different machines and mixes. \
Do not substitute.
- **Air vs water cooled**: Cooling method is a hard requirement when specified.
- **Number of hoppers/flavors**: 1 vs 2 vs twist is a hard constraint.
- **Mix type**: Dairy vs non-dairy compatibility matters if specified.
""",
        ),
        "refrigeration": VerticalOverlay(
            description=(
                "Refrigeration & freezers for cold storage and cold prep "
                "(reach-ins, undercounters, prep tables, walk-ins; not ice makers)"
            ),
            content="""\
### Refrigeration Equipment — Scoring Guidance

This query involves refrigeration/freezer equipment for cold storage, cold prep, \
or cold display (NOT ice makers; see ice_machines overlay).

**Critical distinctions to enforce:**

- **Reach-in vs undercounter vs walk-in**: Fundamentally different form factors and capacities. \
Walk-in queries should not return reach-in units. Undercounter units are designed for counter \
integration; height/clearance matters when specified.
- **Refrigerator vs freezer vs dual-temp**: Confusing these is a critical error. Match temperature class \
when stated (e.g., freezer, -10°F; refrigerator, 33–41°F).
- **Food-prep refrigeration types**:
  * *Sandwich/salad prep tables* commonly use shallower cutting boards and smaller top pans.
  * *Pizza prep tables* commonly have deeper cutting boards and rails designed around larger pans/toppings.
  * *Mega-top* units expand top-rail capacity.
  If the query specifies pizza vs sandwich vs mega-top, treat it as a hard subtype.
- **Door configuration**: Solid vs glass doors, number of doors/sections, and pass-thru (doors on both sides) \
are hard specs when specified.
- **System configuration**: Self-contained vs remote condenser (common in walk-ins and some high-capacity \
systems) is a hard constraint when specified.
- **Blast chillers vs standard freezers**: Blast chillers support rapid cooling for food safety. Do not treat a \
standard freezer as a blast chiller.

**Terminology equivalences** (do not penalize lexical mismatches when intent aligns):
- lowboy = undercounter refrigerator / freezer
- reach-in = upright commercial refrigerator / freezer
- chef base = refrigerated equipment stand / griddle stand
""",
        ),
        "ice_machines": VerticalOverlay(
            description=(
                "Ice makers, ice machine heads, undercounter ice machines, ice bins, "
                "and ice dispensers (not refrigerators/freezers)"
            ),
            content="""\
### Ice Machines — Scoring Guidance

This query involves commercial ice production or ice dispensing equipment.

**Critical distinctions to enforce:**

- **Ice form / ice type**: Cube (regular/dice/half-dice), crescent, nugget/cubelet/pellet, and flake ice \
have different beverage and display use cases. If the query specifies the ice type, it is a hard constraint.
- **Machine type**:
  * *Modular* (head-only) units require a separate storage bin or dispenser.
  * *Self-contained undercounter* units include a built-in bin and fit under counters.
  Do not return a head-only machine for an undercounter-with-bin query, and do not return a bin-only \
product for an ice-maker query unless the query is explicitly about bins.
- **Condenser / cooling method**: Air-cooled vs water-cooled vs remote-cooled configurations are not \
interchangeable when specified (different utilities + install).
- **Production ratings**: Ice makers often publish "maximum" production at 70°F air / 50°F water and a \
lower AHRI "standard" production at 90°F air / 70°F water. If the query specifies a lbs/day capacity, \
match the correct rating basis when it is stated; otherwise treat the listed range as an approximation.
- **Bin/dispensing configuration**: Ice dispensers (hotel/beverage dispensers) are not simple storage bins. \
If the query says "dispenser", "hotel dispenser", or "chewable nugget dispenser", require a dispensing unit.

**Terminology**:
- nugget ice = cubelet ice = pellet ice (often called "chewable")
- cuber = cube ice machine
- flaker = flake ice machine
""",
        ),
        "serving_holding": VerticalOverlay(
            description=(
                "Serving and holding: hot holding cabinets, soup warmers, "
                "steam tables, heat lamps, food wells, display cases"
            ),
            content="""\
### Serving and Holding — Scoring Guidance

This query involves equipment for holding and serving prepared food.

**Critical distinctions to enforce:**

- **Heated holding vs cooking**: Holding cabinets and heat lamps do not cook. \
Do not substitute.
- **Wet vs dry**: Steam tables and food wells differ (wet requires water). \
If query specifies wet/dry, treat as hard.
- **Sneeze guards and display**: Display cases may be heated or refrigerated; \
match temperature class.
""",
        ),
        "storage_transport": VerticalOverlay(
            description=(
                "Storage and transport: shelving, racks, carts, ingredient bins, "
                "food pan carriers, transport cabinets"
            ),
            content="""\
### Storage and Transport — Scoring Guidance

This query involves shelving, racks, carts, and transport systems.

**Critical distinctions to enforce:**

- **Rack type**: Sheet pan racks, bun pan racks, dish racks, and speed racks \
(kitchen) are different. Match rack spacing and pan size when specified.
- **Material**: Stainless vs chrome vs polymer differ in environment constraints \
(walk-in, dishroom, corrosion).
- **Load rating**: Weight capacity is hard when specified.
""",
        ),
        "smallwares": VerticalOverlay(
            description=(
                "Pans, food storage, utensils, cookware, "
                "and kitchen hand tools (not disposables)"
            ),
            content="""\
### Smallwares — Scoring Guidance

This query involves reusable kitchen tools and containers.

**Critical distinctions to enforce:**

- **Hotel pan vs GN pan systems**: US hotel pans and European GN pans are \
different sizing standards; they are not interchangeable.
- **Pan depth**: Standard depths (2.5", 4", 6") matter. If depth is specified, \
it is a hard requirement.
- **Cutting board / tool color-coding**: Many operations use HACCP-style color coding to \
separate tasks, but mappings vary by program. If the query specifies a color, \
treat that color as a hard requirement; do not "normalize" colors to an assumed \
meat/produce map.
- **Container system compatibility**: Lid fit and container series matter \
(Cambro vs Carlisle vs Rubbermaid are not always interchangeable).
""",
        ),
        "tabletop": VerticalOverlay(
            description=(
                "Tabletop: plates, bowls, glassware, flatware, servingware, "
                "barware (reusable, not disposables)"
            ),
            content="""\
### Tabletop — Scoring Guidance

This query involves reusable front-of-house dining and bar serviceware.

**Critical distinctions to enforce:**

- **Material**: Porcelain vs melamine vs glass vs stainless differ in durability \
and use. If query specifies one, treat as hard.
- **Dimensions**: Plate diameter and bowl capacity are hard when specified.
- **Glassware type**: Pint vs rocks vs wine glass vs martini are distinct.
""",
        ),
        "ventilation": VerticalOverlay(
            description=(
                "Kitchen ventilation: hoods, make-up air, exhaust fans, "
                "filters, fire suppression (not cooking equipment)"
            ),
            content="""\
### Ventilation — Scoring Guidance

This query involves kitchen ventilation systems and accessories.

**Critical distinctions to enforce:**

- **Hood type**: Type I (grease) vs Type II (heat/steam/condensate) matters. \
Do not substitute when specified.
- **Length and CFM**: Hood length, CFM, and filter type are hard constraints.
- **Fire suppression**: If query includes suppression, treat as hard.
""",
        ),
        "proteins": VerticalOverlay(
            description=(
                "Meat and seafood: beef, pork, poultry, fish, shellfish, "
                "processed proteins"
            ),
            content="""\
### Proteins — Scoring Guidance

This query involves meat, poultry, fish, or other protein products.

**Critical distinctions to enforce:**

- **Species and cut**: Ribeye vs strip vs tenderloin are not substitutes. \
If cut is specified, treat as hard.
- **Fresh vs frozen**: Frozen and fresh are not interchangeable when specified.
- **Size counts**: Seafood counts (e.g., 21/25 shrimp) are hard constraints.
- **Case pack / portion control**: Catch weight vs portioned items differ.
""",
        ),
        "prepared_foods": VerticalOverlay(
            description=(
                "Prepared foods: frozen entrees, appetizers, ready-to-eat items, "
                "par-cooked products"
            ),
            content="""\
### Prepared Foods — Scoring Guidance

This query involves prepared or partially prepared foods.

**Critical distinctions to enforce:**

- **Ready-to-eat vs par-cooked vs raw**: Do not substitute when specified.
- **Frozen vs refrigerated vs shelf-stable**: Storage state is a hard constraint.
- **Case pack and portion size**: Match portion counts and weights when specified.
""",
        ),
        "produce": VerticalOverlay(
            description=(
                "Produce: fruits, vegetables, fresh herbs, fresh-cut, "
                "bulk produce and case packs"
            ),
            content="""\
### Produce — Scoring Guidance

This query involves fruits, vegetables, and fresh produce.

**Critical distinctions to enforce:**

- **Fresh vs frozen**: Do not substitute when specified.
- **Organic vs conventional**: Hard constraint when specified.
- **Case pack and size**: Count, size grade, and pack are key.
""",
        ),
        "plumbing": VerticalOverlay(
            description=(
                "Commercial kitchen plumbing & fixtures: sinks, faucets, floor drains, "
                "grease traps/interceptors, and plumbing hardware"
            ),
            content="""\
### Plumbing and Fixtures — Scoring Guidance

This query involves commercial kitchen plumbing components: stainless sinks, \
faucets, pre-rinse units, drains/floor troughs, and grease management.

**Critical distinctions to enforce:**

- **Sink type matters**: Hand sinks, prep sinks, mop/service sinks, and compartment sinks are \
different compliance and workflow tools. Do not substitute across sink types when the query is explicit.
- **Compartment counts and drainboards**: "3-compartment" vs "1-compartment" is a hard distinction. \
Drainboard presence and LEFT/RIGHT orientation are often specified and should be treated as hard.
- **Mount style / hole pattern**: Wall-mount vs deck/splash-mount faucets are not interchangeable. \
Commercial faucets are frequently specified by "centers" (e.g., 8" adjustable centers) and by inlet \
type/size; treat these as hard when present.
- **Pre-rinse assemblies**: A pre-rinse unit includes a spray valve + hose + spring (often with an add-on \
faucet). Do not return a standard spout faucet for a "pre-rinse" query unless the listing clearly includes \
the spray assembly.
- **Grease traps vs interceptors**: Under-sink grease traps are commonly rated by flow (GPM) and grease \
capacity (lb). Large grease interceptors are higher capacity and different installation class. When the \
query gives GPM or lb rating, it is a hard spec.

**Terminology**:
- service sink = mop sink
- splash mount = deck mount (context: faucet mounting on backsplash/deck of sink)
- floor trough = trench drain
""",
        ),
        "waste_reduction": VerticalOverlay(
            description=(
                "Waste handling and waste reduction: garbage disposers, waste pulpers, "
                "trash compactors, and fryer-oil disposal equipment"
            ),
            content="""\
### Waste Handling and Waste Reduction — Scoring Guidance

This query involves back-of-house waste equipment: commercial garbage disposers, \
waste pulpers/extractors, trash compactors, or used-fryer-oil handling tools.

**Critical distinctions to enforce:**

- **Garbage disposer vs waste pulper vs trash compactor**:
  * A *garbage disposer* (in-sink disposer) grinds waste and sends it down plumbing.
  * A *waste pulper / extractor* breaks food waste down into a slurry and often separates \
solids/liquids to reduce volume.
  * A *trash compactor* compresses waste into bags/containers; it does not grind or use plumbing.
  These are different product categories—do not substitute.
- **Install constraints are often hard**: Voltage/phase, horsepower, inlet/bowl/mounting collar type, \
and throughput ratings can define fit. If the query specifies any of these, treat as hard.
- **Oil disposal is its own class**: Shortening/oil disposal units (oil caddies) are for transferring used \
fryer oil safely. Do not return solid-waste equipment for an "oil disposal" query.

**Terminology**:
- waste pulper = pulper/extractor = waste extractor (depending on whether dewatering is included)
- oil caddy = shortening disposal unit
""",
        ),
        "warewash": VerticalOverlay(
            description=(
                "Commercial dishwashers and glasswashers, racks, dishtables, "
                "and dishmachine chemicals (not general janitorial)"
            ),
            content="""\
### Warewashing — Scoring Guidance

This query involves commercial warewashing equipment (dishwashers, glasswashers, \
pot/utensil washers), ware racks, and dishmachine chemicals (detergent, rinse aid, \
dishmachine sanitizer).

**Critical distinctions to enforce:**

- **Machine class / throughput**:
  * Undercounter / bar glasswashers (small footprint)
  * Door-type / hood-type (single-rack, 20×20 racks common)
  * Conveyor / flight-type (high volume)
  These are different scales—do not substitute a bar glasswasher for a conveyor query.
- **Sanitization method**:
  * High-temp machines sanitize via hot-water final rinse (typically requiring a booster heater).
  * Low-temp machines sanitize via chemical sanitizer in the final rinse.
  If the query specifies high-temp vs low-temp (or "chemical sanitizing"), treat as hard.
- **Rack size**: 20×20 racks are a common standard for many door-type/conveyor machines; if a query specifies \
rack size or "20×20", enforce compatibility.
- **Ventless / hood requirements**: "Ventless"/"hoodless" dishmachines use heat recovery/condensing designs. \
If the query specifies ventless, it is a hard requirement; do not return standard hood-required machines.
- **Chemical type and format**: Dishmachine detergents, rinse aids, and sanitizers are distinct products. \
Chlorine vs iodine vs other sanitizer formulations are not automatically interchangeable when specified. \
Concentrate vs ready-to-use vs solid block are format constraints when specified.

**Compatibility rule**: If the query includes a machine brand/model, chemical results must be explicitly \
compatible with that machine type (high-temp vs low-temp) and feeding system when stated.
""",
        ),
    },
)
