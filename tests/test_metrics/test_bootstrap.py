"""Tests for BCa bootstrap confidence intervals."""

from __future__ import annotations

import pytest

from veritail.metrics.bootstrap import (
    BootstrapCI,
    PairedBootstrapResult,
    _norm_cdf,
    _norm_ppf,
    bootstrap_ci,
    paired_bootstrap_test,
)


class TestNormCDF:
    def test_zero(self) -> None:
        assert _norm_cdf(0.0) == pytest.approx(0.5, abs=1e-6)

    def test_positive(self) -> None:
        assert _norm_cdf(1.96) == pytest.approx(0.975, abs=1e-3)

    def test_negative(self) -> None:
        assert _norm_cdf(-1.96) == pytest.approx(0.025, abs=1e-3)

    def test_extreme_positive(self) -> None:
        assert _norm_cdf(10.0) == 1.0

    def test_extreme_negative(self) -> None:
        assert _norm_cdf(-10.0) == 0.0

    def test_one_sigma(self) -> None:
        assert _norm_cdf(1.0) == pytest.approx(0.8413, abs=1e-3)


class TestNormPPF:
    def test_median(self) -> None:
        assert _norm_ppf(0.5) == 0.0

    def test_upper_tail(self) -> None:
        assert _norm_ppf(0.975) == pytest.approx(1.96, abs=1e-2)

    def test_lower_tail(self) -> None:
        assert _norm_ppf(0.025) == pytest.approx(-1.96, abs=1e-2)

    def test_boundary_zero(self) -> None:
        assert _norm_ppf(0.0) == -8.0

    def test_boundary_one(self) -> None:
        assert _norm_ppf(1.0) == 8.0

    def test_roundtrip(self) -> None:
        for p in [0.1, 0.25, 0.5, 0.75, 0.9, 0.95, 0.99]:
            z = _norm_ppf(p)
            recovered = _norm_cdf(z)
            assert recovered == pytest.approx(p, abs=1e-3)


class TestBootstrapCI:
    def test_returns_none_for_empty(self) -> None:
        assert bootstrap_ci([]) is None

    def test_returns_none_for_single_value(self) -> None:
        assert bootstrap_ci([0.5]) is None

    def test_identical_values(self) -> None:
        result = bootstrap_ci([0.7, 0.7, 0.7, 0.7, 0.7])
        assert result is not None
        assert result.lower == pytest.approx(0.7)
        assert result.upper == pytest.approx(0.7)

    def test_ci_contains_mean(self) -> None:
        values = [0.1, 0.3, 0.5, 0.7, 0.9, 0.4, 0.6, 0.8, 0.2, 0.35]
        result = bootstrap_ci(values)
        assert result is not None
        mean = sum(values) / len(values)
        assert result.lower <= mean <= result.upper

    def test_ci_width_shrinks_with_more_data(self) -> None:
        import random as stdlib_random

        rng = stdlib_random.Random(123)
        small = [rng.random() for _ in range(10)]
        large = [rng.random() for _ in range(100)]

        ci_small = bootstrap_ci(small)
        ci_large = bootstrap_ci(large)
        assert ci_small is not None
        assert ci_large is not None

        width_small = ci_small.upper - ci_small.lower
        width_large = ci_large.upper - ci_large.lower
        assert width_large < width_small

    def test_deterministic_with_seed(self) -> None:
        values = [0.1, 0.4, 0.7, 0.9, 0.2]
        r1 = bootstrap_ci(values, seed=42)
        r2 = bootstrap_ci(values, seed=42)
        assert r1 is not None
        assert r2 is not None
        assert r1.lower == r2.lower
        assert r1.upper == r2.upper

    def test_different_seed_different_result(self) -> None:
        import random as stdlib_random

        rng = stdlib_random.Random(77)
        values = [rng.random() for _ in range(30)]
        r1 = bootstrap_ci(values, seed=42)
        r2 = bootstrap_ci(values, seed=99)
        assert r1 is not None
        assert r2 is not None
        # With 30 continuous values, different seeds should give different CIs
        assert r1.lower != r2.lower or r1.upper != r2.upper

    def test_lower_le_upper(self) -> None:
        values = [0.0, 0.2, 0.8, 1.0, 0.5]
        result = bootstrap_ci(values)
        assert result is not None
        assert result.lower <= result.upper

    def test_two_values(self) -> None:
        result = bootstrap_ci([0.3, 0.7])
        assert result is not None
        assert result.lower <= result.upper

    def test_all_zeros(self) -> None:
        result = bootstrap_ci([0.0, 0.0, 0.0])
        assert result is not None
        assert result.lower == pytest.approx(0.0)
        assert result.upper == pytest.approx(0.0)

    def test_known_tight_distribution(self) -> None:
        # 50 values very close to 0.5 → tight CI
        values = [0.49 + i * 0.0004 for i in range(50)]
        result = bootstrap_ci(values)
        assert result is not None
        mean = sum(values) / len(values)
        assert result.upper - result.lower < 0.02
        assert result.lower <= mean <= result.upper

    def test_returns_bootstrap_ci_type(self) -> None:
        result = bootstrap_ci([0.1, 0.5, 0.9])
        assert isinstance(result, BootstrapCI)


class TestPairedBootstrapTest:
    def test_returns_none_for_single_pair(self) -> None:
        assert paired_bootstrap_test([0.5], [0.6]) is None

    def test_returns_none_for_empty(self) -> None:
        assert paired_bootstrap_test([], []) is None

    def test_returns_none_for_mismatched_lengths(self) -> None:
        assert paired_bootstrap_test([0.1, 0.2], [0.3]) is None

    def test_identical_inputs_not_significant(self) -> None:
        values = [0.5, 0.6, 0.7, 0.8, 0.9]
        result = paired_bootstrap_test(values, values)
        assert result is not None
        assert result.delta == pytest.approx(0.0)
        assert not result.significant

    def test_large_difference_significant(self) -> None:
        a = [0.1] * 20
        b = [0.9] * 20
        result = paired_bootstrap_test(a, b)
        assert result is not None
        assert result.significant
        assert result.delta == pytest.approx(0.8)
        assert result.p_value < 0.001

    def test_delta_sign_positive(self) -> None:
        a = [0.3, 0.4, 0.5]
        b = [0.6, 0.7, 0.8]
        result = paired_bootstrap_test(a, b)
        assert result is not None
        assert result.delta > 0

    def test_delta_sign_negative(self) -> None:
        a = [0.6, 0.7, 0.8]
        b = [0.3, 0.4, 0.5]
        result = paired_bootstrap_test(a, b)
        assert result is not None
        assert result.delta < 0

    def test_p_value_in_range(self) -> None:
        a = [0.1, 0.5, 0.9, 0.3, 0.7]
        b = [0.2, 0.4, 0.8, 0.6, 0.5]
        result = paired_bootstrap_test(a, b)
        assert result is not None
        assert 0.0 <= result.p_value <= 1.0

    def test_ci_contains_delta(self) -> None:
        a = [0.1, 0.3, 0.5, 0.7, 0.9]
        b = [0.2, 0.4, 0.6, 0.8, 1.0]
        result = paired_bootstrap_test(a, b)
        assert result is not None
        assert result.ci_lower <= result.delta <= result.ci_upper

    def test_deterministic_with_seed(self) -> None:
        a = [0.1, 0.3, 0.5]
        b = [0.2, 0.6, 0.4]
        r1 = paired_bootstrap_test(a, b, seed=42)
        r2 = paired_bootstrap_test(a, b, seed=42)
        assert r1 is not None
        assert r2 is not None
        assert r1.p_value == r2.p_value
        assert r1.ci_lower == r2.ci_lower

    def test_tiny_consistent_difference_not_significant(self) -> None:
        """Reviewer's example: [0.5, 0.5] vs [0.51, 0.51] should NOT be significant.

        With only n=2 and a tiny constant delta, a proper null-hypothesis
        test should yield a high p-value (no evidence to reject H0).
        """
        a = [0.5, 0.5]
        b = [0.51, 0.51]
        result = paired_bootstrap_test(a, b)
        assert result is not None
        assert result.p_value > 0.05
        assert not result.significant

    def test_constant_delta_with_float_residue_not_significant(self) -> None:
        """Constant deltas that differ only by float residue (e.g. 0.2-0.1
        vs 1.0-0.9) should trigger the sign-test fallback, not the bootstrap
        path which would incorrectly return p=0.0.
        """
        a = [0.1, 0.9]
        b = [0.2, 1.0]
        result = paired_bootstrap_test(a, b)
        assert result is not None
        assert result.p_value > 0.05
        assert not result.significant

    def test_small_noisy_difference_not_significant(self) -> None:
        """Mixed small deltas with n=5 should not be significant."""
        a = [0.5, 0.6, 0.4, 0.55, 0.45]
        b = [0.52, 0.58, 0.43, 0.54, 0.47]
        result = paired_bootstrap_test(a, b)
        assert result is not None
        assert not result.significant

    def test_returns_paired_bootstrap_result_type(self) -> None:
        result = paired_bootstrap_test([0.1, 0.5], [0.2, 0.6])
        assert isinstance(result, PairedBootstrapResult)
