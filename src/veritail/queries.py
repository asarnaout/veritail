"""Query set loading from CSV and JSON files."""

from __future__ import annotations

import csv
import json
from pathlib import Path

from veritail.types import QueryEntry


def load_queries(path: str) -> list[QueryEntry]:
    """Load a query set from a CSV or JSON file.

    CSV files must have a 'query' column.
    Optional columns: 'type', 'category'.
    JSON files must be a list of objects with a 'query' key
    and optional keys above.
    """
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"Query file not found: {path}")

    suffix = file_path.suffix.lower()
    if suffix == ".csv":
        return _load_csv(file_path)
    elif suffix == ".json":
        return _load_json(file_path)
    else:
        raise ValueError(f"Unsupported query file format: {suffix}. Use .csv or .json")


def _load_csv(path: Path) -> list[QueryEntry]:
    """Load queries from a CSV file."""
    entries: list[QueryEntry] = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None or "query" not in reader.fieldnames:
            raise ValueError("CSV file must have a 'query' column")
        for row in reader:
            query = row["query"].strip()
            if not query:
                continue
            entries.append(
                QueryEntry(
                    query=query,
                    type=row.get("type", "").strip() or None,
                    category=row.get("category", "").strip() or None,
                    overlay=row.get("overlay", "").strip() or None,
                )
            )
    if not entries:
        raise ValueError(f"No queries found in {path}")
    return entries


def _load_json(path: Path) -> list[QueryEntry]:
    """Load queries from a JSON file."""
    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise ValueError("JSON query file must contain a list of objects")

    entries: list[QueryEntry] = []
    for item in data:
        if not isinstance(item, dict) or "query" not in item:
            raise ValueError("Each JSON object must have a 'query' key")
        query = str(item["query"]).strip()
        if not query:
            continue
        entries.append(
            QueryEntry(
                query=query,
                type=item.get("type"),
                category=item.get("category"),
                overlay=item.get("overlay"),
            )
        )
    if not entries:
        raise ValueError(f"No queries found in {path}")
    return entries
