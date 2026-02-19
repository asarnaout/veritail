"""Home improvement autocomplete mock adapter.

Returns hardcoded type-ahead suggestions for home improvement prefixes.
Replace with real API calls to your autocomplete endpoint.
"""

from veritail import AutocompleteResponse

_SUGGESTIONS: dict[str, list[str]] = {
    "dr": [
        "drill",
        "drain snake",
        "drywall screws",
        "drop cloth",
        "drawer slides",
        "dryer vent kit",
    ],
    "pe": [
        "pex tubing",
        "pendant light",
        "peel and stick tile",
        "pergo flooring",
        "pegboard hooks",
        "pex crimp rings",
    ],
    "fa": [
        "faucet",
        "fan ceiling",
        "fasteners",
        "farmhouse sink",
        "fascia board",
        "fan bathroom exhaust",
    ],
    "dec": [
        "deck screws",
        "deck stain",
        "deck boards composite",
        "deck railing",
        "decorative shelf brackets",
        "deck post cap",
    ],
    "pex": [
        "pex tubing 1/2 inch",
        "pex tubing 3/4 inch",
        "pex crimp tool",
        "pex fittings",
        "pex crimp rings",
        "pex manifold",
    ],
    "gfci": [
        "gfci outlet",
        "gfci outlet 20 amp",
        "gfci breaker",
        "gfci outlet outdoor",
        "gfci outlet white",
        "gfci outlet with usb",
    ],
    "drill": [
        "drill bit set",
        "drill press",
        "drill cordless",
        "drill dewalt 20v",
        "drill bits for concrete",
        "drill impact driver combo",
    ],
    "cedar": [
        "cedar fence pickets",
        "cedar boards",
        "cedar deck boards",
        "cedar shingles",
        "cedar 4x4 post",
        "cedar fence panels",
    ],
    "romex": [
        "romex 12/2 wire",
        "romex 14/2 wire",
        "romex 10/3 wire",
        "romex wire staples",
        "romex connector",
        "romex 12/2 250 ft",
    ],
    "insula": [
        "insulation fiberglass",
        "insulation foam board",
        "insulation r-13",
        "insulation r-19",
        "insulation spray foam",
        "insulation pipe wrap",
    ],
    "dewalt": [
        "dewalt 20v drill",
        "dewalt impact driver",
        "dewalt circular saw",
        "dewalt battery 20v",
        "dewalt miter saw",
        "dewalt oscillating tool",
    ],
    "toilet": [
        "toilet",
        "toilet elongated",
        "toilet seat",
        "toilet flange",
        "toilet wax ring",
        "toilet fill valve",
    ],
    "pressure treated": [
        "pressure treated 2x4",
        "pressure treated 4x4 post",
        "pressure treated deck boards",
        "pressure treated 2x6",
        "pressure treated plywood",
        "pressure treated lattice",
    ],
    "brushed nickel cabinet": [
        "brushed nickel cabinet pulls",
        "brushed nickel cabinet knobs",
        "brushed nickel cabinet handles",
        "brushed nickel cabinet hinges",
        "brushed nickel cabinet bar pulls",
    ],
    "led recessed light 6 inch": [
        "led recessed light 6 inch retrofit",
        "led recessed light 6 inch dimmable",
        "led recessed light 6 inch 3000k",
        "led recessed light 6 inch 4000k",
        "led recessed light 6 inch canless",
    ],
    "milwaukee m18 impact driver": [
        "milwaukee m18 impact driver",
        "milwaukee m18 impact driver kit",
        "milwaukee m18 impact driver brushless",
        "milwaukee m18 impact driver fuel",
    ],
    "kohler toilet elongated": [
        "kohler toilet elongated",
        "kohler toilet elongated white",
        "kohler toilet elongated comfort height",
        "kohler toilet elongated one piece",
        "kohler toilet elongated highline",
    ],
    "self drilling drywall anchor": [
        "self drilling drywall anchors",
        "self drilling drywall anchor #8",
        "self drilling drywall anchor zinc",
        "self drilling drywall anchor with screws",
    ],
}


def suggest(prefix: str) -> AutocompleteResponse:
    """Return autocomplete suggestions for a given prefix.

    Replace this with a real API call to your autocomplete endpoint:

        response = requests.get(
            "https://your-api.com/suggest",
            params={"q": prefix},
        )
        return AutocompleteResponse(suggestions=response.json()["suggestions"])
    """
    suggestions = _SUGGESTIONS.get(prefix, [])
    return AutocompleteResponse(suggestions=suggestions)
