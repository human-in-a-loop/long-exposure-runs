from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import probe_schreier_spectral_toy as probe


def test_deterministic_graph_construction_degree_and_symmetry():
    a = np.asarray([1, 2, 0])
    b = np.asarray([0, 2, 1])
    adjacency = probe.permutation_matrix_adjacency((a, b))
    assert np.allclose(adjacency, adjacency.T)
    assert np.allclose(adjacency.sum(axis=1), 4.0)
    assert adjacency[0, 0] == 2.0


def test_trace_identity_matches_eigenvalue_power_sum():
    a = np.asarray([1, 2, 3, 0])
    b = np.asarray([0, 2, 1, 3])
    adjacency = probe.permutation_matrix_adjacency((a, b))
    eigenvalues = np.linalg.eigvalsh(adjacency)
    for k in (2, 4, 6):
        matrix_trace = float(np.trace(np.linalg.matrix_power(adjacency, k)))
        eigen_trace = float(np.sum(eigenvalues**k))
        assert abs(matrix_trace - eigen_trace) < 1e-8


def test_tree_closed_walk_moments_for_four_regular_tree():
    assert probe.tree_closed_walk_moment(4, 2) == 4
    assert probe.tree_closed_walk_moment(4, 4) == 28
    assert probe.tree_closed_walk_moment(4, 6) == 232


def test_reproducible_sampling_under_fixed_seed():
    rows1, _ = probe.run_trials([8], 3, 12345, 4)
    rows2, _ = probe.run_trials([8], 3, 12345, 4)
    assert rows1 == rows2
    assert {"n", "trial", "observable", "value", "seed"}.issubset(rows1[0])


def test_top_nontrivial_gracefully_pads_when_count_exceeds_available():
    eigenvalues = np.asarray([4.0, 1.0, -1.0])
    values = probe.top_nontrivial(eigenvalues, 5)
    assert values[:2] == [1.0, -1.0]
    assert len(values) == 5
    assert np.isnan(values[-1])


if __name__ == "__main__":
    test_deterministic_graph_construction_degree_and_symmetry()
    test_trace_identity_matches_eigenvalue_power_sum()
    test_tree_closed_walk_moments_for_four_regular_tree()
    test_reproducible_sampling_under_fixed_seed()
    test_top_nontrivial_gracefully_pads_when_count_exceeds_available()
    print("all Schreier spectral toy tests passed")
