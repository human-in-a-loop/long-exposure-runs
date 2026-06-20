# created: 2026-05-16T20:16:00Z
# cycle: 39
# run_id: run-2026-05-15T153635Z
# agent: worker
# milestone: M28-theorem2-lp-mass-distribution-corollaries

from __future__ import annotations

import csv
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import analyze_theorem2_lp_mass_corollaries as m28


def approx_equal(left: float, right: float, tol: float = 1e-12) -> bool:
    return abs(left - right) <= tol


def test_interpolation_endpoints() -> None:
    alpha = 0.02
    assert approx_equal(m28.interpolation_decay_exponent(alpha, 2), 0.0)
    assert approx_equal(m28.interpolation_decay_exponent(alpha, math.inf), alpha)


def test_effective_support_exponent_fixed_energy() -> None:
    alpha = 0.02
    assert approx_equal(m28.effective_support_exponent(alpha, 0.0, 1.5), 2.0 * alpha)


def test_small_set_nontrivial_threshold() -> None:
    alpha = 0.02
    assert m28.small_set_mass_envelope(alpha, 0.0, 1.5, 0.01) < 0
    assert m28.small_set_mass_envelope(alpha, 0.0, 1.5, 0.05) > 0


def test_remark_mass_rows_classify_by_consequence_not_input_model() -> None:
    rows = m28.build_mass_rows()
    remark_rows = [
        row
        for row in rows
        if row["alpha_label"] == "remark_interpolation_representative"
    ]
    assert any(row["classification"] == "nontrivial_mass_delocalization" for row in remark_rows)
    assert any(row["classification"] == "bookkeeping_only" for row in remark_rows)
    assert not any(row["classification"] == "direct_theorem2_corollary" for row in remark_rows)


def test_no_quantum_ergodicity_classification() -> None:
    rows = m28.build_classification(m28.build_lp_rows(), m28.build_mass_rows())
    joined = " ".join(str(value).lower() for row in rows for value in row.values())
    assert "quantum_ergodicity" not in joined
    assert "equidistribution" in joined
    assert any(row["classification"] == "unsupported_stronger_claim" for row in rows)


def test_exactly_one_branch_decision_row() -> None:
    rows = m28.build_classification(m28.build_lp_rows(), m28.build_mass_rows())
    decision_rows = [row for row in rows if row["decision"]]
    assert len(decision_rows) == 1
    assert decision_rows[0]["decision"] == "advance_theorem2_consequence_branch"


def test_generated_csv_decision_if_present() -> None:
    path = Path("data/extension_candidates/m28_corollary_classification.csv")
    if not path.exists():
        return
    rows = list(csv.DictReader(path.open()))
    decision_rows = [row for row in rows if row["decision"]]
    assert len(decision_rows) == 1


if __name__ == "__main__":
    test_interpolation_endpoints()
    test_effective_support_exponent_fixed_energy()
    test_small_set_nontrivial_threshold()
    test_no_quantum_ergodicity_classification()
    test_exactly_one_branch_decision_row()
    test_generated_csv_decision_if_present()
    print("all theorem2 lp/mass corollary tests passed")
