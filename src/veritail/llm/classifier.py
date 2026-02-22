"""LLM-based query type classification."""

from __future__ import annotations

import logging
import re

from veritail.llm.client import LLMClient
from veritail.prompts import load_prompt

logger = logging.getLogger(__name__)

CLASSIFICATION_SYSTEM_PROMPT = load_prompt("llm/classification.md")

CLASSIFICATION_MAX_TOKENS = 96

_VALID_TYPES = frozenset({"navigational", "broad", "long_tail", "attribute"})

_TYPE_RE = re.compile(r"(?i)QUERY_TYPE\s*[:=]\s*(\w+)")
_OVERLAY_RE = re.compile(r"(?i)OVERLAY\s*[:=]\s*(\w+)")


def build_classification_system_prompt(
    context: str | None = None,
    vertical: str | None = None,
) -> str:
    """Build the full system prompt for query type classification."""
    system_prompt = CLASSIFICATION_SYSTEM_PROMPT
    prefix_parts: list[str] = []
    if context:
        prefix_parts.append(f"## Business Context\n{context}")
    if vertical:
        prefix_parts.append(vertical)
    if prefix_parts:
        prefix = "\n\n".join(prefix_parts)
        system_prompt = f"{prefix}\n\n{system_prompt}"
    return system_prompt


def parse_classification_response(content: str) -> str | None:
    """Parse a classification response into a query type string.

    Returns the type string or None if parsing fails.
    """
    match = _TYPE_RE.search(content)
    if not match:
        return None

    value = match.group(1).lower()
    if value not in _VALID_TYPES:
        return None

    return value


def classify_query_type(
    llm_client: LLMClient,
    query: str,
    context: str | None = None,
    vertical: str | None = None,
) -> str | None:
    """Classify a single query into one of the four query types.

    Returns the type string or None if classification fails.
    """
    system_prompt = build_classification_system_prompt(context, vertical)
    user_prompt = f"Query: {query}"

    try:
        response = llm_client.complete(
            system_prompt, user_prompt, max_tokens=CLASSIFICATION_MAX_TOKENS
        )
    except Exception:
        return None

    return parse_classification_response(response.content)


def parse_classification_with_overlay(
    content: str,
    overlay_keys: dict[str, str] | None = None,
) -> tuple[str | None, str | None]:
    """Parse a classification response that may include an overlay key.

    Returns (query_type, overlay_key).  overlay_key is None when
    *overlay_keys* is not provided or the response lacks a valid OVERLAY line.
    """
    query_type = parse_classification_response(content)

    overlay_key: str | None = None
    if overlay_keys:
        match = _OVERLAY_RE.search(content)
        if match:
            value = match.group(1).lower()
            if value in overlay_keys:
                overlay_key = value

    return query_type, overlay_key


def _build_overlay_prompt_section(
    overlay_keys: dict[str, str],
) -> str:
    """Build the overlay classification section for the system prompt."""
    lines = [
        "\n## Overlay Classification",
        "",
        "Also classify which domain overlay applies to this query. Choose exactly one:",
        "",
    ]
    for key, description in sorted(overlay_keys.items()):
        lines.append(f"- **{key}**: {description}")
    lines.append("")
    lines.append(
        "If the query is even partially related to a category above, select that "
        "category. Only use `none` when the query is entirely outside all listed "
        'domains (e.g., "restaurant insurance", "chef hiring", "food truck financing").'
    )
    lines.append("")
    lines.append(
        "Add a second line to your response:\n\n"
        "OVERLAY: <" + "|".join(sorted(overlay_keys)) + "|none>"
    )
    return "\n".join(lines)


def classify_query(
    llm_client: LLMClient,
    query: str,
    context: str | None = None,
    vertical: str | None = None,
    overlay_keys: dict[str, str] | None = None,
) -> tuple[str | None, str | None]:
    """Classify a query's type and optional overlay key in a single LLM call.

    When *overlay_keys* is provided, appends overlay classification to the
    system prompt so both type and overlay are classified together.  When
    not provided, delegates to :func:`classify_query_type` and returns
    ``(type, None)``.

    Returns:
        Tuple of (query_type, overlay_key).
    """
    if not overlay_keys:
        return classify_query_type(llm_client, query, context, vertical), None

    system_prompt = build_classification_system_prompt(context, vertical)
    system_prompt += _build_overlay_prompt_section(overlay_keys)
    user_prompt = f"Query: {query}"

    try:
        response = llm_client.complete(
            system_prompt, user_prompt, max_tokens=CLASSIFICATION_MAX_TOKENS
        )
    except Exception:
        logger.debug("classification failed for %r", query, exc_info=True)
        return None, None

    result = parse_classification_with_overlay(response.content, overlay_keys)
    logger.debug(
        "classify_query %r -> type=%s, overlay=%s",
        query,
        result[0],
        result[1],
    )
    return result
