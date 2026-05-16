# created: 2026-05-16T01:45:00Z
# cycle: 15
# run_id: run-2026-05-15T153635Z
# agent: worker
# milestone: M5-extension-candidates
"""Tests for growing labelled-template expansion diagnostics."""

from __future__ import annotations

import sys
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import plot_growing_template_expansions as grow  # noqa: E402


def exact_value(V: int, counts: list[int], n: int) -> Fraction:
    def falling(value: int, order: int) -> int:
        out = 1
        for j in range(order):
            out *= value - j
        return out

    result = Fraction(n, 1) ** (sum(counts) - V)
    result *= falling(n, V)
    for count in counts:
        result /= falling(n, count)
    return result


def series_value(coeffs: list[Fraction], n: int) -> Fraction:
    x = Fraction(1, n)
    return sum(coeff * x**order for order, coeff in enumerate(coeffs))


def test_single_label_cycle_profile_is_one() -> None:
    for L in (1, 2, 8, 40):
        coeffs = grow.coefficients_for_profile(L, [L])
        assert coeffs == [Fraction(1)] + [Fraction(0)] * grow.MAX_ORDER


def test_single_label_path_profile_is_one_minus_lx() -> None:
    for L in (1, 5, 40):
        coeffs = grow.coefficients_for_profile(L + 1, [L])
        expected = [Fraction(1), Fraction(-L)] + [Fraction(0)] * (grow.MAX_ORDER - 1)
        assert coeffs == expected


def test_truncated_series_matches_exact_to_expected_order() -> None:
    L = 5
    V = 2 * L - 1
    counts = [L, L]
    n = 200
    coeffs = grow.coefficients_for_profile(V, counts)
    exact = exact_value(V, counts, n)
    trunc = series_value(coeffs, n)
    assert abs(exact - trunc) < Fraction(10**8, n ** (grow.MAX_ORDER + 1))


def test_coefficient_extraction_is_deterministic() -> None:
    assert grow.coefficients_for_profile(11, [7, 7]) == grow.coefficients_for_profile(11, [7, 7])


def test_radius_proxy_decreases_for_nontrivial_family() -> None:
    r5 = grow.parse_fraction(grow.nearest_scale("rank2_balanced_profile", 9, [5, 5]))
    r20 = grow.parse_fraction(grow.nearest_scale("rank2_balanced_profile", 39, [20, 20]))
    assert r20 < r5


if __name__ == "__main__":
    test_single_label_cycle_profile_is_one()
    test_single_label_path_profile_is_one_minus_lx()
    test_truncated_series_matches_exact_to_expected_order()
    test_coefficient_extraction_is_deterministic()
    test_radius_proxy_decreases_for_nontrivial_family()
    print("all growing template expansion tests passed")
