# created: 2026-05-13T04:48:00Z
# cycle: 1
# run_id: run-2026-05-13T015136Z
# agent: worker
# milestone: M-FINAL-1

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_manifest() -> list[dict[str, str]]:
    with (ROOT / "physicalized-weights/data/evidence_manifest.csv").open(newline="") as handle:
        return list(csv.DictReader(handle))


def test_final_synthesis_mentions_validated_milestones() -> None:
    text = (ROOT / "physicalized-weights/docs/final_synthesis.md").read_text()
    for milestone in [
        "M-TAX-1",
        "M-MODEL-1",
        "M-BASE-1",
        "M-TARGET-1",
        "M-ARCH-1",
        "M-PROTO-1",
        "M-FINAL-1",
        "M-CAL-1",
        "M-WORKLOAD-1",
        "M-SWBASE-2",
    ]:
        assert milestone in text


def test_manifest_includes_major_artifacts_and_existing_paths() -> None:
    rows = load_manifest()
    paths = {row["path"] for row in rows}
    required = {
        "physicalized-weights/docs/taxonomy_and_null.md",
        "physicalized-weights/data/breakeven_summary.json",
        "physicalized-weights/data/target_scores_summary.json",
        "physicalized-weights/docs/hybrid_safety_filter_architecture.md",
        "physicalized-weights/data/hybrid_arch_summary.json",
        "physicalized-weights/data/prototype_summary.json",
        "physicalized-weights/data/hdl_sim_results.csv",
        "physicalized-weights/data/prototype_verification_closure.json",
        "physicalized-weights/docs/final_synthesis.md",
        "physicalized-weights/docs/reproducibility.md",
        "physicalized-weights/data/final_evidence_map.png",
        "physicalized-weights/data/phase2_claim_matrix.csv",
        "physicalized-weights/data/phase2_synthesis_summary.json",
        "physicalized-weights/data/phase2_evidence_map.png",
        "physicalized-weights/docs/phase2_synthesis_downgrade.md",
    }
    assert required <= paths
    for row in rows:
        assert (ROOT / row["path"]).exists(), row["path"]


def test_artifact_hashes_are_current() -> None:
    for row in load_manifest():
        artifact_hash = row["artifact_hash"]
        assert len(artifact_hash) == 64
        int(artifact_hash, 16)
        assert artifact_hash == sha256(ROOT / row["path"])


def test_final_claims_have_evidence_labels() -> None:
    text = (ROOT / "physicalized-weights/docs/final_synthesis.md").read_text()
    for label in ["sourced", "modeled", "simulated", "synthesized", "inferred", "speculative"]:
        assert label in text
    assert "Evidence-Labeled Claim Table" in text
    manifest_types = {row["evidence_type"] for row in load_manifest()}
    assert {"sourced", "modeled", "simulated", "synthesized", "inferred", "speculative"} <= manifest_types


def test_falsification_and_reopen_rules_present() -> None:
    text = (ROOT / "physicalized-weights/docs/final_synthesis.md").read_text()
    assert "Falsification Roadmap" in text
    assert "Reopen `M-PROTO-1`" in text
    assert "compiled Verilator later disagrees" in text
    assert "HDL hash changes" in text


def test_no_full_frontier_fixed_weight_promotion() -> None:
    text = (ROOT / "physicalized-weights/docs/final_synthesis.md").read_text().lower()
    assert "full frontier llm dense weights should not be burned permanently" in text
    forbidden = [
        "full frontier llm dense weights should be burned",
        "full frontier-model fixed-weight physicalization is supported",
        "burn full frontier",
    ]
    for phrase in forbidden:
        assert phrase not in text


def test_final_summary_schema() -> None:
    summary = json.loads((ROOT / "physicalized-weights/data/final_synthesis_summary.json").read_text())
    assert summary["milestone_id"] == "M-FINAL-1"
    assert summary["status"] == "validated"
    assert summary["prototype_closure_status"] == "validated"
    assert summary["compiled_verilator_status"] == "blocked_make_unavailable"
    assert summary["phase2_hybrid_workload_wins"] == 0
    assert summary["phase2_preserved_case_winner"] == "programmable_accelerator"
    for evidence_type in ["sourced", "modeled", "simulated", "synthesized", "inferred", "speculative"]:
        assert summary["evidence_type_counts"][evidence_type] > 0


def test_phase2_downgrade_addendum_present() -> None:
    text = (ROOT / "physicalized-weights/docs/final_synthesis.md").read_text()
    assert "Phase 2 Addendum" in text
    assert "hybrid physicalized safety/filter wins zero workload scenarios" in text
    assert "performance/economic superiority" in text


def run_tests() -> None:
    tests = [
        test_final_synthesis_mentions_validated_milestones,
        test_manifest_includes_major_artifacts_and_existing_paths,
        test_artifact_hashes_are_current,
        test_final_claims_have_evidence_labels,
        test_falsification_and_reopen_rules_present,
        test_no_full_frontier_fixed_weight_promotion,
        test_final_summary_schema,
        test_phase2_downgrade_addendum_present,
    ]
    for test in tests:
        test()
        print(f"PASS {test.__name__}")


if __name__ == "__main__":
    run_tests()
