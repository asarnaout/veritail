"""Prefix set loading from CSV and JSON files."""

from __future__ import annotations

import csv
import json
from pathlib import Path

from veritail.types import PrefixEntry


def load_prefixes(path: str) -> list[PrefixEntry]:
    """Load a prefix set from a CSV or JSON file.

    CSV files must have a 'prefix' column.
    Optional column: 'type'.
    JSON files must be a list of objects with a 'prefix' key.
    """
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"Prefix file not found: {path}")

    suffix = file_path.suffix.lower()
    if suffix == ".csv":
        return _load_csv(file_path)
    elif suffix == ".json":
        return _load_json(file_path)
    else:
        raise ValueError(f"Unsupported prefix file format: {suffix}. Use .csv or .json")


def _load_csv(path: Path) -> list[PrefixEntry]:
    """Load prefixes from a CSV file."""
    entries: list[PrefixEntry] = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            raise ValueError("CSV file must have a 'prefix' column")
        if "prefix" not in reader.fieldnames:
            raise ValueError("CSV file is missing required column: prefix")
        for row in reader:
            prefix = row["prefix"].strip()
            if not prefix:
                continue
            entries.append(
                PrefixEntry(
                    prefix=prefix,
                    type=row.get("type", "").strip() or None,
                )
            )
    if not entries:
        raise ValueError(f"No prefixes found in {path}")
    return entries


def _load_json(path: Path) -> list[PrefixEntry]:
    """Load prefixes from a JSON file."""
    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise ValueError("JSON prefix file must contain a list of objects")

    entries: list[PrefixEntry] = []
    for item in data:
        if not isinstance(item, dict):
            raise ValueError("Each JSON element must be an object")
        if "prefix" not in item:
            raise ValueError("Each JSON object must have a 'prefix' key")
        prefix = str(item["prefix"]).strip()
        if not prefix:
            continue
        entries.append(
            PrefixEntry(
                prefix=prefix,
                type=item.get("type"),
            )
        )
    if not entries:
        raise ValueError(f"No prefixes found in {path}")
    return entries
