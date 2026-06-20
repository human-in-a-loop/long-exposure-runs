# created: 2026-05-17T00:15:00Z
# cycle: 47
# run_id: run-2026-05-15T153635Z
# agent: worker
# milestone: M36-direct-small-x-surface-numerator-target

from __future__ import annotations

import csv
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from analyze_direct_small_x_surface_numerator_target import (  # noqa: E402
    BUDGET_CSV,
    CLASS_CSV,
    DENOM_CSV,
    IMPLICATION_CSV,
    LAMBDA0_POWER,
    variance_exponent,
    MODELS,
)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open() as f:
        return list(csv.DictReader(f))


def test_markov_baseline_has_q_2kappa_and_lambda0_20() -> None:
    rows = [r for r in read_csv(BUDGET_CSV) if r["model"] == "markov_baseline"]
    assert rows
    for row in rows:
        kappa = float(row["kappa"])
        eta = float(row["eta"])
        assert abs(float(row["A"]) - 2.0 * kappa) < 1e-12
        assert abs(float(row["q_loss_exponent"]) - 2.0 * kappa * eta) < 1e-12
        assert row["baseline_q_2kappa_reproduced"] == "True"
        assert int(row["Lambda0_power"]) == 20 == LAMBDA0_POWER
        assert abs(float(row["saving_vs_markov"])) < 1e-12


def test_denominator_loss_degrades_savings() -> None:
    rows = [
        r for r in read_csv(DENOM_CSV)
        if r["eta"] == "0.08" and r["A_offset_from_markov"] == "2.0" and r["sigma"] == "0.6"
    ]
    assert rows
    by_loss = {float(r["denominator_loss_D"]): float(r["net_beta_after_denominator"]) for r in rows}
    assert by_loss[0.0] > by_loss[0.5] > by_loss[1.0]
    assert by_loss[0.0] > 0
    assert by_loss[1.0] < 0
    obstructed = [r for r in rows if r["denominator_loss_D"] == "1.0"]
    assert obstructed[0]["near_zero_denominator_obstruction"] == "True"


def test_no_toy_evidence_is_theorem_level() -> None:
    class_rows = read_csv(CLASS_CSV)
    toy = [r for r in class_rows if r["mechanism"] == "schreier_toy_transfer"]
    assert toy
    assert toy[0]["uses_only_schreier_or_independent_permutation_evidence"] == "True"
    assert toy[0]["proof_status"] == "blocked"
    assert toy[0]["paper_proved_input"] == "False"


def test_special_points_include_fixed_and_high_lambda0() -> None:
    mechanisms = {r["mechanism"] for r in read_csv(CLASS_CSV)}
    assert "special_point:fixed_Lambda0" in mechanisms
    assert "special_point:high_Lambda0" in mechanisms
    assert "special_point:Q_id(1/n)=0" in mechanisms
    assert "special_point:Q_id(1/n) near-zero" in mechanisms


def test_direct_route_is_distinct_but_conditional() -> None:
    rows = read_csv(IMPLICATION_CSV)
    direct = [r for r in rows if r["route"] == "direct_small_x_ratio_bound"]
    assert direct
    assert direct[0]["strictly_weaker_than_coefficient_variation"] == "potentially_true"
    assert direct[0]["independent_route_status"] == "plausible_conditional"
    blocked = [r for r in rows if r["route"] == "direct_bound_from_fixed_pair_Q_estimates_only"]
    assert blocked and blocked[0]["independent_route_status"] == "blocked"


def test_no_generated_row_claims_proved_improvement_or_local_statistics() -> None:
    for row in read_csv(CLASS_CSV):
        assert row["claims_proved_exponent_improvement"] == "False"
        assert row["claims_local_statistics"] == "False"
        assert row["claims_variance_law"] == "False"
        assert row["claims_shrinking_window_theorem"] == "False"
    for row in read_csv(BUDGET_CSV):
        if row["model"] != "markov_baseline":
            assert row["paper_proved_success"] == "False"


def test_formula_helper_matches_generated_exponent() -> None:
    model = next(m for m in MODELS if m.name == "direct_small_x_with_denominator_loss")
    expected = variance_exponent(5.0, 0.08, model)
    rows = [
        r for r in read_csv(BUDGET_CSV)
        if r["model"] == model.name and r["kappa"] == "5.0" and r["eta"] == "0.08"
    ]
    assert rows
    assert abs(float(rows[0]["variance_exponent"]) - expected) < 1e-12


def test_proof_ledger_preserves_lambda0_20_and_target_statement() -> None:
    text = (ROOT / "docs/proof_ledger/direct_small_x_surface_numerator_target.md").read_text()
    assert "Lambda0^20" in text
    assert "|p(1/n) / Q_id(1/n)|" in text
    assert "DSE(A,sigma)" in text


def main() -> None:
    test_markov_baseline_has_q_2kappa_and_lambda0_20()
    test_denominator_loss_degrades_savings()
    test_no_toy_evidence_is_theorem_level()
    test_special_points_include_fixed_and_high_lambda0()
    test_direct_route_is_distinct_but_conditional()
    test_no_generated_row_claims_proved_improvement_or_local_statistics()
    test_formula_helper_matches_generated_exponent()
    test_proof_ledger_preserves_lambda0_20_and_target_statement()
    print("all direct small-x surface numerator target tests passed")


if __name__ == "__main__":
    main()
