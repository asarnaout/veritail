### Suspension, Steering, and Hubs — Scoring Guidance

This query involves suspension/steering components or wheel-end hardware.

**Hard constraints:**

- **Shock vs strut is a category boundary**: Shocks and struts are different parts and are not interchangeable. If the query says strut, a shock absorber result is wrong and vice versa.
- **Loaded/complete strut assembly vs bare strut**: A complete/loaded strut assembly includes the coil spring and mount hardware. If the query asks for a complete/loaded assembly, a bare strut is incomplete.
- **Handed and position-specific parts**: Left vs right control arms, knuckles, hubs, CV axles, and some tie rods are side-specific. Enforce LH/RH and front/rear when specified.
- **Control arm vs ball joint scope**:
  - A control arm assembly may include bushings and sometimes a ball joint.
  - A ball joint alone is not a control arm.
  If the query asks for the full arm, returning only the ball joint is a scope mismatch.
- **Wheel bearing vs hub assembly scope**:
  - "Hub assembly" commonly means a complete unit (bearing + hub flange, and may incorporate ABS encoder features).
  - A press-in bearing is not the same as a full hub assembly.
  Match the query’s scope.
- **ABS encoder / tone ring compatibility (when specified)**:
  - Some wheel-end parts integrate or depend on a tone ring/encoder for ABS. If the query specifies ABS compatibility or sensor/encoder presence, enforce it.

**Significant penalties:**

- "Universal" coilover/aftermarket performance kits for an OEM replacement strut query unless the query clearly wants performance/adjustability.
- Missing included hardware when the query specifies mounts, bushings, or "with ball joint".

**Common disqualifiers:**

- Returning an alignment service kit or tools for a hard-parts query (unless explicitly requested).
- Returning sway-bar links for a control arm query (system-adjacent but wrong part).

**Terminology**:
- strut assembly = loaded strut = complete strut (typically includes spring + top mount)
- tie rod end usually means outer tie rod end; inner tie rod is a different part class
