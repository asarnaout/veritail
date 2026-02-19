"""Deterministic autocomplete quality checks."""

from __future__ import annotations

import re
import unicodedata

from veritail.types import CheckResult


def _tokenize(text: str) -> set[str]:
    """Lowercase and split text into word tokens."""
    return set(re.findall(r"\w+", text.lower()))


def check_empty_suggestions(prefix: str, suggestions: list[str]) -> CheckResult:
    """Check if the autocomplete returned no suggestions."""
    if not suggestions:
        return CheckResult(
            check_name="empty_suggestions",
            query=prefix,
            product_id=None,
            passed=False,
            detail=f"No suggestions returned for prefix '{prefix}'",
            severity="fail",
        )
    return CheckResult(
        check_name="empty_suggestions",
        query=prefix,
        product_id=None,
        passed=True,
        detail=f"Returned {len(suggestions)} suggestion(s)",
        severity="info",
    )


def check_duplicate_suggestions(
    prefix: str, suggestions: list[str]
) -> list[CheckResult]:
    """Check for duplicate suggestions in the list."""
    checks: list[CheckResult] = []
    seen: dict[str, int] = {}
    for i, s in enumerate(suggestions):
        key = s.lower().strip()
        if key in seen:
            checks.append(
                CheckResult(
                    check_name="duplicate_suggestion",
                    query=prefix,
                    product_id=None,
                    passed=False,
                    detail=(
                        f"Duplicate suggestion '{s}' at position {i} "
                        f"(first seen at position {seen[key]})"
                    ),
                    severity="warning",
                )
            )
        else:
            seen[key] = i
    return checks


def check_prefix_coherence(prefix: str, suggestions: list[str]) -> list[CheckResult]:
    """Verify suggestions contain prefix tokens or start with prefix."""
    checks: list[CheckResult] = []
    prefix_lower = prefix.lower().strip()
    prefix_tokens = _tokenize(prefix)

    for suggestion in suggestions:
        suggestion_lower = suggestion.lower().strip()
        starts_with = suggestion_lower.startswith(prefix_lower)
        suggestion_tokens = _tokenize(suggestion)
        token_overlap = bool(prefix_tokens & suggestion_tokens)

        coherent = starts_with or token_overlap
        checks.append(
            CheckResult(
                check_name="prefix_coherence",
                query=prefix,
                product_id=None,
                passed=coherent,
                detail=(
                    f"Suggestion '{suggestion}' is coherent with prefix '{prefix}'"
                    if coherent
                    else (
                        f"Suggestion '{suggestion}' does not start with or "
                        f"share tokens with prefix '{prefix}'"
                    )
                ),
                severity="info" if coherent else "warning",
            )
        )
    return checks


def check_offensive_content(
    prefix: str,
    suggestions: list[str],
    blocklist: list[str] | None = None,
) -> list[CheckResult]:
    """Check suggestions against an offensive content blocklist."""
    checks: list[CheckResult] = []
    if not blocklist:
        return checks

    blocked_set = {w.lower().strip() for w in blocklist}
    for suggestion in suggestions:
        suggestion_tokens = _tokenize(suggestion)
        matched = suggestion_tokens & blocked_set
        if matched:
            checks.append(
                CheckResult(
                    check_name="offensive_content",
                    query=prefix,
                    product_id=None,
                    passed=False,
                    detail=(
                        f"Suggestion '{suggestion}' contains blocked "
                        f"term(s): {', '.join(sorted(matched))}"
                    ),
                    severity="fail",
                )
            )
    return checks


_HTML_ENTITY_RE = re.compile(r"&[a-zA-Z]+;|&#\d+;|&#x[0-9a-fA-F]+;")


def check_encoding_issues(prefix: str, suggestions: list[str]) -> list[CheckResult]:
    """Detect HTML entities, control characters, and leading/trailing whitespace."""
    checks: list[CheckResult] = []
    for suggestion in suggestions:
        issues: list[str] = []
        if _HTML_ENTITY_RE.search(suggestion):
            issues.append("contains HTML entities")
        if any(
            unicodedata.category(ch).startswith("C") and ch not in ("\t",)
            for ch in suggestion
        ):
            issues.append("contains control characters")
        if suggestion != suggestion.strip():
            issues.append("has leading/trailing whitespace")
        if issues:
            checks.append(
                CheckResult(
                    check_name="encoding_issues",
                    query=prefix,
                    product_id=None,
                    passed=False,
                    detail=(f"Suggestion '{suggestion.strip()}' {'; '.join(issues)}"),
                    severity="warning",
                )
            )
    return checks


def check_length_anomalies(prefix: str, suggestions: list[str]) -> list[CheckResult]:
    """Flag suggestions shorter than 2 chars or longer than 80 chars."""
    checks: list[CheckResult] = []
    for suggestion in suggestions:
        length = len(suggestion.strip())
        if length < 2:
            checks.append(
                CheckResult(
                    check_name="length_anomaly",
                    query=prefix,
                    product_id=None,
                    passed=False,
                    detail=(
                        f"Suggestion '{suggestion}' is too short "
                        f"({length} char(s), min 2)"
                    ),
                    severity="warning",
                )
            )
        elif length > 80:
            checks.append(
                CheckResult(
                    check_name="length_anomaly",
                    query=prefix,
                    product_id=None,
                    passed=False,
                    detail=(
                        f"Suggestion '{suggestion[:40]}...' is too long "
                        f"({length} chars, max 80)"
                    ),
                    severity="warning",
                )
            )
    return checks


def check_latency(
    prefix: str,
    latency_ms: float,
    threshold_ms: float = 200.0,
) -> CheckResult:
    """Check whether adapter response time exceeds a threshold."""
    passed = latency_ms <= threshold_ms
    return CheckResult(
        check_name="latency",
        query=prefix,
        product_id=None,
        passed=passed,
        detail=(
            f"Response time {latency_ms:.0f}ms"
            if passed
            else (
                f"Response time {latency_ms:.0f}ms exceeds "
                f"threshold {threshold_ms:.0f}ms"
            )
        ),
        severity="info" if passed else "warning",
    )
