"""Tests for prefix generation from query sets."""

from __future__ import annotations

from veritail.autocomplete.prefixgen import generate_prefixes


class TestGeneratePrefixes:
    def test_basic(self, tmp_path) -> None:
        queries_csv = tmp_path / "queries.csv"
        queries_csv.write_text("query,type\nrunning shoes,broad\nnike,navigational\n")

        output = tmp_path / "prefixes.csv"
        rows = generate_prefixes(str(queries_csv), str(output))

        # 2 queries * 3 ratios = 6 rows
        assert len(rows) == 6
        assert output.exists()

    def test_custom_ratios(self, tmp_path) -> None:
        queries_csv = tmp_path / "queries.csv"
        queries_csv.write_text("query,type\nrunning shoes,broad\n")

        output = tmp_path / "prefixes.csv"
        rows = generate_prefixes(str(queries_csv), str(output), char_ratios=[0.5])
        assert len(rows) == 1
        # "running shoes" has 13 chars, 0.5 * 13 = 6.5, round to 6
        assert rows[0]["prefix"] == "runnin"
        assert rows[0]["target_query"] == "running shoes"

    def test_type_labels(self, tmp_path) -> None:
        queries_csv = tmp_path / "queries.csv"
        queries_csv.write_text("query\nrunning shoes\n")

        output = tmp_path / "prefixes.csv"
        rows = generate_prefixes(str(queries_csv), str(output))

        types = {r["type"] for r in rows}
        assert "short_prefix" in types
        assert "mid_prefix" in types
        assert "long_prefix" in types

    def test_short_query(self, tmp_path) -> None:
        queries_csv = tmp_path / "queries.csv"
        queries_csv.write_text("query\nab\n")

        output = tmp_path / "prefixes.csv"
        rows = generate_prefixes(str(queries_csv), str(output))
        # At least 1 char per prefix
        assert all(len(r["prefix"]) >= 1 for r in rows)

    def test_output_csv_columns(self, tmp_path) -> None:
        queries_csv = tmp_path / "queries.csv"
        queries_csv.write_text("query\nshoes\n")

        output = tmp_path / "prefixes.csv"
        generate_prefixes(str(queries_csv), str(output))

        content = output.read_text()
        header = content.split("\n")[0]
        assert "prefix" in header
        assert "target_query" in header
        assert "type" in header

    def test_creates_output_dir(self, tmp_path) -> None:
        queries_csv = tmp_path / "queries.csv"
        queries_csv.write_text("query\nshoes\n")

        output = tmp_path / "subdir" / "prefixes.csv"
        generate_prefixes(str(queries_csv), str(output))
        assert output.exists()
