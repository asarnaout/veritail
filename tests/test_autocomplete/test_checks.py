"""Tests for autocomplete deterministic checks."""

from __future__ import annotations

from veritail.autocomplete.checks import (
    check_duplicate_suggestions,
    check_empty_suggestions,
    check_offensive_content,
    check_prefix_coherence,
)


class TestEmptySuggestions:
    def test_no_suggestions(self) -> None:
        result = check_empty_suggestions("run", [])
        assert not result.passed
        assert result.severity == "fail"

    def test_has_suggestions(self) -> None:
        result = check_empty_suggestions("run", ["running shoes"])
        assert result.passed


class TestDuplicateSuggestions:
    def test_no_duplicates(self) -> None:
        results = check_duplicate_suggestions("run", ["running", "runner"])
        assert len(results) == 0

    def test_exact_duplicate(self) -> None:
        results = check_duplicate_suggestions("run", ["running", "running"])
        assert len(results) == 1
        assert not results[0].passed

    def test_case_insensitive_duplicate(self) -> None:
        results = check_duplicate_suggestions("run", ["Running", "running"])
        assert len(results) == 1
        assert not results[0].passed

    def test_empty_list(self) -> None:
        results = check_duplicate_suggestions("run", [])
        assert len(results) == 0

    def test_multiple_duplicates(self) -> None:
        results = check_duplicate_suggestions("run", ["a", "b", "a", "b"])
        assert len(results) == 2


class TestPrefixCoherence:
    def test_starts_with_prefix(self) -> None:
        results = check_prefix_coherence("run", ["running shoes", "run fast"])
        assert all(r.passed for r in results)

    def test_shares_tokens(self) -> None:
        results = check_prefix_coherence("run", ["best run gear"])
        assert all(r.passed for r in results)

    def test_no_coherence(self) -> None:
        results = check_prefix_coherence("xyz", ["basketball"])
        assert len(results) == 1
        assert not results[0].passed

    def test_empty_suggestions(self) -> None:
        results = check_prefix_coherence("run", [])
        assert len(results) == 0


class TestOffensiveContent:
    def test_no_blocklist(self) -> None:
        results = check_offensive_content("run", ["running shoes"])
        assert len(results) == 0

    def test_empty_blocklist(self) -> None:
        results = check_offensive_content("run", ["running shoes"], blocklist=[])
        assert len(results) == 0

    def test_no_match(self) -> None:
        results = check_offensive_content(
            "run", ["running shoes"], blocklist=["badword"]
        )
        assert len(results) == 0

    def test_match_found(self) -> None:
        results = check_offensive_content(
            "run", ["running badword shoes"], blocklist=["badword"]
        )
        assert len(results) == 1
        assert not results[0].passed
        assert results[0].severity == "fail"

    def test_case_insensitive(self) -> None:
        results = check_offensive_content(
            "run", ["running BADWORD"], blocklist=["badword"]
        )
        assert len(results) == 1
        assert not results[0].passed
