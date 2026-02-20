"""A/B comparison report generation."""

from __future__ import annotations

import re
from collections.abc import Mapping
from io import StringIO
from pathlib import Path

from jinja2 import Environment, select_autoescape
from rich.console import Console
from rich.table import Table

from veritail.reporting.single import (
    CHECK_DESCRIPTIONS,
    METRIC_DESCRIPTIONS,
    QUERY_TYPE_DESCRIPTIONS,
    QUERY_TYPE_DISPLAY_NAMES,
    summarize_checks,
)
from veritail.types import CheckResult, CorrectionJudgment, JudgmentRecord, MetricResult

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
    correction_judgments_a: list[CorrectionJudgment] | None = None,
    correction_judgments_b: list[CorrectionJudgment] | None = None,
    sibling_report: str | None = None,
    judgments_a: list[JudgmentRecord] | None = None,
    judgments_b: list[JudgmentRecord] | None = None,
    checks_a: list[CheckResult] | None = None,
    checks_b: list[CheckResult] | None = None,
) -> str:
    """Generate a comparison report for two evaluation configurations.

    Args:
        metrics_a: Metrics from baseline configuration
        metrics_b: Metrics from experimental configuration
        comparison_checks: Cross-configuration check results
        config_a: Name of the baseline configuration
        config_b: Name of the experimental configuration
        format: "terminal" or "html"
        correction_judgments_a: Optional correction judgments for config A
        correction_judgments_b: Optional correction judgments for config B
        sibling_report: Optional relative path to a sibling report.
        judgments_a: Optional LLM judgments for config A (used in HTML)
        judgments_b: Optional LLM judgments for config B (used in HTML)
        checks_a: Optional per-config check results for config A (HTML)
        checks_b: Optional per-config check results for config B (HTML)

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
            sibling_report=sibling_report,
            judgments_a=judgments_a,
            judgments_b=judgments_b,
            checks_a=checks_a,
            checks_b=checks_b,
            correction_judgments_a=correction_judgments_a,
            correction_judgments_b=correction_judgments_b,
        )
    return _generate_terminal(
        metrics_a,
        metrics_b,
        comparison_checks,
        config_a,
        config_b,
        correction_judgments_a=correction_judgments_a,
        correction_judgments_b=correction_judgments_b,
    )


def _generate_terminal(
    metrics_a: list[MetricResult],
    metrics_b: list[MetricResult],
    comparison_checks: list[CheckResult],
    config_a: str,
    config_b: str,
    correction_judgments_a: list[CorrectionJudgment] | None = None,
    correction_judgments_b: list[CorrectionJudgment] | None = None,
) -> str:
    """Generate a rich-formatted terminal comparison report."""
    console = Console(file=StringIO(), width=120)

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
            # Check if both sides have no applicable queries
            a_na = m_a.query_count is not None and m_a.query_count == 0
            b_na = m_b.query_count is not None and m_b.query_count == 0
            if a_na and b_na:
                table.add_row(
                    m_a.metric_name,
                    "[dim]N/A[/dim]",
                    "[dim]N/A[/dim]",
                    "[dim]-[/dim]",
                    "[dim]-[/dim]",
                )
                continue

            def _fmt_value(m: MetricResult) -> str:
                if m.query_count is not None and m.query_count == 0:
                    return "[dim]N/A[/dim]"
                return f"{m.value:.4f}"

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
                _fmt_value(m_a),
                _fmt_value(m_b),
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

    # Correction summary
    has_corrections = correction_judgments_a or correction_judgments_b
    if has_corrections:
        console.print("\n[bold]Query Corrections[/bold]")
        for label, cjs in [
            (config_a, correction_judgments_a),
            (config_b, correction_judgments_b),
        ]:
            if cjs:
                appropriate = sum(1 for c in cjs if c.verdict == "appropriate")
                inappropriate = sum(1 for c in cjs if c.verdict == "inappropriate")
                errored = sum(
                    1 for c in cjs if c.verdict not in ("appropriate", "inappropriate")
                )
                line = (
                    f"  {label}: {len(cjs)} corrected "
                    f"({appropriate} appropriate, {inappropriate} inappropriate"
                )
                if errored:
                    line += f", {errored} errored"
                line += ")"
                console.print(line)

    assert isinstance(console.file, StringIO)
    return console.file.getvalue()


def _generate_html(
    metrics_a: list[MetricResult],
    metrics_b: list[MetricResult],
    comparison_checks: list[CheckResult],
    config_a: str,
    config_b: str,
    run_metadata: Mapping[str, object] | None = None,
    sibling_report: str | None = None,
    judgments_a: list[JudgmentRecord] | None = None,
    judgments_b: list[JudgmentRecord] | None = None,
    checks_a: list[CheckResult] | None = None,
    checks_b: list[CheckResult] | None = None,
    correction_judgments_a: list[CorrectionJudgment] | None = None,
    correction_judgments_b: list[CorrectionJudgment] | None = None,
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
            a_na = m_a.query_count is not None and m_a.query_count == 0
            b_na = m_b.query_count is not None and m_b.query_count == 0
            delta = m_b.value - m_a.value
            pct = (delta / m_a.value * 100) if m_a.value != 0 else 0.0
            comparison_data.append(
                {
                    "name": m_a.metric_name,
                    "value_a": m_a.value,
                    "value_b": m_b.value,
                    "delta": delta,
                    "pct_change": pct,
                    "a_na": a_na,
                    "b_na": b_na,
                }
            )

    shift_checks = [c for c in comparison_checks if c.check_name == "position_shift"]

    # Result set overlap summary
    overlap_summary: dict[str, object] | None = None
    overlap_checks = [c for c in comparison_checks if c.check_name == "result_overlap"]
    if overlap_checks:
        jaccard_values: list[float] = []
        for oc in overlap_checks:
            match = re.search(r"Result overlap: ([\d.]+)", oc.detail)
            if match:
                jaccard_values.append(float(match.group(1)))
        if jaccard_values:
            mean_jaccard = sum(jaccard_values) / len(jaccard_values)
            if mean_jaccard > 0.7:
                interpretation = (
                    "Configs return mostly the same products — differences "
                    "are primarily in ranking order."
                )
            elif mean_jaccard < 0.3:
                interpretation = (
                    "Configs return substantially different products — "
                    "this is a retrieval change, not just a ranking change."
                )
            else:
                interpretation = (
                    "Configs share some products but also retrieve distinct "
                    "results — a mix of retrieval and ranking differences."
                )
            overlap_summary = {
                "mean_jaccard": round(mean_jaccard, 3),
                "interpretation": interpretation,
                "query_count": len(jaccard_values),
            }

    # Win/loss/tie from NDCG@10 per-query deltas
    ndcg_a = next((m for m in metrics_a if m.metric_name == "ndcg@10"), None)
    ndcg_b = next((m for m in metrics_b if m.metric_name == "ndcg@10"), None)

    win_loss: dict[str, object] | None = None
    if ndcg_a and ndcg_b and ndcg_a.per_query and ndcg_b.per_query:
        wins = losses = ties = 0
        for query in ndcg_a.per_query:
            if query in ndcg_b.per_query:
                delta = ndcg_b.per_query[query] - ndcg_a.per_query[query]
                if delta > 0.001:
                    wins += 1
                elif delta < -0.001:
                    losses += 1
                else:
                    ties += 1
        total = wins + losses + ties
        if total > 0:
            win_loss = {
                "wins": wins,
                "losses": losses,
                "ties": ties,
                "total": total,
                "win_pct": round(wins / total * 100, 1),
                "loss_pct": round(losses / total * 100, 1),
                "tie_pct": round(ties / total * 100, 1),
            }

    # NDCG scatter plot (A vs B)
    scatter_plot: dict[str, object] | None = None
    if ndcg_a and ndcg_b and ndcg_a.per_query and ndcg_b.per_query:
        query_type_lookup: dict[str, str] = {}
        for jlist in [judgments_a, judgments_b]:
            if jlist:
                for j in jlist:
                    if j.query not in query_type_lookup and j.query_type:
                        query_type_lookup[j.query] = j.query_type

        type_colors: dict[str, str] = {
            "broad": "#4f6bed",
            "navigational": "#16a34a",
            "long_tail": "#ea580c",
            "attribute": "#8b5cf6",
        }
        default_color = "#6b7280"

        sc_left, sc_right, sc_top, sc_bottom = 50, 480, 20, 450
        sc_w = sc_right - sc_left
        sc_h = sc_bottom - sc_top

        def _ndcg_to_x(val: float) -> float:
            return sc_left + val * sc_w

        def _ndcg_to_y(val: float) -> float:
            return sc_bottom - val * sc_h

        scatter_points: list[dict[str, object]] = []
        observed_types: set[str] = set()
        for query in ndcg_a.per_query:
            if query in ndcg_b.per_query:
                sc_va = ndcg_a.per_query[query]
                sc_vb = ndcg_b.per_query[query]
                qt = query_type_lookup.get(query, "")
                color = type_colors.get(qt, default_color)
                if qt:
                    observed_types.add(qt)
                scatter_points.append(
                    {
                        "x": round(_ndcg_to_x(sc_va), 1),
                        "y": round(_ndcg_to_y(sc_vb), 1),
                        "query": query,
                        "ndcg_a": round(sc_va, 4),
                        "ndcg_b": round(sc_vb, 4),
                        "type": qt or "unknown",
                        "color": color,
                    }
                )

        if scatter_points:
            diag_start_x = round(_ndcg_to_x(0), 1)
            diag_start_y = round(_ndcg_to_y(0), 1)
            diag_end_x = round(_ndcg_to_x(1), 1)
            diag_end_y = round(_ndcg_to_y(1), 1)

            sc_gridlines = [
                {
                    "val": v,
                    "x": round(_ndcg_to_x(v), 1),
                    "y": round(_ndcg_to_y(v), 1),
                }
                for v in [0, 0.25, 0.5, 0.75, 1.0]
            ]

            legend_entries = [
                {"type": qt, "color": type_colors[qt]}
                for qt in sorted(observed_types)
                if qt in type_colors
            ]

            scatter_plot = {
                "points": scatter_points,
                "diag_start_x": diag_start_x,
                "diag_start_y": diag_start_y,
                "diag_end_x": diag_end_x,
                "diag_end_y": diag_end_y,
                "gridlines": sc_gridlines,
                "legend": legend_entries,
                "left": sc_left,
                "right": sc_right,
                "top": sc_top,
                "bottom": sc_bottom,
            }

    # Biggest winners and losers (per-query NDCG@10 deltas)
    winners: list[dict[str, object]] = []
    losers: list[dict[str, object]] = []
    if ndcg_a and ndcg_b and ndcg_a.per_query and ndcg_b.per_query:
        deltas: list[dict[str, object]] = []
        for query in ndcg_a.per_query:
            if query in ndcg_b.per_query:
                d = ndcg_b.per_query[query] - ndcg_a.per_query[query]
                deltas.append(
                    {
                        "query": query,
                        "value_a": ndcg_a.per_query[query],
                        "value_b": ndcg_b.per_query[query],
                        "delta": d,
                    }
                )
        deltas.sort(key=lambda x: float(str(x["delta"])))
        losers = [d for d in deltas if float(str(d["delta"])) < -0.001][:10]
        winners = [d for d in reversed(deltas) if float(str(d["delta"])) > 0.001][:10]

    # Score distributions for side-by-side comparison
    def _score_distribution(
        judgments: list[JudgmentRecord] | None,
    ) -> dict[str, object] | None:
        if not judgments:
            return None
        counts = {0: 0, 1: 0, 2: 0, 3: 0}
        for j in judgments:
            counts[j.score] = counts.get(j.score, 0) + 1
        total = sum(counts.values())
        if total == 0:
            return None
        pcts = {s: round(c / total * 100, 1) for s, c in counts.items()}
        return {"counts": counts, "total": total, "pcts": pcts}

    score_dist_a = _score_distribution(judgments_a)
    score_dist_b = _score_distribution(judgments_b)

    # Mean relevance by position line chart
    def _mean_by_position(
        judgments: list[JudgmentRecord] | None,
    ) -> dict[int, float]:
        if not judgments:
            return {}
        by_pos: dict[int, list[int]] = {}
        for j in judgments:
            pos = j.product.position + 1
            by_pos.setdefault(pos, []).append(j.score)
        return {pos: sum(scores) / len(scores) for pos, scores in by_pos.items()}

    position_line_chart: dict[str, object] | None = None
    means_a = _mean_by_position(judgments_a)
    means_b = _mean_by_position(judgments_b)
    if means_a or means_b:
        all_positions = sorted(set(means_a.keys()) | set(means_b.keys()))
        if all_positions:
            chart_left = 50
            chart_right = 580
            chart_top = 20
            chart_bottom = 240
            chart_w = chart_right - chart_left
            chart_h = chart_bottom - chart_top
            max_score = 3.0
            n_pos = len(all_positions)

            def _pos_to_x(idx: int) -> float:
                if n_pos == 1:
                    return chart_left + chart_w / 2
                return chart_left + idx * chart_w / (n_pos - 1)

            def _score_to_y(score: float) -> float:
                return chart_bottom - (score / max_score) * chart_h

            points_a: list[dict[str, object]] = []
            points_b: list[dict[str, object]] = []
            for idx, pos in enumerate(all_positions):
                x = _pos_to_x(idx)
                if pos in means_a:
                    y = _score_to_y(means_a[pos])
                    points_a.append(
                        {
                            "x": round(x, 1),
                            "y": round(y, 1),
                            "pos": pos,
                            "score": round(means_a[pos], 2),
                        }
                    )
                if pos in means_b:
                    y = _score_to_y(means_b[pos])
                    points_b.append(
                        {
                            "x": round(x, 1),
                            "y": round(y, 1),
                            "pos": pos,
                            "score": round(means_b[pos], 2),
                        }
                    )

            polyline_a = (
                " ".join(f"{p['x']},{p['y']}" for p in points_a) if points_a else ""
            )
            polyline_b = (
                " ".join(f"{p['x']},{p['y']}" for p in points_b) if points_b else ""
            )

            gridlines = [
                {"y": round(_score_to_y(s), 1), "label": s} for s in [0, 1, 2, 3]
            ]
            x_ticks = [
                {"x": round(_pos_to_x(idx), 1), "label": pos}
                for idx, pos in enumerate(all_positions)
            ]

            position_line_chart = {
                "points_a": points_a,
                "points_b": points_b,
                "polyline_a": polyline_a,
                "polyline_b": polyline_b,
                "gridlines": gridlines,
                "x_ticks": x_ticks,
                "chart_left": chart_left,
                "chart_right": chart_right,
                "chart_top": chart_top,
                "chart_bottom": chart_bottom,
            }

    # Metrics by query type comparison
    all_types: set[str] = set()
    for m in metrics_a + metrics_b:
        all_types.update(m.by_query_type.keys())
    query_types = sorted(all_types)

    type_comparison: list[dict[str, object]] = []
    if query_types:
        for m_a in metrics_a:
            m_b = metrics_b_lookup.get(m_a.metric_name)
            if m_b:
                per_type: dict[str, dict[str, float | None]] = {}
                for qt in query_types:
                    va = m_a.by_query_type.get(qt)
                    vb = m_b.by_query_type.get(qt)
                    qt_delta: float | None = (
                        (vb - va) if va is not None and vb is not None else None
                    )
                    per_type[qt] = {"value_a": va, "value_b": vb, "delta": qt_delta}
                type_comparison.append({"name": m_a.metric_name, "types": per_type})

    # Deterministic checks comparison
    check_comparison: list[dict[str, object]] = []
    if checks_a or checks_b:
        summary_a = dict(summarize_checks(checks_a or []))
        summary_b = dict(summarize_checks(checks_b or []))
        all_check_names: list[str] = list(summary_a.keys())
        for name in summary_b:
            if name not in summary_a:
                all_check_names.append(name)
        for name in all_check_names:
            a_data = summary_a.get(name)
            b_data = summary_b.get(name)
            display = (
                str(a_data["display_name"])
                if a_data
                else str(b_data["display_name"])
                if b_data
                else name
            )
            failed_a = int(a_data["failed"]) if a_data else 0
            failed_b = int(b_data["failed"]) if b_data else 0
            check_comparison.append(
                {
                    "name": name,
                    "display_name": display,
                    "failed_a": failed_a,
                    "failed_b": failed_b,
                    "delta": failed_b - failed_a,
                }
            )

    # Correction data for side-by-side tables
    def _build_correction_data(
        cjs: list[CorrectionJudgment] | None,
    ) -> list[dict[str, str]]:
        if not cjs:
            return []
        return [
            {
                "original_query": c.original_query,
                "corrected_query": c.corrected_query,
                "verdict": c.verdict,
                "reasoning": c.reasoning,
            }
            for c in cjs
        ]

    correction_data_a = _build_correction_data(correction_judgments_a)
    correction_data_b = _build_correction_data(correction_judgments_b)

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
        sibling_report=sibling_report,
        win_loss=win_loss,
        overlap_summary=overlap_summary,
        scatter_plot=scatter_plot,
        score_dist_a=score_dist_a,
        score_dist_b=score_dist_b,
        position_line_chart=position_line_chart,
        type_comparison=type_comparison,
        query_types=query_types,
        query_type_display_names=QUERY_TYPE_DISPLAY_NAMES,
        query_type_descriptions=QUERY_TYPE_DESCRIPTIONS,
        metric_descriptions=METRIC_DESCRIPTIONS,
        check_comparison=check_comparison,
        check_descriptions=CHECK_DESCRIPTIONS,
        correction_data_a=correction_data_a,
        correction_data_b=correction_data_b,
        winners=winners,
        losers=losers,
    )
