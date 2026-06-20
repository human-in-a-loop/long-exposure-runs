# created: 2026-05-17T01:06:00Z
# cycle: 49
# run_id: run-2026-05-15T153635Z
# agent: worker
# milestone: M38-surface-native-grouping-problem

from __future__ import annotations

import csv
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from analyze_surface_native_grouping_problem import (  # noqa: E402
    BETA_CSV,
    CLASSIFICATION_CSV,
    DEPENDENCY_CSV,
    GROUPINGS,
    LAMBDA0_POWER,
    TEMPLATE_CSV,
)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open() as f:
        return list(csv.DictReader(f))


def test_markov_baseline_preserves_lambda0_20_and_zero_saving() -> None:
    row = [r for r in read_csv(CLASSIFICATION_CSV) if r["grouping"] == "markov_baseline"][0]
    assert int(row["Lambda0_power"]) == 20 == LAMBDA0_POWER
    assert float(row["A_offset"]) == 0.0
    assert float(row["sigma"]) == 0.0
    assert float(row["D"]) == 0.0
    assert row["classification"] == "paper_proved_baseline"


def test_denominator_loss_subtracts_from_beta() -> None:
    rows = [
        r
        for r in read_csv(BETA_CSV)
        if r["grouping"] == "surface_relation_kernel_grouping"
        and r["kappa"] == "5.0"
        and r["eta"] == "0.08"
    ]
    by_d = {float(r["D"]): float(r["beta"]) for r in rows}
    assert by_d[0.0] > by_d[0.25] > by_d[0.5] > by_d[1.0]
    expected = 1.25 * 0.08 + 0.35 - 0.25
    assert abs(by_d[0.25] - expected) < 1e-12


def test_x0_cancellation_is_wrong_point_blocked() -> None:
    row = [r for r in read_csv(CLASSIFICATION_CSV) if r["grouping"] == "coefficient_expansion_by_x0"][0]
    assert row["classification"] == "range_blocked"
    assert row["evaluation_point"] == "x=0"
    assert row["pointwise_at_x_1_over_n"] == "False"


def test_schreier_rows_are_not_theorem_evidence() -> None:
    row = [r for r in read_csv(CLASSIFICATION_CSV) if r["grouping"] == "schreier_pairing_analogy"][0]
    assert row["classification"] == "toy_only"
    assert row["paper_native"] == "False"
    assert row["uses_schreier_or_independent_permutation_evidence"] == "True"
    assert row["claims_proved_exponent_improvement"] == "False"


def test_absolute_fixed_stratum_rows_are_coefficient_variation_equivalent() -> None:
    rows = [r for r in read_csv(CLASSIFICATION_CSV) if r["requires_absolute_fixed_stratum"] == "True"]
    assert rows
    assert {r["classification"] for r in rows} == {"coefficient_variation_equivalent"}


def test_surface_theorem_ready_rows_are_pointwise_and_denominator_safe() -> None:
    rows = [r for r in read_csv(BETA_CSV) if r["theorem_ready_spc_g"] == "True"]
    assert rows
    assert {r["D"] for r in rows} == {"0.0"}
    assert {r["classification"] for r in rows} == {"surface_theorem_target"}
    names = {r["grouping"] for r in rows}
    assert "surface_relation_kernel_grouping" in names
    assert "length_shell_transform_phase" in names


def test_template_table_contains_spc_g_and_pivot_rule() -> None:
    rows = read_csv(TEMPLATE_CSV)
    assert rows
    assert any("SPC_G" in r["template"] for r in rows)
    for row in rows:
        assert "Q_i(1/n)/Q_id(1/n)" in row["statement"]
        assert "Lambda0^20" in row["statement"]
        assert "pivot to coefficient/signed variation" in row["pivot_rule"]
        assert row["claims_proved_exponent_improvement"] == "False"


def test_dependency_matrix_blocks_toy_and_denominator_failures() -> None:
    rows = read_csv(DEPENDENCY_CSV)
    toy = [
        r
        for r in rows
        if r["grouping"] == "schreier_pairing_analogy"
        and r["dependency"] == "Schreier independent pairing"
    ][0]
    assert toy["status_for_grouping"] == "toy_only"
    denom = [
        r
        for r in rows
        if r["grouping"] == "near_zero_denominator_grouping"
        and r["dependency"] == "Q_id(1/n) lower bound"
    ][0]
    assert denom["status_for_grouping"] == "fails_or_costs_D"


def test_helper_formula_matches_beta_row() -> None:
    group = next(g for g in GROUPINGS if g.name == "length_shell_transform_phase")
    expected = group.beta(0.12, 0.5)
    row = [
        r
        for r in read_csv(BETA_CSV)
        if r["grouping"] == group.name
        and r["kappa"] == "5.0"
        and r["eta"] == "0.12"
        and r["D"] == "0.5"
    ][0]
    assert abs(float(row["beta"]) - expected) < 1e-12


def test_docs_preserve_m35_m37_exactness_constraints() -> None:
    text = (ROOT / "docs/proof_ledger/surface_native_grouping_problem.md").read_text()
    assert "Lambda0^20" in text
    assert "SPC_G(A,sigma)" in text
    assert "x=1/n" in text
    assert "Schreier" in text


def main() -> None:
    test_markov_baseline_preserves_lambda0_20_and_zero_saving()
    test_denominator_loss_subtracts_from_beta()
    test_x0_cancellation_is_wrong_point_blocked()
    test_schreier_rows_are_not_theorem_evidence()
    test_absolute_fixed_stratum_rows_are_coefficient_variation_equivalent()
    test_surface_theorem_ready_rows_are_pointwise_and_denominator_safe()
    test_template_table_contains_spc_g_and_pivot_rule()
    test_dependency_matrix_blocks_toy_and_denominator_failures()
    test_helper_formula_matches_beta_row()
    test_docs_preserve_m35_m37_exactness_constraints()
    print("all surface-native grouping problem tests passed")


if __name__ == "__main__":
    main()
