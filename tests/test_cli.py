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

    def test_run_dual_config_with_only_one_name_fails(self, tmp_path):
        queries_file = tmp_path / "queries.csv"
        queries_file.write_text("query\nshoes\n")

        adapter_a = tmp_path / "adapter_a.py"
        adapter_a.write_text("def search(q): return []\n")
        adapter_b = tmp_path / "adapter_b.py"
        adapter_b.write_text("def search(q): return []\n")

        runner = CliRunner()
        result = runner.invoke(main, [
            "run",
            "--queries", str(queries_file),
            "--adapter", str(adapter_a),
            "--adapter", str(adapter_b),
            "--config-name", "only-one-name",
        ])
        assert result.exit_code != 0
        assert "matching --config-name" in result.output

    def test_run_rejects_top_k_less_than_one(self, tmp_path):
        queries_file = tmp_path / "queries.csv"
        queries_file.write_text("query\nshoes\n")

        adapter_file = tmp_path / "adapter.py"
        adapter_file.write_text("def search(q): return []\n")

        runner = CliRunner()
        result = runner.invoke(main, [
            "run",
            "--queries", str(queries_file),
            "--adapter", str(adapter_file),
            "--top-k", "0",
        ])
        assert result.exit_code != 0
        assert "--top-k must be >= 1." in result.output

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

    def test_run_single_config_auto_generates_config_name(self, tmp_path):
        queries_file = tmp_path / "queries.csv"
        queries_file.write_text("query\nshoes\n")

        adapter_file = tmp_path / "my_adapter.py"
        adapter_file.write_text(
            "from veritail.types import SearchResult\n"
            "def search(q):\n"
            "    return [SearchResult(product_id='SKU-1', title='Shoe', description='A shoe',\n"
            "                        category='Shoes', price=50.0, position=0)]\n"
        )

        from unittest.mock import Mock, patch
        from veritail.llm.client import LLMClient, LLMResponse

        mock_client = Mock(spec=LLMClient)
        mock_client.complete.return_value = LLMResponse(
            content="SCORE: 2\nREASONING: Good match",
            model="test-model",
            input_tokens=100,
            output_tokens=50,
        )

        output_dir = tmp_path / "results"
        with patch("veritail.cli.create_llm_client", return_value=mock_client):
            runner = CliRunner()
            result = runner.invoke(main, [
                "run",
                "--queries", str(queries_file),
                "--adapter", str(adapter_file),
                "--backend", "file",
                "--output-dir", str(output_dir),
                "--llm-model", "test-model",
            ])

        assert result.exit_code == 0
        assert "No --config-name provided. Using generated names:" in result.output

        experiment_dirs = [p for p in output_dir.iterdir() if p.is_dir()]
        assert len(experiment_dirs) == 1
        assert experiment_dirs[0].name.startswith("my-adapter-")
        assert (experiment_dirs[0] / "metrics.json").exists()
        assert (experiment_dirs[0] / "report.html").exists()

    def test_version(self):
        runner = CliRunner()
        result = runner.invoke(main, ["--version"])
        assert result.exit_code == 0
        assert "0.1.0" in result.output
