from fractions import Fraction
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import certify_labelled_embedding_expectation as cert


def template(name):
    return next(t for t in cert.TEMPLATES if t.name == name)


def test_formula_zero_when_n_below_vertex_count():
    cyclic = template("eight_word_cyclic_toy")
    assert cert.formula_expectation(cyclic, 7) == Fraction(0, 1)
    assert cert.brute_force_expectation(cyclic, 3) == Fraction(0, 1)


def test_formula_equals_bruteforce_for_small_templates():
    names = ["no_edge", "single_edge", "same_label_path", "inverse_edge", "inverse_regression_pair"]
    for name in names:
        t = template(name)
        for n in range(2, 5):
            assert cert.formula_expectation(t, n) == cert.brute_force_expectation(t, n)


def test_conflicting_partial_maps_return_zero():
    for name in ["conflicting_domain", "conflicting_image"]:
        t = template(name)
        assert cert.constraint_counts(t) is None
        assert cert.formula_expectation(t, 4) == Fraction(0, 1)
        assert cert.brute_force_expectation(t, 4) == Fraction(0, 1)


def test_inverse_labels_normalize_by_reversing_orientation():
    forward = cert.LabelledTemplate("forward", (0, 1), ((1, 0, "a"),), "forward reversed edge")
    inverse = template("inverse_edge")
    assert cert.constraint_counts(forward) == cert.constraint_counts(inverse)
    assert cert.formula_expectation(forward, 4) == cert.formula_expectation(inverse, 4) == Fraction(3, 1)


def test_cycle8_inverse_label_regression_pair():
    t = template("inverse_regression_pair")
    assert cert.constraint_counts(t) == {"a": 2}
    for n in range(2, 5):
        expected = Fraction(1, 1)
        assert cert.formula_expectation(t, n) == expected
        assert cert.brute_force_expectation(t, n) == expected


def test_m3_benchmark_formula_values():
    cyclic = template("eight_word_cyclic_toy")
    rank2 = template("eight_word_rank2_toy")
    assert cert.constraint_counts(cyclic) == {"a": 8}
    assert cert.constraint_counts(rank2) == {"a": 4, "b": 4}
    assert cert.formula_expectation(cyclic, 8) == Fraction(1, 1)
    assert cert.formula_expectation(rank2, 7) == Fraction(1, 140)
    assert cert.formula_expectation(rank2, 8) == Fraction(1, 70)
    assert cert.normalized_by_naive_power(cyclic, 8, cert.formula_expectation(cyclic, 8)) == Fraction(1, 1)


def test_result_rows_are_all_exact_matches():
    rows = cert.result_rows(4)
    assert rows
    assert all(row["match"] == 1 for row in rows)


if __name__ == "__main__":
    test_formula_zero_when_n_below_vertex_count()
    test_formula_equals_bruteforce_for_small_templates()
    test_conflicting_partial_maps_return_zero()
    test_inverse_labels_normalize_by_reversing_orientation()
    test_cycle8_inverse_label_regression_pair()
    test_m3_benchmark_formula_values()
    test_result_rows_are_all_exact_matches()
    print("all labelled embedding expectation identity tests passed")
