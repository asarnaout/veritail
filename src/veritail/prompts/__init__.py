"""Prompt loading utilities."""

from __future__ import annotations

from functools import cache
from pathlib import Path

_PROMPTS_DIR = Path(__file__).resolve().parent


@cache
def load_prompt(relative_path: str) -> str:
    """Load a prompt markdown file relative to the prompts directory."""
    path = _PROMPTS_DIR / relative_path
    text = path.read_text(encoding="utf-8")
    return text.replace("\r\n", "\n").strip()
