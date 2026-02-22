"""Built-in vertical contexts for domain-specific LLM judge guidance."""

from __future__ import annotations

import logging
from pathlib import Path

from veritail.types import VerticalContext
from veritail.verticals.automotive import AUTOMOTIVE
from veritail.verticals.beauty import BEAUTY
from veritail.verticals.electronics import ELECTRONICS
from veritail.verticals.fashion import FASHION
from veritail.verticals.foodservice import FOODSERVICE
from veritail.verticals.furniture import FURNITURE
from veritail.verticals.groceries import GROCERIES
from veritail.verticals.home_improvement import HOME_IMPROVEMENT
from veritail.verticals.industrial import INDUSTRIAL
from veritail.verticals.marketplace import MARKETPLACE
from veritail.verticals.medical import MEDICAL
from veritail.verticals.office_supplies import OFFICE_SUPPLIES
from veritail.verticals.pet_supplies import PET_SUPPLIES
from veritail.verticals.sporting_goods import SPORTING_GOODS

logger = logging.getLogger(__name__)

__all__ = [
    "AUTOMOTIVE",
    "BEAUTY",
    "ELECTRONICS",
    "FASHION",
    "FOODSERVICE",
    "FURNITURE",
    "GROCERIES",
    "HOME_IMPROVEMENT",
    "INDUSTRIAL",
    "MARKETPLACE",
    "MEDICAL",
    "OFFICE_SUPPLIES",
    "PET_SUPPLIES",
    "SPORTING_GOODS",
    "list_verticals",
    "load_vertical",
]

_BUILTIN_VERTICALS: dict[str, VerticalContext] = {
    "automotive": AUTOMOTIVE,
    "beauty": BEAUTY,
    "electronics": ELECTRONICS,
    "fashion": FASHION,
    "foodservice": FOODSERVICE,
    "furniture": FURNITURE,
    "groceries": GROCERIES,
    "home-improvement": HOME_IMPROVEMENT,
    "industrial": INDUSTRIAL,
    "marketplace": MARKETPLACE,
    "medical": MEDICAL,
    "office-supplies": OFFICE_SUPPLIES,
    "pet-supplies": PET_SUPPLIES,
    "sporting-goods": SPORTING_GOODS,
}


def list_verticals() -> list[str]:
    """Return sorted names of all built-in verticals."""
    return sorted(_BUILTIN_VERTICALS)


def load_vertical(name: str) -> VerticalContext:
    """Load vertical context by built-in name or file path.

    Args:
        name: Built-in vertical name (automotive, beauty, electronics,
              fashion, foodservice, furniture, groceries, home-improvement,
              industrial, marketplace, medical, office-supplies,
              pet-supplies, sporting-goods) or path to a plain text file.

    Returns:
        VerticalContext with core text (and overlays for built-in verticals
        that define them).

    Raises:
        FileNotFoundError: If name is not a built-in vertical and the file
            path does not exist.
    """
    key = name.lower()
    if key in _BUILTIN_VERTICALS:
        vc = _BUILTIN_VERTICALS[key]
        overlay_count = len(vc.overlays) if vc.overlays else 0
        logger.debug(
            "loaded built-in vertical: %s, core=%d chars, overlays=%d",
            key,
            len(vc.core),
            overlay_count,
        )
        return vc

    path = Path(name)
    if path.is_file():
        vc = VerticalContext(core=path.read_text(encoding="utf-8").rstrip())
        logger.debug(
            "loaded vertical from file: %s, core=%d chars",
            name,
            len(vc.core),
        )
        return vc

    available = ", ".join(sorted(_BUILTIN_VERTICALS))
    raise FileNotFoundError(
        f"Unknown vertical '{name}'. "
        f"Available built-in verticals: {available}. "
        f"Or provide a path to a text file."
    )
