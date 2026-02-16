"""Tests for query set loading."""

from __future__ import annotations

import json

import pytest

from veritail.queries import load_queries


def test_load_csv(tmp_path):
    csv_file = tmp_path / "queries.csv"
    csv_file.write_text(
        "query,type,category\nrunning shoes,broad,Shoes\nred dress,attribute,Clothing\n"
    )

    entries = load_queries(str(csv_file))
    assert len(entries) == 2
    assert entries[0].query == "running shoes"
    assert entries[0].type == "broad"
    assert entries[0].category == "Shoes"
    assert entries[1].query == "red dress"


def test_load_csv_minimal(tmp_path):
    csv_file = tmp_path / "queries.csv"
    csv_file.write_text("query\nrunning shoes\nred dress\n")

    entries = load_queries(str(csv_file))
    assert len(entries) == 2
    assert entries[0].type is None
    assert entries[0].category is None


def test_load_csv_skips_empty_queries(tmp_path):
    csv_file = tmp_path / "queries.csv"
    csv_file.write_text("query\nrunning shoes\n\nred dress\n")

    entries = load_queries(str(csv_file))
    assert len(entries) == 2


def test_load_csv_missing_query_column(tmp_path):
    csv_file = tmp_path / "queries.csv"
    csv_file.write_text("search_term,type\nrunning shoes,broad\n")

    with pytest.raises(ValueError, match="must have a 'query' column"):
        load_queries(str(csv_file))


def test_load_csv_empty_file(tmp_path):
    csv_file = tmp_path / "queries.csv"
    csv_file.write_text("query\n")

    with pytest.raises(ValueError, match="No queries found"):
        load_queries(str(csv_file))


def test_load_json(tmp_path):
    json_file = tmp_path / "queries.json"
    data = [
        {
            "query": "running shoes",
            "type": "broad",
            "category": "Shoes",
        },
        {"query": "red dress", "type": "attribute"},
    ]
    json_file.write_text(json.dumps(data))

    entries = load_queries(str(json_file))
    assert len(entries) == 2
    assert entries[0].query == "running shoes"
    assert entries[0].category == "Shoes"
    assert entries[1].category is None


def test_load_json_minimal(tmp_path):
    json_file = tmp_path / "queries.json"
    data = [{"query": "running shoes"}, {"query": "red dress"}]
    json_file.write_text(json.dumps(data))

    entries = load_queries(str(json_file))
    assert len(entries) == 2
    assert entries[0].type is None


def test_load_json_not_a_list(tmp_path):
    json_file = tmp_path / "queries.json"
    json_file.write_text('{"query": "running shoes"}')

    with pytest.raises(ValueError, match="must contain a list"):
        load_queries(str(json_file))


def test_load_json_missing_query_key(tmp_path):
    json_file = tmp_path / "queries.json"
    data = [{"search_term": "running shoes"}]
    json_file.write_text(json.dumps(data))

    with pytest.raises(ValueError, match="must have a 'query' key"):
        load_queries(str(json_file))


def test_load_unsupported_format(tmp_path):
    txt_file = tmp_path / "queries.txt"
    txt_file.write_text("running shoes")

    with pytest.raises(ValueError, match="Unsupported query file format"):
        load_queries(str(txt_file))


def test_load_file_not_found():
    with pytest.raises(FileNotFoundError):
        load_queries("/nonexistent/queries.csv")
