"""File-based evaluation backend using JSONL files."""

from __future__ import annotations

import csv
import json
import random
from dataclasses import asdict
from pathlib import Path
from typing import Any

from veritail.backends import EvalBackend
from veritail.types import HumanScore, JudgmentRecord, SearchResult


class FileBackend(EvalBackend):
    """Zero-infrastructure backend that stores everything in local files.

    Output structure:
        {output_dir}/{experiment}/
            judgments.jsonl      - All LLM judgments
            deterministic.jsonl  - Deterministic check results
            config.json          - Experiment configuration
            review-sample.csv    - Human review export
            human-scores.csv     - Human annotations (filled in manually)
            metrics.json         - Computed IR metrics
    """

    def __init__(self, output_dir: str = "./eval-results") -> None:
        self._output_dir = Path(output_dir)

    def _experiment_dir(self, experiment: str) -> Path:
        d = self._output_dir / experiment
        d.mkdir(parents=True, exist_ok=True)
        return d

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

        with open(config_file, "w", encoding="utf-8") as f:
            json.dump({"name": name, **config}, f, indent=2, default=str)

    def get_human_scores(self, experiment: str) -> list[HumanScore]:
        """Read human scores from CSV file."""
        exp_dir = self._experiment_dir(experiment)
        scores_file = exp_dir / "human-scores.csv"

        if not scores_file.exists():
            return []

        scores: list[HumanScore] = []
        with open(scores_file, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                score_val = row.get("human_score", row.get("score", "")).strip()
                if not score_val:
                    continue
                scores.append(
                    HumanScore(
                        query=row["query"],
                        product_id=row["product_id"],
                        score=int(score_val),
                        experiment=experiment,
                    )
                )
        return scores

    def get_judgments(self, experiment: str) -> list[JudgmentRecord]:
        """Read all judgments from JSONL file."""
        exp_dir = self._experiment_dir(experiment)
        judgments_file = exp_dir / "judgments.jsonl"

        if not judgments_file.exists():
            return []

        judgments: list[JudgmentRecord] = []
        with open(judgments_file, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                data = json.loads(line)
                product_data = data.pop("product")
                product = SearchResult(**product_data)
                judgments.append(JudgmentRecord(product=product, **data))

        return judgments

    def create_review_queue(
        self,
        experiment: str,
        sample_rate: float,
        strategy: str = "random",
    ) -> None:
        """Export a sample of judgments as a CSV for human review.

        The CSV has columns: query, product_id, title, llm_score, llm_reasoning, human_score.
        The human_score column is left blank for reviewers to fill in.
        """
        judgments = self.get_judgments(experiment)
        if not judgments:
            return

        if strategy == "stratified":
            sample = self._stratified_sample(judgments, sample_rate)
        else:
            sample_size = max(1, int(len(judgments) * sample_rate))
            sample = random.sample(judgments, min(sample_size, len(judgments)))

        exp_dir = self._experiment_dir(experiment)
        review_file = exp_dir / "review-sample.csv"

        with open(review_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["query", "product_id", "title", "llm_score", "llm_reasoning", "human_score"])
            for j in sample:
                writer.writerow([
                    j.query,
                    j.product.product_id,
                    j.product.title,
                    j.score,
                    j.reasoning,
                    "",  # human_score left blank
                ])

    @staticmethod
    def _stratified_sample(
        judgments: list[JudgmentRecord],
        sample_rate: float,
    ) -> list[JudgmentRecord]:
        """Sample evenly across score levels."""
        by_score: dict[int, list[JudgmentRecord]] = {}
        for j in judgments:
            by_score.setdefault(j.score, []).append(j)

        sample: list[JudgmentRecord] = []
        for score_level, items in by_score.items():
            n = max(1, int(len(items) * sample_rate))
            sample.extend(random.sample(items, min(n, len(items))))

        return sample
