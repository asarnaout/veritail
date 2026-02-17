"""Tests for LLM-powered query generation."""

from __future__ import annotations

import json
from unittest.mock import Mock, patch

from click.testing import CliRunner

from veritail.cli import main
from veritail.llm.client import LLMClient, LLMResponse
from veritail.querygen import (
    QUERY_TYPES,
    _compute_distribution,
    _parse_response,
    _write_csv,
    generate_queries,
)

# ---------------------------------------------------------------------------
# TestComputeDistribution
# ---------------------------------------------------------------------------


class TestComputeDistribution:
    def test_sum_equals_count_for_various_values(self):
        for count in [1, 5, 25, 100]:
            dist = _compute_distribution(count)
            assert sum(dist.values()) == count, f"Failed for count={count}"

    def test_all_five_types_present(self):
        dist = _compute_distribution(25)
        assert set(dist.keys()) == set(QUERY_TYPES)

    def test_all_counts_positive_for_reasonable_inputs(self):
        dist = _compute_distribution(25)
        for qtype, n in dist.items():
            assert n >= 1, f"{qtype} has count {n}"

    def test_broad_and_long_tail_are_largest(self):
        dist = _compute_distribution(25)
        for qtype in QUERY_TYPES:
            if qtype not in ("broad", "long_tail"):
                assert dist["broad"] >= dist[qtype]
                assert dist["long_tail"] >= dist[qtype]

    def test_distribution_for_25(self):
        dist = _compute_distribution(25)
        # broad=7, long_tail=7, attribute=5, navigational=3, edge_case=3
        # (may vary slightly by remainder allocation, but sum must be 25)
        assert dist["broad"] + dist["long_tail"] >= dist["attribute"]
        assert sum(dist.values()) == 25


# ---------------------------------------------------------------------------
# TestParseResponse
# ---------------------------------------------------------------------------


class TestParseResponse:
    def test_clean_json(self):
        raw = json.dumps(
            [
                {"query": "shoes", "type": "broad", "category": "Footwear"},
                {"query": "nike", "type": "navigational", "category": "Shoes"},
            ]
        )
        result = _parse_response(raw)
        assert len(result) == 2
        assert result[0]["query"] == "shoes"
        assert result[1]["type"] == "navigational"

    def test_markdown_fences(self):
        raw = '```json\n[{"query": "test", "type": "broad", "category": "X"}]\n```'
        result = _parse_response(raw)
        assert len(result) == 1
        assert result[0]["query"] == "test"

    def test_surrounding_text(self):
        raw = (
            "Here are the queries:\n"
            '[{"query": "laptop", "type": "broad", "category": "Electronics"}]\n'
            "Hope that helps!"
        )
        result = _parse_response(raw)
        assert len(result) == 1
        assert result[0]["query"] == "laptop"

    def test_missing_type_defaults_to_broad(self):
        raw = json.dumps([{"query": "shoes", "category": "Footwear"}])
        result = _parse_response(raw)
        assert result[0]["type"] == "broad"

    def test_missing_category_defaults_to_empty(self):
        raw = json.dumps([{"query": "shoes", "type": "broad"}])
        result = _parse_response(raw)
        assert result[0]["category"] == ""

    def test_empty_queries_skipped(self):
        raw = json.dumps(
            [
                {"query": "", "type": "broad", "category": "X"},
                {"query": "shoes", "type": "broad", "category": "Y"},
            ]
        )
        result = _parse_response(raw)
        assert len(result) == 1
        assert result[0]["query"] == "shoes"

    def test_missing_query_key_skipped(self):
        raw = json.dumps(
            [
                {"type": "broad", "category": "X"},
                {"query": "shoes", "type": "broad", "category": "Y"},
            ]
        )
        result = _parse_response(raw)
        assert len(result) == 1

    def test_not_a_list_raises(self):
        import pytest

        with pytest.raises(ValueError, match="Could not parse"):
            _parse_response('{"query": "shoes"}')

    def test_no_json_raises(self):
        import pytest

        with pytest.raises(ValueError, match="Could not parse"):
            _parse_response("no json here at all")

    def test_empty_array_raises(self):
        import pytest

        with pytest.raises(ValueError, match="No valid queries"):
            _parse_response("[]")

    def test_non_dict_items_skipped(self):
        import pytest

        raw = json.dumps(["shoes", "boots"])
        with pytest.raises(ValueError, match="No valid queries"):
            _parse_response(raw)


# ---------------------------------------------------------------------------
# TestWriteCsv
# ---------------------------------------------------------------------------


class TestWriteCsv:
    def test_writes_valid_csv_with_source_column(self, tmp_path):
        queries = [
            {"query": "shoes", "type": "broad", "category": "Footwear"},
            {"query": "nike", "type": "navigational", "category": "Shoes"},
        ]
        out = tmp_path / "queries.csv"
        _write_csv(queries, out)

        text = out.read_text(encoding="utf-8")
        assert "query,type,category,source" in text
        assert "generated" in text

        lines = text.strip().splitlines()
        assert len(lines) == 3  # header + 2 rows

    def test_compatible_with_load_queries(self, tmp_path):
        """Round-trip: generated CSV can be loaded by load_queries()."""
        from veritail.queries import load_queries

        queries = [
            {"query": "running shoes", "type": "broad", "category": "Shoes"},
        ]
        out = tmp_path / "queries.csv"
        _write_csv(queries, out)

        loaded = load_queries(str(out))
        assert len(loaded) == 1
        assert loaded[0].query == "running shoes"
        assert loaded[0].type == "broad"
        assert loaded[0].category == "Shoes"

    def test_creates_parent_directories(self, tmp_path):
        out = tmp_path / "sub" / "dir" / "queries.csv"
        _write_csv([{"query": "test", "type": "broad", "category": ""}], out)
        assert out.exists()


# ---------------------------------------------------------------------------
# TestGenerateQueries
# ---------------------------------------------------------------------------


class TestGenerateQueries:
    def _make_mock_client(self, response_json: list[dict[str, str]]) -> Mock:
        mock = Mock(spec=LLMClient)
        mock.complete.return_value = LLMResponse(
            content=json.dumps(response_json),
            model="test-model",
            input_tokens=500,
            output_tokens=200,
        )
        return mock

    def test_end_to_end_with_mocked_client(self, tmp_path):
        fake_queries = [
            {"query": "laptop", "type": "broad", "category": "Electronics"},
            {"query": "Dell XPS", "type": "navigational", "category": "Laptops"},
        ]
        client = self._make_mock_client(fake_queries)
        out = tmp_path / "queries.csv"

        result = generate_queries(
            llm_client=client,
            output_path=out,
            count=10,
            vertical="electronics",
        )

        assert len(result) == 2
        assert out.exists()
        client.complete.assert_called_once()

    def test_requires_vertical_or_context(self, tmp_path):
        import pytest

        client = self._make_mock_client([])
        out = tmp_path / "queries.csv"

        with pytest.raises(ValueError, match="At least one"):
            generate_queries(
                llm_client=client,
                output_path=out,
                count=10,
            )

    def test_accepts_context_only(self, tmp_path):
        fake_queries = [
            {"query": "widgets", "type": "broad", "category": "Widgets"},
        ]
        client = self._make_mock_client(fake_queries)
        out = tmp_path / "queries.csv"

        result = generate_queries(
            llm_client=client,
            output_path=out,
            count=5,
            context="We sell industrial widgets for manufacturing.",
        )

        assert len(result) == 1

    def test_accepts_vertical_only(self, tmp_path):
        fake_queries = [
            {"query": "earbuds", "type": "broad", "category": "Audio"},
        ]
        client = self._make_mock_client(fake_queries)
        out = tmp_path / "queries.csv"

        result = generate_queries(
            llm_client=client,
            output_path=out,
            count=5,
            vertical="electronics",
        )

        assert len(result) == 1

    def test_context_file_reading(self, tmp_path):
        ctx_file = tmp_path / "context.txt"
        ctx_file.write_text("B2B HVAC distributor", encoding="utf-8")

        fake_queries = [
            {"query": "hvac filter", "type": "broad", "category": "HVAC"},
        ]
        client = self._make_mock_client(fake_queries)
        out = tmp_path / "queries.csv"

        generate_queries(
            llm_client=client,
            output_path=out,
            count=5,
            context=str(ctx_file),
            vertical="electronics",
        )

        # The user prompt should contain the file content, not the path
        call_args = client.complete.call_args
        user_prompt = call_args.args[1]
        assert "B2B HVAC distributor" in user_prompt
        assert str(ctx_file) not in user_prompt

    def test_distribution_appears_in_user_prompt(self, tmp_path):
        fake_queries = [
            {"query": "test", "type": "broad", "category": "X"},
        ]
        client = self._make_mock_client(fake_queries)
        out = tmp_path / "queries.csv"

        generate_queries(
            llm_client=client,
            output_path=out,
            count=25,
            vertical="electronics",
        )

        user_prompt = client.complete.call_args.args[1]
        for qtype in QUERY_TYPES:
            assert qtype in user_prompt

    def test_max_tokens_passed_to_client(self, tmp_path):
        fake_queries = [
            {"query": "test", "type": "broad", "category": "X"},
        ]
        client = self._make_mock_client(fake_queries)
        out = tmp_path / "queries.csv"

        generate_queries(
            llm_client=client,
            output_path=out,
            count=5,
            vertical="electronics",
        )

        call_kwargs = client.complete.call_args.kwargs
        assert call_kwargs["max_tokens"] == 4096


# ---------------------------------------------------------------------------
# TestGenerateQueriesCLI
# ---------------------------------------------------------------------------


class TestGenerateQueriesCLI:
    def _make_mock_client(self) -> Mock:
        mock = Mock(spec=LLMClient)
        mock.complete.return_value = LLMResponse(
            content=json.dumps(
                [
                    {"query": "laptop", "type": "broad", "category": "Electronics"},
                    {
                        "query": "Dell XPS",
                        "type": "navigational",
                        "category": "Laptops",
                    },
                ]
            ),
            model="test-model",
            input_tokens=500,
            output_tokens=200,
        )
        return mock

    def test_basic_invocation(self, tmp_path):
        mock_client = self._make_mock_client()
        out = tmp_path / "queries.csv"

        with patch("veritail.cli.create_llm_client", return_value=mock_client):
            runner = CliRunner()
            result = runner.invoke(
                main,
                [
                    "generate-queries",
                    "--output",
                    str(out),
                    "--vertical",
                    "electronics",
                    "--llm-model",
                    "test-model",
                ],
            )

        assert result.exit_code == 0
        assert "Generated 2 queries" in result.output
        assert out.exists()

    def test_rejects_missing_vertical_and_context(self, tmp_path):
        out = tmp_path / "queries.csv"
        runner = CliRunner()
        result = runner.invoke(
            main,
            [
                "generate-queries",
                "--output",
                str(out),
                "--llm-model",
                "test-model",
            ],
        )
        assert result.exit_code != 0
        assert "At least one" in result.output

    def test_rejects_count_less_than_one(self, tmp_path):
        out = tmp_path / "queries.csv"
        runner = CliRunner()
        result = runner.invoke(
            main,
            [
                "generate-queries",
                "--output",
                str(out),
                "--vertical",
                "electronics",
                "--llm-model",
                "test-model",
                "--count",
                "0",
            ],
        )
        assert result.exit_code != 0
        assert "--count must be >= 1" in result.output

    def test_rejects_non_csv_output(self, tmp_path):
        out = tmp_path / "queries.json"
        runner = CliRunner()
        result = runner.invoke(
            main,
            [
                "generate-queries",
                "--output",
                str(out),
                "--vertical",
                "electronics",
                "--llm-model",
                "test-model",
            ],
        )
        assert result.exit_code != 0
        assert ".csv" in result.output

    def test_shows_next_step_hint(self, tmp_path):
        mock_client = self._make_mock_client()
        out = tmp_path / "queries.csv"

        with patch("veritail.cli.create_llm_client", return_value=mock_client):
            runner = CliRunner()
            result = runner.invoke(
                main,
                [
                    "generate-queries",
                    "--output",
                    str(out),
                    "--vertical",
                    "electronics",
                    "--llm-model",
                    "test-model",
                ],
            )

        assert result.exit_code == 0
        assert "veritail run" in result.output
        assert "--adapter" in result.output

    def test_preflight_failure_aborts(self, tmp_path):
        mock_client = Mock(spec=LLMClient)
        mock_client.preflight_check.side_effect = RuntimeError("API key is invalid.")
        out = tmp_path / "queries.csv"

        with patch("veritail.cli.create_llm_client", return_value=mock_client):
            runner = CliRunner()
            result = runner.invoke(
                main,
                [
                    "generate-queries",
                    "--output",
                    str(out),
                    "--vertical",
                    "electronics",
                    "--llm-model",
                    "test-model",
                ],
            )

        assert result.exit_code != 0
        assert "API key is invalid" in result.output

    def test_custom_count_and_context_string(self, tmp_path):
        mock_client = self._make_mock_client()
        out = tmp_path / "queries.csv"

        with patch("veritail.cli.create_llm_client", return_value=mock_client):
            runner = CliRunner()
            result = runner.invoke(
                main,
                [
                    "generate-queries",
                    "--output",
                    str(out),
                    "--context",
                    "B2B industrial supplier",
                    "--llm-model",
                    "test-model",
                    "--count",
                    "10",
                ],
            )

        assert result.exit_code == 0
        assert "Generated 2 queries" in result.output

    def test_requires_llm_model(self, tmp_path):
        out = tmp_path / "queries.csv"
        runner = CliRunner()
        result = runner.invoke(
            main,
            [
                "generate-queries",
                "--output",
                str(out),
                "--vertical",
                "electronics",
            ],
        )
        assert result.exit_code != 0
        assert "Missing option '--llm-model'" in result.output

    def test_help(self):
        runner = CliRunner()
        result = runner.invoke(main, ["generate-queries", "--help"])
        assert result.exit_code == 0
        assert "--output" in result.output
        assert "--vertical" in result.output
        assert "--context" in result.output
        assert "--count" in result.output
