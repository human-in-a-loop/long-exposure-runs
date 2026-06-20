# created: 2026-05-16T15:10:00Z
# cycle: 29
# run_id: run-2026-05-15T153635Z
# agent: worker
# milestone: M18-test-function-localization-feasibility
"""Tests for M18 test-function localization tradeoff analysis."""

from __future__ import annotations

import csv
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import analyze_test_function_localization_tradeoffs as m18  # noqa: E402


def test_delta_r_exact_and_bulk_approximation() -> None:
    lam = 4.0
    coarse = 1e-2
    fine = 1e-5
    exact_fine = m18.exact_delta_r(lam, fine)
    assert exact_fine == (lam + fine - 0.25) ** 0.5 - (lam - 0.25) ** 0.5
    coarse_rel = abs(m18.bulk_delta_r_approx(lam, coarse) / m18.exact_delta_r(lam, coarse) - 1.0)
    fine_rel = abs(m18.bulk_delta_r_approx(lam, fine) / exact_fine - 1.0)
    assert fine_rel < coarse_rel


def test_required_support_increases_as_delta_decreases() -> None:
    lam = 1.0
    coarse_exp = m18.r_required_exponent("compact_support_R_inverse_width", 0.01, lam, 1e-2)
    fine_exp = m18.r_required_exponent("compact_support_R_inverse_width", 0.2, lam, 1e-2)
    assert fine_exp > coarse_exp


def test_edge_inverse_width_uses_square_root_scale() -> None:
    edge_exp = m18.r_required_exponent("compact_support_R_inverse_width", 0.2, 0.25, 10 ** (-6 * 0.2))
    bulk_exp = m18.r_required_exponent("compact_support_R_inverse_width", 0.2, 4.0, 10 ** (-6 * 0.2))
    assert abs(edge_exp - 0.1) < 1e-12
    assert abs(bulk_exp - 0.2) < 1e-12


def test_edge_regime_does_not_use_bulk_classification() -> None:
    assert m18.classify_regime(0.25, 1e-4) == "edge_or_transition"
    assert m18.classify_regime(0.250001, 1e-4) == "edge_or_transition"
    assert m18.bulk_delta_r_approx(0.25, 1e-4) == float("inf")


def test_trace_and_pretrace_loss_proxies_are_generated() -> None:
    rows = m18.build_rows()
    sides = {row["architecture_side"] for row in rows}
    assert {"trace_2kappa", "pretrace_4kappa"} <= sides


def test_generated_csv_contains_distinct_scales() -> None:
    if not m18.OUT_CSV.exists():
        m18.main()
    with m18.OUT_CSV.open() as handle:
        rows = list(csv.DictReader(handle))
    assert rows
    required = {
        "Delta_exponent_d",
        "r_width_exact",
        "support_exponent_R_n_power",
        "architecture_side",
        "markov_loss_exponent_proxy",
    }
    assert required <= set(rows[0])
    assert "Lambda0^(-1/2) q" in rows[0]["paper_q_dependency"]


if __name__ == "__main__":
    test_delta_r_exact_and_bulk_approximation()
    test_required_support_increases_as_delta_decreases()
    test_edge_inverse_width_uses_square_root_scale()
    test_edge_regime_does_not_use_bulk_classification()
    test_trace_and_pretrace_loss_proxies_are_generated()
    test_generated_csv_contains_distinct_scales()
    print("all test-function localization tradeoff tests passed")
