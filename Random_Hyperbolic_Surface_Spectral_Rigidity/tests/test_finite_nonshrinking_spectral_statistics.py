# created: 2026-05-16T23:46:00Z
# cycle: 45
# run_id: run-2026-05-15T153635Z
# agent: worker
# milestone: M34-finite-nonshrinking-spectral-statistics

from __future__ import annotations

import csv
import math
from pathlib import Path

import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.analyze_finite_nonshrinking_spectral_statistics import (  # noqa: E402
    CLASSIFICATION_PATH,
    EDGE,
    THRESHOLDS_PATH,
    build_classification_rows,
    build_threshold_rows,
    edge_window_asym,
    f_prime,
    f_profile,
    f_window,
)


def test_f_prime_formula_matches_finite_difference() -> None:
    for lam in [0.31, 1.0, 4.0, 100.0]:
        h = 1e-5 * max(lam, 1.0)
        finite_diff = (f_profile(lam + h) - f_profile(lam - h)) / (2.0 * h)
        assert abs(finite_diff - f_prime(lam)) < 8e-4
    assert f_prime(EDGE) == 0.0


def test_edge_expansion_begins_with_delta_three_halves() -> None:
    for delta in [1e-3, 3e-4, 1e-4]:
        exact = f_window(EDGE, EDGE + delta)
        assert abs(exact / delta**1.5 - math.pi / 3.0) < 0.02
        assert edge_window_asym(delta) > 0.0


def test_fixed_positive_width_windows_have_order_n_main_term() -> None:
    rows = build_threshold_rows()
    fixed_rows = [row for row in rows if row["width_kind"] == "fixed"]
    assert fixed_rows
    assert all(float(row["F_b_minus_F_a"]) > 0.0 for row in fixed_rows)
    assert all(float(row["main_term_n_exponent"]) == 1.0 for row in fixed_rows)
    assert any(row["regime"] == "bulk" for row in fixed_rows)
    assert any(row["regime"] == "edge_adjacent" for row in fixed_rows)
    assert any(row["regime"] == "high_energy" for row in fixed_rows)


def test_shrinking_rows_are_rejected_or_outside_scope() -> None:
    rows = build_threshold_rows()
    shrinking_rows = [row for row in rows if row["width_kind"] == "shrinking"]
    assert shrinking_rows
    assert all(row["classification"] == "requires_new_variance_input" for row in shrinking_rows)
    assert all(row["decision"] == "exclude_from_m34" for row in shrinking_rows)


def test_no_distributional_or_local_universality_claims() -> None:
    rows = build_classification_rows()
    forbidden_claim_ids = {
        "variance_asymptotics",
        "limiting_distribution",
        "level_repulsion_or_universality",
    }
    by_id = {row["claim_id"]: row for row in rows}
    assert forbidden_claim_ids <= set(by_id)
    for claim_id in forbidden_claim_ids:
        assert by_id[claim_id]["decision"] == "no_claim"
    assert not any("Poisson" in row["evidence"] for row in rows)


def test_generated_csvs_preserve_scope_classifications() -> None:
    if not THRESHOLDS_PATH.exists() or not CLASSIFICATION_PATH.exists():
        test_shrinking_rows_are_rejected_or_outside_scope()
        test_no_distributional_or_local_universality_claims()
        return
    with THRESHOLDS_PATH.open() as handle:
        threshold_rows = list(csv.DictReader(handle))
    with CLASSIFICATION_PATH.open() as handle:
        classification_rows = list(csv.DictReader(handle))
    assert any(row["classification"] == "theorem_level_corollary" for row in threshold_rows)
    assert any(row["classification"] == "requires_new_variance_input" for row in threshold_rows)
    assert any(row["classification"] == "not_claimed" for row in classification_rows)
    assert not any(row["decision"] == "claim_local_statistics" for row in classification_rows)


if __name__ == "__main__":
    test_f_prime_formula_matches_finite_difference()
    test_edge_expansion_begins_with_delta_three_halves()
    test_fixed_positive_width_windows_have_order_n_main_term()
    test_shrinking_rows_are_rejected_or_outside_scope()
    test_no_distributional_or_local_universality_claims()
    test_generated_csvs_preserve_scope_classifications()
    print("all finite nonshrinking spectral statistics tests passed")
