# created: 2026-05-16T19:13:00Z
# cycle: 36
# run_id: run-2026-05-15T153635Z
# agent: worker
# milestone: M25-local-window-route-synthesis-and-branch-decision

"""Tests for the M25 local-window route synthesis builder."""

from __future__ import annotations

import csv
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_local_window_route_synthesis as m25  # noqa: E402


EXPECTED_MILESTONES = {
    "M16-local-spectral-window-corollaries",
    "M17-local-window-variance-input",
    "M18-test-function-localization-feasibility",
    "M19-smoothed-window-paley-wiener-lemma",
    "M20-long-support-trace-variance-requirement",
    "M21-trace-side-long-support-variance-template",
    "M22-trace-corollary34-uniform-coefficient-variation-target",
    "M23-localized-trace-numerator-quotient-family-model",
    "M24-localized-transform-geodesic-weight-decay-obstruction",
}


def ensure_outputs() -> None:
    if not m25.EVIDENCE_CSV.exists() or not m25.DECISION_CSV.exists():
        assert m25.main() == 0


def test_all_m16_m24_milestones_appear() -> None:
    assert {row["milestone"] for row in m25.EVIDENCE_ROWS} == EXPECTED_MILESTONES


def test_at_least_one_artifact_is_indexed_per_milestone() -> None:
    for row in m25.EVIDENCE_ROWS:
        assert row["primary_artifact"]
        assert (ROOT / row["primary_artifact"]).exists()


def test_claim_labels_are_allowed() -> None:
    labels = {row["claim_type"] for row in m25.EVIDENCE_ROWS + m25.DECISION_ROWS}
    assert labels <= m25.ALLOWED_LABELS


def test_final_decision_is_allowed_and_expected() -> None:
    assert m25.FINAL_DECISION in m25.ALLOWED_DECISIONS
    assert m25.FINAL_DECISION == "preserve_as_followup_problem"


def test_generated_csvs_contain_required_rows() -> None:
    ensure_outputs()
    with m25.EVIDENCE_CSV.open() as handle:
        evidence_rows = list(csv.DictReader(handle))
    with m25.DECISION_CSV.open() as handle:
        decision_rows = list(csv.DictReader(handle))
    assert len(evidence_rows) == 9
    assert {row["milestone"] for row in evidence_rows} == EXPECTED_MILESTONES
    assert len(decision_rows) == 3
    assert {row["decision"] for row in decision_rows} == {"preserve_as_followup_problem"}


if __name__ == "__main__":
    test_all_m16_m24_milestones_appear()
    test_at_least_one_artifact_is_indexed_per_milestone()
    test_claim_labels_are_allowed()
    test_final_decision_is_allowed_and_expected()
    test_generated_csvs_contain_required_rows()
    print("all local-window route synthesis tests passed")
