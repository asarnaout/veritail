"""LLM-powered query generation for ecommerce search evaluation."""

from __future__ import annotations

import csv
import json
import logging
import re
import warnings
from pathlib import Path

from veritail.llm.client import LLMClient
from veritail.prompts import load_prompt

logger = logging.getLogger(__name__)

DEFAULT_QUERY_COUNT = 25
MAX_QUERY_COUNT = 50
_GENERATION_MAX_TOKENS = 4096

QUERY_TYPES = ["navigational", "broad", "long_tail", "attribute", "edge_case"]

# Weights for distributing queries across types (must sum to 1.0).
_TYPE_WEIGHTS: dict[str, float] = {
    "broad": 0.25,
    "long_tail": 0.25,
    "attribute": 0.20,
    "navigational": 0.15,
    "edge_case": 0.15,
}

SYSTEM_PROMPT = load_prompt("querygen.md")


def _compute_distribution(count: int) -> dict[str, int]:
    """Distribute *count* queries across types using weighted allocation.

    Uses floor allocation with round-robin remainder distribution to ensure
    all counts are positive for reasonable inputs and the sum equals *count*.
    """
    # Floor allocation
    dist: dict[str, int] = {}
    allocated = 0
    remainders: list[tuple[float, str]] = []
    for qtype in QUERY_TYPES:
        weight = _TYPE_WEIGHTS[qtype]
        raw = count * weight
        floored = int(raw)
        dist[qtype] = floored
        allocated += floored
        remainders.append((raw - floored, qtype))

    # Distribute the remainder by largest fractional part
    remainder = count - allocated
    remainders.sort(key=lambda x: x[0], reverse=True)
    for i in range(remainder):
        dist[remainders[i][1]] += 1

    return dist


def _build_user_prompt(
    *,
    distribution: dict[str, int],
    vertical_name: str | None,
    vertical_text: str | None,
    context: str | None,
) -> str:
    """Build the user prompt specifying exact counts and context."""
    parts: list[str] = []

    parts.append("Generate the following search queries:\n")
    for qtype, n in distribution.items():
        parts.append(f"- {n} {qtype} queries")

    if vertical_text:
        label = f" ({vertical_name})" if vertical_name else ""
        parts.append(f"\n## Vertical context{label}\n\n{vertical_text}")

    if context:
        parts.append(f"\n## Business context\n\n{context}")

    return "\n".join(parts)


def _parse_response(content: str) -> list[str]:
    """Parse LLM response into a list of query strings.

    Handles clean JSON arrays, markdown code fences, and JSON embedded
    in surrounding text.  Accepts both plain string arrays
    (``["shoes", "boots"]``) and legacy object arrays
    (``[{"query": "shoes", ...}]``).  Empty queries are skipped.

    Raises ``ValueError`` when no valid JSON array can be extracted.
    """
    text = content.strip()

    # Try to extract from markdown code fences first
    fence_match = re.search(r"```(?:json)?\s*\n?(.*?)```", text, re.DOTALL)
    if fence_match:
        text = fence_match.group(1).strip()

    # Try direct parse
    parsed = _try_parse_json_array(text)

    # Fallback: find first [ ... ] in the text
    if parsed is None:
        bracket_match = re.search(r"\[.*]", text, re.DOTALL)
        if bracket_match:
            parsed = _try_parse_json_array(bracket_match.group(0))

    if parsed is None:
        raise ValueError("Could not parse JSON array from LLM response.")

    if not isinstance(parsed, list):
        raise ValueError("LLM response is not a JSON array.")

    queries: list[str] = []
    for item in parsed:
        if isinstance(item, str):
            query = item.strip()
        elif isinstance(item, dict):
            # Accept legacy object format for robustness
            query = str(item.get("query", "")).strip()
        else:
            continue
        if query:
            queries.append(query)

    if not queries:
        raise ValueError("No valid queries found in LLM response.")

    return queries


def _try_parse_json_array(text: str) -> list[object] | None:
    """Attempt to parse *text* as a JSON array, returning ``None`` on failure."""
    try:
        result = json.loads(text)
        if isinstance(result, list):
            return result
    except (json.JSONDecodeError, ValueError):
        pass
    return None


def _write_csv(queries: list[str], output_path: Path) -> None:
    """Write queries to a single-column CSV."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["query"])
        for q in queries:
            writer.writerow([q])


def generate_queries(
    *,
    llm_client: LLMClient,
    output_path: Path,
    count: int = DEFAULT_QUERY_COUNT,
    vertical: str | None = None,
    context: str | None = None,
) -> list[str]:
    """Generate evaluation queries using an LLM and save to CSV.

    At least one of *vertical* or *context* must be provided so the LLM
    has enough domain information to produce useful queries.

    Args:
        llm_client: Configured LLM client.
        output_path: Destination CSV path.
        count: Target number of queries to generate (approximate — LLMs may
            return slightly more or fewer). Must be between 1 and
            :data:`MAX_QUERY_COUNT`.
        vertical: Built-in vertical name or text file path.
        context: Business context string or file path.

    Returns:
        List of generated query strings.

    Raises:
        ValueError: If neither vertical nor context is provided, or if
            *count* exceeds :data:`MAX_QUERY_COUNT`.
    """
    if count > MAX_QUERY_COUNT:
        raise ValueError(
            f"--count must be <= {MAX_QUERY_COUNT}. "
            "For larger query sets, run the command multiple times "
            "or curate queries manually."
        )

    if not vertical and not context:
        raise ValueError(
            "At least one of --vertical or --context is required "
            "so the LLM has enough domain context to generate useful queries."
        )

    vertical_name: str | None = None
    vertical_text: str | None = None
    if vertical:
        from veritail.verticals import load_vertical

        vertical_name = vertical
        vertical_text = load_vertical(vertical).core

    # Read context from file if it looks like a file path
    if context and Path(context).is_file():
        context = Path(context).read_text(encoding="utf-8").rstrip()

    distribution = _compute_distribution(count)
    logger.debug("query distribution: %s", distribution)

    user_prompt = _build_user_prompt(
        distribution=distribution,
        vertical_name=vertical_name,
        vertical_text=vertical_text,
        context=context,
    )

    response = llm_client.complete(
        SYSTEM_PROMPT, user_prompt, max_tokens=_GENERATION_MAX_TOKENS
    )

    queries = _parse_response(response.content)
    logger.debug("llm returned %d queries", len(queries))

    if len(queries) != count:
        warnings.warn(
            f"Requested {count} queries but the LLM returned {len(queries)}. "
            "This is expected — LLM output counts are approximate. "
            "Review the output and supplement manually if needed.",
            stacklevel=2,
        )

    _write_csv(queries, output_path)

    return queries
