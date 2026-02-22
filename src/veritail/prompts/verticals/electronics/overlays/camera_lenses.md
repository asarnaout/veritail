### Camera Lenses and Lens Adapters — Scoring Guidance

This query involves a lens (or a lens adapter), where mount compatibility is the primary hard gate.

**Critical distinctions to enforce:**

- **Lens mount matching is mandatory**: A lens must match the camera mount (or explicitly include the correct adapter). EF/EF-S vs RF, Nikon F vs Z, Sony E/FE, and Micro Four Thirds are distinct mounts.

- **Adapter specificity**: If the query is for adapting a legacy mount to a new mount, the correct adapter name/class is the product. Do not return unrelated adapters with the same physical connector idea.

- **FE vs E nuance (Sony)**: Full-frame FE lenses can be used on APS-C E-mount bodies (with crop), but APS-C lenses on full-frame bodies can force crop mode or vignette. If the query is explicit about full-frame coverage, enforce it.

- **Focal length / zoom range**: If the query specifies a focal length (e.g., 50mm) or a zoom range, treat it as a hard requirement. Do not substitute "close" focal lengths unless the query is clearly broad.

- **Do not substitute camera bodies**: A lens query should not return camera bodies or lens caps/filters as the main results.
