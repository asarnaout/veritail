"""Integration tests for the evaluation pipeline."""

from __future__ import annotations

from unittest.mock import Mock

import pytest

from veritail.backends import EvalBackend
from veritail.backends.file import FileBackend
from veritail.checkpoint import BatchCheckpoint, save_checkpoint
from veritail.llm.client import BatchRequest, BatchResult, LLMClient, LLMResponse
from veritail.pipeline import run_batch_evaluation, run_dual_evaluation, run_evaluation
from veritail.types import (
    CheckResult,
    ExperimentConfig,
    QueryEntry,
    SearchResponse,
    SearchResult,
)


def _make_mock_adapter():
    """Create a mock adapter that returns fixed results."""

    def adapter(query: str) -> list[SearchResult]:
        return [
            SearchResult(
                product_id=f"SKU-{i}",
                title=f"Result {i} for {query}",
                description=f"Description for result {i}",
                category="Shoes > Running",
                price=100.0 + i * 10,
                position=i,
                attributes={"color": "black"},
            )
            for i in range(3)
        ]

    return adapter


def _make_mock_llm_client() -> LLMClient:
    """Create a mock LLM client that returns canned responses."""
    client = Mock(spec=LLMClient)
    # Return different scores for different calls
    responses = [
        LLMResponse(
            content="SCORE: 3\nATTRIBUTES: match\nREASONING: Excellent match",
            model="test",
            input_tokens=100,
            output_tokens=50,
        ),
        LLMResponse(
            content="SCORE: 2\nATTRIBUTES: partial\nREASONING: Good match",
            model="test",
            input_tokens=100,
            output_tokens=50,
        ),
        LLMResponse(
            content="SCORE: 1\nATTRIBUTES: mismatch\nREASONING: Marginal match",
            model="test",
            input_tokens=100,
            output_tokens=50,
        ),
    ]
    client.complete.side_effect = responses * 10  # enough for multiple queries
    return client


class TestRunEvaluation:
    def test_basic_pipeline(self, tmp_path):
        queries = [
            QueryEntry(query="running shoes", type="broad"),
        ]
        adapter = _make_mock_adapter()
        config = ExperimentConfig(
            name="test-exp",
            adapter_path="test.py",
            llm_model="test-model",
            rubric="ecommerce-default",
            top_k=3,
        )
        llm_client = _make_mock_llm_client()
        backend = FileBackend(output_dir=str(tmp_path))
        rubric = ("system prompt", lambda q, r: f"Query: {q}\nProduct: {r.title}")

        judgments, checks, metrics, corrections = run_evaluation(
            queries,
            adapter,
            config,
            llm_client,
            rubric,
            backend,
        )

        # Should have 3 judgments (1 query * 3 results)
        assert len(judgments) == 3
        assert judgments[0].score == 3
        assert judgments[1].score == 2
        assert judgments[2].score == 1

        # Should have checks
        assert len(checks) > 0

        # Should have metrics
        metric_names = [m.metric_name for m in metrics]
        assert "ndcg@10" in metric_names
        assert "mrr" in metric_names

        # No corrections since adapter returns bare list
        assert len(corrections) == 0

        # Judgments should be persisted in backend
        stored = backend.get_judgments("test-exp")
        assert len(stored) == 3

    def test_multiple_queries(self, tmp_path):
        queries = [
            QueryEntry(query="running shoes", type="broad"),
            QueryEntry(query="laptop stand", type="navigational"),
        ]
        adapter = _make_mock_adapter()
        config = ExperimentConfig(
            name="test-exp",
            adapter_path="test.py",
            llm_model="test-model",
            rubric="ecommerce-default",
            top_k=3,
        )
        llm_client = _make_mock_llm_client()
        backend = FileBackend(output_dir=str(tmp_path))
        rubric = ("system prompt", lambda q, r: f"Query: {q}")

        judgments, checks, metrics, corrections = run_evaluation(
            queries,
            adapter,
            config,
            llm_client,
            rubric,
            backend,
        )

        # 2 queries * 3 results = 6 judgments
        assert len(judgments) == 6

        # Metrics should have per-query values
        ndcg = next(m for m in metrics if m.metric_name == "ndcg@10")
        assert "running shoes" in ndcg.per_query
        assert "laptop stand" in ndcg.per_query

    def test_vertical_in_system_prompt(self, tmp_path):
        """Vertical context appears in the system prompt sent to the LLM."""
        queries = [QueryEntry(query="steam table", type="broad")]
        adapter = _make_mock_adapter()
        config = ExperimentConfig(
            name="test-exp",
            adapter_path="test.py",
            llm_model="test-model",
            rubric="ecommerce-default",
            top_k=3,
        )
        llm_client = _make_mock_llm_client()
        backend = FileBackend(output_dir=str(tmp_path))
        rubric = ("You are an expert judge.", lambda q, r: f"Query: {q}")

        vertical_text = "## Vertical: Foodservice\nFood-safety certs matter."

        run_evaluation(
            queries,
            adapter,
            config,
            llm_client,
            rubric,
            backend,
            vertical=vertical_text,
        )

        # The system prompt passed to RelevanceJudge should contain the vertical
        system_prompt_used = (
            llm_client.complete.call_args_list[0][1].get("system_prompt")
            or llm_client.complete.call_args_list[0][0][0]
        )
        assert "Foodservice" in system_prompt_used
        assert "You are an expert judge." in system_prompt_used

    def test_context_and_vertical_compose(self, tmp_path):
        """Context comes before vertical, which comes before the rubric."""
        queries = [QueryEntry(query="gloves", type="broad")]
        adapter = _make_mock_adapter()
        config = ExperimentConfig(
            name="test-exp",
            adapter_path="test.py",
            llm_model="test-model",
            rubric="ecommerce-default",
            top_k=3,
        )
        llm_client = _make_mock_llm_client()
        backend = FileBackend(output_dir=str(tmp_path))
        rubric = ("RUBRIC_START", lambda q, r: f"Query: {q}")

        run_evaluation(
            queries,
            adapter,
            config,
            llm_client,
            rubric,
            backend,
            context="BBQ restaurant supplier",
            vertical="## Vertical: Foodservice\nScoring guidance here.",
        )

        system_prompt_used = (
            llm_client.complete.call_args_list[0][1].get("system_prompt")
            or llm_client.complete.call_args_list[0][0][0]
        )

        ctx_pos = system_prompt_used.index("## Business Context")
        vert_pos = system_prompt_used.index("## Vertical: Foodservice")
        rubric_pos = system_prompt_used.index("RUBRIC_START")

        assert ctx_pos < vert_pos < rubric_pos

    def test_vertical_alone_no_business_context_header(self, tmp_path):
        """Vertical without context should not produce a Business Context header."""
        queries = [QueryEntry(query="pan", type="broad")]
        adapter = _make_mock_adapter()
        config = ExperimentConfig(
            name="test-exp",
            adapter_path="test.py",
            llm_model="test-model",
            rubric="ecommerce-default",
            top_k=3,
        )
        llm_client = _make_mock_llm_client()
        backend = FileBackend(output_dir=str(tmp_path))
        rubric = ("RUBRIC", lambda q, r: f"Query: {q}")

        run_evaluation(
            queries,
            adapter,
            config,
            llm_client,
            rubric,
            backend,
            vertical="## Vertical: Foodservice\nGuidance.",
        )

        system_prompt_used = (
            llm_client.complete.call_args_list[0][1].get("system_prompt")
            or llm_client.complete.call_args_list[0][0][0]
        )

        assert "## Business Context" not in system_prompt_used
        assert "## Vertical: Foodservice" in system_prompt_used

    def test_adapter_error_handled(self, tmp_path):
        queries = [QueryEntry(query="error query", type="broad")]

        def failing_adapter(query: str):
            raise RuntimeError("API down")

        config = ExperimentConfig(
            name="test-exp",
            adapter_path="test.py",
            llm_model="test",
            rubric="default",
        )
        llm_client = _make_mock_llm_client()
        backend = FileBackend(output_dir=str(tmp_path))
        rubric = ("system", lambda q, r: q)

        judgments, checks, metrics, corrections = run_evaluation(
            queries,
            failing_adapter,
            config,
            llm_client,
            rubric,
            backend,
        )

        # No judgments because adapter failed
        assert len(judgments) == 0

    def test_failed_query_counts_as_zero_in_metrics(self, tmp_path):
        """Queries where the adapter fails must be included in metric aggregates as 0.0,
        not silently dropped from the denominator."""
        queries = [
            QueryEntry(query="good query", type="broad"),
            QueryEntry(query="bad query", type="broad"),
        ]

        def mixed_adapter(query: str) -> list[SearchResult]:
            if query == "bad query":
                raise RuntimeError("adapter error")
            return [
                SearchResult(
                    product_id="SKU-1",
                    title="Perfect Result",
                    description="desc",
                    category="Shoes",
                    price=50.0,
                    position=0,
                )
            ]

        config = ExperimentConfig(
            name="test-exp",
            adapter_path="test.py",
            llm_model="test-model",
            rubric="ecommerce-default",
            top_k=3,
        )
        # LLM always returns score 3 for the successful query
        llm_client = Mock(spec=LLMClient)
        llm_client.complete.return_value = LLMResponse(
            content="SCORE: 3\nATTRIBUTES: match\nREASONING: Perfect",
            model="test",
            input_tokens=10,
            output_tokens=10,
        )
        backend = FileBackend(output_dir=str(tmp_path))
        rubric = ("system", lambda q, r: f"Query: {q}")

        judgments, checks, metrics, corrections = run_evaluation(
            queries,
            mixed_adapter,
            config,
            llm_client,
            rubric,
            backend,
        )

        ndcg = next(m for m in metrics if m.metric_name == "ndcg@10")

        # Both queries must appear in per_query
        assert "good query" in ndcg.per_query
        assert "bad query" in ndcg.per_query

        # Failed query scores 0
        assert ndcg.per_query["bad query"] == 0.0

        # Aggregate must be the mean of both (not just the good query)
        expected_aggregate = (ndcg.per_query["good query"] + 0.0) / 2
        assert ndcg.value == pytest.approx(expected_aggregate)

    def test_duplicate_query_rows_are_counted_separately(self, tmp_path):
        """Duplicate query text should not collapse into one metric row."""
        queries = [
            QueryEntry(query="same query", type="broad"),
            QueryEntry(query="same query", type="broad"),
        ]

        def adapter(query: str) -> list[SearchResult]:
            return [
                SearchResult(
                    product_id="SKU-1",
                    title="Result",
                    description="desc",
                    category="Shoes",
                    price=50.0,
                    position=0,
                )
            ]

        config = ExperimentConfig(
            name="test-exp",
            adapter_path="test.py",
            llm_model="test-model",
            rubric="ecommerce-default",
            top_k=1,
        )
        llm_client = Mock(spec=LLMClient)
        llm_client.complete.side_effect = [
            LLMResponse(
                content="SCORE: 3\nATTRIBUTES: n/a\nREASONING: Perfect",
                model="test",
                input_tokens=10,
                output_tokens=10,
            ),
            LLMResponse(
                content="SCORE: 0\nATTRIBUTES: n/a\nREASONING: Irrelevant",
                model="test",
                input_tokens=10,
                output_tokens=10,
            ),
        ]
        backend = FileBackend(output_dir=str(tmp_path))
        rubric = ("system", lambda q, r: f"Query: {q}")

        judgments, checks, metrics, corrections = run_evaluation(
            queries,
            adapter,
            config,
            llm_client,
            rubric,
            backend,
        )

        assert len(judgments) == 2
        ndcg = next(m for m in metrics if m.metric_name == "ndcg@10")
        assert "same query [1]" in ndcg.per_query
        assert "same query [2]" in ndcg.per_query
        assert ndcg.per_query["same query [1]"] == pytest.approx(1.0)
        assert ndcg.per_query["same query [2]"] == pytest.approx(0.0)
        assert ndcg.value == pytest.approx(0.5)

    def test_custom_checks_are_included(self, tmp_path):
        """Custom check results appear alongside built-in checks."""
        queries = [QueryEntry(query="running shoes", type="broad")]
        adapter = _make_mock_adapter()
        config = ExperimentConfig(
            name="test-exp",
            adapter_path="test.py",
            llm_model="test-model",
            rubric="ecommerce-default",
            top_k=3,
        )
        llm_client = _make_mock_llm_client()
        backend = FileBackend(output_dir=str(tmp_path))
        rubric = ("system prompt", lambda q, r: f"Query: {q}")

        def custom_check(query, results):
            return [
                CheckResult(
                    check_name="custom_always_fail",
                    query=query.query,
                    product_id=None,
                    passed=False,
                    detail="Custom check failed",
                )
            ]

        judgments, checks, metrics, corrections = run_evaluation(
            queries,
            adapter,
            config,
            llm_client,
            rubric,
            backend,
            custom_checks=[custom_check],
        )

        custom = [c for c in checks if c.check_name == "custom_always_fail"]
        assert len(custom) == 1
        assert not custom[0].passed
        # Built-in checks should still be present
        builtin = [c for c in checks if c.check_name != "custom_always_fail"]
        assert len(builtin) > 0

    def test_correction_flow(self, tmp_path):
        """Adapter returning SearchResponse with corrected_query triggers
        correction checks and LLM correction evaluation."""
        queries = [QueryEntry(query="runnign shoes", type="broad")]

        def adapter(query: str) -> SearchResponse:
            return SearchResponse(
                results=[
                    SearchResult(
                        product_id="SKU-1",
                        title="Running Shoes",
                        description="Great running shoes",
                        category="Shoes",
                        price=100.0,
                        position=0,
                    )
                ],
                corrected_query="running shoes",
            )

        config = ExperimentConfig(
            name="test-exp",
            adapter_path="test.py",
            llm_model="test-model",
            rubric="ecommerce-default",
            top_k=3,
        )
        llm_client = Mock(spec=LLMClient)
        # First call: relevance judgment, second call: correction judgment
        llm_client.complete.side_effect = [
            LLMResponse(
                content="SCORE: 3\nATTRIBUTES: match\nREASONING: Perfect",
                model="test",
                input_tokens=100,
                output_tokens=50,
            ),
            LLMResponse(
                content=("VERDICT: appropriate\nREASONING: Spelling fix."),
                model="test",
                input_tokens=80,
                output_tokens=30,
            ),
        ]
        backend = FileBackend(output_dir=str(tmp_path))
        rubric = ("system prompt", lambda q, r: f"Query: {q}")

        judgments, checks, metrics, corrections = run_evaluation(
            queries,
            adapter,
            config,
            llm_client,
            rubric,
            backend,
        )

        # Should have correction checks
        corr_checks = [
            c
            for c in checks
            if c.check_name in ("correction_vocabulary", "unnecessary_correction")
        ]
        assert len(corr_checks) == 2

        # Should have one correction judgment
        assert len(corrections) == 1
        assert corrections[0].verdict == "appropriate"
        assert corrections[0].original_query == "runnign shoes"
        assert corrections[0].corrected_query == "running shoes"

        # Judgment metadata should include corrected_query
        assert judgments[0].metadata["corrected_query"] == "running shoes"

    def test_no_corrections_when_none(self, tmp_path):
        """Adapter returning no corrected_query produces zero corrections."""
        queries = [QueryEntry(query="shoes", type="broad")]
        adapter = _make_mock_adapter()
        config = ExperimentConfig(
            name="test-exp",
            adapter_path="test.py",
            llm_model="test-model",
            rubric="ecommerce-default",
            top_k=3,
        )
        llm_client = _make_mock_llm_client()
        backend = FileBackend(output_dir=str(tmp_path))
        rubric = ("system", lambda q, r: f"Query: {q}")

        judgments, checks, metrics, corrections = run_evaluation(
            queries,
            adapter,
            config,
            llm_client,
            rubric,
            backend,
        )

        assert len(corrections) == 0
        # No correction checks should be in the list
        corr_checks = [
            c
            for c in checks
            if c.check_name in ("correction_vocabulary", "unnecessary_correction")
        ]
        assert len(corr_checks) == 0

    def test_empty_corrected_query_normalized_to_none(self, tmp_path):
        """Empty or whitespace corrected_query is treated as None."""
        queries = [QueryEntry(query="shoes", type="broad")]

        def adapter(query: str) -> SearchResponse:
            return SearchResponse(
                results=[
                    SearchResult(
                        product_id="SKU-1",
                        title="Shoes",
                        description="desc",
                        category="Shoes",
                        price=50.0,
                        position=0,
                    )
                ],
                corrected_query="   ",
            )

        config = ExperimentConfig(
            name="test-exp",
            adapter_path="test.py",
            llm_model="test-model",
            rubric="ecommerce-default",
            top_k=3,
        )
        llm_client = _make_mock_llm_client()
        backend = FileBackend(output_dir=str(tmp_path))
        rubric = ("system", lambda q, r: f"Query: {q}")

        judgments, checks, metrics, corrections = run_evaluation(
            queries,
            adapter,
            config,
            llm_client,
            rubric,
            backend,
        )

        assert len(corrections) == 0

    def test_backend_log_judgment_failure_does_not_crash(self, tmp_path):
        """If backend.log_judgment raises, the judgment is still collected."""
        queries = [QueryEntry(query="shoes", type="broad")]
        adapter = _make_mock_adapter()
        config = ExperimentConfig(
            name="test-exp",
            adapter_path="test.py",
            llm_model="test-model",
            rubric="ecommerce-default",
            top_k=3,
        )
        llm_client = _make_mock_llm_client()
        rubric = ("system prompt", lambda q, r: f"Query: {q}")

        backend = Mock(spec=EvalBackend)
        backend.log_judgment.side_effect = RuntimeError("Langfuse down")

        judgments, checks, metrics, corrections = run_evaluation(
            queries,
            adapter,
            config,
            llm_client,
            rubric,
            backend,
        )

        # Judgments still collected despite backend failures
        assert len(judgments) == 3
        assert len(metrics) > 0

    def test_backend_log_experiment_failure_does_not_crash(self, tmp_path):
        """If backend.log_experiment raises, evaluation still runs."""
        queries = [QueryEntry(query="shoes", type="broad")]
        adapter = _make_mock_adapter()
        config = ExperimentConfig(
            name="test-exp",
            adapter_path="test.py",
            llm_model="test-model",
            rubric="ecommerce-default",
            top_k=3,
        )
        llm_client = _make_mock_llm_client()
        rubric = ("system prompt", lambda q, r: f"Query: {q}")

        backend = Mock(spec=EvalBackend)
        backend.log_experiment.side_effect = ConnectionError("Network down")

        judgments, checks, metrics, corrections = run_evaluation(
            queries,
            adapter,
            config,
            llm_client,
            rubric,
            backend,
        )

        assert len(judgments) == 3

    def test_backend_log_correction_failure_does_not_crash(self, tmp_path):
        """If backend.log_correction_judgment raises, corrections still collected."""
        queries = [QueryEntry(query="runnign shoes", type="broad")]

        def adapter(query: str) -> SearchResponse:
            return SearchResponse(
                results=[
                    SearchResult(
                        product_id="SKU-1",
                        title="Running Shoes",
                        description="Great shoes",
                        category="Shoes",
                        price=100.0,
                        position=0,
                    )
                ],
                corrected_query="running shoes",
            )

        config = ExperimentConfig(
            name="test-exp",
            adapter_path="test.py",
            llm_model="test-model",
            rubric="ecommerce-default",
            top_k=3,
        )
        llm_client = Mock(spec=LLMClient)
        llm_client.complete.side_effect = [
            LLMResponse(
                content="SCORE: 3\nATTRIBUTES: match\nREASONING: Perfect",
                model="test",
                input_tokens=100,
                output_tokens=50,
            ),
            LLMResponse(
                content="VERDICT: appropriate\nREASONING: Spelling fix.",
                model="test",
                input_tokens=80,
                output_tokens=30,
            ),
        ]
        rubric = ("system prompt", lambda q, r: f"Query: {q}")

        backend = Mock(spec=EvalBackend)
        backend.log_correction_judgment.side_effect = RuntimeError("Backend down")

        judgments, checks, metrics, corrections = run_evaluation(
            queries,
            adapter,
            config,
            llm_client,
            rubric,
            backend,
        )

        # Correction still collected despite backend failure
        assert len(corrections) == 1
        assert corrections[0].verdict == "appropriate"

    def test_comparison_check_failure_does_not_crash(self, tmp_path):
        """If a comparison check throws, the dual evaluation still completes."""
        queries = [QueryEntry(query="shoes", type="broad")]
        adapter = _make_mock_adapter()
        config_a = ExperimentConfig(
            name="config-a",
            adapter_path="test.py",
            llm_model="test-model",
            rubric="ecommerce-default",
            top_k=3,
        )
        config_b = ExperimentConfig(
            name="config-b",
            adapter_path="test.py",
            llm_model="test-model",
            rubric="ecommerce-default",
            top_k=3,
        )
        llm_client = _make_mock_llm_client()
        backend = FileBackend(output_dir=str(tmp_path))
        rubric = ("system prompt", lambda q, r: f"Query: {q}")

        from unittest.mock import patch

        with patch(
            "veritail.pipeline.check_result_overlap",
            side_effect=RuntimeError("Unexpected error"),
        ):
            result = run_dual_evaluation(
                queries,
                adapter,
                config_a,
                adapter,
                config_b,
                llm_client,
                rubric,
                backend,
            )

        # Should return a valid 9-tuple despite comparison check failure
        assert len(result) == 9
        judgments_a, judgments_b = result[0], result[1]
        assert len(judgments_a) == 3
        assert len(judgments_b) == 3
        # Comparison checks may be empty due to the error
        comparison_checks = result[6]
        assert isinstance(comparison_checks, list)

    def test_correction_error_verdict_counted_in_summary(self, tmp_path, capsys):
        """Error verdicts from failed correction judges are counted separately."""
        queries = [
            QueryEntry(query="plats", type="broad"),
            QueryEntry(query="cambro", type="broad"),
        ]

        def adapter(query: str) -> SearchResponse:
            return SearchResponse(
                results=[
                    SearchResult(
                        product_id="SKU-1",
                        title="Product",
                        description="desc",
                        category="Kitchen",
                        price=50.0,
                        position=0,
                    )
                ],
                corrected_query=query + " corrected",
            )

        config = ExperimentConfig(
            name="test-exp",
            adapter_path="test.py",
            llm_model="test-model",
            rubric="ecommerce-default",
            top_k=1,
        )

        def make_response(content: str) -> LLMResponse:
            return LLMResponse(
                content=content,
                model="test",
                input_tokens=10,
                output_tokens=10,
            )

        llm_client = Mock(spec=LLMClient)
        llm_client.complete.side_effect = [
            # Relevance judgments (2 queries x 1 result)
            make_response("SCORE: 2\nATTRIBUTES: n/a\nREASONING: OK"),
            make_response("SCORE: 2\nATTRIBUTES: n/a\nREASONING: OK"),
            # Correction judgments: first succeeds, second fails
            make_response("VERDICT: appropriate\nREASONING: Spelling fix."),
            RuntimeError("LLM timeout"),
        ]
        backend = FileBackend(output_dir=str(tmp_path))
        rubric = ("system prompt", lambda q, r: f"Query: {q}")

        judgments, checks, metrics, corrections = run_evaluation(
            queries,
            adapter,
            config,
            llm_client,
            rubric,
            backend,
        )

        assert len(corrections) == 2
        verdicts = [c.verdict for c in corrections]
        assert "appropriate" in verdicts
        assert "error" in verdicts

    def test_prepass_classification(self, tmp_path):
        """Queries without type get classified before evaluation."""
        queries = [
            QueryEntry(query="nike air max"),  # type is None
        ]
        adapter = _make_mock_adapter()
        config = ExperimentConfig(
            name="test-exp",
            adapter_path="test.py",
            llm_model="test-model",
            rubric="ecommerce-default",
            top_k=3,
        )
        llm_client = Mock(spec=LLMClient)
        # First call: classifier, then 3 relevance judgments
        llm_client.complete.side_effect = [
            LLMResponse(
                content="QUERY_TYPE: navigational",
                model="test",
                input_tokens=10,
                output_tokens=10,
            ),
            LLMResponse(
                content="SCORE: 3\nATTRIBUTES: match\nREASONING: Excellent",
                model="test",
                input_tokens=100,
                output_tokens=50,
            ),
            LLMResponse(
                content="SCORE: 2\nATTRIBUTES: partial\nREASONING: Good",
                model="test",
                input_tokens=100,
                output_tokens=50,
            ),
            LLMResponse(
                content="SCORE: 1\nATTRIBUTES: mismatch\nREASONING: Marginal",
                model="test",
                input_tokens=100,
                output_tokens=50,
            ),
        ]
        backend = FileBackend(output_dir=str(tmp_path))
        rubric = ("system prompt", lambda q, r: f"Query: {q}")

        judgments, checks, metrics, corrections = run_evaluation(
            queries,
            adapter,
            config,
            llm_client,
            rubric,
            backend,
        )

        # Query type should have been classified
        assert queries[0].type == "navigational"
        # Metrics should have by_type breakdown
        ndcg = next(m for m in metrics if m.metric_name == "ndcg@10")
        assert "navigational" in ndcg.by_query_type


def _make_mock_batch_llm_client(responses: list[str]) -> LLMClient:
    """Create a mock LLM client with batch support.

    The client records submitted BatchRequests and returns pre-built
    BatchResults based on the provided response strings.
    """
    client = Mock(spec=LLMClient)
    client.supports_batch.return_value = True

    submitted: list[list[BatchRequest]] = []

    def submit_batch(requests):
        submitted.append(list(requests))
        return f"batch-{len(submitted)}"

    client.submit_batch.side_effect = submit_batch
    client.poll_batch.return_value = ("completed", 0, 0)

    call_count = [0]

    def retrieve_batch_results(batch_id):
        results = []
        batch_idx = int(batch_id.split("-")[1]) - 1
        reqs = submitted[batch_idx]
        for req in reqs:
            idx = call_count[0]
            content = responses[idx] if idx < len(responses) else "SCORE: 0"
            call_count[0] += 1
            results.append(
                BatchResult(
                    custom_id=req.custom_id,
                    response=LLMResponse(
                        content=content,
                        model="test",
                        input_tokens=100,
                        output_tokens=50,
                    ),
                )
            )
        return results

    client.retrieve_batch_results.side_effect = retrieve_batch_results
    return client


class TestRunBatchEvaluation:
    def test_batch_basic_pipeline(self, tmp_path):
        queries = [QueryEntry(query="running shoes", type="broad")]
        adapter = _make_mock_adapter()
        config = ExperimentConfig(
            name="test-batch",
            adapter_path="test.py",
            llm_model="test-model",
            rubric="ecommerce-default",
            top_k=3,
        )
        responses = [
            "SCORE: 3\nATTRIBUTES: match\nREASONING: Excellent match",
            "SCORE: 2\nATTRIBUTES: partial\nREASONING: Good match",
            "SCORE: 1\nATTRIBUTES: mismatch\nREASONING: Marginal match",
        ]
        llm_client = _make_mock_batch_llm_client(responses)
        backend = FileBackend(output_dir=str(tmp_path))
        rubric = ("system prompt", lambda q, r: f"Query: {q}\nProduct: {r.title}")

        judgments, checks, metrics, corrections = run_batch_evaluation(
            queries,
            adapter,
            config,
            llm_client,
            rubric,
            backend,
            poll_interval=0,
        )

        assert len(judgments) == 3
        assert judgments[0].score == 3
        assert judgments[1].score == 2
        assert judgments[2].score == 1

        assert len(checks) > 0

        metric_names = [m.metric_name for m in metrics]
        assert "ndcg@10" in metric_names
        assert "mrr" in metric_names

        assert len(corrections) == 0
        llm_client.submit_batch.assert_called_once()

    def test_batch_zero_requests(self, tmp_path):
        """All adapters fail → empty judgments, zero-filled metrics."""
        queries = [QueryEntry(query="error query", type="broad")]

        def failing_adapter(query: str):
            raise RuntimeError("API down")

        config = ExperimentConfig(
            name="test-batch",
            adapter_path="test.py",
            llm_model="test",
            rubric="default",
        )
        llm_client = _make_mock_batch_llm_client([])
        backend = FileBackend(output_dir=str(tmp_path))
        rubric = ("system", lambda q, r: q)

        judgments, checks, metrics, corrections = run_batch_evaluation(
            queries,
            failing_adapter,
            config,
            llm_client,
            rubric,
            backend,
            poll_interval=0,
        )

        assert len(judgments) == 0
        llm_client.submit_batch.assert_not_called()

    def test_batch_partial_failures(self, tmp_path):
        """Some results error → score=0 judgments."""
        queries = [QueryEntry(query="running shoes", type="broad")]
        adapter = _make_mock_adapter()
        config = ExperimentConfig(
            name="test-batch",
            adapter_path="test.py",
            llm_model="test-model",
            rubric="ecommerce-default",
            top_k=3,
        )

        client = Mock(spec=LLMClient)
        client.supports_batch.return_value = True
        client.submit_batch.return_value = "batch-1"
        client.poll_batch.return_value = ("completed", 3, 3)

        # First result succeeds, second/third fail
        client.retrieve_batch_results.return_value = [
            BatchResult(
                custom_id="rel-0-0",
                response=LLMResponse(
                    content="SCORE: 3\nATTRIBUTES: match\nREASONING: Good",
                    model="test",
                    input_tokens=100,
                    output_tokens=50,
                ),
            ),
            BatchResult(
                custom_id="rel-0-1",
                response=None,
                error="Rate limit exceeded",
            ),
            BatchResult(
                custom_id="rel-0-2",
                response=None,
                error="Server error",
            ),
        ]

        backend = FileBackend(output_dir=str(tmp_path))
        rubric = ("system prompt", lambda q, r: f"Query: {q}")

        judgments, checks, metrics, corrections = run_batch_evaluation(
            queries,
            adapter,
            config,
            client,
            rubric,
            backend,
            poll_interval=0,
        )

        assert len(judgments) == 3
        assert judgments[0].score == 3
        assert judgments[1].score == 0
        assert "Rate limit" in judgments[1].reasoning
        assert judgments[2].score == 0

    def test_batch_with_corrections(self, tmp_path):
        """Verify two separate batches submitted when corrections exist."""
        queries = [QueryEntry(query="runnign shoes", type="broad")]

        def adapter(query: str) -> SearchResponse:
            return SearchResponse(
                results=[
                    SearchResult(
                        product_id="SKU-1",
                        title="Running Shoes",
                        description="Great shoes",
                        category="Shoes",
                        price=100.0,
                        position=0,
                    )
                ],
                corrected_query="running shoes",
            )

        config = ExperimentConfig(
            name="test-batch",
            adapter_path="test.py",
            llm_model="test-model",
            rubric="ecommerce-default",
            top_k=3,
        )
        responses = [
            # Relevance judgment
            "SCORE: 3\nATTRIBUTES: match\nREASONING: Perfect",
            # Correction judgment
            "VERDICT: appropriate\nREASONING: Spelling fix.",
        ]
        llm_client = _make_mock_batch_llm_client(responses)
        backend = FileBackend(output_dir=str(tmp_path))
        rubric = ("system prompt", lambda q, r: f"Query: {q}")

        judgments, checks, metrics, corrections = run_batch_evaluation(
            queries,
            adapter,
            config,
            llm_client,
            rubric,
            backend,
            poll_interval=0,
        )

        assert len(judgments) == 1
        assert judgments[0].score == 3
        assert len(corrections) == 1
        assert corrections[0].verdict == "appropriate"
        # Two batches: one for relevance, one for corrections
        assert llm_client.submit_batch.call_count == 2

    def test_batch_poll_failure(self, tmp_path):
        """'failed' status → RuntimeError."""
        queries = [QueryEntry(query="shoes", type="broad")]
        adapter = _make_mock_adapter()
        config = ExperimentConfig(
            name="test-batch",
            adapter_path="test.py",
            llm_model="test-model",
            rubric="ecommerce-default",
            top_k=3,
        )

        client = Mock(spec=LLMClient)
        client.supports_batch.return_value = True
        client.submit_batch.return_value = "batch-1"
        client.poll_batch.return_value = ("failed", 0, 3)

        backend = FileBackend(output_dir=str(tmp_path))
        rubric = ("system prompt", lambda q, r: f"Query: {q}")

        with pytest.raises(RuntimeError, match="batch-1 failed"):
            run_batch_evaluation(
                queries,
                adapter,
                config,
                client,
                rubric,
                backend,
                poll_interval=0,
            )

    def test_batch_parse_errors(self, tmp_path):
        """Unparseable LLM output → graceful score=0 fallback."""
        queries = [QueryEntry(query="shoes", type="broad")]

        def adapter(query: str) -> list[SearchResult]:
            return [
                SearchResult(
                    product_id="SKU-1",
                    title="Shoe",
                    description="A shoe",
                    category="Shoes",
                    price=50.0,
                    position=0,
                )
            ]

        config = ExperimentConfig(
            name="test-batch",
            adapter_path="test.py",
            llm_model="test-model",
            rubric="ecommerce-default",
            top_k=1,
        )
        # Response that can't be parsed (no SCORE)
        responses = ["This is a bad response with no score."]
        llm_client = _make_mock_batch_llm_client(responses)
        backend = FileBackend(output_dir=str(tmp_path))
        rubric = ("system prompt", lambda q, r: f"Query: {q}")

        judgments, checks, metrics, corrections = run_batch_evaluation(
            queries,
            adapter,
            config,
            llm_client,
            rubric,
            backend,
            poll_interval=0,
        )

        assert len(judgments) == 1
        assert judgments[0].score == 0
        assert "Error" in judgments[0].reasoning

    def test_batch_results_match_non_batch(self, tmp_path):
        """Same LLM content through both paths → identical scores."""
        queries = [QueryEntry(query="running shoes", type="broad")]

        def adapter(query: str) -> list[SearchResult]:
            return [
                SearchResult(
                    product_id="SKU-1",
                    title="Running Shoes",
                    description="Great shoes",
                    category="Shoes",
                    price=100.0,
                    position=0,
                )
            ]

        rubric = ("system prompt", lambda q, r: f"Query: {q}")
        response_text = "SCORE: 3\nATTRIBUTES: match\nREASONING: Perfect"

        # Non-batch path
        config_sync = ExperimentConfig(
            name="test-sync",
            adapter_path="test.py",
            llm_model="test-model",
            rubric="ecommerce-default",
            top_k=1,
        )
        sync_client = Mock(spec=LLMClient)
        sync_client.complete.return_value = LLMResponse(
            content=response_text,
            model="test",
            input_tokens=100,
            output_tokens=50,
        )
        backend_sync = FileBackend(output_dir=str(tmp_path / "sync"))
        j_sync, _, m_sync, _ = run_evaluation(
            queries, adapter, config_sync, sync_client, rubric, backend_sync
        )

        # Batch path
        config_batch = ExperimentConfig(
            name="test-batch",
            adapter_path="test.py",
            llm_model="test-model",
            rubric="ecommerce-default",
            top_k=1,
        )
        batch_client = _make_mock_batch_llm_client([response_text])
        backend_batch = FileBackend(output_dir=str(tmp_path / "batch"))
        j_batch, _, m_batch, _ = run_batch_evaluation(
            queries,
            adapter,
            config_batch,
            batch_client,
            rubric,
            backend_batch,
            poll_interval=0,
        )

        assert len(j_sync) == len(j_batch) == 1
        assert j_sync[0].score == j_batch[0].score
        assert j_sync[0].attribute_verdict == j_batch[0].attribute_verdict

        ndcg_sync = next(m for m in m_sync if m.metric_name == "ndcg@10")
        ndcg_batch = next(m for m in m_batch if m.metric_name == "ndcg@10")
        assert ndcg_sync.value == pytest.approx(ndcg_batch.value)

    def test_batch_prepass_classification(self, tmp_path):
        """Queries without type get classified via batch API before evaluation."""
        queries = [
            QueryEntry(query="nike air max"),  # type is None
        ]
        adapter = _make_mock_adapter()
        config = ExperimentConfig(
            name="test-batch",
            adapter_path="test.py",
            llm_model="test-model",
            rubric="ecommerce-default",
            top_k=3,
        )
        # Classification batch + relevance batch = 2 submit_batch calls
        responses = [
            # Classification batch result
            "QUERY_TYPE: navigational",
            # Relevance batch results (3 results for 1 query)
            "SCORE: 3\nATTRIBUTES: match\nREASONING: Excellent",
            "SCORE: 2\nATTRIBUTES: partial\nREASONING: Good",
            "SCORE: 1\nATTRIBUTES: mismatch\nREASONING: Marginal",
        ]
        llm_client = _make_mock_batch_llm_client(responses)
        backend = FileBackend(output_dir=str(tmp_path))
        rubric = ("system prompt", lambda q, r: f"Query: {q}")

        judgments, checks, metrics, corrections = run_batch_evaluation(
            queries,
            adapter,
            config,
            llm_client,
            rubric,
            backend,
            poll_interval=0,
        )

        # Query type should have been classified
        assert queries[0].type == "navigational"
        # Two batches submitted: classification + relevance
        assert llm_client.submit_batch.call_count == 2
        # Metrics should have by_type breakdown
        ndcg = next(m for m in metrics if m.metric_name == "ndcg@10")
        assert "navigational" in ndcg.by_query_type

    def test_batch_concurrent_submit_both_upfront(self, tmp_path):
        """Both relevance and correction batches are submitted before polling."""
        queries = [QueryEntry(query="runnign shoes", type="broad")]

        def adapter(query: str) -> SearchResponse:
            return SearchResponse(
                results=[
                    SearchResult(
                        product_id="SKU-1",
                        title="Running Shoes",
                        description="Great shoes",
                        category="Shoes",
                        price=100.0,
                        position=0,
                    )
                ],
                corrected_query="running shoes",
            )

        config = ExperimentConfig(
            name="test-batch",
            adapter_path="test.py",
            llm_model="test-model",
            rubric="ecommerce-default",
            top_k=3,
        )
        responses = [
            "SCORE: 3\nATTRIBUTES: match\nREASONING: Perfect",
            "VERDICT: appropriate\nREASONING: Spelling fix.",
        ]
        llm_client = _make_mock_batch_llm_client(responses)
        backend = FileBackend(output_dir=str(tmp_path))
        rubric = ("system prompt", lambda q, r: f"Query: {q}")

        judgments, checks, metrics, corrections = run_batch_evaluation(
            queries,
            adapter,
            config,
            llm_client,
            rubric,
            backend,
            poll_interval=0,
        )

        # Both batches submitted before polling: 2 submit_batch calls
        assert llm_client.submit_batch.call_count == 2
        # Both results processed correctly
        assert len(judgments) == 1
        assert judgments[0].score == 3
        assert len(corrections) == 1
        assert corrections[0].verdict == "appropriate"

        # Verify submit order: relevance first, corrections second
        first_batch_reqs = llm_client.submit_batch.call_args_list[0][0][0]
        second_batch_reqs = llm_client.submit_batch.call_args_list[1][0][0]
        assert first_batch_reqs[0].custom_id.startswith("rel-")
        assert second_batch_reqs[0].custom_id.startswith("corr-")

    def test_batch_no_corrections_single_submit(self, tmp_path):
        """Only 1 submit_batch when there are no corrections."""
        queries = [QueryEntry(query="shoes", type="broad")]
        adapter = _make_mock_adapter()
        config = ExperimentConfig(
            name="test-batch",
            adapter_path="test.py",
            llm_model="test-model",
            rubric="ecommerce-default",
            top_k=3,
        )
        responses = [
            "SCORE: 3\nATTRIBUTES: match\nREASONING: Excellent",
            "SCORE: 2\nATTRIBUTES: partial\nREASONING: Good",
            "SCORE: 1\nATTRIBUTES: mismatch\nREASONING: Marginal",
        ]
        llm_client = _make_mock_batch_llm_client(responses)
        backend = FileBackend(output_dir=str(tmp_path))
        rubric = ("system prompt", lambda q, r: f"Query: {q}")

        judgments, checks, metrics, corrections = run_batch_evaluation(
            queries,
            adapter,
            config,
            llm_client,
            rubric,
            backend,
            poll_interval=0,
        )

        # Only relevance batch submitted
        assert llm_client.submit_batch.call_count == 1
        assert len(corrections) == 0

    def test_batch_resume_with_correction_batch_id(self, tmp_path):
        """Checkpoint with correction_batch_id resumes and processes both."""
        config = ExperimentConfig(
            name="test-batch",
            adapter_path="test.py",
            llm_model="test-model",
            rubric="ecommerce-default",
            top_k=1,
        )

        # Save a checkpoint with both batch IDs
        from veritail.checkpoint import serialize_request_context

        result = SearchResult(
            product_id="SKU-1",
            title="Shoe",
            description="desc",
            category="Shoes",
            price=50.0,
            position=0,
        )
        req_ctx = {
            "rel-0-0": ("runnign shoes", result, "broad", "running shoes", [], 0)
        }
        cp = BatchCheckpoint(
            batch_id="batch-rel",
            experiment_name="test-batch",
            phase="relevance",
            request_context=serialize_request_context(req_ctx),
            checks=[],
            correction_entries=[[0, "runnign shoes", "running shoes"]],
            correction_batch_id="batch-corr",
            correction_context={
                "corr-0": {"original": "runnign shoes", "corrected": "running shoes"}
            },
        )
        save_checkpoint(str(tmp_path), "test-batch", cp)

        # Mock client that returns completed results for both batches
        client = Mock(spec=LLMClient)
        client.supports_batch.return_value = True
        client.poll_batch.return_value = ("completed", 1, 1)

        client.retrieve_batch_results.side_effect = [
            # Relevance results
            [
                BatchResult(
                    custom_id="rel-0-0",
                    response=LLMResponse(
                        content="SCORE: 3\nATTRIBUTES: match\nREASONING: Perfect",
                        model="test",
                        input_tokens=10,
                        output_tokens=10,
                    ),
                )
            ],
            # Correction results
            [
                BatchResult(
                    custom_id="corr-0",
                    response=LLMResponse(
                        content="VERDICT: appropriate\nREASONING: Spelling fix.",
                        model="test",
                        input_tokens=10,
                        output_tokens=10,
                    ),
                )
            ],
        ]

        backend = FileBackend(output_dir=str(tmp_path))
        rubric = ("system prompt", lambda q, r: f"Query: {q}")
        queries = [QueryEntry(query="runnign shoes", type="broad")]

        judgments, checks, metrics, corrections = run_batch_evaluation(
            queries,
            _make_mock_adapter(),
            config,
            client,
            rubric,
            backend,
            poll_interval=0,
            resume=True,
            output_dir=str(tmp_path),
        )

        # No submit_batch calls (resumed from checkpoint)
        client.submit_batch.assert_not_called()
        assert len(judgments) == 1
        assert judgments[0].score == 3
        assert len(corrections) == 1
        assert corrections[0].verdict == "appropriate"

    def test_batch_resume_backward_compat(self, tmp_path):
        """Old checkpoint without correction_batch_id still works."""
        config = ExperimentConfig(
            name="test-batch",
            adapter_path="test.py",
            llm_model="test-model",
            rubric="ecommerce-default",
            top_k=1,
        )

        from veritail.checkpoint import serialize_request_context

        result = SearchResult(
            product_id="SKU-1",
            title="Shoe",
            description="desc",
            category="Shoes",
            price=50.0,
            position=0,
        )
        req_ctx = {"rel-0-0": ("shoes", result, "broad", None, [], 0)}
        cp = BatchCheckpoint(
            batch_id="batch-rel",
            experiment_name="test-batch",
            phase="relevance",
            request_context=serialize_request_context(req_ctx),
            checks=[],
            correction_entries=[],
            # No correction_batch_id, no correction_context
        )
        save_checkpoint(str(tmp_path), "test-batch", cp)

        client = Mock(spec=LLMClient)
        client.supports_batch.return_value = True
        client.poll_batch.return_value = ("completed", 1, 1)
        client.retrieve_batch_results.return_value = [
            BatchResult(
                custom_id="rel-0-0",
                response=LLMResponse(
                    content="SCORE: 2\nATTRIBUTES: partial\nREASONING: OK",
                    model="test",
                    input_tokens=10,
                    output_tokens=10,
                ),
            )
        ]

        backend = FileBackend(output_dir=str(tmp_path))
        rubric = ("system prompt", lambda q, r: f"Query: {q}")
        queries = [QueryEntry(query="shoes", type="broad")]

        judgments, checks, metrics, corrections = run_batch_evaluation(
            queries,
            _make_mock_adapter(),
            config,
            client,
            rubric,
            backend,
            poll_interval=0,
            resume=True,
            output_dir=str(tmp_path),
        )

        assert len(judgments) == 1
        assert len(corrections) == 0

    def test_batch_correction_batch_fails(self, tmp_path):
        """RuntimeError when correction batch fails."""
        queries = [QueryEntry(query="runnign shoes", type="broad")]

        def adapter(query: str) -> SearchResponse:
            return SearchResponse(
                results=[
                    SearchResult(
                        product_id="SKU-1",
                        title="Running Shoes",
                        description="Great shoes",
                        category="Shoes",
                        price=100.0,
                        position=0,
                    )
                ],
                corrected_query="running shoes",
            )

        config = ExperimentConfig(
            name="test-batch",
            adapter_path="test.py",
            llm_model="test-model",
            rubric="ecommerce-default",
            top_k=1,
        )

        client = Mock(spec=LLMClient)
        client.supports_batch.return_value = True

        submitted: list[list[BatchRequest]] = []

        def submit_batch(requests):
            submitted.append(list(requests))
            return f"batch-{len(submitted)}"

        client.submit_batch.side_effect = submit_batch

        # First poll (relevance): completed; second poll (correction): failed
        client.poll_batch.side_effect = [
            ("completed", 1, 1),
            ("failed", 0, 1),
        ]
        client.batch_error_message.return_value = None

        backend = FileBackend(output_dir=str(tmp_path))
        rubric = ("system prompt", lambda q, r: f"Query: {q}")

        with pytest.raises(RuntimeError, match="batch-2 failed"):
            run_batch_evaluation(
                queries,
                adapter,
                config,
                client,
                rubric,
                backend,
                poll_interval=0,
            )
