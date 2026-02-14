"""Integration tests for the evaluation pipeline."""

from __future__ import annotations

from unittest.mock import Mock

import pytest

from veritail.backends.file import FileBackend
from veritail.llm.client import LLMClient, LLMResponse
from veritail.pipeline import run_evaluation
from veritail.types import ExperimentConfig, QueryEntry, SearchResult


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

        judgments, checks, metrics = run_evaluation(
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

        judgments, checks, metrics = run_evaluation(
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
        queries = [QueryEntry(query="error query")]

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

        judgments, checks, metrics = run_evaluation(
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

        judgments, checks, metrics = run_evaluation(
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

        judgments, checks, metrics = run_evaluation(
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

    def test_skip_on_check_fail_skips_failed_result_rows(self, tmp_path):
        queries = [QueryEntry(query="nike shoes", type="broad")]

        def adapter(query: str) -> list[SearchResult]:
            return [
                SearchResult(
                    product_id="SKU-1",
                    title="Nike Air Max 90 Running Shoes Black",
                    description="desc",
                    category="Shoes",
                    price=120.0,
                    position=0,
                ),
                SearchResult(
                    product_id="SKU-2",
                    title="Nike Air Max 90 Running Shoes White",
                    description="desc",
                    category="Shoes",
                    price=121.0,
                    position=1,
                ),
            ]

        config = ExperimentConfig(
            name="test-exp",
            adapter_path="test.py",
            llm_model="test-model",
            rubric="ecommerce-default",
            top_k=10,
        )
        llm_client = Mock(spec=LLMClient)
        llm_client.complete.return_value = LLMResponse(
            content="SCORE: 2\nATTRIBUTES: n/a\nREASONING: Good match",
            model="test",
            input_tokens=10,
            output_tokens=10,
        )
        backend = FileBackend(output_dir=str(tmp_path))
        rubric = ("system", lambda q, r: f"Query: {q}")

        judgments, checks, _ = run_evaluation(
            queries,
            adapter,
            config,
            llm_client,
            rubric,
            backend,
            skip_llm_on_fail=True,
        )

        assert any(c.check_name == "duplicate" and not c.passed for c in checks)
        assert llm_client.complete.call_count == 1

        skipped = [j for j in judgments if j.metadata.get("skipped")]
        assert len(skipped) == 1
        assert skipped[0].product.product_id == "SKU-1"
        assert skipped[0].score == 0
        assert skipped[0].reasoning.startswith("Skipped:")

    def test_skip_on_check_fail_false_keeps_llm_calls(self, tmp_path):
        queries = [QueryEntry(query="nike shoes", type="broad")]

        def adapter(query: str) -> list[SearchResult]:
            return [
                SearchResult(
                    product_id="SKU-1",
                    title="Nike Air Max 90 Running Shoes Black",
                    description="desc",
                    category="Shoes",
                    price=120.0,
                    position=0,
                ),
                SearchResult(
                    product_id="SKU-2",
                    title="Nike Air Max 90 Running Shoes White",
                    description="desc",
                    category="Shoes",
                    price=121.0,
                    position=1,
                ),
            ]

        config = ExperimentConfig(
            name="test-exp",
            adapter_path="test.py",
            llm_model="test-model",
            rubric="ecommerce-default",
            top_k=10,
        )
        llm_client = Mock(spec=LLMClient)
        llm_client.complete.return_value = LLMResponse(
            content="SCORE: 2\nATTRIBUTES: n/a\nREASONING: Good match",
            model="test",
            input_tokens=10,
            output_tokens=10,
        )
        backend = FileBackend(output_dir=str(tmp_path))
        rubric = ("system", lambda q, r: f"Query: {q}")

        judgments, checks, _ = run_evaluation(
            queries,
            adapter,
            config,
            llm_client,
            rubric,
            backend,
            skip_llm_on_fail=False,
        )

        assert any(c.check_name == "duplicate" and not c.passed for c in checks)
        assert llm_client.complete.call_count == 2
        assert all(not j.metadata.get("skipped") for j in judgments)
