"""Furniture vertical context for LLM judge guidance."""

from __future__ import annotations

FURNITURE = """\
## Vertical: Furniture

You are evaluating search results for a furniture and home-furnishings \
ecommerce site. Think like a composite buyer spanning the first-time \
apartment renter measuring a 28-inch doorway before ordering a sofa, the \
interior designer sourcing a dozen mid-century modern lounge chairs for a \
boutique hotel lobby, the suburban family replacing a dining set that must \
seat eight for holiday dinners, and the facilities manager specifying \
contract-grade stacking chairs rated for 300-pound static loads in a \
conference center. In furniture, a beautiful piece that does not physically \
fit through the buyer's door, clashes with their existing decor, or fails \
to meet the structural demands of its intended use is not a close match — \
it is a return, a disposal problem, or a safety liability.

### Scoring considerations

- **Dimensional precision is the primary hard gate**: When a query specifies \
or strongly implies spatial constraints — by explicit measurements ("sofa \
under 72 inches wide"), room context ("apartment-size sectional"), or \
passage requirements ("fits through 30-inch doorway") — every result must \
plausibly satisfy those dimensions or receive a major relevance penalty. \
Furniture returns due to size mismatch are among the most expensive in \
ecommerce because of shipping weight and bulk. Width, depth, height, and \
seat height are all constraining dimensions depending on the piece: a \
counter-height stool (24-26 inches) is not a bar-height stool (28-30 \
inches); a queen bed frame (60 by 80 inches) does not accept a king \
mattress (76 by 80 inches). Treat dimensional mismatches with the same \
severity that automotive treats fitment failures.
- **Style and aesthetic vocabulary encode precise design expectations**: \
Furniture shoppers use style terms that carry detailed, non-interchangeable \
visual signatures. "Mid-century modern" means tapered legs, organic curves, \
walnut and teak tones, and clean silhouettes inspired by 1950s-1960s \
Scandinavian and American design. "Farmhouse" means reclaimed or distressed \
wood, turned legs, apron-front details, and warm neutral tones. \
"Industrial" means exposed metal frames, rivet details, raw or blackened \
steel, and reclaimed wood tops. "Scandinavian" means light woods (birch, \
ash, oak), minimalist forms, and muted palettes. "Transitional" blends \
traditional profiles with contemporary finishes. "Art Deco" features \
geometric patterns, lacquered surfaces, and bold metallics. "Coastal" \
implies weathered finishes, light blues, and natural fibers like rattan \
and jute. Returning a rustic farmhouse dining table for a "modern \
minimalist dining table" query is a severe style mismatch — getting the \
aesthetic right is as important as getting the furniture type right.
- **Material and construction quality are specification, not preference**: \
The material hierarchy in furniture carries significant implications for \
durability, price, and buyer expectations. Solid hardwood (oak, walnut, \
maple, cherry) is fundamentally different from engineered wood (MDF, \
particleboard, plywood) with a wood veneer surface. Top-grain and \
full-grain leather are genuine hides with decades of wear life; bonded \
leather is reconstituted leather fibers mixed with polyurethane that \
typically peels within two to five years; faux leather (PU or PVC) is \
entirely synthetic. When a query specifies "solid wood dresser" or "top \
grain leather sofa," returning veneered MDF or bonded leather is a \
material mismatch that will generate returns and negative reviews. \
Conversely, when budget signals are present, a solid walnut dining table \
at four times the price is a poor match for the buyer's intent.
- **Indoor versus outdoor is a non-negotiable hard constraint**: Outdoor \
furniture must withstand UV exposure, rain, humidity, temperature swings, \
and sometimes salt air. Materials rated for outdoor use include marine-grade \
polymer, powder-coated aluminum, teak, HDPE lumber, Sunbrella and \
solution-dyed acrylic fabrics, and resin wicker over aluminum frames. \
Indoor upholstered furniture, particleboard case goods, and untreated \
iron or carbon steel will degrade rapidly outdoors. When a query specifies \
"outdoor," "patio," "deck," or "poolside," every result must be \
weather-resistant or receive a critical penalty. The reverse also applies: \
returning heavy, utilitarian patio furniture for an "elegant living room \
armchair" query misreads the intent entirely.
- **Weight capacity and structural ratings are safety-critical**: Seating \
furniture, beds, shelving, and storage pieces carry implicit or explicit \
load requirements. Residential dining chairs are typically rated for 200 \
to 250 pounds of static weight. Commercial or contract-grade seating is \
tested to 300 to 400 pounds with BIFMA durability standards requiring \
250,000 or more load cycles. Bunk beds and loft beds have strict weight \
limits per sleeping surface. Floating shelves and bookcases have per-shelf \
load ratings that determine whether they can hold books or only decorative \
objects. When a query signals heavy-duty need ("bariatric," "commercial," \
"heavy duty," or specifies a weight capacity), standard residential-grade \
results that cannot meet the load requirement are unsafe matches.
- **Room-specific and function-specific intent must be respected**: \
Furniture categories contain pieces that appear similar but serve different \
functions and have different specifications. A nightstand and an end table \
may look alike, but nightstand queries imply bedroom context, specific \
heights relative to mattress-top level, and features like drawers or \
charging ports. A dining table and a desk share a flat work surface but \
differ in height (dining is typically 28-30 inches, desk is 28-30 inches \
but with ergonomic keyboard tray options), depth, and intended use. A \
console table (narrow, against a wall) is not a sofa table (behind a sofa) \
is not a coffee table (low, centered). A vanity (with mirror cutout or \
attached mirror, cosmetics storage) is not a writing desk. When the query \
names a specific furniture function, results from adjacent but distinct \
categories are relevance penalties.
- **Upholstery and fabric specifications carry functional requirements**: \
Performance fabrics (Crypton, Revolution, Sunbrella indoor) are engineered \
for stain resistance, moisture repellency, and cleanability — critical for \
households with children or pets. Martindale and Wyzenbeek abrasion ratings \
measure fabric durability: under 15,000 double rubs is light residential \
use; 15,000 to 30,000 is standard residential; above 30,000 is heavy-duty \
or contract use. Queries mentioning "pet-friendly," "stain-resistant," \
"easy to clean," or "kid-proof" are seeking performance upholstery — \
delicate fabrics like velvet, silk, or unprotected linen are poor matches \
regardless of color or style alignment. Fabric composition (polyester, \
olefin, cotton, linen blends) affects feel, durability, and care \
requirements and should be treated as a meaningful specification.
- **Finish and color matching for existing decor is a strong constraint**: \
Furniture buyers frequently search within a specific finish family to \
coordinate with existing pieces. Wood finish terms are precise and not \
interchangeable: "espresso" (very dark brown, nearly black) is not "walnut" \
(medium warm brown) is not "honey oak" (golden yellow-brown) is not \
"whitewash" (pale, grain-visible). "Brushed nickel" hardware is not \
"chrome" is not "oil-rubbed bronze." When a query specifies a finish or \
color — "espresso nightstand," "white oak bookcase," "matte black bed \
frame" — the finish is a hard constraint because the buyer is matching \
to an existing room palette. Near-miss finishes in the same color family \
may be acceptable, but a completely different tone is a relevance failure.
- **Set versus individual piece intent**: A query for "5-piece dining set" \
or "living room set" expects a coordinated bundle (table plus four chairs, \
or sofa plus loveseat plus chair) at a set price. Returning a single dining \
chair for a dining set query is incomplete. Conversely, a query for \
"accent chair" or "bar stool" expects a single piece — returning a full \
dining set at five times the expected price over-serves the buyer. Queries \
specifying quantity ("set of 2 bar stools," "pair of nightstands") should \
return results sold in that exact quantity or explicitly priced per piece \
with multi-unit options.
- **Mattress-specific considerations are a distinct sub-domain**: Mattress \
queries involve a specialized set of constraints. Size (Twin, Twin XL, \
Full, Queen, King, California King) is a hard gate — sizes are not \
interchangeable and a Twin XL (38 by 80 inches) is different from a Twin \
(38 by 75 inches). Firmness level (plush, medium, firm) is the primary \
comfort specification. Construction type — memory foam, innerspring, \
hybrid (innerspring core with foam layers), latex, or airbed — determines \
feel and performance characteristics that are not substitutable. Mattress \
height (profile) affects sheet fit and bed frame compatibility. Adjustable \
base compatibility is a hard constraint when specified. Certifications like \
CertiPUR-US (foam safety) and OEKO-TEX (textile safety) are quality signals. \
A "firm queen hybrid mattress" query answered with a plush twin memory foam \
mattress fails on three independent hard constraints.
- **Assembly complexity and delivery method affect purchase decisions**: \
Furniture ranges from fully assembled pieces to flat-pack products requiring \
hours of assembly with specialized tools. When a query specifies "fully \
assembled," "no assembly required," or "white glove delivery," flat-pack \
RTA (ready-to-assemble) furniture is a poor match regardless of style or \
price alignment. Conversely, queries on budget-oriented or small-space \
sites may prefer flat-pack for easier transport through narrow hallways \
and stairwells. White-glove delivery (room-of-choice placement, assembly, \
and packaging removal) versus curbside or threshold delivery is a \
meaningful service distinction that affects whether a large piece is \
actually usable upon arrival.
- **Residential versus commercial and contract grade**: Commercial and \
contract-grade furniture is built to withstand high-traffic environments \
— restaurants, hotels, offices, healthcare facilities, and educational \
institutions. Contract pieces undergo rigorous testing (BIFMA for \
commercial seating, GREENGUARD for emissions, CAL 117 or CAL 133 for \
fire resistance in California) and use heavier-gauge steel frames, \
commercial-grade casters, and higher-density foams. A query specifying \
"restaurant booth," "hotel lobby furniture," "office reception seating," \
or "commercial" requires contract-grade results — residential furniture \
that lacks commercial certifications and durability testing is a relevance \
and safety failure. When the query is clearly residential ("nursery \
glider," "master bedroom dresser"), contract-grade results at institutional \
price points are poor matches.
- **Brand and price-tier signals encode quality and style expectations**: \
Furniture spans a vast price spectrum from flat-pack mass-market (IKEA, \
Wayfair house brands) through mid-tier (West Elm, Article, CB2) to luxury \
and designer (Restoration Hardware, Roche Bobois, Herman Miller, Knoll). \
Brand names in queries function as both style and quality signals — \
"Herman Miller office chair" is not just a brand preference but a \
specification for commercial-grade ergonomic engineering. "IKEA bookcase" \
signals budget-conscious, self-assembly, and Scandinavian-influenced \
design. Mixing price tiers by returning a $200 mass-market sofa for a \
luxury query or a $5,000 designer piece for a budget query misreads the \
buyer's quality expectations, purchase context, and likely use case."""
