"""Tests for the CLI interface."""

from __future__ import annotations

import json

from click.testing import CliRunner

from veritail.cli import main
from veritail.types import MetricResult


class TestDeduplicateConfigName:
    def test_returns_name_unchanged_when_no_conflict(self, tmp_path):
        from veritail.cli import _deduplicate_config_name

        assert _deduplicate_config_name("my-run", str(tmp_path)) == "my-run"

    def test_appends_dot_2_on_first_conflict(self, tmp_path):
        from veritail.cli import _deduplicate_config_name

        (tmp_path / "my-run").mkdir()
        assert _deduplicate_config_name("my-run", str(tmp_path)) == "my-run.2"

    def test_increments_suffix_past_existing(self, tmp_path):
        from veritail.cli import _deduplicate_config_name

        (tmp_path / "my-run").mkdir()
        (tmp_path / "my-run.2").mkdir()
        (tmp_path / "my-run.3").mkdir()
        assert _deduplicate_config_name("my-run", str(tmp_path)) == "my-run.4"

    def test_cli_prints_warning_on_dedup(self, tmp_path):
        """When --config-name collides, CLI warns and uses deduplicated name."""
        queries_file = tmp_path / "queries.csv"
        queries_file.write_text("query\nshoes\n")

        adapter_file = tmp_path / "adapter.py"
        adapter_file.write_text(
            "from veritail.types import SearchResult\n"
            "def search(q):\n"
            "    return [SearchResult(\n"
            "        product_id='SKU-1', title='Shoe',\n"
            "        description='A shoe',\n"
            "        category='Shoes', price=50.0, position=0)]\n"
        )

        output_dir = tmp_path / "results"
        # Pre-create the directory to force a collision
        (output_dir / "my-run").mkdir(parents=True)

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
            result = runner.invoke(
                main,
                [
                    "run",
                    "--queries",
                    str(queries_file),
                    "--adapter",
                    str(adapter_file),
                    "--config-name",
                    "my-run",
                    "--backend",
                    "file",
                    "--output-dir",
                    str(output_dir),
                    "--llm-model",
                    "test-model",
                ],
            )

        assert result.exit_code == 0
        assert "already exists" in result.output
        assert "my-run.2" in result.output
        # Results land in the deduplicated directory
        assert (output_dir / "my-run.2" / "report.html").exists()

    def test_resume_does_not_deduplicate(self, tmp_path):
        """--resume should reuse the existing directory, not create .2."""
        queries_file = tmp_path / "queries.csv"
        queries_file.write_text("query\nshoes\n")

        adapter_file = tmp_path / "adapter.py"
        adapter_file.write_text(
            "from veritail.types import SearchResult\n"
            "def search(q):\n"
            "    return [SearchResult(\n"
            "        product_id='SKU-1', title='Shoe',\n"
            "        description='A shoe',\n"
            "        category='Shoes', price=50.0, position=0)]\n"
        )

        output_dir = tmp_path / "results"
        exp_dir = output_dir / "my-run"
        exp_dir.mkdir(parents=True)
        # Write a matching config so resume validation passes
        (exp_dir / "config.json").write_text(
            json.dumps({"llm_model": "test-model", "top_k": 10}),
            encoding="utf-8",
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

        with patch("veritail.cli.create_llm_client", return_value=mock_client):
            runner = CliRunner()
            result = runner.invoke(
                main,
                [
                    "run",
                    "--queries",
                    str(queries_file),
                    "--adapter",
                    str(adapter_file),
                    "--config-name",
                    "my-run",
                    "--backend",
                    "file",
                    "--output-dir",
                    str(output_dir),
                    "--llm-model",
                    "test-model",
                    "--resume",
                ],
            )

        assert result.exit_code == 0
        # Should NOT have created my-run.2
        assert "already exists" not in result.output
        assert not (output_dir / "my-run.2").exists()


class TestCLI:
    def test_init_creates_starter_files(self, tmp_path):
        runner = CliRunner()
        result = runner.invoke(main, ["init", "--dir", str(tmp_path)])

        assert result.exit_code == 0
        assert "Created" in result.output

        adapter_path = tmp_path / "adapter.py"
        queries_path = tmp_path / "queries.csv"
        prefixes_path = tmp_path / "prefixes.csv"

        assert adapter_path.exists()
        assert queries_path.exists()
        assert prefixes_path.exists()

        adapter_text = adapter_path.read_text(encoding="utf-8")
        assert "def search(query: str) -> SearchResponse:" in adapter_text
        assert "def suggest(prefix: str) -> AutocompleteResponse:" in adapter_text
        assert "urlopen(request, timeout=10)" in adapter_text
        assert "SEARCH_API_URL" in adapter_text

        queries_text = queries_path.read_text(encoding="utf-8")
        assert "running shoes" in queries_text
        assert "nike air max 90" in queries_text

        # No separate suggest_adapter.py
        assert not (tmp_path / "suggest_adapter.py").exists()

    def test_init_refuses_to_overwrite_without_force(self, tmp_path):
        adapter_path = tmp_path / "adapter.py"
        adapter_path.write_text("old adapter\n", encoding="utf-8")

        runner = CliRunner()
        result = runner.invoke(main, ["init", "--dir", str(tmp_path)])

        assert result.exit_code != 0
        assert "Refusing to overwrite existing file(s)" in result.output
        assert "--force" in result.output
        assert adapter_path.read_text(encoding="utf-8") == "old adapter\n"

    def test_init_force_overwrites_existing_files(self, tmp_path):
        adapter_path = tmp_path / "adapter.py"
        queries_path = tmp_path / "queries.csv"
        prefixes_path = tmp_path / "prefixes.csv"
        adapter_path.write_text("old adapter\n", encoding="utf-8")
        queries_path.write_text("old queries\n", encoding="utf-8")
        prefixes_path.write_text("old prefixes\n", encoding="utf-8")

        runner = CliRunner()
        result = runner.invoke(main, ["init", "--dir", str(tmp_path), "--force"])

        assert result.exit_code == 0
        content = adapter_path.read_text(encoding="utf-8")
        assert "Generated by `veritail init`" in content
        assert "running shoes" in queries_path.read_text(encoding="utf-8")
        assert "run" in prefixes_path.read_text(encoding="utf-8")

    def test_init_supports_custom_file_names(self, tmp_path):
        runner = CliRunner()
        result = runner.invoke(
            main,
            [
                "init",
                "--dir",
                str(tmp_path),
                "--adapter-name",
                "my_adapter.py",
                "--queries-name",
                "my_queries.csv",
            ],
        )

        assert result.exit_code == 0
        assert (tmp_path / "my_adapter.py").exists()
        assert (tmp_path / "my_queries.csv").exists()

    def test_init_validates_file_extensions(self, tmp_path):
        runner = CliRunner()
        result = runner.invoke(
            main,
            ["init", "--dir", str(tmp_path), "--adapter-name", "adapter.txt"],
        )

        assert result.exit_code != 0
        assert "--adapter-name must end with .py" in result.output

    def test_help(self):
        runner = CliRunner()
        result = runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "veritail" in result.output

    def test_vertical_list(self):
        runner = CliRunner()
        result = runner.invoke(main, ["vertical", "list"])
        assert result.exit_code == 0
        assert "home-improvement" in result.output
        assert "fashion" in result.output
        assert "electronics" in result.output
        # Verify sorted order
        lines = result.output.strip().splitlines()
        assert lines == sorted(lines)

    def test_vertical_show(self):
        runner = CliRunner()
        result = runner.invoke(main, ["vertical", "show", "fashion"])
        assert result.exit_code == 0
        # Should contain actual vertical content
        assert len(result.output) > 100

    def test_vertical_show_unknown(self):
        runner = CliRunner()
        result = runner.invoke(main, ["vertical", "show", "nonexistent"])
        assert result.exit_code != 0
        assert "Unknown vertical" in result.output

    def test_vertical_show_pipe_to_file(self, tmp_path):
        """Verify output is plain text suitable for shell redirection."""
        runner = CliRunner()
        result = runner.invoke(main, ["vertical", "show", "home-improvement"])
        assert result.exit_code == 0
        # Write to file to simulate: veritail vertical show home-improvement > file.txt
        out_file = tmp_path / "my_vertical.txt"
        out_file.write_text(result.output, encoding="utf-8")
        # The file should be usable as a custom vertical
        assert out_file.read_text(encoding="utf-8") == result.output

    def test_run_context_from_file(self, tmp_path):
        """--context accepts a file path and reads its contents."""
        queries_file = tmp_path / "queries.csv"
        queries_file.write_text("query\nshoes\n")

        adapter_file = tmp_path / "adapter.py"
        adapter_file.write_text(
            "from veritail.types import SearchResult\n"
            "def search(q):\n"
            "    return [SearchResult(\n"
            "        product_id='SKU-1', title='Shoe',\n"
            "        description='A shoe',\n"
            "        category='Shoes', price=50.0, position=0)]\n"
        )

        context_file = tmp_path / "context.txt"
        context_file.write_text(
            "We are a B2B commercial HVAC distributor.\n"
            "HVAC queries require strict part number matching."
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

        with patch("veritail.cli.create_llm_client", return_value=mock_client):
            runner = CliRunner()
            result = runner.invoke(
                main,
                [
                    "run",
                    "--queries",
                    str(queries_file),
                    "--adapter",
                    str(adapter_file),
                    "--config-name",
                    "test",
                    "--backend",
                    "file",
                    "--output-dir",
                    str(tmp_path / "results"),
                    "--llm-model",
                    "test-model",
                    "--context",
                    str(context_file),
                ],
            )

        assert result.exit_code == 0
        # Verify the file contents were passed to the LLM, not the file path
        call_args = mock_client.complete.call_args
        system_prompt = call_args.args[0]
        assert "HVAC" in system_prompt
        assert str(context_file) not in system_prompt

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
        result = runner.invoke(
            main,
            [
                "run",
                "--queries",
                str(queries_file),
                "--adapter",
                str(adapter_file),
                "--llm-model",
                "test-model",
                "--config-name",
                "a",
                "--config-name",
                "b",
            ],
        )
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
        result = runner.invoke(
            main,
            [
                "run",
                "--queries",
                str(queries_file),
                "--adapter",
                str(adapter_a),
                "--adapter",
                str(adapter_b),
                "--llm-model",
                "test-model",
                "--config-name",
                "only-one-name",
            ],
        )
        assert result.exit_code != 0
        assert "matching --config-name" in result.output

    def test_run_rejects_top_k_less_than_one(self, tmp_path):
        queries_file = tmp_path / "queries.csv"
        queries_file.write_text("query\nshoes\n")

        adapter_file = tmp_path / "adapter.py"
        adapter_file.write_text("def search(q): return []\n")

        runner = CliRunner()
        result = runner.invoke(
            main,
            [
                "run",
                "--queries",
                str(queries_file),
                "--adapter",
                str(adapter_file),
                "--llm-model",
                "test-model",
                "--top-k",
                "0",
            ],
        )
        assert result.exit_code != 0
        assert "--top-k must be >= 1." in result.output

    def test_run_single_config_with_file_backend(self, tmp_path, monkeypatch):
        queries_file = tmp_path / "queries.csv"
        queries_file.write_text("query\nshoes\n")

        adapter_file = tmp_path / "adapter.py"
        adapter_file.write_text(
            "from veritail.types import SearchResult\n"
            "def search(q):\n"
            "    return [SearchResult(\n"
            "        product_id='SKU-1', title='Shoe',\n"
            "        description='A shoe',\n"
            "        category='Shoes', price=50.0, position=0)]\n"
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
            result = runner.invoke(
                main,
                [
                    "run",
                    "--queries",
                    str(queries_file),
                    "--adapter",
                    str(adapter_file),
                    "--config-name",
                    "test",
                    "--backend",
                    "file",
                    "--output-dir",
                    str(tmp_path / "results"),
                    "--llm-model",
                    "test-model",
                ],
            )

        assert result.exit_code == 0
        assert "ndcg" in result.output.lower() or "Evaluating" in result.output

    def test_run_single_config_auto_generates_config_name(self, tmp_path):
        queries_file = tmp_path / "queries.csv"
        queries_file.write_text("query\nshoes\n")

        adapter_file = tmp_path / "my_adapter.py"
        adapter_file.write_text(
            "from veritail.types import SearchResult\n"
            "def search(q):\n"
            "    return [SearchResult(\n"
            "        product_id='SKU-1', title='Shoe',\n"
            "        description='A shoe',\n"
            "        category='Shoes', price=50.0, position=0)]\n"
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
            result = runner.invoke(
                main,
                [
                    "run",
                    "--queries",
                    str(queries_file),
                    "--adapter",
                    str(adapter_file),
                    "--backend",
                    "file",
                    "--output-dir",
                    str(output_dir),
                    "--llm-model",
                    "test-model",
                ],
            )

        assert result.exit_code == 0
        assert "No --config-name provided. Using generated names:" in result.output

        experiment_dirs = [p for p in output_dir.iterdir() if p.is_dir()]
        assert len(experiment_dirs) == 1
        assert experiment_dirs[0].name.startswith("my-adapter-")
        assert (experiment_dirs[0] / "metrics.json").exists()
        assert (experiment_dirs[0] / "report.html").exists()

    def test_run_help_shows_llm_base_url_option(self):
        runner = CliRunner()
        result = runner.invoke(main, ["run", "--help"])
        assert result.exit_code == 0
        assert "--llm-base-url" in result.output
        assert "--llm-api-key" in result.output

    def test_generate_queries_help_shows_llm_base_url_option(self):
        runner = CliRunner()
        result = runner.invoke(main, ["generate-queries", "--help"])
        assert result.exit_code == 0
        assert "--llm-base-url" in result.output
        assert "--llm-api-key" in result.output

    def test_run_with_llm_base_url(self, tmp_path):
        """--llm-base-url and --llm-api-key are forwarded to create_llm_client."""
        queries_file = tmp_path / "queries.csv"
        queries_file.write_text("query\nshoes\n")

        adapter_file = tmp_path / "adapter.py"
        adapter_file.write_text(
            "from veritail.types import SearchResult\n"
            "def search(q):\n"
            "    return [SearchResult(\n"
            "        product_id='SKU-1', title='Shoe',\n"
            "        description='A shoe',\n"
            "        category='Shoes', price=50.0, position=0)]\n"
        )

        from unittest.mock import Mock, patch

        from veritail.llm.client import LLMClient, LLMResponse

        mock_client = Mock(spec=LLMClient)
        mock_client.complete.return_value = LLMResponse(
            content="SCORE: 2\nREASONING: Good match",
            model="qwen3:14b",
            input_tokens=100,
            output_tokens=50,
        )

        with patch(
            "veritail.cli.create_llm_client", return_value=mock_client
        ) as mock_create:
            runner = CliRunner()
            result = runner.invoke(
                main,
                [
                    "run",
                    "--queries",
                    str(queries_file),
                    "--adapter",
                    str(adapter_file),
                    "--config-name",
                    "test",
                    "--backend",
                    "file",
                    "--output-dir",
                    str(tmp_path / "results"),
                    "--llm-model",
                    "qwen3:14b",
                    "--llm-base-url",
                    "http://localhost:11434/v1",
                    "--llm-api-key",
                    "not-needed",
                ],
            )

        assert result.exit_code == 0
        mock_create.assert_called_once_with(
            "qwen3:14b",
            base_url="http://localhost:11434/v1",
            api_key="not-needed",
        )

    def test_run_warns_on_unrecognized_model_with_base_url(self, tmp_path):
        queries_file = tmp_path / "queries.csv"
        queries_file.write_text("query\nshoes\n")

        adapter_file = tmp_path / "adapter.py"
        adapter_file.write_text(
            "from veritail.types import SearchResult\n"
            "def search(q):\n"
            "    return [SearchResult(\n"
            "        product_id='SKU-1', title='Shoe',\n"
            "        description='A shoe',\n"
            "        category='Shoes', price=50.0, position=0)]\n"
        )

        from unittest.mock import Mock, patch

        from veritail.llm.client import LLMClient, LLMResponse

        mock_client = Mock(spec=LLMClient)
        mock_client.complete.return_value = LLMResponse(
            content="SCORE: 2\nREASONING: Good match",
            model="llama3.1:8b",
            input_tokens=100,
            output_tokens=50,
        )

        with patch("veritail.cli.create_llm_client", return_value=mock_client):
            runner = CliRunner()
            result = runner.invoke(
                main,
                [
                    "run",
                    "--queries",
                    str(queries_file),
                    "--adapter",
                    str(adapter_file),
                    "--config-name",
                    "test",
                    "--backend",
                    "file",
                    "--output-dir",
                    str(tmp_path / "results"),
                    "--llm-model",
                    "llama3.1:8b",
                    "--llm-base-url",
                    "http://localhost:11434/v1",
                    "--llm-api-key",
                    "ollama",
                ],
            )

        assert result.exit_code == 0
        assert "custom endpoint" in result.output
        assert "70B+" in result.output

    def test_run_help_shows_checks_option(self):
        runner = CliRunner()
        result = runner.invoke(main, ["run", "--help"])
        assert result.exit_code == 0
        assert "--checks" in result.output

    def test_run_with_custom_checks(self, tmp_path):
        queries_file = tmp_path / "queries.csv"
        queries_file.write_text("query\nshoes\n")

        adapter_file = tmp_path / "adapter.py"
        adapter_file.write_text(
            "from veritail.types import SearchResult\n"
            "def search(q):\n"
            "    return [SearchResult(\n"
            "        product_id='SKU-1', title='Shoe',\n"
            "        description='A shoe',\n"
            "        category='Shoes', price=50.0, position=0)]\n"
        )

        check_file = tmp_path / "my_checks.py"
        check_file.write_text(
            "from veritail.types import CheckResult, QueryEntry, SearchResult\n"
            "\n"
            "def check_custom(\n"
            "    query: QueryEntry, results: list[SearchResult]\n"
            ") -> list[CheckResult]:\n"
            "    return [CheckResult(\n"
            "        check_name='custom',\n"
            "        query=query.query,\n"
            "        product_id=None,\n"
            "        passed=True,\n"
            "        detail='ok',\n"
            "    )]\n"
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

        with patch("veritail.cli.create_llm_client", return_value=mock_client):
            runner = CliRunner()
            result = runner.invoke(
                main,
                [
                    "run",
                    "--queries",
                    str(queries_file),
                    "--adapter",
                    str(adapter_file),
                    "--config-name",
                    "test",
                    "--backend",
                    "file",
                    "--output-dir",
                    str(tmp_path / "results"),
                    "--llm-model",
                    "test-model",
                    "--checks",
                    str(check_file),
                ],
            )

        assert result.exit_code == 0
        assert "Loaded 1 custom check(s)" in result.output

    def test_run_help_shows_sample_option(self):
        runner = CliRunner()
        result = runner.invoke(main, ["run", "--help"])
        assert result.exit_code == 0
        assert "--sample" in result.output

    def test_run_rejects_sample_less_than_one(self, tmp_path):
        queries_file = tmp_path / "queries.csv"
        queries_file.write_text("query\nshoes\n")

        adapter_file = tmp_path / "adapter.py"
        adapter_file.write_text("def search(q): return []\n")

        runner = CliRunner()
        result = runner.invoke(
            main,
            [
                "run",
                "--queries",
                str(queries_file),
                "--adapter",
                str(adapter_file),
                "--llm-model",
                "test-model",
                "--sample",
                "0",
            ],
        )
        assert result.exit_code != 0
        assert "--sample must be >= 1" in result.output

    def test_run_sample_selects_subset(self, tmp_path):
        queries_file = tmp_path / "queries.csv"
        queries_file.write_text("query\nshoes\nboots\nsandals\nsneakers\nloafers\n")

        adapter_file = tmp_path / "adapter.py"
        adapter_file.write_text(
            "from veritail.types import SearchResult\n"
            "def search(q):\n"
            "    return [SearchResult(\n"
            "        product_id='SKU-1', title=q,\n"
            "        description='A product',\n"
            "        category='Footwear', price=50.0, position=0)]\n"
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

        with patch("veritail.cli.create_llm_client", return_value=mock_client):
            runner = CliRunner()
            result = runner.invoke(
                main,
                [
                    "run",
                    "--queries",
                    str(queries_file),
                    "--adapter",
                    str(adapter_file),
                    "--config-name",
                    "test",
                    "--backend",
                    "file",
                    "--output-dir",
                    str(tmp_path / "results"),
                    "--llm-model",
                    "test-model",
                    "--sample",
                    "2",
                ],
            )

        assert result.exit_code == 0
        assert "Sampled 2 of 5 queries" in result.output
        # 2 classifier pre-pass calls + 2 relevance judgment calls = 4
        assert mock_client.complete.call_count == 4

    def test_run_sample_gte_total_uses_all(self, tmp_path):
        queries_file = tmp_path / "queries.csv"
        queries_file.write_text("query\nshoes\nboots\n")

        adapter_file = tmp_path / "adapter.py"
        adapter_file.write_text(
            "from veritail.types import SearchResult\n"
            "def search(q):\n"
            "    return [SearchResult(\n"
            "        product_id='SKU-1', title=q,\n"
            "        description='A product',\n"
            "        category='Footwear', price=50.0, position=0)]\n"
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

        with patch("veritail.cli.create_llm_client", return_value=mock_client):
            runner = CliRunner()
            result = runner.invoke(
                main,
                [
                    "run",
                    "--queries",
                    str(queries_file),
                    "--adapter",
                    str(adapter_file),
                    "--config-name",
                    "test",
                    "--backend",
                    "file",
                    "--output-dir",
                    str(tmp_path / "results"),
                    "--llm-model",
                    "test-model",
                    "--sample",
                    "10",
                ],
            )

        assert result.exit_code == 0
        # --sample 10 >= 2 total queries, so all are used
        assert "Loaded 2 queries" in result.output
        # 2 classifier pre-pass calls + 2 relevance judgment calls = 4
        assert mock_client.complete.call_count == 4

    def test_run_sample_is_deterministic(self, tmp_path):
        """Same --sample N with same query file should pick the same queries."""
        queries_file = tmp_path / "queries.csv"
        queries_file.write_text("query\nalpha\nbravo\ncharlie\ndelta\necho\nfoxtrot\n")

        adapter_file = tmp_path / "adapter.py"
        adapter_file.write_text(
            "from veritail.types import SearchResult\n"
            "def search(q):\n"
            "    return [SearchResult(\n"
            "        product_id='SKU-1', title=q,\n"
            "        description='A product',\n"
            "        category='Test', price=10.0, position=0)]\n"
        )

        from unittest.mock import Mock, patch

        from veritail.llm.client import LLMClient, LLMResponse

        queries_seen: list[list[str]] = []

        def capture_calls():
            mock_client = Mock(spec=LLMClient)
            mock_client.complete.return_value = LLMResponse(
                content="SCORE: 2\nREASONING: Good match",
                model="test-model",
                input_tokens=100,
                output_tokens=50,
            )
            return mock_client

        for run_idx in range(2):
            mock_client = capture_calls()
            with patch("veritail.cli.create_llm_client", return_value=mock_client):
                runner = CliRunner()
                result = runner.invoke(
                    main,
                    [
                        "run",
                        "--queries",
                        str(queries_file),
                        "--adapter",
                        str(adapter_file),
                        "--config-name",
                        f"test-{run_idx}",
                        "--backend",
                        "file",
                        "--output-dir",
                        str(tmp_path / f"results-{run_idx}"),
                        "--llm-model",
                        "test-model",
                        "--sample",
                        "3",
                    ],
                )
            assert result.exit_code == 0
            # Extract which queries were judged from the LLM call args
            called_queries = [
                call.args[1]  # user_prompt
                for call in mock_client.complete.call_args_list
            ]
            queries_seen.append(called_queries)

        # Both runs should have called the LLM with the exact same prompts
        assert queries_seen[0] == queries_seen[1]

    def test_run_aborts_on_preflight_check_failure(self, tmp_path):
        queries_file = tmp_path / "queries.csv"
        queries_file.write_text("query\nshoes\n")

        adapter_file = tmp_path / "adapter.py"
        adapter_file.write_text("def search(q): return []\n")

        from unittest.mock import Mock, patch

        from veritail.llm.client import LLMClient

        mock_client = Mock(spec=LLMClient)
        mock_client.preflight_check.side_effect = RuntimeError(
            "Anthropic API key is invalid. "
            "Check your ANTHROPIC_API_KEY environment variable."
        )

        with patch("veritail.cli.create_llm_client", return_value=mock_client):
            runner = CliRunner()
            result = runner.invoke(
                main,
                [
                    "run",
                    "--queries",
                    str(queries_file),
                    "--adapter",
                    str(adapter_file),
                    "--llm-model",
                    "test-model",
                    "--config-name",
                    "test",
                    "--output-dir",
                    str(tmp_path / "results"),
                ],
            )

        assert result.exit_code != 0
        assert "API key is invalid" in result.output

    def test_run_requires_llm_model_for_search(self, tmp_path):
        queries_file = tmp_path / "queries.csv"
        queries_file.write_text("query\nshoes\n")

        adapter_file = tmp_path / "adapter.py"
        adapter_file.write_text("def search(q): return []\n")

        runner = CliRunner()
        result = runner.invoke(
            main,
            [
                "run",
                "--queries",
                str(queries_file),
                "--adapter",
                str(adapter_file),
            ],
        )
        assert result.exit_code != 0
        assert "--llm-model is required when --queries is provided" in result.output

    def test_version(self):
        runner = CliRunner()
        result = runner.invoke(main, ["--version"])
        assert result.exit_code == 0
        assert "veritail" in result.output or "version" in result.output

    def test_run_batch_flag_in_help(self):
        runner = CliRunner()
        result = runner.invoke(main, ["run", "--help"])
        assert result.exit_code == 0
        assert "--batch" in result.output

    def test_run_batch_rejects_base_url(self, tmp_path):
        queries_file = tmp_path / "queries.csv"
        queries_file.write_text("query\nshoes\n")

        adapter_file = tmp_path / "adapter.py"
        adapter_file.write_text("def search(q): return []\n")

        from unittest.mock import Mock, patch

        from veritail.llm.client import LLMClient

        mock_client = Mock(spec=LLMClient)
        mock_client.supports_batch.return_value = True

        with patch("veritail.cli.create_llm_client", return_value=mock_client):
            runner = CliRunner()
            result = runner.invoke(
                main,
                [
                    "run",
                    "--queries",
                    str(queries_file),
                    "--adapter",
                    str(adapter_file),
                    "--llm-model",
                    "gpt-4o",
                    "--llm-base-url",
                    "http://localhost:11434/v1",
                    "--batch",
                ],
            )

        assert result.exit_code != 0
        assert "--batch cannot be used with --llm-base-url" in result.output

    def test_run_batch_invokes_batch_pipeline(self, tmp_path):
        queries_file = tmp_path / "queries.csv"
        queries_file.write_text("query\nshoes\n")

        adapter_file = tmp_path / "adapter.py"
        adapter_file.write_text(
            "from veritail.types import SearchResult\n"
            "def search(q):\n"
            "    return [SearchResult(\n"
            "        product_id='SKU-1', title='Shoe',\n"
            "        description='A shoe',\n"
            "        category='Shoes', price=50.0, position=0)]\n"
        )

        from unittest.mock import Mock, patch

        from veritail.llm.client import LLMClient

        mock_client = Mock(spec=LLMClient)
        mock_client.supports_batch.return_value = True

        mock_metrics = [
            MetricResult(metric_name="ndcg@10", value=0.8),
            MetricResult(metric_name="mrr", value=0.7),
        ]

        with (
            patch("veritail.cli.create_llm_client", return_value=mock_client),
            patch(
                "veritail.cli.run_batch_evaluation",
                return_value=([], [], mock_metrics, []),
            ) as mock_batch,
        ):
            runner = CliRunner()
            result = runner.invoke(
                main,
                [
                    "run",
                    "--queries",
                    str(queries_file),
                    "--adapter",
                    str(adapter_file),
                    "--config-name",
                    "test",
                    "--backend",
                    "file",
                    "--output-dir",
                    str(tmp_path / "results"),
                    "--llm-model",
                    "gpt-4o",
                    "--batch",
                ],
            )

        assert result.exit_code == 0
        mock_batch.assert_called_once()

    def test_run_without_batch_invokes_normal_pipeline(self, tmp_path):
        queries_file = tmp_path / "queries.csv"
        queries_file.write_text("query\nshoes\n")

        adapter_file = tmp_path / "adapter.py"
        adapter_file.write_text(
            "from veritail.types import SearchResult\n"
            "def search(q):\n"
            "    return [SearchResult(\n"
            "        product_id='SKU-1', title='Shoe',\n"
            "        description='A shoe',\n"
            "        category='Shoes', price=50.0, position=0)]\n"
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

        with patch("veritail.cli.create_llm_client", return_value=mock_client):
            runner = CliRunner()
            result = runner.invoke(
                main,
                [
                    "run",
                    "--queries",
                    str(queries_file),
                    "--adapter",
                    str(adapter_file),
                    "--config-name",
                    "test",
                    "--backend",
                    "file",
                    "--output-dir",
                    str(tmp_path / "results"),
                    "--llm-model",
                    "test-model",
                ],
            )

        assert result.exit_code == 0
        # Should have called complete() (sync path), not submit_batch()
        mock_client.complete.assert_called()

    def test_run_batch_dual_config(self, tmp_path):
        queries_file = tmp_path / "queries.csv"
        queries_file.write_text("query\nshoes\n")

        adapter_a = tmp_path / "adapter_a.py"
        adapter_a.write_text(
            "from veritail.types import SearchResult\n"
            "def search(q):\n"
            "    return [SearchResult(\n"
            "        product_id='SKU-1', title='Shoe',\n"
            "        description='A shoe',\n"
            "        category='Shoes', price=50.0, position=0)]\n"
        )
        adapter_b = tmp_path / "adapter_b.py"
        adapter_b.write_text(
            "from veritail.types import SearchResult\n"
            "def search(q):\n"
            "    return [SearchResult(\n"
            "        product_id='SKU-2', title='Boot',\n"
            "        description='A boot',\n"
            "        category='Shoes', price=60.0, position=0)]\n"
        )

        from unittest.mock import Mock, patch

        from veritail.llm.client import LLMClient

        mock_client = Mock(spec=LLMClient)
        mock_client.supports_batch.return_value = True

        mock_metrics = [
            MetricResult(metric_name="ndcg@10", value=0.8),
            MetricResult(metric_name="mrr", value=0.7),
        ]
        dual_return = ([], [], [], [], mock_metrics, mock_metrics, [], [], [])

        with (
            patch("veritail.cli.create_llm_client", return_value=mock_client),
            patch(
                "veritail.cli.run_dual_batch_evaluation",
                return_value=dual_return,
            ) as mock_dual_batch,
        ):
            runner = CliRunner()
            result = runner.invoke(
                main,
                [
                    "run",
                    "--queries",
                    str(queries_file),
                    "--adapter",
                    str(adapter_a),
                    "--adapter",
                    str(adapter_b),
                    "--config-name",
                    "a",
                    "--config-name",
                    "b",
                    "--backend",
                    "file",
                    "--output-dir",
                    str(tmp_path / "results"),
                    "--llm-model",
                    "gpt-4o",
                    "--batch",
                ],
            )

        assert result.exit_code == 0
        mock_dual_batch.assert_called_once()

    def test_run_requires_queries_or_autocomplete(self, tmp_path):
        adapter_file = tmp_path / "adapter.py"
        adapter_file.write_text("def search(q): return []\n")

        runner = CliRunner()
        result = runner.invoke(
            main,
            [
                "run",
                "--adapter",
                str(adapter_file),
                "--llm-model",
                "test-model",
            ],
        )
        assert result.exit_code != 0
        assert "Provide --queries, --autocomplete, or both" in result.output

    def test_run_autocomplete_only(self, tmp_path):
        """--autocomplete + --adapter with suggest() + --llm-model works."""
        prefixes_file = tmp_path / "prefixes.csv"
        prefixes_file.write_text("prefix,type\nrun,short_prefix\n")

        adapter_file = tmp_path / "adapter.py"
        adapter_file.write_text(
            "from veritail.types import AutocompleteResponse\n"
            "def suggest(prefix):\n"
            "    return AutocompleteResponse(suggestions=['running shoes'])\n"
        )

        from unittest.mock import Mock, patch

        from veritail.llm.client import LLMClient, LLMResponse

        mock_client = Mock(spec=LLMClient)
        mock_client.complete.return_value = LLMResponse(
            content="RELEVANCE: 3\nDIVERSITY: 2\nFLAGGED: none\nREASONING: Good.",
            model="test-model",
            input_tokens=10,
            output_tokens=10,
        )

        with patch("veritail.cli.create_llm_client", return_value=mock_client):
            runner = CliRunner()
            result = runner.invoke(
                main,
                [
                    "run",
                    "--autocomplete",
                    str(prefixes_file),
                    "--adapter",
                    str(adapter_file),
                    "--config-name",
                    "ac-test",
                    "--output-dir",
                    str(tmp_path / "results"),
                    "--llm-model",
                    "gpt-4o",
                ],
            )
        assert result.exit_code == 0
        assert "Autocomplete HTML report" in result.output
        assert (tmp_path / "results" / "ac-test" / "autocomplete-report.html").exists()

    def test_run_adapter_missing_suggest(self, tmp_path):
        """--autocomplete provided but adapter lacks suggest() -> clear error."""
        prefixes_file = tmp_path / "prefixes.csv"
        prefixes_file.write_text("prefix,type\nrun,short_prefix\n")

        adapter_file = tmp_path / "adapter.py"
        adapter_file.write_text("def search(q): return []\n")

        runner = CliRunner()
        result = runner.invoke(
            main,
            [
                "run",
                "--autocomplete",
                str(prefixes_file),
                "--adapter",
                str(adapter_file),
                "--llm-model",
                "gpt-4o",
            ],
        )
        assert result.exit_code != 0
        assert "suggest()" in result.output

    def test_run_help_shows_autocomplete_option(self):
        runner = CliRunner()
        result = runner.invoke(main, ["run", "--help"])
        assert result.exit_code == 0
        assert "--autocomplete" in result.output
        assert "--autocomplete-checks" in result.output

    def test_run_both_search_and_autocomplete(self, tmp_path):
        """--queries + --autocomplete + --adapter (with both functions) works."""
        queries_file = tmp_path / "queries.csv"
        queries_file.write_text("query\nshoes\n")

        prefixes_file = tmp_path / "prefixes.csv"
        prefixes_file.write_text("prefix,type\nrun,short_prefix\n")

        adapter_file = tmp_path / "adapter.py"
        adapter_file.write_text(
            "from veritail.types import SearchResult, AutocompleteResponse\n"
            "def search(q):\n"
            "    return [SearchResult(\n"
            "        product_id='SKU-1', title='Shoe',\n"
            "        description='A shoe',\n"
            "        category='Shoes', price=50.0, position=0)]\n"
            "def suggest(prefix):\n"
            "    return AutocompleteResponse(suggestions=['running shoes'])\n"
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

        with patch("veritail.cli.create_llm_client", return_value=mock_client):
            runner = CliRunner()
            result = runner.invoke(
                main,
                [
                    "run",
                    "--queries",
                    str(queries_file),
                    "--autocomplete",
                    str(prefixes_file),
                    "--adapter",
                    str(adapter_file),
                    "--config-name",
                    "both-test",
                    "--backend",
                    "file",
                    "--output-dir",
                    str(tmp_path / "results"),
                    "--llm-model",
                    "test-model",
                ],
            )

        assert result.exit_code == 0
        exp_dir = tmp_path / "results" / "both-test"
        assert (exp_dir / "report.html").exists()
        assert (exp_dir / "autocomplete-report.html").exists()

    def test_init_next_steps_show_all_modes(self, tmp_path):
        """init shows search, autocomplete, and combined run commands."""
        runner = CliRunner()
        result = runner.invoke(main, ["init", "--dir", str(tmp_path)])

        assert result.exit_code == 0
        assert "Search evaluation:" in result.output
        assert "Autocomplete evaluation:" in result.output
        assert "Both:" in result.output
        assert "--autocomplete prefixes.csv" in result.output

    def test_autocomplete_requires_llm_model(self, tmp_path):
        """--autocomplete without --llm-model (single adapter) -> error."""
        prefixes_file = tmp_path / "prefixes.csv"
        prefixes_file.write_text("prefix,type\nrun,short_prefix\n")

        adapter_file = tmp_path / "adapter.py"
        adapter_file.write_text(
            "from veritail.types import AutocompleteResponse\n"
            "def suggest(prefix):\n"
            "    return AutocompleteResponse(suggestions=['running shoes'])\n"
        )

        runner = CliRunner()
        result = runner.invoke(
            main,
            [
                "run",
                "--autocomplete",
                str(prefixes_file),
                "--adapter",
                str(adapter_file),
            ],
        )
        assert result.exit_code != 0
        assert "--llm-model is required for autocomplete evaluation" in result.output

    def test_batch_autocomplete_llm_invokes_batch_pipeline(self, tmp_path):
        """--batch autocomplete routes to batch pipeline."""
        prefixes_file = tmp_path / "prefixes.csv"
        prefixes_file.write_text("prefix,type\nrun,short_prefix\n")

        adapter_file = tmp_path / "adapter.py"
        adapter_file.write_text(
            "from veritail.types import AutocompleteResponse\n"
            "def suggest(prefix):\n"
            "    return AutocompleteResponse(suggestions=['running shoes'])\n"
        )

        from unittest.mock import Mock, patch

        from veritail.llm.client import LLMClient
        from veritail.types import SuggestionJudgment

        mock_client = Mock(spec=LLMClient)
        mock_client.supports_batch.return_value = True

        mock_judgment = SuggestionJudgment(
            prefix="run",
            suggestions=["running shoes"],
            relevance_score=3,
            diversity_score=2,
            flagged_suggestions=[],
            reasoning="Good.",
            model="test-model",
            experiment="test",
        )

        with (
            patch("veritail.cli.create_llm_client", return_value=mock_client),
            patch(
                "veritail.autocomplete.pipeline.run_autocomplete_batch_llm_evaluation",
                return_value=[mock_judgment],
            ) as mock_batch,
        ):
            runner = CliRunner()
            result = runner.invoke(
                main,
                [
                    "run",
                    "--autocomplete",
                    str(prefixes_file),
                    "--adapter",
                    str(adapter_file),
                    "--config-name",
                    "test",
                    "--output-dir",
                    str(tmp_path / "results"),
                    "--llm-model",
                    "gpt-4o",
                    "--batch",
                ],
            )

        assert result.exit_code == 0
        mock_batch.assert_called_once()

    def test_autocomplete_llm_without_batch_invokes_sync(self, tmp_path):
        """Without --batch, autocomplete uses sync pipeline."""
        prefixes_file = tmp_path / "prefixes.csv"
        prefixes_file.write_text("prefix,type\nrun,short_prefix\n")

        adapter_file = tmp_path / "adapter.py"
        adapter_file.write_text(
            "from veritail.types import AutocompleteResponse\n"
            "def suggest(prefix):\n"
            "    return AutocompleteResponse(suggestions=['running shoes'])\n"
        )

        from unittest.mock import Mock, patch

        from veritail.llm.client import LLMClient, LLMResponse

        mock_client = Mock(spec=LLMClient)
        mock_client.complete.return_value = LLMResponse(
            content="RELEVANCE: 3\nDIVERSITY: 2\nFLAGGED: none\nREASONING: Good.",
            model="test-model",
            input_tokens=10,
            output_tokens=10,
        )

        with patch("veritail.cli.create_llm_client", return_value=mock_client):
            runner = CliRunner()
            result = runner.invoke(
                main,
                [
                    "run",
                    "--autocomplete",
                    str(prefixes_file),
                    "--adapter",
                    str(adapter_file),
                    "--config-name",
                    "test",
                    "--output-dir",
                    str(tmp_path / "results"),
                    "--llm-model",
                    "gpt-4o",
                ],
            )

        assert result.exit_code == 0
        # Sync path calls complete(), not submit_batch()
        mock_client.complete.assert_called()
        mock_client.submit_batch.assert_not_called()

    def test_batch_autocomplete_llm_rejects_base_url(self, tmp_path):
        """--batch --llm-base-url → error for autocomplete."""
        prefixes_file = tmp_path / "prefixes.csv"
        prefixes_file.write_text("prefix,type\nrun,short_prefix\n")

        adapter_file = tmp_path / "adapter.py"
        adapter_file.write_text(
            "from veritail.types import AutocompleteResponse\n"
            "def suggest(prefix):\n"
            "    return AutocompleteResponse(suggestions=['running shoes'])\n"
        )

        from unittest.mock import Mock, patch

        from veritail.llm.client import LLMClient

        mock_client = Mock(spec=LLMClient)
        mock_client.supports_batch.return_value = True

        with patch("veritail.cli.create_llm_client", return_value=mock_client):
            runner = CliRunner()
            result = runner.invoke(
                main,
                [
                    "run",
                    "--autocomplete",
                    str(prefixes_file),
                    "--adapter",
                    str(adapter_file),
                    "--config-name",
                    "test",
                    "--output-dir",
                    str(tmp_path / "results"),
                    "--llm-model",
                    "gpt-4o",
                    "--batch",
                    "--llm-base-url",
                    "http://localhost:11434/v1",
                ],
            )

        assert result.exit_code != 0
        assert "--batch cannot be used with --llm-base-url" in result.output

    def test_batch_autocomplete_llm_validates_supports_batch(self, tmp_path):
        """Autocomplete --batch with unsupported model → error."""
        prefixes_file = tmp_path / "prefixes.csv"
        prefixes_file.write_text("prefix,type\nrun,short_prefix\n")

        adapter_file = tmp_path / "adapter.py"
        adapter_file.write_text(
            "from veritail.types import AutocompleteResponse\n"
            "def suggest(prefix):\n"
            "    return AutocompleteResponse(suggestions=['running shoes'])\n"
        )

        from unittest.mock import Mock, patch

        from veritail.llm.client import LLMClient

        mock_client = Mock(spec=LLMClient)
        mock_client.supports_batch.return_value = False

        with patch("veritail.cli.create_llm_client", return_value=mock_client):
            runner = CliRunner()
            result = runner.invoke(
                main,
                [
                    "run",
                    "--autocomplete",
                    str(prefixes_file),
                    "--adapter",
                    str(adapter_file),
                    "--config-name",
                    "test",
                    "--output-dir",
                    str(tmp_path / "results"),
                    "--llm-model",
                    "gpt-4o",
                    "--batch",
                ],
            )

        assert result.exit_code != 0
        assert "does not support batch operations" in result.output

    def test_run_requires_adapter(self, tmp_path):
        queries_file = tmp_path / "queries.csv"
        queries_file.write_text("query\nshoes\n")

        runner = CliRunner()
        result = runner.invoke(
            main,
            [
                "run",
                "--queries",
                str(queries_file),
                "--llm-model",
                "test-model",
            ],
        )
        assert result.exit_code != 0
        assert "--adapter is required" in result.output

    def test_run_rejects_more_than_two_adapters(self, tmp_path):
        queries_file = tmp_path / "queries.csv"
        queries_file.write_text("query\nshoes\n")

        adapter_a = tmp_path / "a.py"
        adapter_a.write_text("def search(q): return []\n")
        adapter_b = tmp_path / "b.py"
        adapter_b.write_text("def search(q): return []\n")
        adapter_c = tmp_path / "c.py"
        adapter_c.write_text("def search(q): return []\n")

        runner = CliRunner()
        result = runner.invoke(
            main,
            [
                "run",
                "--queries",
                str(queries_file),
                "--adapter",
                str(adapter_a),
                "--adapter",
                str(adapter_b),
                "--adapter",
                str(adapter_c),
                "--llm-model",
                "test-model",
            ],
        )
        assert result.exit_code != 0
        assert "At most 2 adapter/config-name pairs" in result.output

    def test_run_resume_requires_config_name(self, tmp_path):
        queries_file = tmp_path / "queries.csv"
        queries_file.write_text("query\nshoes\n")

        adapter_file = tmp_path / "adapter.py"
        adapter_file.write_text("def search(q): return []\n")

        runner = CliRunner()
        result = runner.invoke(
            main,
            [
                "run",
                "--queries",
                str(queries_file),
                "--adapter",
                str(adapter_file),
                "--llm-model",
                "test-model",
                "--resume",
            ],
        )
        assert result.exit_code != 0
        assert "--resume requires --config-name" in result.output

    def test_run_resume_nonexistent_experiment_dir(self, tmp_path):
        queries_file = tmp_path / "queries.csv"
        queries_file.write_text("query\nshoes\n")

        adapter_file = tmp_path / "adapter.py"
        adapter_file.write_text("def search(q): return []\n")

        runner = CliRunner()
        result = runner.invoke(
            main,
            [
                "run",
                "--queries",
                str(queries_file),
                "--adapter",
                str(adapter_file),
                "--llm-model",
                "test-model",
                "--config-name",
                "nonexistent",
                "--output-dir",
                str(tmp_path / "results"),
                "--resume",
            ],
        )
        assert result.exit_code != 0
        assert "does not exist" in result.output

    def test_run_resume_config_mismatch_llm_model(self, tmp_path):
        queries_file = tmp_path / "queries.csv"
        queries_file.write_text("query\nshoes\n")

        adapter_file = tmp_path / "adapter.py"
        adapter_file.write_text("def search(q): return []\n")

        output_dir = tmp_path / "results"
        exp_dir = output_dir / "my-config"
        exp_dir.mkdir(parents=True)
        config_file = exp_dir / "config.json"
        config_file.write_text(
            json.dumps({"llm_model": "gpt-4o", "top_k": 10}),
            encoding="utf-8",
        )

        runner = CliRunner()
        result = runner.invoke(
            main,
            [
                "run",
                "--queries",
                str(queries_file),
                "--adapter",
                str(adapter_file),
                "--llm-model",
                "claude-sonnet-4-5",
                "--config-name",
                "my-config",
                "--output-dir",
                str(output_dir),
                "--resume",
            ],
        )
        assert result.exit_code != 0
        assert "config mismatch" in result.output
        assert "llm_model" in result.output

    def test_run_resume_config_mismatch_top_k(self, tmp_path):
        queries_file = tmp_path / "queries.csv"
        queries_file.write_text("query\nshoes\n")

        adapter_file = tmp_path / "adapter.py"
        adapter_file.write_text("def search(q): return []\n")

        output_dir = tmp_path / "results"
        exp_dir = output_dir / "my-config"
        exp_dir.mkdir(parents=True)
        config_file = exp_dir / "config.json"
        config_file.write_text(
            json.dumps({"llm_model": "gpt-4o", "top_k": 10}),
            encoding="utf-8",
        )

        runner = CliRunner()
        result = runner.invoke(
            main,
            [
                "run",
                "--queries",
                str(queries_file),
                "--adapter",
                str(adapter_file),
                "--llm-model",
                "gpt-4o",
                "--top-k",
                "5",
                "--config-name",
                "my-config",
                "--output-dir",
                str(output_dir),
                "--resume",
            ],
        )
        assert result.exit_code != 0
        assert "config mismatch" in result.output
        assert "top_k" in result.output

    def test_run_batch_rejects_unsupported_model_search(self, tmp_path):
        queries_file = tmp_path / "queries.csv"
        queries_file.write_text("query\nshoes\n")

        adapter_file = tmp_path / "adapter.py"
        adapter_file.write_text("def search(q): return []\n")

        from unittest.mock import Mock, patch

        from veritail.llm.client import LLMClient

        mock_client = Mock(spec=LLMClient)
        mock_client.supports_batch.return_value = False

        with patch("veritail.cli.create_llm_client", return_value=mock_client):
            runner = CliRunner()
            result = runner.invoke(
                main,
                [
                    "run",
                    "--queries",
                    str(queries_file),
                    "--adapter",
                    str(adapter_file),
                    "--llm-model",
                    "gpt-4o",
                    "--batch",
                ],
            )
        assert result.exit_code != 0
        assert "does not support batch operations" in result.output

    def test_batch_concurrent_search_and_autocomplete(self, tmp_path):
        """--batch with both --queries and --autocomplete runs both pipelines."""
        queries_file = tmp_path / "queries.csv"
        queries_file.write_text("query\nshoes\n")

        prefixes_file = tmp_path / "prefixes.csv"
        prefixes_file.write_text("prefix,type\nrun,short_prefix\n")

        adapter_file = tmp_path / "adapter.py"
        adapter_file.write_text(
            "from veritail.types import SearchResult, AutocompleteResponse\n"
            "def search(q):\n"
            "    return [SearchResult(\n"
            "        product_id='SKU-1', title='Shoe',\n"
            "        description='A shoe',\n"
            "        category='Shoes', price=50.0, position=0)]\n"
            "def suggest(prefix):\n"
            "    return AutocompleteResponse(suggestions=['running shoes'])\n"
        )

        from pathlib import Path
        from unittest.mock import Mock, patch

        from veritail.llm.client import LLMClient

        search_called = []
        ac_called = []

        def mock_search_pipeline(**kwargs):
            search_called.append(True)
            # Create a minimal report file
            exp_dir = Path(kwargs["output_dir"]) / kwargs["config_names"][0]
            exp_dir.mkdir(parents=True, exist_ok=True)
            html_path = exp_dir / "report.html"
            html_path.write_text("<html>search</html>", encoding="utf-8")
            return [html_path]

        def mock_ac_pipeline(**kwargs):
            ac_called.append(True)
            exp_dir = Path(kwargs["output_dir"]) / kwargs["config_names"][0]
            exp_dir.mkdir(parents=True, exist_ok=True)
            html_path = exp_dir / "autocomplete-report.html"
            html_path.write_text("<html>ac</html>", encoding="utf-8")
            return [html_path]

        mock_client = Mock(spec=LLMClient)
        mock_client.supports_batch.return_value = True

        with (
            patch("veritail.cli.create_llm_client", return_value=mock_client),
            patch(
                "veritail.cli._run_search_pipeline",
                side_effect=mock_search_pipeline,
            ),
            patch(
                "veritail.cli._run_autocomplete_pipeline",
                side_effect=mock_ac_pipeline,
            ),
        ):
            runner = CliRunner()
            result = runner.invoke(
                main,
                [
                    "run",
                    "--queries",
                    str(queries_file),
                    "--autocomplete",
                    str(prefixes_file),
                    "--adapter",
                    str(adapter_file),
                    "--config-name",
                    "test",
                    "--output-dir",
                    str(tmp_path / "results"),
                    "--llm-model",
                    "gpt-4o",
                    "--batch",
                ],
            )

        assert result.exit_code == 0
        # Both pipelines were invoked
        assert len(search_called) == 1
        assert len(ac_called) == 1

    def test_run_dual_config_without_batch(self, tmp_path):
        queries_file = tmp_path / "queries.csv"
        queries_file.write_text("query\nshoes\n")

        adapter_a = tmp_path / "adapter_a.py"
        adapter_a.write_text(
            "from veritail.types import SearchResult\n"
            "def search(q):\n"
            "    return [SearchResult(\n"
            "        product_id='SKU-1', title='Shoe',\n"
            "        description='A shoe',\n"
            "        category='Shoes', price=50.0, position=0)]\n"
        )
        adapter_b = tmp_path / "adapter_b.py"
        adapter_b.write_text(
            "from veritail.types import SearchResult\n"
            "def search(q):\n"
            "    return [SearchResult(\n"
            "        product_id='SKU-2', title='Boot',\n"
            "        description='A boot',\n"
            "        category='Shoes', price=60.0, position=0)]\n"
        )

        from unittest.mock import Mock, patch

        from veritail.llm.client import LLMClient

        mock_client = Mock(spec=LLMClient)

        mock_metrics = [
            MetricResult(metric_name="ndcg@10", value=0.8),
            MetricResult(metric_name="mrr", value=0.7),
        ]
        dual_return = ([], [], [], [], mock_metrics, mock_metrics, [], [], [])

        with (
            patch("veritail.cli.create_llm_client", return_value=mock_client),
            patch(
                "veritail.cli.run_dual_evaluation",
                return_value=dual_return,
            ) as mock_dual,
        ):
            runner = CliRunner()
            result = runner.invoke(
                main,
                [
                    "run",
                    "--queries",
                    str(queries_file),
                    "--adapter",
                    str(adapter_a),
                    "--adapter",
                    str(adapter_b),
                    "--config-name",
                    "a",
                    "--config-name",
                    "b",
                    "--backend",
                    "file",
                    "--output-dir",
                    str(tmp_path / "results"),
                    "--llm-model",
                    "gpt-4o",
                ],
            )

        assert result.exit_code == 0
        mock_dual.assert_called_once()

    def test_batch_concurrent_both_fail(self, tmp_path):
        """Both pipelines fail — both error messages appear in output."""
        queries_file = tmp_path / "queries.csv"
        queries_file.write_text("query\nshoes\n")

        prefixes_file = tmp_path / "prefixes.csv"
        prefixes_file.write_text("prefix,type\nrun,short_prefix\n")

        adapter_file = tmp_path / "adapter.py"
        adapter_file.write_text(
            "from veritail.types import SearchResult, AutocompleteResponse\n"
            "def search(q):\n"
            "    return [SearchResult(\n"
            "        product_id='SKU-1', title='Shoe',\n"
            "        description='A shoe',\n"
            "        category='Shoes', price=50.0, position=0)]\n"
            "def suggest(prefix):\n"
            "    return AutocompleteResponse(suggestions=['running shoes'])\n"
        )

        from unittest.mock import Mock, patch

        from veritail.llm.client import LLMClient

        mock_client = Mock(spec=LLMClient)
        mock_client.supports_batch.return_value = True

        def fail_search(**kwargs):
            raise RuntimeError("search pipeline exploded")

        def fail_ac(**kwargs):
            raise RuntimeError("autocomplete pipeline exploded")

        with (
            patch("veritail.cli.create_llm_client", return_value=mock_client),
            patch("veritail.cli._run_search_pipeline", side_effect=fail_search),
            patch("veritail.cli._run_autocomplete_pipeline", side_effect=fail_ac),
        ):
            runner = CliRunner()
            result = runner.invoke(
                main,
                [
                    "run",
                    "--queries",
                    str(queries_file),
                    "--autocomplete",
                    str(prefixes_file),
                    "--adapter",
                    str(adapter_file),
                    "--config-name",
                    "test",
                    "--output-dir",
                    str(tmp_path / "results"),
                    "--llm-model",
                    "gpt-4o",
                    "--batch",
                ],
            )

        assert result.exit_code != 0
        assert "search pipeline exploded" in result.output
        assert "autocomplete pipeline exploded" in result.output

    def test_batch_concurrent_one_fails_other_cancelled(self, tmp_path):
        """One pipeline fails, other gets cancelled — only real error surfaces."""
        queries_file = tmp_path / "queries.csv"
        queries_file.write_text("query\nshoes\n")

        prefixes_file = tmp_path / "prefixes.csv"
        prefixes_file.write_text("prefix,type\nrun,short_prefix\n")

        adapter_file = tmp_path / "adapter.py"
        adapter_file.write_text(
            "from veritail.types import SearchResult, AutocompleteResponse\n"
            "def search(q):\n"
            "    return [SearchResult(\n"
            "        product_id='SKU-1', title='Shoe',\n"
            "        description='A shoe',\n"
            "        category='Shoes', price=50.0, position=0)]\n"
            "def suggest(prefix):\n"
            "    return AutocompleteResponse(suggestions=['running shoes'])\n"
        )

        from unittest.mock import Mock, patch

        from veritail.batch_utils import BatchCancelledError
        from veritail.llm.client import LLMClient

        mock_client = Mock(spec=LLMClient)
        mock_client.supports_batch.return_value = True

        def fail_search(**kwargs):
            raise RuntimeError("search batch failed")

        def slow_ac(**kwargs):
            """Simulate a pipeline that checks cancel_event via polling."""
            cancel = kwargs.get("cancel_event")
            if cancel is not None:
                # Wait for cancellation (simulates poll loop)
                cancel.wait(timeout=10)
                if cancel.is_set():
                    raise BatchCancelledError()
            return []

        with (
            patch("veritail.cli.create_llm_client", return_value=mock_client),
            patch("veritail.cli._run_search_pipeline", side_effect=fail_search),
            patch("veritail.cli._run_autocomplete_pipeline", side_effect=slow_ac),
        ):
            runner = CliRunner()
            result = runner.invoke(
                main,
                [
                    "run",
                    "--queries",
                    str(queries_file),
                    "--autocomplete",
                    str(prefixes_file),
                    "--adapter",
                    str(adapter_file),
                    "--config-name",
                    "test",
                    "--output-dir",
                    str(tmp_path / "results"),
                    "--llm-model",
                    "gpt-4o",
                    "--batch",
                ],
            )

        assert result.exit_code != 0
        assert "search batch failed" in result.output
        # The BatchCancelledError message should NOT appear
        assert "Batch polling cancelled" not in result.output
