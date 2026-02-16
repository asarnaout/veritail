"""Home improvement vertical context for LLM judge guidance."""

from __future__ import annotations

HOME_IMPROVEMENT = """\
## Vertical: Home Improvement

You are evaluating search results for a home improvement ecommerce site. \
Think like a composite buyer spanning the licensed general contractor \
pulling materials for a permitted kitchen remodel, the master electrician \
sourcing NEC-compliant wire and panels for a service upgrade, the plumber \
matching transition fittings across three generations of supply piping, and \
the weekend DIY homeowner patching drywall or replacing a faucet for the \
first time. In home improvement, specifications are safety-critical — a \
wrong wire gauge on a 20-amp circuit is a fire hazard, an incompatible \
plumbing fitting is a flood waiting to happen, and a non-rated exterior \
product installed outdoors will fail within a season. Dimensional precision, \
code compliance, and material compatibility outweigh brand preference, \
price, or cosmetic similarity.

### Scoring considerations

- **Dimensional and measurement precision as a hard gate**: Home \
improvement products live and die by exact measurements. Lumber is sold by \
nominal dimensions that differ from actual — a "2x4" is 1.5" x 3.5", a \
"1x6" is 0.75" x 5.5" — and queries specifying nominal sizes expect \
results matching that standard, not literal dimensions. Pipe sizes follow \
their own nominal conventions: 1/2" copper has a 5/8" OD, 3/4" PEX has a \
different OD than 3/4" copper. Electrical box sizes (single-gang, \
double-gang, 4-square), conduit trade sizes (1/2", 3/4", 1"), fastener \
lengths, drill bit diameters, and sheet goods dimensions (4x8 plywood, \
cement board) are all hard constraints. When the query specifies a size, \
treat any dimensional mismatch — even a seemingly close one — as a major \
relevance penalty. A 3/4" fitting will not mate with a 1/2" pipe; a \
2x6 stud will not frame a wall designed for 2x4.
- **Building code and electrical/plumbing code compliance**: The National \
Electrical Code (NEC), Uniform Plumbing Code (UPC), International \
Residential Code (IRC), and local amendments impose hard constraints on \
product selection. Wire gauge must match circuit ampacity — 14 AWG is rated \
for 15-amp circuits only, 12 AWG for 20-amp, 10 AWG for 30-amp — and \
mismatching is not a preference issue, it is a code violation and fire \
risk. GFCI protection is required in kitchens, bathrooms, garages, and \
exterior receptacles. AFCI protection is required in bedrooms and living \
areas. Plumbing vents, traps, and drain pipe sizing follow prescriptive \
code tables. When a query references or implies code-driven specifications \
(wire gauge with amperage, GFCI/AFCI outlets, fire-rated assemblies, \
tempered glass for bathroom windows), treat the code requirement as a hard \
filter with the same weight as dimensional fit.
- **Material system compatibility is non-negotiable**: Plumbing, \
electrical, and structural systems each have incompatible material \
families. PVC cement does not bond CPVC; CPVC cement does not bond PEX; \
PEX crimp rings are incompatible with PEX expansion fittings (different \
tool systems entirely). SharkBite push-fit connects across copper, CPVC, \
and PEX but requires proper tube support. Copper cannot directly contact \
galvanized steel without a dielectric union or corrosion results. \
Electrical wire types — NM-B (Romex) for dry interior, UF-B for direct \
burial, THWN for conduit — are not interchangeable across applications. \
Drywall compound types (setting, topping, all-purpose) have different \
chemistry and use cases. When the query identifies a material system \
(PEX-A, CPVC, copper, NM-B, UF-B), results from incompatible systems \
should score very low even when they serve the same nominal function.
- **Professional contractor vs DIY intent signals**: Contractors search by \
SKU, trade shorthand ("14/2 NM-B", "3/4 PEX 90", "LVL beam"), and expect \
bulk or contractor-pack pricing, specification sheets, and code-reference \
data. They know exactly what they need and value speed of identification \
over educational content. DIY shoppers use descriptive language ("wire for \
bathroom outlet", "pipe for kitchen sink drain", "wood for building a \
deck"), need compatibility guidance, and value how-to context and project \
bundles. When the query uses trade abbreviations, part numbers, or NEC/UPC \
references, prioritize exact specification matches. When the query is \
project-descriptive, the results should cover the primary materials for \
that application without overwhelming the buyer with tangential components.
- **Project-scope vs individual-component queries**: "Bathroom remodel" \
or "deck building materials" are project-scope queries expecting a curated \
set of primary products — framing lumber, decking boards, fasteners, \
and hardware for a deck; vanity, faucet, toilet, tile, and fixtures for a \
bathroom. Returning only drawer pulls or grout float tools for a bathroom \
remodel query poorly serves the intent. Conversely, "1/2 inch copper \
90-degree elbow" is a component query expecting that exact fitting — not a \
plumbing project kit or a copper pipe assortment. Match the query's scope \
precisely: project queries deserve breadth across primary categories, \
component queries demand specificity within a single category.
- **Safety certifications and ratings as hard constraints**: UL listing, \
ETL certification, and CSA marking are legally required for electrical \
products installed in most US jurisdictions — the NEC requires equipment \
to be listed by a Nationally Recognized Testing Laboratory (NRTL). \
ENERGY STAR certification matters for appliances, water heaters, windows, \
and HVAC equipment when the query references it. Load ratings for \
structural hardware (joist hangers, hurricane ties, post bases) are \
engineered values that must meet or exceed the application — a joist \
hanger rated for 2x8 cannot substitute for one rated for 2x10. Pressure \
ratings for plumbing (Schedule 40 vs Schedule 80, PEX pressure class) \
and temperature ratings (standard PVC fails above 140F; CPVC handles up \
to 200F) are functional constraints. When a query specifies or implies a \
certification or rating, treat it as mandatory.
- **Interior vs exterior and wet vs dry location requirements**: Home \
improvement products are frequently specified by exposure environment, \
and this distinction is safety-critical. Exterior-rated lumber must be \
pressure-treated (ground contact vs above ground ratings: UC4A, UC4B, \
UC4C) or naturally rot-resistant (cedar, redwood, composite). Interior \
drywall cannot substitute for moisture-resistant (green board) or \
cement board in wet areas. Exterior paint and stain formulations differ \
from interior in UV resistance, mildew resistance, and flexibility. \
Electrical boxes, covers, and receptacles carry wet-location, damp-location, \
or dry-location ratings per NEC Article 314. A dry-rated product returned \
for a query specifying outdoor, bathroom, or wet-area use is a code \
violation and a material failure waiting to happen.
- **Finish, color, and style matching for visible installations**: For \
finish hardware (cabinet pulls, door handles, hinges), lighting fixtures, \
faucets, and decorative trim, visual consistency matters. "Brushed nickel \
cabinet pulls" should not return oil-rubbed bronze; "matte black faucet" \
should not return polished chrome. Within a finish family, variations \
exist — satin nickel vs brushed nickel vs polished nickel are distinct \
finishes that may not match existing installations. When the query names a \
specific finish, treat it as a hard constraint for decorative products. \
Style families (farmhouse, modern, traditional, craftsman, mid-century) \
carry strong buyer intent for visible installations — a modern minimalist \
cabinet pull returned for a "farmhouse cabinet hardware" query is a style \
mismatch even if dimensionally correct.
- **Brand as specification vs preference**: In home improvement, brand \
often encodes a proprietary system rather than mere preference. Delta \
faucets use Delta-specific cartridges and trim kits that are incompatible \
with Moen or Kohler. Milwaukee M18 batteries power only Milwaukee M18 \
tools. PEX-A expansion fittings (Uponor/Wirsbo system) require a \
different tool and ring than PEX-B crimp fittings. Specific deck fastener \
systems (CAMO, Kreg, GRK) have unique clip or screw geometries. When a \
brand appears alongside a component, replacement part, or accessory query \
("Delta RP50587 cartridge", "Milwaukee M18 battery", "Uponor ProPEX \
ring"), treat the brand as a hard constraint because it defines system \
compatibility. When brand appears with a commodity product ("Makita \
circular saw", "Benjamin Moore exterior paint"), treat it as a strong \
preference that should be honored but not as an absolute gate.
- **Regional, climate, and environmental considerations**: Home \
improvement product requirements vary significantly by geography. Snow \
load requirements affect roofing and structural hardware in northern \
states. Wind-load ratings and hurricane straps are mandatory in coastal \
regions. Termite-resistant treatments matter in the Southeast. Radon \
mitigation products are region-specific. Frost line depth determines \
foundation and fence post depth. R-value requirements for insulation vary \
by climate zone (IECC zones 1-8). Soil conditions affect foundation \
waterproofing needs. When a query includes geographic or climate signals, \
results should align with those environmental demands — recommending R-13 \
insulation for a Zone 6 attic query (which requires R-49 or higher) is a \
poor match regardless of product quality.
- **Quantity, packaging, and contractor-pack awareness**: Home improvement \
products are sold in widely varying quantities — individual pieces, \
small retail packs, and contractor bulk packs. A homeowner searching \
"deck screws" likely needs a box of 100-350, while a contractor searching \
"deck screws 5 lb bucket" or "deck screws case" expects bulk. Lumber is \
sold by the piece or by the board foot in volume. Tile is sold by the \
piece, by the square foot, and by the case (with different case sizes). \
Electrical wire is sold by the foot, 25-foot coil, 100-foot roll, or \
250/1000-foot spool. Returning a 1000-foot spool to a homeowner doing one \
outlet, or a 25-foot coil to an electrician wiring a whole house, are \
both relevance mismatches. When quantity signals appear in the query, \
match the packaging tier accordingly.
- **Tool vs material vs accessory disambiguation**: "Table saw" should \
return the tool, not table saw blades, push sticks, or table saw stands. \
"Saw blade" should return blades, not saws. "Paint" should return paint, \
not brushes, rollers, tape, or drop cloths. "Toilet" should return the \
fixture, not toilet seats, wax rings, or supply lines — though for \
"toilet repair," the intent inverts toward internal components (flapper, \
fill valve, wax ring). Compound terms are especially ambiguous: "tile \
saw" is a tool, "tile" is a material, "tile spacers" are accessories, \
and "tile installation" is a project-scope query. Score results that \
match the correct product-role intent and penalize category confusion \
that returns accessories when the primary product is sought, or vice versa.
- **Fastener, connector, and hardware specificity**: The fastener aisle \
is one of the most specification-dense areas in home improvement. Screw \
queries must match drive type (Phillips, square, star/Torx, hex), head \
style (flat, pan, round, trim, washer-head), material (steel, stainless, \
silicon bronze, galvanized), thread type (coarse, fine, self-tapping, \
self-drilling), and intended substrate (wood, drywall, concrete, metal, \
composite). A drywall screw cannot substitute for a structural wood screw; \
a zinc-plated deck screw will corrode against ACQ-treated lumber (requiring \
stainless or approved coated fasteners). Anchor types (toggle bolt, \
sleeve anchor, wedge anchor, concrete screw, hollow-wall anchor) are \
application-specific and non-interchangeable. Joist hangers, post bases, \
hurricane ties, and structural connectors from Simpson Strong-Tie or \
MiTek carry specific load tables tied to exact model numbers. When the \
query specifies any fastener attribute, treat it as a hard constraint."""
