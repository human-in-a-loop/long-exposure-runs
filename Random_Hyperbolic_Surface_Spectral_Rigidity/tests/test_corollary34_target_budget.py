# created: 2026-05-16T17:53:00Z
# cycle: 33
# run_id: run-2026-05-15T153635Z
# agent: worker
# milestone: M22-trace-corollary34-uniform-coefficient-variation-target

from __future__ import annotations

import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from analyze_corollary34_target_budget import (  # noqa: E402
    BUDGET_CSV,
    Target,
    candidate_beta,
    endpoint_beating,
    required_beta,
    support_valid,
)


def test_required_beta_formula() -> None:
    assert abs(required_beta(5.0, 0.05, 0.08) - (2.0 * 5.0 * 0.08 + 2.0 * 0.05 - 1.0)) < 1e-12


def test_support_invalid_when_eta_less_than_d() -> None:
    assert not support_valid(0.08, 0.05)
    assert support_valid(0.05, 0.08)


def test_endpoint_requires_strictly_larger_than_alpha_w() -> None:
    assert not endpoint_beating(0.006, 0.006)
    assert endpoint_beating(0.008, 0.006)


def test_direct_small_x_saving_monotone_in_sigma() -> None:
    eta = 0.08
    low = candidate_beta(5.0, eta, Target("direct_small_x", "low", 0.0, 0.25))
    high = candidate_beta(5.0, eta, Target("direct_small_x", "high", 0.0, 0.75))
    assert high > low


def test_markov_baseline_fails_positive_required_beta_rows() -> None:
    rows = []
    with BUDGET_CSV.open() as f:
        for row in csv.DictReader(f):
            if row["target_label"] == "baseline A=2k":
                rows.append(row)
    positives = [
        row
        for row in rows
        if row["support_valid"] == "True"
        and row["endpoint_beating"] == "True"
        and float(row["required_beta"]) > 0.0
    ]
    assert positives
    assert all(row["local_window_success"] == "False" for row in positives)


def test_generated_csv_contains_required_columns() -> None:
    with BUDGET_CSV.open() as f:
        header = set(next(csv.DictReader(f)).keys())
    required = {
        "support_valid",
        "endpoint_beating",
        "required_beta",
        "candidate_beta",
        "local_window_success",
        "target_type",
        "failure_reason",
    }
    assert required <= header


def main() -> None:
    test_required_beta_formula()
    test_support_invalid_when_eta_less_than_d()
    test_endpoint_requires_strictly_larger_than_alpha_w()
    test_direct_small_x_saving_monotone_in_sigma()
    test_markov_baseline_fails_positive_required_beta_rows()
    test_generated_csv_contains_required_columns()
    print("all corollary34 target budget tests passed")


if __name__ == "__main__":
    main()
