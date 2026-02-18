"""Autocomplete evaluation pipeline orchestrators."""

from __future__ import annotations

from collections.abc import Callable

from rich.console import Console
from rich.progress import Progress

from veritail.autocomplete import run_autocomplete_checks
from veritail.autocomplete.comparison import (
    check_rank_agreement,
    check_suggestion_overlap,
)
from veritail.autocomplete.metrics import compute_autocomplete_metrics
from veritail.types import (
    AutocompleteConfig,
    AutocompleteResponse,
    CheckResult,
    MetricResult,
    PrefixEntry,
)

console = Console()


def run_autocomplete_evaluation(
    prefixes: list[PrefixEntry],
    adapter: Callable[[str], AutocompleteResponse],
    config: AutocompleteConfig,
    custom_checks: (
        list[Callable[[str, AutocompleteResponse], list[CheckResult]]] | None
    ) = None,
) -> tuple[list[CheckResult], list[MetricResult], dict[int, AutocompleteResponse]]:
    """Run a single-configuration autocomplete evaluation.

    For each prefix: call adapter, run checks, collect response.
    After loop: compute metrics.

    Returns:
        Tuple of (checks, metrics, responses_by_prefix).
    """
    all_checks: list[CheckResult] = []
    responses_by_prefix: dict[int, AutocompleteResponse] = {}

    with Progress(console=console) as progress:
        task = progress.add_task(
            f"[cyan]Evaluating '{config.name}'...", total=len(prefixes)
        )
        for i, entry in enumerate(prefixes):
            try:
                response = adapter(entry.prefix)
                # Trim to top_k
                response = AutocompleteResponse(
                    suggestions=response.suggestions[: config.top_k],
                    metadata=response.metadata,
                )
                responses_by_prefix[i] = response
            except Exception as exc:
                console.print(
                    f"[yellow]Adapter error for prefix '{entry.prefix}': {exc}[/yellow]"
                )
                responses_by_prefix[i] = AutocompleteResponse(suggestions=[])

            checks = run_autocomplete_checks(
                entry.prefix, responses_by_prefix[i], custom_checks=custom_checks
            )
            all_checks.extend(checks)
            progress.advance(task)

    metrics = compute_autocomplete_metrics(responses_by_prefix, prefixes)
    return all_checks, metrics, responses_by_prefix


def run_dual_autocomplete_evaluation(
    prefixes: list[PrefixEntry],
    adapter_a: Callable[[str], AutocompleteResponse],
    config_a: AutocompleteConfig,
    adapter_b: Callable[[str], AutocompleteResponse],
    config_b: AutocompleteConfig,
    custom_checks: (
        list[Callable[[str, AutocompleteResponse], list[CheckResult]]] | None
    ) = None,
) -> tuple[
    list[CheckResult],
    list[CheckResult],
    list[MetricResult],
    list[MetricResult],
    list[CheckResult],
]:
    """Run a dual-configuration autocomplete evaluation.

    Returns:
        Tuple of (checks_a, checks_b, metrics_a, metrics_b, comparison_checks).
    """
    checks_a, metrics_a, responses_a = run_autocomplete_evaluation(
        prefixes, adapter_a, config_a, custom_checks=custom_checks
    )
    checks_b, metrics_b, responses_b = run_autocomplete_evaluation(
        prefixes, adapter_b, config_b, custom_checks=custom_checks
    )

    comparison_checks: list[CheckResult] = []
    for i, entry in enumerate(prefixes):
        sug_a = responses_a.get(i, AutocompleteResponse(suggestions=[]))
        sug_b = responses_b.get(i, AutocompleteResponse(suggestions=[]))
        comparison_checks.append(
            check_suggestion_overlap(entry.prefix, sug_a.suggestions, sug_b.suggestions)
        )
        comparison_checks.append(
            check_rank_agreement(entry.prefix, sug_a.suggestions, sug_b.suggestions)
        )

    return checks_a, checks_b, metrics_a, metrics_b, comparison_checks
