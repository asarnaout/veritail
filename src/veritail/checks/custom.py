"""Dynamic loading of developer-provided custom check functions."""

from __future__ import annotations

import importlib.util
from collections.abc import Callable
from pathlib import Path

from veritail.types import CheckResult, QueryEntry, SearchResult

CustomCheckFn = Callable[[QueryEntry, list[SearchResult]], list[CheckResult]]


def load_checks(path: str) -> list[CustomCheckFn]:
    """Load custom check functions from a Python file.

    The file must define one or more functions whose names start with
    ``check_``.  Each function must accept ``(QueryEntry, list[SearchResult])``
    and return ``list[CheckResult]``.

    Non-callable attributes whose names start with ``check_`` (e.g.
    ``check_threshold = 0.5``) are silently skipped.

    Returns:
        Sorted list of discovered check functions.

    Raises:
        FileNotFoundError: If *path* does not exist.
        ValueError: If *path* is not a ``.py`` file or no ``check_*``
            functions are found.
    """
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"Check module not found: {path}")
    if file_path.suffix != ".py":
        raise ValueError(
            f"Check module must be a Python file (.py), got: {file_path.suffix}"
        )

    spec = importlib.util.spec_from_file_location("custom_checks_module", file_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load check module from: {path}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    check_fns: list[tuple[str, CustomCheckFn]] = []
    for name in sorted(dir(module)):
        if name.startswith("check_"):
            obj = getattr(module, name)
            if callable(obj):
                check_fns.append((name, obj))

    if not check_fns:
        available = [n for n in dir(module) if not n.startswith("_")]
        raise ValueError(
            f"Check module '{path}' has no check_* functions. "
            f"Available names: {available}"
        )

    return [fn for _, fn in check_fns]
