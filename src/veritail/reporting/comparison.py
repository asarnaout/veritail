"""A/B comparison report generation."""

from __future__ import annotations

from collections.abc import Mapping
from io import StringIO
from pathlib import Path

from jinja2 import Environment, select_autoescape
from rich.console import Console
from rich.table import Table

from veritail.types import CheckResult, MetricResult

_JINJA_ENV = Environment(
    autoescape=select_autoescape(("html", "xml"), default_for_string=True),
)


def generate_comparison_report(
    metrics_a: list[MetricResult],
    metrics_b: list[MetricResult],
    comparison_checks: list[CheckResult],
    config_a: str,
    config_b: str,
    format: str = "terminal",
    run_metadata: Mapping[str, object] | None = None,
) -> str:
    """Generate a comparison report for two evaluation configurations.

    Args:
        metrics_a: Metrics from baseline configuration
        metrics_b: Metrics from experimental configuration
        comparison_checks: Cross-configuration check results
        config_a: Name of the baseline configuration
        config_b: Name of the experimental configuration
        format: "terminal" or "html"

    Returns:
        Formatted report string.
    """
    if format == "html":
        return _generate_html(
            metrics_a,
            metrics_b,
            comparison_checks,
            config_a,
            config_b,
            run_metadata=run_metadata,
        )
    return _generate_terminal(
        metrics_a,
        metrics_b,
        comparison_checks,
        config_a,
        config_b,
    )


def _generate_terminal(
    metrics_a: list[MetricResult],
    metrics_b: list[MetricResult],
    comparison_checks: list[CheckResult],
    config_a: str,
    config_b: str,
) -> str:
    """Generate a rich-formatted terminal comparison report."""
    console = Console(file=StringIO(), force_terminal=True, width=120)

    console.print(
        f"\n[bold]Search Evaluation Comparison: '{config_a}' vs '{config_b}'[/bold]\n"
    )

    # Side-by-side metrics
    table = Table(title="Metrics Comparison", show_header=True)
    table.add_column("Metric", style="cyan")
    table.add_column(config_a, justify="right")
    table.add_column(config_b, justify="right")
    table.add_column("Delta", justify="right")
    table.add_column("% Change", justify="right")

    metrics_b_lookup = {m.metric_name: m for m in metrics_b}
    for m_a in metrics_a:
        m_b = metrics_b_lookup.get(m_a.metric_name)
        if m_b:
            delta = m_b.value - m_a.value
            pct = (delta / m_a.value * 100) if m_a.value != 0 else 0.0
            delta_str = f"{delta:+.4f}"
            pct_str = f"{pct:+.1f}%"

            # Color: green for improvement, red for regression
            if delta > 0:
                delta_str = f"[green]{delta_str}[/green]"
                pct_str = f"[green]{pct_str}[/green]"
            elif delta < 0:
                delta_str = f"[red]{delta_str}[/red]"
                pct_str = f"[red]{pct_str}[/red]"

            table.add_row(
                m_a.metric_name,
                f"{m_a.value:.4f}",
                f"{m_b.value:.4f}",
                delta_str,
                pct_str,
            )

    console.print(table)

    # By query type comparison
    all_types: set[str] = set()
    for m in metrics_a + metrics_b:
        all_types.update(m.by_query_type.keys())

    if all_types:
        console.print("\n")
        for qt in sorted(all_types):
            type_table = Table(title=f"Query Type: {qt}", show_header=True)
            type_table.add_column("Metric", style="cyan")
            type_table.add_column(config_a, justify="right")
            type_table.add_column(config_b, justify="right")
            type_table.add_column("Delta", justify="right")

            for m_a in metrics_a:
                m_b = metrics_b_lookup.get(m_a.metric_name)
                if m_b and qt in m_a.by_query_type and qt in m_b.by_query_type:
                    va = m_a.by_query_type[qt]
                    vb = m_b.by_query_type[qt]
                    delta = vb - va
                    delta_str = f"{delta:+.4f}"
                    if delta > 0:
                        delta_str = f"[green]{delta_str}[/green]"
                    elif delta < 0:
                        delta_str = f"[red]{delta_str}[/red]"
                    type_table.add_row(
                        m_a.metric_name,
                        f"{va:.4f}",
                        f"{vb:.4f}",
                        delta_str,
                    )

            console.print(type_table)

    # Comparison checks summary
    overlap_checks = [c for c in comparison_checks if c.check_name == "result_overlap"]
    shift_checks = [c for c in comparison_checks if c.check_name == "position_shift"]
    if overlap_checks:
        console.print("\n[bold]Result Set Overlap[/bold]")
        for c in overlap_checks[:5]:
            console.print(f"  {c.query}: {c.detail}")

    if shift_checks:
        console.print("\n[bold]Biggest Position Shifts[/bold]")
        for c in shift_checks[:10]:
            console.print(f"  {c.query}: {c.detail}")

    # Regression detection
    ndcg_a = next(
        (m for m in metrics_a if m.metric_name == "ndcg@10"),
        None,
    )
    ndcg_b = next(
        (m for m in metrics_b if m.metric_name == "ndcg@10"),
        None,
    )

    if ndcg_a and ndcg_b and ndcg_a.per_query and ndcg_b.per_query:
        regressions = []
        for query in ndcg_a.per_query:
            if query in ndcg_b.per_query:
                delta = ndcg_b.per_query[query] - ndcg_a.per_query[query]
                if delta < -0.1:
                    regressions.append(
                        (
                            query,
                            ndcg_a.per_query[query],
                            ndcg_b.per_query[query],
                            delta,
                        )
                    )

        if regressions:
            console.print("\n")
            reg_table = Table(
                title="Regressions (NDCG@10 drop > 0.1)",
                show_header=True,
            )
            reg_table.add_column("Query", style="cyan")
            reg_table.add_column(config_a, justify="right")
            reg_table.add_column(config_b, justify="right")
            reg_table.add_column("Delta", justify="right", style="red")

            regressions.sort(key=lambda x: x[3])
            for query, va, vb, delta in regressions[:10]:
                reg_table.add_row(
                    query,
                    f"{va:.4f}",
                    f"{vb:.4f}",
                    f"{delta:+.4f}",
                )

            console.print(reg_table)

    output = console.file.getvalue()
    return output


def _generate_html(
    metrics_a: list[MetricResult],
    metrics_b: list[MetricResult],
    comparison_checks: list[CheckResult],
    config_a: str,
    config_b: str,
    run_metadata: Mapping[str, object] | None = None,
) -> str:
    """Generate an HTML comparison report."""
    tmpl_dir = Path(__file__).parent / "templates"
    template_path = tmpl_dir / "report.html"
    template_str = template_path.read_text(encoding="utf-8")
    template = _JINJA_ENV.from_string(template_str)

    metrics_b_lookup = {m.metric_name: m for m in metrics_b}
    comparison_data = []
    for m_a in metrics_a:
        m_b = metrics_b_lookup.get(m_a.metric_name)
        if m_b:
            delta = m_b.value - m_a.value
            pct = (delta / m_a.value * 100) if m_a.value != 0 else 0.0
            comparison_data.append(
                {
                    "name": m_a.metric_name,
                    "value_a": m_a.value,
                    "value_b": m_b.value,
                    "delta": delta,
                    "pct_change": pct,
                }
            )

    shift_checks = [c for c in comparison_checks if c.check_name == "position_shift"]

    metadata_rows: list[dict[str, str]] = []
    if run_metadata:
        key_to_label = [
            ("generated_at_utc", "Timestamp (UTC)"),
            ("llm_model", "Model"),
            ("rubric", "Rubric"),
            ("vertical", "Vertical"),
            ("top_k", "Top-K"),
            ("adapter_path", "Adapter Path"),
            ("adapter_path_a", "Adapter Path (A)"),
            ("adapter_path_b", "Adapter Path (B)"),
        ]
        for key, label in key_to_label:
            if key in run_metadata:
                metadata_rows.append(
                    {
                        "label": label,
                        "value": str(run_metadata[key]),
                    }
                )

    return template.render(
        is_comparison=True,
        config_a=config_a,
        config_b=config_b,
        comparison_data=comparison_data,
        shift_checks=shift_checks[:10],
        run_metadata_rows=metadata_rows,
    )
