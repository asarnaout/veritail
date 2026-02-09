"""Langfuse-based evaluation backend."""

from __future__ import annotations

import random
from typing import Any

from langfuse import Langfuse

from search_eval.backends import EvalBackend
from search_eval.types import HumanScore, JudgmentRecord, SearchResult


class LangfuseBackend(EvalBackend):
    """Backend using Langfuse for tracing, scoring, and human annotation.

    Provides the richest experience:
    - Every LLM judge call stored as a trace with full prompt/response
    - Score storage for both LLM-generated and human-annotated scores
    - Built-in annotation queue UI for human review
    - Experiment tracking and versioning across runs

    Configuration can be provided via constructor args or environment variables:
        LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY, LANGFUSE_HOST
    """

    def __init__(
        self,
        url: str | None = None,
        public_key: str | None = None,
        secret_key: str | None = None,
    ) -> None:
        kwargs: dict[str, Any] = {}
        if url:
            kwargs["host"] = url
        if public_key:
            kwargs["public_key"] = public_key
        if secret_key:
            kwargs["secret_key"] = secret_key

        self._client = Langfuse(**kwargs)

    def log_judgment(self, judgment: JudgmentRecord) -> None:
        """Store a judgment as a Langfuse trace with a generation span and score."""
        trace = self._client.trace(
            name=f"search-eval-judgment",
            metadata={
                "experiment": judgment.experiment,
                "query": judgment.query,
                "product_id": judgment.product.product_id,
                "product_title": judgment.product.title,
            },
            tags=[judgment.experiment],
        )

        trace.generation(
            name="relevance-judgment",
            model=judgment.model,
            metadata={
                "query": judgment.query,
                "product": {
                    "product_id": judgment.product.product_id,
                    "title": judgment.product.title,
                    "category": judgment.product.category,
                    "price": judgment.product.price,
                },
            },
            output=judgment.reasoning,
            usage={
                "input": judgment.metadata.get("input_tokens", 0),
                "output": judgment.metadata.get("output_tokens", 0),
            },
        )

        trace.score(
            name="relevance",
            value=judgment.score,
            comment=judgment.reasoning,
        )

    def log_experiment(self, name: str, config: dict[str, Any]) -> None:
        """Create a Langfuse session/dataset for the experiment."""
        self._client.trace(
            name=f"experiment-{name}",
            metadata={"experiment_config": config, "type": "experiment_registration"},
            tags=[name, "experiment-config"],
        )

    def get_human_scores(self, experiment: str) -> list[HumanScore]:
        """Retrieve human annotation scores from Langfuse."""
        scores: list[HumanScore] = []

        # Fetch traces for this experiment
        traces = self._client.fetch_traces(tags=[experiment])
        for trace in traces.data:
            # Look for human-annotated scores
            trace_scores = self._client.fetch_scores(trace_id=trace.id)
            for score in trace_scores.data:
                if score.name == "human-relevance" and trace.metadata:
                    scores.append(
                        HumanScore(
                            query=trace.metadata.get("query", ""),
                            product_id=trace.metadata.get("product_id", ""),
                            score=int(score.value),
                            experiment=experiment,
                        )
                    )

        return scores

    def get_judgments(self, experiment: str) -> list[JudgmentRecord]:
        """Retrieve all LLM judgments from Langfuse traces."""
        judgments: list[JudgmentRecord] = []

        traces = self._client.fetch_traces(tags=[experiment])
        for trace in traces.data:
            if not trace.metadata or trace.metadata.get("type") == "experiment_registration":
                continue

            # Find the relevance score
            trace_scores = self._client.fetch_scores(trace_id=trace.id)
            relevance_score = None
            reasoning = ""
            for score in trace_scores.data:
                if score.name == "relevance":
                    relevance_score = int(score.value)
                    reasoning = score.comment or ""
                    break

            if relevance_score is None:
                continue

            product = SearchResult(
                product_id=trace.metadata.get("product_id", ""),
                title=trace.metadata.get("product_title", ""),
                description="",
                category="",
                price=0.0,
                position=0,
            )

            judgments.append(
                JudgmentRecord(
                    query=trace.metadata.get("query", ""),
                    product=product,
                    score=relevance_score,
                    reasoning=reasoning,
                    model="",
                    experiment=experiment,
                )
            )

        return judgments

    def create_review_queue(
        self,
        experiment: str,
        sample_rate: float,
        strategy: str = "random",
    ) -> None:
        """Create a Langfuse annotation queue with sampled traces.

        Users can then review and annotate in the Langfuse web UI.
        """
        traces = self._client.fetch_traces(tags=[experiment])
        all_traces = [
            t for t in traces.data
            if t.metadata and t.metadata.get("type") != "experiment_registration"
        ]

        if not all_traces:
            return

        sample_size = max(1, int(len(all_traces) * sample_rate))
        sampled = random.sample(all_traces, min(sample_size, len(all_traces)))

        # Tag sampled traces for review
        for trace in sampled:
            self._client.trace(
                id=trace.id,
                tags=list(set((trace.tags or []) + [f"{experiment}-review"])),
            )
