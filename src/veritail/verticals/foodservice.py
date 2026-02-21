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
- **Frozen drink machines**: Granita (non-carbonated slush, no dairy) vs \
frozen carbonated beverage machines are different machines despite visual \
similarity — confusing them is a category error.
- **Draft beer**: Direct draw (short draw, no glycol) vs long-draw \
(glycol-cooled lines) are different systems. Number of taps and kegerator vs \
jockey box are hard specs.
- **Tea equipment**: Hot tea brewers vs iced tea brewers are different \
machines. Capacity (3 gal vs 5 gal) is a hard spec.
- **Bar blenders**: Sound-enclosed bar blenders (drink-specific programs) vs \
high-performance blenders (smoothie programs, power-focused) serve different \
operational needs.""",
        ),
        "beverages": VerticalOverlay(
            description=(
                "Consumable drink products — coffee beans, tea, juice, "
                "soda syrup, bottled water (NOT beverage equipment/machines)"
            ),
            content="""\
### Beverages (Consumable Products) — Scoring Guidance

This query involves consumable beverage products — the drinks themselves, \
not the machines that dispense or brew them. Coffee beans, tea leaves, \
juice, soda syrup, bottled water, and related drink products fall here. \
Queries for espresso machines, coffee brewers, fountain dispensers, or \
other equipment belong to the beverage equipment overlay.

**Critical distinctions to enforce:**

- **Coffee roast level**: Light, medium, dark, French, and Italian are \
distinct roast profiles with named synonyms: City = medium, Full City = \
medium-dark, Vienna = dark, French = very dark (oily), Italian = \
near-black. Roast level is a hard constraint — returning dark roast for \
a "light roast" query is a relevance failure. Trade names like "breakfast \
blend" or "espresso roast" imply medium-light and dark respectively but \
are marketing terms, not standardized grades.
- **Grind size**: Whole bean, coarse (French press), medium (drip), fine \
(espresso), extra-fine (Turkish) are functionally distinct — using the \
wrong grind damages equipment or ruins extraction. Grind size is a hard \
constraint when specified. "Drip grind" = medium grind. "Espresso grind" \
= fine grind. Whole bean is never a match for a query specifying a ground \
size, and vice versa.
- **Single-serve pod systems**: K-Cup (Keurig), Nespresso OriginalLine, \
and Nespresso Vertuo are physically incompatible capsule formats — cross-\
matching is a hard failure. Nespresso Original and Vertuo capsules are \
different sizes, shapes, and barcode systems and cannot be interchanged. \
ESE (Easy Serving Espresso) pods are a fourth distinct format.
- **Decaf process**: Swiss Water Process (chemical-free, water-only) vs \
solvent-based (methylene chloride or ethyl acetate / "sugarcane process") \
are distinct methods. When a query specifies "Swiss Water" or \
"chemical-free decaf," solvent-processed decaf is a hard mismatch.
- **Coffee species**: Arabica vs Robusta are distinct species. Robusta has \
roughly 2x the caffeine, more bitterness, and is common in instant coffee \
and Italian espresso blends for crema. "100% Arabica" is a hard constraint \
when specified — blends containing Robusta do not qualify.
- **Tea type**: Black, green, white, oolong, pu-erh, and herbal/tisane \
are fundamentally different products — herbal is technically not tea \
(Camellia sinensis) at all. Type is a hard constraint; returning green \
tea for a "black tea" query is a category error. Chai = spiced black tea \
(not a separate tea type).
- **Tea grade (orthodox)**: OP (Orange Pekoe) = whole-leaf, BOP (Broken \
Orange Pekoe) = broken-leaf, FBOP (Flowery BOP) = broken with tips. \
These indicate leaf size and quality, not flavor. CTC (crush-tear-curl) \
is an entirely different processing method producing uniform granules — \
CTC dominates tea bags and foodservice chai. Fannings and dust are the \
smallest grades, used in commercial tea bags for fast, strong infusion.
- **Tea form factor**: Loose leaf, sachets (pyramid bags with whole-leaf \
tea), standard tea bags (fannings/dust in paper), powdered/instant (matcha \
is ground whole-leaf; instant tea is extract), and RTD (ready-to-drink \
bottled/canned). Form factor is a hard constraint when specified.
- **Fountain syrup — BIB**: Bag-in-box (BIB) syrup concentrate is the \
standard foodservice format, typically 2.5- or 5-gallon bags. Post-mix \
systems (BIB syrup mixed with carbonated water at the dispenser, standard \
ratio 5:1 water-to-syrup for regular, ~4.75:1 for diet) vs pre-mix \
(pre-blended ready-to-dispense beverage) are incompatible delivery \
systems. Brix measures sugar concentration in the finished drink and is \
used to calibrate fountain dispensers — a process called "Brixing." \
Returning BIB syrup for a query seeking finished bottled soda, or vice \
versa, is a format mismatch.
- **Juice processing**: NFC (not from concentrate) = pasteurized, never \
concentrated, requires refrigeration; from-concentrate (FC/reconstituted) \
= water removed then reconstituted, shelf-stable or refrigerated; \
fresh-squeezed = unpasteurized, shortest shelf life; frozen concentrate = \
sold frozen for on-site dilution. These are distinct product tiers — NFC \
is a hard constraint when specified. "100% juice" is a regulatory term \
(no added sweeteners) orthogonal to processing method.
- **Carbonated water types**: Sparkling mineral water (naturally \
carbonated or carbonated spring water with dissolved minerals), seltzer \
(plain carbonated water, no minerals added), club soda (carbonated water \
with added sodium bicarbonate / potassium sulfate for slight salinity), \
and tonic water (carbonated water with quinine and sweetener, ~80-130 \
cal/serving) are four distinct products. Tonic water especially must \
never be substituted for seltzer or club soda — it is sweetened and \
caloric.
- **Cold brew concentrate vs RTD cold brew**: Concentrate requires \
dilution (typically 1:1 to 2:1 water-to-concentrate); RTD (ready-to-drink) \
is pre-diluted. Returning concentrate for an RTD query or vice versa is \
a format mismatch.

**Commercial pack formats** (hard constraint when query specifies format):
- Frac pack / pillow pack = pre-measured single-pot coffee portion \
(typically 1.75–2.5 oz for a 12-cup brewer), sold in cases of 24–48
- BIB = bag-in-box syrup (2.5 gal or 5 gal); a 5-gal BIB at 5:1 ratio \
yields ~30 gal / ~3,840 oz of finished beverage
- Case of cans: typically 24-pack of 12 oz cans for foodservice
- Bottles: 20 oz (single-serve), 2 L (table), 5-gallon (water cooler)
- Bulk coffee: 2 lb or 5 lb bags (whole bean or ground) for commercial \
brewing; 12 oz bags are retail-size and a weak match for commercial queries

**Terminology equivalences** (do not penalize lexical mismatches when \
intent aligns):
- frac pack = fractional pack = pillow pack = portion pack (single-pot \
pre-measured coffee)
- BIB = bag-in-box = fountain syrup
- cold brew = cold-brewed coffee (not iced coffee — iced coffee is hot-\
brewed then chilled)
- matcha = powdered green tea (stone-ground whole leaf, not instant tea)
- chai = masala chai = spiced tea (black tea base unless otherwise stated)
- OP = Orange Pekoe (leaf grade, not a flavor)
- espresso roast = dark roast coffee (marketing term, not a grind size — \
does not imply espresso grind)""",
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
        "dairy_eggs": VerticalOverlay(
            description=(
                "Dairy products, eggs, butter, cheese, cream, "
                "and cultured dairy for foodservice"
            ),
            content="""\
### Dairy & Eggs — Scoring Guidance

This query involves dairy products, eggs, butter, cheese, cream, milk, \
or cultured dairy items for commercial foodservice.

**Critical distinctions to enforce:**

- **Egg form is a hard constraint**: Shell eggs, liquid whole eggs, \
liquid whites, liquid yolks, frozen eggs, and dried/powdered eggs are \
distinct products — they are NOT interchangeable. Frozen whole eggs and \
yolks contain added sugar, salt, or corn syrup to prevent gelation; \
dried whites are glucose-removed and may contain whipping aids (sodium \
lauryl sulfate). Returning liquid whites for a "shell eggs" query or \
dried eggs for a "liquid whole egg" query is a hard failure.
- **Egg grades**: USDA AA (firm thick whites, round yolks, air cell \
≤ 1/8"), A (slightly less firm whites, air cell ≤ 3/16"), B (thin \
whites, flat yolks — used primarily for breaker/processed products, \
rarely sold retail). Grade is a hard constraint when specified.
- **Egg sizing is by weight per dozen, not per egg**: Jumbo ≥ 30 oz, \
Extra Large ≥ 27 oz, Large ≥ 24 oz, Medium ≥ 21 oz, Small ≥ 18 oz, \
Peewee ≥ 15 oz. Recipes and foodservice specs default to Large unless \
stated otherwise. Size is a hard constraint when specified.
- **Egg housing claims**: Cage-free (indoor, uncaged), free-range \
(outdoor access — USDA definition is minimal), pasture-raised (no \
USDA standard — relies on third-party certification like Certified \
Humane). These are not interchangeable tiers; each has distinct \
procurement and labeling implications.
- **Butter grades**: USDA AA (highest — fine, highly pleasing flavor), \
A (pleasing, may have slight off-flavors), B (fairly pleasing — \
typically industrial/foodservice only). All US butter must be ≥ 80% \
milkfat. Grade is a hard constraint when specified.
- **European-style butter** (82–86% fat) vs American-style (80% fat) \
is a critical distinction for baking and lamination. Higher fat means \
lower moisture, better plasticity for croissant and puff pastry doughs. \
"Lamination butter" or "dry butter" specifically implies 82%+ fat. Do \
not return standard 80% butter for a European-style or lamination query.
- **Milk fat designations (FDA 21 CFR 131)**: Whole ≥ 3.25%, 2% \
reduced-fat = 2%, 1% low-fat = 1%, skim/nonfat < 0.5%. These are \
legally defined — "2% milk" is not "low-fat milk." Fat percentage is \
a hard constraint when specified.
- **Cream hierarchy (FDA)**: Half-and-half (10.5–18% fat), light cream \
(18–30%), light whipping cream (30–36%), heavy cream / heavy whipping \
cream (≥ 36%). "Heavy cream" and "heavy whipping cream" are the same \
product (≥ 36% fat). Light cream is NOT whipping cream — it will not \
whip. Returning light cream for a "heavy cream" query is a hard failure.
- **Cheese: process vs natural**: Pasteurized process cheese (real \
cheese + emulsifiers), pasteurized process cheese food (≥ 51% cheese, \
more moisture, softer), pasteurized process cheese spread (spreadable \
at 70 °F, 44–60% moisture), and "cheese product" (no FDA standard of \
identity — unregulated term). These are a legal hierarchy, not \
synonyms. "American cheese" may be any of these — check labeling.
- **Cheese form matters**: Shredded cheese contains anti-caking agents \
(cellulose, potato starch) that impair melting and sauce-making. Block \
cheese has no additives and melts cleanly. Sliced, crumbled, and \
shredded are distinct forms. When a query specifies form, it is a hard \
constraint — do not return shredded for a "block" query.
- **Cheese aging and classification**: Fresh/unripened (ricotta, \
mascarpone, cream cheese, cottage — high moisture, short shelf life), \
soft-ripened (brie, camembert — mold-ripened exterior), semi-soft \
(havarti, muenster), semi-hard (cheddar, gouda, gruyère), hard/grating \
(parmesan, pecorino, Grana Padano — aged 9–36+ months, low moisture). \
Age class determines functionality; hard cheeses grate, fresh cheeses \
spread — confusing these categories is a relevance error.
- **PDO/PGI cheese names in the US**: "Parmigiano-Reggiano" is a \
protected DOP name (must be Italian-made); "parmesan" is generic in \
the US and may be domestic. Similarly, "gruyère," "feta," "asiago," \
and "fontina" are generic in the US but protected in the EU. When a \
query uses the full PDO name (e.g., "Parmigiano-Reggiano"), only the \
authentic product satisfies it. When it uses the generic English name \
(e.g., "parmesan"), domestic products are acceptable matches.
- **Cream cheese vs Neufchâtel**: Cream cheese ≥ 33% fat, ≤ 55% \
moisture. Neufchâtel 20–33% fat, ≤ 65% moisture. Often marketed as \
"1/3 less fat cream cheese" but they are distinct FDA standards of \
identity — do not treat as identical when the query specifies one.
- **Cultured dairy products**: Sour cream (≥ 18% fat, curdles when \
heated), crème fraîche (~30% fat, heat-stable — will not curdle), \
yogurt (≥ 3.25% fat for full-fat), Greek/strained yogurt (higher \
protein, thicker — no separate FDA standard, must meet yogurt SOI), \
cultured buttermilk (typically 1–2% fat, liquid, tangy). These are \
functionally different — sour cream and crème fraîche are not \
interchangeable in hot applications.
- **Kosher dairy (chalav Yisrael)**: Milk produced under continuous \
rabbinical supervision from milking through processing. This is a hard \
constraint — chalav Yisrael products are NOT interchangeable with \
standard kosher dairy (OU-D). When a query specifies chalav Yisrael, \
only products bearing that specific certification are acceptable.

**Commercial pack sizes** (do not penalize pack-size variants unless \
the query specifies an exact size):
- Eggs: 15-dozen case (standard), 30-dozen case (volume), flats of 30
- Butter: 1 lb prints (36/case), 55 lb bulk blocks, 25 kg blocks \
(European-style/lamination)
- Shredded cheese: 5 lb bags (standard foodservice), 4x5 lb cases
- Block cheese: 10 lb loaves, 20 lb blocks, 40 lb blocks
- Milk/cream: half-pint, pint, quart, half-gallon, gallon, 5-gallon \
bag-in-box (dispensing)

**Terminology equivalences** (do not penalize lexical mismatches when \
intent aligns):
- heavy cream = heavy whipping cream (both ≥ 36% fat)
- Parmigiano-Reggiano ≠ parmesan (PDO vs generic — see rules above)
- American cheese = process cheese slices (colloquial, but check \
product tier)
- Swiss cheese = Emmentaler-style (US generic, not Swiss PDO)
- cottage cheese = curds and whey (informal)
- buttermilk = cultured buttermilk (traditional buttermilk is \
unavailable commercially)
- egg whites = albumen (liquid or dried)
- egg yolks = liquid yolks (in commercial context)""",
        ),
        "dry_goods": VerticalOverlay(
            description=(
                "Pantry staples, canned goods, baking, oils, sauces, "
                "condiments, spices, rice, pasta, and dry ingredients"
            ),
            content="""\
### Dry Goods — Scoring Guidance

This query involves pantry staples, canned goods, baking ingredients, oils, \
vinegars, sauces, condiments, spices, rice, pasta, flour, sugar, or other \
shelf-stable dry ingredients for commercial foodservice.

**Critical distinctions to enforce:**

- **Can size numbering**: Industry-standard sizes are hard specs — \
#10 (~96–117 oz / 6–7.3 lb, institutional standard), \
#5 (~56 oz / 3.5 lb), #2.5 (~26–29 oz), #303 (~15–16 oz), \
#300 (~14–15 oz). The numbering is NOT sequential by size — #303 and #300 \
are close in volume despite the number gap. A #10 can query must not return \
#303 cans or retail cans.
- **Canned goods packing medium**: Heavy syrup, light syrup, juice pack, \
water pack, and solid pack are distinct specifications affecting sugar \
content, cost, and recipe suitability. USDA grades for canned vegetables — \
Grade A (Fancy), Grade B (Extra Standard), Grade C (Standard) — indicate \
quality tier and are hard specs when specified.
- **Oil: fryer vs finishing**: Fryer oils require smoke points >400 °F \
(canola ~400–475 °F, refined peanut ~450 °F, high-oleic soybean ~450 °F, \
refined avocado ~480–520 °F). Finishing oils (EVOO, toasted sesame, walnut, \
truffle) have low smoke points and are used unheated for flavor — returning \
a finishing oil for a "fryer oil" query is a category error and vice versa. \
"High oleic" oils last ~50% longer in fryers and are a premium spec. \
Shortening (solid fat) and liquid fry oil are distinct products.
- **Oil packaging**: Institutional oil is sold in 35 lb jugs (carboys/JIB), \
gallon jugs, and pails — not retail bottles. Pack size is a hard spec when \
specified.
- **Flour — protein content determines function**: Bread flour (~12–14% \
protein), all-purpose (~10–12%), pastry (~8–9%), cake flour (~7–8%). \
These are NOT interchangeable — protein drives gluten development. \
00 flour (Tipo 00) is an Italian grind fineness designation, NOT a protein \
level — 00 can range from ~8% to 14% protein depending on the wheat. \
Semolina (durum wheat, coarse grind) is a hard constraint for dried pasta \
and specific breads. Whole wheat flour includes bran and germ, \
fundamentally different from white flours.
- **Corn products — not interchangeable**: Cornstarch (pure starch, \
thickener), corn flour (finely ground whole kernel), cornmeal (coarsely \
ground, >0.2 mm particle), and masa harina (nixtamalized, required for \
tortillas/tamales) are distinct products. Substituting one for another \
produces incorrect results.
- **Sugar types**: Granulated, powdered/confectioners (graded by fineness: \
10X = ultrafine for glazes, 6X = standard baking, 4X = coarse), brown \
(light vs dark — molasses content differs), turbinado/demerara (raw, \
coarse crystal), and liquid sugar/simple syrup (for high-speed production). \
The "X" grade is a hard spec when specified.
- **Rice varieties — not interchangeable**: Long grain (separate, fluffy), \
medium grain (slightly sticky), short grain (very sticky). Within these: \
jasmine (aromatic, soft, clingy), basmati (aromatic, grains elongate, \
stay separate), arborio (high-starch, for risotto — releases starch when \
stirred). Parboiled/converted rice holds on steam tables far longer than \
regular white rice — critical for institutional service. \
A "basmati" query must not return arborio or short grain.
- **Pasta**: Dried (semolina + water, 12% moisture, long shelf life, \
8–12 min cook) vs fresh (egg + 00/AP flour, ~30% moisture, perishable, \
2–4 min cook) are fundamentally different products. Egg pasta vs semolina \
pasta differ in richness and application. Shape/cut is a hard spec — \
penne, rigatoni, spaghetti, linguine, etc. are not interchangeable \
despite all being "pasta."
- **Spice form — hard constraint**: Whole, cracked, ground, rubbed, and \
flaked are distinct processing levels that affect release rate, texture, \
and application. Ground is ~2× the potency of rubbed by volume \
(substitution: 1 tsp rubbed ≈ ½ tsp ground). Whole spices (peppercorns, \
cinnamon sticks, bay leaves) are not substitutes for ground in recipes \
requiring even distribution. Form is a hard constraint when specified.
- **Leavening agents — not interchangeable**: Baking soda (pure sodium \
bicarbonate, needs acid) vs baking powder (includes acid, self-contained). \
Double-acting baking powder (reacts on mixing + on heating) is the \
commercial standard — single-acting is rare and not a substitute. Yeast \
types: active dry (requires proofing/hydration), instant/rapid-rise \
(no proofing, use 25% less by weight), fresh/compressed (perishable, \
~70% moisture, 2-week shelf life). These have different hydration \
requirements and are not freely interchangeable.
- **Salt grain size — affects volume measurement**: 1 tsp table salt ≈ \
1.5 tsp Morton kosher ≈ 2 tsp Diamond Crystal kosher. Diamond Crystal \
and Morton kosher are NOT interchangeable by volume despite both being \
"kosher salt" — hollow pyramid vs rolled flake crystals. Foodservice \
specs should specify brand or weight, not volume alone.
- **Vinegar types**: Distilled white (sharp, for pickling/cleaning), \
apple cider (fruity, dressings), rice (mild, low acid, Asian cuisine), \
balsamic (aged, sweet-tart, finishing), sherry (complex, aged) — each has \
distinct acidity and flavor profile. Returning balsamic for a "distilled \
white vinegar" query is a category error.
- **Sauce/condiment pack format**: Portion control packets (0.25–2 oz), \
squeeze bottles (tabletop), gallon jugs (back-of-house), \
#10 cans (bulk prep), bag-in-box/pouches (dispenser systems, 1.5–3 gal). \
Pack format is a hard spec when specified — a gallon jug is not a \
substitute for portion packets.

**Terminology equivalences** (do not penalize lexical mismatches when \
intent aligns):
- powdered sugar = confectioners sugar = icing sugar (graded 10X/6X/4X)
- AP flour = all-purpose flour
- 00 flour = doppio zero = Tipo 00
- converted rice = parboiled rice
- EVOO = extra virgin olive oil (finishing oil, not for frying)
- high-oleic = premium fryer oil spec (longer fry life)
- carboy = 35 lb jug = JIB (jug-in-box)
- instant yeast = rapid-rise yeast = bread machine yeast
- masa = masa harina (dried nixtamalized corn flour)
- light brown sugar = golden brown sugar
- kosher salt brand matters: Diamond Crystal ≠ Morton by volume""",
        ),
        "disposables": VerticalOverlay(
            description=(
                "Disposable food packaging, cups, lids, to-go containers, "
                "paper products, and single-use supplies"
            ),
            content="""\
### Disposables — Scoring Guidance

This query involves disposable food packaging, cups, lids, to-go \
containers, bags, paper products, gloves, or other single-use supplies.

**Critical distinctions to enforce:**

- **Hot cups vs cold cups**: Functionally incompatible. Paper hot cups \
(PE-lined) handle 200 °F+; PET cold cups deform above ~140 °F. PLA \
(compostable plastic) cups are cold-only — heat deflection at ~115–135 °F. \
Returning a cold cup for a "hot cup" query is a hard failure.
- **Cup/lid compatibility**: Lid fit depends on top diameter (commonly \
80 mm or 90 mm), wall thickness, and seal design (friction fit vs tab \
lock). Lids are often brand/line-specific — a Solo Traveler lid fits \
Solo hot cups but not Dart cups of the same nominal size. Returning an \
incompatible lid is a hard failure.
- **Material constraints — regulatory**: Expanded polystyrene (EPS/foam) \
is banned for foodservice in 12+ US states (NY, CA, MD, ME, VT, NJ, CO, \
VA, WA, DE, OR, RI). Returning foam products for queries from \
ban-affected jurisdictions or for "eco-friendly" / "compostable" queries \
is a hard failure.
- **Compostable certifications**: BPI Certified Compostable (ASTM D6400 \
for products, ASTM D6868 for coated items) is the US commercial standard. \
"Biodegradable" and "compostable" are legally distinct claims in multiple \
states — do not treat them as equivalent. "Plant-based" or "bio-based" \
does not imply compostable.
- **Container sizing**: All dimensions are hard specs. Cups: oz (8, 12, \
16, 20, 24, 32). Clamshells: L×W (6×6, 8×8, 9×9). Deli containers: oz. \
Food wrap rolls: width in inches (12", 18", 24"). An 8 oz cup is not a \
substitute for a 12 oz cup.
- **To-go container types**: Clamshell (hinged-lid), two-piece \
(base + separate lid), compartmentalized (2 or 3 sections), and soup \
containers are distinct form factors — each serves different menu items.
- **Microwave safety**: PP containers are microwave-safe; PS and PET are \
not. Hard constraint when "microwave-safe" is specified.
- **Glove material**: Nitrile, vinyl, latex, and poly are distinct \
materials with different puncture resistance, allergen profiles (latex \
allergy), and cost. Powdered vs powder-free is a hard spec. Material is \
a hard constraint when specified.
- **Catering disposables**: Disposable aluminum steam table pans and lids, \
chafing fuel (Sterno), and disposable serving utensils are catering-specific \
— distinct from everyday disposables.

**Commercial pack sizing**: Disposables are sold in case packs (1000-count \
cups, 500-count containers, 200-count plates). Retail-size packaging \
(10-count, 50-count) is a weak match for commercial queries. Do not \
penalize single-unit results when the query specifies a single item.

**Terminology equivalences** (do not penalize lexical mismatches when \
intent aligns):
- clamshell = hinged container = take-out container
- SOS bag = self-opening sack (flat-bottom paper bag)
- Sterno = chafing fuel (genericized brand)
- deli container = round plastic container with lid
- poly gloves = food handling gloves (thin, loose-fit polyethylene)""",
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
        "furniture": VerticalOverlay(
            description=(
                "Restaurant seating, tables, booths, bar stools, "
                "and dining room furniture"
            ),
            content="""\
### Restaurant Furniture — Scoring Guidance

This query involves restaurant seating, tables, booths, bar stools, or \
other commercial dining room furniture.

**Critical distinctions to enforce:**

- **Seating height classes**: Dining (17–19" seat height), counter (24–26"), \
bar (28–30") — hard constraint, must match table or counter height. A "bar \
stool" query must not return dining-height chairs.
- **Commercial vs residential grade**: Commercial furniture must withstand \
100+ seatings per day. BIFMA certifications (X5.1, X5.4, X5.6) indicate \
commercial durability. Welded steel frames, high-density foam (1.8+ lb/ft³), \
commercial-grade upholstery. Residential furniture fails within months at \
restaurant traffic levels.
- **Booth seating**: Single vs double, wall-mounted vs floor-mounted, length \
(36/42/48" per seat) are hard specs. Vinyl vs fabric upholstery. \
Channel-back, smooth, tufted are distinct styles.
- **Indoor vs outdoor**: Outdoor requires weather-resistant materials \
(powder-coated aluminum, resin, teak, marine-grade polymer). Indoor \
upholstered furniture will deteriorate outdoors. Hard failure when \
"patio" or "outdoor" is specified.
- **Stacking**: Stackable chairs are a distinct feature for banquet and \
multi-purpose use. Stack capacity and dolly compatibility matter.
- **Fabric durability**: Wyzenbeek abrasion test — under 15,000 double \
rubs = residential, 30,000+ = commercial. Vinyl is standard for restaurants \
(easy clean, bleach-resistant). Material type is a hard constraint when \
specified.
- **Fire safety**: CA TB 133 for upholstered seating in public occupancy \
buildings. Hard requirement when specified.
- **Table tops vs bases**: Often sold separately in commercial settings. \
When query specifies "table top" or "table base," return only that \
component. Shape, size, and material are hard specs.

**Terminology equivalences** (do not penalize lexical mismatches when \
intent aligns):
- banquet chair = stacking banquet chair = ballroom chair
- captain's chair = arm chair (restaurant seating with armrests)
- deuce = two-top = table for two
- four-top = table for four
- T-mold edge = vinyl edge banding (table top edge finish)""",
        ),
        "ice_cream": VerticalOverlay(
            description=(
                "Soft serve machines, batch freezers, gelato cases, "
                "and frozen dessert equipment"
            ),
            content="""\
### Frozen Dessert Equipment — Scoring Guidance

This query involves soft serve machines, batch freezers, gelato cases, \
dipping cabinets, or other frozen dessert equipment.

**Critical distinctions to enforce:**

- **Soft serve vs batch freezer vs dipping cabinet**: Fundamentally \
different machines. Soft serve = continuous freezer dispensing on demand \
(servings/hour). Batch freezer = discrete batches (quart capacity per \
cycle, 2–30+ qt). Dipping cabinet = passive cold display for pre-made \
tubs (tub count 4–12+). Confusing any pair is a category error.
- **Soft serve**: Flavor count (single, twin-twist/two-flavor, \
three-flavor) is a hard spec. Feed system — gravity (hopper-on-top, \
lower volume) vs pressurized (separate mix cabinet, higher overrun) — \
determines capacity. Overrun % affects economics. Countertop vs floor is \
a form factor constraint.
- **Batch freezer**: Quart capacity per batch is a hard spec. Cycle time \
determines throughput. Manual vs auto extraction. Water-cooled vs \
air-cooled compressor.
- **Dipping cabinet**: Tub count (4, 6, 8, 12) is a hard spec. Curved \
glass vs flat glass vs solid lid. Forced-air vs gravity-cold. LED lighting.
- **Frozen yogurt machines vs soft serve**: Mechanically similar but \
frozen yogurt machines optimize for yogurt-based mixes (different viscosity, \
acidity, overrun). Do not penalize interchangeable use unless the query \
specifies a technical distinction.
- **Gelato vs ice cream batch freezers**: Gelato = lower speed (20–30% \
overrun vs 50–100%), served at higher temp (−10 to −12 °C vs −18 °C). \
When query specifies "gelato," prefer gelato-specific equipment.
- **Shake machines**: Spindle-type mixers that blend pre-made ice cream — \
distinct from soft serve and batch freezers, which freeze mix.

**Terminology equivalences** (do not penalize lexical mismatches when \
intent aligns):
- soft serve = soft-serve = softy machine
- batch freezer = ice cream maker (commercial context)
- dipping cabinet = ice cream display case = dipping case
- gelato case = gelato display = gelato showcase
- FroYo machine = frozen yogurt machine
- twist = twin-twist = two-flavor (soft serve with swirl)""",
        ),
        "refrigeration": VerticalOverlay(
            description=(
                "Refrigeration, freezers, ice machines, and cold storage "
                "(not frozen dessert equipment)"
            ),
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
                "Pans, food storage, utensils, cookware, "
                "and kitchen hand tools (not disposables)"
            ),
            content="""\
### Smallwares — Scoring Guidance

This query involves pans, food storage containers, utensils, cookware, \
or other durable kitchen hand tools and supplies.

**Critical distinctions to enforce:**

- **Pan systems**: US hotel pans (full, half, third, quarter, sixth, ninth) \
and European GN pans (1/1, 1/2, 1/3, 2/3, etc.) are dimensionally \
incompatible — different corner radii and rim profiles. Do not cross-match \
hotel pan queries with GN products or vice versa.
- **Pan depth**: Steam table pans come in standard depths (2.5", 4", 6"). \
Depth is a hard requirement when specified — a 2.5" pan cannot substitute \
for a 6" pan.
- **Cutting board color-coding**: HACCP color protocols (green = produce, \
red = raw meat, blue = cooked meat, etc.) are food safety standards, not \
aesthetics — color is a hard requirement when specified.
- **Food storage containers**: Round vs square, capacity, and lid \
compatibility matter. Cambro and Carlisle container systems are not always \
interchangeable.
- **Cookware gauge**: Heavier gauge (lower number) = thicker, more durable. \
Commercial sheet pans: 18-gauge (standard) vs 16-gauge (heavy duty) vs \
perforated (baking) are distinct. Gauge is a hard spec when specified.
- **Utensil material**: Stainless steel vs silicone vs nylon vs wood — \
material determines heat resistance and food safety compliance. \
Stainless is standard for commercial; nylon and silicone for non-stick \
surfaces. Material is a hard constraint when specified.

**Terminology equivalences** (do not penalize lexical mismatches when \
intent aligns):
- lexan = clear polycarbonate food storage container (genericized brand)
- sheet pan = bun pan = half sheet (18×13) or full sheet (18×26)
- hotel pan = steam table pan = GN container (but US and GN are incompatible)""",
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
        "ventilation": VerticalOverlay(
            description=(
                "Kitchen ventilation: exhaust hoods, makeup air units, "
                "fire suppression, ductwork, and fans"
            ),
            content="""\
### Kitchen Ventilation — Scoring Guidance

This query involves kitchen exhaust hoods, makeup air units, fire \
suppression systems, ductwork, or exhaust fans.

**Critical distinctions to enforce:**

- **Type I (grease) vs Type II (heat/steam/condensate) hoods**: \
Code-critical distinction. Type I requires grease-rated baffle filters \
and is mandatory over grease-producing equipment (fryers, griddles, \
broilers). Type II handles steam and heat from dishwashers, steam tables. \
Returning a Type II hood for a Type I query is a building code violation.
- **Hood configuration**: Wall-mount (canopy), island, proximity \
(backshelf/low-profile), ventless (self-contained recirculating) — \
different infrastructure requirements. Configuration is a hard constraint \
when specified.
- **Fire suppression**: UL 300 wet-chemical systems are required for all \
Type I hoods. Pre-piped vs field-piped, nozzle count, and coverage area \
are hard specs. Hoods sold "without fire suppression" need separate systems.
- **CFM (cubic feet per minute)**: Airflow capacity determined by hood \
size and equipment BTU output. Hard spec when specified.
- **Makeup air units (MAU)**: Supply tempered replacement air. CFM \
capacity and heating method (gas vs electric) are hard specs. A MAU is \
NOT an exhaust fan — confusing supply vs exhaust is a category error.
- **Ductwork**: Grease duct (16-gauge welded per NFPA 96) is \
fundamentally different from standard HVAC duct. Using HVAC ductwork on \
a grease run is a fire code violation.
- **Exhaust fans**: Upblast vs utility/inline vs sidewall — different \
installation positions. Belt-driven vs direct-drive are distinct \
motor configurations.
- **Ventless/recirculating systems**: Multi-stage filtration (HEPA, \
activated carbon, ESP), no ductwork required. Limited to specific \
equipment types — not a universal replacement for ducted hoods.

**Terminology equivalences** (do not penalize lexical mismatches when \
intent aligns):
- grease hood = Type I hood
- condensate hood = heat hood = vapor hood = Type II hood
- MAU = makeup air unit
- upblast = roof exhaust fan (upward discharge)
- Ansul = wet chemical fire suppression (genericized brand)""",
        ),
        "proteins": VerticalOverlay(
            description=(
                "Meat, poultry, and seafood: cuts, grades, certifications, "
                "and pack sizing"
            ),
            content="""\
### Proteins — Scoring Guidance

This query involves meat, poultry, or seafood products for foodservice \
purchasing.

**Critical distinctions to enforce:**

- **USDA quality grades are hierarchical hard constraints**: Prime (top \
~8 % of carcasses, abundant marbling), Choice (moderate marbling, \
~60 % of carcasses), Select (slight marbling, leaner). When a query \
specifies a grade, a lower grade is a hard failure and a higher grade \
is an acceptable over-delivery (score at most 1 point below exact \
match). Certified Angus Beef (CAB) requires upper-two-thirds Choice \
or higher Angus cattle meeting 10 additional specs — it is a branded \
program above generic Choice, not a USDA grade itself.
- **USDA yield grades (1–5) measure cutability, not eating quality**: \
YG 1 = highest lean-meat yield, YG 5 = lowest. Yield grades are \
independent of quality grades. A query specifying "YG 2" should not \
return YG 4 product. Yield grade is rarely searched directly but \
appears on boxed-beef labels.
- **IMPS/NAMP numbering is a hard identifier system**: Searches \
containing an IMPS number (e.g., "NAMP 180", "IMPS 112A", "#1189") \
must match that exact item. The series structure: 100 = fresh beef, \
200 = fresh lamb, 300 = fresh veal/calf, 400 = fresh pork, \
500 = cured/smoked pork (bacon, ham), 600 = cured/smoked beef, \
700 = variety meats/offal, 800 = sausage products. Portion-cut codes \
add a 1000-series prefix to the subprimal number (e.g., 180 strip \
loin subprimal -> 1180 strip steak portion cut). Key beef codes: \
109 = rib roast-ready, 112A = ribeye roll lip-on, 116A = chuck roll, \
120 = brisket, 168 = top round, 170 = bottom round, 174 = short loin, \
180 = strip loin boneless, 184 = top sirloin butt boneless, \
189A = tenderloin full side-muscle-on defatted. Key portion-cut \
codes: 1112 = ribeye steak, 1180 = strip steak, 1184 = top sirloin \
steak, 1189/1189A = tenderloin steak (filet mignon). Suffix letters \
denote trim variations (A, B, C, D) — these are distinct specs.
- **Primal vs subprimal vs portion cut hierarchy**: Primal = large \
carcass section (chuck, rib, loin, round, brisket, plate, flank, \
shank). Subprimal = further-broken wholesale cut (e.g., strip loin, \
ribeye roll, top sirloin butt) — these are what arrive in cases. \
Portion cut = steak or roast cut to exact weight from a subprimal. \
A query for "ribeye" (subprimal, IMPS 112) is different from \
"ribeye steak" (portion cut, IMPS 1112). Do not conflate levels.
- **Preparation states are hard constraints**: Raw, marinated, \
seasoned, breaded, pre-cooked/fully-cooked, and ready-to-cook are \
distinct product states with different labor requirements and food \
safety handling. A query for "raw chicken breast" must not return \
breaded or pre-cooked product, and vice versa.
- **Frozen states are distinct and non-interchangeable**: IQF \
(Individually Quick Frozen, each piece separate, ~2 % trim loss) vs \
block frozen (pieces frozen in a solid block, ~14 % trim loss, must \
thaw entire block) vs fresh/never-frozen (short shelf life, premium \
pricing). When a query specifies IQF, block frozen is not acceptable.
- **Portion control vs random weight vs catch weight**: Portion \
control (PC) = exact target weight per piece (e.g., "8 oz ribeye"), \
tight tolerance. Random weight = natural variation within a range. \
Catch weight = invoiced by actual weight of each piece (common for \
whole subprimals and high-value proteins). A "6 oz portion cut filet" \
query requires PC product, not a random-weight tenderloin.
- **Religious certifications are absolute hard constraints**: Kosher \
(requires rabbinical supervision and specific slaughter method; \
glatt kosher = strictest standard requiring smooth lungs) and halal \
(zabiha = hand-slaughtered per Islamic law) are non-negotiable when \
specified. Kosher and halal are NOT interchangeable — they follow \
different religious laws. Non-certified product is a hard failure.

**Pack size encoding**: Foodservice proteins use the format \
"[units]/[weight]" where the first number is count of pieces or bags \
in the case and the second is weight per unit. Examples: "4/10 lb" = \
4 bags of 10 lb each (40 lb case); "40/6 oz" = 40 portion-cut pieces \
at 6 oz each; "2/5 lb" = 2 bags of 5 lb each. Case weight and \
portion size are both hard specs when specified.

**Seafood-specific rules:**

- **Count-per-pound sizing is a hard spec for shrimp and scallops**: \
Shrimp: 21/25 = 21–25 shrimp per pound, U/15 = under 15 per pound \
(larger). The "U" prefix means "under" that count. Smaller count = \
larger individual size. Common sizes: U/10, U/15, 16/20, 21/25, \
26/30, 31/35, 36/40, 41/50. Scallops: U/10, 10/20, 20/30, 30/40 \
(same convention). These are hard specs — a 21/25 shrimp query must \
not return 41/50 product.
- **Dry-pack vs wet-pack scallops**: Dry-pack (no phosphate treatment, \
natural moisture, premium, sears properly) vs wet-pack (STP/phosphate-\
treated, absorbs up to 50 % added water weight, cheaper per nominal \
pound but lower yield). These are fundamentally different products \
when specified — returning wet for a "dry pack" query is a hard failure.
- **Wild-caught vs farm-raised is a hard constraint when specified**: \
Different production methods, flavor profiles, price points, and \
sustainability certifications. MSC (Marine Stewardship Council) = \
wild fisheries only. BAP (Best Aquaculture Practices) and ASC \
(Aquaculture Stewardship Council) = farm-raised only. Do not cross-\
match certifications with production methods.
- **FDA market names vs common names**: Chilean sea bass = Patagonian \
toothfish (marketing rebrand, same species). Mahi-mahi = dolphinfish \
= dorado (NOT dolphin the mammal). Scampi = langoustine in Italian/\
European usage, but "shrimp scampi" in US means shrimp in garlic-\
butter sauce. Escolar is sometimes fraudulently sold as "white tuna" \
or "super white tuna." These naming overlaps affect search relevance.

**Poultry-specific rules:**

- **Whole bird vs parts vs portion cuts**: WOG (Without Giblets) = \
whole carcass minus neck and organs. 8-piece cut = 2 breast halves, \
2 thighs, 2 drumsticks, 2 wings — an industry-standard breakdown. \
Airline breast = boneless skin-on breast with first wing joint \
(drumette) attached (also called Statler breast). Split breast = \
one half of the breast. These are distinct products.
- **Poultry is NOT USDA-graded like beef**: USDA poultry grades \
(A, B, C) measure appearance and defects, not marbling or eating \
quality. Grade A is the only grade typically sold at foodservice level.

**Distributor brand tiers** (signals price/quality positioning):

- Sysco: Butcher's Block Reserve (premium steaks) > Buckhead Pride / \
Newport Pride (specialty hand-cut) > Sysco Premium (formerly Imperial/\
Supreme) > Sysco Classic > Sysco Reliance (value). Portico = seafood \
brand (quality-assured, net-weight audited).
- US Foods: Stock Yards (premium USDA Prime and upper Choice steaks) > \
Chef's Line (premium prepared/convenience) > Cattleman's Selection \
(mid-tier whole-muscle beef and veal, value-oriented). Harbor Banks = \
seafood brand (wild-caught and farm-raised).

**Terminology equivalences** (do not penalize lexical mismatches when \
intent aligns):
- NY strip = New York strip = Kansas City strip = strip steak = \
top loin steak = ambassador steak = hotel steak (IMPS 1180; bone-in \
vs boneless is the only meaningful distinction)
- filet mignon = tenderloin steak = tournedos (IMPS 1189/1189A)
- ribeye = Delmonico (ambiguous — sometimes means ribeye, sometimes \
strip; prefer ribeye interpretation in foodservice context) = \
Spencer steak = beauty steak
- flat iron = top blade steak (IMPS 1114D; from the chuck, NOT the \
same as petite tender)
- petite tender = teres major = shoulder tender (distinct muscle from \
flat iron despite both being chuck cuts)
- hanger steak = butcher's steak = onglet (only one per carcass)
- tri-tip = bottom sirloin triangle = Santa Maria steak (IMPS 185D)
- flap meat = sirloin flap = bavette (IMPS 185A)
- skirt steak: outside skirt (IMPS 121C, more tender, preferred) vs \
inside skirt (IMPS 121D) — these are different muscles
- pork butt = Boston butt = pork shoulder (IMPS 406; confusingly, \
it is from the shoulder, not the rear)
- baby back ribs = loin back ribs (IMPS 422) vs spare ribs \
(IMPS 416) vs St. Louis style (IMPS 416A, trimmed spare ribs) — \
these are distinct cuts
- shrimp = prawn (in US foodservice, used interchangeably regardless \
of taxonomic distinction)
- calamari = squid
- crawfish = crayfish = crawdads""",
        ),
        "prepared_foods": VerticalOverlay(
            description=(
                "Frozen entrees, appetizers, soups, bakery, "
                "desserts, pizza, and prepared meal components"
            ),
            content="""\
### Prepared Foods — Scoring Guidance

This query involves frozen entrees, appetizers, soups, bakery products, \
desserts, pizza components, or other pre-made food items sold to \
foodservice operators.

**Critical distinctions to enforce:**

- **Preparation level classifications**: These are NOT interchangeable \
and determine kitchen labor, equipment, and food-safety requirements. \
Ready-to-eat (RTE) = fully cooked, safe to consume without further \
cooking (may require reheating for palatability only). \
Fully cooked / heat-and-serve = cooked during processing, requires \
reheating to serving temperature but no cook-through. \
Ready-to-cook (RTC) / cook-from-frozen = raw or partially cooked, \
MUST reach safe internal temperature (e.g., 165 °F poultry) — \
labeling says "Cook and Serve," "Not Ready to Eat," or "Oven Ready." \
Thaw-and-serve = fully finished, serve after thawing with no heating \
required (common for desserts, breads, pastries). Returning an RTC \
product for an RTE query (or vice versa) is a category-level error \
because it implies fundamentally different kitchen workflows.
- **Frozen appetizers / starters**: IQF (individually quick frozen) \
vs tray-packed are distinct formats — IQF allows portioning from bag, \
tray-packed is pre-arranged in layers. Piece count per case and \
individual portion weight (e.g., 1 oz, 1.5 oz, 3 oz egg rolls) are \
hard specs when specified. Egg rolls, spring rolls, wontons, \
mozzarella sticks, and breaded cheese curds are distinct product \
types despite all being "appetizers."
- **Frozen entrees**: Individual portion-controlled (IW = individually \
wrapped) vs multi-serve bulk pans (hotel-pan or steam-table-tray \
format) are different product formats for different service models. \
Case packs are specified as piece count × portion weight or \
bag count × bag weight (e.g., 72 pc/case × 4 oz, or 4/5 lb bags). \
Portion weight is a hard spec when specified.
- **Soup products**: Condensed (requires dilution, typically 1:1 with \
water or milk), ready-to-serve / RTS (heat and serve, no dilution), \
soup base / concentrate (paste or dry powder, requires water plus \
cooking — NOT the same as condensed), and frozen soup (typically RTS \
after thawing/reheating) are four distinct product types. Returning a \
soup base for a "ready-to-serve soup" query is a category error — \
soup base is an ingredient, not a finished soup.
- **Bakery preparation levels**: Frozen dough (requires proofing, \
shaping, and full bake — highest labor/skill), parbaked / par-baked \
(80–90% baked, finish 10–15 min in oven for crust and color — \
moderate labor, no proofing), thaw-and-serve (fully baked and frozen, \
no oven needed — zero labor), scratch-ready mixes (add water/eggs, \
mix, shape, proof, bake — high labor). Each level implies different \
equipment needs, skill requirements, and labor costs — they are not \
interchangeable. A "parbaked rolls" query must not return frozen dough.
- **Pizza products**: Dough balls (raw, require stretching/proofing/ \
full bake — highest labor), sheeted dough (pre-rolled, still raw), \
par-baked crusts (structure set, finish with toppings and short bake), \
self-rising / rising crust (leavening activates during bake — distinct \
texture profile), and fully topped frozen pizza (heat-and-serve, \
lowest labor) are each a different product category. Confusing dough \
balls with par-baked crusts is a category error.
- **Frozen desserts as food products**: Thaw-and-serve cakes, pies, \
cheesecakes, and individually portioned desserts are finished food \
items — distinct from ice cream / frozen dessert EQUIPMENT (soft \
serve machines, batch freezers). Pre-sliced / pre-scored vs whole \
(operator-portioned) is a format distinction. When the query says \
"frozen dessert" in a prepared-foods context, do not return equipment.
- **CN (Child Nutrition) labeling**: USDA FNS program that certifies \
a product's contribution toward meal pattern requirements in K-12 \
school nutrition programs. A CN label states the oz-equivalent \
meat/meat alternate (M/MA) credit per serving — minimum 0.50 oz eq \
to qualify. CN-labeled products carry an audit warranty; products \
without a CN label require a Product Formulation Statement (PFS) \
from the manufacturer instead. When a query specifies "CN labeled" \
or targets K-12 / school foodservice, CN labeling is a hard \
requirement — non-CN products are not acceptable substitutes.
- **Whole grain-rich (WGR)**: Required for all grains in USDA school \
meal programs — whole grain must be the first grain ingredient by \
weight (or combined whole grains outweigh refined). Products bearing \
the Whole Grain Stamp guarantee ≥ 8 g whole grain per serving. Hard \
requirement when query specifies "whole grain" or targets K-12.
- **USDA Foods (commodity) products**: Bulk raw commodities (chicken, \
beef, turkey, cheese) purchased by USDA and diverted to processors \
for conversion into finished end products via the processing / \
diversion program. End products are listed on Summary End Product \
Data Schedules (SEPDS) with specific item codes. Operators searching \
for "USDA commodity" or "USDA Foods" products expect these specific \
program items — commercial equivalents without USDA commodity \
value pass-through are not the same product.
- **Allergen and dietary certifications**: Certified Gluten-Free \
(GFCO standard: ≤ 10 ppm gluten, stricter than FDA's 20 ppm \
threshold for "gluten-free" labeling) is a distinct claim from \
"gluten-free" on label. Dedicated allergen-free facility means \
zero cross-contact risk — different from "made on shared equipment" \
or "in a facility that also processes." When a query specifies \
a certification level, treat it as a hard constraint.

**Pack-size conventions**: Frozen prepared foods are sold by case. \
Cases are described by portion count × portion weight (e.g., \
"96 pc × 1 oz"), bag count × bag weight (e.g., "4/5 lb"), or \
total case weight. When the query specifies a pack format, match it.

**Brand relevance in prepared foods**: Major foodservice prepared-foods \
manufacturers often operate brand portfolios targeting different \
segments. Tyson (AdvancePierre, Hillshire Farm, Jimmy Dean, State \
Fair), Schwan's / CJ (Tony's, Big Daddy's, Minh, Pagoda, Red Baron), \
Rich Products (Jon Donaire, Farm Rich, Casa Di Bertacchi), and \
ConAgra Foodservice are parent companies whose sub-brands buyers \
cross-shop within the same portfolio — do not penalize returning a \
sister brand from the same parent when specs align.

**Terminology equivalences** (do not penalize lexical mismatches when \
intent aligns):
- heat-and-serve = fully cooked frozen = warm and serve
- parbaked = par-baked = partially baked = bake-off (finishing step)
- IW = individually wrapped (portion-controlled entrees)
- IQF = individually quick frozen (loose-piece format)
- CN label = Child Nutrition label (USDA meal-pattern crediting)
- PFS = Product Formulation Statement (alternative to CN label)
- WGR = whole grain-rich (USDA school meal grain requirement)
- soup base = soup starter = bouillon concentrate (ingredient, \
not finished soup)
- dough ball = dough round (raw pizza dough, requires full bake)
- RTE = ready to eat; RTC = ready to cook; RTS = ready to serve""",
        ),
        "produce": VerticalOverlay(
            description=(
                "Fresh fruits, vegetables, herbs, and processed produce for foodservice"
            ),
            content="""\
### Produce — Scoring Guidance

This query involves fresh fruits, vegetables, herbs, or processed \
produce products for commercial foodservice purchasing.

**Critical distinctions to enforce:**

- **USDA produce grades are hierarchical hard constraints**: \
Extra Fancy (highest — superior color, shape, freedom from defects), \
Fancy (premium quality), U.S. No. 1 (good commercial quality, \
standard for most foodservice), U.S. No. 2 (slightly lower quality, \
more defects tolerated — often used for processing or pre-cut). \
When a query specifies a grade, a lower grade is a hard failure. \
Not all commodities use every grade — apples use Extra Fancy through \
Utility; potatoes use U.S. No. 1, No. 2, and Utility. Grade is a \
hard constraint when specified.
- **Count-per-case sizing (fruits)**: Size is expressed as the number \
of pieces per standard case — larger count = smaller individual fruit. \
Oranges: 48 (largest), 56, 72, 88, 113, 138, 163 (smallest). \
Lemons: 75, 95, 115, 140, 165, 200, 235. Avocados: 28, 32, 36, 40, \
48, 60, 70, 84 (Hass). Apples: 48, 56, 64, 72, 80, 88, 100, 113, \
125, 138, 163, 198. A "88 size orange" means 88 oranges per case — \
returning 48-size (much larger fruit) is a size mismatch and a hard \
failure.
- **Processed produce forms are hard constraints**: Fresh whole, \
fresh-cut (pre-washed, pre-cut, ready-to-use), IQF (individually \
quick frozen — loose pieces), block frozen, freeze-dried, and \
dehydrated are distinct product forms with different storage, shelf \
life, and culinary applications. IQF maintains piece integrity and \
allows portioning from bag; block frozen requires thawing the entire \
block. Freeze-dried retains shape and rehydrates; dehydrated is \
volume-reduced and shelf-stable. Returning IQF for a "fresh-cut" \
query or dehydrated for a "freeze-dried" query is a form mismatch.
- **Fresh-cut / value-added produce vs whole produce**: Pre-washed \
bagged salad mixes, pre-cut fruit cups, shredded lettuce, diced \
onions, peeled garlic, and spiralized vegetables are value-added \
products with higher per-unit cost but lower labor. These are distinct \
from whole commodity produce — a "diced onion" query must not return \
whole onions, and a "whole head lettuce" query must not return \
shredded bags.
- **PLU code system**: 4-digit PLU codes (assigned by IFPS) identify \
conventional produce items at point of sale (e.g., 4011 = yellow \
banana, 4065 = green pepper, 4225 = Roma tomato). A 5-digit PLU \
starting with 9 indicates organic (e.g., 94011 = organic yellow \
banana). PLU codes are hard identifiers — when a query includes a \
PLU number, match it exactly.
- **Herbs: fresh vs dried is a hard constraint**: Fresh herbs (sold \
in bunches, clamshells, or living pots) and dried herbs are \
fundamentally different products with different flavor intensity, \
shelf life, and culinary application. Substitution ratio is roughly \
3:1 fresh-to-dried by volume. Returning dried basil for a "fresh \
basil" query (or vice versa) is a category error.
- **Herb packaging**: Bunches (tied stems, traditional), clamshells \
(plastic hinged containers, pre-washed, retail/foodservice crossover), \
and living/potted herbs (rooted, longest shelf life) are distinct \
pack types. Pack type is a hard constraint when specified.
- **Organic certification tiers**: USDA Organic (certified by \
USDA-accredited certifying agent, no synthetic pesticides/fertilizers, \
non-GMO), Transitional Organic (farm in 3-year transition period — \
grown organically but not yet certified, cannot use USDA Organic \
seal), and GAP-certified (Good Agricultural Practices — food safety \
certification, NOT an organic claim). These are distinct programs — \
GAP is not organic, and Transitional is not fully certified organic. \
When a query specifies "organic," only USDA Organic-certified \
product satisfies it.
- **Ripeness and readiness**: For avocados, bananas, tomatoes, and \
other climacteric fruits, ripeness stage is a functional spec. \
"Green" (unripe, for ripening on-site), "turning/breaker" \
(partially ripe), and "ripe/ready-to-eat" are distinct purchasing \
specs. Foodservice buyers specify ripeness based on intended use \
date — hard constraint when specified.
- **Potato type determines culinary application**: Russet/Idaho \
(high starch — baking, frying), Yukon Gold/yellow (medium starch — \
roasting, mashing), red (low starch/waxy — boiling, potato salad), \
fingerling (small, waxy, roasting), sweet potato/yam (botanically \
distinct species — sweet potato is Ipomoea batatas, true yam is \
Dioscorea; US "yam" is almost always a sweet potato variety). \
Potato type is a hard constraint when specified.
- **Tomato classification**: Cherry, grape, Roma/plum, beefsteak, \
vine-ripe (TOV = tomatoes on the vine), and heirloom are distinct \
types with different size, texture, and culinary uses. Canned \
tomatoes (whole peeled, diced, crushed, paste) belong in dry_goods, \
not produce. Hydroponic/greenhouse vs field-grown is a production \
method distinction, not a type.
- **Lettuce and greens are not interchangeable**: Iceberg (crisp, \
mild, shredding), Romaine (sturdy, Caesar salad standard), green \
leaf, red leaf, butter/Bibb (tender, cups), spring mix/mesclun \
(mixed baby greens), spinach (baby vs mature), arugula (peppery), \
and kale (sturdy, bitter) are distinct products. Returning iceberg \
for a "romaine" query is a category error.

**Pack-size conventions** (do not penalize variants unless query \
specifies exact size):
- Bushel = traditional volume measure (~1.24 cu ft), varies by \
commodity (bushel of apples ~42-48 lb, bushel of tomatoes ~53 lb)
- Case/carton = standard commercial unit (weight varies: 10 lb, \
20 lb, 25 lb, 40 lb, 50 lb depending on commodity)
- Flat = shallow tray, typically for berries (8 pints or 12 half-pints)
- Lug = field box for grapes, stone fruit (~24-28 lb)
- RPC (Reusable Plastic Crate) = standardized stackable crate used \
by IFCO/Tosca supply chains — indicates supply chain logistics, \
not product quality
- Count per case = sizing for fruits (see count-per-case rules above)
- Clamshell = rigid hinged plastic container for berries, cherry \
tomatoes, herbs, baby greens
- Bag = typically 1 lb, 2 lb, 3 lb, 5 lb for pre-washed salad \
mixes and fresh-cut produce

**Foodservice produce brand tiers** (signals quality/service level):
- Markon: First Crop (premium whole produce, spec'd for foodservice), \
Ready-Set-Serve (pre-cut, washed, ready-to-use), Markon Essentials \
(value tier)
- Fresh Express: foodservice salad mixes and pre-cut lettuce \
(5 lb bags standard)
- Dole Fresh Vegetables: foodservice-scale pre-cut and salad kits
- Sysco: Imperial Fresh (premium), Classic (standard), Reliance (value)
- US Foods: Cross Valley Farms (produce brand)

**Terminology equivalences** (do not penalize lexical mismatches when \
intent aligns):
- PLU = price look-up code (4-digit conventional, 9-prefix = organic)
- IQF = individually quick frozen (loose-piece frozen produce)
- fresh-cut = pre-cut = value-added produce (washed, cut, bagged)
- TOV = tomatoes on the vine = vine-ripe tomatoes
- spring mix = mesclun = mixed baby greens
- yam = sweet potato (in US commercial usage — true yams are rare)
- flat = berry flat (tray of berry baskets)
- lug = field lug = harvest box
- clamshell = hinged plastic produce container
- RPC = reusable plastic crate (IFCO, Tosca)
- RSS = Ready-Set-Serve (Markon pre-cut produce line)
- Idaho potato = Russet Burbank (most common Russet cultivar)""",
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
