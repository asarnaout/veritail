"""Single-configuration report generation."""

from __future__ import annotations

from io import StringIO
from pathlib import Path
from typing import Optional

from jinja2 import Template
from rich.console import Console
from rich.table import Table

from veritail.types import CheckResult, JudgmentRecord, MetricResult

METRIC_DESCRIPTIONS: dict[str, str] = {
    "ndcg@5": "Ranking quality at top 5 — rewards placing the most relevant products highest (graded 0-3)",
    "ndcg@10": "Ranking quality at top 10 — rewards placing the most relevant products highest (graded 0-3)",
    "mrr": "Mean Reciprocal Rank — how high up the first relevant result appears (1.0 = first position)",
    "map": "Mean Average Precision — overall precision across all relevant results",
    "p@5": "Precision at 5 — fraction of top 5 results that are relevant (score >= 2)",
    "p@10": "Precision at 10 — fraction of top 10 results that are relevant (score >= 2)",
}


def generate_single_report(
    metrics: list[MetricResult],
    checks: list[CheckResult],
    agreement: Optional[dict] = None,
    format: str = "terminal",
    judgments: Optional[list[JudgmentRecord]] = None,
) -> str:
    """Generate a report for a single evaluation configuration.

    Args:
        metrics: Computed IR metrics
        checks: Deterministic check results
        agreement: Optional inter-rater agreement data
        format: "terminal" for rich console output, "html" for HTML file
        judgments: Optional list of per-product LLM judgments (used in HTML output)

    Returns:
        Formatted report string.
    """
    if format == "html":
        return _generate_html(metrics, checks, agreement, judgments)
    return _generate_terminal(metrics, checks, agreement)


def _generate_terminal(
    metrics: list[MetricResult],
    checks: list[CheckResult],
    agreement: Optional[dict],
) -> str:
    """Generate a rich-formatted terminal report."""
    console = Console(file=StringIO(), force_terminal=True, width=100)

    console.print("\n[bold]Search Evaluation Report[/bold]\n")

    # Metrics table
    table = Table(title="IR Metrics", show_header=True)
    table.add_column("Metric", style="cyan")
    table.add_column("Value", justify="right")

    for m in metrics:
        table.add_row(m.metric_name, f"{m.value:.4f}")

    console.print(table)

    # By query type breakdown (if available)
    type_metrics = [m for m in metrics if m.by_query_type]
    if type_metrics:
        console.print("\n")
        type_table = Table(title="Metrics by Query Type", show_header=True)
        type_table.add_column("Metric", style="cyan")

        # Collect all query types
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

        console.print(type_table)

    # Deterministic checks summary
    console.print("\n")
    check_table = Table(title="Deterministic Checks", show_header=True)
    check_table.add_column("Check", style="cyan")
    check_table.add_column("Passed", justify="right", style="green")
    check_table.add_column("Failed", justify="right", style="red")

    check_summary: dict[str, dict[str, int]] = {}
    for c in checks:
        if c.check_name not in check_summary:
            check_summary[c.check_name] = {"passed": 0, "failed": 0}
        if c.passed:
            check_summary[c.check_name]["passed"] += 1
        else:
            check_summary[c.check_name]["failed"] += 1

    for name, counts in sorted(check_summary.items()):
        check_table.add_row(name, str(counts["passed"]), str(counts["failed"]))

    console.print(check_table)

    # Worst queries (lowest NDCG@10)
    ndcg = next((m for m in metrics if m.metric_name == "ndcg@10"), None)
    if ndcg and ndcg.per_query:
        console.print("\n")
        worst = sorted(ndcg.per_query.items(), key=lambda x: x[1])[:10]
        worst_table = Table(title="Worst Performing Queries (NDCG@10)", show_header=True)
        worst_table.add_column("Query", style="cyan")
        worst_table.add_column("NDCG@10", justify="right")

        for query, value in worst:
            worst_table.add_row(query, f"{value:.4f}")

        console.print(worst_table)

    # Agreement
    if agreement:
        console.print("\n")
        console.print("[bold]LLM-Human Agreement[/bold]")
        console.print(f"  Cohen's kappa: {agreement['kappa']:.3f}")
        console.print(f"  Matched pairs: {agreement['n_matched']}")
        console.print(f"  Exact agreement: {agreement['agreement_rate']:.1%}")
        console.print(f"  Calibration: {agreement['calibration']}")

    output = console.file.getvalue()
    return output


def _generate_html(
    metrics: list[MetricResult],
    checks: list[CheckResult],
    agreement: Optional[dict],
    judgments: Optional[list[JudgmentRecord]] = None,
) -> str:
    """Generate an HTML report using Jinja2."""
    template_path = Path(__file__).parent / "templates" / "report.html"
    template_str = template_path.read_text(encoding="utf-8")
    template = Template(template_str)

    # Build check summary
    check_summary: dict[str, dict[str, int]] = {}
    for c in checks:
        if c.check_name not in check_summary:
            check_summary[c.check_name] = {"passed": 0, "failed": 0}
        if c.passed:
            check_summary[c.check_name]["passed"] += 1
        else:
            check_summary[c.check_name]["failed"] += 1

    # Worst queries
    ndcg = next((m for m in metrics if m.metric_name == "ndcg@10"), None)
    worst_queries = []
    if ndcg and ndcg.per_query:
        worst_queries = sorted(ndcg.per_query.items(), key=lambda x: x[1])[:10]

    # Group judgments by query for the drill-down section
    judgments_for_template: list[dict] = []
    if judgments:
        from collections import defaultdict
        grouped: dict[str, list[JudgmentRecord]] = defaultdict(list)
        for j in judgments:
            grouped[j.query].append(j)
        for q in grouped:
            grouped[q].sort(key=lambda j: j.product.position)
        judgments_for_template = [
            {
                "query": q,
                "avg_score": sum(j.score for j in js) / len(js),
                "judgments": js,
            }
            for q, js in sorted(grouped.items())
        ]

    return template.render(
        metrics=metrics,
        check_summary=check_summary,
        worst_queries=worst_queries,
        agreement=agreement,
        is_comparison=False,
        judgments_for_template=judgments_for_template,
        metric_descriptions=METRIC_DESCRIPTIONS,
    )
