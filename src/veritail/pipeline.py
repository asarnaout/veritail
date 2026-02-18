"""Main evaluation pipeline orchestrator."""

from __future__ import annotations

import time
from collections import defaultdict
from collections.abc import Callable

from rich.console import Console
from rich.progress import Progress

from veritail.backends import EvalBackend
from veritail.checks import run_all_checks
from veritail.checks.comparison import (
    check_rank_correlation,
    check_result_overlap,
    find_position_shifts,
)
from veritail.checks.correction import (
    check_correction_vocabulary,
    check_unnecessary_correction,
)
from veritail.llm.client import BatchRequest, LLMClient
from veritail.llm.judge import CORRECTION_SYSTEM_PROMPT, CorrectionJudge, RelevanceJudge
from veritail.metrics.ir import compute_all_metrics
from veritail.types import (
    CheckResult,
    CorrectionJudgment,
    ExperimentConfig,
    JudgmentRecord,
    MetricResult,
    QueryEntry,
    SearchResponse,
    SearchResult,
)

console = Console()


def run_evaluation(
    queries: list[QueryEntry],
    adapter: Callable[[str], SearchResponse | list[SearchResult]],
    config: ExperimentConfig,
    llm_client: LLMClient,
    rubric: tuple[str, Callable[..., str]],
    backend: EvalBackend,
    context: str | None = None,
    vertical: str | None = None,
    custom_checks: (
        list[Callable[[QueryEntry, list[SearchResult]], list[CheckResult]]] | None
    ) = None,
) -> tuple[
    list[JudgmentRecord],
    list[CheckResult],
    list[MetricResult],
    list[CorrectionJudgment],
]:
    """Run a full evaluation pipeline for a single configuration.

    Steps:
        1. Log the experiment
        2. For each query: call adapter, run checks, judge with LLM, log results
        3. Run correction evaluations for corrected queries
        4. Compute IR metrics

    Returns:
        Tuple of (judgments, check_results, metrics, correction_judgments)
    """
    system_prompt, format_user_prompt = rubric
    prefix_parts: list[str] = []
    if context:
        prefix_parts.append(f"## Business Context\n{context}")
    if vertical:
        prefix_parts.append(vertical)
    if prefix_parts:
        prefix = "\n\n".join(prefix_parts)
        system_prompt = f"{prefix}\n\n{system_prompt}"
    judge = RelevanceJudge(
        llm_client,
        system_prompt,
        format_user_prompt,
        config.name,
    )

    # Build correction judge
    if prefix_parts:
        prefix = "\n\n".join(prefix_parts)
        correction_system_prompt = f"{prefix}\n\n{CORRECTION_SYSTEM_PROMPT}"
    else:
        correction_system_prompt = CORRECTION_SYSTEM_PROMPT
    correction_judge = CorrectionJudge(
        llm_client, correction_system_prompt, config.name
    )

    try:
        backend.log_experiment(
            config.name,
            {
                "adapter_path": config.adapter_path,
                "llm_model": config.llm_model,
                "rubric": config.rubric,
                "top_k": config.top_k,
                "context": context,
                "vertical": vertical,
            },
        )
    except Exception as e:
        console.print(f"[yellow]Warning: failed to log experiment to backend: {e}")

    all_judgments: list[JudgmentRecord] = []
    all_checks: list[CheckResult] = []
    # Key by query-row index instead of raw query text so duplicate query
    # strings are evaluated as separate rows in metric aggregation.
    judgments_by_query: dict[int | str, list[JudgmentRecord]] = defaultdict(list)

    # Track queries with corrections for later LLM evaluation
    correction_entries: list[tuple[int, str, str]] = []  # (index, original, corrected)

    with Progress(console=console) as progress:
        task = progress.add_task(
            f"[cyan]Evaluating '{config.name}'...",
            total=len(queries),
        )

        for query_index, query_entry in enumerate(queries):
            # Step 1: Call adapter
            try:
                raw_response = adapter(query_entry.query)
                if isinstance(raw_response, SearchResponse):
                    response = raw_response
                else:
                    response = SearchResponse(results=raw_response)
                results = response.results[: config.top_k]
                corrected_query = response.corrected_query
                # Normalize empty strings to None
                if corrected_query is not None and not corrected_query.strip():
                    corrected_query = None
            except Exception as e:
                console.print(f"[red]Adapter error for '{query_entry.query}': {e}")
                progress.advance(task)
                continue

            # Step 2: Run deterministic checks
            checks = run_all_checks(query_entry, results, custom_checks=custom_checks)
            all_checks.extend(checks)

            # Step 2b: Run correction checks if corrected
            if corrected_query is not None:
                all_checks.append(
                    check_correction_vocabulary(
                        query_entry.query, corrected_query, results
                    )
                )
                all_checks.append(
                    check_unnecessary_correction(
                        query_entry.query, corrected_query, results
                    )
                )
                correction_entries.append(
                    (query_index, query_entry.query, corrected_query)
                )

            # Build failed-checks info per product.
            # A "failed check" is any deterministic check with passed=False
            # attached to a specific product row.
            failed_checks_by_product: dict[str, list[dict[str, str]]] = {}
            for check in checks:
                if not check.passed and check.product_id:
                    pid = check.product_id
                    failed_checks_by_product.setdefault(
                        pid,
                        [],
                    ).append(
                        {
                            "check_name": check.check_name,
                            "detail": check.detail,
                        }
                    )

            # Step 3: LLM judgment for each result
            for result in results:
                product_failed_checks = failed_checks_by_product.get(
                    result.product_id,
                    [],
                )

                try:
                    judgment = judge.judge(
                        query_entry.query,
                        result,
                        query_type=query_entry.type,
                        corrected_query=corrected_query,
                    )
                except Exception as e:
                    console.print(
                        f"[red]LLM error for '{query_entry.query}' / "
                        f"'{result.product_id}': {e}"
                    )
                    judgment = JudgmentRecord(
                        query=query_entry.query,
                        product=result,
                        score=0,
                        reasoning=f"Error: {e}",
                        attribute_verdict="n/a",
                        model=config.llm_model,
                        experiment=config.name,
                        query_type=query_entry.type,
                        metadata={"error": str(e)},
                    )
                # Annotate with check failures
                if product_failed_checks:
                    judgment.metadata["failed_checks"] = product_failed_checks
                # Annotate with corrected query
                if corrected_query is not None:
                    judgment.metadata["corrected_query"] = corrected_query

                try:
                    backend.log_judgment(judgment)
                except Exception as e:
                    console.print(
                        f"[yellow]Warning: failed to log judgment to backend: {e}"
                    )
                all_judgments.append(judgment)
                judgments_by_query[query_index].append(judgment)

            progress.advance(task)

    # Step 3b: Correction LLM evaluations
    all_correction_judgments: list[CorrectionJudgment] = []
    if correction_entries:
        with Progress(console=console) as progress:
            corr_task = progress.add_task(
                f"[cyan]Evaluating query corrections for '{config.name}'...",
                total=len(correction_entries),
            )
            for _idx, original, corrected in correction_entries:
                try:
                    cj = correction_judge.judge(original, corrected)
                except Exception as e:
                    console.print(
                        f"[red]Correction judge error for "
                        f"'{original}' -> '{corrected}': {e}"
                    )
                    cj = CorrectionJudgment(
                        original_query=original,
                        corrected_query=corrected,
                        verdict="error",
                        reasoning=f"Error: {e}",
                        model=config.llm_model,
                        experiment=config.name,
                        metadata={"error": str(e)},
                    )
                all_correction_judgments.append(cj)
                try:
                    backend.log_correction_judgment(cj)
                except Exception as e:
                    console.print(
                        f"[yellow]Warning: failed to log correction to backend: {e}"
                    )
                progress.advance(corr_task)

        # Console summary
        appropriate = sum(
            1 for cj in all_correction_judgments if cj.verdict == "appropriate"
        )
        inappropriate = sum(
            1 for cj in all_correction_judgments if cj.verdict == "inappropriate"
        )
        errored = sum(
            1
            for cj in all_correction_judgments
            if cj.verdict not in ("appropriate", "inappropriate")
        )
        n = len(all_correction_judgments)
        summary = (
            f"[bold]Corrections:[/bold] {n} queries corrected, "
            f"{appropriate} appropriate, {inappropriate} inappropriate"
        )
        if errored:
            summary += f", {errored} errored"
        summary += f" ({n} extra LLM calls)"
        console.print(summary)

    # Step 4: Compute metrics
    metrics = compute_all_metrics(judgments_by_query, queries)

    return all_judgments, all_checks, metrics, all_correction_judgments


def run_dual_evaluation(
    queries: list[QueryEntry],
    adapter_a: Callable[[str], SearchResponse | list[SearchResult]],
    config_a: ExperimentConfig,
    adapter_b: Callable[[str], SearchResponse | list[SearchResult]],
    config_b: ExperimentConfig,
    llm_client: LLMClient,
    rubric: tuple[str, Callable[..., str]],
    backend: EvalBackend,
    context: str | None = None,
    vertical: str | None = None,
    custom_checks: (
        list[Callable[[QueryEntry, list[SearchResult]], list[CheckResult]]] | None
    ) = None,
) -> tuple[
    list[JudgmentRecord],
    list[JudgmentRecord],
    list[CheckResult],
    list[CheckResult],
    list[MetricResult],
    list[MetricResult],
    list[CheckResult],
    list[CorrectionJudgment],
    list[CorrectionJudgment],
]:
    """Run evaluation for two configurations and generate comparison checks.

    Returns:
        Tuple of (judgments_a, judgments_b, checks_a, checks_b,
                  metrics_a, metrics_b, comparison_checks,
                  correction_judgments_a, correction_judgments_b)
    """
    console.print(
        f"\n[bold]Running dual evaluation: "
        f"'{config_a.name}' vs '{config_b.name}'[/bold]\n"
    )

    # Run evaluation for config A
    judgments_a, checks_a, metrics_a, corrections_a = run_evaluation(
        queries,
        adapter_a,
        config_a,
        llm_client,
        rubric,
        backend,
        context=context,
        vertical=vertical,
        custom_checks=custom_checks,
    )

    # Run evaluation for config B
    judgments_b, checks_b, metrics_b, corrections_b = run_evaluation(
        queries,
        adapter_b,
        config_b,
        llm_client,
        rubric,
        backend,
        context=context,
        vertical=vertical,
        custom_checks=custom_checks,
    )

    # Run comparison checks
    console.print("\n[cyan]Running comparison checks...[/cyan]")
    comparison_checks: list[CheckResult] = []

    # Collect results by query for comparison
    results_a_by_query: dict[str, list[SearchResult]] = defaultdict(list)
    results_b_by_query: dict[str, list[SearchResult]] = defaultdict(list)

    for j in judgments_a:
        results_a_by_query[j.query].append(j.product)
    for j in judgments_b:
        results_b_by_query[j.query].append(j.product)

    for query_entry in queries:
        q = query_entry.query
        ra = results_a_by_query.get(q, [])
        rb = results_b_by_query.get(q, [])

        try:
            comparison_checks.append(check_result_overlap(q, ra, rb))
            comparison_checks.append(check_rank_correlation(q, ra, rb))
            comparison_checks.extend(find_position_shifts(q, ra, rb))
        except Exception as e:
            console.print(f"[yellow]Warning: comparison check failed for '{q}': {e}")

    return (
        judgments_a,
        judgments_b,
        checks_a,
        checks_b,
        metrics_a,
        metrics_b,
        comparison_checks,
        corrections_a,
        corrections_b,
    )


def run_batch_evaluation(
    queries: list[QueryEntry],
    adapter: Callable[[str], SearchResponse | list[SearchResult]],
    config: ExperimentConfig,
    llm_client: LLMClient,
    rubric: tuple[str, Callable[..., str]],
    backend: EvalBackend,
    context: str | None = None,
    vertical: str | None = None,
    custom_checks: (
        list[Callable[[QueryEntry, list[SearchResult]], list[CheckResult]]] | None
    ) = None,
    poll_interval: int = 60,
) -> tuple[
    list[JudgmentRecord],
    list[CheckResult],
    list[MetricResult],
    list[CorrectionJudgment],
]:
    """Run a batch evaluation pipeline using the provider's batch API.

    Same as run_evaluation() but collects all LLM requests, submits them as a
    single batch, polls for completion, then processes results.
    """
    # Phase 0: Build judges (identical to run_evaluation)
    system_prompt, format_user_prompt = rubric
    prefix_parts: list[str] = []
    if context:
        prefix_parts.append(f"## Business Context\n{context}")
    if vertical:
        prefix_parts.append(vertical)
    if prefix_parts:
        prefix = "\n\n".join(prefix_parts)
        system_prompt = f"{prefix}\n\n{system_prompt}"
    judge = RelevanceJudge(
        llm_client,
        system_prompt,
        format_user_prompt,
        config.name,
    )

    if prefix_parts:
        prefix = "\n\n".join(prefix_parts)
        correction_system_prompt = f"{prefix}\n\n{CORRECTION_SYSTEM_PROMPT}"
    else:
        correction_system_prompt = CORRECTION_SYSTEM_PROMPT
    correction_judge = CorrectionJudge(
        llm_client, correction_system_prompt, config.name
    )

    try:
        backend.log_experiment(
            config.name,
            {
                "adapter_path": config.adapter_path,
                "llm_model": config.llm_model,
                "rubric": config.rubric,
                "top_k": config.top_k,
                "context": context,
                "vertical": vertical,
                "batch_mode": True,
            },
        )
    except Exception as e:
        console.print(f"[yellow]Warning: failed to log experiment to backend: {e}")

    # Phase 1: Collect — call adapters and build batch requests
    all_checks: list[CheckResult] = []
    batch_requests: list[BatchRequest] = []
    # Context for each request:
    # (query, result, query_type, corrected_query, failed_checks, query_index)
    request_context: dict[
        str,
        tuple[str, SearchResult, str | None, str | None, list[dict[str, str]], int],
    ] = {}
    correction_entries: list[tuple[int, str, str]] = []

    with Progress(console=console) as progress:
        task = progress.add_task(
            f"[cyan]Collecting requests for '{config.name}'...",
            total=len(queries),
        )

        for query_index, query_entry in enumerate(queries):
            try:
                raw_response = adapter(query_entry.query)
                if isinstance(raw_response, SearchResponse):
                    response = raw_response
                else:
                    response = SearchResponse(results=raw_response)
                results = response.results[: config.top_k]
                corrected_query = response.corrected_query
                if corrected_query is not None and not corrected_query.strip():
                    corrected_query = None
            except Exception as e:
                console.print(f"[red]Adapter error for '{query_entry.query}': {e}")
                progress.advance(task)
                continue

            # Deterministic checks
            checks = run_all_checks(query_entry, results, custom_checks=custom_checks)
            all_checks.extend(checks)

            # Correction checks
            if corrected_query is not None:
                all_checks.append(
                    check_correction_vocabulary(
                        query_entry.query, corrected_query, results
                    )
                )
                all_checks.append(
                    check_unnecessary_correction(
                        query_entry.query, corrected_query, results
                    )
                )
                correction_entries.append(
                    (query_index, query_entry.query, corrected_query)
                )

            # Failed checks by product
            failed_checks_by_product: dict[str, list[dict[str, str]]] = {}
            for check in checks:
                if not check.passed and check.product_id:
                    pid = check.product_id
                    failed_checks_by_product.setdefault(pid, []).append(
                        {
                            "check_name": check.check_name,
                            "detail": check.detail,
                        }
                    )

            # Build batch requests for each result
            for result_idx, result in enumerate(results):
                custom_id = f"rel:{query_index}:{result_idx}"
                product_failed_checks = failed_checks_by_product.get(
                    result.product_id, []
                )

                try:
                    batch_req = judge.prepare_request(
                        custom_id,
                        query_entry.query,
                        result,
                        corrected_query=corrected_query,
                    )
                    batch_requests.append(batch_req)
                    request_context[custom_id] = (
                        query_entry.query,
                        result,
                        query_entry.type,
                        corrected_query,
                        product_failed_checks,
                        query_index,
                    )
                except Exception as e:
                    console.print(
                        f"[red]Error preparing request for '{query_entry.query}' / "
                        f"'{result.product_id}': {e}"
                    )

            progress.advance(task)

    # Edge case: no requests
    if not batch_requests:
        metrics = compute_all_metrics({}, queries)
        return [], all_checks, metrics, []

    # Phase 2: Submit batch
    console.print(f"[cyan]Submitting batch of {len(batch_requests)} requests...[/cyan]")
    batch_id = llm_client.submit_batch(batch_requests)
    console.print(f"[dim]Batch ID: {batch_id}[/dim]")

    # Phase 3: Poll for completion
    with Progress(console=console) as progress:
        poll_task = progress.add_task(
            "[cyan]Waiting for batch completion...",
            total=len(batch_requests),
        )
        while True:
            status, completed, total = llm_client.poll_batch(batch_id)
            progress.update(
                poll_task, completed=completed, total=total or len(batch_requests)
            )

            if status == "completed":
                break
            if status in ("failed", "expired"):
                detail = llm_client.batch_error_message(batch_id)
                msg = f"Batch {batch_id} {status}."
                if detail:
                    msg += f" Error: {detail}"
                else:
                    msg += " Check your provider's dashboard for details."
                raise RuntimeError(msg)

            time.sleep(poll_interval)

    # Phase 4: Retrieve and map results
    console.print("[cyan]Retrieving batch results...[/cyan]")
    batch_results = llm_client.retrieve_batch_results(batch_id)
    results_by_id = {r.custom_id: r for r in batch_results}

    all_judgments: list[JudgmentRecord] = []
    judgments_by_query: dict[int | str, list[JudgmentRecord]] = defaultdict(list)

    for custom_id, ctx in request_context.items():
        (
            query,
            result,
            query_type,
            corrected_query,
            product_failed_checks,
            query_index,
        ) = ctx

        batch_result = results_by_id.get(custom_id)

        if batch_result and batch_result.response:
            try:
                judgment = judge.parse_batch_result(
                    batch_result.response, query, result, query_type=query_type
                )
            except Exception as e:
                judgment = JudgmentRecord(
                    query=query,
                    product=result,
                    score=0,
                    reasoning=f"Error parsing response: {e}",
                    attribute_verdict="n/a",
                    model=config.llm_model,
                    experiment=config.name,
                    query_type=query_type,
                    metadata={"error": str(e)},
                )
        else:
            error_msg = batch_result.error if batch_result else "No result returned"
            judgment = JudgmentRecord(
                query=query,
                product=result,
                score=0,
                reasoning=f"Batch error: {error_msg}",
                attribute_verdict="n/a",
                model=config.llm_model,
                experiment=config.name,
                query_type=query_type,
                metadata={"error": error_msg},
            )

        # Annotate with check failures
        if product_failed_checks:
            judgment.metadata["failed_checks"] = product_failed_checks
        # Annotate with corrected query
        if corrected_query is not None:
            judgment.metadata["corrected_query"] = corrected_query

        try:
            backend.log_judgment(judgment)
        except Exception as e:
            console.print(f"[yellow]Warning: failed to log judgment to backend: {e}")
        all_judgments.append(judgment)
        judgments_by_query[query_index].append(judgment)

    # Phase 5: Corrections batch
    all_correction_judgments: list[CorrectionJudgment] = []
    if correction_entries:
        corr_requests: list[BatchRequest] = []
        corr_context: dict[str, tuple[str, str]] = {}

        for idx, (_, original, corrected) in enumerate(correction_entries):
            custom_id = f"corr:{idx}"
            corr_req = correction_judge.prepare_request(custom_id, original, corrected)
            corr_requests.append(corr_req)
            corr_context[custom_id] = (original, corrected)

        console.print(
            f"[cyan]Submitting correction batch of "
            f"{len(corr_requests)} requests...[/cyan]"
        )
        corr_batch_id = llm_client.submit_batch(corr_requests)

        with Progress(console=console) as progress:
            corr_poll_task = progress.add_task(
                "[cyan]Waiting for correction batch...",
                total=len(corr_requests),
            )
            while True:
                status, completed, total = llm_client.poll_batch(corr_batch_id)
                progress.update(
                    corr_poll_task,
                    completed=completed,
                    total=total or len(corr_requests),
                )

                if status == "completed":
                    break
                if status in ("failed", "expired"):
                    detail = llm_client.batch_error_message(corr_batch_id)
                    msg = f"Correction batch {corr_batch_id} {status}."
                    if detail:
                        msg += f" Error: {detail}"
                    else:
                        msg += " Check your provider's dashboard for details."
                    raise RuntimeError(msg)

                time.sleep(poll_interval)

        corr_results = llm_client.retrieve_batch_results(corr_batch_id)
        corr_results_by_id = {r.custom_id: r for r in corr_results}

        for custom_id, (original, corrected) in corr_context.items():
            batch_result = corr_results_by_id.get(custom_id)

            if batch_result and batch_result.response:
                try:
                    cj = correction_judge.parse_batch_result(
                        batch_result.response, original, corrected
                    )
                except Exception as e:
                    cj = CorrectionJudgment(
                        original_query=original,
                        corrected_query=corrected,
                        verdict="error",
                        reasoning=f"Error: {e}",
                        model=config.llm_model,
                        experiment=config.name,
                        metadata={"error": str(e)},
                    )
            else:
                error_msg = batch_result.error if batch_result else "No result returned"
                cj = CorrectionJudgment(
                    original_query=original,
                    corrected_query=corrected,
                    verdict="error",
                    reasoning=f"Batch error: {error_msg}",
                    model=config.llm_model,
                    experiment=config.name,
                    metadata={"error": error_msg},
                )

            all_correction_judgments.append(cj)
            try:
                backend.log_correction_judgment(cj)
            except Exception as e:
                console.print(
                    f"[yellow]Warning: failed to log correction to backend: {e}"
                )

        # Console summary
        appropriate = sum(
            1 for cj in all_correction_judgments if cj.verdict == "appropriate"
        )
        inappropriate = sum(
            1 for cj in all_correction_judgments if cj.verdict == "inappropriate"
        )
        errored = sum(
            1
            for cj in all_correction_judgments
            if cj.verdict not in ("appropriate", "inappropriate")
        )
        n = len(all_correction_judgments)
        summary = (
            f"[bold]Corrections:[/bold] {n} queries corrected, "
            f"{appropriate} appropriate, {inappropriate} inappropriate"
        )
        if errored:
            summary += f", {errored} errored"
        console.print(summary)

    # Phase 6: Compute metrics
    metrics = compute_all_metrics(judgments_by_query, queries)

    return all_judgments, all_checks, metrics, all_correction_judgments


def run_dual_batch_evaluation(
    queries: list[QueryEntry],
    adapter_a: Callable[[str], SearchResponse | list[SearchResult]],
    config_a: ExperimentConfig,
    adapter_b: Callable[[str], SearchResponse | list[SearchResult]],
    config_b: ExperimentConfig,
    llm_client: LLMClient,
    rubric: tuple[str, Callable[..., str]],
    backend: EvalBackend,
    context: str | None = None,
    vertical: str | None = None,
    custom_checks: (
        list[Callable[[QueryEntry, list[SearchResult]], list[CheckResult]]] | None
    ) = None,
    poll_interval: int = 60,
) -> tuple[
    list[JudgmentRecord],
    list[JudgmentRecord],
    list[CheckResult],
    list[CheckResult],
    list[MetricResult],
    list[MetricResult],
    list[CheckResult],
    list[CorrectionJudgment],
    list[CorrectionJudgment],
]:
    """Run batch evaluation for two configurations and generate comparison checks."""
    console.print(
        f"\n[bold]Running dual batch evaluation: "
        f"'{config_a.name}' vs '{config_b.name}'[/bold]\n"
    )

    judgments_a, checks_a, metrics_a, corrections_a = run_batch_evaluation(
        queries,
        adapter_a,
        config_a,
        llm_client,
        rubric,
        backend,
        context=context,
        vertical=vertical,
        custom_checks=custom_checks,
        poll_interval=poll_interval,
    )

    judgments_b, checks_b, metrics_b, corrections_b = run_batch_evaluation(
        queries,
        adapter_b,
        config_b,
        llm_client,
        rubric,
        backend,
        context=context,
        vertical=vertical,
        custom_checks=custom_checks,
        poll_interval=poll_interval,
    )

    # Run comparison checks
    console.print("\n[cyan]Running comparison checks...[/cyan]")
    comparison_checks: list[CheckResult] = []

    results_a_by_query: dict[str, list[SearchResult]] = defaultdict(list)
    results_b_by_query: dict[str, list[SearchResult]] = defaultdict(list)

    for j in judgments_a:
        results_a_by_query[j.query].append(j.product)
    for j in judgments_b:
        results_b_by_query[j.query].append(j.product)

    for query_entry in queries:
        q = query_entry.query
        ra = results_a_by_query.get(q, [])
        rb = results_b_by_query.get(q, [])

        try:
            comparison_checks.append(check_result_overlap(q, ra, rb))
            comparison_checks.append(check_rank_correlation(q, ra, rb))
            comparison_checks.extend(find_position_shifts(q, ra, rb))
        except Exception as e:
            console.print(f"[yellow]Warning: comparison check failed for '{q}': {e}")

    return (
        judgments_a,
        judgments_b,
        checks_a,
        checks_b,
        metrics_a,
        metrics_b,
        comparison_checks,
        corrections_a,
        corrections_b,
    )
