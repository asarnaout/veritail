"""Tests for autocomplete pipeline orchestrators."""

from __future__ import annotations

from unittest.mock import Mock

import pytest

from veritail.autocomplete.pipeline import (
    AC_CHECKPOINT_FILENAME,
    run_autocomplete_batch_llm_evaluation,
    run_autocomplete_evaluation,
    run_autocomplete_llm_evaluation,
    run_dual_autocomplete_evaluation,
)
from veritail.checkpoint import BatchCheckpoint, load_checkpoint, save_checkpoint
from veritail.llm.client import BatchRequest, BatchResult, LLMClient, LLMResponse
from veritail.types import (
    AutocompleteConfig,
    AutocompleteResponse,
    PrefixEntry,
    SuggestionJudgment,
)


def _make_adapter(suggestions_map: dict[str, list[str]]):
    """Create a mock suggest adapter from a prefix->suggestions mapping."""

    def adapter(prefix: str) -> AutocompleteResponse:
        return AutocompleteResponse(suggestions=suggestions_map.get(prefix, []))

    return adapter


class TestRunAutocompleteEvaluation:
    def test_happy_path(self) -> None:
        prefixes = [
            PrefixEntry(prefix="run"),
            PrefixEntry(prefix="nik"),
        ]
        adapter = _make_adapter(
            {"run": ["running shoes", "runner"], "nik": ["nike", "nikon"]}
        )
        config = AutocompleteConfig(name="test", adapter_path="test.py")

        checks, responses = run_autocomplete_evaluation(prefixes, adapter, config)
        assert len(responses) == 2
        assert len(checks) > 0

    def test_adapter_error_resilience(self) -> None:
        prefixes = [
            PrefixEntry(prefix="run"),
        ]

        def failing_adapter(prefix: str) -> AutocompleteResponse:
            raise RuntimeError("API down")

        config = AutocompleteConfig(name="test", adapter_path="test.py")
        checks, responses = run_autocomplete_evaluation(
            prefixes, failing_adapter, config
        )
        # Should not raise, should return empty suggestions
        assert 0 in responses
        assert responses[0].suggestions == []

    def test_top_k_trimming(self) -> None:
        prefixes = [PrefixEntry(prefix="a")]
        adapter = _make_adapter({"a": ["a1", "a2", "a3", "a4", "a5", "a6"]})
        config = AutocompleteConfig(name="test", adapter_path="test.py", top_k=3)
        _, responses = run_autocomplete_evaluation(prefixes, adapter, config)
        assert len(responses[0].suggestions) == 3


class TestRunDualAutocompleteEvaluation:
    def test_dual_eval(self) -> None:
        prefixes = [
            PrefixEntry(prefix="run"),
        ]
        adapter_a = _make_adapter({"run": ["running shoes", "runner"]})
        adapter_b = _make_adapter({"run": ["run fast", "running shoes"]})
        config_a = AutocompleteConfig(name="a", adapter_path="a.py")
        config_b = AutocompleteConfig(name="b", adapter_path="b.py")

        checks_a, checks_b, comparison_checks = run_dual_autocomplete_evaluation(
            prefixes, adapter_a, config_a, adapter_b, config_b
        )
        assert len(checks_a) > 0
        assert len(checks_b) > 0
        assert len(comparison_checks) > 0

        # Should have both overlap and rank agreement checks
        check_names = {c.check_name for c in comparison_checks}
        assert "suggestion_overlap" in check_names
        assert "rank_agreement" in check_names


class TestRunAutocompleteLlmEvaluation:
    def test_happy_path(self) -> None:
        prefixes = [
            PrefixEntry(prefix="run"),
            PrefixEntry(prefix="nik"),
        ]
        responses = {
            0: AutocompleteResponse(suggestions=["running shoes", "runner"]),
            1: AutocompleteResponse(suggestions=["nike", "nikon"]),
        }
        config = AutocompleteConfig(name="test", adapter_path="test.py")

        mock_judge = Mock()
        mock_judge.judge.return_value = SuggestionJudgment(
            prefix="run",
            suggestions=["running shoes", "runner"],
            relevance_score=3,
            diversity_score=2,
            flagged_suggestions=[],
            reasoning="Good suggestions.",
            model="test-model",
            experiment="test",
        )

        judgments = run_autocomplete_llm_evaluation(
            prefixes, responses, mock_judge, config
        )
        assert len(judgments) == 2
        assert mock_judge.judge.call_count == 2

    def test_skips_empty_suggestions(self) -> None:
        prefixes = [
            PrefixEntry(prefix="run"),
            PrefixEntry(prefix="xyz"),
        ]
        responses = {
            0: AutocompleteResponse(suggestions=["running shoes"]),
            1: AutocompleteResponse(suggestions=[]),
        }
        config = AutocompleteConfig(name="test", adapter_path="test.py")

        mock_judge = Mock()
        mock_judge.judge.return_value = SuggestionJudgment(
            prefix="run",
            suggestions=["running shoes"],
            relevance_score=3,
            diversity_score=2,
            flagged_suggestions=[],
            reasoning="Good.",
            model="test-model",
            experiment="test",
        )

        judgments = run_autocomplete_llm_evaluation(
            prefixes, responses, mock_judge, config
        )
        assert len(judgments) == 1
        assert mock_judge.judge.call_count == 1

    def test_error_resilience(self) -> None:
        prefixes = [PrefixEntry(prefix="run")]
        responses = {
            0: AutocompleteResponse(suggestions=["running shoes"]),
        }
        config = AutocompleteConfig(name="test", adapter_path="test.py")

        mock_judge = Mock()
        mock_judge.judge.side_effect = ValueError("LLM parse error")

        judgments = run_autocomplete_llm_evaluation(
            prefixes, responses, mock_judge, config
        )
        assert len(judgments) == 1
        assert judgments[0].relevance_score == 0
        assert judgments[0].diversity_score == 0
        assert "error" in judgments[0].metadata


def _make_batch_judge() -> Mock:
    """Create a mock SuggestionJudge with batch methods."""
    judge = Mock()
    judge.prepare_request.side_effect = lambda cid, prefix, sug: BatchRequest(
        custom_id=cid,
        system_prompt="system",
        user_prompt=f"Prefix: {prefix}\nSuggestions: {sug}",
    )
    judge.parse_batch_result.side_effect = lambda resp, prefix, sug: SuggestionJudgment(
        prefix=prefix,
        suggestions=sug,
        relevance_score=3,
        diversity_score=2,
        flagged_suggestions=[],
        reasoning="Good suggestions.",
        model=resp.model,
        experiment="test",
    )
    return judge


def _make_batch_client(
    results: list[BatchResult] | None = None,
    poll_status: str = "completed",
) -> Mock:
    """Create a mock LLMClient with batch support."""
    client = Mock(spec=LLMClient)
    client.supports_batch.return_value = True
    client.submit_batch.return_value = "batch-ac-1"
    client.poll_batch.return_value = (poll_status, 2, 2)
    client.batch_error_message.return_value = None
    if results is not None:
        client.retrieve_batch_results.return_value = results
    return client


class TestRunAutocompleteBatchLlmEvaluation:
    def test_batch_happy_path(self, tmp_path) -> None:
        prefixes = [
            PrefixEntry(prefix="run"),
            PrefixEntry(prefix="nik"),
        ]
        responses = {
            0: AutocompleteResponse(suggestions=["running shoes", "runner"]),
            1: AutocompleteResponse(suggestions=["nike", "nikon"]),
        }
        config = AutocompleteConfig(name="test", adapter_path="test.py")
        judge = _make_batch_judge()
        results = [
            BatchResult(
                custom_id="ac-0",
                response=LLMResponse(
                    content="RELEVANCE: 3\nDIVERSITY: 2\nFLAGGED: none\n"
                    "REASONING: Good.",
                    model="test-model",
                    input_tokens=10,
                    output_tokens=10,
                ),
            ),
            BatchResult(
                custom_id="ac-1",
                response=LLMResponse(
                    content="RELEVANCE: 2\nDIVERSITY: 1\nFLAGGED: none\nREASONING: OK.",
                    model="test-model",
                    input_tokens=10,
                    output_tokens=10,
                ),
            ),
        ]
        client = _make_batch_client(results=results)

        judgments = run_autocomplete_batch_llm_evaluation(
            prefixes,
            responses,
            judge,
            config,
            client,
            poll_interval=0,
            output_dir=str(tmp_path),
        )

        assert len(judgments) == 2
        client.submit_batch.assert_called_once()
        assert judge.prepare_request.call_count == 2

    def test_batch_skips_empty_suggestions(self, tmp_path) -> None:
        prefixes = [
            PrefixEntry(prefix="run"),
            PrefixEntry(prefix="xyz"),
        ]
        responses = {
            0: AutocompleteResponse(suggestions=["running shoes"]),
            1: AutocompleteResponse(suggestions=[]),
        }
        config = AutocompleteConfig(name="test", adapter_path="test.py")
        judge = _make_batch_judge()
        results = [
            BatchResult(
                custom_id="ac-0",
                response=LLMResponse(
                    content="ok",
                    model="test-model",
                    input_tokens=10,
                    output_tokens=10,
                ),
            ),
        ]
        client = _make_batch_client(results=results)
        client.poll_batch.return_value = ("completed", 1, 1)

        judgments = run_autocomplete_batch_llm_evaluation(
            prefixes,
            responses,
            judge,
            config,
            client,
            poll_interval=0,
            output_dir=str(tmp_path),
        )

        assert len(judgments) == 1
        # Only 1 request submitted (empty prefix skipped)
        submitted_reqs = client.submit_batch.call_args[0][0]
        assert len(submitted_reqs) == 1

    def test_batch_zero_requests(self, tmp_path) -> None:
        prefixes = [PrefixEntry(prefix="xyz")]
        responses = {0: AutocompleteResponse(suggestions=[])}
        config = AutocompleteConfig(name="test", adapter_path="test.py")
        judge = _make_batch_judge()
        client = _make_batch_client()

        judgments = run_autocomplete_batch_llm_evaluation(
            prefixes,
            responses,
            judge,
            config,
            client,
            poll_interval=0,
            output_dir=str(tmp_path),
        )

        assert judgments == []
        client.submit_batch.assert_not_called()

    def test_batch_partial_failures(self, tmp_path) -> None:
        prefixes = [
            PrefixEntry(prefix="run"),
            PrefixEntry(prefix="nik"),
        ]
        responses = {
            0: AutocompleteResponse(suggestions=["running shoes"]),
            1: AutocompleteResponse(suggestions=["nike"]),
        }
        config = AutocompleteConfig(name="test", adapter_path="test.py")
        judge = _make_batch_judge()
        results = [
            BatchResult(
                custom_id="ac-0",
                response=LLMResponse(
                    content="ok",
                    model="test-model",
                    input_tokens=10,
                    output_tokens=10,
                ),
            ),
            BatchResult(
                custom_id="ac-1",
                response=None,
                error="Rate limit exceeded",
            ),
        ]
        client = _make_batch_client(results=results)

        judgments = run_autocomplete_batch_llm_evaluation(
            prefixes,
            responses,
            judge,
            config,
            client,
            poll_interval=0,
            output_dir=str(tmp_path),
        )

        assert len(judgments) == 2
        # Second judgment should be error with score=0
        assert judgments[1].relevance_score == 0
        assert judgments[1].diversity_score == 0
        assert "Rate limit" in judgments[1].reasoning

    def test_batch_parse_error(self, tmp_path) -> None:
        prefixes = [PrefixEntry(prefix="run")]
        responses = {0: AutocompleteResponse(suggestions=["running shoes"])}
        config = AutocompleteConfig(name="test", adapter_path="test.py")
        judge = _make_batch_judge()
        judge.parse_batch_result.side_effect = ValueError("Cannot parse")
        results = [
            BatchResult(
                custom_id="ac-0",
                response=LLMResponse(
                    content="bad response",
                    model="test-model",
                    input_tokens=10,
                    output_tokens=10,
                ),
            ),
        ]
        client = _make_batch_client(results=results)
        client.poll_batch.return_value = ("completed", 1, 1)

        judgments = run_autocomplete_batch_llm_evaluation(
            prefixes,
            responses,
            judge,
            config,
            client,
            poll_interval=0,
            output_dir=str(tmp_path),
        )

        assert len(judgments) == 1
        assert judgments[0].relevance_score == 0
        assert "error" in judgments[0].metadata

    def test_batch_poll_failure(self, tmp_path) -> None:
        prefixes = [PrefixEntry(prefix="run")]
        responses = {0: AutocompleteResponse(suggestions=["running shoes"])}
        config = AutocompleteConfig(name="test", adapter_path="test.py")
        judge = _make_batch_judge()
        client = _make_batch_client(poll_status="failed")

        with pytest.raises(RuntimeError, match="batch-ac-1 failed"):
            run_autocomplete_batch_llm_evaluation(
                prefixes,
                responses,
                judge,
                config,
                client,
                poll_interval=0,
                output_dir=str(tmp_path),
            )

        # Checkpoint should be cleared
        assert (
            load_checkpoint(str(tmp_path), "test", filename=AC_CHECKPOINT_FILENAME)
            is None
        )

    def test_batch_results_match_sync(self, tmp_path) -> None:
        """Same LLM content through both paths → identical scores."""
        prefixes = [PrefixEntry(prefix="run")]
        responses = {0: AutocompleteResponse(suggestions=["running shoes", "runner"])}
        config = AutocompleteConfig(name="test", adapter_path="test.py")

        # Sync path
        sync_judge = Mock()
        sync_judgment = SuggestionJudgment(
            prefix="run",
            suggestions=["running shoes", "runner"],
            relevance_score=3,
            diversity_score=2,
            flagged_suggestions=[],
            reasoning="Good.",
            model="test-model",
            experiment="test",
        )
        sync_judge.judge.return_value = sync_judgment

        sync_results = run_autocomplete_llm_evaluation(
            prefixes, responses, sync_judge, config
        )

        # Batch path
        batch_judge = _make_batch_judge()
        llm_resp = LLMResponse(
            content="ok", model="test-model", input_tokens=10, output_tokens=10
        )
        batch_result_list = [
            BatchResult(custom_id="ac-0", response=llm_resp),
        ]
        client = _make_batch_client(results=batch_result_list)
        client.poll_batch.return_value = ("completed", 1, 1)

        batch_results = run_autocomplete_batch_llm_evaluation(
            prefixes,
            responses,
            batch_judge,
            config,
            client,
            poll_interval=0,
            output_dir=str(tmp_path),
        )

        assert len(sync_results) == len(batch_results) == 1
        assert sync_results[0].relevance_score == batch_results[0].relevance_score
        assert sync_results[0].diversity_score == batch_results[0].diversity_score

    def test_batch_checkpoint_lifecycle(self, tmp_path) -> None:
        prefixes = [PrefixEntry(prefix="run")]
        responses = {0: AutocompleteResponse(suggestions=["running shoes"])}
        config = AutocompleteConfig(name="test", adapter_path="test.py")
        judge = _make_batch_judge()

        results = [
            BatchResult(
                custom_id="ac-0",
                response=LLMResponse(
                    content="ok",
                    model="test-model",
                    input_tokens=10,
                    output_tokens=10,
                ),
            ),
        ]
        client = _make_batch_client(results=results)
        client.poll_batch.return_value = ("completed", 1, 1)

        run_autocomplete_batch_llm_evaluation(
            prefixes,
            responses,
            judge,
            config,
            client,
            poll_interval=0,
            output_dir=str(tmp_path),
        )

        # After success, checkpoint should be cleared
        assert (
            load_checkpoint(str(tmp_path), "test", filename=AC_CHECKPOINT_FILENAME)
            is None
        )

    def test_batch_resume_skips_submit(self, tmp_path) -> None:
        prefixes = [PrefixEntry(prefix="run")]
        responses = {0: AutocompleteResponse(suggestions=["running shoes"])}
        config = AutocompleteConfig(name="test", adapter_path="test.py")
        judge = _make_batch_judge()

        # Pre-save checkpoint
        save_checkpoint(
            str(tmp_path),
            "test",
            BatchCheckpoint(
                batch_id="batch-ac-resume",
                experiment_name="test",
                phase="autocomplete",
                request_context={
                    "ac-0": {
                        "prefix": "run",
                        "suggestions": ["running shoes"],
                        "prefix_index": 0,
                    }
                },
                checks=[],
                correction_entries=[],
            ),
            filename=AC_CHECKPOINT_FILENAME,
        )

        results = [
            BatchResult(
                custom_id="ac-0",
                response=LLMResponse(
                    content="ok",
                    model="test-model",
                    input_tokens=10,
                    output_tokens=10,
                ),
            ),
        ]
        client = _make_batch_client(results=results)
        client.poll_batch.return_value = ("completed", 1, 1)

        judgments = run_autocomplete_batch_llm_evaluation(
            prefixes,
            responses,
            judge,
            config,
            client,
            poll_interval=0,
            resume=True,
            output_dir=str(tmp_path),
        )

        assert len(judgments) == 1
        # submit_batch should NOT have been called (resumed from checkpoint)
        client.submit_batch.assert_not_called()
        # poll_batch should still be called
        client.poll_batch.assert_called_with("batch-ac-resume")
