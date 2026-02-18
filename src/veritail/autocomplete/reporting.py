"""Autocomplete evaluation report generation."""

from __future__ import annotations

from collections.abc import Mapping
from io import StringIO
from pathlib import Path

from jinja2 import Environment, select_autoescape
from rich.console import Console
from rich.table import Table

from veritail.types import (
    AutocompleteResponse,
    CheckResult,
    MetricResult,
    PrefixEntry,
)

_JINJA_ENV = Environment(
    autoescape=select_autoescape(("html", "xml"), default_for_string=True),
)

METRIC_DESCRIPTIONS: dict[str, str] = {
    "mrr": (
        "Mean Reciprocal Rank - reciprocal of the rank of the "
        "first exact match of the target query in suggestions"
    ),
    "psaved": (
        "Proportion Saved - fraction of keystrokes saved by "
        "using the prefix instead of typing the full query"
    ),
    "sr@5": ("Success Rate at 5 - fraction of prefixes where target appears in top 5"),
    "sr@10": (
        "Success Rate at 10 - fraction of prefixes where the target appears in top 10"
    ),
    "esaved@5": "Expected Saved at 5 - pSaved * SR@5",
    "esaved@10": "Expected Saved at 10 - pSaved * SR@10",
}

CHECK_DESCRIPTIONS: dict[str, str] = {
    "empty_suggestions": "Fails when a prefix returns no suggestions at all",
    "duplicate_suggestion": "Detects duplicate suggestions in the response",
    "prefix_coherence": (
        "Verifies suggestions start with or share tokens with the prefix"
    ),
    "offensive_content": "Flags suggestions containing blocked terms",
    "suggestion_overlap": "Jaccard overlap of suggestions between two configurations",
    "rank_agreement": "Spearman rank correlation of shared suggestions",
}


def _summarize_checks(
    checks: list[CheckResult],
) -> dict[str, dict[str, str | int | bool]]:
    """Build a display-ready check summary for reports."""
    summary: dict[str, dict[str, str | int | bool]] = {}
    for c in checks:
        if c.check_name not in summary:
            summary[c.check_name] = {
                "display_name": c.check_name,
                "passed": 0,
                "failed": 0,
                "passed_display": "0",
                "passed_is_na": False,
            }
        if c.passed:
            summary[c.check_name]["passed"] = int(summary[c.check_name]["passed"]) + 1
        else:
            summary[c.check_name]["failed"] = int(summary[c.check_name]["failed"]) + 1

    for counts in summary.values():
        counts["passed_display"] = str(counts["passed"])

    return summary


def generate_autocomplete_report(
    metrics: list[MetricResult],
    checks: list[CheckResult],
    format: str = "terminal",
    responses_by_prefix: dict[int, AutocompleteResponse] | None = None,
    prefixes: list[PrefixEntry] | None = None,
    run_metadata: Mapping[str, object] | None = None,
) -> str:
    """Generate a report for a single autocomplete evaluation.

    Args:
        metrics: Computed autocomplete metrics.
        checks: Deterministic check results.
        format: "terminal" for rich console output, "html" for HTML file.
        responses_by_prefix: Optional mapping of prefix index to responses.
        prefixes: Optional list of prefix entries.
        run_metadata: Optional provenance metadata.

    Returns:
        Formatted report string.
    """
    if format == "html":
        return _generate_html(
            metrics, checks, responses_by_prefix, prefixes, run_metadata
        )
    return _generate_terminal(metrics, checks, responses_by_prefix, prefixes)


def generate_autocomplete_comparison_report(
    metrics_a: list[MetricResult],
    metrics_b: list[MetricResult],
    comparison_checks: list[CheckResult],
    config_a: str,
    config_b: str,
    format: str = "terminal",
    run_metadata: Mapping[str, object] | None = None,
) -> str:
    """Generate a comparison report for two autocomplete configurations."""
    if format == "html":
        return _generate_comparison_html(
            metrics_a, metrics_b, comparison_checks, config_a, config_b, run_metadata
        )
    return _generate_comparison_terminal(
        metrics_a, metrics_b, comparison_checks, config_a, config_b
    )


def _generate_terminal(
    metrics: list[MetricResult],
    checks: list[CheckResult],
    responses_by_prefix: dict[int, AutocompleteResponse] | None = None,
    prefixes: list[PrefixEntry] | None = None,
) -> str:
    """Generate a rich-formatted terminal report."""
    con = Console(file=StringIO(), force_terminal=True, width=100)

    con.print("\n[bold]Autocomplete Evaluation Report[/bold]\n")

    # Metrics table
    table = Table(title="Autocomplete Metrics", show_header=True)
    table.add_column("Metric", style="cyan")
    table.add_column("Value", justify="right")
    for m in metrics:
        table.add_row(m.metric_name, f"{m.value:.4f}")
    con.print(table)

    # By type breakdown
    type_metrics = [m for m in metrics if m.by_query_type]
    if type_metrics:
        con.print("\n")
        type_table = Table(title="Metrics by Prefix Type", show_header=True)
        type_table.add_column("Metric", style="cyan")
        all_types: set[str] = set()
        for m in type_metrics:
            all_types.update(m.by_query_type.keys())
        for qt in sorted(all_types):
            type_table.add_column(qt, justify="right")
        for m in type_metrics:
            row = [m.metric_name]
            for qt in sorted(all_types):
                val = m.by_query_type.get(qt)
                row.append(f"{val:.4f}" if val is not None else "-")
            type_table.add_row(*row)
        con.print(type_table)

    # Checks summary
    con.print("\n")
    check_table = Table(title="Deterministic Checks", show_header=True)
    check_table.add_column("Check", style="cyan")
    check_table.add_column("Passed", justify="right", style="green")
    check_table.add_column("Failed", justify="right", style="red")
    check_summary = _summarize_checks(checks)
    for _, counts in sorted(check_summary.items()):
        check_table.add_row(
            str(counts["display_name"]),
            str(counts["passed_display"]),
            str(counts["failed"]),
        )
    con.print(check_table)

    # Worst prefixes by MRR
    mrr_metric = next((m for m in metrics if m.metric_name == "mrr"), None)
    if mrr_metric and mrr_metric.per_query:
        con.print("\n")
        worst = sorted(mrr_metric.per_query.items(), key=lambda x: x[1])[:10]
        worst_table = Table(title="Worst Performing Prefixes (MRR)", show_header=True)
        worst_table.add_column("Prefix", style="cyan")
        worst_table.add_column("MRR", justify="right")
        for prefix, value in worst:
            worst_table.add_row(prefix, f"{value:.4f}")
        con.print(worst_table)

    # Per-prefix drill-down
    if prefixes and responses_by_prefix:
        con.print("\n")
        drill_table = Table(title="Per-Prefix Results", show_header=True)
        drill_table.add_column("Prefix", style="cyan")
        drill_table.add_column("Target Query")
        drill_table.add_column("MRR", justify="right")
        drill_table.add_column("Suggestions", style="dim")

        # Sort by MRR ascending (worst first)
        prefix_mrr_values: list[tuple[int, float]] = []
        for i, entry in enumerate(prefixes):
            val = mrr_metric.per_query.get(entry.prefix, 0.0) if mrr_metric else 0.0
            prefix_mrr_values.append((i, val))
        prefix_mrr_values.sort(key=lambda x: x[1])

        for idx, mrr_val in prefix_mrr_values[:20]:
            entry = prefixes[idx]
            resp = responses_by_prefix.get(idx)
            sug_str = ", ".join(resp.suggestions[:5]) if resp else "(none)"
            if resp and len(resp.suggestions) > 5:
                sug_str += f" (+{len(resp.suggestions) - 5} more)"
            drill_table.add_row(
                entry.prefix, entry.target_query, f"{mrr_val:.4f}", sug_str
            )
        con.print(drill_table)

    assert isinstance(con.file, StringIO)
    return con.file.getvalue()


def _generate_comparison_terminal(
    metrics_a: list[MetricResult],
    metrics_b: list[MetricResult],
    comparison_checks: list[CheckResult],
    config_a: str,
    config_b: str,
) -> str:
    """Generate a rich-formatted terminal comparison report."""
    con = Console(file=StringIO(), force_terminal=True, width=120)

    con.print(f"\n[bold]Autocomplete Comparison: '{config_a}' vs '{config_b}'[/bold]\n")

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
    con.print(table)

    # Comparison checks summary
    overlap_checks = [
        c for c in comparison_checks if c.check_name == "suggestion_overlap"
    ]
    if overlap_checks:
        con.print("\n[bold]Suggestion Overlap[/bold]")
        for c in overlap_checks[:5]:
            con.print(f"  {c.query}: {c.detail}")

    assert isinstance(con.file, StringIO)
    return con.file.getvalue()


def _generate_html(
    metrics: list[MetricResult],
    checks: list[CheckResult],
    responses_by_prefix: dict[int, AutocompleteResponse] | None = None,
    prefixes: list[PrefixEntry] | None = None,
    run_metadata: Mapping[str, object] | None = None,
) -> str:
    """Generate an HTML report using Jinja2."""
    tmpl_dir = Path(__file__).resolve().parent.parent / "reporting" / "templates"
    template_path = tmpl_dir / "autocomplete_report.html"
    template_str = template_path.read_text(encoding="utf-8")
    template = _JINJA_ENV.from_string(template_str)

    check_summary = _summarize_checks(checks)

    # Worst prefixes by MRR
    mrr_metric = next((m for m in metrics if m.metric_name == "mrr"), None)
    worst_prefixes: list[tuple[str, float]] = []
    if mrr_metric and mrr_metric.per_query:
        worst_prefixes = sorted(mrr_metric.per_query.items(), key=lambda x: x[1])[:10]

    # Per-prefix drill-down
    prefix_details: list[dict[str, object]] = []
    if prefixes and responses_by_prefix:
        for i, entry in enumerate(prefixes):
            resp = responses_by_prefix.get(i)
            mrr_val = mrr_metric.per_query.get(entry.prefix, 0.0) if mrr_metric else 0.0
            prefix_details.append(
                {
                    "prefix": entry.prefix,
                    "target_query": entry.target_query,
                    "type": entry.type or "",
                    "mrr": mrr_val,
                    "suggestions": resp.suggestions if resp else [],
                }
            )
        prefix_details.sort(key=lambda x: float(str(x["mrr"])))

    # By type breakdown
    type_metrics = [m for m in metrics if m.by_query_type]
    query_types: list[str] = []
    if type_metrics:
        all_types: set[str] = set()
        for m in type_metrics:
            all_types.update(m.by_query_type.keys())
        query_types = sorted(all_types)

    metadata_rows: list[dict[str, str]] = []
    if run_metadata:
        key_to_label = [
            ("generated_at_utc", "Timestamp (UTC)"),
            ("top_k", "Top-K"),
            ("adapter_path", "Adapter Path"),
            ("adapter_path_a", "Adapter Path (A)"),
            ("adapter_path_b", "Adapter Path (B)"),
        ]
        for key, label in key_to_label:
            if key in run_metadata:
                metadata_rows.append({"label": label, "value": str(run_metadata[key])})

    return template.render(
        is_comparison=False,
        metrics=metrics,
        check_summary=check_summary,
        worst_prefixes=worst_prefixes,
        prefix_details=prefix_details,
        metric_descriptions=METRIC_DESCRIPTIONS,
        check_descriptions=CHECK_DESCRIPTIONS,
        run_metadata_rows=metadata_rows,
        type_metrics=type_metrics,
        query_types=query_types,
    )


def _generate_comparison_html(
    metrics_a: list[MetricResult],
    metrics_b: list[MetricResult],
    comparison_checks: list[CheckResult],
    config_a: str,
    config_b: str,
    run_metadata: Mapping[str, object] | None = None,
) -> str:
    """Generate an HTML comparison report."""
    tmpl_dir = Path(__file__).resolve().parent.parent / "reporting" / "templates"
    template_path = tmpl_dir / "autocomplete_report.html"
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

    overlap_checks = [
        c for c in comparison_checks if c.check_name == "suggestion_overlap"
    ]

    metadata_rows: list[dict[str, str]] = []
    if run_metadata:
        key_to_label = [
            ("generated_at_utc", "Timestamp (UTC)"),
            ("top_k", "Top-K"),
            ("adapter_path_a", "Adapter Path (A)"),
            ("adapter_path_b", "Adapter Path (B)"),
        ]
        for key, label in key_to_label:
            if key in run_metadata:
                metadata_rows.append({"label": label, "value": str(run_metadata[key])})

    return template.render(
        is_comparison=True,
        config_a=config_a,
        config_b=config_b,
        comparison_data=comparison_data,
        overlap_checks=overlap_checks[:10],
        run_metadata_rows=metadata_rows,
    )
