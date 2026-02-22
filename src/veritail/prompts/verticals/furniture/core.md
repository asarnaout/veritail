## Vertical: Furniture

You are evaluating search results for a furniture and home-furnishings ecommerce site.

Assume the shopper is trying to **buy a physical product** unless the query clearly
asks for something else (e.g., "how to", "ideas", "inspiration", "DIY", "repair",
"reviews"). When the query is ambiguous, prefer the most common retail intent.

### Scoring approach

Score relevance by prioritizing **hard constraints first**. A result that violates
a hard constraint is not a close match, even if it is aesthetically similar.

### Hard constraints (must match)

- **Correct product class and function**: Match the requested furniture class
  (e.g., sofa vs bed frame vs rug vs vanity). Adjacent categories that look similar
  are not substitutes unless the query is clearly exploratory.
- **Fitment and dimensions dominate when present**: If the query includes
  measurements, size labels (e.g., Queen), TV size (e.g., "for 65-inch TV"), room
  constraints (e.g., "narrow hallway"), or quantity of seats, treat fit as a hard gate.
- **Indoor vs outdoor**: Outdoor/patio intent requires outdoor-rated materials and
  construction; indoor intent should not be satisfied by utilitarian patio furniture.
- **Material / finish / grade when specified**: If the query specifies a material
  (solid wood vs engineered wood), upholstery (top-grain leather vs bonded/faux),
  hardware finish (matte black vs brushed nickel), or grade (commercial/contract),
  treat it as a hard requirement.
- **Quantity / bundle intent**: "Set of 2", "pair", "5-piece set", "sectional 3-piece"
  implies a specific selling unit. Do not treat a single piece as a match for a set.
- **Assembly and delivery constraints when specified**: "No assembly", "fully
  assembled", "white glove delivery", "RTA/flat-pack" are purchase-decision constraints.
- **Compliance / safety / certification claims when specified**: If the query names
  a safety standard, emissions label, or certification, only match results that
  explicitly satisfy it (do not infer compliance).

### Soft constraints (helpful but secondary)

- Style family (modern, farmhouse, mid-century), color/finish family when not
  explicitly specified, reversible/convertible features when not requested,
  and price-tier alignment are useful signals but should not override hard fitment.

### Common disqualifiers

- Obvious category mismatch (e.g., returning decor, tools, or replacement parts).
- Wrong environment (indoor-only item for outdoor query, or the reverse).
- Wrong size label or explicit measurement mismatch.
