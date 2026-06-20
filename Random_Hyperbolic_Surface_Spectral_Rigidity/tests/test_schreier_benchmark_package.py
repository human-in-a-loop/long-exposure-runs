from pathlib import Path
import csv
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_schreier_benchmark_package as pkg


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def test_source_artifacts_exist():
    missing = [rel for _, rel, _ in pkg.SOURCE_ARTIFACTS if not (ROOT / rel).exists()]
    assert missing == []


def test_claim_ledger_contains_theorem_package_core():
    claim_ids = {row["claim_id"] for row in pkg.claim_rows()}
    assert {
        "fixed_k_expectation",
        "tree_word_separation",
        "fixed_pair_covariance",
        "fixed_k_variance",
        "no_hyperbolic_transfer",
    } <= claim_ids

    theorem_or_lemma = [row for row in pkg.claim_rows() if row["claim_type"] in {"theorem", "lemma"}]
    assert len(theorem_or_lemma) >= 4


def test_scope_firewall_has_required_negative_rows():
    firewall = {row["boundary_item"]: row for row in pkg.firewall_rows()}
    for item in [
        "hyperbolic_random_covers",
        "selberg_trace_transfer",
        "adjacency_to_laplacian_transfer",
        "shrinking_local_spectral_windows",
    ]:
        assert firewall[item]["classification"] == "not_claimed"
        assert firewall[item]["package_position"] == "outside_scope"


def test_no_claim_classifies_schreier_as_hyperbolic_random_cover_result():
    for row in pkg.claim_rows():
        text = " ".join(str(value).lower() for value in row.values())
        assert "proved_for_hyperbolic" not in text
        assert "hyperbolic random-cover result" not in text


def test_generated_outputs_are_consistent_if_present():
    if not pkg.CLAIM_LEDGER.exists():
        return

    claim_rows = rows(pkg.CLAIM_LEDGER)
    claim_ids = {row["claim_id"] for row in claim_rows}
    assert "fixed_k_variance" in claim_ids
    assert "no_hyperbolic_transfer" in claim_ids

    artifact_rows = rows(pkg.ARTIFACT_INDEX)
    artifact_paths = {row["artifact_path"] for row in artifact_rows}
    for _, rel, _ in pkg.SOURCE_ARTIFACTS:
        assert rel in artifact_paths
    for _, rel, _ in pkg.M33_ARTIFACTS:
        assert rel in artifact_paths

    missing = [row["artifact_path"] for row in artifact_rows if row["exists"] != "True"]
    assert missing == []


if __name__ == "__main__":
    test_source_artifacts_exist()
    test_claim_ledger_contains_theorem_package_core()
    test_scope_firewall_has_required_negative_rows()
    test_no_claim_classifies_schreier_as_hyperbolic_random_cover_result()
    test_generated_outputs_are_consistent_if_present()
    print("all Schreier benchmark package tests passed")
