# created: 2026-05-16T10:20:00Z
# cycle: 23
# run_id: run-2026-05-15T153635Z
# agent: worker
# milestone: M12-restricted-aggregate-theorem-template
"""Tests for the M12 restricted aggregate theorem-template checker."""

from __future__ import annotations

import csv
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import analyze_restricted_aggregate_theorem_template as m12  # noqa: E402
import enumerate_trace_like_weighted_quotients as m11  # noqa: E402


def rows_for(rows: list[dict[str, str]], **filters: str) -> list[dict[str, str]]:
    return [row for row in rows if all(row[key] == value for key, value in filters.items())]


def test_coefficient_sums_are_stratified_by_n_power() -> None:
    records = m11.build_pair_records(max_len=3)
    strata = m12.build_strata_rows(records)
    rows = rows_for(strata, L="3", variant="all_conflict_free", weight_scheme="weight_unweighted")
    assert len({row["n_power"] for row in rows}) >= 2
    stratified_sum = sum(float(row["coeff_order_1"]) for row in rows)
    global_sum = sum(
        m11.pair_weights(record)["weight_unweighted"] * float(m11.profile_coefficients(record.skeleton)[1])
        for record in records
        if record.L == 3 and m11.record_in_variant(record, "all_conflict_free")
    )
    assert abs(stratified_sum - global_sum) < 1e-9


def test_diagonal_subtracted_tv_equals_all_minus_diagonal_by_stratum() -> None:
    records = m11.build_pair_records(max_len=5)
    strata = m12.build_strata_rows(records)
    keys = {
        (row["L"], row["weight_scheme"], row["n_power"])
        for row in strata
        if row["variant"] in {"all_conflict_free", "diagonal_cyclic_only", "signed_diagonal_subtracted_proxy"}
    }
    for L, scheme, d in keys:
        all_tv = sum(float(row["weight_l1"]) for row in rows_for(strata, L=L, variant="all_conflict_free", weight_scheme=scheme, n_power=d))
        diagonal_tv = sum(float(row["weight_l1"]) for row in rows_for(strata, L=L, variant="diagonal_cyclic_only", weight_scheme=scheme, n_power=d))
        signed_tv = sum(float(row["weight_l1"]) for row in rows_for(strata, L=L, variant="signed_diagonal_subtracted_proxy", weight_scheme=scheme, n_power=d))
        assert abs(signed_tv - (all_tv - diagonal_tv)) < 1e-6


def test_hand_built_cancellation_has_zero_actual_and_positive_tv() -> None:
    L = 4
    order = 1
    coeff = -3.0
    weights = [2.0, -2.0]
    actual = sum(weight * coeff for weight in weights)
    tv = sum(abs(weight) for weight in weights)
    bound = (L ** (2 * order)) * tv
    assert actual == 0.0
    assert tv > 0.0
    assert bound > 0.0


def test_bound_check_ratios_are_finite_and_nonnegative() -> None:
    records = m11.build_pair_records(max_len=4)
    bounds = m12.build_bound_rows(m12.build_strata_rows(records))
    assert bounds
    for row in bounds:
        ratio = float(row["empirical_ratio"])
        assert ratio >= 0.0
        assert ratio < float("inf")


def test_report_referenced_csv_columns_exist() -> None:
    m12.main()
    with m12.STRATA_CSV.open(newline="") as f:
        strata_header = set(next(csv.DictReader(f)).keys())
    with m12.BOUND_CSV.open(newline="") as f:
        bound_header = set(next(csv.DictReader(f)).keys())
    assert {"L", "variant", "weight_scheme", "n_power", "weight_l1", "coeff_order_1"} <= strata_header
    assert {"L", "variant", "weight_scheme", "n_power", "coefficient_order", "empirical_ratio"} <= bound_header


if __name__ == "__main__":
    test_coefficient_sums_are_stratified_by_n_power()
    test_diagonal_subtracted_tv_equals_all_minus_diagonal_by_stratum()
    test_hand_built_cancellation_has_zero_actual_and_positive_tv()
    test_bound_check_ratios_are_finite_and_nonnegative()
    test_report_referenced_csv_columns_exist()
    print("all restricted aggregate theorem-template tests passed")
