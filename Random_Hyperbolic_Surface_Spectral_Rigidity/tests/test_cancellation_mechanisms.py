# created: 2026-05-16T11:20:00Z
# cycle: 24
# run_id: run-2026-05-15T153635Z
# agent: worker
# milestone: M13-cancellation-mechanism-diagnostics
"""Tests for M13 cancellation-mechanism diagnostics."""

from __future__ import annotations

import csv
import math
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import analyze_cancellation_mechanisms as m13  # noqa: E402
import enumerate_trace_like_weighted_quotients as m11  # noqa: E402


def rows_for(rows: list[dict[str, str]], **filters: str) -> list[dict[str, str]]:
    return [row for row in rows if all(row[key] == value for key, value in filters.items())]


def test_hand_built_two_template_cancellation_has_zero_rho() -> None:
    stats = m13.summarize_terms([(None, 1.0, 3.0), (None, 1.0, -3.0)], L=2, order=1)  # type: ignore[list-item]
    assert stats["signed_sum"] == 0.0
    assert stats["coeff_abs_variation"] == 6.0
    assert stats["cancellation_ratio"] == 0.0


def test_all_same_sign_example_has_rho_one() -> None:
    stats = m13.summarize_terms([(None, 2.0, -3.0), (None, 1.0, -6.0)], L=2, order=1)  # type: ignore[list-item]
    assert stats["signed_sum"] == -12.0
    assert stats["coeff_abs_variation"] == 12.0
    assert stats["cancellation_ratio"] == 1.0


def test_zero_absolute_variation_is_handled_without_division_error() -> None:
    stats = m13.summarize_terms([(None, 5.0, 0.0)], L=2, order=1)  # type: ignore[list-item]
    assert stats["signed_sum"] == 0.0
    assert stats["coeff_abs_variation"] == 0.0
    assert math.isnan(stats["cancellation_ratio"])


def test_grouped_sums_refine_ungrouped_total() -> None:
    records = m11.build_pair_records(max_len=5)
    coeff_rows = m13.build_coefficient_rows(records)
    group_rows = m13.build_group_rows(records)
    target = rows_for(
        coeff_rows,
        L="5",
        variant="rank_two_noncyclic_remainder",
        weight_scheme="weight_unweighted",
        n_power="1",
        coefficient_order="2",
    )[0]
    for rule in ["length_pair", "rank_cyclic_proxy", "primitive_diagonal_status", "folded_profile_key", "coefficient_sign_vector"]:
        parts = rows_for(
            group_rows,
            grouping_rule=rule,
            L="5",
            variant="rank_two_noncyclic_remainder",
            weight_scheme="weight_unweighted",
            n_power="1",
            coefficient_order="2",
        )
        assert parts
        signed = sum(float(row["signed_coefficient_sum"]) for row in parts)
        assert abs(signed - float(target["signed_coefficient_sum"])) < 1e-9


def test_m11_m12_known_l5_unweighted_d1_values_are_reproduced() -> None:
    records = m11.build_pair_records(max_len=5)
    coeff_rows = m13.build_coefficient_rows(records)
    all_cf = rows_for(
        coeff_rows,
        L="5",
        variant="all_conflict_free",
        weight_scheme="weight_unweighted",
        n_power="1",
        coefficient_order="1",
    )[0]
    signed_diag = rows_for(
        coeff_rows,
        L="5",
        variant="signed_diagonal_subtracted_proxy",
        weight_scheme="weight_unweighted",
        n_power="1",
        coefficient_order="1",
    )[0]
    rank_two = rows_for(
        coeff_rows,
        L="5",
        variant="rank_two_noncyclic_remainder",
        weight_scheme="weight_unweighted",
        n_power="1",
        coefficient_order="1",
    )[0]
    assert float(all_cf["signed_coefficient_sum"]) == -800.0
    assert signed_diag["signed_coefficient_sum"] == rank_two["signed_coefficient_sum"]
    assert signed_diag["coefficient_absolute_variation"] == rank_two["coefficient_absolute_variation"]


def test_report_referenced_csv_columns_exist() -> None:
    m13.main()
    with m13.COEFF_CSV.open(newline="") as f:
        coeff_header = set(next(csv.DictReader(f)).keys())
    with m13.GROUP_CSV.open(newline="") as f:
        group_header = set(next(csv.DictReader(f)).keys())
    with m13.PAIRING_CSV.open(newline="") as f:
        pairing_header = set(next(csv.DictReader(f)).keys())
    assert {"L", "variant", "n_power", "coefficient_order", "signed_coefficient_sum", "cancellation_ratio"} <= coeff_header
    assert {"grouping_rule", "group_key", "signed_coefficient_sum", "coefficient_absolute_variation"} <= group_header
    assert {"structure_key", "combined_cancellation_ratio", "persists_L3_L4_L5"} <= pairing_header


if __name__ == "__main__":
    test_hand_built_two_template_cancellation_has_zero_rho()
    test_all_same_sign_example_has_rho_one()
    test_zero_absolute_variation_is_handled_without_division_error()
    test_grouped_sums_refine_ungrouped_total()
    test_m11_m12_known_l5_unweighted_d1_values_are_reproduced()
    test_report_referenced_csv_columns_exist()
    print("all cancellation mechanism tests passed")
