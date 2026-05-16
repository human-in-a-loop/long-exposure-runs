# created: 2026-05-16T16:08:00Z
# cycle: 30
# run_id: run-2026-05-15T153635Z
# agent: worker
# milestone: M19-smoothed-window-paley-wiener-lemma
"""Tests for M19 smoothed-window leakage diagnostics."""

from __future__ import annotations

import csv
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import analyze_smoothed_window_leakage as m19  # noqa: E402


def test_tail_proxies_decrease_with_scaled_support() -> None:
    xs = [0.1, 1.0, 4.0]
    for kernel in ["gaussian_fourier_tail", "exponential_tail_proxy", "compact_fejer_transition_proxy"]:
        vals = [m19.leakage_proxy(kernel, x) for x in xs]
        assert vals[0] > vals[1] >= vals[2]


def test_logarithmic_support_fails_for_fixed_positive_d() -> None:
    for d in [0.002, 0.01, 0.1]:
        assert m19.asymptotic_relation(0.0, d, "log_n") == "goes_to_zero"
        assert m19.classification("log_n", 0.0, d) == "negative obstruction"


def test_edge_uses_half_exponent() -> None:
    assert m19.delta_r_exponent("edge", 0.2) == 0.1
    assert m19.delta_r_exponent("bulk", 0.2) == 0.2
    assert m19.delta_r_exponent("high_energy", 0.2) == 0.2


def test_polynomial_support_resolves_bulk_exactly_when_eta_at_least_d() -> None:
    d = 0.05
    assert m19.asymptotic_relation(0.04, d, "n_eta") == "goes_to_zero"
    assert m19.asymptotic_relation(0.05, d, "n_eta") == "stays_bounded"
    assert m19.asymptotic_relation(0.06, d, "n_eta") == "goes_to_infinity"


def test_generated_csv_contains_required_columns() -> None:
    if not m19.OUT_CSV.exists():
        m19.main()
    with m19.OUT_CSV.open() as handle:
        rows = list(csv.DictReader(handle))
    assert rows
    required = {
        "delta_r_exponent",
        "R_delta_exponent",
        "leakage_proxy",
        "resolved_flag",
        "small_leakage_flag",
        "classification",
    }
    assert required <= set(rows[0])


if __name__ == "__main__":
    test_tail_proxies_decrease_with_scaled_support()
    test_logarithmic_support_fails_for_fixed_positive_d()
    test_edge_uses_half_exponent()
    test_polynomial_support_resolves_bulk_exactly_when_eta_at_least_d()
    test_generated_csv_contains_required_columns()
    print("all smoothed-window leakage tests passed")
