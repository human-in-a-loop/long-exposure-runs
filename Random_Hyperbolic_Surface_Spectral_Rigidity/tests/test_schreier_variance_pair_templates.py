# created: 2026-05-16T21:44:00Z
# cycle: 42
# run_id: run-2026-05-15T153635Z
# agent: worker
# milestone: M31-schreier-variance-mechanism-theoremization
"""Tests for M31 Schreier variance pair-template analysis."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import analyze_schreier_variance_pair_templates as m31  # noqa: E402


def test_free_reduction_and_inverse_normalization() -> None:
    assert m31.reduce_word(tuple("aA")) == ()
    assert m31.reduce_word(tuple("abBA")) == ()
    assert m31.inverse_word(tuple("abA")) == tuple("aBA")
    order = m31.template_order(tuple("A"), tuple("a"), same_basepoint=False)
    assert order.partial_injection
    assert order.exponent == 0


def test_identity_words_are_separate_and_deterministic() -> None:
    rows, _, summary = m31.build_pair_rows((2,))
    identity_rows = [row for row in rows if row["pair_class"] == "identity_identity"]
    assert len(identity_rows) == 1
    assert identity_rows[0]["word_pair_multiplicity"] == 16
    assert identity_rows[0]["positive_power_obstruction"] is False
    assert summary[0]["supports_ok_n_minus_2_template"] is True


def test_inverse_and_shared_relation_classes_are_detected() -> None:
    assert m31.pair_class(tuple("ab"), tuple("BA")) == "inverse_reduced_word"
    assert m31.pair_class(tuple("abab"), tuple("ab")) == "shared_power_relation"
    rows, _, _ = m31.build_pair_rows((4,))
    classes = {row["pair_class"] for row in rows}
    assert "inverse_reduced_word" in classes
    assert "shared_power_relation" in classes


def test_normalized_o_n_minus_2_rows_are_backed_by_o_one_covariance() -> None:
    rows, _, summary = m31.build_pair_rows((2, 4, 6))
    for row in rows:
        if row["normalized_variance_order_after_n_minus_2"] == "O(n^-2)":
            assert row["covariance_order_before_normalization"] == "O(1)"
            assert int(row["max_template_exponent"]) <= 0
    assert all(row["supports_ok_n_minus_2_template"] for row in summary)


def test_class_orders_are_computed_from_all_reduced_pair_templates() -> None:
    rows, _, _ = m31.build_pair_rows((4,))
    row = next(
        item
        for item in rows
        if item["k"] == 4 and item["pair_class"] == "generic_shared_generator"
    )
    counts = m31.reduced_word_counts(4)
    expected = -999
    for w1 in counts:
        for w2 in counts:
            if m31.pair_class(w1, w2) == "generic_shared_generator":
                expected = max(
                    expected,
                    m31.template_order(w1, w2, same_basepoint=False).exponent,
                    m31.template_order(w1, w2, same_basepoint=True).exponent,
                )
    assert row["max_template_exponent"] == expected


def test_exactly_one_branch_decision_row() -> None:
    _, _, summary = m31.build_pair_rows((2, 4, 6))
    rows = m31.classification_rows(summary, [])
    decisions = [row for row in rows if row["claim_status"] == "decision"]
    assert len(decisions) == 1
    assert decisions[0]["decision"] in {
        "advance_schreier_variance_theorem",
        "preserve_variance_as_conjectural_benchmark",
        "pivot_to_finite_nonshrinking_spectral_statistics",
    }


if __name__ == "__main__":
    test_free_reduction_and_inverse_normalization()
    test_identity_words_are_separate_and_deterministic()
    test_inverse_and_shared_relation_classes_are_detected()
    test_normalized_o_n_minus_2_rows_are_backed_by_o_one_covariance()
    test_class_orders_are_computed_from_all_reduced_pair_templates()
    test_exactly_one_branch_decision_row()
    print("all Schreier variance pair-template tests passed")
