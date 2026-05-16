# created: 2026-05-16T14:36:00Z
# cycle: 28
# run_id: run-2026-05-15T153635Z
# agent: worker
# milestone: M17-local-window-variance-input
"""Tests for M17 local-window variance requirement analysis."""

from __future__ import annotations

import csv
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import analyze_local_window_variance_requirements as m17  # noqa: E402


def test_chebyshev_criterion_is_monotone_in_variance() -> None:
    mean_exponent = 0.9
    assert m17.chebyshev_passes(mean_exponent, var_exponent=1.0)
    assert not m17.chebyshev_passes(mean_exponent, var_exponent=1.9)


def test_smaller_delta_lowers_mean_mass() -> None:
    coarse = m17.mean_mass_exponent("bulk", 0.01)
    fine = m17.mean_mass_exponent("bulk", 0.25)
    assert fine < coarse
    edge_coarse = m17.mean_mass_exponent("edge", 0.01)
    edge_fine = m17.mean_mass_exponent("edge", 0.25)
    assert edge_fine < edge_coarse


def test_beats_endpoint_requires_below_m16_threshold() -> None:
    threshold = 0.006
    assert not m17.beats_endpoint(0.004, threshold)
    assert not m17.beats_endpoint(0.006, threshold)
    assert m17.beats_endpoint(0.008, threshold)


def test_analyzer_emits_passing_and_failing_variance_regimes() -> None:
    rows = m17.build_rows()
    useful_values = {row["useful_new_input"] for row in rows}
    pass_values = {row["chebyshev_pass"] for row in rows}
    assert {"true", "false"} <= useful_values
    assert {"true", "false"} <= pass_values


def test_generated_csv_contains_required_columns() -> None:
    if not m17.OUT_CSV.exists():
        m17.main()
    with m17.OUT_CSV.open() as handle:
        rows = list(csv.DictReader(handle))
    assert rows
    required = {
        "regime",
        "Lambda",
        "Delta_exponent",
        "mean_exponent",
        "endpoint_threshold_exponent",
        "variance_exponent",
        "chebyshev_pass",
        "beats_endpoint",
    }
    assert required <= set(rows[0])


if __name__ == "__main__":
    test_chebyshev_criterion_is_monotone_in_variance()
    test_smaller_delta_lowers_mean_mass()
    test_beats_endpoint_requires_below_m16_threshold()
    test_analyzer_emits_passing_and_failing_variance_regimes()
    test_generated_csv_contains_required_columns()
    print("all local window variance requirement tests passed")
