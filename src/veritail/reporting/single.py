"""Single-configuration report generation."""

from __future__ import annotations

import statistics
from collections.abc import Mapping
from io import StringIO
from pathlib import Path

from jinja2 import Environment, select_autoescape
from rich.console import Console
from rich.table import Table

from veritail.types import (
    CheckResult,
    CorrectionJudgment,
    JudgmentRecord,
    MetricResult,
)

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

QUERY_TYPE_DISPLAY_NAMES: dict[str, str] = {
    "long_tail": "long-tail",
}

QUERY_TYPE_DESCRIPTIONS: dict[str, str] = {
    "attribute": (
        "Queries that filter by a specific product attribute "
        "such as color, size, material, or brand"
    ),
    "broad": (
        "General category queries with wide intent that could match many products"
    ),
    "long_tail": (
        "Highly specific, multi-word queries that target a narrow set of products"
    ),
    "navigational": (
        "Queries searching for a specific brand, product line, or known item by name"
    ),
}

CHECK_DESCRIPTIONS: dict[str, str] = {
    "zero_results": ("Fails when a query returns no results at all"),
    "result_count": (
        "Fails when a query returns fewer results than "
        "the expected minimum (default: 3)"
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
    "correction_vocabulary": (
        "Checks if corrected query terms appear in any "
        "returned product title or description"
    ),
    "unnecessary_correction": (
        "Flags corrections where original query terms "
        "still appear in the corrected result set"
    ),
}

FAILURE_ONLY_CHECKS: set[str] = {"duplicate"}
CHECK_DISPLAY_NAMES: dict[str, str] = {
    "duplicate": "duplicate (flagged pairs)",
}

# Display order for the deterministic checks table.  Checks not listed
# here (e.g. custom checks) are appended alphabetically at the end.
CHECK_ORDER: list[str] = [
    "duplicate",
    "out_of_stock_prominence",
    "price_outlier",
    "result_count",
    "zero_results",
    "title_length",
    "text_overlap",
    "correction_vocabulary",
    "unnecessary_correction",
]


_MAX_FAILURES_PER_CHECK = 50


def _build_check_failures(
    checks: list[CheckResult],
) -> dict[str, dict[str, object]]:
    """Group failed CheckResults by check_name for drill-down display.

    Returns a mapping of check_name → {"items": [...], "total": int}.
    Each item has keys: query, product_id, detail, severity.
    Capped at ``_MAX_FAILURES_PER_CHECK`` items per check.
    """
    failures: dict[str, list[dict[str, str | None]]] = {}
    totals: dict[str, int] = {}
    for c in checks:
        if c.passed:
            continue
        totals[c.check_name] = totals.get(c.check_name, 0) + 1
        if c.check_name not in failures:
            failures[c.check_name] = []
        if len(failures[c.check_name]) < _MAX_FAILURES_PER_CHECK:
            failures[c.check_name].append(
                {
                    "query": c.query,
                    "product_id": c.product_id,
                    "detail": c.detail,
                    "severity": c.severity,
                }
            )
    return {
        name: {"entries": items, "total": totals[name]}
        for name, items in failures.items()
    }


def summarize_checks(
    checks: list[CheckResult],
) -> list[tuple[str, dict[str, str | int | bool]]]:
    """Build a display-ready, ordered check summary for reports."""
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

    order_index = {name: i for i, name in enumerate(CHECK_ORDER)}
    fallback = len(CHECK_ORDER)
    ordered = sorted(
        summary.items(),
        key=lambda item: (order_index.get(item[0], fallback), item[0]),
    )
    return ordered


def generate_single_report(
    metrics: list[MetricResult],
    checks: list[CheckResult],
    format: str = "terminal",
    judgments: list[JudgmentRecord] | None = None,
    run_metadata: Mapping[str, object] | None = None,
    correction_judgments: list[CorrectionJudgment] | None = None,
    sibling_report: str | None = None,
) -> str:
    """Generate a report for a single evaluation configuration.

    Args:
        metrics: Computed IR metrics
        checks: Deterministic check results
        format: "terminal" for rich console output, "html" for HTML file
        judgments: Optional list of per-product LLM judgments (used in HTML output)
        correction_judgments: Optional list of correction judgments
        sibling_report: Optional relative path to a sibling report (e.g.
            autocomplete-report.html) to render as a cross-link banner.

    Returns:
        Formatted report string.
    """
    if format == "html":
        return _generate_html(
            metrics,
            checks,
            judgments,
            run_metadata,
            correction_judgments,
            sibling_report=sibling_report,
        )
    return _generate_terminal(
        metrics, checks, correction_judgments, judgments=judgments
    )


def _generate_terminal(
    metrics: list[MetricResult],
    checks: list[CheckResult],
    correction_judgments: list[CorrectionJudgment] | None = None,
    judgments: list[JudgmentRecord] | None = None,
) -> str:
    """Generate a rich-formatted terminal report."""
    console = Console(file=StringIO(), width=100)

    console.print("\n[bold]Search Evaluation Report[/bold]\n")

    # Metrics table
    table = Table(title="IR Metrics", show_header=True)
    table.add_column("Metric", style="cyan")
    table.add_column("Value", justify="right")

    for m in metrics:
        if m.query_count is not None and m.query_count == 0:
            table.add_row(
                m.metric_name,
                "[dim]N/A (no queries with attribute constraints)[/dim]",
            )
        elif (
            m.query_count is not None
            and m.total_queries is not None
            and m.query_count < m.total_queries
        ):
            table.add_row(
                m.metric_name,
                f"{m.value:.4f}  [dim](n={m.query_count} of"
                f" {m.total_queries} queries)[/dim]",
            )
        else:
            table.add_row(m.metric_name, f"{m.value:.4f}")

    console.print(table)

    # Score distribution
    if judgments:
        score_counts: dict[int, int] = {0: 0, 1: 0, 2: 0, 3: 0}
        for jdg in judgments:
            score_counts[jdg.score] = score_counts.get(jdg.score, 0) + 1
        total_judgments = sum(score_counts.values())
        if total_judgments > 0:
            console.print("\n")
            score_table = Table(
                title=f"Score Distribution ({total_judgments} judgments)",
                show_header=True,
            )
            score_table.add_column("Score", style="cyan")
            score_table.add_column("Count", justify="right")
            score_table.add_column("%", justify="right")
            for sc in (3, 2, 1, 0):
                pct = score_counts[sc] / total_judgments * 100
                score_table.add_row(f"{sc}/3", str(score_counts[sc]), f"{pct:.1f}%")
            console.print(score_table)

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

        sorted_types = sorted(all_types)
        for qt in sorted_types:
            display = QUERY_TYPE_DISPLAY_NAMES.get(qt, qt)
            type_table.add_column(display, justify="right")

        for m in type_metrics:
            row = [m.metric_name]
            for qt in sorted_types:
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

    check_summary = summarize_checks(checks)

    for _, counts in check_summary:
        check_table.add_row(
            str(counts["display_name"]),
            str(counts["passed_display"]),
            str(counts["failed"]),
        )

    console.print(check_table)

    # Query Corrections table
    if correction_judgments:
        console.print("\n")
        corr_table = Table(title="Query Corrections", show_header=True)
        corr_table.add_column("Original Query", style="cyan")
        corr_table.add_column("Corrected Query")
        corr_table.add_column("Verdict", justify="center")
        corr_table.add_column("Reasoning")

        for cj in correction_judgments:
            verdict_style = (
                "[green]appropriate[/green]"
                if cj.verdict == "appropriate"
                else (
                    "[red]inappropriate[/red]"
                    if cj.verdict == "inappropriate"
                    else f"[yellow]{cj.verdict}[/yellow]"
                )
            )
            corr_table.add_row(
                cj.original_query,
                cj.corrected_query,
                verdict_style,
                cj.reasoning,
            )

        console.print(corr_table)

    # Worst queries (lowest NDCG@10)
    ndcg = next((m for m in metrics if m.metric_name == "ndcg@10"), None)
    if ndcg and ndcg.per_query:
        ndcg_values = list(ndcg.per_query.values())
        if len(ndcg_values) >= 2:
            console.print(
                f"\n  [dim]NDCG@10 spread:"
                f"  min={min(ndcg_values):.4f}"
                f"  median={statistics.median(ndcg_values):.4f}"
                f"  max={max(ndcg_values):.4f}"
                f"  stdev={statistics.stdev(ndcg_values):.4f}[/dim]"
            )
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
    correction_judgments: list[CorrectionJudgment] | None = None,
    sibling_report: str | None = None,
) -> str:
    """Generate an HTML report using Jinja2."""
    tmpl_dir = Path(__file__).parent / "templates"
    template_path = tmpl_dir / "report.html"
    template_str = template_path.read_text(encoding="utf-8")
    template = _JINJA_ENV.from_string(template_str)

    # Build check summary
    check_summary = summarize_checks(checks)
    check_failures = _build_check_failures(checks)

    # Worst queries
    ndcg = next(
        (m for m in metrics if m.metric_name == "ndcg@10"),
        None,
    )
    worst_queries: list[dict[str, object]] = []

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

    # Build correction lookup by original query
    correction_lookup: dict[str, CorrectionJudgment] = {}
    correction_summary: list[dict[str, str]] = []
    if correction_judgments:
        for cj in correction_judgments:
            correction_lookup[cj.original_query] = cj
            correction_summary.append(
                {
                    "original_query": cj.original_query,
                    "corrected_query": cj.corrected_query,
                    "verdict": cj.verdict,
                    "reasoning": cj.reasoning,
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
        unsorted = [
            {
                "query": q,
                "avg_score": sum(j.score for j in js) / len(js),
                "judgments": js,
                "correction": correction_lookup.get(q),
            }
            for q, js in grouped.items()
        ]
        judgments_for_template = sorted(
            unsorted,  # type: ignore[arg-type]
            key=lambda x: float(x["avg_score"]),  # type: ignore[arg-type]
        )

    # Enriched worst queries (needs judgments_for_template for anchors)
    if ndcg and ndcg.per_query:
        query_type_lookup: dict[str, str] = {}
        if judgments:
            for j in judgments:
                if j.query not in query_type_lookup and j.query_type:
                    query_type_lookup[j.query] = j.query_type

        per_query_failed_checks: dict[str, int] = {}
        for c in checks:
            if not c.passed:
                per_query_failed_checks[c.query] = (
                    per_query_failed_checks.get(c.query, 0) + 1
                )

        query_anchor_map: dict[str, str] = {}
        for idx, item in enumerate(judgments_for_template):
            query_anchor_map[str(item["query"])] = f"query-{idx}"

        sorted_ndcg = sorted(ndcg.per_query.items(), key=lambda x: x[1])[:10]
        worst_queries = [
            {
                "query": q,
                "ndcg": v,
                "query_type": QUERY_TYPE_DISPLAY_NAMES.get(
                    query_type_lookup.get(q, ""), query_type_lookup.get(q, "")
                ),
                "failed_checks": per_query_failed_checks.get(q, 0),
                "anchor_id": query_anchor_map.get(q, ""),
            }
            for q, v in sorted_ndcg
        ]

    # Score distribution
    score_counts: dict[int, int] | None = None
    score_total: int = 0
    score_pcts: dict[int, float] | None = None
    if judgments:
        score_counts = {0: 0, 1: 0, 2: 0, 3: 0}
        for j in judgments:
            score_counts[j.score] = score_counts.get(j.score, 0) + 1
        score_total = sum(score_counts.values())
        if score_total > 0:
            score_pcts = {
                s: round(c / score_total * 100, 1) for s, c in score_counts.items()
            }
        else:
            score_counts = None

    # NDCG@10 distribution stats
    ndcg_stats: dict[str, float] | None = None
    if ndcg and ndcg.per_query:
        pq_values = list(ndcg.per_query.values())
        if len(pq_values) >= 2:
            ndcg_stats = {
                "min": min(pq_values),
                "max": max(pq_values),
                "median": statistics.median(pq_values),
                "stdev": statistics.stdev(pq_values),
            }

    # Score by position chart
    position_chart: list[dict[str, object]] | None = None
    if judgments:
        pos_scores: dict[int, list[int]] = defaultdict(list)
        for j in judgments:
            pos_scores[j.product.position + 1].append(j.score)
        if len(pos_scores) >= 2:
            sorted_positions = sorted(pos_scores.keys())
            n = len(sorted_positions)
            chart_inner_w = 640.0
            chart_inner_h = 150.0
            gap = 6.0
            bar_w = min(56.0, max(20.0, (chart_inner_w - gap * max(1, n - 1)) / n))
            total_w = n * bar_w + (n - 1) * gap
            x_start = 40.0 + (chart_inner_w - total_w) / 2.0
            bars: list[dict[str, object]] = []
            for i, pos in enumerate(sorted_positions):
                sc = pos_scores[pos]
                avg = sum(sc) / len(sc)
                bar_h = max(2.0, (avg / 3.0) * chart_inner_h)
                if avg > 2.25:
                    color = "#16a34a"
                elif avg > 1.5:
                    color = "#ca8a04"
                elif avg > 0.75:
                    color = "#ea580c"
                else:
                    color = "#dc2626"
                bars.append(
                    {
                        "position": pos,
                        "avg_score": avg,
                        "count": len(sc),
                        "x": round(x_start + i * (bar_w + gap), 1),
                        "y": round(15.0 + chart_inner_h - bar_h, 1),
                        "width": round(bar_w, 1),
                        "height": round(bar_h, 1),
                        "color": color,
                        "label_y": round(15.0 + chart_inner_h - bar_h - 5, 1),
                    }
                )
            position_chart = bars

    # Metrics by query type
    type_metrics = [m for m in metrics if m.by_query_type]
    query_types: list[str] = []
    if type_metrics:
        all_types: set[str] = set()
        for m in type_metrics:
            all_types.update(m.by_query_type.keys())
        query_types = sorted(all_types)

    return template.render(
        metrics=metrics,
        check_summary=check_summary,
        worst_queries=worst_queries,
        is_comparison=False,
        judgments_for_template=judgments_for_template,
        metric_descriptions=METRIC_DESCRIPTIONS,
        check_descriptions=CHECK_DESCRIPTIONS,
        check_failures=check_failures,
        run_metadata_rows=metadata_rows,
        correction_summary=correction_summary,
        score_counts=score_counts,
        score_total=score_total,
        score_pcts=score_pcts,
        ndcg_stats=ndcg_stats,
        position_chart=position_chart,
        type_metrics=type_metrics,
        query_types=query_types,
        query_type_display_names=QUERY_TYPE_DISPLAY_NAMES,
        query_type_descriptions=QUERY_TYPE_DESCRIPTIONS,
        sibling_report=sibling_report,
    )
