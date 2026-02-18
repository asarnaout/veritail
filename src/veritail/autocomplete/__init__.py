"""Autocomplete suggestion evaluation checks."""

from __future__ import annotations

from collections.abc import Callable

from veritail.autocomplete.checks import (
    check_duplicate_suggestions,
    check_empty_suggestions,
    check_offensive_content,
    check_prefix_coherence,
)
from veritail.types import AutocompleteResponse, CheckResult


def run_autocomplete_checks(
    prefix: str,
    response: AutocompleteResponse,
    custom_checks: (
        list[Callable[[str, AutocompleteResponse], list[CheckResult]]] | None
    ) = None,
) -> list[CheckResult]:
    """Run all applicable deterministic checks for a prefix and its suggestions."""
    checks: list[CheckResult] = []
    suggestions = response.suggestions

    checks.append(check_empty_suggestions(prefix, suggestions))
    if suggestions:
        checks.extend(check_duplicate_suggestions(prefix, suggestions))
        checks.extend(check_prefix_coherence(prefix, suggestions))
        checks.extend(check_offensive_content(prefix, suggestions))

    if custom_checks:
        for check_fn in custom_checks:
            checks.extend(check_fn(prefix, response))

    return checks


__all__ = [
    "run_autocomplete_checks",
]
