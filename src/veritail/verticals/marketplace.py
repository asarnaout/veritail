"""Marketplace vertical context for LLM judge guidance."""

from veritail.types import VerticalContext, VerticalOverlay

MARKETPLACE = VerticalContext(
    core="""\
## Vertical: Marketplace

You are evaluating search results for a multi-seller marketplace platform (similar to \
Amazon, eBay, Walmart Marketplace, Etsy, or Mercari). Think like a marketplace search \
quality analyst who understands that buyers on these platforms face unique challenges: \
multiple sellers competing on the same product, wide variation in item condition and \
price, differing fulfillment reliability, and authenticity concerns that do not exist \
on single-retailer sites. Your goal is to judge whether a result genuinely satisfies \
the buyer's intent given the full marketplace context — not just whether the product \
category matches.

### Scoring considerations

- **Offer-level relevance, not just product-level**: On a marketplace, two listings for \
the identical SKU can have vastly different relevance due to price, condition, seller \
reputation, and fulfillment method. Evaluate the complete offer — product match alone \
is necessary but not sufficient. A correct product from a seller with a 60% feedback \
rating, no return policy, and 3-week shipping is a weaker match than the same product \
from a top-rated seller with Prime/next-day fulfillment.
- **Condition alignment with query intent**: If the query specifies or implies a \
condition (new, refurbished, used, certified pre-owned, for parts), mismatched \
condition is a significant relevance penalty. When no condition is specified, default \
to new-condition intent for commodity and current-generation products, but recognize \
that categories like collectibles, vintage goods, books, and out-of-production items \
carry a natural used/pre-owned expectation. Refurbished listings can be relevant for \
electronics and appliance queries even without explicit mention, but the refurbishment \
source (manufacturer vs third-party) and warranty coverage affect relevance strength.
- **Price competitiveness and total landed cost**: Evaluate price relative to the \
market norm for the product, not in isolation. A listing priced 40%+ above typical \
market value is a weaker match even if the product is correct — marketplace buyers \
comparison-shop and unreasonable pricing signals a gray-market, low-trust, or \
predatory listing. Always consider total landed cost: a lower item price with high \
shipping fees or no free-shipping option may be less relevant than a slightly higher \
price with free shipping, because marketplace buyers weigh total out-of-pocket cost \
and increasingly expect shipping-inclusive pricing.
- **Seller trust and fulfillment signals**: Seller reputation (feedback score, \
percentage positive, detailed seller ratings) and fulfillment method are material \
relevance signals on marketplaces. Marketplace-fulfilled listings (FBA, WFS, or \
platform-managed) carry implicit trust advantages — faster shipping guarantees, \
easier returns, and platform-backed buyer protection. Merchant-fulfilled listings from \
high-rated, established sellers can be equally relevant, but merchant-fulfilled \
listings from new or low-rated sellers should be considered weaker matches, especially \
for high-value items where buyer risk is elevated.
- **Authenticity and brand-authorization risk**: For branded products — especially in \
categories prone to counterfeiting (electronics, luxury goods, cosmetics, branded \
apparel, health supplements) — seller authorization and authenticity signals are \
relevance factors. Listings from brand-authorized or brand-owned storefronts are \
stronger matches than identical products from unknown third-party sellers at \
suspiciously low prices. Deep discounts (40%+ below MSRP) on branded goods from \
unestablished sellers are a negative relevance signal, as they indicate potential \
counterfeit, gray-market imports without warranty, or bait-and-switch risk.
- **Listing completeness and quality as trust proxy**: On marketplaces where anyone can \
list, listing quality varies enormously. Treat listing completeness — filled item \
specifics, multiple high-quality images, accurate and detailed descriptions, proper \
categorization, and included product identifiers (UPC/EAN/MPN) — as a positive \
relevance signal. Sparse listings with stock photos, missing specifications, vague \
descriptions, or incorrect categorization are weaker matches because they create buyer \
uncertainty and signal lower seller professionalism. Listings with complete structured \
attributes are up to 3x more likely to convert on major platforms, reflecting their \
higher effective relevance.
- **Duplicate and multi-offer deduplication awareness**: Marketplace search results \
often contain multiple listings for the exact same product from different sellers. When \
evaluating relevance, recognize that the best offer for a given product (considering \
price, condition, seller trust, and fulfillment) is the most relevant listing, and \
near-duplicate offers that are strictly inferior on all dimensions add noise rather \
than value. However, when offers differ meaningfully — different conditions (new vs \
refurbished), significantly different price tiers, or different bundle configurations — \
showing multiple listings serves buyer comparison needs and each can be independently \
relevant.
- **Category-specific marketplace dynamics**: Different product categories follow \
different relevance patterns on marketplaces. Commodity products (cables, batteries, \
office supplies) are price-and-speed sensitive — the cheapest offer with reliable \
delivery wins. Collectibles and vintage items are uniqueness-driven — condition \
grading accuracy, provenance, and seller specialization matter more than price. \
Handmade and artisan goods (Etsy-style) are creator-driven — the maker's reputation, \
customization options, and aesthetic alignment with query intent are primary. Branded \
electronics are spec-and-trust sensitive — compatibility, generation accuracy, and \
counterfeit risk dominate relevance. Adjust scoring weights to match the category's \
natural marketplace dynamics.
- **Primary product vs accessory and consumable intent**: If the query names a primary \
product ("iPad", "KitchenAid mixer", "Canon EOS R5"), listings for accessories, \
replacement parts, cases, or consumables should score lower unless the query \
explicitly asks for them. Conversely, accessory-intent queries ("iPhone 15 case", \
"Keurig K-Cup pods") should not return the primary device. Marketplace search results \
are particularly prone to this mismatch because third-party sellers aggressively \
keyword-stuff accessory listings with primary product names.
- **Seller diversity as a quality signal for result sets**: A healthy marketplace \
search result page should surface offers from diverse sellers rather than being \
monopolized by a single seller's listings. When evaluating individual results, note \
that a result from a seller who already dominates the result set provides diminishing \
relevance value — the tenth listing from the same seller adds less buyer utility than \
a first listing from a competitive alternative, even if the product match is identical.""",
    overlays={
        "automotive_parts": VerticalOverlay(
            description=(
                "Automotive parts, car accessories, replacement components, "
                "and fitment-dependent vehicle hardware."
            ),
            content="""\
### Automotive Parts — Scoring Guidance

This query involves automotive components and vehicle accessories.

**Critical distinctions to enforce:**

- **Fitment is absolute**: Queries containing vehicle identifiers (year, make, model, \
engine) utilize ACES (Aftermarket Catalog Exchange Standard) databases. A part that does \
not explicitly list compatibility with the queried vehicle is a severe mismatch, regardless \
of visual similarity.
- **Core Charges**: Heavy remanufactured parts (alternators, calipers, turbos) often \
include a "core charge" — a refundable deposit returned when the buyer ships back their \
broken part. Do not penalize listings with core charges as having "hidden fees" or \
forcing the purchase of unrelated accessories.
- **OEM vs. Aftermarket**: If a query explicitly requests OEM (Original Equipment Manufacturer) \
or a specific brand (e.g., "Motorcraft", "ACDelco"), aftermarket equivalents are poor \
matches. If not specified, high-rated aftermarket parts are acceptable.
- **Universal vs. Specific**: Items like floor mats or seat covers may be "universal fit." \
If the query requests a specific vehicle, custom-molded parts rank much higher than \
cut-to-fit universal options.
""",
        ),
        "refurbished_electronics": VerticalOverlay(
            description=(
                "Used, renewed, and refurbished consumer electronics, laptops, "
                "smartphones, and tablets."
            ),
            content="""\
### Refurbished Electronics — Scoring Guidance

This query involves pre-owned or refurbished consumer electronics.

**Critical distinctions to enforce:**

- **Grading Tiers**: Refurbished goods are strictly graded. Grade A (Excellent/Like-New) \
requires minimal to no cosmetic wear. Grade B (Good) allows light wear/scratches. \
Grade C (Fair) has noticeable cosmetic flaws (dents, heavy scratches). If a query \
requests "Grade A" or "Excellent," a Grade C or "Good" listing is a hard mismatch.
- **Open-Box vs. Refurbished**: "Open-box" items are unsealed returns that usually \
have not undergone factory repair. "Refurbished" or "Renewed" items have been tested, \
repaired, and repackaged. Do not treat them as identical if the query specifies one.
- **Platform Certifications**: Listings marked under official platform programs \
(e.g., Amazon Renewed, eBay Refurbished) guarantee warranty and condition standards. \
These should rank higher in seller trust than uncertified "seller refurbished" items.
""",
        ),
        "graded_collectibles": VerticalOverlay(
            description=(
                "Graded trading cards (sports, Pokémon, MTG) and graded comic books, "
                "involving specific grading authorities like PSA, BGS, CGC."
            ),
            content="""\
### Graded Collectibles — Scoring Guidance

This query involves professionally graded trading cards or comic books.

**Critical distinctions to enforce:**

- **Grading Authorities are not interchangeable**: PSA, BGS (Beckett), CGC, and CBCS \
are distinct entities. If a query specifies "PSA 10," a "BGS 9.5" or "CGC 10" is not \
a perfect match.
- **Sub-grades and Labels**: For trading cards, a BGS "Black Label" or "Pristine 10" \
requires perfect sub-grades and is significantly rarer and more valuable than a standard \
PSA 10. For comics, CGC and CBCS are the standards. CGC half-grades (e.g., 9.5) exist \
and must be matched exactly if requested.
- **Restoration Penalties**: In comics, a "Universal" label (usually blue) denotes an \
unaltered book. A "Restored" or "Conserved" label (usually purple) denotes chemical \
bleaching or touch-ups, drastically reducing market value. A query for a standard \
grade (e.g., "Action Comics #1 CGC 5.0") implicitly expects Universal; a Restored \
listing is a poor match unless restoration is requested.
- **Coverless Books**: In comic grading, a book missing its entire cover receives \
a strict uniform grade of 0.3.
""",
        ),
        "luxury_goods": VerticalOverlay(
            description=(
                "High-end luxury fashion, designer handbags, footwear, and accessories "
                "(e.g., Louis Vuitton, Chanel, Hermes) involving authenticity signals."
            ),
            content="""\
### Luxury Apparel and Accessories — Scoring Guidance

This query involves high-end designer fashion and luxury accessories.

**Critical distinctions to enforce:**

- **Gray Market / Parallel Imports**: Authentic luxury items legally distributed outside \
the brand's authorized retail channels are known as "gray market" goods. They often feature \
steep discounts. Do not automatically flag heavily discounted items as "counterfeit" if \
sold by reputable multi-brand sellers, but note they may lack original warranties.
- **Date Codes vs. Serial Numbers**: Brands like Louis Vuitton historically used "date codes" \
indicating the factory and date of manufacture, NOT unique serial numbers. Do not penalize \
a listing if it states "date code" when a user queries "serial number" for such brands. \
(Note: Modern bags often use RFID microchips instead).
- **Condition Modifiers**: Pay strict attention to condition acronyms. NWT (New With Tags), \
NWOT (New Without Tags), EUC (Excellent Used Condition), and GUC (Good Used Condition) \
are hard boundaries. An EUC listing fails a query looking for NWT.
""",
        ),
        "fine_jewelry": VerticalOverlay(
            description=(
                "Fine jewelry, natural diamonds, lab-grown diamonds, and gemstone "
                "certification (GIA, IGI)."
            ),
            content="""\
### Fine Jewelry and Gemstones — Scoring Guidance

This query involves diamonds, gemstones, and fine jewelry.

**Critical distinctions to enforce:**

- **Lab-Grown vs. Natural**: This is an absolute hard constraint. Never return a \
lab-grown diamond for a query explicitly seeking a natural/mined diamond, and vice versa.
- **Certification Authorities**: GIA is the strict, historical standard for natural \
diamonds. IGI is the industry standard and dominant certifier for lab-grown diamonds. \
Do not penalize an IGI-certified lab-grown diamond as having "inferior certification," \
as IGI is the accepted standard in that specific sub-market.
- **Grading Report vs. Appraisal**: A grading report (often called a certificate) \
documents the 4Cs (Cut, Color, Clarity, Carat) and verifies the physical stone. An appraisal \
is a financial document for insurance valuing the item. If a user queries a "certified" \
stone, an appraisal alone does not satisfy this requirement.
""",
        ),
        "power_tools": VerticalOverlay(
            description=(
                "Power tools, cordless drills, saws, impact drivers, and tool batteries "
                "(e.g., DeWalt, Milwaukee, Makita)."
            ),
            content="""\
### Power Tools — Scoring Guidance

This query involves power tools and related hardware.

**Critical distinctions to enforce:**

- **Voltage Marketing (18V vs. 20V Max)**: Electrically and chemically, an 18V battery \
and a "20V Max" battery (using 5-cell lithium-ion architecture) are identical. "20V Max" \
is a marketing term for maximum initial peak voltage, while "18V" is the nominal sustained \
operating voltage. Do NOT penalize an 18V tool as "less powerful" than a 20V Max tool, and treat \
them as interchangeable if the battery platform matches the user's intent.
- **Brushed vs. Brushless**: Brushless motors use electronic controllers instead of \
carbon brushes, offering longer runtime and power. If a query specifies "brushless," \
a standard brushed tool is a severe mismatch.
- **Bare Tool vs. Kit**: A "bare tool" (or "tool only") does not include a battery \
or charger. A "kit" does. If a user queries a kit, a bare tool is a hard mismatch \
due to the massive hidden cost of buying batteries separately.
""",
        ),
        "apparel_and_footwear": VerticalOverlay(
            description=(
                "General clothing, shoes, sneakers, and apparel sizing variations "
                "across international standards."
            ),
            content="""\
### Apparel and Footwear — Scoring Guidance

This query involves clothing and shoes.

**Critical distinctions to enforce:**

- **Regional Sizing Conversions**: US sizes are typically body-measurement based, \
while EU sizes are often garment-measurement based. A US Women's 8 roughly equates \
to an EU 38. A US 10 roughly equates to a UK 14. If a query specifies an EU size, \
a result in US sizing is relevant ONLY if the listing provides an accurate conversion.
- **Vanity Sizing**: Nominal sizes in the US have inflated over time. A "Size 0" \
today is physically larger than a "Size 0" from twenty years ago. For vintage apparel, \
rely on physical garment measurements (chest, waist, inseam) rather than nominal tag size.
- **Condition Abbreviations**: Enforce strict matching for NWT (New With Tags), \
NWOT (New Without Tags), EUC (Excellent Used Condition), and GUC (Good Used Condition).
""",
        ),
        "physical_media": VerticalOverlay(
            description=(
                "Vinyl records, LPs, collectible books, first editions, and physical media."
            ),
            content="""\
### Physical Media — Scoring Guidance

This query involves vinyl records and collectible books.

**Critical distinctions to enforce:**

- **Goldmine Grading Standard (Vinyl)**: Condition must adhere to: Mint (M), Near Mint (NM), \
Very Good Plus (VG+), Very Good (VG), and Good Plus (G+). A VG+ record is typically \
worth 50% of an NM record. A query for NM cannot be satisfied by VG+.
- **Dead Wax / Matrix Numbers (Vinyl)**: The definitive identifier of a specific vinyl pressing \
is the alphanumeric "matrix number" engraved in the "dead wax" (runout groove), NOT the \
barcode or sleeve text. Listings providing matrix numbers are highly relevant for first pressings.
- **First Edition vs. Book Club Edition (Books)**: A true First Edition holds immense \
value. A Book Club Edition (BCE) or Book of the Month Club (BOMC) edition was printed \
cheaply. BCEs generally lack a printed price on the dust jacket. If a query asks for a \
"First Edition," a BCE listing must be severely penalized.
""",
        ),
        "baby_and_juvenile": VerticalOverlay(
            description=(
                "Baby gear, strollers, cribs, car seats, and infant toys subject to "
                "child safety regulations."
            ),
            content="""\
### Baby and Juvenile Products — Scoring Guidance

This query involves products designed for infants and children under 12.

**Critical distinctions to enforce:**

- **Safety Certifications**: CPSC (Consumer Product Safety Commission) compliance is a \
mandatory federal law. ASTM International provides voluntary, independent safety standards. \
JPMA (Baby Safety Alliance) is a manufacturer-driven verification program that tests \
against ASTM standards.
- **Certification Hierarchy**: If a query demands "ASTM certified," a product bearing a \
JPMA seal satisfies this, as JPMA tests to ASTM standards.
- **Age Determination Guidelines**: Products must align with CPSC age-grading. A product \
with small parts is a severe mismatch and safety hazard if returned for an "infant" or \
"toddler" query, regardless of generic relevance.
""",
        ),
        "health_and_supplements": VerticalOverlay(
            description=(
                "Vitamins, dietary supplements, skincare, cosmetics, and wellness goods."
            ),
            content="""\
### Health, Beauty, and Supplements — Scoring Guidance

This query involves dietary supplements and topical beauty products.

**Critical distinctions to enforce:**

- **Professional vs. Consumer Grade Skincare**: Professional/medical-grade products \
(sold via spas/derm clinics) possess significantly higher concentrations of active ingredients \
than mass-market over-the-counter (OTC) consumer products. Do not treat them as identical \
if a query requests clinical/professional strength.
- **Supplement Certifications**: The FDA does not pre-approve supplements. Trust signals \
rely on third-party labs. USP verifies ingredients and potency. However, for athletes, \
"NSF Certified for Sport" is the absolute standard, as it tests for 280+ banned substances. \
A query for "athlete safe supplement" requires NSF Certified for Sport; USP alone is insufficient.
- **Expiration Logistics**: Supplements and cosmetics are perishable. Listings that guarantee \
freshness or adhere to FEFO (First Expired, First Out) policies rank higher.
""",
        ),
        "video_games": VerticalOverlay(
            description=(
                "Video games, gaming consoles, physical discs/cartridges, and digital "
                "download codes."
            ),
            content="""\
### Video Games — Scoring Guidance

This query involves gaming hardware and software.

**Critical distinctions to enforce:**

- **Region Locking (Physical vs. Digital)**: Historically, NTSC-U (North America), \
PAL (Europe), and NTSC-J (Japan) denoted analog video incompatibility. Today, they \
denote market regions for digital rights management.
- **Media Formats**: Modern physical games (Switch cartridges, PS5 discs) are generally \
region-free; a US player can use a European physical game. However, digital download \
codes and DLC are STRICTLY region-locked to the original digital storefront.
- **Penalty**: A query for a digital game code must exactly match the user's region. \
Returning a European digital code for a US buyer is a fatal mismatch.
""",
        ),
        "heavy_goods_and_logistics": VerticalOverlay(
            description=(
                "Large appliances (refrigerators, washers), heavy furniture, and goods "
                "requiring freight/LTL shipping."
            ),
            content="""\
### Heavy Furniture and Appliances — Scoring Guidance

This query involves bulky items requiring specialized logistics.

**Critical distinctions to enforce:**

- **Assembly Status**: Distinguish strictly between Ready-To-Assemble (RTA) / "flat-pack" \
furniture and fully assembled pieces. Flat-pack reduces freight costs but requires DIY \
labor. If a query specifies "fully assembled," an RTA listing is a severe mismatch.
- **LTL and Last-Mile Logistics**: Heavy goods ship via Less-Than-Truckload (LTL) freight. \
Relevance for major appliances is heavily dependent on the inclusion of last-mile services \
like "liftgate delivery," "white-glove installation," and "old unit haul-away." Offers \
including these services are highly relevant compared to threshold-only deliveries.
""",
        ),
        "sports_safety_equipment": VerticalOverlay(
            description=(
                "Protective athletic gear, helmets, and sports equipment requiring "
                "impact certifications."
            ),
            content="""\
### Protective Sports Equipment — Scoring Guidance

This query involves high-impact athletic safety gear.

**Critical distinctions to enforce:**

- **NOCSAE vs. SEI**: NOCSAE develops the biomechanical standards for sports helmets; \
they do NOT certify products. SEI (Safety Equipment Institute) is the third-party body \
that actually executes the certification.
- **Aftermarket Voiding**: Attaching uncertified third-party accessories (e.g., aftermarket \
visors) to an SEI-certified helmet instantly voids the helmet's certification. Penalize \
listings that bundle uncertified accessories with certified helmets, as this represents \
a severe safety and liability failure.
""",
        ),
    },
)
