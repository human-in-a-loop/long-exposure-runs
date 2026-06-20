# created: 2026-05-16T16:36:00Z
# cycle: 31
# run_id: run-2026-05-15T153635Z
# agent: worker
# milestone: M20-long-support-trace-variance-requirement
"""Tests for M20 long-support variance budget analysis."""

from __future__ import annotations

import csv
import statistics
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import analyze_long_support_variance_budget as m20  # noqa: E402


def test_required_support_increases_with_window_exponent() -> None:
    assert m20.support_requirement("bulk", 0.02) > m20.support_requirement("bulk", 0.01)
    assert m20.support_requirement("edge", 0.02) > m20.support_requirement("edge", 0.01)


def test_trace_loss_is_half_pretrace_loss() -> None:
    q_exp = 0.02
    kappa = 5.0
    trace = m20.loss_exponent("trace", kappa, q_exp)
    pretrace = m20.loss_exponent("pretrace", kappa, q_exp)
    assert trace == 0.5 * pretrace


def test_chebyshev_pass_fail_matches_inequality() -> None:
    mean = m20.mean_exponent("bulk", 0.1)
    assert m20.chebyshev_passes(2.0 * mean - 0.01, mean)
    assert not m20.chebyshev_passes(2.0 * mean, mean)
    assert not m20.chebyshev_passes(2.0 * mean + 0.01, mean)


def test_endpoint_beating_bulk_rows_require_d_above_alpha_w() -> None:
    rows = m20.build_rows()
    bulk = [r for r in rows if r["regime"] == "bulk"]
    assert all((float(r["Delta_exponent_d"]) > m20.ALPHA_W) == (r["beats_endpoint"] == "true") for r in bulk)


def test_edge_support_and_mean_exponents() -> None:
    d = 0.2
    assert abs(m20.support_requirement("edge", d) - 0.1) < 1e-12
    assert abs(m20.mean_exponent("edge", d) - 0.7) < 1e-12


def test_generated_csv_contains_required_columns() -> None:
    if not m20.OUT_CSV.exists():
        m20.main()
    with m20.OUT_CSV.open() as handle:
        rows = list(csv.DictReader(handle))
    assert rows
    required = {
        "support_requirement_met",
        "q_exponent",
        "loss_exponent",
        "mean_exponent",
        "required_beta",
        "beats_endpoint",
        "feasibility_class",
    }
    assert required <= set(rows[0])


def test_summary_uses_true_median_for_even_endpoint_sets() -> None:
    rows = m20.build_rows()
    summary = m20.build_summary(rows)
    target_rows = [
        r for r in rows
        if r["regime"] == "edge"
        and r["architecture"] == "pretrace"
        and r["kappa"] == "5"
        and r["beats_endpoint"] == "true"
        and r["support_requirement_met"] == "true"
    ]
    target_summary = next(
        r for r in summary
        if r["regime"] == "edge" and r["architecture"] == "pretrace" and r["kappa"] == "5"
    )
    expected = statistics.median(float(r["required_beta"]) for r in target_rows)
    assert abs(float(target_summary["median_required_beta_endpoint_support_met"]) - expected) < 1e-12


if __name__ == "__main__":
    test_required_support_increases_with_window_exponent()
    test_trace_loss_is_half_pretrace_loss()
    test_chebyshev_pass_fail_matches_inequality()
    test_endpoint_beating_bulk_rows_require_d_above_alpha_w()
    test_edge_support_and_mean_exponents()
    test_generated_csv_contains_required_columns()
    test_summary_uses_true_median_for_even_endpoint_sets()
    print("all long-support variance budget tests passed")
