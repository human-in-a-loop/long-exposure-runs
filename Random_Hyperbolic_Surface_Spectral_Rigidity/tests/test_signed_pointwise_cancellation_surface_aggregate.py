# created: 2026-05-17T00:36:00Z
# cycle: 48
# run_id: run-2026-05-15T153635Z
# agent: worker
# milestone: M37-signed-pointwise-cancellation-surface-aggregate

from __future__ import annotations

import csv
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from analyze_signed_pointwise_cancellation_surface_aggregate import (  # noqa: E402
    DENOM_CSV,
    LAMBDA0_POWER,
    MECHANISM_CSV,
    STRATUM_CSV,
    TARGET_CSV,
    MECHANISMS,
)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open() as f:
        return list(csv.DictReader(f))


def test_markov_baseline_preserves_lambda0_20_and_zero_saving() -> None:
    rows = [r for r in read_csv(MECHANISM_CSV) if r["mechanism"] == "markov_baseline"]
    assert rows
    row = rows[0]
    assert int(row["Lambda0_power"]) == 20 == LAMBDA0_POWER
    assert float(row["A_offset_from_markov"]) == 0.0
    assert float(row["sigma"]) == 0.0
    assert float(row["denominator_loss_D"]) == 0.0
    assert row["paper_proved_success"] == "True"


def test_denominator_loss_degrades_beta_formula() -> None:
    rows = [
        r
        for r in read_csv(DENOM_CSV)
        if r["eta"] == "0.08" and r["mechanism"] == "surface_signed_pointwise_grouping"
    ]
    assert rows
    by_loss = {float(r["denominator_loss_D"]): float(r["net_beta_after_denominator"]) for r in rows}
    assert by_loss[0.0] > by_loss[0.5] > by_loss[1.0]
    assert abs(by_loss[0.25] - (1.5 * 0.08 + 0.35 - 0.25)) < 1e-12
    assert by_loss[1.0] < 0


def test_no_schreier_or_toy_row_claims_surface_theorem() -> None:
    rows = read_csv(MECHANISM_CSV)
    toy = [r for r in rows if r["mechanism"] == "schreier_pairing_transfer"]
    assert toy
    assert toy[0]["classification"] == "toy_only"
    assert toy[0]["uses_only_schreier_or_independent_permutation_evidence"] == "True"
    assert toy[0]["surface_attached"] == "False"
    assert toy[0]["claims_proved_exponent_improvement"] == "False"


def test_absolute_control_rows_are_cv_equivalent() -> None:
    rows = read_csv(MECHANISM_CSV)
    absolute_rows = [r for r in rows if r["requires_absolute_control"] == "True"]
    assert absolute_rows
    assert {r["classification"] for r in absolute_rows} == {"coefficient_variation_equivalent"}


def test_negative_wrong_point_and_off_range_cases_are_blocked() -> None:
    rows = {r["mechanism"]: r for r in read_csv(MECHANISM_CSV)}
    assert rows["x_zero_only_cancellation"]["classification"] == "range_blocked"
    assert rows["x_zero_only_cancellation"]["pointwise_at_x_1_over_n"] == "False"
    assert rows["off_range_reciprocal_cancellation"]["classification"] == "range_blocked"
    assert rows["off_range_reciprocal_cancellation"]["paper_safe_range"] == "False"


def test_surface_targets_are_independent_only_when_pointwise_and_safe() -> None:
    rows = read_csv(STRATUM_CSV)
    independent = [r for r in rows if r["independent_signed_target"] == "True"]
    assert independent
    assert {r["classification"] for r in independent} == {"surface_theorem_target"}
    blocked = [r for r in rows if r["mechanism"] == "x_zero_only_cancellation"]
    assert blocked and all(r["independent_signed_target"] == "False" for r in blocked)


def test_no_generated_row_claims_theorem_improvement_or_local_statistics() -> None:
    for row in read_csv(MECHANISM_CSV):
        assert row["claims_proved_exponent_improvement"] == "False"
        assert row["claims_local_statistics"] == "False"
        assert row["claims_variance_law"] == "False"
        assert row["claims_shrinking_window_theorem"] == "False"
    for row in read_csv(TARGET_CSV):
        assert row["claims_proved_exponent_improvement"] == "False"


def test_theorem_target_table_has_required_classifications() -> None:
    rows = read_csv(TARGET_CSV)
    classifications = {r["classification"] for r in rows}
    assert "surface_theorem_target" in classifications
    assert "coefficient_variation_equivalent" in classifications
    assert "denominator_blocked" in classifications
    assert "range_blocked" in classifications
    assert "toy_only" in classifications
    spc = [r for r in rows if r["target"] == "SPC(A,sigma)"][0]
    assert "p(1/n)/Q_id(1/n)" in spc["statement"]
    assert "Lambda0^20" in spc["statement"]


def test_helper_formula_matches_stratum_row() -> None:
    model = next(m for m in MECHANISMS if m.name == "surface_signed_pointwise_grouping")
    expected = model.beta(0.08)
    rows = [
        r
        for r in read_csv(STRATUM_CSV)
        if r["mechanism"] == model.name
        and r["kappa"] == "5.0"
        and r["eta"] == "0.08"
        and r["stratum_type"] == "fixed_d"
    ]
    assert rows
    assert abs(float(rows[0]["candidate_beta"]) - expected) < 1e-12


def test_proof_ledger_preserves_signed_target_and_firewalls() -> None:
    text = (ROOT / "docs/proof_ledger/signed_pointwise_cancellation_surface_aggregate.md").read_text()
    assert "Lambda0^20" in text
    assert "SPC(A,sigma)" in text
    assert "|p(1/n) / Q_id(1/n)|" in text
    assert "Schreier" in text


def main() -> None:
    test_markov_baseline_preserves_lambda0_20_and_zero_saving()
    test_denominator_loss_degrades_beta_formula()
    test_no_schreier_or_toy_row_claims_surface_theorem()
    test_absolute_control_rows_are_cv_equivalent()
    test_negative_wrong_point_and_off_range_cases_are_blocked()
    test_surface_targets_are_independent_only_when_pointwise_and_safe()
    test_no_generated_row_claims_theorem_improvement_or_local_statistics()
    test_theorem_target_table_has_required_classifications()
    test_helper_formula_matches_stratum_row()
    test_proof_ledger_preserves_signed_target_and_firewalls()
    print("all signed pointwise cancellation surface aggregate tests passed")


if __name__ == "__main__":
    main()
