# created: 2026-05-16T00:55:00Z
# cycle: 14
# run_id: run-2026-05-15T153635Z
# agent: worker
# milestone: M5-extension-candidates
"""Tests for labelled-template falling-factorial expansions."""

from __future__ import annotations

import sys
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import compare_expansions_to_cycle9 as cmp  # noqa: E402


COEFFS = ROOT / "data/extension_candidates/labelled_embedding_expansion_coefficients.csv"
DIAGNOSTICS = ROOT / "data/polynomial_method/polynomial_window_diagnostics.csv"


def load_coefficients() -> dict[str, dict[str, object]]:
    return cmp.read_coefficients(COEFFS)


def test_control_coefficients_by_hand() -> None:
    coefficients = load_coefficients()
    assert coefficients["no_edge_control"]["coeffs"] == [Fraction(1), Fraction(-1), Fraction(0), Fraction(0), Fraction(0)]
    assert coefficients["single_edge_control"]["coeffs"] == [Fraction(1), Fraction(-1), Fraction(0), Fraction(0), Fraction(0)]
    assert coefficients["single_label_cycle"]["coeffs"] == [Fraction(1), Fraction(0), Fraction(0), Fraction(0), Fraction(0)]


def test_conflict_template_is_zero() -> None:
    coefficients = load_coefficients()
    conflict = coefficients["conflicting_domain"]
    assert conflict["conflict"] is True
    assert conflict["coeffs"] == [Fraction(0), Fraction(0), Fraction(0), Fraction(0), Fraction(0)]
    assert cmp.exact_normalized(conflict, 20) == 0


def test_truncated_expansion_matches_exact_to_order() -> None:
    coefficients = load_coefficients()
    rank2 = coefficients["eight_word_rank2_toy"]
    n = 1000
    x = Fraction(1, n)
    exact = cmp.exact_normalized(rank2, n)
    order4 = cmp.taylor_value(rank2["coeffs"], x, 4)
    assert abs(exact - order4) < Fraction(1000, n**5)


def test_comparison_skips_missing_trace_pair() -> None:
    coefficients = load_coefficients()
    diagnostics = cmp.read_cycle9_diagnostics(DIAGNOSTICS)
    rows = cmp.build_comparison({"trace_pair_toy": coefficients["trace_pair_toy"]}, diagnostics)
    assert rows == [
        {
            "template": "trace_pair_toy",
            "comparison_status": "skipped_no_cycle9_rows",
            "n": "",
            "x": "",
            "split": "",
            "cycle9_fit_degree": "",
            "observed": "",
            "cycle9_prediction": "",
            "cycle9_abs_error": "",
            "exact_value": "",
            "exact_abs_error": "",
            "taylor_order": "",
            "taylor_prediction": "",
            "taylor_abs_error": "",
        }
    ]


if __name__ == "__main__":
    test_control_coefficients_by_hand()
    test_conflict_template_is_zero()
    test_truncated_expansion_matches_exact_to_order()
    test_comparison_skips_missing_trace_pair()
    print("all labelled embedding expansion tests passed")
