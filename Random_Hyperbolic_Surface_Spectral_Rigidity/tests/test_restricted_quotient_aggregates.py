# created: 2026-05-16T08:15:00Z
# cycle: 21
# run_id: run-2026-05-15T153635Z
# agent: worker
# milestone: M10-restricted-quotient-aggregate
"""Tests for the M10 restricted quotient aggregate enumerator."""

from __future__ import annotations

import csv
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import enumerate_restricted_quotient_aggregates as m10  # noqa: E402


def test_inverse_label_normalization() -> None:
    assert m10.normalize_step(0, 1, "A") == (1, "a", 0)
    assert m10.normalize_step(0, 1, "b") == (0, "b", 1)


def test_canonicalization_invariant_under_vertex_relabeling() -> None:
    edges = [(0, "a", 1), (1, "b", 2), (2, "a", 0)]
    relabelled = [(0, "a", 5), (5, "b", 3), (3, "a", 0)]
    assert m10.canonicalize_edges(edges).key == m10.canonicalize_edges(relabelled).key


def test_single_generator_loop_profile() -> None:
    skeleton = m10.canonicalize_edges(m10.two_word_edges("a", "a"))
    assert skeleton.vertex_count == 1
    assert skeleton.count_a == 1
    assert m10.profile_expression(skeleton) == "(n-0)/(n-0)"
    assert m10.profile_coefficients(skeleton)[1] == 0


def test_conflict_detection_on_raw_partial_injection() -> None:
    assert m10.has_partial_injection_conflict([(0, "a", 1), (0, "a", 2)])
    assert m10.has_partial_injection_conflict([(1, "a", 0), (2, "a", 0)])


def test_generated_summary_matches_profile_multiplicities() -> None:
    m10.main()
    with m10.PROFILE_CSV.open(newline="") as f:
        profiles = list(csv.DictReader(f))
    with m10.SUMMARY_CSV.open(newline="") as f:
        summaries = list(csv.DictReader(f))
    for L in range(1, m10.L_MAX + 1):
        profile_total = sum(int(row["multiplicity"]) for row in profiles if row["L"] == str(L) and row["conflict"] == "no")
        summary = [
            row
            for row in summaries
            if row["L"] == str(L) and row["variant"] == "all_conflict_free" and row["coefficient_order"] == "1"
        ][0]
        assert int(summary["total_multiplicity"]) == profile_total
        assert int(summary["weight_l1"]) == profile_total


if __name__ == "__main__":
    test_inverse_label_normalization()
    test_canonicalization_invariant_under_vertex_relabeling()
    test_single_generator_loop_profile()
    test_conflict_detection_on_raw_partial_injection()
    test_generated_summary_matches_profile_multiplicities()
    print("all restricted quotient aggregate tests passed")
