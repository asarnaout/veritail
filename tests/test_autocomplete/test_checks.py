"""Tests for autocomplete deterministic checks."""

from __future__ import annotations

from veritail.autocomplete.checks import (
    check_duplicate_suggestions,
    check_empty_suggestions,
    check_encoding_issues,
    check_latency,
    check_length_anomalies,
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


class TestEncodingIssues:
    def test_clean_suggestions(self) -> None:
        results = check_encoding_issues("run", ["running shoes", "runner"])
        assert len(results) == 0

    def test_html_entity(self) -> None:
        results = check_encoding_issues("run", ["shoes &amp; boots"])
        assert len(results) == 1
        assert not results[0].passed
        assert "HTML entities" in results[0].detail

    def test_control_character(self) -> None:
        results = check_encoding_issues("run", ["running\x00shoes"])
        assert len(results) == 1
        assert not results[0].passed
        assert "control characters" in results[0].detail

    def test_leading_whitespace(self) -> None:
        results = check_encoding_issues("run", [" running shoes"])
        assert len(results) == 1
        assert not results[0].passed
        assert "whitespace" in results[0].detail

    def test_trailing_whitespace(self) -> None:
        results = check_encoding_issues("run", ["running shoes "])
        assert len(results) == 1
        assert not results[0].passed

    def test_empty_list(self) -> None:
        results = check_encoding_issues("run", [])
        assert len(results) == 0


class TestLengthAnomalies:
    def test_normal_length(self) -> None:
        results = check_length_anomalies("run", ["running shoes"])
        assert len(results) == 0

    def test_too_short(self) -> None:
        results = check_length_anomalies("r", ["x"])
        assert len(results) == 1
        assert not results[0].passed
        assert "too short" in results[0].detail

    def test_too_long(self) -> None:
        long_suggestion = "a" * 81
        results = check_length_anomalies("run", [long_suggestion])
        assert len(results) == 1
        assert not results[0].passed
        assert "too long" in results[0].detail

    def test_boundary_valid(self) -> None:
        # 2 chars and 80 chars should pass
        results = check_length_anomalies("r", ["ab", "a" * 80])
        assert len(results) == 0

    def test_empty_list(self) -> None:
        results = check_length_anomalies("run", [])
        assert len(results) == 0


class TestLatency:
    def test_within_threshold(self) -> None:
        result = check_latency("run", 150.0)
        assert result.passed
        assert result.check_name == "latency"

    def test_exceeds_threshold(self) -> None:
        result = check_latency("run", 250.0)
        assert not result.passed
        assert "exceeds" in result.detail

    def test_at_threshold(self) -> None:
        result = check_latency("run", 200.0)
        assert result.passed

    def test_custom_threshold(self) -> None:
        result = check_latency("run", 150.0, threshold_ms=100.0)
        assert not result.passed

    def test_zero_latency(self) -> None:
        result = check_latency("run", 0.0)
        assert result.passed
