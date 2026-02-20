"""Main evaluation pipeline orchestrator."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable
from dataclasses import asdict

from rich.console import Console
from rich.progress import Progress

from veritail.backends import EvalBackend
from veritail.batch_utils import poll_multiple_batches, poll_until_done
from veritail.checkpoint import (
    BatchCheckpoint,
    clear_checkpoint,
    deserialize_request_context,
    load_checkpoint,
    save_checkpoint,
    serialize_request_context,
)
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
from veritail.llm.classifier import (
    CLASSIFICATION_MAX_TOKENS,
    build_classification_system_prompt,
    classify_query_type,
    parse_classification_response,
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


def _classify_missing_query_types(
    queries: list[QueryEntry],
    llm_client: LLMClient,
    context: str | None,
    vertical: str | None,
) -> None:
    """Pre-pass: classify queries that have no type using a single LLM call each.

    Mutates query_entry.type in-place for entries where type is None.
    """
    missing = [(i, q) for i, q in enumerate(queries) if q.type is None]
    if not missing:
        return

    console.print(f"[cyan]Classifying {len(missing)} query type(s) via LLM...[/cyan]")
    classified = 0
    with Progress(console=console) as progress:
        task = progress.add_task(
            "[cyan]Classifying query types...",
            total=len(missing),
        )
        for _i, query_entry in missing:
            inferred = classify_query_type(
                llm_client, query_entry.query, context=context, vertical=vertical
            )
            if inferred is not None:
                query_entry.type = inferred
                classified += 1
            progress.advance(task)

    console.print(f"[dim]Classified {classified}/{len(missing)} queries[/dim]")


def _classify_missing_query_types_batch(
    queries: list[QueryEntry],
    llm_client: LLMClient,
    context: str | None,
    vertical: str | None,
    poll_interval: int,
) -> None:
    """Batch variant of query type classification.

    Submits all untyped queries as a single batch request, polls for
    completion, then parses and assigns types.  Falls back to the
    synchronous path when there are no missing types.
    """
    missing = [(i, q) for i, q in enumerate(queries) if q.type is None]
    if not missing:
        return

    system_prompt = build_classification_system_prompt(context, vertical)

    batch_requests: list[BatchRequest] = []
    for idx, query_entry in missing:
        batch_requests.append(
            BatchRequest(
                custom_id=f"cls-{idx}",
                system_prompt=system_prompt,
                user_prompt=f"Query: {query_entry.query}",
                max_tokens=CLASSIFICATION_MAX_TOKENS,
            )
        )

    console.print(
        f"[cyan]Submitting classification batch of "
        f"{len(batch_requests)} requests...[/cyan]"
    )
    batch_id = llm_client.submit_batch(batch_requests)

    poll_until_done(
        llm_client,
        batch_id,
        expected_total=len(batch_requests),
        poll_interval=poll_interval,
        label="Waiting for classification batch...",
    )

    batch_results = llm_client.retrieve_batch_results(batch_id)
    results_by_id = {r.custom_id: r for r in batch_results}

    classified = 0
    for idx, query_entry in missing:
        result = results_by_id.get(f"cls-{idx}")
        if result and result.response:
            inferred = parse_classification_response(result.response.content)
            if inferred is not None:
                query_entry.type = inferred
                classified += 1

    console.print(f"[dim]Classified {classified}/{len(missing)} queries[/dim]")


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
    resume: bool = False,
    output_dir: str = "./eval-results",
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
            resume=resume,
        )
    except Exception as e:
        console.print(f"[yellow]Warning: failed to log experiment to backend: {e}")

    # Pre-pass: classify query types that are missing
    _classify_missing_query_types(queries, llm_client, context, vertical)

    all_judgments: list[JudgmentRecord] = []
    all_checks: list[CheckResult] = []
    # Key by query-row index instead of raw query text so duplicate query
    # strings are evaluated as separate rows in metric aggregation.
    judgments_by_query: dict[int | str, list[JudgmentRecord]] = defaultdict(list)

    # Resume: reload existing judgments
    completed_indices: set[int] = set()
    if resume:
        completed_indices = backend.get_completed_query_indices(config.name)
        if completed_indices:
            existing = backend.get_judgments(config.name)
            for j in existing:
                qi = j.metadata.get("query_index")
                if qi is not None:
                    all_judgments.append(j)
                    judgments_by_query[int(qi)].append(j)
            remaining = len(queries) - len(completed_indices)
            console.print(
                f"[bold]Resuming: {len(completed_indices)} queries already "
                f"complete, {remaining} remaining[/bold]"
            )

    # Track queries with corrections for later LLM evaluation
    correction_entries: list[tuple[int, str, str]] = []  # (index, original, corrected)

    with Progress(console=console) as progress:
        task = progress.add_task(
            f"[cyan]Evaluating '{config.name}'...",
            total=len(queries),
        )

        for query_index, query_entry in enumerate(queries):
            # Skip already-completed queries on resume
            if query_index in completed_indices:
                progress.advance(task)
                continue

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
                # Always store query_index for resume support
                judgment.metadata["query_index"] = query_index

                try:
                    backend.log_judgment(judgment)
                except Exception as e:
                    console.print(
                        f"[yellow]Warning: failed to log judgment to backend: {e}"
                    )
                all_judgments.append(judgment)
                judgments_by_query[query_index].append(judgment)

            progress.advance(task)

    # Step 3b: Correction LLM evaluations (always re-run from scratch)
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
    resume: bool = False,
    output_dir: str = "./eval-results",
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
        resume=resume,
        output_dir=output_dir,
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
        resume=resume,
        output_dir=output_dir,
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
    resume: bool = False,
    output_dir: str = "./eval-results",
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
            resume=resume,
        )
    except Exception as e:
        console.print(f"[yellow]Warning: failed to log experiment to backend: {e}")

    # Pre-pass: classify query types that are missing (batched)
    _classify_missing_query_types_batch(
        queries, llm_client, context, vertical, poll_interval
    )

    # Check for existing checkpoint when resuming
    saved_checkpoint: BatchCheckpoint | None = None
    if resume:
        saved_checkpoint = load_checkpoint(output_dir, config.name)

    # ---- Resume path: skip Phase 1 & 2, jump to polling ----
    corr_batch_id: str | None = None
    corr_context: dict[str, tuple[str, str]] = {}

    if saved_checkpoint is not None:
        batch_id = saved_checkpoint.batch_id
        request_context = deserialize_request_context(saved_checkpoint.request_context)
        all_checks_data = saved_checkpoint.checks
        all_checks = [CheckResult(**c) for c in all_checks_data]
        correction_entries = [
            (int(e[0]), str(e[1]), str(e[2]))
            for e in saved_checkpoint.correction_entries
        ]
        # Restore Gemini custom_id ordering if needed
        if saved_checkpoint.gemini_custom_id_order:
            llm_client.restore_batch_custom_ids(
                batch_id, saved_checkpoint.gemini_custom_id_order
            )
        # Restore correction batch info
        corr_batch_id = saved_checkpoint.correction_batch_id
        if saved_checkpoint.correction_context:
            corr_context = {
                k: (v["original"], v["corrected"])
                for k, v in saved_checkpoint.correction_context.items()
            }
        if corr_batch_id and saved_checkpoint.gemini_correction_custom_id_order:
            llm_client.restore_batch_custom_ids(
                corr_batch_id, saved_checkpoint.gemini_correction_custom_id_order
            )

        # Re-submit correction batch if partial checkpoint (relevance submitted,
        # correction never submitted).
        if corr_batch_id is None and correction_entries:
            corr_requests: list[BatchRequest] = []
            for idx, (_, original, corrected) in enumerate(correction_entries):
                custom_id = f"corr-{idx}"
                corr_req = correction_judge.prepare_request(
                    custom_id, original, corrected
                )
                corr_requests.append(corr_req)
                corr_context[custom_id] = (original, corrected)

            console.print(
                f"[cyan]Submitting correction batch of "
                f"{len(corr_requests)} requests...[/cyan]"
            )
            corr_batch_id = llm_client.submit_batch(corr_requests)

            # Update checkpoint with correction info
            gemini_corr_order = getattr(llm_client, "_batch_custom_ids", {}).get(
                corr_batch_id, []
            )
            save_checkpoint(
                output_dir,
                config.name,
                BatchCheckpoint(
                    batch_id=batch_id,
                    experiment_name=config.name,
                    phase="relevance",
                    request_context=saved_checkpoint.request_context,
                    checks=saved_checkpoint.checks,
                    correction_entries=saved_checkpoint.correction_entries,
                    gemini_custom_id_order=saved_checkpoint.gemini_custom_id_order,
                    correction_batch_id=corr_batch_id,
                    correction_context={
                        k: {"original": v[0], "corrected": v[1]}
                        for k, v in corr_context.items()
                    },
                    gemini_correction_custom_id_order=gemini_corr_order,
                ),
            )

        console.print(f"[bold]Resuming batch {batch_id} for '{config.name}'...[/bold]")
    else:
        # Phase 1: Collect — call adapters and build batch requests
        all_checks = []
        batch_requests: list[BatchRequest] = []
        request_context = {}
        correction_entries = []

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
                checks = run_all_checks(
                    query_entry, results, custom_checks=custom_checks
                )
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
                    custom_id = f"rel-{query_index}-{result_idx}"
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
                            f"[red]Error preparing request for "
                            f"'{query_entry.query}' / '{result.product_id}': {e}"
                        )

                progress.advance(task)

        # Edge case: no requests
        if not batch_requests:
            metrics = compute_all_metrics({}, queries)
            return [], all_checks, metrics, []

        # Build correction batch requests upfront (inputs available after Phase 1)
        corr_requests = []
        if correction_entries:
            for idx, (_, original, corrected) in enumerate(correction_entries):
                custom_id = f"corr-{idx}"
                corr_req = correction_judge.prepare_request(
                    custom_id, original, corrected
                )
                corr_requests.append(corr_req)
                corr_context[custom_id] = (original, corrected)

        # Phase 2: Submit batches
        console.print(
            f"[cyan]Submitting batch of {len(batch_requests)} requests...[/cyan]"
        )
        batch_id = llm_client.submit_batch(batch_requests)
        console.print(f"[dim]Batch ID: {batch_id}[/dim]")

        # Save partial checkpoint immediately so the relevance batch ID
        # survives even if the correction submit below raises.
        gemini_order = getattr(llm_client, "_batch_custom_ids", {}).get(batch_id, [])
        serialized_req_ctx = serialize_request_context(request_context)
        serialized_checks = [asdict(c) for c in all_checks]
        serialized_corr_entries = [
            [idx, orig, corr] for idx, orig, corr in correction_entries
        ]
        save_checkpoint(
            output_dir,
            config.name,
            BatchCheckpoint(
                batch_id=batch_id,
                experiment_name=config.name,
                phase="relevance",
                request_context=serialized_req_ctx,
                checks=serialized_checks,
                correction_entries=serialized_corr_entries,
                gemini_custom_id_order=gemini_order,
                correction_batch_id=None,
                correction_context=None,
                gemini_correction_custom_id_order=[],
            ),
        )

        if corr_requests:
            console.print(
                f"[cyan]Submitting correction batch of "
                f"{len(corr_requests)} requests...[/cyan]"
            )
            corr_batch_id = llm_client.submit_batch(corr_requests)

            # Update checkpoint with correction batch info
            gemini_corr_order = getattr(llm_client, "_batch_custom_ids", {}).get(
                corr_batch_id, []
            )
            save_checkpoint(
                output_dir,
                config.name,
                BatchCheckpoint(
                    batch_id=batch_id,
                    experiment_name=config.name,
                    phase="relevance",
                    request_context=serialized_req_ctx,
                    checks=serialized_checks,
                    correction_entries=serialized_corr_entries,
                    gemini_custom_id_order=gemini_order,
                    correction_batch_id=corr_batch_id,
                    correction_context={
                        k: {"original": v[0], "corrected": v[1]}
                        for k, v in corr_context.items()
                    },
                    gemini_correction_custom_id_order=gemini_corr_order,
                ),
            )

    # Phase 3: Poll for completion (both batches together)
    poll_entries: list[tuple[str, int, str]] = [
        (batch_id, len(request_context), "Waiting for relevance batch..."),
    ]
    if corr_batch_id:
        poll_entries.append(
            (corr_batch_id, len(corr_context), "Waiting for correction batch..."),
        )

    try:
        poll_multiple_batches(
            llm_client,
            poll_entries,
            poll_interval=poll_interval,
        )
    except RuntimeError as exc:
        clear_checkpoint(output_dir, config.name)
        msg = str(exc)
        if resume:
            msg += (
                " Checkpoint cleared — re-run without --resume to start a fresh batch."
            )
        raise RuntimeError(msg) from exc

    # Phase 4: Retrieve and map relevance results
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
        # Store query_index for resume support
        judgment.metadata["query_index"] = query_index

        try:
            backend.log_judgment(judgment)
        except Exception as e:
            console.print(f"[yellow]Warning: failed to log judgment to backend: {e}")
        all_judgments.append(judgment)
        judgments_by_query[query_index].append(judgment)

    # Phase 5: Retrieve correction results (already submitted & polled above)
    all_correction_judgments: list[CorrectionJudgment] = []
    if corr_batch_id and corr_context:
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

    # Clear checkpoint on success
    clear_checkpoint(output_dir, config.name)

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
    resume: bool = False,
    output_dir: str = "./eval-results",
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
        resume=resume,
        output_dir=output_dir,
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
        resume=resume,
        output_dir=output_dir,
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
