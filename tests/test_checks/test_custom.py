"""Tests for custom check loading."""

from __future__ import annotations

import pytest

from veritail.checks.custom import load_checks
from veritail.types import QueryEntry, SearchResult


def _make_query() -> QueryEntry:
    return QueryEntry(query="test query", type="broad")


def _make_results() -> list[SearchResult]:
    return [
        SearchResult(
            product_id="SKU-1",
            title="Test Product",
            description="desc",
            category="Test",
            price=10.0,
            position=0,
        )
    ]


def test_load_single_check(tmp_path):
    check_file = tmp_path / "my_checks.py"
    check_file.write_text(
        "from veritail.types import CheckResult, QueryEntry, SearchResult\n"
        "\n"
        "def check_always_pass(\n"
        "    query: QueryEntry, results: list[SearchResult]\n"
        ") -> list[CheckResult]:\n"
        "    return [CheckResult(\n"
        "        check_name='always_pass',\n"
        "        query=query.query,\n"
        "        product_id=None,\n"
        "        passed=True,\n"
        "        detail='Always passes',\n"
        "    )]\n"
    )

    fns = load_checks(str(check_file))
    assert len(fns) == 1

    results = fns[0](_make_query(), _make_results())
    assert len(results) == 1
    assert results[0].check_name == "always_pass"
    assert results[0].passed is True


def test_load_multiple_checks_excludes_helpers(tmp_path):
    check_file = tmp_path / "my_checks.py"
    check_file.write_text(
        "from veritail.types import CheckResult, QueryEntry, SearchResult\n"
        "\n"
        "def _helper(): pass\n"
        "\n"
        "def check_one(\n"
        "    query: QueryEntry, results: list[SearchResult]\n"
        ") -> list[CheckResult]:\n"
        "    return []\n"
        "\n"
        "def check_two(\n"
        "    query: QueryEntry, results: list[SearchResult]\n"
        ") -> list[CheckResult]:\n"
        "    return []\n"
        "\n"
        "def do_something(): pass\n"
    )

    fns = load_checks(str(check_file))
    assert len(fns) == 2


def test_sorted_discovery_order(tmp_path):
    check_file = tmp_path / "my_checks.py"
    check_file.write_text(
        "from veritail.types import CheckResult, QueryEntry, SearchResult\n"
        "\n"
        "def check_zebra(\n"
        "    query: QueryEntry, results: list[SearchResult]\n"
        ") -> list[CheckResult]:\n"
        "    return [CheckResult(\n"
        "        check_name='zebra', query=query.query,\n"
        "        product_id=None, passed=True, detail='z',\n"
        "    )]\n"
        "\n"
        "def check_alpha(\n"
        "    query: QueryEntry, results: list[SearchResult]\n"
        ") -> list[CheckResult]:\n"
        "    return [CheckResult(\n"
        "        check_name='alpha', query=query.query,\n"
        "        product_id=None, passed=True, detail='a',\n"
        "    )]\n"
    )

    fns = load_checks(str(check_file))
    results_first = fns[0](_make_query(), _make_results())
    results_second = fns[1](_make_query(), _make_results())

    assert results_first[0].check_name == "alpha"
    assert results_second[0].check_name == "zebra"


def test_no_check_functions_raises(tmp_path):
    check_file = tmp_path / "empty_checks.py"
    check_file.write_text("def helper(): pass\n")

    with pytest.raises(ValueError, match="no check_\\* functions"):
        load_checks(str(check_file))


def test_file_not_found():
    with pytest.raises(FileNotFoundError):
        load_checks("/nonexistent/checks.py")


def test_wrong_extension(tmp_path):
    check_file = tmp_path / "checks.txt"
    check_file.write_text("def check_a(q, r): return []\n")

    with pytest.raises(ValueError, match="must be a Python file"):
        load_checks(str(check_file))


def test_non_callable_check_name_skipped(tmp_path):
    check_file = tmp_path / "my_checks.py"
    check_file.write_text(
        "from veritail.types import CheckResult, QueryEntry, SearchResult\n"
        "\n"
        "check_threshold = 0.5\n"
        "check_constant = 42\n"
        "\n"
        "def check_real(\n"
        "    query: QueryEntry, results: list[SearchResult]\n"
        ") -> list[CheckResult]:\n"
        "    return []\n"
    )

    fns = load_checks(str(check_file))
    assert len(fns) == 1
