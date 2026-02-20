"""Autocomplete evaluation pipeline orchestrators."""

from __future__ import annotations

import threading
import time
from collections.abc import Callable
from typing import Any

from rich.console import Console
from rich.progress import Progress

from veritail.autocomplete import run_autocomplete_checks
from veritail.autocomplete.comparison import (
    check_rank_agreement,
    check_suggestion_overlap,
)
from veritail.autocomplete.judge import SuggestionJudge
from veritail.batch_utils import poll_until_done
from veritail.checkpoint import (
    BatchCheckpoint,
    clear_checkpoint,
    load_checkpoint,
    save_checkpoint,
)
from veritail.llm.client import BatchRequest, LLMClient
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


AC_CHECKPOINT_FILENAME = "ac-checkpoint.json"


def run_autocomplete_batch_llm_evaluation(
    prefixes: list[PrefixEntry],
    responses_by_prefix: dict[int, AutocompleteResponse],
    judge: SuggestionJudge,
    config: AutocompleteConfig,
    llm_client: LLMClient,
    *,
    poll_interval: int = 60,
    resume: bool = False,
    output_dir: str = "./eval-results",
    cancel_event: threading.Event | None = None,
) -> list[SuggestionJudgment]:
    """Run batch LLM-based semantic evaluation on autocomplete suggestions.

    Same as ``run_autocomplete_llm_evaluation`` but uses the provider batch
    API for 50% cost reduction.
    """
    # Step 1: Resume check
    saved_checkpoint: BatchCheckpoint | None = None
    if resume:
        saved_checkpoint = load_checkpoint(
            output_dir, config.name, filename=AC_CHECKPOINT_FILENAME
        )

    if saved_checkpoint is not None:
        batch_id = saved_checkpoint.batch_id
        request_context: dict[str, dict[str, Any]] = saved_checkpoint.request_context
        # Restore Gemini custom_id ordering if needed
        if saved_checkpoint.gemini_custom_id_order:
            llm_client.restore_batch_custom_ids(
                batch_id, saved_checkpoint.gemini_custom_id_order
            )
        console.print(
            f"[bold]Resuming autocomplete batch {batch_id} "
            f"for '{config.name}'...[/bold]"
        )
    else:
        # Step 2: Collect & submit
        batch_requests: list[BatchRequest] = []
        request_context = {}

        for i, entry in enumerate(prefixes):
            resp = responses_by_prefix.get(i)
            if not resp or not resp.suggestions:
                continue

            custom_id = f"ac-{i}"
            batch_req = judge.prepare_request(custom_id, entry.prefix, resp.suggestions)
            batch_requests.append(batch_req)
            request_context[custom_id] = {
                "prefix": entry.prefix,
                "suggestions": resp.suggestions,
                "prefix_index": i,
            }

        if not batch_requests:
            return []

        console.print(
            f"[cyan]Submitting autocomplete batch of "
            f"{len(batch_requests)} requests...[/cyan]"
        )
        batch_id = llm_client.submit_batch(batch_requests)
        console.print(f"[dim]Batch ID: {batch_id}[/dim]")

        gemini_order = getattr(llm_client, "_batch_custom_ids", {}).get(batch_id, [])
        save_checkpoint(
            output_dir,
            config.name,
            BatchCheckpoint(
                batch_id=batch_id,
                experiment_name=config.name,
                phase="autocomplete",
                request_context=request_context,
                checks=[],
                correction_entries=[],
                gemini_custom_id_order=gemini_order,
            ),
            filename=AC_CHECKPOINT_FILENAME,
        )

    # Step 3: Poll
    try:
        poll_until_done(
            llm_client,
            batch_id,
            expected_total=len(request_context),
            poll_interval=poll_interval,
            label="Waiting for autocomplete batch...",
            cancel_event=cancel_event,
        )
    except RuntimeError as exc:
        clear_checkpoint(output_dir, config.name, filename=AC_CHECKPOINT_FILENAME)
        msg = str(exc)
        if resume:
            msg += (
                " Checkpoint cleared — re-run without --resume to start a fresh batch."
            )
        raise RuntimeError(msg) from exc

    # Step 4: Retrieve & parse
    console.print("[cyan]Retrieving autocomplete batch results...[/cyan]")
    batch_results = llm_client.retrieve_batch_results(batch_id)
    results_by_id = {r.custom_id: r for r in batch_results}

    judgments: list[SuggestionJudgment] = []

    for custom_id, ctx in request_context.items():
        prefix = ctx["prefix"]
        suggestions = ctx["suggestions"]

        batch_result = results_by_id.get(custom_id)

        if batch_result and batch_result.response:
            try:
                sj = judge.parse_batch_result(
                    batch_result.response, prefix, suggestions
                )
                judgments.append(sj)
            except Exception as exc:
                judgments.append(
                    SuggestionJudgment(
                        prefix=prefix,
                        suggestions=suggestions,
                        relevance_score=0,
                        diversity_score=0,
                        flagged_suggestions=[],
                        reasoning=f"Error parsing response: {exc}",
                        model="",
                        experiment=config.name,
                        metadata={"error": str(exc)},
                    )
                )
        else:
            error_msg = batch_result.error if batch_result else "No result returned"
            judgments.append(
                SuggestionJudgment(
                    prefix=prefix,
                    suggestions=suggestions,
                    relevance_score=0,
                    diversity_score=0,
                    flagged_suggestions=[],
                    reasoning=f"Batch error: {error_msg}",
                    model="",
                    experiment=config.name,
                    metadata={"error": error_msg},
                )
            )

    clear_checkpoint(output_dir, config.name, filename=AC_CHECKPOINT_FILENAME)
    return judgments
