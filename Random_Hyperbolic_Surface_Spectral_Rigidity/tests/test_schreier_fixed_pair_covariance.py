# created: 2026-05-16T22:35:00Z
# cycle: 43
# run_id: run-2026-05-15T153635Z
# agent: worker
# milestone: M32-schreier-fixed-pair-covariance-lemma
"""Tests for the M32 Schreier fixed-pair covariance proof checker."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import prove_schreier_fixed_pair_covariance as m32  # noqa: E402


def test_identity_cases_are_deterministic() -> None:
    rows, _, implication = m32.build_rows(2)
    identity_rows = [row for row in rows if row["relation_class"] == "identity"]
    assert identity_rows
    assert all(row["covariance_order_bound"] == "zero" for row in identity_rows)
    assert any(row["item"] == "fixed_k_variance" for row in implication)


def test_exceptional_pair_classes_are_detected_and_bounded() -> None:
    assert m32.relation_class(tuple("ab"), tuple("BA")) == "inverse"
    assert m32.relation_class(tuple("ab"), tuple("ba")) == "cyclic_conjugate"
    assert m32.relation_class(tuple("abab"), tuple("ab")) == "shared_power"
    rows, _, _ = m32.build_rows(4)
    for cls in ("inverse", "cyclic_conjugate", "shared_power"):
        class_rows = [row for row in rows if row["relation_class"] == cls]
        assert class_rows
        assert all(row["covariance_order_bound"] == "O(1)" for row in class_rows)


def test_generic_pair_has_no_positive_base_exponent() -> None:
    same = m32.base_stats(tuple("ab"), tuple("aB"), "same")
    distinct = m32.base_stats(tuple("ab"), tuple("aB"), "distinct")
    assert same.exponent <= 0
    assert distinct.exponent <= 0
    assert m32.relation_class(tuple("ab"), tuple("aB")) == "generic"


def test_partial_injection_failure_contributes_zero() -> None:
    vertices = ["s", "t", "u"]
    edges = [("s", "t", "a"), ("s", "u", "a")]
    alias = {"s": "s", "t": "t", "u": "u"}
    stats = m32.stats_for_alias(vertices, edges, alias)
    assert not stats.partial_injection


def test_exhaustive_quotient_audit_respects_proof_bound() -> None:
    audit = m32.exhaustive_quotient_stats(tuple("ab"), tuple("BA"), "same")
    assert audit["checked"] is True
    assert audit["quotient_templates"] > 0
    assert audit["max_admissible_exponent"] <= 0


def test_all_length_six_classes_use_nonpositive_proof_bound() -> None:
    rows, proof_rows, _ = m32.build_rows(6)
    nonidentity_rows = [row for row in rows if row["relation_class"] != "identity"]
    assert nonidentity_rows
    assert all(int(row["max_proof_exponent_bound"]) == 0 for row in nonidentity_rows)
    checked_rows = [row for row in proof_rows if row["exhaustive_quotient_check"] is True]
    assert checked_rows
    assert all(row["passes_exponent_bound"] is True for row in checked_rows)


def test_class_rows_record_representative_base_template_stats() -> None:
    rows, _, _ = m32.build_rows(4)
    target = next(
        row
        for row in rows
        if row["len_u"] == 2 and row["len_v"] == 2 and row["relation_class"] == "generic"
    )
    u = tuple(str(target["representative_u"]))
    v = tuple(str(target["representative_v"]))
    same = m32.base_stats(u, v, "same")
    distinct = m32.base_stats(u, v, "distinct")
    assert int(target["representative_same_basepoint_base_exponent"]) == same.exponent
    assert int(target["representative_distinct_basepoint_base_exponent"]) == distinct.exponent
    assert int(target["partial_injection_failures_in_base_templates"]) == (
        int(not same.partial_injection) + int(not distinct.partial_injection)
    )
    assert "general_bound_by_lemma" in str(target["audit_scope"])


if __name__ == "__main__":
    test_identity_cases_are_deterministic()
    test_exceptional_pair_classes_are_detected_and_bounded()
    test_generic_pair_has_no_positive_base_exponent()
    test_partial_injection_failure_contributes_zero()
    test_exhaustive_quotient_audit_respects_proof_bound()
    test_all_length_six_classes_use_nonpositive_proof_bound()
    test_class_rows_record_representative_base_template_stats()
    print("all Schreier fixed-pair covariance tests passed")
