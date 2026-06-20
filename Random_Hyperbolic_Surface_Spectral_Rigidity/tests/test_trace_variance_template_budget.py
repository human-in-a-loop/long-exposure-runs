# created: 2026-05-16T17:22:00Z
# cycle: 32
# run_id: run-2026-05-15T153635Z
# agent: worker
# milestone: M21-trace-side-long-support-variance-template
"""Tests for the M21 trace-side variance theorem-template budget."""

from __future__ import annotations

import csv
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import analyze_trace_variance_template_budget as m21  # noqa: E402


def test_local_success_requires_endpoint_and_beta_threshold() -> None:
    rows = m21.build_rows()
    success_rows = [r for r in rows if r["local_window_success"] == "true"]
    assert success_rows
    for row in success_rows:
        assert row["endpoint_beating"] == "true"
        assert row["support_valid"] == "true"
        beta_req = m21.required_beta(
            float(row["kappa"]),
            float(row["Delta_exponent_d"]),
            float(row["eta"]),
        )
        assert float(row["hypothetical_beta"]) > beta_req


def test_eta_below_d_is_support_invalid() -> None:
    rows = m21.build_rows()
    for row in rows:
        d = float(row["Delta_exponent_d"])
        eta = float(row["eta"])
        if eta < d:
            assert row["support_valid"] == "false"


def test_increasing_kappa_increases_required_beta() -> None:
    d = 0.05
    eta = 0.05
    assert m21.required_beta(5.0, d, eta) > m21.required_beta(3.0, d, eta)
    assert m21.required_beta(8.0, d, eta) > m21.required_beta(5.0, d, eta)


def test_no_new_saving_only_succeeds_when_required_beta_negative() -> None:
    rows = [
        r for r in m21.build_rows()
        if r["beta_model"] == "no_new_saving"
        and r["endpoint_beating"] == "true"
        and r["support_valid"] == "true"
    ]
    assert rows
    for row in rows:
        success = row["local_window_success"] == "true"
        beta_req = m21.required_beta(
            float(row["kappa"]),
            float(row["Delta_exponent_d"]),
            float(row["eta"]),
        )
        assert success == (0.0 > beta_req)


def test_generated_csv_contains_required_columns() -> None:
    if not m21.OUT_CSV.exists():
        m21.main()
    with m21.OUT_CSV.open() as handle:
        rows = list(csv.DictReader(handle))
    assert rows
    required = {
        "endpoint_beating",
        "support_valid",
        "required_beta",
        "hypothetical_beta",
        "chebyshev_success",
        "local_window_success",
        "theorem_plausibility_class",
    }
    assert required <= set(rows[0])


if __name__ == "__main__":
    test_local_success_requires_endpoint_and_beta_threshold()
    test_eta_below_d_is_support_invalid()
    test_increasing_kappa_increases_required_beta()
    test_no_new_saving_only_succeeds_when_required_beta_negative()
    test_generated_csv_contains_required_columns()
    print("all trace variance template budget tests passed")
