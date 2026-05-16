# created: 2026-05-16T09:15:00Z
# cycle: 22
# run_id: run-2026-05-15T153635Z
# agent: worker
# milestone: M11-trace-like-weighted-quotient-class
"""Tests for the M11 trace-like weighted quotient-class enumerator."""

from __future__ import annotations

import csv
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import enumerate_trace_like_weighted_quotients as m11  # noqa: E402


def test_cyclic_rotation_canonicalization() -> None:
    assert m11.canonical_conjugacy_word("aba") == m11.canonical_conjugacy_word("baa")
    assert m11.canonical_conjugacy_word("aba") == m11.canonical_conjugacy_word("aab")


def test_inversion_canonicalization() -> None:
    word = "abAB"
    assert m11.canonical_conjugacy_word(word) == m11.canonical_conjugacy_word(m11.inverse_word(word))


def test_primitive_power_detection() -> None:
    root, exponent = m11.primitive_root("abab")
    assert root == m11.canonical_conjugacy_word("ab")
    assert exponent == 2
    assert m11.primitive_root("ab")[1] == 1


def test_inverse_label_normalization() -> None:
    assert m11.normalize_step(0, 1, "A") == (1, "a", 0)
    assert m11.normalize_step(0, 1, "b") == (0, "b", 1)


def test_explicit_n_power_examples() -> None:
    single = m11.canonicalize_edges(m11.two_word_edges("a", "a"))
    assert single.count_a + single.count_b - single.vertex_count == 0
    rank_two = m11.canonicalize_edges(m11.two_word_edges("ab", "aB"))
    assert rank_two.count_a + rank_two.count_b - rank_two.vertex_count == 1


def test_generated_summary_matches_profile_weight_sums() -> None:
    m11.main()
    with m11.PROFILE_CSV.open(newline="") as f:
        profiles = list(csv.DictReader(f))
    with m11.SUMMARY_CSV.open(newline="") as f:
        summaries = list(csv.DictReader(f))
    for L in range(1, m11.L_MAX + 1):
        profile_total = sum(float(row["weight_unweighted"]) for row in profiles if row["L"] == str(L) and row["conflict"] == "no")
        summary = [
            row
            for row in summaries
            if row["L"] == str(L)
            and row["variant"] == "all_conflict_free"
            and row["weight_scheme"] == "weight_unweighted"
            and row["coefficient_order"] == "1"
        ][0]
        assert abs(float(summary["weight_l1"]) - profile_total) < 1e-6


def test_signed_diagonal_subtracted_summary_removes_diagonal_weight() -> None:
    records = m11.build_pair_records()
    summaries = m11.summarize_records(records)
    for L in range(1, m11.L_MAX + 1):
        all_row = [
            row
            for row in summaries
            if row["L"] == str(L)
            and row["variant"] == "all_conflict_free"
            and row["weight_scheme"] == "weight_unweighted"
            and row["coefficient_order"] == "1"
        ][0]
        diagonal_row = [
            row
            for row in summaries
            if row["L"] == str(L)
            and row["variant"] == "diagonal_cyclic_only"
            and row["weight_scheme"] == "weight_unweighted"
            and row["coefficient_order"] == "1"
        ][0]
        signed_row = [
            row
            for row in summaries
            if row["L"] == str(L)
            and row["variant"] == "signed_diagonal_subtracted_proxy"
            and row["weight_scheme"] == "weight_unweighted"
            and row["coefficient_order"] == "1"
        ][0]
        assert float(signed_row["weight_l1"]) == float(all_row["weight_l1"]) - float(diagonal_row["weight_l1"])


if __name__ == "__main__":
    test_cyclic_rotation_canonicalization()
    test_inversion_canonicalization()
    test_primitive_power_detection()
    test_inverse_label_normalization()
    test_explicit_n_power_examples()
    test_generated_summary_matches_profile_weight_sums()
    test_signed_diagonal_subtracted_summary_removes_diagonal_weight()
    print("all trace-like weighted quotient tests passed")
