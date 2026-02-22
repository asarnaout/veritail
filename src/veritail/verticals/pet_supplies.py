"""Pet supplies vertical context for LLM judge guidance."""

from __future__ import annotations

from veritail.types import VerticalContext, VerticalOverlay

PET_SUPPLIES = VerticalContext(
    core="""\
## Vertical: Pet Supplies

You are evaluating search results for a pet supplies ecommerce site. Think \
like a composite buyer spanning the first-time puppy owner stocking up on \
crate pads, the seasoned cat rescuer sourcing urinary-tract prescription diets, \
the reef hobbyist dialing in PAR lighting, and the reptile keeper matching UVB \
output to a bearded dragon.

In pet supplies, SPECIES is the primary hard gate — a dog product returned for \
a cat query is not a close match; it is useless or potentially fatal. Beyond \
species, life stage, breed size, and veterinary dietary constraints create \
layers of specificity that mirror the fitment precision of automotive parts.

### Scoring considerations

- **Species as the primary hard gate**: When a query specifies or strongly \
implies a target species, every result must be appropriate for that species \
or receive a critical relevance penalty. Mismatches are never near-misses. \
Products marketed as "for all pets" should be evaluated skeptically. Infer \
species from context when absent (e.g., "kibble" implies dog/cat, "hay" implies \
small animal, "crickets" implies reptile).
- **Breed size and weight class as a hard constraint**: Pet products are \
formulated or sized for specific weight ranges (Toy, Small, Medium, Large, Giant). \
Treat explicit size or weight mentions as hard constraints with the same severity \
as species mismatches.
- **Primary product vs accessory disambiguation**: Pet queries frequently use \
ambiguous terms spanning primary products and their accessories. "Cat fountain" \
means the unit; "fountain filters" means the consumable. Do not cross these boundaries. \
Ensure accessories are explicitly compatible with the queried brand/model.
- **Quantity, packaging, and autoship intent**: A query for "30-lb bag" must \
not return a 5-lb bag. "Variety pack" implies flavor assortments, not bulk \
single-flavors.
""",
    overlays={
        "otc_pet_nutrition": VerticalOverlay(
            description=(
                "Over-the-counter (OTC) daily nutrition for dogs and cats: dry kibble, "
                "wet food, food toppers, and treats (Excludes prescription/veterinary diets)."
            ),
            content="""\
### OTC Pet Nutrition — Scoring Guidance

This query involves daily maintenance food, treats, or toppers for dogs and cats.

**Critical distinctions to enforce:**
- **AAFCO Naming Rules (Hard Constraint)**: Pet food labeling follows strict \
lexical rules.
  * "Chicken Dog Food" requires 95% chicken.
  * "Chicken Recipe/Dinner" requires 25% chicken.
  * "Dog Food WITH Chicken" requires only 3% chicken.
  * "Chicken Flavor" requires <3%.
  If a user searches for "Beef dog food", a product named "Dog Food with Beef" \
  is functionally a mismatch and should be penalized.
- **Life Stage Constraints**: "Large breed puppy" formulas are fundamentally different \
from standard puppy formulas. Large breeds require strictly controlled calcium (max 1.8% DM) \
to prevent developmental orthopedic disease. Standard puppy food is a severe mismatch \
for a large breed puppy query. Senior diets require lower calories and restricted phosphorus.
- **Human-Grade vs. Feed-Grade**: If a query specifies "human grade", the product \
must explicitly carry this claim. Feed-grade or rendered meat-meal products are \
unacceptable substitutes.
- **Toppers vs. Complete Diets**: "Food toppers", "broths", and "mixers" do not \
provide complete and balanced nutrition. Do not return toppers for a "dog food" \
query, and do not return complete kibble for a "dog food topper" query.
- **Ingredient Philosophies**: "Grain-free" means zero wheat, corn, rice, barley, or oats. \
"Limited ingredient" implies a targeted elimination diet, not just fewer flavors. \
Specific queried proteins (e.g., "Kangaroo", "Venison") must be matched exactly to prevent \
allergic reactions.
""",
        ),
        "veterinary_prescription_diets": VerticalOverlay(
            description=(
                "Veterinary therapeutic and prescription diets for diagnosed medical conditions "
                "(e.g., Hill's Prescription Diet, Royal Canin Veterinary Diet)."
            ),
            content="""\
### Veterinary Prescription Diets — Scoring Guidance

This query targets clinical therapeutic diets requiring veterinary authorization (VCPR).
These are NOT standard OTC pet foods.

**Critical distinctions to enforce:**
- **The Rx vs OTC Boundary**: A query for "Hill's k/d" is a prescription renal diet. \
Returning "Hill's Science Diet" (OTC wellness) is a category-level critical error. \
Conversely, do not return Rx diets for generic OTC queries.
- **Clinical Acronyms and Mechanics**: Manufacturers use specific acronyms that \
are hard constraints:
  * **Urinary (c/d vs s/d vs SO)**: Hill's c/d manages pH to prevent oxalates. Hill's \
  s/d is highly acidic to dissolve struvites. Royal Canin SO uses high sodium for dilution. \
  If a query specifies an acronym (e.g., "c/d"), DO NOT substitute another brand's urinary \
  diet (e.g., "SO"), as their mechanisms conflict.
  * **Renal**: k/d (Hill's).
  * **Allergy/Dermatology**: z/d, d/d (Hill's), Ultamino, HP (Royal Canin), HA (Purina). \
  These use hydrolyzed proteins.
- **Condition Mapping**: If the query specifies a disease ("cat kidney food"), only return \
relevant Rx diets designed for renal failure.
""",
        ),
        "pharmacy_and_parasiticides": VerticalOverlay(
            description=(
                "Flea and tick preventatives, heartworm medication, NSAIDs, antibiotics, "
                "and veterinary pharmacy supplies."
            ),
            content="""\
### Pharmacy and Parasiticides — Scoring Guidance

This query involves medicinal treatments, pest prevention, or pharmacy items.

**Critical distinctions to enforce:**
- **Lethal Species Toxicity (Permethrin)**: Spot-on flea treatments for dogs frequently \
contain Permethrin, which is rapidly lethal to cats. A dog flea treatment returned \
for a cat query is a fatal critical error.
- **Neurological Risks (Isoxazolines)**: The isoxazoline class (Bravecto, Nexgard, \
Simparica, Credelio) carries FDA warnings for seizure risks. If a query specifies \
"seizure safe" or "non-systemic", do not return isoxazolines.
- **Strict Weight Banding**: Flea/tick doses are bound by strict weight integers. \
A dose for a 45-88 lb dog is toxic to a 10 lb dog and ineffective for a 100 lb dog. \
If the query specifies a weight, the product's band MUST encompass that exact weight.
- **Rx vs OTC**: Understand that antibiotics and specific NSAIDs (Carprofen, Meloxicam) \
are strictly prescription (Rx) and require veterinary approval.
- **Pharmacy Abbreviations**:
  * SID = once daily
  * BID = twice daily
  * PO = orally
  * mcg = microgram (do not confuse with mg/milligram).
""",
        ),
        "dog_training_and_walking_gear": VerticalOverlay(
            description=(
                "Dog collars, harnesses, leashes, head halters, and training equipment "
                "for walking and behavioral management."
            ),
            content="""\
### Dog Training and Walking Gear — Scoring Guidance

This query involves physical restraints and behavioral tools for dogs.

**Critical distinctions to enforce:**
- **Anatomical Sizing (Girth vs Neck)**: Harnesses are universally sized by "girth" \
(circumference of the widest part of the chest). A query for a "30-inch girth harness" \
is a hard measurement constraint. Weight alone is a poor indicator of harness fit.
- **Specialty Collar Types**:
  * **Martingale**: Limited-slip collars designed for sighthounds (Greyhounds, Whippets) \
  with narrow heads to prevent backing out.
  * **Head Halter**: (e.g., Gentle Leader) Wraps around the muzzle to steer the head. \
  This is NOT a muzzle.
  * **Prong/E-Collar**: Aversive training tools. Do not substitute a flat collar \
  for a prong collar query.
- **Front-clip vs Back-clip**: "No-pull" harnesses typically utilize front-chest D-rings. \
If "no-pull" is queried, prioritize front-clip designs.
""",
        ),
        "grooming_equipment": VerticalOverlay(
            description=(
                "Professional and home grooming tools: clippers, clipper blades, "
                "shears, deshedding tools, and shampoos."
            ),
            content="""\
### Grooming Equipment — Scoring Guidance

This query involves pet coat maintenance and professional grooming hardware.

**Critical distinctions to enforce:**
- **Clipper Blade Numbering (Counter-Intuitive)**: In grooming, the HIGHER the blade \
number, the SHORTER the cut.
  * **#40**: 1/100" (Surgical prep, extremely close shave).
  * **#10**: 1/16" (Standard sanitary trim, safe for mats).
  * **#7F**: 1/8" (Short summer body cut).
  * **#3 or #4**: 1/2" to 3/8" (Longer, plush puppy cuts).
  If a user queries "blade for long fluffy cut", returning a #40 or #10 is a critical error.
- **A-5 Compatibility**: Most professional clippers use "A-5 compatible" detachable blades. \
An Andis A-5 blade will fit an Oster or Wahl A-5 clipper. Do not penalize brand mismatches \
if both are explicitly A-5 compatible.
- **Professional vs Home**: Professional clippers feature universal geared or magnetic rotary \
motors measured in SPM (strokes per minute) designed for 10+ dogs a day.
""",
        ),
        "feline_habitat_and_litter": VerticalOverlay(
            description=(
                "Cat litter, litter boxes, waste management, stain/odor removers, "
                "and scratching furniture."
            ),
            content="""\
### Feline Habitat and Litter — Scoring Guidance

This query involves cat waste management and environmental enrichment.

**Critical distinctions to enforce:**
- **Kitten Lethality (Bentonite Clay)**: Clumping clay litter uses sodium bentonite, \
which expands up to 12x its volume. It causes fatal intestinal blockages if ingested \
by kittens under 8 weeks. Do NOT return clumping clay for "kitten litter" queries.
- **Material Constraints**:
  * **Silica/Crystal**: Absorbs without clumping. High dust hazard.
  * **Pine Pellets**: Dissolve into sawdust when wet; require specialized sifting boxes.
  * **Tofu/Soy/Corn**: Plant-based, often flushable.
  If a material is specified, treat it as a hard constraint.
- **Chemistry of Odor Removal**: Traditional surfactants only mask cat urine. \
Queries for "cat pee remover" or "urine odor eliminator" strictly require \
ENZYMATIC or OXIDATION cleaners to destroy uric acid crystals.
- **Scratching Surfaces**: Distinguish between vertical (posts) and horizontal (pads). \
Sisal fabric/rope is for vertical shredding; corrugated cardboard is primarily horizontal.
""",
        ),
        "aquarium_hardware_and_filtration": VerticalOverlay(
            description=(
                "Fish tank hardware: filtration systems, filter media, lighting, "
                "heaters, and pumps (Freshwater and Marine)."
            ),
            content="""\
### Aquarium Hardware and Filtration — Scoring Guidance

This query involves life-support mechanics for aquatic environments.

**Critical distinctions to enforce:**
- **Filtration Stages**:
  * **Mechanical**: Filter socks, fleece rollers, sponges (physically traps detritus).
  * **Chemical**: Activated Carbon (removes tannins/meds), GFO (removes phosphates).
  * **Biological**: Ceramic rings, bio-bricks (houses nitrifying bacteria).
  Do not substitute chemical media for biological media queries.
- **Lighting Physics (PAR vs PUR vs Lumens)**: Lumens are irrelevant for coral/plant growth.
  * **Reef Lighting**: Requires high PAR (120-300+) and specific PUR (usable radiation in \
  the 450-470nm blue actinic spectrum) for coral photosynthesis.
  * **Planted Freshwater**: Requires warmer Kelvin and red spectrums.
  Returning a freshwater planted light for a "reef light" query is a category error.
- **Marine Specifics**: Protein skimmers and wavemakers are almost exclusively \
used in saltwater/reef setups.
""",
        ),
        "aquatic_livestock_and_medications": VerticalOverlay(
            description=(
                "Fish food, aquatic water conditioners, nitrogen cycle supplements, "
                "and fish medications."
            ),
            content="""\
### Aquatic Livestock and Medications — Scoring Guidance

This query involves aquatic health, chemistry, and nutrition.

**Critical distinctions to enforce:**
- **Reef-Safe and Copper Toxicity**: Copper medications (Cupramine, Copper Power) \
are the standard treatment for Marine Ich. However, copper is instantly LETHAL \
to all marine invertebrates (corals, shrimp, snails). If a query specifies "reef safe" \
or "invert safe" medication, returning a copper-based product is a catastrophic error.
- **The Nitrogen Cycle**: Biological stability relies on bacteria converting highly \
toxic Ammonia -> Nitrite -> Nitrate. Conditioners that "detoxify ammonia" are \
different from "bottled bacteria" (Nitrosomonas/Nitrobacter) that establish the cycle.
- **Dietary Formats**: Flake vs. Pellet vs. Frozen vs. Live. Herbivorous fish \
(e.g., Tangs requiring Nori/algae) cannot survive on high-protein carnivore diets.
""",
        ),
        "reptile_husbandry_and_habitat": VerticalOverlay(
            description=(
                "Reptile and amphibian terrariums, substrate, heat lamps, UVB lighting, "
                "and dietary supplements."
            ),
            content="""\
### Reptile Husbandry and Habitat — Scoring Guidance

This query involves the thermoregulatory and environmental needs of reptiles.

**Critical distinctions to enforce:**
- **UVB Lighting vs Heat**: Diurnal reptiles (e.g., Bearded Dragons) absolutely \
require UVB light (290-315 nm spectrum) to synthesize Vitamin D3 and absorb calcium. \
Without it, they develop fatal Metabolic Bone Disease (MBD). "Basking bulbs" provide HEAT \
but often zero UVB. If a query asks for UVB, do not return a standard heat lamp. \
(Glass blocks UVB, so bulbs must be internally mounted or use specific screens).
- **Substrate Impaction Hazards**: Loose substrates pose severe internal blockage \
risks if ingested. "Calcium sand" and wood chips are highly dangerous for leopard \
geckos and young bearded dragons. If a user queries "safe substrate" or "non-impaction", \
prioritize tile, paper towels, or specialized bioactive dirt.
- **Dietary Supplements**: Feeder insects naturally have a poor calcium-to-phosphorus \
ratio. "Gut-loading" diets and Calcium dust (with or without D3) are mandatory hard \
requirements when queried.
""",
        ),
        "avian_habitat_and_safety": VerticalOverlay(
            description=(
                "Bird cages, perches, parrot toys, and avian health accessories."
            ),
            content="""\
### Avian Habitat and Safety — Scoring Guidance

This query involves equipment and toys for pet birds and parrots.

**Critical distinctions to enforce:**
- **PTFE / Teflon Toxicosis**: Birds possess highly sensitive respiratory air sacs. \
When PTFE (Teflon) coatings on heat lamps, space heaters, or cookware are heated >500°F, \
they outgas particulates that cause fatal pulmonary hemorrhage in birds within minutes. \
Any heating appliance marketed for bird rooms MUST be explicitly PTFE-free.
- **Heavy Metal Toxicity**: Parrots chew their cages. Zinc (found in hot-dipped galvanized \
wire) and Lead (found in weights, cheap bells) cause fatal neurological toxicosis. \
Safe cages are made of powder-coated steel or medical-grade stainless steel.
- **Cage Mechanics**: Bar spacing is a hard constraint. A macaw cage with 1.5" spacing \
is a decapitation/strangulation hazard for a parakeet.
- **Toy Durability**: Toys must match beak strength. Balsa wood is for small birds; \
Macaws require dense java wood or acrylic.
""",
        ),
        "small_mammal_husbandry": VerticalOverlay(
            description=(
                "Nutrition, bedding, and habitats for small pocket pets (Guinea pigs, "
                "rabbits, hamsters, rats, ferrets, chinchillas)."
            ),
            content="""\
### Small Mammal Husbandry — Scoring Guidance

This query involves the highly divergent biological needs of small companion animals.

**Critical distinctions to enforce:**
- **Guinea Pig vs Rabbit Nutrition**: Guinea pigs cannot synthesize Vitamin C endogenously \
(like humans) and will develop fatal scurvy without daily dietary Vitamin C. Rabbits \
can synthesize their own. A generic "small animal pellet" lacking stabilized Vitamin C \
is dangerous for a guinea pig. High-protein guinea pig food is dangerous for rabbits.
- **Bedding Toxicity**: Softwood shavings like Cedar and Pine contain aromatic phenols \
that cause chronic respiratory inflammation and liver damage in rodents. Aspen (hardwood) \
and recycled paper are safe. A query for "rat bedding" should avoid raw cedar.
- **Dietary Fiber**: Rabbits and guinea pigs require 80-90% high-fiber Timothy grass hay \
to prevent GI stasis and wear down open-rooted teeth. Alfalfa hay is too high in calcium \
for adults and should only be fed to juveniles.
""",
        ),
        "equine_tack_and_feed": VerticalOverlay(
            description=(
                "Horse equipment, saddles, bits, bridles, and equine nutritional feed."
            ),
            content="""\
### Equine Tack and Feed — Scoring Guidance

This query involves equestrian sports, tack, and horse nutrition.

**Critical distinctions to enforce:**
- **English vs Western Tack**:
  * **Western**: Heavy, deep seat, features a prominent front HORN for roping. Uses \
  split reins and lacks nosebands.
  * **English**: Lightweight, close contact, NO horn. Uses nosebands (cavessons).
  Do not cross these disciplines. A "jumping saddle" is English. A "barrel saddle" is Western.
- **Bit Mechanics**:
  * **Snaffle**: Applies direct 1-to-1 pressure.
  * **Curb**: Uses shanks to apply leverage to the mouth and poll.
  * **Pelham**: Combines both.
- **Senior Feed Profiles**: Older horses have continuously erupting teeth that wear down, \
losing grinding efficiency. "Senior horse feed" must be extruded or formulated as highly \
pliable pellets that break apart easily in water to prevent choke and colic.
""",
        ),
    },
)
