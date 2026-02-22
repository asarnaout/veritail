"""Default ecommerce relevance judgment rubric."""

from __future__ import annotations

from veritail.prompts import load_prompt
from veritail.types import SearchResult

SYSTEM_PROMPT = load_prompt("rubrics/ecommerce_default.md")


def format_user_prompt(
    query: str,
    result: SearchResult,
    *,
    corrected_query: str | None = None,
    overlay: str | None = None,
) -> str:
    """Format a query-product pair into a user prompt for the LLM judge."""
    attrs_str = ""
    if result.attributes:
        attrs_lines = [f"  - {k}: {v}" for k, v in result.attributes.items()]
        attrs_str = "\n".join(attrs_lines)

    metadata_str = ""
    if result.metadata:
        meta_lines = [f"  - {k}: {v}" for k, v in result.metadata.items()]
        metadata_str = "\n".join(meta_lines)

    if corrected_query is not None:
        query_section = (
            f"## Original Search Query\n{query}\n\n"
            f"## Corrected Search Query (used for retrieval)\n{corrected_query}"
        )
    else:
        query_section = f"## Search Query\n{query}"

    overlay_section = ""
    if overlay:
        overlay_section = f"\n\n## Domain-Specific Scoring Guidance\n{overlay}"

    return f"""\
{query_section}{overlay_section}

## Product
- **Title**: {result.title}
- **Description**: {result.description}
- **Category**: {result.category}
- **Price**: ${result.price:.2f}
- **In Stock**: {"Yes" if result.in_stock else "No"}
- **Position in Results**: {result.position + 1}
{f"- **Attributes**:{chr(10)}{attrs_str}" if attrs_str else ""}\
{f"{chr(10)}- **Metadata**:{chr(10)}{metadata_str}" if metadata_str else ""}

Please evaluate the relevance of this product to the search query."""
