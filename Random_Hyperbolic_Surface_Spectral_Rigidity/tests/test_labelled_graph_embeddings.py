from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import probe_common_fixed_points as base
import probe_labelled_graph_embeddings as probe


def test_exact_and_monte_carlo_calibrate_on_single_loop():
    template = next(t for t in probe.TEMPLATES if t.template == "single_label_cycle")
    exact_count, exact_probability = probe.exact_embedding_count(template, 4)
    estimate, probability, _ = probe.monte_carlo_embedding_count(template, 4, 2000, np.random.SeedSequence(123))
    assert exact_count == 1.0
    assert exact_probability == 0.25
    assert abs(estimate - exact_count) < 0.25
    assert abs(probability - exact_probability) < 0.07


def test_no_edge_graph_has_falling_factorial_embeddings():
    template = probe.LabelledTemplate("free", (0, 1, 2), (), "control", "free injective vertices")
    exact_count, probability = probe.exact_embedding_count(template, 5)
    assert exact_count == 5 * 4 * 3
    assert probability == 1.0


def test_impossible_same_label_constraints_return_zero():
    outgoing = probe.LabelledTemplate("bad_out", (0, 1, 2), ((0, 1, "a"), (0, 2, "a")), "bad", "bad outgoing")
    incoming = probe.LabelledTemplate("bad_in", (0, 1, 2), ((1, 0, "a"), (2, 0, "a")), "bad", "bad incoming")
    perm = np.asarray([1, 2, 0])
    perms = {"a": perm, "A": base.invert_perm(perm)}
    assert probe.count_embeddings_for_perms(outgoing, 3, perms) == 0
    assert probe.count_embeddings_for_perms(incoming, 3, perms) == 0


def test_inverse_label_constraints_reverse_orientation_in_estimator():
    template = probe.LabelledTemplate("inverse_pair", (0, 1), ((0, 1, "a"), (0, 1, "A")), "rank_one", "edge and inverse edge")
    exact_count, exact_probability = probe.exact_embedding_count(template, 4)
    estimate, probability, _ = probe.monte_carlo_embedding_count(template, 4, 20, np.random.SeedSequence(123))
    assert abs(exact_count - estimate) < 1e-12
    assert abs(exact_probability - probability) < 1e-12


def test_deterministic_seed_reproduces_rows():
    rows1 = probe.result_rows([3], 20, 99, 3)
    rows2 = probe.result_rows([3], 20, 99, 3)
    assert rows1 == rows2
    assert {
        "n",
        "sample_mode",
        "template",
        "vertices",
        "edges",
        "labels_used",
        "cyclomatic_rank",
        "is_rank_one_template",
        "embedding_count_estimate",
        "success_probability",
        "naive_power",
        "normalized_count",
        "seed",
    }.issubset(rows1[0])


def test_template_invariants_separate_rank_one_and_figure_eight():
    single = next(t for t in probe.TEMPLATES if t.template == "single_label_cycle")
    figure = next(t for t in probe.TEMPLATES if t.template == "figure_eight_ab")
    inv_single = probe.template_invariants(single)
    inv_figure = probe.template_invariants(figure)
    assert inv_single["is_rank_one_template"] == 1
    assert inv_single["labels_used"] == "a"
    assert inv_figure["is_rank_one_template"] == 0
    assert inv_figure["labels_used"] == "a b"
    assert inv_figure["cyclomatic_rank"] > inv_single["cyclomatic_rank"]


if __name__ == "__main__":
    test_exact_and_monte_carlo_calibrate_on_single_loop()
    test_no_edge_graph_has_falling_factorial_embeddings()
    test_impossible_same_label_constraints_return_zero()
    test_inverse_label_constraints_reverse_orientation_in_estimator()
    test_deterministic_seed_reproduces_rows()
    test_template_invariants_separate_rank_one_and_figure_eight()
    print("all labelled graph embedding tests passed")
