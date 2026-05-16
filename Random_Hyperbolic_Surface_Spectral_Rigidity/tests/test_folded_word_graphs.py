from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import probe_folded_word_graphs as probe


def test_cyclic_pair_classifies_as_rank_one_cyclic():
    inv = probe.build_trajectory_graph(("a", "aa"))
    assert inv["generator_rank"] == 1
    assert inv["is_cyclic_power_family"] is True
    assert inv["cyclomatic_rank"] >= 1


def test_rank_two_pair_has_larger_noncyclic_invariant():
    cyclic = probe.build_trajectory_graph(("a", "aa"))
    rank_two = probe.build_trajectory_graph(("a", "b"))
    assert rank_two["generator_rank"] > cyclic["generator_rank"]
    assert rank_two["is_cyclic_power_family"] is False
    assert rank_two["cyclomatic_rank"] >= cyclic["cyclomatic_rank"]


def test_identity_handling_is_explicit():
    inv = probe.build_trajectory_graph(("1",))
    assert inv["identity_present"] is True
    assert inv["vertices"] == 1
    assert inv["directed_edges"] == 0
    assert inv["cyclomatic_rank"] == 0
    assert inv["is_cyclic_power_family"] is False


def test_deterministic_seed_reproduces_rows():
    rows1 = probe.family_rows([6], 2, 99, 3)
    rows2 = probe.family_rows([6], 2, 99, 3)
    assert rows1 == rows2
    assert len(rows1) == 2 * len(probe.WORD_FAMILIES)
    assert {
        "n",
        "sample",
        "family",
        "words",
        "vertices",
        "directed_edges",
        "cyclomatic_rank",
        "is_cyclic_power_family",
        "fixed_common",
        "trajectory_profile",
        "seed",
    }.issubset(rows1[0])


if __name__ == "__main__":
    test_cyclic_pair_classifies_as_rank_one_cyclic()
    test_rank_two_pair_has_larger_noncyclic_invariant()
    test_identity_handling_is_explicit()
    test_deterministic_seed_reproduces_rows()
    print("all folded word-graph tests passed")
