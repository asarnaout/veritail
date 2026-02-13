"""Tests for the CLI interface."""

from __future__ import annotations

from click.testing import CliRunner

from veritail.cli import main


class TestCLI:
    def test_help(self):
        runner = CliRunner()
        result = runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "veritail" in result.output

    def test_run_help(self):
        runner = CliRunner()
        result = runner.invoke(main, ["run", "--help"])
        assert result.exit_code == 0
        assert "--queries" in result.output
        assert "--adapter" in result.output
        assert "--config-name" in result.output
        assert "--vertical" in result.output

    def test_run_mismatched_adapters_and_configs(self, tmp_path):
        queries_file = tmp_path / "queries.csv"
        queries_file.write_text("query\nshoes\n")
        adapter_file = tmp_path / "adapter.py"
        adapter_file.write_text("def search(q): return []\n")

        runner = CliRunner()
        result = runner.invoke(main, [
            "run",
            "--queries", str(queries_file),
            "--adapter", str(adapter_file),
            "--config-name", "a",
            "--config-name", "b",
        ])
        assert result.exit_code != 0
        assert "matching --config-name" in result.output

    def test_run_single_config_with_file_backend(self, tmp_path, monkeypatch):
        queries_file = tmp_path / "queries.csv"
        queries_file.write_text("query\nshoes\n")

        adapter_file = tmp_path / "adapter.py"
        adapter_file.write_text(
            "from veritail.types import SearchResult\n"
            "def search(q):\n"
            "    return [SearchResult(product_id='SKU-1', title='Shoe', description='A shoe',\n"
            "                        category='Shoes', price=50.0, position=0)]\n"
        )

        # Mock the LLM client to avoid needing real API keys
        from unittest.mock import Mock, patch
        from veritail.llm.client import LLMClient, LLMResponse

        mock_client = Mock(spec=LLMClient)
        mock_client.complete.return_value = LLMResponse(
            content="SCORE: 2\nREASONING: Good match",
            model="test-model",
            input_tokens=100,
            output_tokens=50,
        )

        with patch("veritail.cli.create_llm_client", return_value=mock_client):
            runner = CliRunner()
            result = runner.invoke(main, [
                "run",
                "--queries", str(queries_file),
                "--adapter", str(adapter_file),
                "--config-name", "test",
                "--backend", "file",
                "--output-dir", str(tmp_path / "results"),
                "--llm-model", "test-model",
            ])

        assert result.exit_code == 0
        assert "ndcg" in result.output.lower() or "Evaluating" in result.output

    def test_version(self):
        runner = CliRunner()
        result = runner.invoke(main, ["--version"])
        assert result.exit_code == 0
        assert "0.1.0" in result.output
