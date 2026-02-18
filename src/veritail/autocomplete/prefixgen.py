"""Prefix generation from query sets."""

from __future__ import annotations

import csv
from pathlib import Path

from veritail.queries import load_queries


def generate_prefixes(
    queries_path: str,
    output_path: str,
    char_ratios: list[float] | None = None,
) -> list[dict[str, str]]:
    """Generate prefix entries from a query set at various character ratios.

    For each query, generates multiple prefixes by truncating at different
    character ratios. For example, "running shoes" with ratio 0.3 yields
    "runn" (4 chars out of 13).

    Args:
        queries_path: Path to a CSV/JSON query file with a 'query' column.
        output_path: Path to write the output prefixes CSV.
        char_ratios: Character ratios for prefix truncation (default: [0.3, 0.5, 0.7]).

    Returns:
        List of generated prefix rows (dicts with prefix, target_query, type).
    """
    if char_ratios is None:
        char_ratios = [0.3, 0.5, 0.7]

    queries = load_queries(queries_path)

    ratio_to_type = _build_ratio_labels(char_ratios)

    rows: list[dict[str, str]] = []
    for q in queries:
        target = q.query.strip()
        if not target:
            continue
        for ratio in char_ratios:
            prefix_len = max(1, round(len(target) * ratio))
            prefix = target[:prefix_len]
            rows.append(
                {
                    "prefix": prefix,
                    "target_query": target,
                    "type": ratio_to_type[ratio],
                }
            )

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["prefix", "target_query", "type"])
        writer.writeheader()
        writer.writerows(rows)

    return rows


def _build_ratio_labels(ratios: list[float]) -> dict[float, str]:
    """Map each ratio to a human-readable type label."""
    sorted_ratios = sorted(ratios)
    n = len(sorted_ratios)
    labels: dict[float, str] = {}
    for i, r in enumerate(sorted_ratios):
        if n == 1:
            labels[r] = "mid_prefix"
        elif i == 0:
            labels[r] = "short_prefix"
        elif i == n - 1:
            labels[r] = "long_prefix"
        else:
            labels[r] = "mid_prefix"
    return labels
