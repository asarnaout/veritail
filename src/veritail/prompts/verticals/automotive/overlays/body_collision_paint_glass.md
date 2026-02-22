### Body, Collision, Paint, and Glass — Scoring Guidance

This query involves body panels, exterior trim, mirrors, paint-matched parts, or automotive glazing.

**Hard constraints:**

- **Paint state and paint code**:
  - Pre-painted, primed, and raw/unpainted parts are different products. Match the query’s requested finish.
  - If a query specifies a paint code (or implies OEM color match), a different paint code/color is wrong.
- **CAPA / certified collision parts (when specified)**:
  - If the query explicitly asks for CAPA-certified parts, require explicit CAPA certification evidence; do not assume "CAPA" from generic marketing language.
- **Mirror feature splits**: Heated vs non-heated, power fold, memory, blind-spot indicator, turn signal, puddle light, and camera features are hard constraints when specified.
- **Glazing classifications and markings**:
  - If the query specifies AS1/AS2/AS3 or DOT markings for glazing, enforce them.
  - Windshields are a special case: if the query is explicitly for a windshield and requires a particular AS marking, enforce it strictly.

**Significant penalties:**

- Missing required included hardware (clips, brackets) when the query is explicit. Do not penalize missing hardware when the listing is clearly panel-only and the query did not ask for hardware.
- OEM vs aftermarket: When the query says OEM/genuine, penalize aftermarket panels; when the query is cost-focused, do not overvalue OEM.

**Common disqualifiers:**

- Returning an unrelated cosmetic accessory (stickers, universal trim) for a structural collision part query.
- Returning a different body style panel (sedan vs hatchback vs wagon) when the query implies a body style.

**Terminology**:
- bumper cover = bumper fascia (often plastic outer skin; may not include reinforcement)
- grille assembly may include emblem mounts and camera provisions; treat such features as hard when specified
