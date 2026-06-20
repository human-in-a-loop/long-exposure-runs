# created: 2026-05-16T19:34:00Z
# cycle: 37
# run_id: run-2026-05-15T153635Z
# agent: worker
# milestone: M26-post-local-extension-reprioritization

"""Tests for the M26 post-local extension candidate scorer."""

from __future__ import annotations

import csv
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import score_post_local_extension_candidates as m26  # noqa: E402


REQUIRED_FAMILIES = {
    "multiplicity/spectral-cluster consequences from rigidity",
    "eigenfunction Lp/mass-distribution consequences from delocalization",
    "finite-window but non-shrinking spectral statistics",
    "random-regular-graph/Schreier benchmark theoremization",
    "transfer template to adjacent random-surface models",
}


def ensure_outputs() -> None:
    if not m26.SCORES_CSV.exists() or not m26.DEPENDENCIES_CSV.exists():
        assert m26.main() == 0


def test_all_required_candidate_families_appear() -> None:
    assert REQUIRED_FAMILIES <= {candidate.family for candidate in m26.CANDIDATES}


def test_m25_dependent_route_is_not_ranked_first() -> None:
    assert m26.ordered_candidates()[0].candidate_id != "m25_dependent_local_window"


def test_each_candidate_has_attachment_and_obstruction() -> None:
    for candidate in m26.CANDIDATES:
        assert candidate.attachment_point
        assert candidate.obstruction


def test_exactly_one_next_milestone_recommended() -> None:
    assert sum(1 for candidate in m26.CANDIDATES if candidate.next_milestone_recommended) == 1
    assert m26.ordered_candidates()[0].next_milestone_recommended


def test_generated_scores_have_expected_recommendation() -> None:
    ensure_outputs()
    with m26.SCORES_CSV.open() as handle:
        rows = list(csv.DictReader(handle))
    recommended = [row for row in rows if row["next_milestone_recommended"] == "yes"]
    assert len(recommended) == 1
    assert recommended[0]["candidate_id"] == "multiplicity_cluster"
    assert recommended[0]["recommended_order"] == "1"
    assert all(row["attachment_point"] and row["obstruction"] for row in rows)


if __name__ == "__main__":
    test_all_required_candidate_families_appear()
    test_m25_dependent_route_is_not_ranked_first()
    test_each_candidate_has_attachment_and_obstruction()
    test_exactly_one_next_milestone_recommended()
    test_generated_scores_have_expected_recommendation()
    print("all post-local extension candidate tests passed")
