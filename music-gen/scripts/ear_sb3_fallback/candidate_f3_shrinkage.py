#!/usr/bin/env python3
"""F3 — conditional-η² with variance shrinkage per Nakagawa-Cuthill.

Motivation. F1 shrinks the DENOMINATOR only. F3 shrinks the NUMERATOR too:
the group means are shrunk toward the grand mean by a factor that depends
on the group size (James-Stein-like). Small groups (n_g = 1) barely
contribute; big groups contribute in full.

Statistic:

    grand   = mean(residuals)
    for each group g:
        mean_g^shrunk = w_g * mean_g(r) + (1 - w_g) * grand
        w_g = n_g / (n_g + k_shrink)
    B'      = sum over groups g of n_g * (mean_g^shrunk - grand)^2
    V_pool  = sum over songs i of (r_i - grand)^2
    S_F3    = B' / V_pool   (clamped to [0,1])

k_shrink is the Nakagawa-Cuthill small-cell prior, k_shrink = median group
size = ceil(N/G). On singleton corpora with N=G=43, k_shrink = 1, so
w_g = 1/(1+1) = 0.5, and the shrunk group means capture only half the
per-song deviation — B' == V_pool * 0.25. That gives a fixed baseline
value of 0.25 under H0, well below saturation.

On repeat-artist corpora (n_g = 5), w_g = 5/(5+5) = 0.5 (same shrinkage
weight because k_shrink scales with median n_g), and B' / V_pool
follows the same distribution shape as η² but bounded well away from 1.

Returns a scalar in [0, 1].
"""
from __future__ import annotations

import math
import sys
from typing import Sequence

if sys.executable != "/usr/bin/python3":
    raise RuntimeError(
        f"Interpreter guard: expected /usr/bin/python3, got {sys.executable}"
    )


def _mean(xs: Sequence[float]) -> float:
    return sum(xs) / len(xs) if xs else 0.0


def f3_statistic(residuals: Sequence[float], artist_ids: Sequence[int]) -> float:
    """Nakagawa-Cuthill-shrunk conditional-η² statistic in [0,1]."""
    if len(residuals) != len(artist_ids):
        raise ValueError("length mismatch")
    if not residuals:
        return 0.0

    n = len(residuals)
    grand = _mean(residuals)
    v_pool = sum((r - grand) ** 2 for r in residuals)
    if v_pool < 1e-12:
        return 0.0

    groups: dict[int, list[float]] = {}
    for r, a in zip(residuals, artist_ids):
        groups.setdefault(a, []).append(r)

    g = len(groups)
    k_shrink = math.ceil(n / g)  # median-ish group size

    b_prime = 0.0
    for xs in groups.values():
        n_g = len(xs)
        w = n_g / (n_g + k_shrink)
        m_g = _mean(xs)
        m_g_shrunk = w * m_g + (1.0 - w) * grand
        b_prime += n_g * (m_g_shrunk - grand) ** 2

    s = b_prime / v_pool
    # Clamp — B'/V_pool can rarely exceed 1 by rounding for large signals.
    if s < 0.0:
        return 0.0
    if s > 1.0:
        return 1.0
    return s


if __name__ == "__main__":
    # Smoke: singleton residuals — B' == V_pool * w^2 == V_pool * 0.25 exactly.
    # Because for singleton corpora each observation IS its group, so
    # mean_g == r_i, shrunk mean = 0.5 * r_i + 0.5 * grand.
    # Deviation from grand = 0.5 * (r_i - grand).
    # B' = sum of (0.5)^2 * (r_i - grand)^2 = 0.25 * V_pool.
    residuals = [1.0, 2.0, 3.0, 4.0, 5.0]
    ids_single = [0, 1, 2, 3, 4]
    s = f3_statistic(residuals, ids_single)
    print(f"singleton smoke S_F3 = {s:.6f}  (expected 0.25)")
    assert abs(s - 0.25) < 1e-9

    ids_rep = [0, 0, 1, 1, 1]
    s2 = f3_statistic(residuals, ids_rep)
    print(f"repeat smoke S_F3 = {s2:.6f}")
    print("F3 smoke OK")
