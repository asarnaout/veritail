"""Built-in vertical contexts for domain-specific LLM judge guidance."""

from __future__ import annotations

from pathlib import Path

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
    "load_vertical",
]

_BUILTIN_VERTICALS: dict[str, str] = {
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


def load_vertical(name: str) -> str:
    """Load vertical context by built-in name or file path.

    Args:
        name: Built-in vertical name (automotive, beauty, electronics,
              fashion, foodservice, furniture, groceries, home-improvement,
              industrial, marketplace, medical, office-supplies,
              pet-supplies, sporting-goods) or path to a plain text file.

    Returns:
        Vertical context string ready for system prompt injection.

    Raises:
        FileNotFoundError: If name is not a built-in vertical and the file
            path does not exist.
    """
    key = name.lower()
    if key in _BUILTIN_VERTICALS:
        return _BUILTIN_VERTICALS[key]

    path = Path(name)
    if path.is_file():
        return path.read_text(encoding="utf-8").rstrip()

    available = ", ".join(sorted(_BUILTIN_VERTICALS))
    raise FileNotFoundError(
        f"Unknown vertical '{name}'. "
        f"Available built-in verticals: {available}. "
        f"Or provide a path to a text file."
    )
