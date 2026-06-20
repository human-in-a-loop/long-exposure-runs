from pathlib import Path
import csv
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import analyze_schreier_trace_benchmark as bench


def test_tree_moments_match_m3_values_and_extend_to_ten():
    rows = bench.build_tree_rows(10)
    moments = {int(row["k"]): int(row["tree_moment"]) for row in rows}
    assert moments[2] == 4
    assert moments[4] == 28
    assert moments[6] == 232
    assert moments[8] == 2092
    assert moments[10] == 19864
    assert all(row["methods_agree"] for row in rows)


def test_odd_tree_moments_vanish():
    rows = bench.build_tree_rows(10)
    odd = [row for row in rows if int(row["k"]) % 2 == 1]
    assert odd
    assert all(int(row["tree_moment"]) == 0 for row in odd)
    assert all(row["odd_moment_zero"] for row in odd)


def test_sampling_reproducible_under_fixed_seed():
    rows1 = bench.run_trials(n_values=(12,), trials=2, seed=123, moments=(1, 2, 3, 4))
    rows2 = bench.run_trials(n_values=(12,), trials=2, seed=123, moments=(1, 2, 3, 4))
    assert rows1 == rows2
    assert {row.k for row in rows1} == {1, 2, 3, 4}


def test_classification_distinguishes_claim_types():
    trial_rows = bench.run_trials(n_values=(12, 16), trials=3, seed=456, moments=(2, 4, 6))
    variance_rows = bench.summarize_variance(trial_rows)
    rows = bench.classification_rows(variance_rows)
    classifications = {row["classification"] for row in rows}
    assert "proved_fixed_k_expectation" in classifications
    assert "numerical_variance_evidence" in classifications
    assert "hyperbolic_transfer_not_claimed" in classifications


def test_classification_uses_current_n_grid_not_default_grid():
    variance_rows = []
    for k, slope in ((2, -1.2), (4, -1.1), (6, -0.9)):
        for n in (12, 16):
            variance_rows.append(
                {
                    "k": k,
                    "n": n,
                    "loglog_variance_slope_for_k": slope,
                }
            )
    rows = bench.classification_rows(variance_rows)
    decision_rows = [row for row in rows if row["claim_status"] == "decision"]
    assert len(decision_rows) == 1
    assert decision_rows[0]["decision"] == "advance_schreier_benchmark_program"


def test_generated_classification_has_one_branch_decision_if_present():
    path = bench.CLASSIFICATION_PATH
    if not path.exists():
        return
    with path.open(newline="") as f:
        rows = list(csv.DictReader(f))
    decision_rows = [row for row in rows if row["claim_status"] == "decision"]
    assert len(decision_rows) == 1
    assert decision_rows[0]["decision"] in {
        "advance_schreier_benchmark_program",
        "preserve_as_computational_benchmark_only",
        "pivot_to_finite_nonshrinking_spectral_statistics",
    }


if __name__ == "__main__":
    test_tree_moments_match_m3_values_and_extend_to_ten()
    test_odd_tree_moments_vanish()
    test_sampling_reproducible_under_fixed_seed()
    test_classification_distinguishes_claim_types()
    test_classification_uses_current_n_grid_not_default_grid()
    test_generated_classification_has_one_branch_decision_if_present()
    print("all Schreier trace benchmark tests passed")
