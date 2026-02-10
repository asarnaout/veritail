"""CLI interface for veritail."""

from __future__ import annotations

from pathlib import Path

import click
from dotenv import load_dotenv
from rich.console import Console

from veritail.adapter import load_adapter
from veritail.backends import create_backend
from veritail.llm.client import create_llm_client
from veritail.pipeline import run_dual_evaluation, run_evaluation
from veritail.queries import load_queries
from veritail.reporting.comparison import generate_comparison_report
from veritail.reporting.single import generate_single_report
from veritail.rubrics import load_rubric
from veritail.types import ExperimentConfig

console = Console()

# Load environment variables from .env file if it exists
# Search in current directory, then parent directories
load_dotenv(verbose=False, override=False)


@click.group()
@click.version_option(package_name="veritail")
def main() -> None:
    """veritail: Ecommerce search relevance evaluation tool."""
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
@click.option("--open", "open_browser", is_flag=True, default=False,
              help="Generate an HTML report and open it in the browser when complete.")
@click.option("--skip-on-check-fail/--no-skip-on-check-fail", default=False,
              help="Skip LLM judgment when a deterministic check fails (default: always run LLM).")
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
    open_browser: bool,
    skip_on_check_fail: bool,
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
            skip_llm_on_fail=skip_on_check_fail,
        )

        report = generate_single_report(metrics, checks)
        console.print(report)

        if open_browser:
            html = generate_single_report(metrics, checks, judgments=judgments, format="html")
            html_path = Path(output_dir) / config_names[0] / "report.html"
            html_path.write_text(html, encoding="utf-8")
            console.print(f"[dim]HTML report ->{html_path}[/dim]")
            import webbrowser
            webbrowser.open(html_path.resolve().as_uri())

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
            skip_llm_on_fail=skip_on_check_fail,
        )

        report = generate_comparison_report(
            metrics_a, metrics_b,
            comparison_checks,
            config_names[0], config_names[1],
        )
        console.print(report)

        if open_browser:
            html = generate_comparison_report(
                metrics_a, metrics_b,
                comparison_checks,
                config_names[0], config_names[1],
                format="html",
            )
            html_path = Path(output_dir) / f"{config_names[0]}_vs_{config_names[1]}" / "report.html"
            html_path.parent.mkdir(parents=True, exist_ok=True)
            html_path.write_text(html, encoding="utf-8")
            console.print(f"[dim]HTML report ->{html_path}[/dim]")
            import webbrowser
            webbrowser.open(html_path.resolve().as_uri())


@main.command()
@click.option("--experiment", required=True, help="Experiment name")
@click.option("--baseline", default=None, help="Baseline experiment name (for comparison)")
@click.option("--output", "output_path", default=None, type=click.Path(), help="Output file path (HTML)")
@click.option("--backend", "backend_type", default="file", type=click.Choice(["file", "langfuse"]))
@click.option("--output-dir", default="./eval-results", help="Output directory (file backend)")
@click.option("--backend-url", default=None, help="Backend URL (langfuse backend)")
@click.option("--open", "open_browser", is_flag=True, default=False,
              help="Open the HTML report in the browser when complete.")
def report(
    experiment: str,
    baseline: str | None,
    output_path: str | None,
    backend_type: str,
    output_dir: str,
    backend_url: str | None,
    open_browser: bool,
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
    from veritail.metrics.ir import compute_all_metrics

    judgments_by_query: dict[str, list] = defaultdict(list)
    for j in judgments:
        judgments_by_query[j.query].append(j)

    # Use empty query entries (no type info available from stored data)
    from veritail.types import QueryEntry
    query_entries = [QueryEntry(query=q) for q in judgments_by_query]
    metrics = compute_all_metrics(judgments_by_query, query_entries)

    needs_html = open_browser or (output_path is not None and output_path.endswith(".html"))
    output_format = "html" if needs_html else "terminal"

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
        report_str = generate_single_report(
            metrics, [], format=output_format,
            judgments=judgments if output_format == "html" else None,
        )

    if output_path:
        Path(output_path).write_text(report_str, encoding="utf-8")
        console.print(f"Report written to {output_path}")
        if open_browser:
            import webbrowser
            webbrowser.open(Path(output_path).resolve().as_uri())
    elif open_browser:
        html_path = Path(output_dir) / experiment / "report.html"
        html_path.write_text(report_str, encoding="utf-8")
        console.print(f"[dim]HTML report ->{html_path}[/dim]")
        import webbrowser
        webbrowser.open(html_path.resolve().as_uri())
    else:
        console.print(report_str)


if __name__ == "__main__":
    main()
