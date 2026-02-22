"""Electronics vertical context for LLM judge guidance."""

from veritail.prompts import load_prompt
from veritail.types import VerticalContext, VerticalOverlay

ELECTRONICS = VerticalContext(
    core=load_prompt("verticals/electronics/core.md"),
    overlays={
        "gaming_desktop_pcs": VerticalOverlay(
            description=(
                "Prebuilt / assembled gaming desktop PCs and towers (NOT individual PC "
                "parts); queries listing CPU+RAM+storage+GPU desktop specs"
            ),
            content=load_prompt("verticals/electronics/overlays/gaming_desktop_pcs.md"),
        ),
        "office_desktops_workstations_aio_mini": VerticalOverlay(
            description=(
                "Non-gaming desktops: office desktops, mini PCs, workstations, "
                "all-in-one PCs (AIO) (NOT monitors alone, NOT laptop computers)"
            ),
            content=load_prompt(
                "verticals/electronics/overlays/office_desktops_workstations_aio_mini.md"
            ),
        ),
        "gaming_laptops": VerticalOverlay(
            description=(
                "Gaming laptops / gaming notebooks (RTX/GTX gaming laptop, high "
                "refresh screens, 'H/HX' CPUs); NOT desktops or components"
            ),
            content=load_prompt("verticals/electronics/overlays/gaming_laptops.md"),
        ),
        "productivity_laptops_ultrabooks": VerticalOverlay(
            description=(
                "Non-gaming laptops: ultrabooks, business laptops, student laptops, "
                "2-in-1s, Chromebooks, thin-and-light; NOT gaming-centric laptops "
                "unless requested"
            ),
            content=load_prompt(
                "verticals/electronics/overlays/productivity_laptops_ultrabooks.md"
            ),
        ),
        "macbooks": VerticalOverlay(
            description=(
                "Apple MacBook laptops (MacBook Air, MacBook Pro; Apple Silicon "
                "M-series; macOS); NOT generic Windows laptops"
            ),
            content=load_prompt("verticals/electronics/overlays/macbooks.md"),
        ),
        "tablets_and_ereaders": VerticalOverlay(
            description=(
                "Tablets and e-readers (iPad, Android tablets, Kindle/Kobo), Wi-Fi vs "
                "cellular, storage tier; NOT laptop computers"
            ),
            content=load_prompt(
                "verticals/electronics/overlays/tablets_and_ereaders.md"
            ),
        ),
        "wearables": VerticalOverlay(
            description=(
                "Wearables: smartwatches, fitness trackers, smart rings; includes GPS "
                "vs cellular watch variants; NOT phones/tablets"
            ),
            content=load_prompt("verticals/electronics/overlays/wearables.md"),
        ),
        "pc_cpus": VerticalOverlay(
            description=(
                "Desktop computer processors/CPUs (Intel Core/Core Ultra, AMD Ryzen, "
                "Threadripper); queries with socket/chipset, 'CPU only', "
                "cores/threads; NOT complete PCs"
            ),
            content=load_prompt("verticals/electronics/overlays/pc_cpus.md"),
        ),
        "pc_gpus": VerticalOverlay(
            description=(
                "Graphics cards / GPUs / video cards (RTX/Radeon/Arc; workstation "
                "GPUs; AIB cards); NOT gaming PCs or laptops"
            ),
            content=load_prompt("verticals/electronics/overlays/pc_gpus.md"),
        ),
        "motherboards": VerticalOverlay(
            description=(
                "PC motherboards (Intel/AMD sockets, chipsets, ATX/mATX/ITX, "
                "DDR4/DDR5); NOT CPUs or RAM kits alone"
            ),
            content=load_prompt("verticals/electronics/overlays/motherboards.md"),
        ),
        "memory_ram": VerticalOverlay(
            description=(
                "Computer memory (RAM): DDR4/DDR5 DIMM & SO-DIMM kits, "
                "capacity/speed/timings, ECC vs non-ECC; NOT storage drives"
            ),
            content=load_prompt("verticals/electronics/overlays/memory_ram.md"),
        ),
        "storage_internal": VerticalOverlay(
            description=(
                "Internal storage drives: NVMe/SATA SSDs, M.2 2230/2242/2280/22110, "
                "2.5-inch SSDs, 3.5-inch HDDs; includes NAS drives; NOT USB flash "
                "drives"
            ),
            content=load_prompt("verticals/electronics/overlays/storage_internal.md"),
        ),
        "external_storage": VerticalOverlay(
            description=(
                "External storage: portable SSDs/HDDs, external NVMe enclosures, "
                "USB4/Thunderbolt external drives; NOT internal bare drives unless "
                "requested"
            ),
            content=load_prompt("verticals/electronics/overlays/external_storage.md"),
        ),
        "memory_cards_and_flash": VerticalOverlay(
            description=(
                "Removable storage cards and flash storage: SD/microSD (UHS-I/UHS-II, "
                "U3/V30/A2), CFexpress; USB flash drives; NOT internal SSDs"
            ),
            content=load_prompt(
                "verticals/electronics/overlays/memory_cards_and_flash.md"
            ),
        ),
        "power_supplies": VerticalOverlay(
            description=(
                "PC power supplies (PSU): ATX/SFX, wattage, 80+ ratings, modular, PCIe "
                "5.x 16-pin (12VHPWR/12V-2x6); NOT chargers/power bricks"
            ),
            content=load_prompt("verticals/electronics/overlays/power_supplies.md"),
        ),
        "pc_cases_and_cooling": VerticalOverlay(
            description=(
                "PC cases, CPU coolers, AIO liquid coolers, case fans, thermal paste, "
                "and cooling accessories; NOT CPUs/GPUs themselves"
            ),
            content=load_prompt(
                "verticals/electronics/overlays/pc_cases_and_cooling.md"
            ),
        ),
        "monitors": VerticalOverlay(
            description=(
                "Computer monitors (gaming monitors, ultrawide, OLED/IPS, high "
                "refresh, USB-C monitors); NOT TVs"
            ),
            content=load_prompt("verticals/electronics/overlays/monitors.md"),
        ),
        "tvs_and_projectors": VerticalOverlay(
            description=(
                "Televisions and projectors (OLED/QLED/LED TVs, 4K120 gaming TV, home "
                "theater projectors); NOT computer monitors unless asked"
            ),
            content=load_prompt("verticals/electronics/overlays/tvs_and_projectors.md"),
        ),
        "headphones_and_earbuds": VerticalOverlay(
            description=(
                "Headphones, earbuds, headsets (noise cancelling, Bluetooth, wired "
                "3.5mm/USB-C/Lightning); NOT speakers/soundbars"
            ),
            content=load_prompt(
                "verticals/electronics/overlays/headphones_and_earbuds.md"
            ),
        ),
        "home_audio": VerticalOverlay(
            description=(
                "Home audio, speakers, soundbars, AV receivers, subwoofers (home "
                "theater); NOT headphones"
            ),
            content=load_prompt("verticals/electronics/overlays/home_audio.md"),
        ),
        "networking": VerticalOverlay(
            description=(
                "Home and small-office networking: Wi-Fi routers, Wi-Fi 6E/7, mesh "
                "systems, modems/gateways, switches, access points"
            ),
            content=load_prompt("verticals/electronics/overlays/networking.md"),
        ),
        "smart_home": VerticalOverlay(
            description=(
                "Smart home devices and hubs: Matter, Thread, Zigbee, Z-Wave, "
                "HomeKit/Alexa/Google compatibility (lights, plugs, locks, sensors)"
            ),
            content=load_prompt("verticals/electronics/overlays/smart_home.md"),
        ),
        "smartphones": VerticalOverlay(
            description=(
                "Mobile phones/smartphones (iPhone, Android), unlocked vs carrier, "
                "storage size, region variants; NOT cases/chargers"
            ),
            content=load_prompt("verticals/electronics/overlays/smartphones.md"),
        ),
        "device_specific_protection": VerticalOverlay(
            description=(
                "Device-specific protective accessories: phone/tablet cases, screen "
                "protectors, watch bands, camera cages; NOT the device itself"
            ),
            content=load_prompt(
                "verticals/electronics/overlays/device_specific_protection.md"
            ),
        ),
        "charging_cables_and_adapters": VerticalOverlay(
            description=(
                "Charging, cables, adapters, docks, hubs: USB-C/USB4/Thunderbolt, "
                "HDMI/DP, USB PD wattage, certified cables; NOT devices like "
                "laptops/phones"
            ),
            content=load_prompt(
                "verticals/electronics/overlays/charging_cables_and_adapters.md"
            ),
        ),
        "cameras_and_kits": VerticalOverlay(
            description=(
                "Cameras and camera kits (mirrorless, DSLR, point-and-shoot, action "
                "cams, camcorders) including body-only vs kit intent; NOT lenses-alone "
                "queries"
            ),
            content=load_prompt("verticals/electronics/overlays/cameras_and_kits.md"),
        ),
        "camera_lenses": VerticalOverlay(
            description=(
                "Interchangeable camera lenses and lens adapters (Canon EF/RF, Nikon "
                "F/Z, Sony E/FE, Micro Four Thirds); NOT camera bodies"
            ),
            content=load_prompt("verticals/electronics/overlays/camera_lenses.md"),
        ),
        "printers_and_scanners": VerticalOverlay(
            description=(
                "Printers and scanners (inkjet vs laser, all-in-one MFP, duplex, "
                "Wi-Fi/Ethernet); NOT ink/toner consumables"
            ),
            content=load_prompt(
                "verticals/electronics/overlays/printers_and_scanners.md"
            ),
        ),
        "printer_ink_and_toner": VerticalOverlay(
            description=(
                "Printer consumables: ink cartridges, toner cartridges, drum units, "
                "maintenance kits; includes XL/high-yield; NOT printers"
            ),
            content=load_prompt(
                "verticals/electronics/overlays/printer_ink_and_toner.md"
            ),
        ),
        "gaming_consoles": VerticalOverlay(
            description=(
                "Game consoles and console accessories: PS5/Xbox/Nintendo Switch, "
                "controllers, docks, storage expansions, game bundles"
            ),
            content=load_prompt("verticals/electronics/overlays/gaming_consoles.md"),
        ),
        "vr_headsets": VerticalOverlay(
            description=(
                "VR headsets and VR accessory kits (PC VR, standalone VR, base "
                "stations, controllers); includes Meta Quest Link cables and SteamVR "
                "tracking"
            ),
            content=load_prompt("verticals/electronics/overlays/vr_headsets.md"),
        ),
    },
)
