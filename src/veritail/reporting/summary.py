"""LLM-powered report summary generation."""

from __future__ import annotations

import html
import logging
import re
import statistics
from collections import defaultdict
from collections.abc import Mapping

from veritail.llm.client import LLMClient
from veritail.prompts import load_prompt
from veritail.types import (
    CheckResult,
    CorrectionJudgment,
    JudgmentRecord,
    MetricResult,
)

logger = logging.getLogger(__name__)

_SUMMARY_MAX_TOKENS = 512
_NO_INSIGHTS_SENTINEL = "__NO_INSIGHTS__"
_MIN_SUMMARY_LENGTH = 20


def _truncate(text: str, max_len: int) -> str:
    """Truncate *text* to *max_len* characters, appending '...' if cut."""
    if len(text) <= max_len:
        return text
    return text[: max_len - 3] + "..."


def _strip_disambiguation(key: str) -> str:
    """Strip ``' [N]'`` suffix from disambiguated query keys."""
    return re.sub(r" \[\d+\]$", "", key)


# ── Single report payload ────────────────────────────────────────


def _build_single_payload(
    metrics: list[MetricResult],
    checks: list[CheckResult],
    judgments: list[JudgmentRecord] | None,
    correction_judgments: list[CorrectionJudgment] | None,
    run_metadata: Mapping[str, object] | None,
) -> str:
    """Build a structured text payload for the single-report summary LLM call."""
    sections: list[str] = []

    # 1. Score distribution
    if judgments:
        score_counts: dict[int, int] = {0: 0, 1: 0, 2: 0, 3: 0}
        for j in judgments:
            score_counts[j.score] = score_counts.get(j.score, 0) + 1
        total = sum(score_counts.values())
        if total > 0:
            lines = [f"## Score Distribution ({total} judgments)"]
            for s in (3, 2, 1, 0):
                pct = score_counts[s] / total * 100
                lines.append(f"- Score {s}: {score_counts[s]} ({pct:.1f}%)")
            sections.append("\n".join(lines))

    # 2. Metrics + by-query-type
    if metrics:
        lines = ["## Metrics"]
        for m in metrics:
            ci_str = ""
            if m.ci_lower is not None and m.ci_upper is not None:
                ci_str = f" [CI: {m.ci_lower:.4f}-{m.ci_upper:.4f}]"
            if m.query_count is not None and m.query_count == 0:
                lines.append(f"- {m.metric_name}: N/A (no applicable queries)")
            else:
                lines.append(f"- {m.metric_name}: {m.value:.4f}{ci_str}")
            if m.by_query_type:
                for qt, val in sorted(m.by_query_type.items()):
                    lines.append(f"  - {qt}: {val:.4f}")
        sections.append("\n".join(lines))

    # 3. Check summary (pass/fail counts)
    if checks:
        check_counts: dict[str, dict[str, int]] = {}
        for c in checks:
            if c.check_name not in check_counts:
                check_counts[c.check_name] = {"passed": 0, "failed": 0}
            key = "passed" if c.passed else "failed"
            check_counts[c.check_name][key] += 1
        lines = ["## Check Summary"]
        for name, counts in sorted(check_counts.items()):
            total_c = counts["passed"] + counts["failed"]
            fail_rate = counts["failed"] / total_c * 100 if total_c > 0 else 0
            lines.append(
                f"- {name}: {counts['passed']} passed, "
                f"{counts['failed']} failed ({fail_rate:.0f}% fail rate)"
            )
        sections.append("\n".join(lines))

    # 4. Worst 5 queries (by NDCG@10)
    ndcg = next((m for m in metrics if m.metric_name == "ndcg@10"), None)
    if ndcg and ndcg.per_query and judgments:
        # Build lookup structures
        query_type_lookup: dict[str, str] = {}
        query_scores: dict[str, list[tuple[int, int]]] = defaultdict(list)
        query_reasoning: dict[str, str] = {}
        for j in judgments:
            if j.query_type and j.query not in query_type_lookup:
                query_type_lookup[j.query] = j.query_type
            query_scores[j.query].append((j.product.position, j.score))
            if j.query not in query_reasoning:
                query_reasoning[j.query] = j.reasoning

        per_query_failed: dict[str, list[str]] = defaultdict(list)
        for c in checks:
            if not c.passed and c.check_name not in per_query_failed[c.query]:
                per_query_failed[c.query].append(c.check_name)

        sorted_queries = sorted(ndcg.per_query.items(), key=lambda x: x[1])[:5]
        lines = ["## Worst 5 Queries (by NDCG@10)"]
        for q, val in sorted_queries:
            raw_q = _strip_disambiguation(q)
            qt = query_type_lookup.get(raw_q, "unknown")
            scores = sorted(query_scores.get(raw_q, []))
            score_str = ", ".join(f"pos{p + 1}={s}" for p, s in scores)
            failed = per_query_failed.get(raw_q, [])
            reason = _truncate(query_reasoning.get(raw_q, ""), 120)
            lines.append(f'- "{q}" (type={qt}, NDCG@10={val:.4f})')
            if score_str:
                lines.append(f"  Scores: [{score_str}]")
            if failed:
                lines.append(f"  Failed checks: {', '.join(failed)}")
            if reason:
                lines.append(f"  Sample reasoning: {reason}")
        sections.append("\n".join(lines))

    # 5. High-variance queries
    if ndcg and ndcg.per_query and judgments and len(ndcg.per_query) >= 3:
        query_score_lists: dict[str, list[int]] = defaultdict(list)
        for j in judgments:
            query_score_lists[j.query].append(j.score)

        variance_items: list[tuple[str, float]] = []
        for q_var, q_scores in query_score_lists.items():
            if len(q_scores) >= 2:
                variance_items.append((q_var, statistics.variance(q_scores)))
        variance_items.sort(key=lambda x: -x[1])
        top_var = variance_items[:3]
        if top_var and top_var[0][1] > 0:
            lines = ["## Mixed-Relevance Queries (widest score spread)"]
            for q_var, var in top_var:
                sorted_scores = sorted(query_score_lists[q_var])
                lines.append(f'- "{q_var}": variance={var:.2f}, scores={sorted_scores}')
            sections.append("\n".join(lines))

    # 6. Position decay
    if judgments:
        pos_scores: dict[int, list[int]] = defaultdict(list)
        for j in judgments:
            pos_scores[j.product.position + 1].append(j.score)
        if len(pos_scores) >= 2:
            lines = ["## Average Score by Position"]
            for pos in sorted(pos_scores.keys()):
                avg = sum(pos_scores[pos]) / len(pos_scores[pos])
                lines.append(f"- Position {pos}: {avg:.2f}")
            sections.append("\n".join(lines))

    # 7. Check failure samples
    if checks:
        failed_by_check: dict[str, list[CheckResult]] = defaultdict(list)
        for c in checks:
            if not c.passed:
                failed_by_check[c.check_name].append(c)
        if failed_by_check:
            lines = ["## Check Failure Samples (up to 3 per check)"]
            for name, failures in sorted(failed_by_check.items()):
                lines.append(f"### {name}")
                for f in failures[:3]:
                    detail = _truncate(f.detail, 100)
                    lines.append(
                        f'- query="{f.query}", product={f.product_id}, detail: {detail}'
                    )
            sections.append("\n".join(lines))

    # 8. Corrections
    if correction_judgments:
        lines = ["## Corrections"]
        for cj in correction_judgments:
            reason = _truncate(cj.reasoning, 120)
            lines.append(
                f'- "{cj.original_query}" -> "{cj.corrected_query}": '
                f"{cj.verdict} ({reason})"
            )
        sections.append("\n".join(lines))

    return "\n\n".join(sections)


# ── Comparison report payload ────────────────────────────────────


def _build_comparison_payload(
    metrics_a: list[MetricResult],
    metrics_b: list[MetricResult],
    checks_a: list[CheckResult] | None,
    checks_b: list[CheckResult] | None,
    judgments_a: list[JudgmentRecord] | None,
    judgments_b: list[JudgmentRecord] | None,
    comparison_checks: list[CheckResult],
    config_a: str,
    config_b: str,
    corrections_a: list[CorrectionJudgment] | None,
    corrections_b: list[CorrectionJudgment] | None,
) -> str:
    """Build a structured text payload for the comparison summary LLM call."""
    sections: list[str] = []

    metrics_b_lookup = {m.metric_name: m for m in metrics_b}

    # 9. Aggregate baseline
    lines = [f"## Aggregate Metrics ({config_a} vs {config_b})"]
    for m_a in metrics_a:
        m_b = metrics_b_lookup.get(m_a.metric_name)
        if m_b:
            lines.append(
                f"- {m_a.metric_name}: {config_a}={m_a.value:.4f}, "
                f"{config_b}={m_b.value:.4f}"
            )
    sections.append("\n".join(lines))

    # 10. Metric deltas
    lines = ["## Metric Deltas"]
    for m_a in metrics_a:
        m_b = metrics_b_lookup.get(m_a.metric_name)
        if m_b:
            delta = m_b.value - m_a.value
            pct = (delta / m_a.value * 100) if m_a.value != 0 else 0.0
            lines.append(f"- {m_a.metric_name}: delta={delta:+.4f} ({pct:+.1f}%)")
    sections.append("\n".join(lines))

    # 11. Win/loss/tie
    ndcg_a = next((m for m in metrics_a if m.metric_name == "ndcg@10"), None)
    ndcg_b = next((m for m in metrics_b if m.metric_name == "ndcg@10"), None)
    if ndcg_a and ndcg_b and ndcg_a.per_query and ndcg_b.per_query:
        wins = losses = ties = 0
        for q in ndcg_a.per_query:
            if q in ndcg_b.per_query:
                d = ndcg_b.per_query[q] - ndcg_a.per_query[q]
                if d > 0.001:
                    wins += 1
                elif d < -0.001:
                    losses += 1
                else:
                    ties += 1
        total = wins + losses + ties
        if total > 0:
            sections.append(
                f"## Win/Loss/Tie (NDCG@10, {total} queries)\n"
                f"- {config_b} wins: {wins} ({wins / total * 100:.0f}%)\n"
                f"- {config_a} wins: {losses} ({losses / total * 100:.0f}%)\n"
                f"- Ties: {ties} ({ties / total * 100:.0f}%)"
            )

    # 12. Top 5 improvements + regressions
    if ndcg_a and ndcg_b and ndcg_a.per_query and ndcg_b.per_query:
        deltas: list[tuple[str, float, float, float]] = []
        for q in ndcg_a.per_query:
            if q in ndcg_b.per_query:
                d = ndcg_b.per_query[q] - ndcg_a.per_query[q]
                deltas.append((q, ndcg_a.per_query[q], ndcg_b.per_query[q], d))
        deltas.sort(key=lambda x: x[3])

        regressions = [x for x in deltas if x[3] < -0.001][:5]
        improvements = [x for x in reversed(deltas) if x[3] > 0.001][:5]

        if improvements:
            lines = ["## Top Improvements"]
            for q, va, vb, d in improvements:
                lines.append(
                    f'- "{q}": {config_a}={va:.4f} -> {config_b}={vb:.4f} ({d:+.4f})'
                )
            sections.append("\n".join(lines))

        if regressions:
            lines = ["## Top Regressions"]
            for q, va, vb, d in regressions:
                lines.append(
                    f'- "{q}": {config_a}={va:.4f} -> {config_b}={vb:.4f} ({d:+.4f})'
                )
            sections.append("\n".join(lines))

    # 13. Check deltas
    if checks_a or checks_b:
        fail_a: dict[str, int] = defaultdict(int)
        fail_b: dict[str, int] = defaultdict(int)
        for c in checks_a or []:
            if not c.passed:
                fail_a[c.check_name] += 1
        for c in checks_b or []:
            if not c.passed:
                fail_b[c.check_name] += 1
        all_names = sorted(set(fail_a.keys()) | set(fail_b.keys()))
        if all_names:
            lines = ["## Check Failure Deltas"]
            for name in all_names:
                a_count = fail_a.get(name, 0)
                b_count = fail_b.get(name, 0)
                delta = b_count - a_count
                lines.append(
                    f"- {name}: {config_a}={a_count}, "
                    f"{config_b}={b_count} (delta={delta:+d})"
                )
            sections.append("\n".join(lines))

    # 14. Metrics by query type (both)
    all_types: set[str] = set()
    for m in metrics_a + metrics_b:
        all_types.update(m.by_query_type.keys())
    if all_types:
        lines = ["## Metrics by Query Type"]
        for m_a in metrics_a:
            m_b = metrics_b_lookup.get(m_a.metric_name)
            if m_b and (m_a.by_query_type or m_b.by_query_type):
                for qt in sorted(all_types):
                    qt_va = m_a.by_query_type.get(qt)
                    qt_vb = m_b.by_query_type.get(qt)
                    if qt_va is not None and qt_vb is not None:
                        lines.append(
                            f"- {m_a.metric_name}/{qt}: "
                            f"{config_a}={qt_va:.4f}, {config_b}={qt_vb:.4f}"
                        )
        sections.append("\n".join(lines))

    # Corrections
    for label, cjs in [
        (config_a, corrections_a),
        (config_b, corrections_b),
    ]:
        if cjs:
            lines = [f"## Corrections ({label})"]
            for cj in cjs:
                reason = _truncate(cj.reasoning, 120)
                lines.append(
                    f'- "{cj.original_query}" -> "{cj.corrected_query}": '
                    f"{cj.verdict} ({reason})"
                )
            sections.append("\n".join(lines))

    return "\n\n".join(sections)


# ── Response parsing ─────────────────────────────────────────────


def _parse_summary_response(text: str) -> str | None:
    """Parse LLM response. Returns ``None`` if no insights or too short."""
    stripped = text.strip()
    if not stripped:
        return None
    if _NO_INSIGHTS_SENTINEL in stripped:
        return None
    if len(stripped) < _MIN_SUMMARY_LENGTH:
        return None
    return stripped


# ── HTML conversion ──────────────────────────────────────────────


def summary_bullets_to_html(text: str) -> str:
    """Convert markdown bullet list to safe HTML.

    Each line starting with ``- `` becomes an ``<li>``.
    Non-bullet lines become ``<p>`` tags.
    All text content is HTML-escaped.
    """
    lines = text.strip().splitlines()
    in_list = False
    parts: list[str] = []

    for line in lines:
        stripped = line.strip()
        if not stripped:
            if in_list:
                parts.append("</ul>")
                in_list = False
            continue

        if stripped.startswith("- "):
            if not in_list:
                parts.append("<ul>")
                in_list = True
            content = html.escape(stripped[2:].strip())
            parts.append(f"<li>{content}</li>")
        else:
            if in_list:
                parts.append("</ul>")
                in_list = False
            parts.append(f"<p>{html.escape(stripped)}</p>")

    if in_list:
        parts.append("</ul>")

    return "\n".join(parts)


# ── Public API ───────────────────────────────────────────────────


def generate_summary(
    client: LLMClient,
    metrics: list[MetricResult],
    checks: list[CheckResult],
    judgments: list[JudgmentRecord] | None = None,
    correction_judgments: list[CorrectionJudgment] | None = None,
    run_metadata: Mapping[str, object] | None = None,
) -> str | None:
    """Generate an AI summary for a single-config evaluation report.

    Returns a markdown bullet string, or ``None`` if the LLM finds
    nothing insightful (or on any error).
    """
    payload = _build_single_payload(
        metrics, checks, judgments, correction_judgments, run_metadata
    )
    if not payload.strip():
        return None

    system_prompt = load_prompt("reporting/summary.md")
    try:
        response = client.complete(
            system_prompt, payload, max_tokens=_SUMMARY_MAX_TOKENS
        )
    except Exception:
        logger.warning("summary LLM call failed", exc_info=True)
        return None
    logger.debug(
        "summary llm call: tokens=%d+%d",
        response.input_tokens,
        response.output_tokens,
    )
    return _parse_summary_response(response.content)


def generate_comparison_summary(
    client: LLMClient,
    metrics_a: list[MetricResult],
    metrics_b: list[MetricResult],
    checks_a: list[CheckResult] | None,
    checks_b: list[CheckResult] | None,
    judgments_a: list[JudgmentRecord] | None,
    judgments_b: list[JudgmentRecord] | None,
    comparison_checks: list[CheckResult],
    config_a: str,
    config_b: str,
    corrections_a: list[CorrectionJudgment] | None = None,
    corrections_b: list[CorrectionJudgment] | None = None,
) -> str | None:
    """Generate an AI summary for an A/B comparison report.

    Returns a markdown bullet string, or ``None`` if the LLM finds
    nothing insightful (or on any error).
    """
    payload = _build_comparison_payload(
        metrics_a,
        metrics_b,
        checks_a,
        checks_b,
        judgments_a,
        judgments_b,
        comparison_checks,
        config_a,
        config_b,
        corrections_a,
        corrections_b,
    )
    if not payload.strip():
        return None

    system_prompt = load_prompt("reporting/comparison_summary.md")
    try:
        response = client.complete(
            system_prompt, payload, max_tokens=_SUMMARY_MAX_TOKENS
        )
    except Exception:
        logger.warning("comparison summary LLM call failed", exc_info=True)
        return None
    logger.debug(
        "comparison summary llm call: tokens=%d+%d",
        response.input_tokens,
        response.output_tokens,
    )
    return _parse_summary_response(response.content)
