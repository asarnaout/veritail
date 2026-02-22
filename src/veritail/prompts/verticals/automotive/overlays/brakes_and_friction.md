### Brakes and Friction — Scoring Guidance

This query involves brake parts (pads, rotors, calipers, drums/shoes, parking brake parts, brake kits).

**Hard constraints:**

- **Disc vs drum is a category boundary**: Pads go with rotors (disc brakes). Shoes go with drums (drum brakes). Do not substitute across these.
- **Axle/position matters**: Front vs rear, left vs right (where applicable), and inner vs outer pads (in some caliper designs) are hard constraints when specified.
- **Brake package splits are common**: Rotor diameter, vented vs solid rotors, and caliper/bracket variants can differ within the same YMM (e.g., base vs sport trim, towing package). If the query includes rotor size, "big brake" wording, or a specific trim/package, enforce it.
- **Kit integrity**: A "pad + rotor kit" query expects both pads and rotors for the specified axle. Returning only pads or only rotors is incomplete.
- **Parking brake style**: Many rear rotors are "drum-in-hat" with an internal parking brake shoe. If the query calls out parking brake shoes/hardware, do not return disc pads.

**Brake-lining identification quirks (high-value signals if present in the query):**

- **Friction rating (two-letter code)**: Some pads carry a friction coefficient code such as EE/FF/GG. The two letters reflect "cold" and "hot" friction behavior. If the query includes a friction code, treat it as a constraint.
- **Pad shape codes (FMSI / D-number)**: A pad shape number like "D154" is an industry shape identifier. If the query includes it, matching that shape is a strong relevance signal.

**Significant penalties:**

- **Missing hardware vs hardware-included mismatch**: If the query says "hardware included" or "with clips/shims", prefer results that include the hardware kit. If the query is only for pads, do not penalize a pad-only listing.
- **Performance compound mismatches**: "Ceramic", "semi-metallic", "track", and "low-dust" are meaningful when specified. Do not treat them as interchangeable when explicitly requested.

**Common disqualifiers / critical errors:**

- Returning brake fluid for a pads/rotors query (unless the query explicitly asks for brake fluid).
- Returning "universal" racing pads for a street OEM pad query when the query clearly expects an OEM-style direct replacement.

**Terminology**:
- rotor = brake disc
- caliper bracket = mounting bracket / anchor bracket (often sold separately; match query scope)
