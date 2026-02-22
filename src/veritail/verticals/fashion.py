"""Fashion vertical context for LLM judge guidance."""

from veritail.prompts import load_prompt
from veritail.types import VerticalContext, VerticalOverlay

FASHION = VerticalContext(
    core=load_prompt("verticals/fashion/core.md"),
    overlays={
        "sneakers_athletic_shoes": VerticalOverlay(
            description=(
                "Sneakers, trainers, and athletic shoes (running, walking, training, "
                "basketball, tennis, skate, trail). Includes shoe sizing scales "
                "(men/women/kids) and widths."
            ),
            content=load_prompt(
                "verticals/fashion/overlays/sneakers_athletic_shoes.md"
            ),
        ),
        "boots": VerticalOverlay(
            description=(
                "Boots (ankle, chelsea, combat, hiking, work, rain, snow, knee-high, "
                "over-the-knee). Covers shaft height, calf width, and weatherproofing "
                "terms."
            ),
            content=load_prompt("verticals/fashion/overlays/boots.md"),
        ),
        "sandals_slides": VerticalOverlay(
            description=(
                "Sandals and slides (flip-flops/thongs, slides, strappy sandals, "
                "wedges, espadrilles, open-back mules). Warm-weather open footwear."
            ),
            content=load_prompt("verticals/fashion/overlays/sandals_slides.md"),
        ),
        "heels_and_dress_shoes": VerticalOverlay(
            description=(
                "Dress shoes and heels (pumps, stilettos, platforms, flats like "
                "ballet/Mary Jane, loafers, oxfords/derbies). Heel height and toe "
                "shape matter."
            ),
            content=load_prompt("verticals/fashion/overlays/heels_and_dress_shoes.md"),
        ),
        "denim_jeans": VerticalOverlay(
            description=(
                "Denim and jeans (raw/dry denim, selvedge, stretch, washes; "
                "skinny/straight/bootcut/wide-leg). Often uses waist×inseam sizing."
            ),
            content=load_prompt("verticals/fashion/overlays/denim_jeans.md"),
        ),
        "intimates_bras_lingerie": VerticalOverlay(
            description=(
                "Intimates: bras, underwear, lingerie sets, shapewear. Band+cup "
                "sizing, international size-system differences, and support features."
            ),
            content=load_prompt(
                "verticals/fashion/overlays/intimates_bras_lingerie.md"
            ),
        ),
        "activewear_athleisure": VerticalOverlay(
            description=(
                "Activewear/athleisure (leggings, yoga/gym/running gear, sports bras, "
                "performance layers). Performance claims like moisture-wicking and "
                "support levels."
            ),
            content=load_prompt("verticals/fashion/overlays/activewear_athleisure.md"),
        ),
        "outerwear_rain_down": VerticalOverlay(
            description=(
                "Outerwear for weather and warmth (coats, puffers, parkas, rain "
                "jackets, shells). Waterproof vs water-resistant, down fill power, and "
                "3-in-1 systems."
            ),
            content=load_prompt("verticals/fashion/overlays/outerwear_rain_down.md"),
        ),
        "tailored_menswear": VerticalOverlay(
            description=(
                "Tailored menswear and formalwear (suits, blazers, tuxedos, dress "
                "shirts, dress trousers). 40R sizing, drop, and dress-code terminology."
            ),
            content=load_prompt("verticals/fashion/overlays/tailored_menswear.md"),
        ),
        "swimwear_upf": VerticalOverlay(
            description=(
                "Swimwear and sun-protective swim apparel (bikinis, one-pieces, "
                "tankinis, swim trunks, boardshorts, rash guards). UPF terms and "
                "coverage intent."
            ),
            content=load_prompt("verticals/fashion/overlays/swimwear_upf.md"),
        ),
        "kids_baby_apparel": VerticalOverlay(
            description=(
                "Kids and baby apparel sizing (preemie/NB/3M-24M, 2T-5T, kids 6X, "
                "youth ranges/XS-XL; regular/slim/husky/plus)."
            ),
            content=load_prompt("verticals/fashion/overlays/kids_baby_apparel.md"),
        ),
        "jewelry_precious_metals": VerticalOverlay(
            description=(
                "Jewelry (rings, necklaces, bracelets, earrings, watches). "
                "Metal/purity/plating terms (karat vs carat, vermeil, gold-filled) and "
                "size constraints."
            ),
            content=load_prompt(
                "verticals/fashion/overlays/jewelry_precious_metals.md"
            ),
        ),
        "resale_vintage": VerticalOverlay(
            description=(
                "Resale/vintage/pre-owned: condition grading and acronyms "
                "(NWT/NWOT/EUC), vintage vs retro, and 'deadstock/DS' terminology."
            ),
            content=load_prompt("verticals/fashion/overlays/resale_vintage.md"),
        ),
    },
)
