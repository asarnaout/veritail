"""Built-in vertical contexts for domain-specific LLM judge guidance."""

from __future__ import annotations

from pathlib import Path

from veritail.verticals.automotive import AUTOMOTIVE
from veritail.verticals.beauty import BEAUTY
from veritail.verticals.electronics import ELECTRONICS
from veritail.verticals.fashion import FASHION
from veritail.verticals.foodservice import FOODSERVICE
from veritail.verticals.groceries import GROCERIES
from veritail.verticals.industrial import INDUSTRIAL
from veritail.verticals.marketplace import MARKETPLACE
from veritail.verticals.medical import MEDICAL

__all__ = [
    "AUTOMOTIVE",
    "BEAUTY",
    "ELECTRONICS",
    "FASHION",
    "FOODSERVICE",
    "GROCERIES",
    "INDUSTRIAL",
    "MARKETPLACE",
    "MEDICAL",
    "load_vertical",
]

_BUILTIN_VERTICALS: dict[str, str] = {
    "automotive": AUTOMOTIVE,
    "beauty": BEAUTY,
    "foodservice": FOODSERVICE,
    "industrial": INDUSTRIAL,
    "electronics": ELECTRONICS,
    "fashion": FASHION,
    "groceries": GROCERIES,
    "marketplace": MARKETPLACE,
    "medical": MEDICAL,
}


def load_vertical(name: str) -> str:
    """Load vertical context by built-in name or file path.

    Args:
        name: Built-in vertical name (automotive, beauty, foodservice,
              industrial, electronics, fashion, groceries, marketplace,
              medical) or path to a plain text file.

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
