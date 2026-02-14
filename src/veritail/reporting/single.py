"""Single-configuration report generation."""

from __future__ import annotations

from collections.abc import Mapping
from io import StringIO
from pathlib import Path

from jinja2 import Environment, select_autoescape
from rich.console import Console
from rich.table import Table

from veritail.types import CheckResult, JudgmentRecord, MetricResult

_JINJA_ENV = Environment(
    autoescape=select_autoescape(("html", "xml"), default_for_string=True),
)

METRIC_DESCRIPTIONS: dict[str, str] = {
    "ndcg@5": (
        "Ranking quality at top 5 — rewards placing the "
        "most relevant products highest (graded 0-3)"
    ),
    "ndcg@10": (
        "Ranking quality at top 10 — rewards placing the "
        "most relevant products highest (graded 0-3)"
    ),
    "mrr": (
        "Mean Reciprocal Rank — how high up the first "
        "relevant result appears (1.0 = first position)"
    ),
    "map": ("Mean Average Precision — overall precision across all relevant results"),
    "p@5": (
        "Precision at 5 — fraction of top 5 results that are relevant (score >= 2)"
    ),
    "p@10": (
        "Precision at 10 — fraction of top 10 results that are relevant (score >= 2)"
    ),
    "attribute_match@5": (
        "Fraction of top-5 results where LLM-judged attributes"
        " match or partially match the query"
        " (excludes queries with no attribute constraints)"
    ),
    "attribute_match@10": (
        "Fraction of top-10 results where LLM-judged attributes"
        " match or partially match the query"
        " (excludes queries with no attribute constraints)"
    ),
}

CHECK_DESCRIPTIONS: dict[str, str] = {
    "zero_results": ("Fails when a query returns no results at all"),
    "result_count": (
        "Fails when a query returns fewer results than "
        "the expected minimum (default: 3)"
    ),
    "category_alignment": (
        "Checks if each result's category matches the "
        "expected or majority category in the result set"
    ),
    "text_overlap": (
        "Measures keyword overlap between the query and "
        "each result's title, category, and description"
    ),
    "price_outlier": (
        "Flags results with prices far outside the "
        "result set's normal range using the IQR method"
    ),
    "duplicate": (
        "Detects near-duplicate products in results based on title similarity"
    ),
    "title_length": (
        "Flags titles that are unusually long "
        "(> 120 chars, possible SEO stuffing) or short "
        "(< 10 chars, possibly malformed)"
    ),
    "out_of_stock_prominence": (
        "Flags out-of-stock products ranked too high "
        "(position 1 = fail, positions 2-5 = warning)"
    ),
}

FAILURE_ONLY_CHECKS: set[str] = {"duplicate"}
CHECK_DISPLAY_NAMES: dict[str, str] = {
    "duplicate": "duplicate (flagged pairs)",
}


def _summarize_checks(
    checks: list[CheckResult],
) -> dict[str, dict[str, str | int | bool]]:
    """Build a display-ready check summary for reports."""
    summary: dict[str, dict[str, str | int | bool]] = {}
    for c in checks:
        if c.check_name not in summary:
            summary[c.check_name] = {
                "display_name": CHECK_DISPLAY_NAMES.get(c.check_name, c.check_name),
                "passed": 0,
                "failed": 0,
                "passed_display": "0",
                "passed_is_na": False,
            }

        if c.passed:
            summary[c.check_name]["passed"] = int(summary[c.check_name]["passed"]) + 1
        else:
            summary[c.check_name]["failed"] = int(summary[c.check_name]["failed"]) + 1

    for check_name, counts in summary.items():
        passed = int(counts["passed"])
        is_failure_only = check_name in FAILURE_ONLY_CHECKS and passed == 0
        counts["passed_is_na"] = is_failure_only
        counts["passed_display"] = "n/a" if is_failure_only else str(passed)

    return summary


def generate_single_report(
    metrics: list[MetricResult],
    checks: list[CheckResult],
    format: str = "terminal",
    judgments: list[JudgmentRecord] | None = None,
    run_metadata: Mapping[str, object] | None = None,
) -> str:
    """Generate a report for a single evaluation configuration.

    Args:
        metrics: Computed IR metrics
        checks: Deterministic check results
        format: "terminal" for rich console output, "html" for HTML file
        judgments: Optional list of per-product LLM judgments (used in HTML output)

    Returns:
        Formatted report string.
    """
    if format == "html":
        return _generate_html(metrics, checks, judgments, run_metadata)
    return _generate_terminal(metrics, checks)


def _generate_terminal(
    metrics: list[MetricResult],
    checks: list[CheckResult],
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

    check_summary = _summarize_checks(checks)

    for _, counts in sorted(check_summary.items()):
        check_table.add_row(
            str(counts["display_name"]),
            str(counts["passed_display"]),
            str(counts["failed"]),
        )

    console.print(check_table)

    # Worst queries (lowest NDCG@10)
    ndcg = next((m for m in metrics if m.metric_name == "ndcg@10"), None)
    if ndcg and ndcg.per_query:
        console.print("\n")
        worst = sorted(ndcg.per_query.items(), key=lambda x: x[1])[:10]
        worst_table = Table(
            title="Worst Performing Queries (NDCG@10)",
            show_header=True,
        )
        worst_table.add_column("Query", style="cyan")
        worst_table.add_column("NDCG@10", justify="right")

        for query, value in worst:
            worst_table.add_row(query, f"{value:.4f}")

        console.print(worst_table)

    assert isinstance(console.file, StringIO)
    return console.file.getvalue()


def _generate_html(
    metrics: list[MetricResult],
    checks: list[CheckResult],
    judgments: list[JudgmentRecord] | None = None,
    run_metadata: Mapping[str, object] | None = None,
) -> str:
    """Generate an HTML report using Jinja2."""
    tmpl_dir = Path(__file__).parent / "templates"
    template_path = tmpl_dir / "report.html"
    template_str = template_path.read_text(encoding="utf-8")
    template = _JINJA_ENV.from_string(template_str)

    # Build check summary
    check_summary = _summarize_checks(checks)

    # Worst queries
    ndcg = next(
        (m for m in metrics if m.metric_name == "ndcg@10"),
        None,
    )
    worst_queries = []
    if ndcg and ndcg.per_query:
        worst_queries = sorted(
            ndcg.per_query.items(),
            key=lambda x: x[1],
        )[:10]

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

    # Group judgments by query for the drill-down section
    judgments_for_template: list[dict[str, object]] = []
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
        is_comparison=False,
        judgments_for_template=judgments_for_template,
        metric_descriptions=METRIC_DESCRIPTIONS,
        check_descriptions=CHECK_DESCRIPTIONS,
        run_metadata_rows=metadata_rows,
    )
