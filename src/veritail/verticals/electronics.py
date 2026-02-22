"""Electronics vertical context for LLM judge guidance."""

from veritail.types import VerticalContext, VerticalOverlay

ELECTRONICS = VerticalContext(
    core="""\
## Vertical: Electronics

You are evaluating search results for a consumer electronics or computer components \
site. Think like a composite buyer spanning the system builder who searches by exact \
model number and socket type, the IT procurement specialist who needs precise SKU and \
compatibility-matrix alignment, and the mainstream consumer who searches by brand plus \
category and relies on the store to prevent incompatible results. Your overriding \
concern is whether a returned product will actually work with the buyer's existing \
hardware, platform, or device—because in electronics, a wrong-generation or \
wrong-connector result is not merely a weak match, it is a potential return.

### Scoring considerations

- **Compatibility is the primary hard gate**: Wrong platform, socket, device model, or \
connector type should heavily penalize relevance even when the product is in the correct \
category. A DDR4 kit returned for a DDR5-only AM5 board query, an LGA 1700 cooler \
shown for an LGA 1851 search, or a Lightning cable surfaced for a USB-C iPhone query \
are functional mismatches that guarantee a return. Treat incompatibility the way \
industrial supply treats wrong thread pitch—an immediate disqualifier unless the query \
is genuinely open-ended.
- **Connector, interface, and protocol precision**: USB-C vs USB-A, Lightning vs USB-C, \
Thunderbolt vs USB-C (same connector, different capability), HDMI 2.2 vs 2.1 vs 2.0, \
DisplayPort vs Mini DisplayPort, SODIMM vs DIMM, M.2 2230 vs 2280, NVMe vs SATA M.2, \
PCIe Gen 3/4/5 lane count, and CPU socket/chipset pairings are hard constraints when \
specified or clearly implied. A "Thunderbolt 4 dock" query answered with a USB-C hub \
lacking Thunderbolt certification is a material mismatch even though the physical \
connector is identical. Similarly, an M.2 SATA drive shown for an "NVMe SSD" query \
will not boot in many NVMe-only slots. Cable certification also matters: an uncertified \
USB-C cable may deliver only USB 2.0 speeds (480 Mbps) despite the connector being \
physically identical to a certified 40 Gbps Thunderbolt cable—treat cable-spec queries \
as requiring matching certification level.
- **Model-generation and architecture specificity**: Queries naming exact models or \
generations ("RTX 5090", "Ryzen 9 9950X", "iPhone 16 Pro Max", "Wi-Fi 7 router") \
require exact-generation alignment. Adjacent generations are weaker matches because \
they often differ in socket, chipset, feature support, or physical dimensions—an RTX \
4090 waterblock will not fit an RTX 5090 with a different PCB layout, and an iPhone 15 \
case will misalign camera cutouts on an iPhone 16. Only score an adjacent generation \
highly when the query is explicitly broad ("RTX GPU") or the product is confirmed \
cross-generation compatible.
- **Spec-driven intent as explicit requirements**: When a query states capacity (2 TB), \
speed class (U3 V30 A2), wattage (850W), refresh rate (240 Hz), resolution (4K/1440p), \
response time, panel type (OLED, IPS, VA), efficiency rating (80+ Gold), or wireless \
standard (Wi-Fi 7 / 802.11be), treat those as hard filters, not soft preferences. A \
"240 Hz gaming monitor" query answered with a 165 Hz panel is a meaningful miss even if \
the panel is otherwise excellent. Note overlapping spec nomenclature: SD card speed \
classes (Class 10, UHS-I U3, V30, A2) each measure different things—match the specific \
class the query references.
- **Form factor and physical fit constraints**: ATX vs Micro-ATX vs Mini-ITX \
motherboards, SFX vs ATX power supplies, 2.5-inch vs 3.5-inch drives, M.2 2230 vs \
2242 vs 2280 SSDs, and tower vs low-profile GPU brackets determine whether a component \
physically fits a build. A full-height GPU shown for an SFF build query, or a standard \
ATX PSU for an ITX case, will not install. GPU length, CPU cooler height clearance, \
and radiator mount support are real-world fitment concerns that affect relevance when \
form factor is specified.
- **Device-specific accessory exactness**: Accessories—cases, screen protectors, chargers, \
bands, cartridges, cables, mounts—are only relevant if they match the exact device \
model or a confirmed-compatible model range. An "Apple Watch Ultra 2 band" query must \
return bands that fit the 49mm case-size compatibility group (Ultra); a "Galaxy S25 Ultra case" \
must not return S24 \
Ultra cases despite near-identical names, because camera module layout and corner \
geometry differ. For \
printer ink/toner, cartridge model numbers are non-negotiable—HP 63 and HP 63XL are \
compatible with the same printers, but HP 65 is not. Penalize heavily when the result \
is for a sibling or predecessor model with incompatible physical dimensions.
- **Ecosystem and platform lock-in**: Some queries carry implicit ecosystem constraints— \
"MagSafe charger" implies Apple iPhone 12 or later, "AirPods case" implies the \
specific AirPods generation, "PS5 controller" excludes Xbox-only peripherals, \
"HomeKit thermostat" requires Apple Home support (not just Alexa or Google Home). \
Matter-certified devices broaden compatibility but not universally—each ecosystem \
supports different Matter device-type versions. Score ecosystem-aligned products \
higher when the query signals platform intent, and penalize cross-ecosystem products \
that would require unsupported bridging.
- **Condition, lock status, and market constraints**: Distinguish new vs refurbished vs \
open-box vs renewed when the query specifies condition. "Unlocked phone" is a hard \
constraint—carrier-locked devices are not acceptable substitutes. Region-locked or \
voltage-specific products (110 V vs 220 V power tools, region-coded Blu-ray players, \
non-US-band phones missing key LTE/5G bands) are functional mismatches in the wrong \
market. Warranty presence or absence also matters when the query signals it.
- **Primary product vs accessory disambiguation**: "Laptop charger" should not return \
laptops; "Nintendo Switch dock" should not return the console itself; "camera lens" \
should return lenses, not camera bodies. Conversely, "laptop" should not be dominated \
by laptop bags and stands. Score results that match the correct product-role intent \
(primary device, replacement part, consumable, accessory, peripheral) and penalize \
role inversions.
- **Recency, generation currency, and lifecycle awareness**: For queries using "latest", \
"newest", "best", or "2026", prioritize current-generation products. Older generations \
may still be relevant when queries signal budget intent, or when the previous generation \
remains widely available and price-competitive (e.g., last-gen GPUs during supply \
shortages). However, discontinued or end-of-life products with no warranty path should \
score lower unless the query explicitly seeks them. Be aware that chipset and platform \
names recycle—"Z790" and "Z890" serve different CPU generations despite similar naming.
- **Bundle, kit, and completeness intent**: When the query implies a complete solution \
("PC build kit", "surveillance camera system", "mesh Wi-Fi system"), individual \
components or single units are weaker matches. Conversely, when the query targets a \
single component ("replacement fan", "single stick 16 GB DDR5"), multi-packs or bundles \
may over-serve or over-price, reducing relevance.
- **Brand and SKU-level precision**: In electronics, model numbers and SKUs carry dense \
information. Queries containing full or partial model numbers ("WD Black SN850X", \
"Sony WH-1000XM5", "Samsung 990 Pro 2TB") demand exact or near-exact SKU matches. \
Returning a different product from the same brand line (SN770 instead of SN850X) is a \
relevance failure, not a close match—the specs, performance tier, and price point \
diverge substantially even within the same product family.""",
    overlays={
        "gaming_desktop_pcs": VerticalOverlay(
            description=(
                "Prebuilt / assembled gaming desktop PCs and towers (NOT individual PC parts); queries listing CPU+RAM+storage+GPU desktop specs"
            ),
            content="""\
### Gaming Desktop PCs — Scoring Guidance

This query is about an assembled, prebuilt gaming desktop PC (tower or small-form-factor gaming desktop), \
not a single component.

**Critical distinctions to enforce:**

- **Prebuilt PC vs parts**: Queries that read like a full system spec (CPU + RAM + storage, often GPU and \
Windows) expect a complete computer. Do not treat CPUs, GPUs, RAM kits, SSDs, cases, power supplies, or \
motherboards as relevant substitutes.

- **Desktop vs laptop vs mini PC**: Do not return gaming laptops for a desktop query. Do not return \
laptop-only parts (e.g., SO-DIMM kits, laptop GPUs) for a desktop PC query. A "mini PC" / "NUC-style" \
query expects that small chassis class; a full tower is a weaker match and a bare motherboard is a mismatch.

- **CPU model is the identifier when specified**: Treat full CPU model strings as hard requirements when \
present (e.g., Ryzen 7 5700G ≠ Ryzen 7 5700X). If the query calls out integrated graphics (common in \
"G" class APUs), do not substitute a CPU variant without iGPU unless a discrete GPU is explicitly included.

- **GPU tiers are not interchangeable**: "Ti", "SUPER", and different series numbers are distinct SKUs. \
If the query specifies "RTX 4070 SUPER", an RTX 4070 (non-SUPER) is not a close match. If the query is \
for a desktop GPU tier, do not treat a "Laptop GPU" listing as equivalent.

- **Memory and storage are purchase-defining specs**: Treat DDR generation (DDR4 vs DDR5), capacity, and \
often speed as strong constraints when specified. Treat NVMe vs SATA, and PCIe Gen requirements as hard \
constraints when requested.

- **System completeness**: If the query implies "ready to plug in and use" (common for consumer pre-builts), \
barebones systems (missing RAM/SSD/OS) are weaker matches unless the query explicitly says "barebones", \
"mini barebone", or "kit".

- **OS / license constraints**: If the query specifies Windows edition ("Windows 11 Pro") or \
"no OS / Linux / FreeDOS", treat that as a meaningful constraint; do not ignore it just because the hardware \
matches.
""",
        ),
        "office_desktops_workstations_aio_mini": VerticalOverlay(
            description=(
                "Non-gaming desktops: office desktops, mini PCs, workstations, all-in-one PCs (AIO) (NOT monitors alone, NOT laptop computers)"
            ),
            content="""\
### Office Desktops, Workstations, All-in-Ones, and Mini PCs — Scoring Guidance

This query is about a non-gaming desktop computer class: classic desktops, compact mini PCs, all-in-one PCs, \
or professional workstations.

**Critical distinctions to enforce:**

- **All-in-one (AIO) vs monitor vs desktop tower**: An AIO includes the computer built into the display. \
Do not treat a monitor-alone listing as relevant for an AIO query, and do not treat a tower-only listing \
as an AIO unless the listing explicitly includes the integrated display.

- **Mini PC vs tower**: "Mini PC", "NUC-style", "Tiny", and similar terms imply a compact chassis class \
with laptop-style CPUs/thermals and often laptop-form-factor RAM (SO-DIMM). A full-size tower can be a \
weaker match; parts are mismatches.

- **Workstation is not a synonym for gaming PC**: "Workstation" intent often implies stability and \
professional features (ECC support, certified drivers, pro GPUs, virtualization features). Do not substitute \
a consumer gaming tower for an explicit workstation query unless the query is broad and allows equivalents.

- **OS and manageability**: Office/procurement queries commonly specify Windows Pro vs Home, or \
"business" lines. Treat OS edition constraints as meaningful when specified.

- **Form factor and mounting**: Some mini PCs and AIOs are VESA-mountable; if the query specifies \
VESA mounting or "wall mount", treat that as a hard requirement.

- **Do not confuse storage capacity with memory**: Many listings say "16GB + 512GB"—the first is RAM, \
the second is storage. Keep these separate in relevance judgments.
""",
        ),
        "gaming_laptops": VerticalOverlay(
            description=(
                "Gaming laptops / gaming notebooks (RTX/GTX gaming laptop, high refresh screens, 'H/HX' CPUs); NOT desktops or components"
            ),
            content="""\
### Gaming Laptops — Scoring Guidance

This query involves a gaming laptop / gaming notebook.

**Critical distinctions to enforce:**

- **Laptop GPU ≠ desktop GPU**: Portable GPUs are configured by OEMs and can vary widely in power/performance \
even with the same name. Do not treat a desktop GPU listing as relevant for a gaming-laptop query, and do \
not assume a desktop-level performance tier from the name alone.

- **GPU name must match, including tier markers**: "Ti", "SUPER", and distinct series numbers are not \
synonyms. If the query specifies a GPU tier (e.g., "RTX 4070"), do not treat "RTX 4060" or "RTX 4070 Ti" \
as close matches.

- **TGP / wattage constraints**: If the query includes GPU power (TGP) or laptop "wattage" constraints, \
treat them as hard. Otherwise, do not penalize a correct GPU-name match just because the listing omits TGP \
(but do penalize results clearly outside the requested power class, e.g., ultra-thin 35W variants for \
explicit "high watt" requests).

- **Display specs are often hard requirements**: Screen size, resolution (1080p/1440p/4K), refresh rate \
(144/165/240 Hz), and panel type (OLED/IPS) should be treated as hard when specified. A 165 Hz panel is \
not a good match for an explicit 240 Hz request.

- **Connector expectations**: If the query includes "Thunderbolt", "USB4", "HDMI 2.1", or specific port needs \
(for external monitors/docks), enforce those constraints. Many gaming laptops have USB-C ports that are \
data-only or do not support DisplayPort output.

- **Do not confuse RAM vs VRAM**: A query for "16GB RAM" is system memory, not "16GB GPU VRAM". Treat them \
as different constraints.

- **Chargers and docks are not laptops**: If the query is for a "laptop charger", "replacement adapter", \
or "dock", do not surface laptops.
""",
        ),
        "productivity_laptops_ultrabooks": VerticalOverlay(
            description=(
                "Non-gaming laptops: ultrabooks, business laptops, student laptops, 2-in-1s, Chromebooks, thin-and-light; NOT gaming-centric laptops unless requested"
            ),
            content="""\
### Productivity Laptops, Ultrabooks, 2-in-1s, and Chromebooks — Scoring Guidance

This query involves a non-gaming laptop class: thin-and-light Windows laptops, business machines, 2-in-1 \
convertibles, or Chromebooks.

**Critical distinctions to enforce:**

- **OS is a hard gate when specified**: Windows vs ChromeOS vs macOS are different ecosystems. \
A "Chromebook" query should not return Windows laptops and vice versa unless the query is ambiguous.

- **CPU segment suffixes signal class**: When the query includes suffixes such as Intel U/P/H/HX or \
explicit "ultrabook"/"thin and light", treat it as a performance/thermal class constraint rather than a \
minor preference. Do not match a low-power U-class request with a heavy gaming H/HX-class machine.

- **2-in-1 / convertible vs clamshell**: If the query specifies "2-in-1", "convertible", or "detachable", \
treat hinge/form factor as a hard requirement. Do not substitute a standard clamshell laptop.

- **Business features**: If the query requests business features (smart card, fingerprint, LTE/5G WWAN, \
vPro/management, Thunderbolt docking), enforce them. These are not generic across consumer laptops.

- **Storage vs memory disambiguation**: Many listings use "16GB + 512GB" shorthand. Treat the first as RAM \
and the second as SSD capacity; do not swap or conflate them.

- **"Laptop" vs accessories**: If the query is for a laptop, do not let results be dominated by \
laptop bags, sleeves, stands, or chargers.
""",
        ),
        "macbooks": VerticalOverlay(
            description=(
                "Apple MacBook laptops (MacBook Air, MacBook Pro; Apple Silicon M-series; macOS); NOT generic Windows laptops"
            ),
            content="""\
### MacBooks — Scoring Guidance

This query is about Apple MacBook laptops (MacBook Air / MacBook Pro).

**Critical distinctions to enforce:**

- **Model line and size are not interchangeable**: "MacBook Air" vs "MacBook Pro" and screen size \
(13/14/15/16-inch) are strong constraints when specified.

- **Apple Silicon generation matters**: If the query specifies M-series generation (e.g., M1/M2/M3/M4) \
or tier (base vs Pro vs Max vs Ultra), treat it as a hard identifier. Adjacent generations are weaker \
matches unless the query is explicitly broad (e.g., "MacBook Air").

- **Unified memory vs storage**: Many listings present "16GB / 512GB" where the first is unified memory \
and the second is SSD storage. Do not confuse these.

- **Ports and charging**: If the query explicitly requests MagSafe charging, specific Thunderbolt/USB-C \
port counts, or HDMI/SD slot presence, enforce it. Accessory ecosystems differ across generations.

- **Do not confuse MacBooks with iPads**: For queries containing "MacBook", do not return iPads or \
iPad keyboard cases as substitutes, even if they are "laptop-like", unless the query explicitly allows \
tablet alternatives.
""",
        ),
        "tablets_and_ereaders": VerticalOverlay(
            description=(
                "Tablets and e-readers (iPad, Android tablets, Kindle/Kobo), Wi-Fi vs cellular, storage tier; NOT laptop computers"
            ),
            content="""\
### Tablets and E-Readers — Scoring Guidance

This query involves a tablet or an e-reader device.

**Critical distinctions to enforce:**

- **Tablet vs laptop vs accessory**: If the query is for the tablet device, do not return keyboard cases, \
folios, screen protectors, or styluses as substitutes.

- **Wi-Fi vs cellular is a core SKU split**: If the query specifies cellular/5G/LTE, require a cellular-capable \
model. If it specifies Wi-Fi-only (or is price-sensitive and only mentions Wi-Fi), do not assume cellular.

- **Generation and screen size are part of compatibility**: Many tablets share the same family name across \
generations, but accessories (cases, keyboard connectors, styluses) can be generation-specific. Treat the \
exact generation/year or model identifier as a hard requirement when provided.

- **Storage and RAM disambiguation**: For tablets, "128GB/256GB/..." typically refers to storage, not RAM. \
If the query specifies both (common in Android tablets), keep them distinct.

- **Stylus ecosystem**: If the query implies an active stylus (e.g., "Apple Pencil", "pen support"), be \
aware that stylus compatibility can be generation-specific; do not treat any generic capacitive stylus as \
equivalent for active-pen intent.

- **E-readers are not generic tablets**: For Kindle/Kobo-like intent, do not substitute Android tablets unless \
the query explicitly allows a general-purpose tablet.
""",
        ),
        "wearables": VerticalOverlay(
            description=(
                "Wearables: smartwatches, fitness trackers, smart rings; includes GPS vs cellular watch variants; NOT phones/tablets"
            ),
            content="""\
### Wearables (Smartwatches / Fitness Trackers / Rings) — Scoring Guidance

This query involves a wearable device.

**Critical distinctions to enforce:**

- **Ecosystem compatibility matters**: Some wearables require a specific phone ecosystem for full features \
(e.g., Apple Watch features depend heavily on iPhone). If the query implies an ecosystem, enforce it.

- **GPS vs cellular watch SKUs**: If the query specifies cellular/LTE, require the cellular model; \
do not substitute GPS-only variants. Conversely, do not penalize GPS-only when the query is clearly Wi-Fi/GPS.

- **Case size and band compatibility**: If the query includes a case size (e.g., 41mm/45mm/49mm), treat it \
as a meaningful selector. Accessory fitment depends on case-size families.

- **Health sensor features**: If the query requests a specific sensor capability (ECG, temperature, SpO2, \
fall detection), enforce it; these features are not universal across models or generations.

- **Do not substitute bands for devices**: If the query is for the wearable device, bands and chargers are \
accessories, not substitutes.
""",
        ),
        "pc_cpus": VerticalOverlay(
            description=(
                "Desktop computer processors/CPUs (Intel Core/Core Ultra, AMD Ryzen, Threadripper); queries with socket/chipset, 'CPU only', cores/threads; NOT complete PCs"
            ),
            content="""\
### Desktop CPUs / Processors — Scoring Guidance

This query is about a CPU sold as a standalone component, not a complete computer.

**Critical distinctions to enforce:**

- **CPU vs full PC**: Do not treat full desktops/laptops as relevant for a CPU-only query. If the query is \
for a CPU, matching the CPU model is the primary signal.

- **Model identifier includes suffix**: Intel and AMD suffix letters are part of the model identity. \
Intel "F" models require discrete graphics (no iGPU), while "K" indicates an unlocked SKU. Treat these as \
hard when the query includes them. For AMD, "G" desktop parts indicate integrated graphics variants \
(commonly listed as "with Radeon Graphics")—do not treat a non-G CPU as the same part.

- **Socket / platform constraints**: If a query references a socket/platform (AM4 vs AM5; LGA 1700 vs newer), \
treat it as a hard requirement. CPUs cannot be used across sockets, even within the same brand.

- **Boxed vs tray / OEM**: If the query specifies "boxed" (retail) vs "tray/OEM", treat that as a stated \
requirement. In many markets, boxed CPUs have different included accessories (e.g., cooler) and warranty \
paths compared with OEM/tray.

- **Cooler included vs not**: If the query explicitly asks for a CPU "with cooler" or references a stock \
cooler name, treat inclusion as a meaningful constraint.

- **Avoid series-name substitution**: Within a brand family, adjacent SKUs can differ materially. \
Treat "Ryzen 7 5700X" vs "5700G" or "Intel i5-14600K" vs "i5-14600" as distinct products unless the query \
explicitly allows alternatives.
""",
        ),
        "pc_gpus": VerticalOverlay(
            description=(
                "Graphics cards / GPUs / video cards (RTX/Radeon/Arc; workstation GPUs; AIB cards); NOT gaming PCs or laptops"
            ),
            content="""\
### Graphics Cards / Discrete GPUs — Scoring Guidance

This query involves a discrete graphics card (add-in GPU), not a full computer.

**Critical distinctions to enforce:**

- **GPU vs full system vs accessories**: Do not treat gaming PCs, motherboards, or "GPU support brackets" \
as relevant substitutes for a GPU query.

- **Exact GPU SKU matters**: Treat tier markers as part of the name (Ti / SUPER / XT / XTX). \
An RTX 4070 is not a close match for RTX 4070 Ti, and RX 7900 XT is not the same as RX 7900 XTX.

- **Form-factor and case fit**: If the query includes physical constraints (ITX build, 2-slot, low-profile, \
length limits, dual-fan vs triple-fan), treat them as hard—many GPUs will not physically fit.

- **Power connector compatibility matters**: High-end modern GPUs may use 16-pin power (12VHPWR / 12V-2x6) \
while others use 8-pin PCIe connectors. If the query specifies a connector type (or a right-angle / \
melt-safe cable), treat it as hard; mismatches can be safety-critical.

- **Workstation vs gaming GPUs**: If the query includes "workstation", "pro", "RTX A-series", "Quadro", \
or similar terms, do not substitute consumer gaming cards unless explicitly allowed—the driver stack and \
certifications are part of the buyer intent.

- **Do not confuse VRAM for system RAM**: "16GB GPU" refers to graphics VRAM, not computer memory.
""",
        ),
        "motherboards": VerticalOverlay(
            description=(
                "PC motherboards (Intel/AMD sockets, chipsets, ATX/mATX/ITX, DDR4/DDR5); NOT CPUs or RAM kits alone"
            ),
            content="""\
### Motherboards — Scoring Guidance

This query involves a motherboard.

**Critical distinctions to enforce:**

- **Socket and chipset are hard gates**: Match motherboard socket to the CPU platform implied by the query. \
Do not substitute between sockets even if the board is the same brand or price tier.

- **DDR generation support**: Motherboards are typically either DDR4 or DDR5. If the query specifies DDR4 \
or DDR5, treat it as a hard requirement; the wrong memory generation will not fit.

- **Form factor controls physical fit**: ATX vs micro-ATX vs mini-ITX is a hard constraint when specified \
because it determines case compatibility and expansion slot layout.

- **Integrated Wi-Fi / connectivity**: If the query specifies Wi-Fi (especially a generation such as Wi-Fi 6E \
or Wi-Fi 7), treat it as a requirement; many boards come in both Wi-Fi and non-Wi-Fi variants with nearly \
identical names.

- **M.2 / PCIe slot capabilities**: If the query specifies PCIe Gen 5 storage, NVMe slot count, or specific \
M.2 lengths (2230/2280/22110), treat these as hard constraints. A board may have an M.2 slot physically but \
not support the requested protocol or generation.

- **Motherboard vs accessories**: Do not treat "I/O shield", "Wi-Fi antennas", or "motherboard standoffs" \
as relevant results for a motherboard query.
""",
        ),
        "memory_ram": VerticalOverlay(
            description=(
                "Computer memory (RAM): DDR4/DDR5 DIMM & SO-DIMM kits, capacity/speed/timings, ECC vs non-ECC; NOT storage drives"
            ),
            content="""\
### Memory (RAM) — Scoring Guidance

This query involves system memory (RAM).

**Critical distinctions to enforce:**

- **DDR generation is non-negotiable**: DDR4 and DDR5 are not interchangeable. If the query specifies DDR4 \
or DDR5, treat it as a hard gate.

- **Form factor matters**: DIMM (desktop) and SO-DIMM (laptop/mini PC) are different physical modules. \
If the query specifies SO-DIMM, do not return desktop DIMMs and vice versa.

- **ECC / registered vs unbuffered**: If the query asks for ECC memory, enforce ECC. If it asks for \
RDIMM/registered or UDIMM/unbuffered, enforce that distinction—server-class RDIMMs are not valid substitutes \
for consumer UDIMMs.

- **Kit composition is part of the spec**: "2×16GB" is not the same as "1×32GB" for buyers optimizing \
dual-channel behavior. If the query specifies sticks count, treat it as a requirement.

- **Overclock profiles are platform-specific**: If the query references Intel XMP or AMD EXPO, treat it \
as a real compatibility signal. Do not assume a kit tuned for one platform is equally appropriate for the \
other when the query is explicit.

- **Speed units and naming**: Listings may mix MHz/MT/s marketing language. Treat requested speed (e.g., \
DDR5-6000) as a hard constraint when specified, especially for performance-oriented builds.
""",
        ),
        "storage_internal": VerticalOverlay(
            description=(
                "Internal storage drives: NVMe/SATA SSDs, M.2 2230/2242/2280/22110, 2.5-inch SSDs, 3.5-inch HDDs; includes NAS drives; NOT USB flash drives"
            ),
            content="""\
### Internal Storage (SSD / HDD) — Scoring Guidance

This query involves internal storage: SSDs and hard drives.

**Critical distinctions to enforce:**

- **NVMe vs SATA is a hard protocol distinction**: M.2 is a shape; SSDs can be SATA or NVMe. If the query \
says NVMe / PCIe, do not return SATA M.2 drives. If it says SATA, do not return NVMe-only products.

- **M.2 length is a physical fit constraint**: 2230/2242/2280/22110 indicate length variants. If the query \
specifies a size (common for handhelds, ultrabooks, and consoles), treat it as hard.

- **Drive role and interface**: 2.5-inch SATA SSDs, 3.5-inch HDDs, and M.2 sticks are not interchangeable \
without adapters/bays. Match form factor and interface implied by the query.

- **PCIe generation requests are real**: "Gen4" vs "Gen3" vs "Gen5" matters when specified—especially for \
platforms with minimum performance recommendations.

- **NAS / RAID nuance: SMR vs CMR**: If the query includes NAS, RAID, ZFS, or rebuild-heavy workloads, \
prefer drives marketed for those uses and avoid SMR models unless the query explicitly requests SMR. \
SMR can behave very differently under sustained random writes and rebuild scenarios.

- **Do not confuse internal drives with external enclosures**: If the query is for the SSD itself, \
USB enclosures, docks, and adapters are not substitutes unless the query asks for a bundle.
""",
        ),
        "external_storage": VerticalOverlay(
            description=(
                "External storage: portable SSDs/HDDs, external NVMe enclosures, USB4/Thunderbolt external drives; NOT internal bare drives unless requested"
            ),
            content="""\
### External Storage (Portable SSD/HDD, External Enclosures) — Scoring Guidance

This query involves storage meant to be used externally over USB/Thunderbolt.

**Critical distinctions to enforce:**

- **External drive vs internal drive + enclosure**: If the query is for a ready-made portable SSD/HDD, \
an internal bare drive is not a substitute unless the query explicitly asks for an enclosure build.

- **Interface speed and port type**: Treat explicit speed claims (USB 10Gbps/20Gbps, USB4 40Gbps, Thunderbolt) \
as hard requirements. Do not treat a USB 2.0/USB 3.x flash drive as equivalent to an NVMe-based portable SSD \
when the query implies high-speed transfers.

- **Thunderbolt vs USB-C**: If the query requests Thunderbolt storage, require explicit Thunderbolt support. \
A USB-C drive is not necessarily Thunderbolt-capable.

- **Capacity and security features**: If the query specifies hardware encryption, ruggedization (IP rating), \
or compatibility with a platform (Mac/Windows/console), enforce it.

- **Do not substitute small USB flash drives**: USB thumb drives are not substitutes for portable SSD/HDD \
intent unless the query explicitly asks for a USB flash drive.
""",
        ),
        "memory_cards_and_flash": VerticalOverlay(
            description=(
                "Removable storage cards and flash storage: SD/microSD (UHS-I/UHS-II, U3/V30/A2), CFexpress; USB flash drives; NOT internal SSDs"
            ),
            content="""\
### Memory Cards and Flash Storage — Scoring Guidance

This query involves removable flash storage where speed-class markings and form factor are the compatibility key.

**Critical distinctions to enforce:**

- **Form factor is non-negotiable**: SD vs microSD vs CFexpress/CFast are physically different. \
If the query specifies microSD, do not return full-size SD without an adapter, and vice versa.

- **SDHC / SDXC nuance**: If the query specifies SDHC vs SDXC (or capacity boundaries that imply them), \
enforce it; some hosts have constraints or require updates for SDXC.

- **Speed-class markings measure different things**: UHS Speed Class (U1/U3), Video Speed Class (V30/V60/V90), \
and Application Performance Class (A1/A2) are not interchangeable labels. Match the specific class requested.

- **Host-interface limitations**: A UHS-II card will work in a UHS-I host, but only at UHS-I speeds. \
If the query is about a device that only supports UHS-I (e.g., some consoles), do not up-score UHS-II \
as inherently more relevant unless the query explicitly seeks maximum transfer speed for off-device workflows.

- **USB flash drives vs memory cards**: Do not substitute USB flash drives for SD/microSD queries or vice versa \
unless an explicit adapter/bundle is requested.
""",
        ),
        "power_supplies": VerticalOverlay(
            description=(
                "PC power supplies (PSU): ATX/SFX, wattage, 80+ ratings, modular, PCIe 5.x 16-pin (12VHPWR/12V-2x6); NOT chargers/power bricks"
            ),
            content="""\
### Power Supplies (PSUs) — Scoring Guidance

This query involves a PC power supply unit.

**Critical distinctions to enforce:**

- **Form factor is a hard fit constraint**: ATX vs SFX vs SFX-L vs TFX/FlexATX are not interchangeable \
without case support. Treat form factor as hard when specified (especially for SFF builds).

- **Modern GPU power connectors**: If the query is for a PSU that supports a 16-pin GPU connector \
(12VHPWR / 12V-2x6, often marketed as PCIe 5.x / ATX 3.x), treat that as a hard requirement. \
A PSU without the required connector (or without enough wattage/rails) is a mismatch.

- **Wattage and headroom**: If the query states wattage (e.g., 850W) treat it as a hard minimum \
unless "around" or a range is clearly implied.

- **Modular cabling**: Fully modular vs semi-modular vs non-modular is a meaningful constraint in \
cable-management-sensitive builds; enforce it when specified.

- **Input voltage constraints**: Some PSUs are 200–240V only. If the query implies a specific market \
or explicitly requests 110V/US use, penalize voltage-limited units that would not work.

- **Do not substitute laptop power bricks**: Laptop AC adapters / USB-C chargers are not PSU alternatives.
""",
        ),
        "pc_cases_and_cooling": VerticalOverlay(
            description=(
                "PC cases, CPU coolers, AIO liquid coolers, case fans, thermal paste, and cooling accessories; NOT CPUs/GPUs themselves"
            ),
            content="""\
### PC Cases and Cooling — Scoring Guidance

This query involves PC enclosures or cooling hardware.

**Critical distinctions to enforce:**

- **Case compatibility is structural**: Motherboard size support (ATX/mATX/ITX), PSU size support (ATX/SFX), \
GPU length clearance, CPU cooler height, and radiator mount sizes are hard constraints when specified.

- **Socket mounting is non-negotiable for CPU coolers**: If the query specifies CPU socket (AM4/AM5/LGA 1700/...) \
or explicitly targets a cooler for a specific platform, do not return a cooler without the matching mounting \
hardware or confirmed compatibility.

- **AIO radiator size matters**: 120/240/280/360 mm radiators are not interchangeable. If the query requests a \
specific size, treat it as hard.

- **Fan size and connector type**: 120 mm vs 140 mm fan size and PWM (4-pin) vs DC (3-pin) can be hard \
requirements when specified, especially for noise/fit builds.

- **Do not confuse thermal paste/pads with coolers**: If the query is for a full cooler, thermal compounds \
alone are not substitutes. If the query is for paste/pads, coolers are overbroad and irrelevant.
""",
        ),
        "monitors": VerticalOverlay(
            description=(
                "Computer monitors (gaming monitors, ultrawide, OLED/IPS, high refresh, USB-C monitors); NOT TVs"
            ),
            content="""\
### Computer Monitors — Scoring Guidance

This query involves a computer monitor.

**Critical distinctions to enforce:**

- **Refresh rate and resolution are often hard requirements**: If the query specifies 240 Hz, 4K, 3440×1440, \
or ultrawide aspect ratio, treat it as hard. A 165 Hz panel is not a good match for an explicit 240 Hz query.

- **Port requirements can be functional gates**: If the query specifies DisplayPort version, HDMI 2.1 for \
4K120, or USB-C video, enforce it. Many monitors include USB-C ports that are data-only or do not provide \
sufficient USB Power Delivery for laptop charging.

- **USB-C monitor nuance**: A USB-C connector does not guarantee video output. If the query implies \
"single-cable laptop setup" (USB-C video + charging + USB hub), require explicit support for DisplayPort \
Alt Mode (or equivalent) and sufficient USB-C PD wattage.

- **HDR claims are not all equivalent**: If the query asks for VESA DisplayHDR tiers (e.g., DisplayHDR 600 or \
True Black), treat the certification tier as the requirement, not generic "HDR" marketing.

- **Adaptive sync compatibility**: If the query specifies G-SYNC (native/compatible) or FreeSync, treat \
that as a requirement; do not assume any monitor supports the requested VRR ecosystem.

- **Do not substitute TVs for monitors**: TVs are weaker matches for explicit "monitor" intent due to \
different ergonomics (pixel density, subpixel layouts, wake behavior) unless the query explicitly allows.
""",
        ),
        "tvs_and_projectors": VerticalOverlay(
            description=(
                "Televisions and projectors (OLED/QLED/LED TVs, 4K120 gaming TV, home theater projectors); NOT computer monitors unless asked"
            ),
            content="""\
### TVs and Projectors — Scoring Guidance

This query involves televisions or projectors.

**Critical distinctions to enforce:**

- **Display technology terms are not synonyms**: OLED is self-emissive; QLED is an LCD TV with a quantum-dot \
layer and backlight. Treat OLED vs QLED/LED as meaningful when specified.

- **HDMI feature requirements**: If the query includes 4K@120, VRR, eARC, or explicit HDMI versioning, enforce \
those capabilities. Many TVs only support high-bandwidth features on specific HDMI ports.

- **Cable-spec dependencies**: If the query is for an HDMI 2.1 / 2.2 high-bandwidth setup, treat certified \
cable classes (e.g., Ultra High Speed, Ultra96) as relevant. A generic "HDMI cable" is not necessarily a \
match for explicit bandwidth/certification requests.

- **Projector specs**: For projectors, stated brightness (ANSI lumens), throw ratio / "short throw", and \
native vs "supported" resolution matter. If the query specifies these, treat them as hard.

- **Smart TV platform constraints**: If the query requests a specific platform/ecosystem capability \
(e.g., "Apple AirPlay", "Google TV"), enforce it; do not assume "smart TV" is equivalent across platforms.

- **Do not substitute monitor listings**: A TV query should not return PC monitors unless the query explicitly \
asks for "TV as monitor" or similar.
""",
        ),
        "headphones_and_earbuds": VerticalOverlay(
            description=(
                "Headphones, earbuds, headsets (noise cancelling, Bluetooth, wired 3.5mm/USB-C/Lightning); NOT speakers/soundbars"
            ),
            content="""\
### Headphones, Earbuds, and Headsets — Scoring Guidance

This query involves personal audio worn on/in the ears.

**Critical distinctions to enforce:**

- **Headphones vs headset vs earbuds**: If the query requests a microphone ("headset", "gaming headset"), \
headphones without a mic are weaker matches unless the listing explicitly includes a detachable mic.

- **Wired connector type is a hard constraint when specified**: 3.5mm analog, USB-C digital, and Lightning \
headsets are not interchangeable without adapters. If the query specifies a connector, enforce it.

- **Wireless codec / platform features**: If the query specifies codec support (e.g., LDAC/aptX) or \
platform features (e.g., multipoint, low-latency mode), treat it as a requirement.

- **Noise cancellation vs isolation**: ANC (active noise cancellation) is not the same as passive isolation. \
If the query explicitly asks for ANC, do not treat non-ANC models as close substitutes.

- **Do not substitute speakers**: Soundbars and speakers are different product roles even if they are \
Bluetooth-enabled.
""",
        ),
        "home_audio": VerticalOverlay(
            description=(
                "Home audio, speakers, soundbars, AV receivers, subwoofers (home theater); NOT headphones"
            ),
            content="""\
### Home Audio and Home Theater — Scoring Guidance

This query involves speakers, soundbars, subwoofers, or AV receivers.

**Critical distinctions to enforce:**

- **Passive vs powered**: Passive speakers require an amplifier/AVR; powered speakers have built-in \
amplification. Do not substitute across these when the query is explicit (e.g., "passive bookshelf speakers").

- **Soundbar completeness**: If the query says "soundbar with subwoofer" or "surround kit", enforce inclusion \
of the required components (sub, rear speakers). A standalone bar is a weak match for an explicit bundle query.

- **TV audio return channel**: ARC vs eARC matters for modern setups. If the query explicitly says eARC, \
do not treat ARC-only products as equivalent.

- **Channel configuration**: 2.1 vs 5.1 vs 5.1.2 etc is a functional difference. Treat channel counts as \
hard when specified.

- **Do not substitute headphones**: Personal audio is not a substitute for room audio intent.
""",
        ),
        "networking": VerticalOverlay(
            description=(
                "Home and small-office networking: Wi-Fi routers, Wi-Fi 6E/7, mesh systems, modems/gateways, switches, access points"
            ),
            content="""\
### Networking (Wi-Fi, Mesh, Modems, Switches) — Scoring Guidance

This query involves networking gear.

**Critical distinctions to enforce:**

- **Wi-Fi generation and bands**: Wi-Fi 6 vs 6E vs 7 are meaningfully different. If the query specifies 6E, \
it implies 6 GHz support; if it specifies Wi-Fi 7, it implies 802.11be-class hardware. Treat these as hard \
when specified.

- **Router vs modem vs gateway**: A modem (DOCSIS/DSL/fiber ONT) is not a router. A router is not a modem. \
A "gateway" may include both. Enforce device role when the query is specific.

- **Mesh systems vs single routers**: If the query asks for a mesh system, prefer multi-node kits or \
explicitly mesh-capable routers; a single non-mesh router is a weak match unless the query is open-ended.

- **DOCSIS compatibility**: If the query requires DOCSIS 3.1 (common for gigabit cable plans), treat it as \
a hard requirement. Do not substitute DOCSIS 3.0 for an explicit 3.1 request.

- **Ethernet speed tiers**: 1GbE vs 2.5GbE vs 10GbE ports are hard constraints when specified. Do not treat \
a 1GbE-only switch as a match for an explicit 2.5GbE/10GbE request.

- **Do not confuse extenders with routers**: Range extenders, Wi-Fi adapters, and powerline kits are not \
routers/modems unless explicitly stated.
""",
        ),
        "smart_home": VerticalOverlay(
            description=(
                "Smart home devices and hubs: Matter, Thread, Zigbee, Z-Wave, HomeKit/Alexa/Google compatibility (lights, plugs, locks, sensors)"
            ),
            content="""\
### Smart Home Devices — Scoring Guidance

This query involves smart home devices, whose usefulness depends on ecosystem and radio protocol compatibility.

**Critical distinctions to enforce:**

- **Ecosystem claims are not interchangeable**: "Works with Alexa" does not imply HomeKit support, and \
vice versa. If the query names a platform (Apple Home/HomeKit, Google Home, Alexa, SmartThings), treat that \
as a hard requirement.

- **Matter is about interoperability, but not universal**: If the query specifies Matter, require explicit \
Matter support. If the query specifies Matter-over-Thread, require Thread capability and be mindful that \
Thread devices typically need a Thread Border Router / controller in the home.

- **Zigbee and Z-Wave are distinct radios**: Zigbee devices generally require a Zigbee coordinator/hub, and \
Z-Wave is its own mesh ecosystem. Do not treat Zigbee and Z-Wave products as substitutes unless the product \
is explicitly a multi-protocol hub/bridge.

- **Device role matters**: A "smart bulb" is not a "smart switch". A "hub" is not an endpoint. \
Enforce device category when the query is explicit.

- **Security device constraints**: For locks and security sensors, query-specified standards (e.g., \
"Thread lock", "HomeKey", "local control") should be treated as hard; cloud-only devices are weaker matches \
for explicit local-control intent.
""",
        ),
        "smartphones": VerticalOverlay(
            description=(
                "Mobile phones/smartphones (iPhone, Android), unlocked vs carrier, storage size, region variants; NOT cases/chargers"
            ),
            content="""\
### Smartphones — Scoring Guidance

This query involves a smartphone device.

**Critical distinctions to enforce:**

- **Unlocked vs carrier-locked is a hard gate**: If the query says "unlocked", do not treat carrier-locked \
models as substitutes. If the query specifies a carrier, do not substitute unlocked-only listings unless \
the carrier context allows it.

- **Exact model and variant match**: Pro/Pro Max/Plus/Ultra, storage tier (128/256/512/1TB), and model year \
are part of the identifier. Treat adjacent models as weaker matches unless explicit "any" language is used.

- **Region and band constraints**: If the query implies a specific region (US vs international) or band \
support, treat region-locked/incompatible variants as functional mismatches.

- **Port ecosystem**: If the query includes "USB-C iPhone" intent, be aware that iPhone 15 and later use USB-C. \
A Lightning-only accessory is not a correct match for an explicit USB-C-only request.

- **Do not substitute accessories**: Cases, screen protectors, chargers, and cables are not substitutes for \
the phone itself.
""",
        ),
        "device_specific_protection": VerticalOverlay(
            description=(
                "Device-specific protective accessories: phone/tablet cases, screen protectors, watch bands, camera cages; NOT the device itself"
            ),
            content="""\
### Cases, Screen Protectors, and Device-Specific Fit Accessories — Scoring Guidance

This query involves accessories where physical fit is the product.

**Critical distinctions to enforce:**

- **Exact device matching is mandatory**: Cases and protectors must match the exact model/size variant. \
"Pro" vs "Pro Max", "Ultra" vs non-Ultra, and year-to-year camera layout changes are frequent causes of \
returns. Penalize sibling/predecessor models heavily unless the listing explicitly states cross-compatibility.

- **MagSafe vs generic magnetic**: If the query says "MagSafe", require explicit MagSafe compatibility \
(not just any magnetic ring) and ensure the device supports that ecosystem.

- **Screen protector sizing**: "iPhone 16 Pro" and "iPhone 16 Pro Max" protectors are not interchangeable. \
If the query specifies privacy, anti-glare, or "tempered glass", treat it as a meaningful constraint.

- **Apple Watch band sizing groups**: Watch bands are compatible across certain case-size families. \
If the query specifies a case size or Ultra, prefer bands that explicitly support that size family; do not \
assume "universal Apple Watch band" fits all.

- **Do not substitute the device**: A case/protector query should not return the phone/tablet/watch itself.
""",
        ),
        "charging_cables_and_adapters": VerticalOverlay(
            description=(
                "Charging, cables, adapters, docks, hubs: USB-C/USB4/Thunderbolt, HDMI/DP, USB PD wattage, certified cables; NOT devices like laptops/phones"
            ),
            content="""\
### Charging, Cables, Adapters, Docks, and Hubs — Scoring Guidance

This query involves connectivity and power accessories where the spec is the function.

**Critical distinctions to enforce:**

- **USB-C is a connector, not a capability**: A USB-C port or cable may support only USB 2.0 data, or may \
lack video output, or may not support high-wattage charging. If the query specifies speed (5/10/20/40 Gbps), \
video, or PD wattage, enforce it.

- **USB 3.2 naming is confusing—use the speed**: If the query specifies "USB 10Gbps" / "20Gbps", treat that \
as the real requirement, and penalize listings that only provide USB 2.0 (480 Mbps) or lower speeds.

- **USB Power Delivery EPR (240W) requires the right cable class**: If the query requests 140W/180W/240W \
charging (USB-C PD 3.1/EPR), require an E-Marked/EPR-capable cable explicitly rated for the wattage. \
Do not treat generic USB-C cables as acceptable.

- **Thunderbolt vs USB-C hub**: If the query requests Thunderbolt (TB3/TB4/TB5), require explicit \
Thunderbolt certification/support. A USB-C hub is not a substitute just because the plug fits.

- **Display adapters depend on alternate modes**: USB-C to HDMI/DP requires the host device to support \
DisplayPort Alt Mode (or equivalent). If the query is about connecting a laptop/phone to an external display, \
prefer products that explicitly state DP Alt Mode compatibility.

- **HDMI cable certification levels matter**: If the query requests high-bandwidth HDMI (4K120, 8K, HDMI 2.1/2.2), \
prefer certified cable classes (e.g., Ultra High Speed, Ultra96) and penalize older "High Speed" cables.

- **Do not return devices**: For cable/dock queries, do not return laptops, monitors, or TVs.
""",
        ),
        "cameras_and_kits": VerticalOverlay(
            description=(
                "Cameras and camera kits (mirrorless, DSLR, point-and-shoot, action cams, camcorders) including body-only vs kit intent; NOT lenses-alone queries"
            ),
            content="""\
### Cameras and Camera Kits — Scoring Guidance

This query is about camera bodies or camera bundles/kits.

**Critical distinctions to enforce:**

- **Body-only vs kit**: If the query says "body only", do not treat lens kits as equivalent (and vice versa). \
Bundle completeness is part of the buyer intent.

- **Camera type matters**: "Mirrorless", "DSLR", "camcorder", and "action camera" are different product roles. \
Do not substitute across them unless the query is broad/ambiguous.

- **Sensor format is a meaningful constraint when stated**: Full-frame vs APS-C vs Micro Four Thirds affects \
lens compatibility and field-of-view. When the query specifies sensor size, enforce it.

- **Do not substitute lenses**: A camera-body query should not return lenses as primary results.
""",
        ),
        "camera_lenses": VerticalOverlay(
            description=(
                "Interchangeable camera lenses and lens adapters (Canon EF/RF, Nikon F/Z, Sony E/FE, Micro Four Thirds); NOT camera bodies"
            ),
            content="""\
### Camera Lenses and Lens Adapters — Scoring Guidance

This query involves a lens (or a lens adapter), where mount compatibility is the primary hard gate.

**Critical distinctions to enforce:**

- **Lens mount matching is mandatory**: A lens must match the camera mount (or explicitly include the correct \
adapter). EF/EF-S vs RF, Nikon F vs Z, Sony E/FE, and Micro Four Thirds are distinct mounts.

- **Adapter specificity**: If the query is for adapting a legacy mount to a new mount, the correct adapter \
name/class is the product. Do not return unrelated adapters with the same physical connector idea.

- **FE vs E nuance (Sony)**: Full-frame FE lenses can be used on APS-C E-mount bodies (with crop), but APS-C \
lenses on full-frame bodies can force crop mode or vignette. If the query is explicit about full-frame \
coverage, enforce it.

- **Focal length / zoom range**: If the query specifies a focal length (e.g., 50mm) or a zoom range, \
treat it as a hard requirement. Do not substitute "close" focal lengths unless the query is clearly broad.

- **Do not substitute camera bodies**: A lens query should not return camera bodies or lens caps/filters \
as the main results.
""",
        ),
        "printers_and_scanners": VerticalOverlay(
            description=(
                "Printers and scanners (inkjet vs laser, all-in-one MFP, duplex, Wi-Fi/Ethernet); NOT ink/toner consumables"
            ),
            content="""\
### Printers and Scanners — Scoring Guidance

This query involves a printer/scanner device.

**Critical distinctions to enforce:**

- **Inkjet vs laser is a category boundary**: If the query specifies laser/toner, do not substitute inkjet. \
If it specifies inkjet/photo printing, do not substitute monochrome laser devices.

- **Functionality constraints**: "All-in-one" (print/scan/copy) vs print-only, color vs monochrome, and \
duplex requirements should be treated as hard when specified.

- **Connectivity**: If the query specifies Wi-Fi, Ethernet, or specific mobile-printing ecosystems, enforce it. \
Many devices have near-identical model names with different connectivity SKUs.

- **Do not substitute consumables**: Ink/toner/drum units are not substitutes for the printer.
""",
        ),
        "printer_ink_and_toner": VerticalOverlay(
            description=(
                "Printer consumables: ink cartridges, toner cartridges, drum units, maintenance kits; includes XL/high-yield; NOT printers"
            ),
            content="""\
### Printer Ink, Toner, and Consumables — Scoring Guidance

This query involves printer consumables where the model number is the compatibility key.

**Critical distinctions to enforce:**

- **Exact cartridge model numbers dominate**: Treat cartridge identifiers (e.g., HP 63 vs 65, TN vs DR series) \
as hard gates. Similar-looking numbers are often incompatible.

- **Standard vs high-yield (XL) nuance**: "XL"/high-yield variants are typically compatible with the same \
printers as the standard cartridge but have different yields/costs. If the query explicitly requests XL, \
do not substitute standard yield and vice versa.

- **Toner vs drum are different parts**: For many laser printers, the toner cartridge and the drum/imaging \
unit are separate consumables. If the query requests a drum unit, do not return toner cartridges, and vice versa.

- **Region/firmware constraints**: If the query mentions region-coded cartridges or "genuine/OEM only", treat \
that as a meaningful hard requirement—compatibles may be rejected by firmware or policy.
""",
        ),
        "gaming_consoles": VerticalOverlay(
            description=(
                "Game consoles and console accessories: PS5/Xbox/Nintendo Switch, controllers, docks, storage expansions, game bundles"
            ),
            content="""\
### Gaming Consoles and Accessories — Scoring Guidance

This query involves gaming consoles and console-specific accessories.

**Critical distinctions to enforce:**

- **Console generation matters**: PS4 vs PS5, Xbox One vs Xbox Series X|S, and Switch model variants have \
non-interchangeable accessories. Treat generation as a hard identifier when specified.

- **Storage expansion is platform-specific**:
  * **PS5 internal expansion** requires a PCIe Gen4x4 M.2 NVMe SSD (Key M) and has strict physical size limits \
and performance recommendations.
  * **Nintendo Switch storage** uses microSD cards—if the query specifies UHS-I guidance, enforce it.
  * **Xbox Series X|S optimized-game storage** is different from generic USB external drives; platform-specific \
expansion solutions may be required for play-from-storage intent.

- **Accessory role disambiguation**: "Controller" vs "charging dock" vs "console stand" vs "console" are \
distinct. Do not invert product roles.

- **Bundle completeness**: If the query requests a console bundle (console + game + controller), a single \
component is a weak match unless the query explicitly allows piecemeal items.
""",
        ),
        "vr_headsets": VerticalOverlay(
            description=(
                "VR headsets and VR accessory kits (PC VR, standalone VR, base stations, controllers); includes Meta Quest Link cables and SteamVR tracking"
            ),
            content="""\
### VR Headsets and VR Accessories — Scoring Guidance

This query involves virtual reality hardware, where platform and connection requirements are frequent failure modes.

**Critical distinctions to enforce:**

- **Standalone vs PC-tethered VR**: If the query specifies PC VR / SteamVR / "requires DisplayPort", \
do not substitute standalone-only headsets unless the listing explicitly supports PC connection. \
If the query specifies standalone usage, do not require a PC.

- **Connection requirements**: Many PC VR headsets require DisplayPort plus USB (and power). If the query \
is about connecting to a PC, enforce the required ports/cables and do not treat "USB-C only" as \
automatically sufficient.

- **Tracking ecosystem**: SteamVR base-station tracking is different from inside-out tracking. If the query \
mentions base stations, Lighthouse/SteamVR tracking, or specific controller families, enforce that ecosystem. \
Base stations are not relevant for inside-out-only systems unless explicitly supported.

- **Do not confuse VR “link” cables with charging cables**: PC-link cables typically require USB 3.x data \
rates; a USB-C cable that is "charging-only" or USB 2.0 is not a substitute when high-speed data is required.

- **Do not substitute games or software**: A hardware headset query should not return VR games/apps as primary results.
""",
        ),
    },
)
