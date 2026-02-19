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

_VALID_TYPES = frozenset({"navigational", "broad", "long_tail", "attribute"})

_TYPE_RE = re.compile(r"(?i)QUERY_TYPE\s*[:=]\s*(\w+)")


def classify_query_type(
    llm_client: LLMClient,
    query: str,
    context: str | None = None,
    vertical: str | None = None,
) -> str | None:
    """Classify a single query into one of the four query types.

    Returns the type string or None if classification fails.
    """
    system_prompt = CLASSIFICATION_SYSTEM_PROMPT
    prefix_parts: list[str] = []
    if context:
        prefix_parts.append(f"## Business Context\n{context}")
    if vertical:
        prefix_parts.append(vertical)
    if prefix_parts:
        prefix = "\n\n".join(prefix_parts)
        system_prompt = f"{prefix}\n\n{system_prompt}"

    user_prompt = f"Query: {query}"

    try:
        response = llm_client.complete(system_prompt, user_prompt, max_tokens=64)
    except Exception:
        return None

    match = _TYPE_RE.search(response.content)
    if not match:
        return None

    value = match.group(1).lower()
    if value not in _VALID_TYPES:
        return None

    return value
