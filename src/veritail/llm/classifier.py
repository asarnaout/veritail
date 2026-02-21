"""LLM-based query type classification."""

from __future__ import annotations

import re

from veritail.llm.client import LLMClient

CLASSIFICATION_SYSTEM_PROMPT = """\
You are an ecommerce search query classifier. Classify the given search query \
into exactly one of these types:

- **navigational**: The shopper is looking for a specific brand, product line, \
or model (e.g. "nike air max 90", "dyson v15", "kohler toilet").
- **broad**: A general product category search with no strong brand or attribute \
constraint (e.g. "running shoes", "kitchen faucet", "ceiling fan").
- **long_tail**: A highly specific multi-word query with multiple constraints \
such as size, color, quantity, or model number \
(e.g. "3/4 inch copper 90 degree elbow", "gfci outlet 20 amp white").
- **attribute**: A query that adds one or two specific attribute filters to a \
category — typically color, material, finish, or a single dimension \
(e.g. "red running shoes", "brushed nickel cabinet pulls", "matte black faucet").

## Response Format

You MUST respond in exactly this format (one line, nothing else):

QUERY_TYPE: <navigational|broad|long_tail|attribute>
"""

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
        "Add a second line to your response:\n\n"
        "OVERLAY: <" + "|".join(sorted(overlay_keys)) + ">"
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
        return None, None

    return parse_classification_with_overlay(response.content, overlay_keys)
