# created: 2026-05-16T23:59:50Z
# cycle: 46
# run_id: run-2026-05-15T153635Z
# agent: worker
# milestone: M35-surface-corollary34-numerator-obstruction

from __future__ import annotations

import csv
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from analyze_surface_corollary34_numerator_obstruction import (  # noqa: E402
    CLASS_CSV,
    GAP_CSV,
    GRID_CSV,
    LOSS_CSV,
    MECHANISMS,
    candidate_beta,
    required_beta,
)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open() as f:
        return list(csv.DictReader(f))


def test_markov_interpolation_loss_reproduces_q_2kappa() -> None:
    rows = [r for r in read_csv(LOSS_CSV) if r["mechanism"] == "existing_markov_interpolation"]
    assert rows
    for row in rows:
        expected = 2.0 * float(row["kappa"]) * float(row["eta"])
        assert abs(float(row["q_loss_exponent"]) - expected) < 1e-12
        assert row["markov_q_2kappa_reproduced"] == "True"


def test_beta_saving_algebra_matches_m22_specialization() -> None:
    mech = next(m for m in MECHANISMS if m.name == "coefficient_variation_target")
    assert abs(candidate_beta(5.0, 0.08, mech) - 2.0 * 0.08) < 1e-12
    assert abs(required_beta(5.0, 0.08, 0.08) - (2.0 * 5.0 * 0.08 + 2.0 * 0.08 - 1.0)) < 1e-12


def test_independent_permutation_evidence_is_insufficient_for_kim_tao() -> None:
    class_rows = read_csv(CLASS_CSV)
    blocked = [r for r in class_rows if r["mechanism"] == "blocked_by_missing_surface_input"]
    assert blocked
    assert blocked[0]["uses_only_schreier_or_independent_permutation_evidence"] == "True"
    assert blocked[0]["classification"] == "toy_only_insufficient"
    gap_rows = read_csv(GAP_CSV)
    toy = [r for r in gap_rows if "independent-permutation" in r["input"]]
    assert toy and toy[0]["schreier_transfer_sufficient"] == "False"


def test_no_overclaims_are_generated() -> None:
    for row in read_csv(CLASS_CSV):
        assert row["claims_proved_exponent_improvement"] == "False"
        assert row["claims_local_statistics"] == "False"
        assert row["claims_variance_law"] == "False"
        assert row["claims_shrinking_window_theorem"] == "False"
    assert all(r["paper_proved_success"] == "False" for r in read_csv(GRID_CSV))


def test_special_point_rows_are_present() -> None:
    mechanisms = {r["mechanism"] for r in read_csv(CLASS_CSV)}
    required = {
        "special_point:x=0",
        "special_point:x=1/n",
        "special_point:n=q^kappa",
        "special_point:q->infinity",
        "special_point:fixed_Lambda0",
        "special_point:high_Lambda0",
        "special_point:Q_id(1/n)",
    }
    assert required <= mechanisms


def test_paper_energy_factor_is_preserved_in_proof_ledger() -> None:
    ledger = (ROOT / "docs/proof_ledger/surface_corollary34_numerator_obstruction.md").read_text()
    assert "Lambda0^20" in ledger
    assert "Lambda0^2 ||htilde||^2" not in ledger


def test_conditional_success_requires_new_surface_input() -> None:
    rows = read_csv(GRID_CSV)
    conditional = [r for r in rows if r["failure_reason"] == "conditional_on_new_surface_group_theorem"]
    assert conditional
    by_mechanism = {r["mechanism"] for r in conditional}
    assert "existing_markov_interpolation" not in by_mechanism
    assert all(r["conditional_success_if_new_surface_input_proved"] == "True" for r in conditional)


def main() -> None:
    test_markov_interpolation_loss_reproduces_q_2kappa()
    test_beta_saving_algebra_matches_m22_specialization()
    test_independent_permutation_evidence_is_insufficient_for_kim_tao()
    test_no_overclaims_are_generated()
    test_special_point_rows_are_present()
    test_paper_energy_factor_is_preserved_in_proof_ledger()
    test_conditional_success_requires_new_surface_input()
    print("all surface corollary34 numerator obstruction tests passed")


if __name__ == "__main__":
    main()
