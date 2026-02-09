"""CLI interface for search-eval."""

from __future__ import annotations

from pathlib import Path

import click
from rich.console import Console

from search_eval.adapter import load_adapter
from search_eval.backends import create_backend
from search_eval.llm.client import create_llm_client
from search_eval.metrics.agreement import compute_agreement
from search_eval.pipeline import run_dual_evaluation, run_evaluation
from search_eval.queries import load_queries
from search_eval.reporting.comparison import generate_comparison_report
from search_eval.reporting.single import generate_single_report
from search_eval.rubrics import load_rubric
from search_eval.types import ExperimentConfig

console = Console()


@click.group()
@click.version_option(package_name="search-eval")
def main() -> None:
    """search-eval: Ecommerce search relevance evaluation tool."""
    pass


@main.command()
@click.option("--queries", required=True, type=click.Path(exists=True), help="Path to query set (CSV or JSON)")
@click.option("--adapter", "adapters", required=True, multiple=True, type=click.Path(exists=True), help="Path to search adapter module(s)")
@click.option("--config-name", "config_names", required=True, multiple=True, help="Name for each configuration")
@click.option("--llm-model", default="claude-sonnet-4-5", help="LLM model to use for judgments")
@click.option("--rubric", default="ecommerce-default", help="Rubric name or path to custom rubric module")
@click.option("--backend", "backend_type", default="file", type=click.Choice(["file", "langfuse"]), help="Evaluation backend")
@click.option("--output-dir", default="./eval-results", help="Output directory (file backend)")
@click.option("--backend-url", default=None, help="Backend URL (langfuse backend)")
@click.option("--top-k", default=10, type=int, help="Number of results to retrieve per query")
def run(
    queries: str,
    adapters: tuple[str, ...],
    config_names: tuple[str, ...],
    llm_model: str,
    rubric: str,
    backend_type: str,
    output_dir: str,
    backend_url: str | None,
    top_k: int,
) -> None:
    """Run evaluation (single or dual configuration)."""
    if len(adapters) != len(config_names):
        raise click.UsageError(
            f"Each --adapter must have a matching --config-name. "
            f"Got {len(adapters)} adapter(s) and {len(config_names)} config name(s)."
        )

    if len(adapters) > 2:
        raise click.UsageError("At most 2 adapter/config-name pairs are supported.")

    query_entries = load_queries(queries)
    console.print(f"Loaded {len(query_entries)} queries from {queries}")

    rubric_data = load_rubric(rubric)
    llm_client = create_llm_client(llm_model)

    backend_kwargs: dict = {}
    if backend_type == "file":
        backend_kwargs["output_dir"] = output_dir
    elif backend_type == "langfuse":
        if backend_url:
            backend_kwargs["url"] = backend_url

    backend = create_backend(backend_type, **backend_kwargs)

    if len(adapters) == 1:
        # Single configuration
        config = ExperimentConfig(
            name=config_names[0],
            adapter_path=adapters[0],
            llm_model=llm_model,
            rubric=rubric,
            top_k=top_k,
        )
        adapter_fn = load_adapter(adapters[0])

        judgments, checks, metrics = run_evaluation(
            query_entries, adapter_fn, config, llm_client, rubric_data, backend,
        )

        report = generate_single_report(metrics, checks)
        console.print(report)

    else:
        # Dual configuration
        config_a = ExperimentConfig(
            name=config_names[0],
            adapter_path=adapters[0],
            llm_model=llm_model,
            rubric=rubric,
            top_k=top_k,
        )
        config_b = ExperimentConfig(
            name=config_names[1],
            adapter_path=adapters[1],
            llm_model=llm_model,
            rubric=rubric,
            top_k=top_k,
        )
        adapter_a = load_adapter(adapters[0])
        adapter_b = load_adapter(adapters[1])

        (
            judgments_a, judgments_b,
            checks_a, checks_b,
            metrics_a, metrics_b,
            comparison_checks,
        ) = run_dual_evaluation(
            query_entries,
            adapter_a, config_a,
            adapter_b, config_b,
            llm_client, rubric_data, backend,
        )

        report = generate_comparison_report(
            metrics_a, metrics_b,
            comparison_checks,
            config_names[0], config_names[1],
        )
        console.print(report)


@main.command()
@click.option("--experiment", required=True, help="Experiment name")
@click.option("--baseline", default=None, help="Baseline experiment name (for comparison)")
@click.option("--include-human-agreement", is_flag=True, help="Include LLM-human agreement analysis")
@click.option("--output", "output_path", default=None, type=click.Path(), help="Output file path (HTML)")
@click.option("--backend", "backend_type", default="file", type=click.Choice(["file", "langfuse"]))
@click.option("--output-dir", default="./eval-results", help="Output directory (file backend)")
@click.option("--backend-url", default=None, help="Backend URL (langfuse backend)")
def report(
    experiment: str,
    baseline: str | None,
    include_human_agreement: bool,
    output_path: str | None,
    backend_type: str,
    output_dir: str,
    backend_url: str | None,
) -> None:
    """Generate report from existing evaluation results."""
    backend_kwargs: dict = {}
    if backend_type == "file":
        backend_kwargs["output_dir"] = output_dir
    elif backend_type == "langfuse" and backend_url:
        backend_kwargs["url"] = backend_url

    backend = create_backend(backend_type, **backend_kwargs)

    judgments = backend.get_judgments(experiment)
    if not judgments:
        console.print(f"[red]No judgments found for experiment '{experiment}'")
        raise SystemExit(1)

    from collections import defaultdict
    from search_eval.metrics.ir import compute_all_metrics

    judgments_by_query: dict[str, list] = defaultdict(list)
    for j in judgments:
        judgments_by_query[j.query].append(j)

    # Use empty query entries (no type info available from stored data)
    from search_eval.types import QueryEntry
    query_entries = [QueryEntry(query=q) for q in judgments_by_query]
    metrics = compute_all_metrics(judgments_by_query, query_entries)

    agreement = None
    if include_human_agreement:
        human_scores = backend.get_human_scores(experiment)
        if human_scores:
            agreement = compute_agreement(judgments, human_scores)
        else:
            console.print("[yellow]No human scores found for agreement computation")

    output_format = "html" if output_path and output_path.endswith(".html") else "terminal"

    if baseline:
        baseline_judgments = backend.get_judgments(baseline)
        if not baseline_judgments:
            console.print(f"[red]No judgments found for baseline '{baseline}'")
            raise SystemExit(1)

        baseline_by_query: dict[str, list] = defaultdict(list)
        for j in baseline_judgments:
            baseline_by_query[j.query].append(j)

        baseline_entries = [QueryEntry(query=q) for q in baseline_by_query]
        baseline_metrics = compute_all_metrics(baseline_by_query, baseline_entries)

        report_str = generate_comparison_report(
            baseline_metrics, metrics, [], baseline, experiment, format=output_format,
        )
    else:
        report_str = generate_single_report(metrics, [], agreement=agreement, format=output_format)

    if output_path:
        Path(output_path).write_text(report_str, encoding="utf-8")
        console.print(f"Report written to {output_path}")
    else:
        console.print(report_str)


@main.command()
@click.option("--experiment", required=True, help="Experiment name")
@click.option("--sample-rate", default=0.10, type=float, help="Fraction of judgments to sample for review")
@click.option("--strategy", default="random", type=click.Choice(["random", "stratified"]), help="Sampling strategy")
@click.option("--backend", "backend_type", default="file", type=click.Choice(["file", "langfuse"]))
@click.option("--output-dir", default="./eval-results", help="Output directory (file backend)")
@click.option("--backend-url", default=None, help="Backend URL (langfuse backend)")
def review(
    experiment: str,
    sample_rate: float,
    strategy: str,
    backend_type: str,
    output_dir: str,
    backend_url: str | None,
) -> None:
    """Create human review annotation queue from evaluation results."""
    backend_kwargs: dict = {}
    if backend_type == "file":
        backend_kwargs["output_dir"] = output_dir
    elif backend_type == "langfuse" and backend_url:
        backend_kwargs["url"] = backend_url

    backend = create_backend(backend_type, **backend_kwargs)
    backend.create_review_queue(experiment, sample_rate, strategy)

    console.print(
        f"Review queue created for '{experiment}' "
        f"(sample rate: {sample_rate:.0%}, strategy: {strategy})"
    )


@main.command()
@click.option("--experiment", required=True, help="Experiment name")
@click.option("--backend", "backend_type", default="file", type=click.Choice(["file", "langfuse"]))
@click.option("--output-dir", default="./eval-results", help="Output directory (file backend)")
@click.option("--backend-url", default=None, help="Backend URL (langfuse backend)")
def agreement(
    experiment: str,
    backend_type: str,
    output_dir: str,
    backend_url: str | None,
) -> None:
    """Compute inter-rater agreement between LLM and human scores."""
    backend_kwargs: dict = {}
    if backend_type == "file":
        backend_kwargs["output_dir"] = output_dir
    elif backend_type == "langfuse" and backend_url:
        backend_kwargs["url"] = backend_url

    backend = create_backend(backend_type, **backend_kwargs)

    judgments = backend.get_judgments(experiment)
    human_scores = backend.get_human_scores(experiment)

    if not judgments:
        console.print(f"[red]No LLM judgments found for experiment '{experiment}'")
        raise SystemExit(1)

    if not human_scores:
        console.print(f"[red]No human scores found for experiment '{experiment}'")
        console.print(
            "Run 'search-eval review' first to create a review queue, "
            "then fill in human scores."
        )
        raise SystemExit(1)

    result = compute_agreement(judgments, human_scores)

    console.print(f"\n[bold]Inter-Rater Agreement: '{experiment}'[/bold]\n")
    console.print(f"  Cohen's kappa:    {result['kappa']:.3f}")
    console.print(f"  Matched pairs:    {result['n_matched']}")
    console.print(f"  Exact agreement:  {result['agreement_rate']:.1%}")
    console.print(f"  Calibration:      {result['calibration']}")
    console.print()
