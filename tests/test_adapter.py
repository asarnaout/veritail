"""Tests for adapter loading."""

from __future__ import annotations

import pytest

from veritail.adapter import load_adapter


def test_load_valid_adapter(tmp_path):
    adapter_file = tmp_path / "my_adapter.py"
    adapter_file.write_text(
        "from veritail.types import SearchResult\n"
        "\n"
        "def search(query: str) -> list[SearchResult]:\n"
        "    return [\n"
        "        SearchResult(\n"
        '            product_id="SKU-001",\n'
        '            title=f"Result for {query}",\n'
        '            description="Test",\n'
        '            category="Test",\n'
        "            price=9.99,\n"
        "            position=0,\n"
        "        )\n"
        "    ]\n"
    )

    search_fn = load_adapter(str(adapter_file))
    response = search_fn("test query")
    # Bare list adapters are wrapped into SearchResponse
    from veritail.types import SearchResponse

    assert isinstance(response, SearchResponse)
    assert len(response.results) == 1
    assert response.results[0].product_id == "SKU-001"
    assert response.results[0].title == "Result for test query"
    assert response.corrected_query is None


def test_load_adapter_returns_search_response(tmp_path):
    adapter_file = tmp_path / "sr_adapter.py"
    adapter_file.write_text(
        "from veritail.types import SearchResponse, SearchResult\n"
        "\n"
        "def search(query: str) -> SearchResponse:\n"
        "    return SearchResponse(\n"
        "        results=[SearchResult(\n"
        '            product_id="SKU-001",\n'
        '            title=f"Result for {query}",\n'
        '            description="Test",\n'
        '            category="Test",\n'
        "            price=9.99,\n"
        "            position=0,\n"
        "        )],\n"
        '        corrected_query="corrected",\n'
        "    )\n"
    )

    search_fn = load_adapter(str(adapter_file))
    response = search_fn("test query")
    from veritail.types import SearchResponse

    assert isinstance(response, SearchResponse)
    assert len(response.results) == 1
    assert response.corrected_query == "corrected"


def test_load_adapter_missing_search_function(tmp_path):
    adapter_file = tmp_path / "bad_adapter.py"
    adapter_file.write_text("def query(q): return []\n")

    with pytest.raises(AttributeError, match="must define a 'search' function"):
        load_adapter(str(adapter_file))


def test_load_adapter_not_callable(tmp_path):
    adapter_file = tmp_path / "bad_adapter.py"
    adapter_file.write_text("search = 42\n")

    with pytest.raises(TypeError, match="not callable"):
        load_adapter(str(adapter_file))


def test_load_adapter_file_not_found():
    with pytest.raises(FileNotFoundError):
        load_adapter("/nonexistent/adapter.py")


def test_load_adapter_wrong_extension(tmp_path):
    adapter_file = tmp_path / "adapter.txt"
    adapter_file.write_text("def search(q): return []\n")

    with pytest.raises(ValueError, match="must be a Python file"):
        load_adapter(str(adapter_file))
