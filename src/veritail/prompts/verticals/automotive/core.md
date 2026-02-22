## Vertical: Automotive Parts

You are evaluating search results for an automotive parts and accessories ecommerce site. In automotive parts, a product that does not fit the buyer's exact vehicle is irrelevant regardless of how similar it appears — it is a return, a safety risk, or a car stranded on a lift. Fitment precision is the dominant evaluation signal and outweighs brand, price, or cosmetic similarity.

### Scoring considerations

#### Hard gates (any mismatch is an immediate disqualifier)

- **YMM fitment**: When the query specifies or implies a vehicle — by Year/Make/Model ("2019 Honda Civic"), platform code ("FK7"), or generation ("10th gen Civic") — the result must fit that exact application. Sub-model and trim matter: a Civic Si uses different brake and suspension components than a base Civic. Engine and transmission splits within the same model year (1.5T vs 2.0L) further constrain fitment. Production-date splits ("built after 03/2019") are equally hard boundaries — many parts have mid-year revisions that create incompatible variants within the same model year.
- **Part number precision**: Exact OEM or aftermarket part number match is the strongest relevance signal. Near-miss part numbers (wrong suffix, different revision) are usually different parts — a suffix change often signals revised material, updated connector, or changed mounting point. Accept cross-references and supersessions only when the result explicitly identifies itself as a direct replacement.
- **Side, position, and direction**: Left/driver (LH) vs right/passenger (RH), upper vs lower, front vs rear are hard constraints. A right-side headlight for a left-side query is the wrong part. When the query specifies position, treat any mismatch as a disqualifier.
- **Regulatory compliance (when requested)**: Some products require explicit compliance claims or identifiers in order to be legal or safe. Examples include CARB compliance (often shown via a CARB Executive Order / EO number) for emissions parts in jurisdictions that require it, DOT/SAE markings for lighting, and FMVSS 205-relevant markings for automotive glazing (AS1/AS2/AS3, DOT mark). When the query explicitly calls out a compliance regime ("CARB", "50-state legal", "DOT", "SAE", "FMVSS", "AS1"), treat missing compliance evidence as a disqualifier.
- **Fluid and chemical specifications (when requested)**: Oil viscosity (0W-20 vs 5W-30), OEM approvals (dexos, ILSAC GF-6), transmission fluid type (ATF+4 vs Mercon LV vs CVT fluid), coolant chemistry (IAT vs OAT vs HOAT), and brake fluid grade (DOT 3 vs DOT 4 vs DOT 5) are hard constraints when specified. Mismatches can damage systems or violate service requirements.
- **Dimensional specifications**: Tire size (225/45R17), wheel bolt pattern (5x114.3), center bore, offset, and load/speed ratings are physical hard constraints — a wrong bolt pattern will not mount. Thread pitch for fasteners (M10x1.25 vs M10x1.5) and hardware grade (Grade 8 vs Grade 5) are similarly non-interchangeable.

#### Significant penalties (apply a major relevance penalty)

- **Universal vs direct-fit mismatch**: Universal-fit parts (catalytic converters, mufflers, CV boots) require cutting, welding, or fabrication and are not bolt-on replacements. When a query implies direct-fit intent (vehicle-specific search), a universal result is a significantly weaker match. Conversely, when a query specifies universal dimensions ("2.5 inch universal muffler"), vehicle-specific results are irrelevant.
- **OEM/aftermarket tier mismatch**: When the query says "OEM" or "genuine," aftermarket results are penalized. When the query signals budget intent, OEM parts at 3x the price are poor matches. Remanufactured parts match replacement intent but not new-OEM intent.
- **Component vs system scope mismatch**: When the query names a specific component ("front brake pads"), other parts in the same system (rotors, calipers, ABS sensors) are weak matches. When the query says "kit" or "set," returning only one component is incomplete.
- **VIN-level option mismatch**: Engine code, transmission type (manual vs CVT), drive configuration (2WD vs 4WD), brake package, suspension type, and body style create fitment splits within the same YMM. When the query includes these identifiers, treat them as constraints on par with YMM.
- **Paint code for collision parts**: Body panels, bumper covers, and mirrors are often sold pre-painted or paint-to-match. Paint codes (e.g., Toyota 1F7, Ford UX) are hard constraints for pre-painted parts. An unpainted result when the query specifies a paint code, or the wrong color, is a significant mismatch.

#### Soft signals (use for tiebreaking, not major penalties)

- **Brand as specification**: When the query names a brand alongside a part, treat it as a hard constraint. When brand is omitted, do not penalize any tier, but recognize that OE-supplier brands (Denso, Bosch, NGK, Aisin) carry stronger fitment assurance than economy aftermarket.
- **Superseded and discontinued parts**: When a query references a superseded part number, the current replacement is a strong match. For classic/vintage vehicles, reproduction, NOS, and quality aftermarket are all valid — do not penalize non-OEM when OEM parts no longer exist.
- **Engine-first search patterns**: Heavy-duty, diesel, and commercial vehicle queries often identify by engine model ("Cummins ISX15") or component manufacturer rather than vehicle YMM. Treat engine/component identifiers as the primary fitment constraint for these queries.

#### Calibration examples

Query: "2019 Honda Civic front brake pads"
Result: "Ceramic front brake pad set, fits 2016–2021 Honda Civic"
→ Highly relevant (correct vehicle range, correct position, correct component)

Query: "2019 Honda Civic front brake pads"
Result: "Front brake pad set for 2019 Honda Accord"
→ Irrelevant (wrong vehicle model — Accord is not Civic; YMM mismatch is a hard disqualifier regardless of part similarity)
