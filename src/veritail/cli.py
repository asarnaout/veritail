"""CLI interface for veritail."""

from __future__ import annotations

import json
import re
from dataclasses import asdict
from datetime import datetime, timezone
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


def _slugify_name(raw: str) -> str:
    """Create a filesystem-safe slug for generated config names."""
    slug = re.sub(r"[^a-z0-9]+", "-", raw.lower()).strip("-")
    return slug or "config"


def _generate_config_names(adapters: tuple[str, ...]) -> tuple[str, ...]:
    """Generate readable, unique config names from adapter paths."""
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    seen: dict[str, int] = {}
    generated: list[str] = []

    for adapter in adapters:
        base = _slugify_name(Path(adapter).stem)
        seen[base] = seen.get(base, 0) + 1
        suffix = f"-{seen[base]}" if seen[base] > 1 else ""
        generated.append(f"{base}{suffix}-{timestamp}")

    return tuple(generated)


@click.group()
@click.version_option(package_name="veritail")
def main() -> None:
    """veritail: Ecommerce search relevance evaluation tool."""
    pass


@main.command()
@click.option("--queries", required=True, type=click.Path(exists=True), help="Path to query set (CSV or JSON)")
@click.option("--adapter", "adapters", required=True, multiple=True, type=click.Path(exists=True), help="Path to search adapter module(s)")
@click.option(
    "--config-name",
    "config_names",
    multiple=True,
    help=(
        "Optional name for each configuration. "
        "Provide one per adapter, or omit to auto-generate names."
    ),
)
@click.option("--llm-model", default="claude-sonnet-4-5", help="LLM model to use for judgments")
@click.option("--rubric", default="ecommerce-default", help="Rubric name or path to custom rubric module")
@click.option("--backend", "backend_type", default="file", type=click.Choice(["file", "langfuse"]), help="Evaluation backend")
@click.option("--output-dir", default="./eval-results", help="Output directory (file backend)")
@click.option("--backend-url", default=None, help="Backend URL (langfuse backend)")
@click.option("--top-k", default=10, type=int, help="Number of results to retrieve per query")
@click.option("--open", "open_browser", is_flag=True, default=False,
              help="Open the HTML report in the browser when complete.")
@click.option("--skip-on-check-fail/--no-skip-on-check-fail", default=False,
              help="Skip LLM judgment when a deterministic check fails (default: always run LLM).")
@click.option("--context", default=None, type=str,
              help="Business context for the LLM judge (e.g. 'B2B industrial kitchen equipment supplier').")
@click.option("--vertical", default=None, type=str,
              help="Vertical for domain-specific scoring guidance (built-in: foodservice, industrial, electronics, fashion, case-insensitive; or path to a text file).")
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
    context: str | None,
    vertical: str | None,
) -> None:
    """Run evaluation (single or dual configuration)."""
    if config_names and len(adapters) != len(config_names):
        raise click.UsageError(
            "Each --adapter must have a matching --config-name when names are provided. "
            f"Got {len(adapters)} adapter(s) and {len(config_names)} config name(s). "
            "Or omit --config-name to auto-generate names."
        )

    if len(adapters) > 2:
        raise click.UsageError("At most 2 adapter/config-name pairs are supported.")

    if not config_names:
        config_names = _generate_config_names(adapters)
        console.print(
            "[dim]No --config-name provided. Using generated names: "
            f"{', '.join(config_names)}[/dim]",
        )

    query_entries = load_queries(queries)
    console.print(f"Loaded {len(query_entries)} queries from {queries}")

    rubric_data = load_rubric(rubric)

    vertical_context: str | None = None
    if vertical:
        from veritail.verticals import load_vertical
        vertical_context = load_vertical(vertical)

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
            context=context,
            vertical=vertical_context,
        )

        report = generate_single_report(metrics, checks)
        console.print(report)

        exp_dir = Path(output_dir) / config_names[0]
        exp_dir.mkdir(parents=True, exist_ok=True)

        metrics_path = exp_dir / "metrics.json"
        metrics_path.write_text(
            json.dumps([asdict(m) for m in metrics], indent=2, default=str),
            encoding="utf-8",
        )

        html = generate_single_report(metrics, checks, judgments=judgments, format="html")
        html_path = exp_dir / "report.html"
        html_path.write_text(html, encoding="utf-8")
        console.print(f"[dim]HTML report -> {html_path}[/dim]")

        if open_browser:
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
            context=context,
            vertical=vertical_context,
        )

        report = generate_comparison_report(
            metrics_a, metrics_b,
            comparison_checks,
            config_names[0], config_names[1],
        )
        console.print(report)

        for cfg_name, cfg_metrics in [(config_names[0], metrics_a), (config_names[1], metrics_b)]:
            exp_dir = Path(output_dir) / cfg_name
            exp_dir.mkdir(parents=True, exist_ok=True)
            metrics_path = exp_dir / "metrics.json"
            metrics_path.write_text(
                json.dumps([asdict(m) for m in cfg_metrics], indent=2, default=str),
                encoding="utf-8",
            )

        html = generate_comparison_report(
            metrics_a, metrics_b,
            comparison_checks,
            config_names[0], config_names[1],
            format="html",
        )
        html_path = Path(output_dir) / f"{config_names[0]}_vs_{config_names[1]}" / "report.html"
        html_path.parent.mkdir(parents=True, exist_ok=True)
        html_path.write_text(html, encoding="utf-8")
        console.print(f"[dim]HTML report -> {html_path}[/dim]")

        if open_browser:
            import webbrowser
            webbrowser.open(html_path.resolve().as_uri())


if __name__ == "__main__":
    main()
