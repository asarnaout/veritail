### Wheels, Tires, and TPMS — Scoring Guidance

This query involves wheels/rims, tires, lug hardware, spacers, or TPMS sensors.

**Hard constraints (physical fitment):**

- **Tire size must match**: A tire size like 225/45R17 encodes width, aspect ratio, and wheel diameter. Mismatching any of these is wrong unless the query explicitly asks for alternatives ("plus size", "similar diameter").
- **Service description (load index + speed rating)**:
  - If the query specifies a service description (e.g., 94W) or minimum load/speed rating, enforce it. These relate to how much load a tire can carry and its tested maximum speed category.
- **Wheel bolt pattern / PCD**: 5x114.3 vs 5x112 are not compatible. Treat mismatch as disqualifying.
- **Center bore and hub-centricity**: A wheel must match the hub bore directly or explicitly include a centering ring solution. If the query specifies hub bore or "hub-centric", enforce it.
- **Offset/backspacing**: Offset controls clearance and steering/suspension geometry. If the query specifies offset/backspacing (common in fitment-focused wheel queries), enforce it.
- **Wheel diameter and width**: A 17x8 wheel is not a 17x7 wheel. When wheel size is specified, enforce both diameter and width.
- **Lug hardware thread pitch/seat type (when specified)**: E.g., M12x1.5 vs M12x1.25 and conical vs ball seat matter; treat mismatches as disqualifying when specified.

**Tire construction and orientation (enforce when specified):**

- **Directional tires**: Usually marked with an arrow / "rotation". They must be oriented correctly.
- **Asymmetrical tires**: Marked "inside/outside" and must be mounted with the correct side facing out.
- **Run-flat / XL / load range (SL vs XL vs LT)**: These are meaningful constraints when stated.

**TPMS-specific constraints:**

- **Frequency matters**: TPMS sensors commonly transmit at 315MHz or 433MHz. If the query specifies frequency, it is a hard requirement; the wrong frequency can prevent relearn/programming.
- **Direct-fit vs programmable**: OE-direct-fit sensors vs universal programmable sensors are different product intents. If the query asks for OE-direct-fit, treat "universal programmable" as a weaker match unless it explicitly supports the vehicle.

**Common disqualifiers:**

- Returning tires for a wheel query (or wheels for a tire query) unless the query asks for a wheel+tire package.
- Returning lug nuts/bolts with the wrong thread pitch or seat type when the query specifies them.

**Terminology**:
- PCD = bolt pattern
- offset is often written ET (e.g., ET35)
