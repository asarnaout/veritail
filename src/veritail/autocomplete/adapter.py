"""Dynamic loading of developer-provided suggest adapter functions."""

from __future__ import annotations

import importlib.util
from collections.abc import Callable
from pathlib import Path

from veritail.types import AutocompleteResponse


def load_suggest_adapter(path: str) -> Callable[[str], AutocompleteResponse]:
    """Load a suggest adapter function from a Python file.

    The file must define a function named 'suggest' that takes a prefix string
    and returns a list of strings or an AutocompleteResponse.
    """
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"Suggest adapter file not found: {path}")
    if not file_path.suffix == ".py":
        raise ValueError(
            f"Suggest adapter must be a Python file (.py), got: {file_path.suffix}"
        )

    spec = importlib.util.spec_from_file_location("suggest_adapter_module", file_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load suggest adapter from: {path}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    if not hasattr(module, "suggest"):
        raise AttributeError(
            f"Suggest adapter module '{path}' must define a 'suggest' function. "
            f"Available names: {[n for n in dir(module) if not n.startswith('_')]}"
        )

    suggest_fn = module.suggest
    if not callable(suggest_fn):
        raise TypeError(f"'suggest' in '{path}' is not callable")

    def _wrap(prefix: str) -> AutocompleteResponse:
        raw = suggest_fn(prefix)
        if isinstance(raw, AutocompleteResponse):
            return raw
        return AutocompleteResponse(suggestions=list(raw))

    return _wrap
