"""Tests for autocomplete prefix set loading."""

from __future__ import annotations

import json

import pytest

from veritail.autocomplete.queries import load_prefixes


class TestLoadPrefixesCsv:
    def test_valid_csv(self, tmp_path) -> None:
        csv_file = tmp_path / "prefixes.csv"
        csv_file.write_text("prefix,type\nrun,short_prefix\n")
        entries = load_prefixes(str(csv_file))
        assert len(entries) == 1
        assert entries[0].prefix == "run"
        assert entries[0].type == "short_prefix"

    def test_missing_prefix_column(self, tmp_path) -> None:
        csv_file = tmp_path / "prefixes.csv"
        csv_file.write_text("type\nshort\n")
        with pytest.raises(ValueError, match="prefix"):
            load_prefixes(str(csv_file))

    def test_optional_type_inferred(self, tmp_path) -> None:
        csv_file = tmp_path / "prefixes.csv"
        csv_file.write_text("prefix\nrun\n")
        entries = load_prefixes(str(csv_file))
        assert entries[0].type == "mid_prefix"  # "run" has 3 chars

    def test_empty_rows_skipped(self, tmp_path) -> None:
        csv_file = tmp_path / "prefixes.csv"
        csv_file.write_text("prefix\nrun\n\n")
        entries = load_prefixes(str(csv_file))
        assert len(entries) == 1

    def test_all_empty(self, tmp_path) -> None:
        csv_file = tmp_path / "prefixes.csv"
        csv_file.write_text("prefix\n\n")
        with pytest.raises(ValueError, match="No prefixes"):
            load_prefixes(str(csv_file))


class TestLoadPrefixesJson:
    def test_valid_json(self, tmp_path) -> None:
        json_file = tmp_path / "prefixes.json"
        data = [{"prefix": "run", "type": "short"}]
        json_file.write_text(json.dumps(data))
        entries = load_prefixes(str(json_file))
        assert len(entries) == 1
        assert entries[0].prefix == "run"

    def test_missing_prefix_key(self, tmp_path) -> None:
        json_file = tmp_path / "prefixes.json"
        data = [{"type": "short"}]
        json_file.write_text(json.dumps(data))
        with pytest.raises(ValueError, match="prefix"):
            load_prefixes(str(json_file))

    def test_not_a_list(self, tmp_path) -> None:
        json_file = tmp_path / "prefixes.json"
        json_file.write_text('{"prefix": "run"}')
        with pytest.raises(ValueError, match="list"):
            load_prefixes(str(json_file))


class TestInferPrefixType:
    def test_short_prefix_boundary_2_chars(self, tmp_path) -> None:
        csv_file = tmp_path / "prefixes.csv"
        csv_file.write_text("prefix\nab\n")
        entries = load_prefixes(str(csv_file))
        assert entries[0].type == "short_prefix"

    def test_mid_prefix_boundary_3_chars(self, tmp_path) -> None:
        csv_file = tmp_path / "prefixes.csv"
        csv_file.write_text("prefix\nabc\n")
        entries = load_prefixes(str(csv_file))
        assert entries[0].type == "mid_prefix"

    def test_mid_prefix_boundary_9_chars(self, tmp_path) -> None:
        csv_file = tmp_path / "prefixes.csv"
        csv_file.write_text("prefix\nabcdefghi\n")
        entries = load_prefixes(str(csv_file))
        assert entries[0].type == "mid_prefix"

    def test_long_prefix_boundary_10_chars(self, tmp_path) -> None:
        csv_file = tmp_path / "prefixes.csv"
        csv_file.write_text("prefix\nabcdefghij\n")
        entries = load_prefixes(str(csv_file))
        assert entries[0].type == "long_prefix"

    def test_explicit_type_takes_precedence(self, tmp_path) -> None:
        csv_file = tmp_path / "prefixes.csv"
        csv_file.write_text("prefix,type\nab,custom_type\n")
        entries = load_prefixes(str(csv_file))
        assert entries[0].type == "custom_type"

    def test_json_infer(self, tmp_path) -> None:
        json_file = tmp_path / "prefixes.json"
        data = [{"prefix": "ab"}]
        json_file.write_text(json.dumps(data))
        entries = load_prefixes(str(json_file))
        assert entries[0].type == "short_prefix"


class TestLoadPrefixesGeneral:
    def test_file_not_found(self) -> None:
        with pytest.raises(FileNotFoundError):
            load_prefixes("/nonexistent/file.csv")

    def test_unsupported_format(self, tmp_path) -> None:
        txt_file = tmp_path / "prefixes.txt"
        txt_file.write_text("hello")
        with pytest.raises(ValueError, match="Unsupported"):
            load_prefixes(str(txt_file))
