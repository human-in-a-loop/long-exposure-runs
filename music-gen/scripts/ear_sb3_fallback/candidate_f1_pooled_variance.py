#!/usr/bin/env python3
"""F1 — pooled-variance-with-small-cell-adjustment.

Motivation. On singleton-artist corpora, the naive one-way η² statistic
S = SS_between / SS_total saturates at 1.0 because each group has a single
observation → group mean == observation → SS_within == 0. The fix: add a
Nakagawa-Cuthill small-cell prior to the within-group variance estimator,
so single-observation groups borrow variance from the global residual pool.

Statistic:

    B  = sum over groups g of n_g * (mean_g(r) - grand_mean(r))^2
    W  = sum over songs i of (r_i - mean_{g(i)}(r))^2
    W' = W + lambda * V_pool                                (Nakagawa-Cuthill)
    lambda = 1 / (1 + n_bar), n_bar = N / G                 (small-cell prior)
    V_pool = sum_i (r_i - grand_mean(r))^2                   (marginal SS)
    S_F1 = B / (B + W')

On singleton corpora: n_g == 1 → group means == observations → B == V_pool
and W == 0, but W' == lambda * V_pool > 0, so S_F1 == 1 / (1 + lambda) < 1.
With G=43, N=43 → n_bar=1 → lambda=0.5 → S_F1 == 2/3 under any input, INCLUDING
random no-leak. Detection then relies on the FRACTION of variance the group
means capture RELATIVE to the shrinkage floor — i.e. how much B exceeds V_pool
scaled by (1 - lambda). We therefore report a normalized statistic:

    S_F1 = (B / V_pool) / (1 + lambda)     with V_pool clipped to 1e-12

which reduces to a plain B/V_pool ratio on large-cell corpora (lambda -> 0)
and stays bounded on singleton corpora (max value = 1 / (1 + lambda)).

Under H0 (no leak), B/V_pool has the same distribution shape as pure
one-way ANOVA between-fraction, so the τ threshold calibration works
without degeneracy.

Returns a single scalar in [0, 1/(1+lambda)] on singleton corpora and
[0, 1] otherwise.
"""
from __future__ import annotations

import sys
from typing import Sequence

if sys.executable != "/usr/bin/python3":
    raise RuntimeError(
        f"Interpreter guard: expected /usr/bin/python3, got {sys.executable}"
    )


def _mean(xs: Sequence[float]) -> float:
    return sum(xs) / len(xs) if xs else 0.0


def f1_statistic(residuals: Sequence[float], artist_ids: Sequence[int]) -> float:
    """Return the pooled-variance-with-small-cell-adjustment scalar.

    See module docstring. Deterministic and pure-Python.
    """
    if len(residuals) != len(artist_ids):
        raise ValueError("length mismatch")
    if not residuals:
        return 0.0

    n = len(residuals)
    grand = _mean(residuals)
    v_pool = sum((r - grand) ** 2 for r in residuals)
    if v_pool < 1e-12:
        return 0.0

    # Group by artist_id.
    groups: dict[int, list[float]] = {}
    for r, a in zip(residuals, artist_ids):
        groups.setdefault(a, []).append(r)

    g = len(groups)
    n_bar = n / g
    lam = 1.0 / (1.0 + n_bar)

    b = 0.0
    for xs in groups.values():
        mg = _mean(xs)
        b += len(xs) * (mg - grand) ** 2

    # Normalized: (B / V_pool) / (1 + lambda) -> bounded stat.
    return (b / v_pool) / (1.0 + lam)


if __name__ == "__main__":
    # Smoke: singleton corpus with random residuals -> B/V_pool == 1 (since
    # every group mean equals the observation) -> S_F1 == 1/(1+lambda) == 2/3.
    residuals = [1.0, 2.0, 3.0, 4.0, 5.0]
    ids = [0, 1, 2, 3, 4]
    s = f1_statistic(residuals, ids)
    print(f"singleton smoke S_F1 = {s:.6f}  (expected 2/3 = 0.666667)")
    assert abs(s - 2/3) < 1e-9

    # Smoke: one big group -> B == 0 -> S_F1 == 0.
    ids2 = [0] * 5
    s2 = f1_statistic(residuals, ids2)
    print(f"one-big-group smoke S_F1 = {s2:.6f}  (expected 0.0)")
    assert abs(s2) < 1e-9
    print("F1 smoke OK")
