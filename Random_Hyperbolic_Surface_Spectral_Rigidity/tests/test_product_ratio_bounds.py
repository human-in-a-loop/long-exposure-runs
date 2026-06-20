# created: 2026-05-16T05:10:00Z
# cycle: 18
# run_id: run-2026-05-15T153635Z
# agent: worker
# milestone: M7-product-ratio-bounds
"""Tests for M7 product-ratio coefficient bounds."""

from __future__ import annotations

import csv
import sys
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import analyze_product_ratio_bounds as bounds  # noqa: E402


def test_path_profile_log_coefficients() -> None:
    L = 7
    numerator, denominator = bounds.supports_from_profile(L + 1, [L])
    assert bounds.log_coefficient_from_supports(numerator, denominator, 1) == Fraction(-L)
    assert bounds.log_coefficient_from_supports(numerator, denominator, 2) == Fraction(-(L**2), 2)
    assert bounds.log_coefficient_from_supports(numerator, denominator, 3) == Fraction(-(L**3), 3)


def test_rank_two_balanced_small_l() -> None:
    L = 3
    numerator, denominator = bounds.supports_from_profile(2 * L - 1, [L, L])
    assert numerator == [1, 2, 3, 4]
    assert denominator == [1, 2, 1, 2]
    assert bounds.log_coefficient_from_supports(numerator, denominator, 1) == Fraction(-4)
    assert bounds.log_coefficient_from_supports(numerator, denominator, 2) == Fraction(-10)


def test_cancellation_supports_match() -> None:
    for order in range(1, 7):
        assert bounds.log_coefficient_from_supports([1, 2, 3], [1, 2, 3], order) == 0


def test_generated_envelope_ratios_are_finite_and_nonnegative() -> None:
    rows = bounds.build_summary_rows()
    assert rows
    for row in rows:
        ratio = float(row["max_envelope_ratio"])
        slope = float(row["slope_estimate"])
        assert ratio >= 0.0
        assert ratio < float("inf")
        assert slope == slope


def test_cycle15_profile_parsing_is_deterministic() -> None:
    summary_path = ROOT / "data/extension_candidates/growing_template_expansion_summary.csv"
    with summary_path.open(newline="") as f:
        rows = list(csv.DictReader(f))
    rank2_l5 = [row for row in rows if row["family"] == "rank2_balanced_profile" and row["L"] == "5"][0]
    assert bounds.parse_counts(rank2_l5["constraint_counts"]) == [5, 5]
    assert bounds.supports_from_profile(int(rank2_l5["V"]), [5, 5]) == (list(range(1, 9)), [1, 2, 3, 4, 1, 2, 3, 4])


if __name__ == "__main__":
    test_path_profile_log_coefficients()
    test_rank_two_balanced_small_l()
    test_cancellation_supports_match()
    test_generated_envelope_ratios_are_finite_and_nonnegative()
    test_cycle15_profile_parsing_is_deterministic()
    print("all product-ratio bound tests passed")
