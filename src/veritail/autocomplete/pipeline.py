"""Autocomplete evaluation pipeline orchestrators."""

from __future__ import annotations

import time
from collections.abc import Callable

from rich.console import Console
from rich.progress import Progress

from veritail.autocomplete import run_autocomplete_checks
from veritail.autocomplete.comparison import (
    check_rank_agreement,
    check_suggestion_overlap,
)
from veritail.autocomplete.judge import SuggestionJudge
from veritail.types import (
    AutocompleteConfig,
    AutocompleteResponse,
    CheckResult,
    PrefixEntry,
    SuggestionJudgment,
)

console = Console()


def run_autocomplete_evaluation(
    prefixes: list[PrefixEntry],
    adapter: Callable[[str], AutocompleteResponse],
    config: AutocompleteConfig,
    custom_checks: (
        list[Callable[[str, AutocompleteResponse], list[CheckResult]]] | None
    ) = None,
) -> tuple[list[CheckResult], dict[int, AutocompleteResponse]]:
    """Run a single-configuration autocomplete evaluation.

    For each prefix: call adapter, run checks, collect response.

    Returns:
        Tuple of (checks, responses_by_prefix).
    """
    all_checks: list[CheckResult] = []
    responses_by_prefix: dict[int, AutocompleteResponse] = {}

    with Progress(console=console) as progress:
        task = progress.add_task(
            f"[cyan]Evaluating '{config.name}'...", total=len(prefixes)
        )
        for i, entry in enumerate(prefixes):
            latency_ms: float | None = None
            try:
                t0 = time.perf_counter()
                response = adapter(entry.prefix)
                latency_ms = (time.perf_counter() - t0) * 1000.0
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
                entry.prefix,
                responses_by_prefix[i],
                custom_checks=custom_checks,
                latency_ms=latency_ms,
            )
            all_checks.extend(checks)
            progress.advance(task)

    return all_checks, responses_by_prefix


def run_dual_autocomplete_evaluation(
    prefixes: list[PrefixEntry],
    adapter_a: Callable[[str], AutocompleteResponse],
    config_a: AutocompleteConfig,
    adapter_b: Callable[[str], AutocompleteResponse],
    config_b: AutocompleteConfig,
    custom_checks: (
        list[Callable[[str, AutocompleteResponse], list[CheckResult]]] | None
    ) = None,
) -> tuple[list[CheckResult], list[CheckResult], list[CheckResult]]:
    """Run a dual-configuration autocomplete evaluation.

    Returns:
        Tuple of (checks_a, checks_b, comparison_checks).
    """
    checks_a, responses_a = run_autocomplete_evaluation(
        prefixes, adapter_a, config_a, custom_checks=custom_checks
    )
    checks_b, responses_b = run_autocomplete_evaluation(
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

    return checks_a, checks_b, comparison_checks


def run_autocomplete_llm_evaluation(
    prefixes: list[PrefixEntry],
    responses_by_prefix: dict[int, AutocompleteResponse],
    judge: SuggestionJudge,
    config: AutocompleteConfig,
) -> list[SuggestionJudgment]:
    """Run LLM-based semantic evaluation on autocomplete suggestions.

    One LLM call per prefix. Skips prefixes with empty suggestions.

    Args:
        prefixes: The prefix entries to evaluate.
        responses_by_prefix: Mapping of prefix index to adapter responses.
        judge: A SuggestionJudge instance for LLM evaluation.
        config: Autocomplete configuration.

    Returns:
        List of SuggestionJudgment results.
    """

    judgments: list[SuggestionJudgment] = []

    with Progress(console=console) as progress:
        task = progress.add_task(
            f"[cyan]LLM judging '{config.name}'...", total=len(prefixes)
        )
        for i, entry in enumerate(prefixes):
            resp = responses_by_prefix.get(i)
            if not resp or not resp.suggestions:
                progress.advance(task)
                continue

            try:
                sj = judge.judge(entry.prefix, resp.suggestions)
                judgments.append(sj)
            except Exception as exc:
                console.print(
                    f"[yellow]LLM judge error for prefix "
                    f"'{entry.prefix}': {exc}[/yellow]"
                )
                judgments.append(
                    SuggestionJudgment(
                        prefix=entry.prefix,
                        suggestions=resp.suggestions,
                        relevance_score=0,
                        diversity_score=0,
                        flagged_suggestions=[],
                        reasoning="",
                        model="",
                        experiment=config.name,
                        metadata={"error": str(exc)},
                    )
                )
            progress.advance(task)

    return judgments
