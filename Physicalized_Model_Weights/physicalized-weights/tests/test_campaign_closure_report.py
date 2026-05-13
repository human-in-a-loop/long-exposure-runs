# created: 2026-05-13T19:10:00Z
# cycle: 9
# run_id: run-2026-05-13T015136Z
# agent: worker
# milestone: M-CLOSURE-1

from __future__ import annotations

import csv
import importlib.util
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "physicalized-weights/scripts/build_campaign_closure_report.py"


def load_builder():
    spec = importlib.util.spec_from_file_location("build_campaign_closure_report", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules["build_campaign_closure_report"] = module
    spec.loader.exec_module(module)
    return module


builder = load_builder()


def run_builder() -> None:
    assert builder.main() == 0


def read_summary() -> dict:
    return json.loads((ROOT / "physicalized-weights/data/campaign_closure_summary.json").read_text(encoding="utf-8"))


def read_claims() -> list[dict[str, str]]:
    with (ROOT / "physicalized-weights/data/campaign_closure_claim_disposition.csv").open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def test_summary_preserves_zero_current_claims() -> None:
    run_builder()
    summary = read_summary()
    assert summary["current_superiority_claim_count"] == 0
    assert summary["actual_reopen_candidate_count"] == 0
    assert summary["new_reopen_gate_count"] == 0
    assert summary["current_artifacts_reopen"] is False


def test_claim_disposition_table_has_required_claims() -> None:
    run_builder()
    claim_ids = {row["claim_id"] for row in read_claims()}
    required = {
        "full_frontier_fixed_weight_physicalization",
        "safety_filter_performance_superiority",
        "hybrid_architecture_failure_mode_value",
        "prototype_hdl_evidence",
        "future_measured_reopen_path",
        "non_safety_target_robustness",
        "campaign_deferral_state",
    }
    assert required <= claim_ids


def test_every_claim_has_existing_supporting_artifact() -> None:
    run_builder()
    for row in read_claims():
        supports = [item.strip() for item in row["supporting_artifacts"].split(";") if item.strip()]
        assert supports, row["claim_id"]
        for support in supports:
            assert (ROOT / support).exists(), support


def test_executive_summary_does_not_mislabel_substitutes_as_measured() -> None:
    run_builder()
    text = (ROOT / "physicalized-weights/docs/campaign_executive_summary.md").read_text(encoding="utf-8").lower()
    guarded = ["synthetic", "proxy", "template", "rehearsal", "vendor-only", "dry-run"]
    assert "are not measured evidence" in text
    for word in guarded:
        assert word in text
    assert "synthetic measured evidence" not in text
    assert "proxy measured evidence" not in text
    assert "template measured evidence" not in text
    assert "rehearsal measured evidence" not in text


def test_final_synthesis_contains_closure_path_and_deferral_state() -> None:
    run_builder()
    text = (ROOT / "physicalized-weights/docs/final_synthesis.md").read_text(encoding="utf-8")
    assert "Campaign Closure Disposition" in text
    assert "physicalized-weights/docs/campaign_closure_report.md" in text
    assert "closed_under_current_evidence_deferred_until_valid_measured_package" in text
    assert "current_superiority_claim_count = 0" in text


def test_manifest_covers_claim_supports_and_outputs() -> None:
    run_builder()
    with (ROOT / "physicalized-weights/data/campaign_closure_manifest.csv").open(newline="", encoding="utf-8") as handle:
        manifest_paths = {row["artifact_path"] for row in csv.DictReader(handle)}
    required_outputs = {
        "physicalized-weights/docs/campaign_closure_report.md",
        "physicalized-weights/docs/campaign_executive_summary.md",
        "physicalized-weights/data/campaign_closure_claim_disposition.csv",
        "physicalized-weights/data/campaign_closure_manifest.csv",
        "physicalized-weights/data/campaign_closure_summary.json",
        "physicalized-weights/data/campaign_closure_evidence_flow.png",
    }
    assert required_outputs <= manifest_paths
    for row in read_claims():
        for support in [item.strip() for item in row["supporting_artifacts"].split(";") if item.strip()]:
            assert support in manifest_paths, f"{row['claim_id']} support missing from manifest: {support}"


def test_png_exists_and_is_nontrivial() -> None:
    run_builder()
    png = ROOT / "physicalized-weights/data/campaign_closure_evidence_flow.png"
    data = png.read_bytes()
    assert data.startswith(b"\x89PNG\r\n\x1a\n")
    assert len(data) > 1000


def run_tests() -> None:
    tests = [
        test_summary_preserves_zero_current_claims,
        test_claim_disposition_table_has_required_claims,
        test_every_claim_has_existing_supporting_artifact,
        test_executive_summary_does_not_mislabel_substitutes_as_measured,
        test_final_synthesis_contains_closure_path_and_deferral_state,
        test_manifest_covers_claim_supports_and_outputs,
        test_png_exists_and_is_nontrivial,
    ]
    for test in tests:
        test()
        print(f"PASS {test.__name__}")


if __name__ == "__main__":
    run_tests()
