# created: 2026-05-17T01:31:00Z
# cycle: 50
# run_id: run-2026-05-15T153635Z
# agent: worker
# milestone: M39-surface-relation-kernel-spc-probe

from __future__ import annotations

import csv
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from analyze_surface_relation_kernel_spc_probe import (  # noqa: E402
    BETA_CSV,
    CLASSIFICATION_CSV,
    LAMBDA0_POWER,
    MECHANISMS,
    PIVOT_CSV,
    PROOF_LEDGER,
    SCHEMA_CSV,
)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open() as f:
        return list(csv.DictReader(f))


def row_for(name: str) -> dict[str, str]:
    return [r for r in read_csv(CLASSIFICATION_CSV) if r["mechanism"] == name][0]


def test_markov_baseline_preserves_lambda0_20_and_zero_saving() -> None:
    row = row_for("markov_baseline")
    assert int(row["Lambda0_power"]) == 20 == LAMBDA0_POWER
    assert float(row["A_offset"]) == 0.0
    assert float(row["sigma"]) == 0.0
    assert float(row["D"]) == 0.0
    assert row["classification"] == "paper_proved_baseline"


def test_beta_formula_and_denominator_loss_subtracts() -> None:
    rows = [
        r
        for r in read_csv(BETA_CSV)
        if r["mechanism"] == "kernel_class_signed_pairing"
        and r["kappa"] == "5.0"
        and r["eta"] == "0.08"
    ]
    by_d = {float(r["D"]): float(r["beta"]) for r in rows}
    assert by_d[0.0] > by_d[0.25] > by_d[0.5] > by_d[1.0]
    expected = 1.25 * 0.08 + 0.35 - 0.25
    assert abs(by_d[0.25] - expected) < 1e-12


def test_x0_cancellation_is_wrong_point_without_value_argument() -> None:
    row = row_for("x0_kernel_coefficient_cancellation")
    assert row["classification"] == "range_blocked"
    assert row["evaluation_point"] == "x=0"
    assert row["pointwise_at_x_1_over_n"] == "False"
    assert "wrong-point" in row["theorem_template"]


def test_toy_free_group_kernel_proxy_is_not_theorem_evidence() -> None:
    row = row_for("toy_free_group_kernel_proxy")
    assert row["classification"] == "toy_only"
    assert row["paper_native"] == "False"
    assert row["uses_toy_or_free_group_proxy"] == "True"
    assert row["claims_proved_exponent_improvement"] == "False"


def test_absolute_kernel_stratum_control_is_coefficient_variation_equivalent() -> None:
    row = row_for("absolute_kernel_stratum_control")
    assert row["requires_absolute_kernel_stratum"] == "True"
    assert row["classification"] == "coefficient_variation_equivalent"
    assert "not SPC_kernel" in row["theorem_template"]


def test_surface_theorem_target_rows_are_pointwise_denominator_safe() -> None:
    rows = [r for r in read_csv(BETA_CSV) if r["theorem_ready_spc_kernel"] == "True"]
    assert rows
    assert {r["D"] for r in rows} == {"0.0"}
    assert {r["classification"] for r in rows} == {"surface_theorem_target"}
    names = {r["mechanism"] for r in rows}
    assert names == {"kernel_class_signed_pairing", "quotient_polynomial_sign_grouping"}


def test_kernel_closure_schema_places_condition_before_polynomial_signs() -> None:
    rows = read_csv(SCHEMA_CSV)
    assert [r["paper_object"] for r in rows][:3] == ["C_{gamma1,gamma2}", "W_r", "E_emb_n(W_r)"]
    wr = [r for r in rows if r["paper_object"] == "W_r"][0]
    assert "ker(F_{2g}->Gamma)" in wr["kernel_condition_role"]
    assert wr["sign_information"] == "admissibility only"
    q = [r for r in rows if r["paper_object"] == "Q_{gamma1,gamma2}(t)"][0]
    assert "possible evaluated signs" in q["sign_information"]


def test_pivot_decision_recommends_coefficient_signed_variation() -> None:
    rows = read_csv(PIVOT_CSV)
    primary = [r for r in rows if r["decision"] == "kernel_spc_not_currently_theorem_ready"][0]
    assert primary["next_target"] == "surface_numerator_coefficient_signed_variation_first_attack"
    assert "sum_i |w_i Q_i(1/n)|" in primary["pivot_rule"]


def test_helper_formula_matches_beta_row() -> None:
    mechanism = next(m for m in MECHANISMS if m.name == "quotient_polynomial_sign_grouping")
    expected = mechanism.beta(5.0, 0.12, 0.5)
    row = [
        r
        for r in read_csv(BETA_CSV)
        if r["mechanism"] == mechanism.name
        and r["kappa"] == "5.0"
        and r["eta"] == "0.12"
        and r["D"] == "0.5"
    ][0]
    assert abs(float(row["beta"]) - expected) < 1e-12


def test_proof_ledger_preserves_exactness_constraints() -> None:
    text = PROOF_LEDGER.read_text()
    assert "Lemma 3.3" in text
    assert "ker(F_{2g} -> Gamma)" in text
    assert "SPC_kernel(A,sigma)" in text
    assert "Lambda0^20" in text
    assert "x=1/n" in text
    assert "beta = (2*kappa - A)*eta + sigma - D" in text
    assert "Schreier" in text


def main() -> None:
    test_markov_baseline_preserves_lambda0_20_and_zero_saving()
    test_beta_formula_and_denominator_loss_subtracts()
    test_x0_cancellation_is_wrong_point_without_value_argument()
    test_toy_free_group_kernel_proxy_is_not_theorem_evidence()
    test_absolute_kernel_stratum_control_is_coefficient_variation_equivalent()
    test_surface_theorem_target_rows_are_pointwise_denominator_safe()
    test_kernel_closure_schema_places_condition_before_polynomial_signs()
    test_pivot_decision_recommends_coefficient_signed_variation()
    test_helper_formula_matches_beta_row()
    test_proof_ledger_preserves_exactness_constraints()
    print("all surface-relation kernel SPC probe tests passed")


if __name__ == "__main__":
    main()
