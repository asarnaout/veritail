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
    PrefixEntry,
    SuggestionJudgment,
)

_JINJA_ENV = Environment(
    autoescape=select_autoescape(("html", "xml"), default_for_string=True),
)

CHECK_DESCRIPTIONS: dict[str, str] = {
    "empty_suggestions": "Fails when a prefix returns no suggestions at all",
    "duplicate_suggestion": "Detects duplicate suggestions in the response",
    "prefix_coherence": (
        "Verifies suggestions start with or share tokens with the prefix"
    ),
    "offensive_content": "Flags suggestions containing blocked terms",
    "suggestion_overlap": "Jaccard overlap of suggestions between two configurations",
    "rank_agreement": "Spearman rank correlation of shared suggestions",
    "encoding_issues": (
        "Flags HTML entities, control characters, and leading/trailing whitespace"
    ),
    "length_anomaly": "Flags suggestions shorter than 2 chars or longer than 80 chars",
    "latency": "Checks whether adapter response time exceeds a threshold",
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
    checks: list[CheckResult],
    format: str = "terminal",
    responses_by_prefix: dict[int, AutocompleteResponse] | None = None,
    prefixes: list[PrefixEntry] | None = None,
    run_metadata: Mapping[str, object] | None = None,
    sibling_report: str | None = None,
    suggestion_judgments: list[SuggestionJudgment] | None = None,
) -> str:
    """Generate a report for a single autocomplete evaluation.

    Args:
        checks: Deterministic check results.
        format: "terminal" for rich console output, "html" for HTML file.
        responses_by_prefix: Optional mapping of prefix index to responses.
        prefixes: Optional list of prefix entries.
        run_metadata: Optional provenance metadata.
        sibling_report: Optional relative path to a sibling report.
        suggestion_judgments: Optional LLM suggestion judgments.

    Returns:
        Formatted report string.
    """
    if format == "html":
        return _generate_html(
            checks,
            responses_by_prefix,
            prefixes,
            run_metadata,
            sibling_report,
            suggestion_judgments,
        )
    return _generate_terminal(
        checks, responses_by_prefix, prefixes, suggestion_judgments
    )


def generate_autocomplete_comparison_report(
    checks_a: list[CheckResult],
    checks_b: list[CheckResult],
    comparison_checks: list[CheckResult],
    config_a: str,
    config_b: str,
    format: str = "terminal",
    run_metadata: Mapping[str, object] | None = None,
    sibling_report: str | None = None,
) -> str:
    """Generate a comparison report for two autocomplete configurations."""
    if format == "html":
        return _generate_comparison_html(
            checks_a,
            checks_b,
            comparison_checks,
            config_a,
            config_b,
            run_metadata,
            sibling_report,
        )
    return _generate_comparison_terminal(
        checks_a, checks_b, comparison_checks, config_a, config_b
    )


def _generate_terminal(
    checks: list[CheckResult],
    responses_by_prefix: dict[int, AutocompleteResponse] | None = None,
    prefixes: list[PrefixEntry] | None = None,
    suggestion_judgments: list[SuggestionJudgment] | None = None,
) -> str:
    """Generate a rich-formatted terminal report."""
    con = Console(file=StringIO(), force_terminal=True, width=100)

    con.print("\n[bold]Autocomplete Evaluation Report[/bold]\n")

    # Checks summary
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

    # Failed checks detail
    failed_checks = [c for c in checks if not c.passed]
    if failed_checks:
        con.print("\n")
        fail_table = Table(title="Failed Checks", show_header=True)
        fail_table.add_column("Prefix", style="cyan")
        fail_table.add_column("Check")
        fail_table.add_column("Detail", style="dim")
        for c in failed_checks[:20]:
            fail_table.add_row(c.query, c.check_name, c.detail)
        if len(failed_checks) > 20:
            con.print(f"[dim]  ... and {len(failed_checks) - 20} more[/dim]")
        con.print(fail_table)

    # LLM Suggestion Quality
    if suggestion_judgments is not None:
        con.print("\n")
        avg_rel = (
            sum(j.relevance_score for j in suggestion_judgments)
            / len(suggestion_judgments)
            if suggestion_judgments
            else 0.0
        )
        avg_div = (
            sum(j.diversity_score for j in suggestion_judgments)
            / len(suggestion_judgments)
            if suggestion_judgments
            else 0.0
        )
        total_flagged = sum(len(j.flagged_suggestions) for j in suggestion_judgments)

        llm_table = Table(title="LLM Suggestion Quality", show_header=True)
        llm_table.add_column("Metric", style="cyan")
        llm_table.add_column("Value", justify="right")
        llm_table.add_row("Avg Relevance", f"{avg_rel:.2f}/3")
        llm_table.add_row("Avg Diversity", f"{avg_div:.2f}/3")
        llm_table.add_row("Prefixes Evaluated", str(len(suggestion_judgments)))
        llm_table.add_row("Total Flagged", str(total_flagged))
        con.print(llm_table)

        # Flagged suggestions detail
        flagged_judgments = [j for j in suggestion_judgments if j.flagged_suggestions]
        if flagged_judgments:
            con.print("\n")
            flag_table = Table(title="Flagged Suggestions", show_header=True)
            flag_table.add_column("Prefix", style="cyan")
            flag_table.add_column("Flagged")
            flag_table.add_column("Reasoning", style="dim")
            for j in flagged_judgments[:20]:
                flag_table.add_row(
                    j.prefix,
                    ", ".join(j.flagged_suggestions),
                    j.reasoning,
                )
            if len(flagged_judgments) > 20:
                con.print(f"[dim]  ... and {len(flagged_judgments) - 20} more[/dim]")
            con.print(flag_table)

        # Lowest relevance scores
        sorted_by_rel = sorted(suggestion_judgments, key=lambda j: j.relevance_score)
        lowest = sorted_by_rel[:5]
        if lowest:
            con.print("\n")
            low_table = Table(title="Lowest Relevance Scores", show_header=True)
            low_table.add_column("Prefix", style="cyan")
            low_table.add_column("Rel", justify="right")
            low_table.add_column("Div", justify="right")
            low_table.add_column("Reasoning", style="dim")
            for j in lowest:
                low_table.add_row(
                    j.prefix,
                    str(j.relevance_score),
                    str(j.diversity_score),
                    j.reasoning,
                )
            con.print(low_table)

    # Per-prefix drill-down
    if prefixes and responses_by_prefix:
        # Build judgment lookup by prefix
        judgment_by_prefix: dict[str, SuggestionJudgment] = {}
        if suggestion_judgments:
            for j in suggestion_judgments:
                judgment_by_prefix[j.prefix] = j

        con.print("\n")
        drill_table = Table(title="Per-Prefix Results", show_header=True)
        drill_table.add_column("Prefix", style="cyan")
        drill_table.add_column("Type", style="dim")
        drill_table.add_column("Suggestions", style="dim")
        drill_table.add_column("Failed Checks", justify="right", style="red")
        if suggestion_judgments is not None:
            drill_table.add_column("Rel", justify="right")
            drill_table.add_column("Div", justify="right")

        prefix_failures: dict[str, int] = {}
        for c in checks:
            if not c.passed:
                prefix_failures[c.query] = prefix_failures.get(c.query, 0) + 1

        for idx, entry in enumerate(prefixes):
            resp = responses_by_prefix.get(idx)
            sug_str = ", ".join(resp.suggestions[:5]) if resp else "(none)"
            if resp and len(resp.suggestions) > 5:
                sug_str += f" (+{len(resp.suggestions) - 5} more)"
            fail_count = prefix_failures.get(entry.prefix, 0)
            row: list[str] = [
                entry.prefix,
                entry.type or "",
                sug_str,
                str(fail_count) if fail_count else "",
            ]
            if suggestion_judgments is not None:
                sj = judgment_by_prefix.get(entry.prefix)
                row.append(str(sj.relevance_score) if sj else "")
                row.append(str(sj.diversity_score) if sj else "")
            drill_table.add_row(*row)
        con.print(drill_table)

    assert isinstance(con.file, StringIO)
    return con.file.getvalue()


def _generate_comparison_terminal(
    checks_a: list[CheckResult],
    checks_b: list[CheckResult],
    comparison_checks: list[CheckResult],
    config_a: str,
    config_b: str,
) -> str:
    """Generate a rich-formatted terminal comparison report."""
    con = Console(file=StringIO(), force_terminal=True, width=120)

    con.print(f"\n[bold]Autocomplete Comparison: '{config_a}' vs '{config_b}'[/bold]\n")

    # Check summaries side-by-side
    summary_a = _summarize_checks(checks_a)
    summary_b = _summarize_checks(checks_b)
    all_check_names = sorted(set(summary_a.keys()) | set(summary_b.keys()))

    table = Table(title="Check Summary Comparison", show_header=True)
    table.add_column("Check", style="cyan")
    table.add_column(f"{config_a} Passed", justify="right")
    table.add_column(f"{config_a} Failed", justify="right", style="red")
    table.add_column(f"{config_b} Passed", justify="right")
    table.add_column(f"{config_b} Failed", justify="right", style="red")

    for name in all_check_names:
        sa = summary_a.get(name, {"passed_display": "-", "failed": "-"})
        sb = summary_b.get(name, {"passed_display": "-", "failed": "-"})
        table.add_row(
            name,
            str(sa["passed_display"]),
            str(sa["failed"]),
            str(sb["passed_display"]),
            str(sb["failed"]),
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
    checks: list[CheckResult],
    responses_by_prefix: dict[int, AutocompleteResponse] | None = None,
    prefixes: list[PrefixEntry] | None = None,
    run_metadata: Mapping[str, object] | None = None,
    sibling_report: str | None = None,
    suggestion_judgments: list[SuggestionJudgment] | None = None,
) -> str:
    """Generate an HTML report using Jinja2."""
    tmpl_dir = Path(__file__).resolve().parent.parent / "reporting" / "templates"
    template_path = tmpl_dir / "autocomplete_report.html"
    template_str = template_path.read_text(encoding="utf-8")
    template = _JINJA_ENV.from_string(template_str)

    check_summary = _summarize_checks(checks)

    # Build judgment lookup by prefix
    judgment_by_prefix: dict[str, SuggestionJudgment] = {}
    if suggestion_judgments:
        for j in suggestion_judgments:
            judgment_by_prefix[j.prefix] = j

    # Per-prefix drill-down
    prefix_details: list[dict[str, object]] = []
    prefix_failures: dict[str, list[CheckResult]] = {}
    for c in checks:
        if not c.passed:
            prefix_failures.setdefault(c.query, []).append(c)

    if prefixes and responses_by_prefix:
        for i, entry in enumerate(prefixes):
            resp = responses_by_prefix.get(i)
            detail: dict[str, object] = {
                "prefix": entry.prefix,
                "type": entry.type or "",
                "suggestions": resp.suggestions if resp else [],
                "failed_checks": [
                    {"name": c.check_name, "detail": c.detail}
                    for c in prefix_failures.get(entry.prefix, [])
                ],
            }
            sj = judgment_by_prefix.get(entry.prefix)
            if sj:
                detail["relevance_score"] = sj.relevance_score
                detail["diversity_score"] = sj.diversity_score
                detail["flagged_suggestions"] = sj.flagged_suggestions
                detail["llm_reasoning"] = sj.reasoning
            else:
                detail["relevance_score"] = None
                detail["diversity_score"] = None
                detail["flagged_suggestions"] = []
                detail["llm_reasoning"] = ""
            prefix_details.append(detail)

    # LLM summary
    llm_summary: dict[str, object] | None = None
    if suggestion_judgments is not None:
        avg_rel = (
            sum(j.relevance_score for j in suggestion_judgments)
            / len(suggestion_judgments)
            if suggestion_judgments
            else 0.0
        )
        avg_div = (
            sum(j.diversity_score for j in suggestion_judgments)
            / len(suggestion_judgments)
            if suggestion_judgments
            else 0.0
        )
        total_flagged = sum(len(j.flagged_suggestions) for j in suggestion_judgments)
        flagged_details = [
            {
                "prefix": j.prefix,
                "flagged": j.flagged_suggestions,
                "reasoning": j.reasoning,
            }
            for j in suggestion_judgments
            if j.flagged_suggestions
        ]
        llm_summary = {
            "avg_relevance": f"{avg_rel:.2f}/3",
            "avg_diversity": f"{avg_div:.2f}/3",
            "count": len(suggestion_judgments),
            "total_flagged": total_flagged,
            "flagged_details": flagged_details,
        }

    metadata_rows: list[dict[str, str]] = []
    if run_metadata:
        key_to_label = [
            ("generated_at_utc", "Timestamp (UTC)"),
            ("top_k", "Top-K"),
            ("llm_model", "LLM Model"),
            ("adapter_path", "Adapter Path"),
            ("adapter_path_a", "Adapter Path (A)"),
            ("adapter_path_b", "Adapter Path (B)"),
        ]
        for key, label in key_to_label:
            if key in run_metadata:
                metadata_rows.append({"label": label, "value": str(run_metadata[key])})

    return template.render(
        is_comparison=False,
        check_summary=check_summary,
        prefix_details=prefix_details,
        check_descriptions=CHECK_DESCRIPTIONS,
        run_metadata_rows=metadata_rows,
        sibling_report=sibling_report,
        llm_summary=llm_summary,
    )


def _generate_comparison_html(
    checks_a: list[CheckResult],
    checks_b: list[CheckResult],
    comparison_checks: list[CheckResult],
    config_a: str,
    config_b: str,
    run_metadata: Mapping[str, object] | None = None,
    sibling_report: str | None = None,
) -> str:
    """Generate an HTML comparison report."""
    tmpl_dir = Path(__file__).resolve().parent.parent / "reporting" / "templates"
    template_path = tmpl_dir / "autocomplete_report.html"
    template_str = template_path.read_text(encoding="utf-8")
    template = _JINJA_ENV.from_string(template_str)

    summary_a = _summarize_checks(checks_a)
    summary_b = _summarize_checks(checks_b)
    all_check_names = sorted(set(summary_a.keys()) | set(summary_b.keys()))

    check_comparison = []
    for name in all_check_names:
        sa = summary_a.get(name, {"passed_display": "-", "failed": "-"})
        sb = summary_b.get(name, {"passed_display": "-", "failed": "-"})
        check_comparison.append(
            {
                "name": name,
                "passed_a": sa["passed_display"],
                "failed_a": sa["failed"],
                "passed_b": sb["passed_display"],
                "failed_b": sb["failed"],
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
        check_comparison=check_comparison,
        overlap_checks=overlap_checks[:10],
        run_metadata_rows=metadata_rows,
        sibling_report=sibling_report,
    )
