"""Main evaluation pipeline orchestrator."""

from __future__ import annotations

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
from veritail.llm.client import LLMClient
from veritail.llm.judge import RelevanceJudge
from veritail.metrics.ir import compute_all_metrics
from veritail.types import (
    CheckResult,
    ExperimentConfig,
    JudgmentRecord,
    MetricResult,
    QueryEntry,
    SearchResult,
)

console = Console()


def run_evaluation(
    queries: list[QueryEntry],
    adapter: Callable[[str], list[SearchResult]],
    config: ExperimentConfig,
    llm_client: LLMClient,
    rubric: tuple[str, Callable[[str, SearchResult], str]],
    backend: EvalBackend,
    skip_llm_on_fail: bool = False,
    context: str | None = None,
    vertical: str | None = None,
    custom_checks: (
        list[Callable[[QueryEntry, list[SearchResult]], list[CheckResult]]] | None
    ) = None,
) -> tuple[list[JudgmentRecord], list[CheckResult], list[MetricResult]]:
    """Run a full evaluation pipeline for a single configuration.

    Steps:
        1. Log the experiment
        2. For each query: call adapter, run checks, judge with LLM, log results
        3. Compute IR metrics

    Returns:
        Tuple of (judgments, check_results, metrics)
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

    all_judgments: list[JudgmentRecord] = []
    all_checks: list[CheckResult] = []
    # Key by query-row index instead of raw query text so duplicate query
    # strings are evaluated as separate rows in metric aggregation.
    judgments_by_query: dict[int | str, list[JudgmentRecord]] = defaultdict(list)

    with Progress(console=console) as progress:
        task = progress.add_task(
            f"[cyan]Evaluating '{config.name}'...",
            total=len(queries),
        )

        for query_index, query_entry in enumerate(queries):
            # Step 1: Call adapter
            try:
                results = adapter(query_entry.query)[: config.top_k]
            except Exception as e:
                console.print(f"[red]Adapter error for '{query_entry.query}': {e}")
                progress.advance(task)
                continue

            # Step 2: Run deterministic checks
            checks = run_all_checks(query_entry, results, custom_checks=custom_checks)
            all_checks.extend(checks)

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

            # Build the skip set (only when skip_llm_on_fail=True)
            failed_product_ids: set[str] = set()
            if skip_llm_on_fail:
                failed_product_ids = set(failed_checks_by_product.keys())

            # Step 3: LLM judgment for each result
            for result in results:
                product_failed_checks = failed_checks_by_product.get(
                    result.product_id,
                    [],
                )

                if result.product_id in failed_product_ids:
                    # Skip LLM — build a descriptive reasoning string
                    reasons = "; ".join(
                        f"[{fc['check_name']}] {fc['detail']}"
                        for fc in product_failed_checks
                    )
                    judgment = JudgmentRecord(
                        query=query_entry.query,
                        product=result,
                        score=0,
                        reasoning=f"Skipped: {reasons}",
                        attribute_verdict="n/a",
                        model=config.llm_model,
                        experiment=config.name,
                        query_type=query_entry.type,
                        metadata={
                            "skipped": True,
                            "failed_checks": product_failed_checks,
                        },
                    )
                else:
                    try:
                        judgment = judge.judge(
                            query_entry.query,
                            result,
                            query_type=query_entry.type,
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
                    # Annotate with check failures even when LLM ran
                    if product_failed_checks:
                        judgment.metadata["failed_checks"] = product_failed_checks

                backend.log_judgment(judgment)
                all_judgments.append(judgment)
                judgments_by_query[query_index].append(judgment)

            progress.advance(task)

    # Step 4: Compute metrics
    metrics = compute_all_metrics(judgments_by_query, queries)

    return all_judgments, all_checks, metrics


def run_dual_evaluation(
    queries: list[QueryEntry],
    adapter_a: Callable[[str], list[SearchResult]],
    config_a: ExperimentConfig,
    adapter_b: Callable[[str], list[SearchResult]],
    config_b: ExperimentConfig,
    llm_client: LLMClient,
    rubric: tuple[str, Callable[[str, SearchResult], str]],
    backend: EvalBackend,
    skip_llm_on_fail: bool = False,
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
]:
    """Run evaluation for two configurations and generate comparison checks.

    Returns:
        Tuple of (judgments_a, judgments_b, checks_a, checks_b,
                  metrics_a, metrics_b, comparison_checks)
    """
    console.print(
        f"\n[bold]Running dual evaluation: "
        f"'{config_a.name}' vs '{config_b.name}'[/bold]\n"
    )

    # Run evaluation for config A
    judgments_a, checks_a, metrics_a = run_evaluation(
        queries,
        adapter_a,
        config_a,
        llm_client,
        rubric,
        backend,
        skip_llm_on_fail=skip_llm_on_fail,
        context=context,
        vertical=vertical,
        custom_checks=custom_checks,
    )

    # Run evaluation for config B
    judgments_b, checks_b, metrics_b = run_evaluation(
        queries,
        adapter_b,
        config_b,
        llm_client,
        rubric,
        backend,
        skip_llm_on_fail=skip_llm_on_fail,
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

        comparison_checks.append(check_result_overlap(q, ra, rb))
        comparison_checks.append(check_rank_correlation(q, ra, rb))
        comparison_checks.extend(find_position_shifts(q, ra, rb))

    return (
        judgments_a,
        judgments_b,
        checks_a,
        checks_b,
        metrics_a,
        metrics_b,
        comparison_checks,
    )
