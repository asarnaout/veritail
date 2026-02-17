"""Langfuse-based evaluation backend."""

from __future__ import annotations

import warnings
from typing import Any

from langfuse import Langfuse  # type: ignore[import-not-found]

from veritail.backends import EvalBackend
from veritail.types import CorrectionJudgment, JudgmentRecord, SearchResult


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
        product = judgment.product
        product_data: dict[str, Any] = {
            "product_id": product.product_id,
            "title": product.title,
            "description": product.description,
            "category": product.category,
            "price": product.price,
            "position": product.position,
            "in_stock": product.in_stock,
            "attributes": product.attributes,
            "metadata": product.metadata,
        }

        trace = self._client.trace(
            name="veritail-judgment",
            metadata={
                "experiment": judgment.experiment,
                "query": judgment.query,
                "product": product_data,
                "attribute_verdict": judgment.attribute_verdict,
                "model": judgment.model,
                "query_type": judgment.query_type,
            },
            tags=[judgment.experiment],
        )

        trace.generation(
            name="relevance-judgment",
            model=judgment.model,
            metadata={
                "query": judgment.query,
                "product": product_data,
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

    def get_judgments(self, experiment: str) -> list[JudgmentRecord]:
        """Retrieve all LLM judgments from Langfuse traces."""
        judgments: list[JudgmentRecord] = []

        traces = self._client.fetch_traces(tags=[experiment])
        for trace in traces.data:
            try:
                if not trace.metadata:
                    continue
                if trace.metadata.get("type") == "experiment_registration":
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

                product_data = trace.metadata.get("product", {})
                product = SearchResult(
                    product_id=product_data.get("product_id", ""),
                    title=product_data.get("title", ""),
                    description=product_data.get("description", ""),
                    category=product_data.get("category", ""),
                    price=float(product_data.get("price", 0.0)),
                    position=int(product_data.get("position", 0)),
                    in_stock=bool(product_data.get("in_stock", True)),
                    attributes=product_data.get("attributes", {}),
                    metadata=product_data.get("metadata", {}),
                )

                judgments.append(
                    JudgmentRecord(
                        query=trace.metadata.get("query", ""),
                        product=product,
                        score=relevance_score,
                        reasoning=reasoning,
                        attribute_verdict=trace.metadata.get(
                            "attribute_verdict", "n/a"
                        ),
                        model=trace.metadata.get("model", ""),
                        experiment=experiment,
                        query_type=trace.metadata.get("query_type"),
                    )
                )
            except Exception as e:
                trace_id = getattr(trace, "id", "unknown")
                warnings.warn(
                    f"Skipping trace {trace_id}: {e}",
                    stacklevel=2,
                )

        return judgments

    def log_correction_judgment(self, judgment: CorrectionJudgment) -> None:
        """Store a correction judgment as a Langfuse trace with a score."""
        trace = self._client.trace(
            name="veritail-correction-judgment",
            metadata={
                "experiment": judgment.experiment,
                "original_query": judgment.original_query,
                "corrected_query": judgment.corrected_query,
                "verdict": judgment.verdict,
                "model": judgment.model,
            },
            tags=[judgment.experiment, "correction"],
        )

        trace.score(
            name="correction_appropriate",
            value=1 if judgment.verdict == "appropriate" else 0,
            comment=judgment.reasoning,
        )
