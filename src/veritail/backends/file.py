"""File-based evaluation backend using JSONL files."""

from __future__ import annotations

import json
import warnings
from dataclasses import asdict
from pathlib import Path
from typing import Any

from veritail.backends import EvalBackend
from veritail.types import JudgmentRecord, SearchResult


class FileBackend(EvalBackend):
    """Zero-infrastructure backend that stores everything in local files.

    Output structure:
        {output_dir}/{experiment}/
            judgments.jsonl  - All LLM judgments
            config.json      - Experiment configuration
            metrics.json     - Computed IR metrics (written by CLI)
            report.html      - HTML report (written by CLI)
    """

    def __init__(self, output_dir: str = "./eval-results") -> None:
        self._output_dir = Path(output_dir)

    def _experiment_dir(self, experiment: str) -> Path:
        d = self._output_dir / experiment
        d.mkdir(parents=True, exist_ok=True)
        return d

    def _experiment_path(self, experiment: str) -> Path:
        """Return the experiment directory path without creating it."""
        return self._output_dir / experiment

    def log_judgment(self, judgment: JudgmentRecord) -> None:
        """Append a judgment record as a JSON line."""
        exp_dir = self._experiment_dir(judgment.experiment)
        judgments_file = exp_dir / "judgments.jsonl"

        record = asdict(judgment)
        with open(judgments_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, default=str) + "\n")

    def log_experiment(self, name: str, config: dict[str, Any]) -> None:
        """Write experiment configuration to a JSON file."""
        exp_dir = self._experiment_dir(name)
        config_file = exp_dir / "config.json"
        judgments_file = exp_dir / "judgments.jsonl"

        with open(config_file, "w", encoding="utf-8") as f:
            json.dump({"name": name, **config}, f, indent=2, default=str)

        # One experiment run should produce one deterministic judgments file.
        judgments_file.write_text("", encoding="utf-8")

    def get_judgments(self, experiment: str) -> list[JudgmentRecord]:
        """Read all judgments from JSONL file."""
        exp_dir = self._experiment_path(experiment)
        judgments_file = exp_dir / "judgments.jsonl"

        if not judgments_file.exists():
            return []

        judgments: list[JudgmentRecord] = []
        with open(judgments_file, encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    product_data = data.pop("product")
                    data.setdefault("attribute_verdict", "n/a")
                    product = SearchResult(**product_data)
                    judgments.append(JudgmentRecord(product=product, **data))
                except (json.JSONDecodeError, KeyError, TypeError) as e:
                    warnings.warn(
                        f"Skipping corrupted line {line_num} in {judgments_file}: {e}",
                        stacklevel=2,
                    )

        return judgments
