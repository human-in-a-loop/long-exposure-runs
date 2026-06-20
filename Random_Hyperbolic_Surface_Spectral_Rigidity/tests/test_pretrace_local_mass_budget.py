# created: 2026-05-16T20:41:00Z
# cycle: 40
# run_id: run-2026-05-15T153635Z
# agent: worker
# milestone: M29-pretrace-local-mass-intermediate-from-theorem2-proof

from __future__ import annotations

import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import analyze_pretrace_local_mass_budget as m29


def test_exactly_one_branch_decision_row() -> None:
    rows = m29.build_classification_rows(m29.build_budget_rows())
    decision_rows = [row for row in rows if row["decision"]]
    assert len(decision_rows) == 1
    assert decision_rows[0]["decision"] == "advance_pretrace_local_mass_branch"


def test_geometric_claim_requires_source_location() -> None:
    rows = m29.build_classification_rows(m29.build_budget_rows())
    geometric_rows = [
        row
        for row in rows
        if row["classification"] == "standalone_geometric_local_mass_corollary"
    ]
    for row in geometric_rows:
        source = row["source"]
        assert "2603.01127" in source or "docs/proof_ledger" in source


def test_hypothetical_rows_cannot_drive_branch_decision() -> None:
    budget_rows = m29.build_budget_rows()
    assert any(row["classification"] == "comparison_only" for row in budget_rows)
    decision_rows = [row for row in m29.build_classification_rows(budget_rows) if row["decision"]]
    assert all("hypothetical" not in row["item"] for row in decision_rows)


def test_claimed_improvements_have_positive_gap() -> None:
    rows = m29.build_budget_rows()
    claimed = [row for row in rows if row["claimed_improvement_over_m28"] is True]
    assert claimed
    for row in claimed:
        assert float(row["lambda_power_gap_vs_m28"]) > 0.0


def test_unsupported_labels_absent() -> None:
    rows = m29.build_classification_rows(m29.build_budget_rows())
    joined = " ".join(str(value).lower() for row in rows for value in row.values())
    assert "quantum_ergodicity" not in joined
    assert "random_wave" not in joined
    assert "lower_mass_on_all_balls" not in joined


def test_generated_csv_decision_if_present() -> None:
    path = Path("data/extension_candidates/m29_local_mass_statement_classification.csv")
    if not path.exists():
        return
    rows = list(csv.DictReader(path.open()))
    decision_rows = [row for row in rows if row["decision"]]
    assert len(decision_rows) == 1


if __name__ == "__main__":
    test_exactly_one_branch_decision_row()
    test_geometric_claim_requires_source_location()
    test_hypothetical_rows_cannot_drive_branch_decision()
    test_claimed_improvements_have_positive_gap()
    test_unsupported_labels_absent()
    test_generated_csv_decision_if_present()
    print("all pretrace local-mass budget tests passed")
