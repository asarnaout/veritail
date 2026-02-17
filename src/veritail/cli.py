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
from veritail.checks.custom import CustomCheckFn, load_checks
from veritail.llm.client import create_llm_client
from veritail.pipeline import run_dual_evaluation, run_evaluation
from veritail.queries import load_queries
from veritail.reporting.comparison import generate_comparison_report
from veritail.reporting.single import generate_single_report
from veritail.rubrics import load_rubric
from veritail.scaffold import (
    DEFAULT_ADAPTER_FILENAME,
    DEFAULT_QUERIES_FILENAME,
    scaffold_project,
)
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


def _build_run_metadata(
    *,
    llm_model: str,
    rubric: str,
    vertical: str | None,
    top_k: int,
    sample: int | None = None,
    total_queries: int | None = None,
    adapter_path: str | None = None,
    adapter_path_a: str | None = None,
    adapter_path_b: str | None = None,
) -> dict[str, object]:
    """Build provenance metadata for report rendering."""
    metadata: dict[str, object] = {
        "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "llm_model": llm_model,
        "rubric": rubric,
        "vertical": vertical if vertical else "none",
        "top_k": top_k,
    }
    if sample is not None and total_queries is not None:
        metadata["sample"] = f"{sample} of {total_queries}"
    if adapter_path is not None:
        metadata["adapter_path"] = adapter_path
    if adapter_path_a is not None:
        metadata["adapter_path_a"] = adapter_path_a
    if adapter_path_b is not None:
        metadata["adapter_path_b"] = adapter_path_b
    return metadata


@click.group()
@click.version_option(package_name="veritail")
def main() -> None:
    """veritail: Ecommerce search relevance evaluation tool."""
    pass


@main.command()
@click.option(
    "--dir",
    "target_dir",
    default=".",
    type=click.Path(file_okay=False, path_type=Path),
    help="Directory where starter files should be created.",
)
@click.option(
    "--adapter-name",
    default=DEFAULT_ADAPTER_FILENAME,
    show_default=True,
    help="Filename for the generated adapter module.",
)
@click.option(
    "--queries-name",
    default=DEFAULT_QUERIES_FILENAME,
    show_default=True,
    help="Filename for the generated query CSV.",
)
@click.option(
    "--force",
    is_flag=True,
    default=False,
    help="Overwrite existing files if they already exist.",
)
def init(
    target_dir: Path,
    adapter_name: str,
    queries_name: str,
    force: bool,
) -> None:
    """Scaffold starter adapter and query files."""
    try:
        adapter_path, queries_path = scaffold_project(
            target_dir=target_dir,
            adapter_name=adapter_name,
            queries_name=queries_name,
            force=force,
        )
    except FileExistsError as exc:
        raise click.ClickException(str(exc)) from exc
    except ValueError as exc:
        raise click.UsageError(str(exc)) from exc

    console.print(f"[green]Created[/green] {adapter_path}")
    console.print(f"[green]Created[/green] {queries_path}")
    console.print("\n[dim]Next step:[/dim]")
    console.print(
        f"[dim]  veritail run --queries {queries_path.name} "
        f"--adapter {adapter_path.name}[/dim]"
    )


@main.group()
def vertical() -> None:
    """Inspect built-in vertical prompts."""
    pass


@vertical.command("list")
def vertical_list() -> None:
    """List all built-in verticals."""
    from veritail.verticals import list_verticals

    for name in list_verticals():
        console.print(name)


@vertical.command("show")
@click.argument("name")
def vertical_show(name: str) -> None:
    """Print the full text of a built-in vertical.

    Use this to inspect a vertical before customizing it, or to copy one
    as a starting point for your own:

        veritail vertical show home-improvement > my_vertical.txt
    """
    from veritail.verticals import load_vertical

    try:
        text = load_vertical(name)
    except FileNotFoundError as exc:
        raise click.ClickException(str(exc)) from exc

    click.echo(text)


@main.command("generate-queries")
@click.option(
    "--output",
    required=True,
    type=str,
    help="Output CSV path (must end with .csv).",
)
@click.option(
    "--count",
    default=25,
    type=int,
    help="Number of queries to generate.",
)
@click.option(
    "--vertical",
    default=None,
    type=str,
    help=(
        "Vertical for domain-specific query generation "
        "(built-in name or path to text file)."
    ),
)
@click.option(
    "--context",
    default=None,
    type=str,
    help="Business context string or path to a text file.",
)
@click.option(
    "--llm-model",
    default="claude-sonnet-4-5",
    help="LLM model to use for generation.",
)
def generate_queries_cmd(
    output: str,
    count: int,
    vertical: str | None,
    context: str | None,
    llm_model: str,
) -> None:
    """Generate evaluation queries with an LLM and save to CSV."""
    if count < 1:
        raise click.UsageError("--count must be >= 1.")

    if not output.endswith(".csv"):
        raise click.UsageError("--output must end with .csv.")

    if not vertical and not context:
        raise click.UsageError("At least one of --vertical or --context is required.")

    llm_client = create_llm_client(llm_model)

    try:
        llm_client.preflight_check()
    except RuntimeError as exc:
        raise click.ClickException(str(exc)) from exc

    from veritail.querygen import generate_queries

    output_path = Path(output)
    try:
        queries = generate_queries(
            llm_client=llm_client,
            output_path=output_path,
            count=count,
            vertical=vertical,
            context=context,
        )
    except (ValueError, FileNotFoundError) as exc:
        raise click.ClickException(str(exc)) from exc

    console.print(f"[green]Generated {len(queries)} queries[/green] -> {output_path}")
    console.print("\n[dim]Next step:[/dim]")
    console.print(
        f"[dim]  veritail run --queries {output_path} --adapter <your_adapter.py>[/dim]"
    )


@main.command()
@click.option(
    "--queries",
    required=False,
    default=None,
    type=click.Path(exists=True),
    help="Path to query set (CSV or JSON)",
)
@click.option(
    "--adapter",
    "adapters",
    required=True,
    multiple=True,
    type=click.Path(exists=True),
    help="Path to search adapter module(s)",
)
@click.option(
    "--config-name",
    "config_names",
    multiple=True,
    help=(
        "Optional name for each configuration. "
        "Provide one per adapter, or omit to auto-generate names."
    ),
)
@click.option(
    "--llm-model",
    default="claude-sonnet-4-5",
    help="LLM model to use for judgments",
)
@click.option(
    "--rubric",
    default="ecommerce-default",
    help="Rubric name or path to custom rubric module",
)
@click.option(
    "--backend",
    "backend_type",
    default="file",
    type=click.Choice(["file", "langfuse"]),
    help="Evaluation backend",
)
@click.option(
    "--output-dir",
    default="./eval-results",
    help="Output directory (file backend)",
)
@click.option(
    "--backend-url",
    default=None,
    help="Backend URL (langfuse backend)",
)
@click.option(
    "--top-k",
    default=10,
    type=int,
    help="Max results to evaluate per query",
)
@click.option(
    "--open",
    "open_browser",
    is_flag=True,
    default=False,
    help="Open the HTML report in the browser when complete.",
)
@click.option(
    "--context",
    default=None,
    type=str,
    help=(
        "Business context for the LLM judge — describes your business, "
        "customer base, and how queries should be interpreted. "
        "Accepts a string or a path to a text file."
    ),
)
@click.option(
    "--vertical",
    default=None,
    type=str,
    help=(
        "Vertical for domain-specific scoring guidance "
        "(built-in: automotive, beauty, electronics, fashion, "
        "foodservice, furniture, groceries, home-improvement, "
        "industrial, marketplace, medical, office-supplies, "
        "pet-supplies, sporting-goods, case-insensitive; "
        "or path to a text file)."
    ),
)
@click.option(
    "--checks",
    "check_modules",
    multiple=True,
    type=click.Path(exists=True),
    help="Path to custom check module(s) with check_* functions.",
)
@click.option(
    "--sample",
    default=None,
    type=int,
    help="Randomly sample N queries from the query set for a faster evaluation.",
)
def run(
    queries: str | None,
    adapters: tuple[str, ...],
    config_names: tuple[str, ...],
    llm_model: str,
    rubric: str,
    backend_type: str,
    output_dir: str,
    backend_url: str | None,
    top_k: int,
    open_browser: bool,
    context: str | None,
    vertical: str | None,
    check_modules: tuple[str, ...],
    sample: int | None,
) -> None:
    """Run evaluation (single or dual configuration)."""
    if not queries:
        raise click.UsageError(
            "--queries is required.\n\n"
            "To generate a starter query set:\n"
            "  veritail generate-queries --vertical <vertical> --output queries.csv\n\n"
            "Then run:\n"
            "  veritail run --queries queries.csv --adapter <your_adapter.py>"
        )

    if config_names and len(adapters) != len(config_names):
        raise click.UsageError(
            "Each --adapter must have a matching "
            "--config-name when names are provided. "
            f"Got {len(adapters)} adapter(s) and "
            f"{len(config_names)} config name(s). "
            "Or omit --config-name to auto-generate names."
        )

    if len(adapters) > 2:
        raise click.UsageError("At most 2 adapter/config-name pairs are supported.")

    if top_k < 1:
        raise click.UsageError("--top-k must be >= 1.")

    if not config_names:
        config_names = _generate_config_names(adapters)
        console.print(
            "[dim]No --config-name provided. Using generated names: "
            f"{', '.join(config_names)}[/dim]",
        )

    if sample is not None and sample < 1:
        raise click.UsageError("--sample must be >= 1.")

    query_entries = load_queries(queries)
    total_queries = len(query_entries)

    if sample is not None and sample < total_queries:
        import random

        rng = random.Random(42)
        query_entries = rng.sample(query_entries, sample)
        console.print(f"Sampled {sample} of {total_queries} queries from {queries}")
    else:
        console.print(f"Loaded {len(query_entries)} queries from {queries}")

    rubric_data = load_rubric(rubric)

    if context and Path(context).is_file():
        context = Path(context).read_text(encoding="utf-8").rstrip()

    vertical_context: str | None = None
    if vertical:
        from veritail.verticals import load_vertical

        vertical_context = load_vertical(vertical)

    custom_check_fns: list[CustomCheckFn] | None = None
    if check_modules:
        custom_check_fns = []
        for check_path in check_modules:
            loaded = load_checks(check_path)
            custom_check_fns.extend(loaded)
            console.print(
                f"[dim]Loaded {len(loaded)} custom check(s) from {check_path}[/dim]"
            )

    llm_client = create_llm_client(llm_model)

    try:
        llm_client.preflight_check()
    except RuntimeError as exc:
        raise click.ClickException(str(exc)) from exc

    backend_kwargs: dict[str, str] = {}
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

        judgments, checks, metrics, correction_judgments = run_evaluation(
            query_entries,
            adapter_fn,
            config,
            llm_client,
            rubric_data,
            backend,
            context=context,
            vertical=vertical_context,
            custom_checks=custom_check_fns,
        )
        run_metadata = _build_run_metadata(
            llm_model=llm_model,
            rubric=rubric,
            vertical=vertical,
            top_k=top_k,
            sample=sample,
            total_queries=total_queries,
            adapter_path=adapters[0],
        )

        report = generate_single_report(
            metrics,
            checks,
            run_metadata=run_metadata,
            correction_judgments=correction_judgments or None,
        )
        console.print(report)

        exp_dir = Path(output_dir) / config_names[0]
        exp_dir.mkdir(parents=True, exist_ok=True)

        metrics_path = exp_dir / "metrics.json"
        metrics_path.write_text(
            json.dumps(
                [asdict(m) for m in metrics],
                indent=2,
                default=str,
            ),
            encoding="utf-8",
        )

        if correction_judgments:
            corrections_path = exp_dir / "corrections.jsonl"
            corrections_path.write_text(
                "\n".join(
                    json.dumps(asdict(cj), default=str) for cj in correction_judgments
                )
                + "\n",
                encoding="utf-8",
            )

        html = generate_single_report(
            metrics,
            checks,
            judgments=judgments,
            format="html",
            run_metadata=run_metadata,
            correction_judgments=correction_judgments or None,
        )
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
            judgments_a,
            judgments_b,
            checks_a,
            checks_b,
            metrics_a,
            metrics_b,
            comparison_checks,
            corrections_a,
            corrections_b,
        ) = run_dual_evaluation(
            query_entries,
            adapter_a,
            config_a,
            adapter_b,
            config_b,
            llm_client,
            rubric_data,
            backend,
            context=context,
            vertical=vertical_context,
            custom_checks=custom_check_fns,
        )
        run_metadata = _build_run_metadata(
            llm_model=llm_model,
            rubric=rubric,
            vertical=vertical,
            top_k=top_k,
            sample=sample,
            total_queries=total_queries,
            adapter_path_a=adapters[0],
            adapter_path_b=adapters[1],
        )

        report = generate_comparison_report(
            metrics_a,
            metrics_b,
            comparison_checks,
            config_names[0],
            config_names[1],
            run_metadata=run_metadata,
            correction_judgments_a=corrections_a or None,
            correction_judgments_b=corrections_b or None,
        )
        console.print(report)

        configs_and_data = [
            (config_names[0], metrics_a, corrections_a),
            (config_names[1], metrics_b, corrections_b),
        ]
        for cfg_name, cfg_metrics, cfg_corrections in configs_and_data:
            exp_dir = Path(output_dir) / cfg_name
            exp_dir.mkdir(parents=True, exist_ok=True)
            metrics_path = exp_dir / "metrics.json"
            metrics_path.write_text(
                json.dumps(
                    [asdict(m) for m in cfg_metrics],
                    indent=2,
                    default=str,
                ),
                encoding="utf-8",
            )
            if cfg_corrections:
                corrections_path = exp_dir / "corrections.jsonl"
                corrections_path.write_text(
                    "\n".join(
                        json.dumps(asdict(cj), default=str) for cj in cfg_corrections
                    )
                    + "\n",
                    encoding="utf-8",
                )

        html = generate_comparison_report(
            metrics_a,
            metrics_b,
            comparison_checks,
            config_names[0],
            config_names[1],
            format="html",
            run_metadata=run_metadata,
        )
        cmp_dir = f"{config_names[0]}_vs_{config_names[1]}"
        html_path = Path(output_dir) / cmp_dir / "report.html"
        html_path.parent.mkdir(parents=True, exist_ok=True)
        html_path.write_text(html, encoding="utf-8")
        console.print(f"[dim]HTML report -> {html_path}[/dim]")

        if open_browser:
            import webbrowser

            webbrowser.open(html_path.resolve().as_uri())


if __name__ == "__main__":
    main()
