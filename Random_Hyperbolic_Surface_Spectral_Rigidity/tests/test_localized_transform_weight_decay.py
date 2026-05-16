# created: 2026-05-16T18:45:00Z
# cycle: 35
# run_id: run-2026-05-15T153635Z
# agent: worker
# milestone: M24-localized-transform-geodesic-weight-decay-obstruction
"""Tests for M24 localized transform/geodesic decay diagnostics."""

from __future__ import annotations

import csv
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import analyze_localized_transform_weight_decay as m24  # noqa: E402


def test_bulk_q_delta_exponent_is_eta_minus_d() -> None:
    assert m24.q_delta_exponent(0.08, 0.03) == 0.05
    assert m24.q_delta_exponent(0.03, 0.08) == -0.05


def test_compact_support_has_no_internal_decay() -> None:
    assert m24.transform_envelope("compact_support_only", 0.01, 10.0) == 1.0
    assert m24.transform_envelope("compact_support_only", 100.0, 10.0) == 1.0


def test_schwartz_envelope_depends_on_scaled_u() -> None:
    small = m24.transform_envelope("smooth_schwartz_scaled", 1.0, 10.0)
    same_u_large_t = m24.transform_envelope("smooth_schwartz_scaled", 1.0, 10_000.0)
    larger_u = m24.transform_envelope("smooth_schwartz_scaled", 10.0, 10.0)
    assert small == same_u_large_t
    assert larger_u < small


def test_bounded_q_delta_has_no_growing_support_scale_damping() -> None:
    eta = d = 0.05
    u_endpoint = m24.N_REF ** m24.q_delta_exponent(eta, d)
    envelope = m24.transform_envelope("smooth_schwartz_scaled", u_endpoint, m24.N_REF**eta)
    assert u_endpoint == 1.0
    assert envelope > 0.0
    assert m24.scaled_damping_exponent("smooth_schwartz_scaled", eta, d) == 0.0


def test_noncompact_gaussian_is_marked_incompatible() -> None:
    assert m24.compatibility("noncompact_gaussian_t_tail") == "incompatible_noncompact_geometric_tail"


def test_noncompact_success_requires_negative_net_growth_balance() -> None:
    rows = m24.build_rows()
    success = [r for r in rows if r["success_row"] == "true"]
    for row in success:
        assert row["m22_support_and_endpoint_conditions"] == "true"
        assert row["compatibility"] == "incompatible_noncompact_geometric_tail"
        assert row["verdict"] == "contrast_success_only"
        assert float(row["net_log10_endpoint_after_growth"]) < 0.0
    insufficient = [r for r in rows if r["verdict"] == "contrast_insufficient"]
    assert insufficient
    for row in insufficient:
        assert float(row["net_log10_endpoint_after_growth"]) >= 0.0


def test_generated_csv_contains_required_columns() -> None:
    if not m24.OUT_CSV.exists():
        m24.main()
    with m24.OUT_CSV.open() as handle:
        rows = list(csv.DictReader(handle))
    assert rows
    required = {
        "q_delta_exponent_eta_minus_d",
        "transform_model",
        "compatibility",
        "growth_model",
        "m22_support_and_endpoint_conditions",
        "verdict",
    }
    assert required <= set(rows[0])


if __name__ == "__main__":
    test_bulk_q_delta_exponent_is_eta_minus_d()
    test_compact_support_has_no_internal_decay()
    test_schwartz_envelope_depends_on_scaled_u()
    test_bounded_q_delta_has_no_growing_support_scale_damping()
    test_noncompact_gaussian_is_marked_incompatible()
    test_noncompact_success_requires_negative_net_growth_balance()
    test_generated_csv_contains_required_columns()
    print("all localized transform weight decay tests passed")
