# created: 2026-05-16T13:36:00Z
# cycle: 27
# run_id: run-2026-05-15T153635Z
# agent: worker
# milestone: M16-local-spectral-window-corollaries
"""Tests for M16 local spectral-window threshold analysis."""

from __future__ import annotations

import csv
import math
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import analyze_local_window_thresholds as m16  # noqa: E402


def test_density_formula_matches_numerical_derivative_away_from_edge() -> None:
    for lam in [0.5, 1.0, 4.0, 25.0]:
        h = 1e-6 * max(1.0, lam)
        numeric = (m16.spectral_F(lam + h) - m16.spectral_F(lam - h)) / (2.0 * h)
        exact = m16.spectral_density(lam)
        assert abs(numeric - exact) < 1e-7


def test_edge_density_tends_to_zero() -> None:
    values = [m16.spectral_density(0.25 + 10.0 ** (-k)) for k in [2, 4, 6, 8]]
    assert values == sorted(values, reverse=True)
    assert values[-1] < 2e-4
    assert m16.spectral_density(0.25) == 0.0


def test_bulk_threshold_improves_as_n_minus_alpha_w() -> None:
    alpha_w = 0.006
    delta1 = m16.bulk_delta_approx(4.0, genus=2, alpha_w=alpha_w, epsilon=0.1, n=10**6)
    delta2 = m16.bulk_delta_approx(4.0, genus=2, alpha_w=alpha_w, epsilon=0.1, n=10**12)
    expected = (10**12 / 10**6) ** (-alpha_w)
    assert abs((delta2 / delta1) / expected - 1.0) < 1e-12


def test_edge_threshold_uses_two_thirds_alpha_w_scaling() -> None:
    alpha_w = 0.5
    delta1 = m16.weyl_delta_threshold(0.25, genus=2, alpha_w=alpha_w, epsilon=0.1, n=10**8)
    delta2 = m16.weyl_delta_threshold(0.25, genus=2, alpha_w=alpha_w, epsilon=0.1, n=10**16)
    expected = (10**16 / 10**8) ** (-2.0 * alpha_w / 3.0)
    assert abs((delta2 / delta1) / expected - 1.0) < 0.03


def test_generated_csvs_contain_edge_bulk_and_high_energy_regimes() -> None:
    if not m16.THRESHOLD_CSV.exists() or not m16.SUMMARY_CSV.exists():
        m16.main()
    with m16.THRESHOLD_CSV.open() as handle:
        threshold_rows = list(csv.DictReader(handle))
    regimes = {row["regime"] for row in threshold_rows}
    assert {"edge", "bulk", "high_energy"} <= regimes
    with m16.SUMMARY_CSV.open() as handle:
        summary_rows = list(csv.DictReader(handle))
    summary_regimes = {row["regime"] for row in summary_rows}
    assert {"edge", "moderate_bulk", "high_energy"} <= summary_regimes


if __name__ == "__main__":
    test_density_formula_matches_numerical_derivative_away_from_edge()
    test_edge_density_tends_to_zero()
    test_bulk_threshold_improves_as_n_minus_alpha_w()
    test_edge_threshold_uses_two_thirds_alpha_w_scaling()
    test_generated_csvs_contain_edge_bulk_and_high_energy_regimes()
    print("all local window threshold tests passed")
