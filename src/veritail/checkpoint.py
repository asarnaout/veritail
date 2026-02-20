"""Batch checkpoint persistence for resume support."""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from veritail.types import SearchResult


@dataclass
class BatchCheckpoint:
    """State snapshot for a batch evaluation in progress."""

    batch_id: str
    experiment_name: str
    phase: str  # "relevance" | "corrections"
    request_context: dict[str, dict[str, Any]]
    checks: list[dict[str, Any]]
    correction_entries: list[list[Any]]
    gemini_custom_id_order: list[str] = field(default_factory=list)
    correction_batch_id: str | None = None
    correction_context: dict[str, dict[str, Any]] | None = None
    gemini_correction_custom_id_order: list[str] = field(default_factory=list)


def _checkpoint_path(
    output_dir: str, experiment: str, *, filename: str = "checkpoint.json"
) -> Path:
    return Path(output_dir) / experiment / filename


def save_checkpoint(
    output_dir: str,
    experiment: str,
    checkpoint: BatchCheckpoint,
    *,
    filename: str = "checkpoint.json",
) -> None:
    """Atomically write checkpoint to disk (write tmp, then rename)."""
    path = _checkpoint_path(output_dir, experiment, filename=filename)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(".tmp")
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(asdict(checkpoint), f, indent=2, default=str)
    # os.replace is atomic on the same filesystem
    os.replace(tmp_path, path)


def load_checkpoint(
    output_dir: str, experiment: str, *, filename: str = "checkpoint.json"
) -> BatchCheckpoint | None:
    """Load a checkpoint from disk, or return None if absent."""
    path = _checkpoint_path(output_dir, experiment, filename=filename)
    if not path.exists():
        return None
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return BatchCheckpoint(**data)


def clear_checkpoint(
    output_dir: str, experiment: str, *, filename: str = "checkpoint.json"
) -> None:
    """Remove the checkpoint file after a successful run."""
    path = _checkpoint_path(output_dir, experiment, filename=filename)
    if path.exists():
        path.unlink()


def serialize_request_context(
    context: dict[
        str,
        tuple[str, SearchResult, str | None, str | None, list[dict[str, str]], int],
    ],
) -> dict[str, dict[str, Any]]:
    """Convert in-memory request context tuples to JSON-safe dicts."""
    serialized: dict[str, dict[str, Any]] = {}
    for custom_id, (
        query,
        result,
        query_type,
        corrected_query,
        failed_checks,
        query_index,
    ) in context.items():
        serialized[custom_id] = {
            "query": query,
            "result": asdict(result),
            "query_type": query_type,
            "corrected_query": corrected_query,
            "failed_checks": failed_checks,
            "query_index": query_index,
        }
    return serialized


def deserialize_request_context(
    data: dict[str, dict[str, Any]],
) -> dict[
    str,
    tuple[str, SearchResult, str | None, str | None, list[dict[str, str]], int],
]:
    """Restore in-memory request context from serialized checkpoint data."""
    context: dict[
        str,
        tuple[str, SearchResult, str | None, str | None, list[dict[str, str]], int],
    ] = {}
    for custom_id, entry in data.items():
        result = SearchResult(**entry["result"])
        context[custom_id] = (
            entry["query"],
            result,
            entry["query_type"],
            entry["corrected_query"],
            entry["failed_checks"],
            entry["query_index"],
        )
    return context
