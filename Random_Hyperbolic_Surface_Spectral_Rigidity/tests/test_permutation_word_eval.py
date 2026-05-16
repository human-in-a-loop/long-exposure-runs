from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import probe_common_fixed_points as probe


def test_identity_word_fixes_all_points():
    n = 7
    rng = np.random.default_rng(123)
    perms = probe.random_generator_perms(n, rng)
    assert probe.count_common_fixed(["1"], perms, n) == n
    assert np.array_equal(probe.eval_word("1", perms, n), np.arange(n))


def test_inverse_cancellation_reduces_to_identity():
    n = 11
    rng = np.random.default_rng(456)
    perms = probe.random_generator_perms(n, rng)
    assert probe.reduce_word("abBA") == ""
    assert probe.count_common_fixed(["abBA"], perms, n) == n


def test_identity_common_fixed_points_match_other_word():
    n = 13
    rng = np.random.default_rng(789)
    perms = probe.random_generator_perms(n, rng)
    assert probe.count_common_fixed(["1", "a"], perms, n) == probe.count_common_fixed(["a"], perms, n)


def test_deterministic_seed_gives_reproducible_output_shape():
    rows1 = probe.family_rows([5, 8], 3, 42)
    rows2 = probe.family_rows([5, 8], 3, 42)
    assert rows1 == rows2
    assert len(rows1) == 2 * 3 * len(probe.WORD_FAMILIES)
    assert set(rows1[0]) == {
        "n",
        "sample",
        "family",
        "word_count",
        "words",
        "fixed_common",
        "normalized_common",
        "seed",
    }


if __name__ == "__main__":
    test_identity_word_fixes_all_points()
    test_inverse_cancellation_reduces_to_identity()
    test_identity_common_fixed_points_match_other_word()
    test_deterministic_seed_gives_reproducible_output_shape()
    print("all permutation word evaluation tests passed")
