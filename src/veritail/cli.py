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
from veritail.pipeline import (
    run_batch_evaluation,
    run_dual_batch_evaluation,
    run_dual_evaluation,
    run_evaluation,
)
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


_KNOWN_MODEL_PREFIXES = ("claude", "gemini", "gpt-", "o1", "o3", "o4")


def _warn_custom_model(model: str, base_url: str | None) -> None:
    """Emit a warning when the model name is unrecognized."""
    if any(model.startswith(p) for p in _KNOWN_MODEL_PREFIXES):
        return
    if base_url:
        console.print(
            f"[yellow]Using custom endpoint ({base_url}) with model '{model}'. "
            "Evaluation quality depends on model capability — "
            "for reliable metrics, 70B+ parameter models are recommended.[/yellow]"
        )
    else:
        console.print(
            f"[yellow]Model '{model}' is not a recognized cloud model. "
            "If you are using a local model server, pass --llm-base-url to "
            "specify the endpoint (e.g. --llm-base-url http://localhost:11434/v1).[/yellow]"
        )


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
@click.option(
    "--autocomplete",
    is_flag=True,
    default=False,
    help="Also generate suggest_adapter.py and prefixes.csv.",
)
def init(
    target_dir: Path,
    adapter_name: str,
    queries_name: str,
    force: bool,
    autocomplete: bool,
) -> None:
    """Scaffold starter adapter and query files."""
    try:
        created = scaffold_project(
            target_dir=target_dir,
            adapter_name=adapter_name,
            queries_name=queries_name,
            force=force,
            autocomplete=autocomplete,
        )
    except FileExistsError as exc:
        raise click.ClickException(str(exc)) from exc
    except ValueError as exc:
        raise click.UsageError(str(exc)) from exc

    for p in created:
        console.print(f"[green]Created[/green] {p}")
    console.print("\n[dim]Next step:[/dim]")
    console.print(
        f"[dim]  veritail run --queries {created[1].name} "
        f"--adapter {created[0].name} --llm-model <model>[/dim]"
    )
    if autocomplete:
        console.print(
            f"[dim]  veritail autocomplete run --prefixes {created[3].name} "
            f"--adapter {created[2].name}[/dim]"
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
    help=(
        "Target number of queries to generate (approximate — LLMs may "
        "return slightly fewer). Max 50."
    ),
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
    required=True,
    help=(
        "LLM model to use for generation "
        "(e.g. gpt-4o, claude-sonnet-4-5, gemini-2.5-flash)."
    ),
)
@click.option(
    "--llm-base-url",
    default=None,
    help=(
        "Base URL for an OpenAI-compatible API endpoint. "
        "Use this to connect to local model servers "
        "(e.g. http://localhost:11434/v1 for Ollama)."
    ),
)
@click.option(
    "--llm-api-key",
    default=None,
    help="API key override (useful for non-OpenAI endpoints that ignore keys).",
)
def generate_queries_cmd(
    output: str,
    count: int,
    vertical: str | None,
    context: str | None,
    llm_model: str,
    llm_base_url: str | None,
    llm_api_key: str | None,
) -> None:
    """Generate evaluation queries with an LLM and save to CSV."""
    if count < 1:
        raise click.UsageError("--count must be >= 1.")

    if count > 50:
        raise click.UsageError(
            "--count must be <= 50. For larger query sets, "
            "run the command multiple times or curate queries manually."
        )

    if not output.endswith(".csv"):
        raise click.UsageError("--output must end with .csv.")

    if not vertical and not context:
        raise click.UsageError("At least one of --vertical or --context is required.")

    _warn_custom_model(llm_model, llm_base_url)
    llm_client = create_llm_client(
        llm_model, base_url=llm_base_url, api_key=llm_api_key
    )

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

    if len(queries) != count:
        console.print(
            f"[green]Generated {len(queries)} queries[/green] "
            f"[yellow](requested {count})[/yellow] -> {output_path}"
        )
    else:
        console.print(
            f"[green]Generated {len(queries)} queries[/green] -> {output_path}"
        )
    console.print("\n[dim]Next step:[/dim]")
    console.print(
        f"[dim]  veritail run --queries {output_path} "
        f"--adapter <your_adapter.py> --llm-model <model>[/dim]"
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
    required=False,
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
    required=True,
    help=(
        "LLM model to use for judgments "
        "(e.g. gpt-4o, claude-sonnet-4-5, gemini-2.5-flash)"
    ),
)
@click.option(
    "--llm-base-url",
    default=None,
    help=(
        "Base URL for an OpenAI-compatible API endpoint. "
        "Use this to connect to local model servers "
        "(e.g. http://localhost:11434/v1 for Ollama)."
    ),
)
@click.option(
    "--llm-api-key",
    default=None,
    help="API key override (useful for non-OpenAI endpoints that ignore keys).",
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
@click.option(
    "--batch",
    "use_batch",
    is_flag=True,
    default=False,
    help="Use provider batch API for LLM calls (50%% cheaper, slower).",
)
@click.option(
    "--resume",
    "use_resume",
    is_flag=True,
    default=False,
    help=(
        "Resume a previously interrupted run. Requires --config-name "
        "to identify the previous run."
    ),
)
def run(
    queries: str | None,
    adapters: tuple[str, ...],
    config_names: tuple[str, ...],
    llm_model: str,
    llm_base_url: str | None,
    llm_api_key: str | None,
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
    use_batch: bool,
    use_resume: bool,
) -> None:
    """Run evaluation (single or dual configuration)."""
    if not queries:
        raise click.UsageError(
            "--queries is required.\n\n"
            "Option 1 - scaffold starter files (adapter + sample queries):\n"
            "  veritail init\n\n"
            "Option 2 - generate domain-aware queries with an LLM:\n"
            "  veritail generate-queries --vertical <vertical> "
            "--output queries.csv --llm-model <model>\n\n"
            "Then run:\n"
            "  veritail run --queries queries.csv "
            "--adapter adapter.py --llm-model <model>"
        )

    if not adapters:
        raise click.UsageError(
            "--adapter is required.\n\n"
            "To scaffold a starter adapter:\n"
            "  veritail init\n\n"
            "Then run:\n"
            "  veritail run --queries queries.csv "
            "--adapter adapter.py --llm-model <model>"
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

    if use_resume:
        if not config_names:
            raise click.UsageError(
                "--resume requires --config-name to identify the previous run."
            )
        # Verify experiment directory exists for each config
        for cn in config_names:
            exp_dir = Path(output_dir) / cn
            if not exp_dir.exists():
                raise click.UsageError(
                    f"--resume: experiment directory '{exp_dir}' does not exist. "
                    "Cannot resume a run that never started."
                )
            # Config mismatch detection
            config_file = exp_dir / "config.json"
            if config_file.exists():
                with open(config_file, encoding="utf-8") as f:
                    saved = json.load(f)
                mismatches: list[str] = []
                if saved.get("llm_model") != llm_model:
                    mismatches.append(
                        f"  llm_model: saved={saved.get('llm_model')!r}, "
                        f"current={llm_model!r}"
                    )
                if saved.get("rubric") != rubric:
                    mismatches.append(
                        f"  rubric: saved={saved.get('rubric')!r}, current={rubric!r}"
                    )
                if saved.get("top_k") != top_k:
                    mismatches.append(
                        f"  top_k: saved={saved.get('top_k')!r}, current={top_k!r}"
                    )
                if mismatches:
                    detail = "\n".join(mismatches)
                    raise click.UsageError(
                        f"--resume: config mismatch for '{cn}':\n{detail}\n"
                        "Drop --resume to start a fresh run, or fix the "
                        "arguments to match the previous run."
                    )

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

    _warn_custom_model(llm_model, llm_base_url)
    llm_client = create_llm_client(
        llm_model, base_url=llm_base_url, api_key=llm_api_key
    )

    try:
        llm_client.preflight_check()
    except RuntimeError as exc:
        raise click.ClickException(str(exc)) from exc

    if use_batch:
        if llm_base_url is not None:
            raise click.UsageError(
                "--batch cannot be used with --llm-base-url. "
                "Batch APIs are only available for cloud providers "
                "(OpenAI, Anthropic, Gemini)."
            )
        if not llm_client.supports_batch():
            raise click.UsageError(
                f"The model '{llm_model}' does not support batch operations."
            )

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

        pipeline_fn = run_batch_evaluation if use_batch else run_evaluation
        judgments, checks, metrics, correction_judgments = pipeline_fn(
            query_entries,
            adapter_fn,
            config,
            llm_client,
            rubric_data,
            backend,
            context=context,
            vertical=vertical_context,
            custom_checks=custom_check_fns,
            resume=use_resume,
            output_dir=output_dir,
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

        dual_fn = run_dual_batch_evaluation if use_batch else run_dual_evaluation
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
        ) = dual_fn(
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
            resume=use_resume,
            output_dir=output_dir,
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
            correction_judgments_a=corrections_a or None,
            correction_judgments_b=corrections_b or None,
        )
        cmp_dir = f"{config_names[0]}_vs_{config_names[1]}"
        html_path = Path(output_dir) / cmp_dir / "report.html"
        html_path.parent.mkdir(parents=True, exist_ok=True)
        html_path.write_text(html, encoding="utf-8")
        console.print(f"[dim]HTML report -> {html_path}[/dim]")

        if open_browser:
            import webbrowser

            webbrowser.open(html_path.resolve().as_uri())


def _build_autocomplete_run_metadata(
    *,
    top_k: int,
    sample: int | None = None,
    total_prefixes: int | None = None,
    adapter_path: str | None = None,
    adapter_path_a: str | None = None,
    adapter_path_b: str | None = None,
) -> dict[str, object]:
    """Build provenance metadata for autocomplete report rendering."""
    metadata: dict[str, object] = {
        "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "top_k": top_k,
    }
    if sample is not None and total_prefixes is not None:
        metadata["sample"] = f"{sample} of {total_prefixes}"
    if adapter_path is not None:
        metadata["adapter_path"] = adapter_path
    if adapter_path_a is not None:
        metadata["adapter_path_a"] = adapter_path_a
    if adapter_path_b is not None:
        metadata["adapter_path_b"] = adapter_path_b
    return metadata


@main.group()
def autocomplete() -> None:
    """Evaluate autocomplete / type-ahead suggestions."""
    pass


@autocomplete.command("run")
@click.option(
    "--prefixes",
    required=True,
    type=click.Path(exists=True),
    help="Path to prefix set (CSV or JSON with prefix + target_query columns).",
)
@click.option(
    "--adapter",
    "adapters",
    required=True,
    multiple=True,
    type=click.Path(exists=True),
    help="Path to suggest adapter module(s). Max 2 for A/B comparison.",
)
@click.option(
    "--config-name",
    "config_names",
    multiple=True,
    help="Optional name for each configuration.",
)
@click.option(
    "--output-dir",
    default="./eval-results",
    help="Output directory for results.",
)
@click.option(
    "--top-k",
    default=10,
    type=int,
    help="Max suggestions to evaluate per prefix.",
)
@click.option(
    "--checks",
    "check_modules",
    multiple=True,
    type=click.Path(exists=True),
    help="Path to custom check module(s).",
)
@click.option(
    "--sample",
    default=None,
    type=int,
    help="Randomly sample N prefixes from the prefix set.",
)
@click.option(
    "--open",
    "open_browser",
    is_flag=True,
    default=False,
    help="Open the HTML report in the browser when complete.",
)
def autocomplete_run(
    prefixes: str,
    adapters: tuple[str, ...],
    config_names: tuple[str, ...],
    output_dir: str,
    top_k: int,
    check_modules: tuple[str, ...],
    sample: int | None,
    open_browser: bool,
) -> None:
    """Run autocomplete evaluation (single or dual configuration)."""
    from veritail.autocomplete.adapter import load_suggest_adapter
    from veritail.autocomplete.pipeline import (
        run_autocomplete_evaluation,
        run_dual_autocomplete_evaluation,
    )
    from veritail.autocomplete.queries import load_prefixes
    from veritail.autocomplete.reporting import (
        generate_autocomplete_comparison_report,
        generate_autocomplete_report,
    )
    from veritail.types import AutocompleteConfig

    if config_names and len(adapters) != len(config_names):
        raise click.UsageError(
            "Each --adapter must have a matching --config-name. "
            f"Got {len(adapters)} adapter(s) and "
            f"{len(config_names)} config name(s)."
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

    prefix_entries = load_prefixes(prefixes)
    total_prefixes = len(prefix_entries)

    if sample is not None and sample < total_prefixes:
        import random

        rng = random.Random(42)
        prefix_entries = rng.sample(prefix_entries, sample)
        console.print(f"Sampled {sample} of {total_prefixes} prefixes from {prefixes}")
    else:
        console.print(f"Loaded {len(prefix_entries)} prefixes from {prefixes}")

    # Load custom checks if any
    custom_check_fns = None
    if check_modules:
        import importlib.util

        custom_check_fns = []
        for check_path in check_modules:
            spec = importlib.util.spec_from_file_location(
                "ac_custom_checks", check_path
            )
            if spec is None or spec.loader is None:
                raise click.ClickException(
                    f"Could not load check module from: {check_path}"
                )
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            found = 0
            for name in sorted(dir(mod)):
                if name.startswith("check_") and callable(getattr(mod, name)):
                    custom_check_fns.append(getattr(mod, name))
                    found += 1
            if found == 0:
                raise click.ClickException(
                    f"Check module '{check_path}' has no check_* functions."
                )
            console.print(
                f"[dim]Loaded {found} custom check(s) from {check_path}[/dim]"
            )

    if len(adapters) == 1:
        config = AutocompleteConfig(
            name=config_names[0],
            adapter_path=adapters[0],
            top_k=top_k,
        )
        adapter_fn = load_suggest_adapter(adapters[0])
        checks, metrics, responses = run_autocomplete_evaluation(
            prefix_entries, adapter_fn, config, custom_checks=custom_check_fns
        )
        run_metadata = _build_autocomplete_run_metadata(
            top_k=top_k,
            sample=sample,
            total_prefixes=total_prefixes,
            adapter_path=adapters[0],
        )

        report = generate_autocomplete_report(
            metrics,
            checks,
            responses_by_prefix=responses,
            prefixes=prefix_entries,
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

        html = generate_autocomplete_report(
            metrics,
            checks,
            format="html",
            responses_by_prefix=responses,
            prefixes=prefix_entries,
            run_metadata=run_metadata,
        )
        html_path = exp_dir / "report.html"
        html_path.write_text(html, encoding="utf-8")
        console.print(f"[dim]HTML report -> {html_path}[/dim]")

        if open_browser:
            import webbrowser

            webbrowser.open(html_path.resolve().as_uri())

    else:
        config_a = AutocompleteConfig(
            name=config_names[0],
            adapter_path=adapters[0],
            top_k=top_k,
        )
        config_b = AutocompleteConfig(
            name=config_names[1],
            adapter_path=adapters[1],
            top_k=top_k,
        )
        adapter_a = load_suggest_adapter(adapters[0])
        adapter_b = load_suggest_adapter(adapters[1])

        (
            checks_a,
            checks_b,
            metrics_a,
            metrics_b,
            comparison_checks,
        ) = run_dual_autocomplete_evaluation(
            prefix_entries,
            adapter_a,
            config_a,
            adapter_b,
            config_b,
            custom_checks=custom_check_fns,
        )
        run_metadata = _build_autocomplete_run_metadata(
            top_k=top_k,
            sample=sample,
            total_prefixes=total_prefixes,
            adapter_path_a=adapters[0],
            adapter_path_b=adapters[1],
        )

        report = generate_autocomplete_comparison_report(
            metrics_a,
            metrics_b,
            comparison_checks,
            config_names[0],
            config_names[1],
        )
        console.print(report)

        for cfg_name, cfg_metrics in [
            (config_names[0], metrics_a),
            (config_names[1], metrics_b),
        ]:
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

        html = generate_autocomplete_comparison_report(
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
