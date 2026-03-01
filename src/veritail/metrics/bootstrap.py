"""BCa bootstrap confidence intervals for IR metrics."""

from __future__ import annotations

import math
import random
from dataclasses import dataclass


@dataclass
class BootstrapCI:
    """Bootstrap confidence interval."""

    lower: float
    upper: float


@dataclass
class PairedBootstrapResult:
    """Result of a paired bootstrap significance test."""

    delta: float
    ci_lower: float
    ci_upper: float
    p_value: float
    significant: bool


# ---------------------------------------------------------------------------
# Normal distribution approximations (Abramowitz & Stegun)
# ---------------------------------------------------------------------------


def _norm_cdf(x: float) -> float:
    """Standard normal CDF via A&S erfc approximation (accuracy ~7.5e-8).

    Uses Φ(x) = 0.5·erfc(-x/√2) with Horner-form polynomial for erfc.
    """
    if x < -8.0:
        return 0.0
    if x > 8.0:
        return 1.0

    a1 = 0.254829592
    a2 = -0.284496736
    a3 = 1.421413741
    a4 = -1.453152027
    a5 = 1.061405429
    p = 0.3275911

    z = abs(x) / math.sqrt(2.0)
    t = 1.0 / (1.0 + p * z)
    erfc = t * (a1 + t * (a2 + t * (a3 + t * (a4 + t * a5)))) * math.exp(-z * z)

    if x >= 0:
        return 1.0 - erfc / 2.0
    return erfc / 2.0


def _norm_ppf(p: float) -> float:
    """Standard normal inverse CDF (percent point function).

    Uses the rational approximation from A&S formula 26.2.23 with one
    Newton-Raphson refinement step.  Accuracy ~4.5e-4 before refinement,
    ~1e-8 after.
    """
    if p <= 0.0:
        return -8.0
    if p >= 1.0:
        return 8.0
    if p == 0.5:
        return 0.0

    # Work in the upper half, flip at the end
    if p < 0.5:
        sign = -1.0
        q = 1.0 - p
    else:
        sign = 1.0
        q = p

    # Rational approximation for 0.5 < q < 1
    t = math.sqrt(-2.0 * math.log(1.0 - q))
    c0 = 2.515517
    c1 = 0.802853
    c2 = 0.010328
    d1 = 1.432788
    d2 = 0.189269
    d3 = 0.001308
    x = t - (c0 + c1 * t + c2 * t * t) / (1.0 + d1 * t + d2 * t * t + d3 * t**3)

    # One Newton-Raphson refinement
    err = _norm_cdf(x) - q
    pdf = math.exp(-x * x / 2.0) / math.sqrt(2.0 * math.pi)
    if pdf > 0:
        x = x - err / pdf

    return sign * x


# ---------------------------------------------------------------------------
# Bootstrap CI
# ---------------------------------------------------------------------------

_MIN_SAMPLES = 2


def bootstrap_ci(
    values: list[float],
    n_resamples: int = 10_000,
    confidence: float = 0.95,
    seed: int = 42,
) -> BootstrapCI | None:
    """BCa bootstrap confidence interval on the mean of *values*.

    Returns ``None`` when ``len(values) < 2`` (CI is undefined).
    Uses a fixed *seed* for reproducibility.
    """
    n = len(values)
    if n < _MIN_SAMPLES:
        return None

    observed = sum(values) / n

    # All identical → degenerate CI
    if all(v == values[0] for v in values):
        return BootstrapCI(values[0], values[0])

    rng = random.Random(seed)

    # Generate bootstrap distribution of the mean
    boot_means: list[float] = []
    for _ in range(n_resamples):
        sample = rng.choices(values, k=n)
        boot_means.append(sum(sample) / n)

    boot_means.sort()

    # --- Bias correction (z0) ---
    count_below = sum(1 for m in boot_means if m < observed)
    proportion = count_below / n_resamples
    # Clamp to avoid ±inf
    lo = 1.0 / (n_resamples + 1)
    hi = n_resamples / (n_resamples + 1)
    proportion = max(lo, min(proportion, hi))
    z0 = _norm_ppf(proportion)

    # --- Acceleration (a) via jackknife ---
    jackknife_means: list[float] = []
    total = sum(values)
    for i in range(n):
        jk_mean = (total - values[i]) / (n - 1)
        jackknife_means.append(jk_mean)

    jk_bar = sum(jackknife_means) / n
    diffs = [jk_bar - m for m in jackknife_means]
    num = sum(d**3 for d in diffs)
    denom = sum(d**2 for d in diffs)
    if denom > 0:
        a = num / (6.0 * denom**1.5)
    else:
        a = 0.0

    # --- Adjusted quantiles ---
    alpha = 1.0 - confidence
    z_low = _norm_ppf(alpha / 2.0)
    z_high = _norm_ppf(1.0 - alpha / 2.0)

    def _adjusted_quantile(z_alpha: float) -> float:
        numer = z0 + z_alpha
        denom_adj = 1.0 - a * numer
        if abs(denom_adj) < 1e-12:
            return _norm_cdf(z0 + z_alpha)
        adjusted = z0 + numer / denom_adj
        return _norm_cdf(adjusted)

    q_low = _adjusted_quantile(z_low)
    q_high = _adjusted_quantile(z_high)

    # Clamp quantiles to valid index range
    q_low = max(0.0, min(q_low, 1.0))
    q_high = max(0.0, min(q_high, 1.0))

    idx_low = max(0, min(int(q_low * n_resamples), n_resamples - 1))
    idx_high = max(0, min(int(q_high * n_resamples), n_resamples - 1))

    return BootstrapCI(lower=boot_means[idx_low], upper=boot_means[idx_high])


# ---------------------------------------------------------------------------
# Paired bootstrap significance test
# ---------------------------------------------------------------------------


def paired_bootstrap_test(
    values_a: list[float],
    values_b: list[float],
    n_resamples: int = 10_000,
    alpha: float = 0.05,
    seed: int = 42,
) -> PairedBootstrapResult | None:
    """Paired bootstrap test on aligned per-query metric values.

    Computes per-query deltas (B - A), bootstraps the mean delta, and
    tests whether the confidence interval excludes zero.

    Returns ``None`` when ``len < 2``.
    """
    n = len(values_a)
    if n < _MIN_SAMPLES or len(values_b) != n:
        return None

    deltas = [b - a for a, b in zip(values_a, values_b)]
    observed_delta = sum(deltas) / n

    rng = random.Random(seed)

    boot_deltas: list[float] = []
    for _ in range(n_resamples):
        sample = rng.choices(deltas, k=n)
        boot_deltas.append(sum(sample) / n)

    boot_deltas.sort()

    # CI via percentile method (sufficient for deltas which are ~symmetric)
    lo_idx = max(0, int((alpha / 2.0) * n_resamples))
    hi_idx = min(n_resamples - 1, int((1.0 - alpha / 2.0) * n_resamples))
    ci_lower = boot_deltas[lo_idx]
    ci_upper = boot_deltas[hi_idx]

    # Two-sided p-value: fraction of bootstrap resamples on opposite side of 0
    if observed_delta >= 0:
        count_opposite = sum(1 for d in boot_deltas if d <= 0)
    else:
        count_opposite = sum(1 for d in boot_deltas if d >= 0)
    p_value = min(1.0, 2.0 * count_opposite / n_resamples)

    return PairedBootstrapResult(
        delta=observed_delta,
        ci_lower=ci_lower,
        ci_upper=ci_upper,
        p_value=p_value,
        significant=p_value < alpha,
    )
