"""Dynamic loading of developer-provided search adapter functions."""

from __future__ import annotations

import importlib.util
from collections.abc import Callable
from pathlib import Path

from search_eval.types import SearchResult


def load_adapter(path: str) -> Callable[[str], list[SearchResult]]:
    """Load a search adapter function from a Python file.

    The file must define a function named 'search' that takes a query string
    and returns a list of SearchResult objects.
    """
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"Adapter file not found: {path}")
    if not file_path.suffix == ".py":
        raise ValueError(f"Adapter must be a Python file (.py), got: {file_path.suffix}")

    spec = importlib.util.spec_from_file_location("adapter_module", file_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load adapter from: {path}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    if not hasattr(module, "search"):
        raise AttributeError(
            f"Adapter module '{path}' must define a 'search' function. "
            f"Available names: {[n for n in dir(module) if not n.startswith('_')]}"
        )

    search_fn = module.search
    if not callable(search_fn):
        raise TypeError(f"'search' in '{path}' is not callable")

    return search_fn
