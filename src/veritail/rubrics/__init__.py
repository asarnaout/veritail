"""Rubric loading for LLM relevance judgment."""

from __future__ import annotations

import importlib.util
from collections.abc import Callable
from pathlib import Path
from typing import Tuple

from veritail.types import SearchResult


def load_rubric(name: str) -> Tuple[str, Callable[[str, SearchResult], str]]:
    """Load a rubric by name or file path.

    Returns a tuple of (system_prompt, format_user_prompt_function).

    Built-in rubrics:
        - "ecommerce-default": Default ecommerce relevance rubric

    Custom rubrics:
        Provide a path to a Python file that defines:
        - SYSTEM_PROMPT: str
        - format_user_prompt(query: str, result: SearchResult) -> str
    """
    if name == "ecommerce-default":
        from veritail.rubrics.ecommerce_default import (
            SYSTEM_PROMPT,
            format_user_prompt,
        )
        return SYSTEM_PROMPT, format_user_prompt

    # Treat as a file path to a custom rubric
    file_path = Path(name)
    if not file_path.exists():
        raise FileNotFoundError(
            f"Rubric '{name}' is not a built-in rubric and file not found. "
            f"Available built-in rubrics: ecommerce-default"
        )

    spec = importlib.util.spec_from_file_location("custom_rubric", file_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load rubric from: {name}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    if not hasattr(module, "SYSTEM_PROMPT"):
        raise AttributeError(f"Custom rubric '{name}' must define SYSTEM_PROMPT")
    if not hasattr(module, "format_user_prompt"):
        raise AttributeError(f"Custom rubric '{name}' must define format_user_prompt")

    return module.SYSTEM_PROMPT, module.format_user_prompt
