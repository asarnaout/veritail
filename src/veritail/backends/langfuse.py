"""Langfuse-based evaluation backend."""

from __future__ import annotations

import warnings
from typing import Any

from langfuse import Langfuse

from veritail.backends import EvalBackend
from veritail.types import CorrectionJudgment, JudgmentRecord, SuggestionJudgment


class LangfuseBackend(EvalBackend):
    """Backend using Langfuse for tracing, scoring, and human annotation.

    Provides the richest experience:
    - Every LLM judge call stored as a trace with full prompt/response
    - Score storage for both LLM-generated and human-annotated scores
    - Built-in annotation queue UI for human review
    - Experiment tracking and versioning across runs

    Configuration can be provided via constructor args or environment variables:
        LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY, LANGFUSE_BASE_URL
    """

    def __init__(
        self,
        url: str | None = None,
        public_key: str | None = None,
        secret_key: str | None = None,
    ) -> None:
        kwargs: dict[str, Any] = {}
        if url:
            kwargs["base_url"] = url
        if public_key:
            kwargs["public_key"] = public_key
        if secret_key:
            kwargs["secret_key"] = secret_key

        self._client: Any = Langfuse(**kwargs)
        self._session_id: str | None = None

    def log_judgment(self, judgment: JudgmentRecord) -> None:
        """Store a judgment as a Langfuse generation with a relevance score."""
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

        trace_id = Langfuse.create_trace_id(
            seed=f"{judgment.experiment}:{judgment.query}:{product.product_id}"
        )
        trace_context = {"trace_id": trace_id}

        span = self._client.start_span(
            trace_context=trace_context,
            name="veritail-judgment",
            metadata={
                "experiment": judgment.experiment,
                "query": judgment.query,
                "product": product_data,
                "attribute_verdict": judgment.attribute_verdict,
                "model": judgment.model,
                "query_type": judgment.query_type,
            },
        )
        if self._session_id:
            self._client.update_current_trace(session_id=self._session_id)

        generation = span.start_generation(
            name="relevance-judgment",
            model=judgment.model,
            metadata={
                "query": judgment.query,
                "product": product_data,
            },
            output=judgment.reasoning,
            usage_details={
                "input": judgment.metadata.get("input_tokens", 0),
                "output": judgment.metadata.get("output_tokens", 0),
            },
        )
        generation.end()
        span.end()

        self._client.create_score(
            trace_id=trace_id,
            name="relevance",
            value=float(judgment.score),
            comment=judgment.reasoning,
        )

    def log_experiment(
        self, name: str, config: dict[str, Any], *, resume: bool = False
    ) -> None:
        """Register an experiment as a Langfuse span."""
        self._session_id = name

        trace_id = Langfuse.create_trace_id(seed=f"experiment:{name}")
        trace_context = {"trace_id": trace_id}

        span = self._client.start_span(
            trace_context=trace_context,
            name=f"experiment-{name}",
            metadata={
                "experiment_config": config,
                "type": "experiment_registration",
            },
        )
        if self._session_id:
            self._client.update_current_trace(session_id=self._session_id)
        span.end()

    def get_judgments(self, experiment: str) -> list[JudgmentRecord]:
        """Retrieve judgments from Langfuse.

        Note: The Langfuse v3 SDK removed ``fetch_traces`` / ``fetch_scores``.
        Judgment retrieval now requires the Langfuse REST API.  For most
        veritail workflows the file backend handles retrieval; Langfuse is
        used primarily as an observability sink.  This method is kept as a
        stub so the interface contract is satisfied.
        """
        warnings.warn(
            "LangfuseBackend.get_judgments is not supported in Langfuse SDK v3. "
            "Use the file backend for judgment retrieval or query the Langfuse "
            "REST API directly.",
            stacklevel=2,
        )
        return []

    def log_correction_judgment(self, judgment: CorrectionJudgment) -> None:
        """Store a correction judgment as a Langfuse generation with a score."""
        trace_id = Langfuse.create_trace_id(
            seed=(
                f"{judgment.experiment}:correction:"
                f"{judgment.original_query}:{judgment.corrected_query}"
            )
        )
        trace_context = {"trace_id": trace_id}

        span = self._client.start_span(
            trace_context=trace_context,
            name="veritail-correction-judgment",
            metadata={
                "experiment": judgment.experiment,
                "original_query": judgment.original_query,
                "corrected_query": judgment.corrected_query,
                "verdict": judgment.verdict,
                "model": judgment.model,
            },
        )
        if self._session_id:
            self._client.update_current_trace(session_id=self._session_id)
        span.end()

        self._client.create_score(
            trace_id=trace_id,
            name="correction_appropriate",
            value=1.0 if judgment.verdict == "appropriate" else 0.0,
            comment=judgment.reasoning,
        )

    def log_suggestion_judgment(self, judgment: SuggestionJudgment) -> None:
        """Store a suggestion judgment as a Langfuse generation with scores."""
        trace_id = Langfuse.create_trace_id(
            seed=f"{judgment.experiment}:autocomplete:{judgment.prefix}"
        )
        trace_context = {"trace_id": trace_id}

        span = self._client.start_span(
            trace_context=trace_context,
            name="veritail-suggestion-judgment",
            metadata={
                "experiment": judgment.experiment,
                "prefix": judgment.prefix,
                "suggestions": judgment.suggestions,
                "flagged_suggestions": judgment.flagged_suggestions,
                "model": judgment.model,
            },
        )
        if self._session_id:
            self._client.update_current_trace(session_id=self._session_id)

        generation = span.start_generation(
            name="suggestion-judgment",
            model=judgment.model,
            metadata={
                "prefix": judgment.prefix,
                "suggestions": judgment.suggestions,
            },
            output=judgment.reasoning,
            usage_details={
                "input": judgment.metadata.get("input_tokens", 0),
                "output": judgment.metadata.get("output_tokens", 0),
            },
        )
        generation.end()
        span.end()

        self._client.create_score(
            trace_id=trace_id,
            name="autocomplete_relevance",
            value=float(judgment.relevance_score),
            comment=judgment.reasoning,
        )
        self._client.create_score(
            trace_id=trace_id,
            name="autocomplete_diversity",
            value=float(judgment.diversity_score),
            comment=judgment.reasoning,
        )
