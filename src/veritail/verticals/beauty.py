"""Beauty vertical context for LLM judge guidance."""

from veritail.prompts import load_prompt
from veritail.types import VerticalContext, VerticalOverlay

BEAUTY = VerticalContext(
    core=load_prompt("verticals/beauty/core.md"),
    overlays={
        "complexion_makeup": VerticalOverlay(
            description=(
                "Complexion/base makeup: foundation, concealer, skin tint, tinted "
                "moisturizer, BB/CC cream, powder (setting or foundation), primer, "
                "setting spray; includes shade/undertone matching."
            ),
            content=load_prompt("verticals/beauty/overlays/complexion_makeup.md"),
        ),
        "eye_makeup": VerticalOverlay(
            description=(
                "Eye makeup & brows: mascara (including tubing), eyeliner "
                "(kohl/kajal), eyeshadow, false lashes, lash glue, brow pencils/gels, "
                "brow lamination."
            ),
            content=load_prompt("verticals/beauty/overlays/eye_makeup.md"),
        ),
        "lip_products": VerticalOverlay(
            description=(
                "Lip products: lipstick (bullet or liquid), lip stain/tint, gloss, lip "
                "oil, balm, lip mask, lip liner; includes finish and long-wear claims."
            ),
            content=load_prompt("verticals/beauty/overlays/lip_products.md"),
        ),
        "cheek_color_contour": VerticalOverlay(
            description=(
                "Cheek makeup: blush, bronzer, contour, highlighter, illuminating "
                "drops; cream vs powder and undertone/finish are important."
            ),
            content=load_prompt("verticals/beauty/overlays/cheek_color_contour.md"),
        ),
        "makeup_tools": VerticalOverlay(
            description=(
                "Makeup tools & brushes: face/eye brushes, sponges, applicators, brush "
                "sets, brush cleaner, lash curler, sharpeners, makeup organizers."
            ),
            content=load_prompt("verticals/beauty/overlays/makeup_tools.md"),
        ),
        "cleansers_makeup_removal": VerticalOverlay(
            description=(
                "Facial cleansers & makeup removal: cleansing oil, cleansing balm, "
                "micellar water, makeup remover, face wash (gel/foam/cream), double "
                "cleansing (first cleanser vs second cleanser)."
            ),
            content=load_prompt(
                "verticals/beauty/overlays/cleansers_makeup_removal.md"
            ),
        ),
        "exfoliants_peels": VerticalOverlay(
            description=(
                "Exfoliants & peels: physical scrubs, chemical exfoliants "
                "(AHA/BHA/PHA), enzyme exfoliants, peel pads, at-home peels, body "
                "exfoliators."
            ),
            content=load_prompt("verticals/beauty/overlays/exfoliants_peels.md"),
        ),
        "acne_and_breakouts": VerticalOverlay(
            description=(
                "Acne & breakouts: benzoyl peroxide, salicylic acid (BHA), adapalene, "
                "azelaic acid, acne cleansers, spot treatments, pimple patches "
                "(hydrocolloid), blackhead/whitehead treatments."
            ),
            content=load_prompt("verticals/beauty/overlays/acne_and_breakouts.md"),
        ),
        "retinoids_antiaging": VerticalOverlay(
            description=(
                "Retinoids & anti-aging: retinol, retinal/retinaldehyde, retinyl "
                "esters, tretinoin (Rx), adapalene, anti-wrinkle serums/creams; "
                "includes pregnancy-safe exclusions."
            ),
            content=load_prompt("verticals/beauty/overlays/retinoids_antiaging.md"),
        ),
        "brightening_dark_spots": VerticalOverlay(
            description=(
                "Dark spots & brightening: vitamin C (L-ascorbic acid and "
                "derivatives), niacinamide, tranexamic acid, kojic acid, arbutin, "
                "hyperpigmentation serums, melasma care; excludes hydroquinone unless "
                "explicitly requested."
            ),
            content=load_prompt("verticals/beauty/overlays/brightening_dark_spots.md"),
        ),
        "hydration_barrier_repair": VerticalOverlay(
            description=(
                "Hydration & barrier repair: hyaluronic acid (HA), glycerin, "
                "ceramides, barrier creams, moisturizers for sensitized/irritated "
                "skin; occlusive vs lightweight textures matter."
            ),
            content=load_prompt(
                "verticals/beauty/overlays/hydration_barrier_repair.md"
            ),
        ),
        "masks_and_treatments": VerticalOverlay(
            description=(
                "Masks & treatments: sheet masks, clay/mud masks, wash-off masks, "
                "sleeping masks/overnight masks, peel-off masks, targeted treatment "
                "masks."
            ),
            content=load_prompt("verticals/beauty/overlays/masks_and_treatments.md"),
        ),
        "sunscreen_spf": VerticalOverlay(
            description=(
                "Sunscreen & SPF: facial/body sunscreen, mineral vs chemical, "
                "broad-spectrum, water-resistant 40/80 minutes, sun sticks, tinted "
                "sunscreen, PA/UVA logos."
            ),
            content=load_prompt("verticals/beauty/overlays/sunscreen_spf.md"),
        ),
        "sunless_tanning": VerticalOverlay(
            description=(
                "Sunless tanning & bronzing: self-tanner with DHA, tanning drops, "
                "gradual tanner, express mousse, spray tan solutions, bronzers vs "
                "self-tanners; NOT sunscreen."
            ),
            content=load_prompt("verticals/beauty/overlays/sunless_tanning.md"),
        ),
        "shampoo_conditioner": VerticalOverlay(
            description=(
                "Hair cleansing & conditioning: shampoo, conditioner, co-wash, "
                "clarifying shampoo, dry shampoo, purple shampoo/toning shampoo, "
                "anti-dandruff shampoo, color-safe."
            ),
            content=load_prompt("verticals/beauty/overlays/shampoo_conditioner.md"),
        ),
        "textured_curl_hair": VerticalOverlay(
            description=(
                "Textured hair & curls: wavy/curly/coily (2A–4C), Curly Girl Method "
                "(CGM), curl creams, gels, leave-ins, porosity, protein sensitivity, "
                "protective styling."
            ),
            content=load_prompt("verticals/beauty/overlays/textured_curl_hair.md"),
        ),
        "hair_color_toning": VerticalOverlay(
            description=(
                "Hair color & toning: permanent/demi/semi dye, bleach/lightener, "
                "toner, gloss, developer volumes (10/20/30/40), root touch-up, "
                "color-depositing masks."
            ),
            content=load_prompt("verticals/beauty/overlays/hair_color_toning.md"),
        ),
        "hair_styling_and_tools": VerticalOverlay(
            description=(
                "Hair styling & tools: heat protectants, blow dryers, flat irons, "
                "curling wands, brushes/combs, styling creams, gels, mousses, pomades, "
                "wax, hairspray, texturizers."
            ),
            content=load_prompt("verticals/beauty/overlays/hair_styling_and_tools.md"),
        ),
        "fragrance": VerticalOverlay(
            description=(
                "Fragrance: perfume/parfum, extrait, eau de parfum (EDP), eau de "
                "toilette (EDT), cologne, body mist, rollerball, fragrance oil, "
                "discovery sets, flankers."
            ),
            content=load_prompt("verticals/beauty/overlays/fragrance.md"),
        ),
        "nails": VerticalOverlay(
            description=(
                "Nails: regular nail lacquer, gel polish (UV/LED cure), dip powder, "
                "acrylic, press-on nails, nail shapes "
                "(almond/coffin/stiletto/squoval), base/top coats."
            ),
            content=load_prompt("verticals/beauty/overlays/nails.md"),
        ),
        "body_care_personal": VerticalOverlay(
            description=(
                "Body & personal care: body wash, body scrub, body lotion/oil, body "
                "acne care, deodorant and antiperspirant, hand/foot care, hair "
                "removal, oral care."
            ),
            content=load_prompt("verticals/beauty/overlays/body_care_personal.md"),
        ),
        "gift_sets_kits": VerticalOverlay(
            description=(
                "Gifts, value sets & kits: skincare sets, makeup sets, hair sets, "
                "fragrance gift sets, discovery sets, minis/travel bundles, duos/trios."
            ),
            content=load_prompt("verticals/beauty/overlays/gift_sets_kits.md"),
        ),
    },
)
