# created: 2026-05-13T11:48:00Z
# cycle: 3
# run_id: run-2026-05-13T015136Z
# agent: worker
# milestone: M-PHASE3-SYNTH-1

from __future__ import annotations

import csv
import importlib.util
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "physicalized-weights/scripts/build_phase3_reopen_synthesis.py"


def load_builder():
    spec = importlib.util.spec_from_file_location("build_phase3_reopen_synthesis", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules["build_phase3_reopen_synthesis"] = module
    spec.loader.exec_module(module)
    return module


builder = load_builder()


def run_builder() -> None:
    assert builder.main() == 0


def read_claim_rows() -> list[dict[str, str]]:
    with (ROOT / "physicalized-weights/data/phase3_reopen_claim_matrix.csv").open(newline="") as handle:
        return list(csv.DictReader(handle))


def test_required_inputs_exist() -> None:
    for paths in builder.REQUIRED_INPUTS.values():
        for path in paths:
            assert path.exists(), path


def test_current_actual_reopen_counts_are_zero() -> None:
    run_builder()
    summary = json.loads((ROOT / "physicalized-weights/data/phase3_reopen_summary.json").read_text())
    pipeline = json.loads((ROOT / "physicalized-weights/data/reopen_pipeline_summary.json").read_text())
    packs = json.loads((ROOT / "physicalized-weights/data/evidence_pack_replay_summary.json").read_text())
    assert summary["actual_reopen_candidate_count"] == 0
    assert pipeline["actual_reopen_candidate_count"] == 0
    assert packs["actual_reopen_candidate_count"] == 0
    assert summary["current_artifacts_reopen"] is False


def test_final_synthesis_includes_phase3_conclusion() -> None:
    run_builder()
    text = (ROOT / "physicalized-weights/docs/final_synthesis.md").read_text()
    assert "Phase 3 Reopen-Pathway Addendum" in text
    assert "current evidence remains downgraded" in text
    assert "physicalized safety/filter is not a current performance/economic winner" in text
    assert builder.FUTURE_REOPEN_CONDITION in text


def test_reproducibility_mentions_all_phase3_scripts() -> None:
    run_builder()
    text = (ROOT / "physicalized-weights/docs/reproducibility.md").read_text()
    for command in builder.PHASE3_COMMANDS:
        assert command in text
    for command in builder.PHASE3_TEST_COMMANDS:
        assert command in text


def test_claim_matrix_contains_required_blocked_classes() -> None:
    run_builder()
    rows = read_claim_rows()
    classes = {row["evidence_class"] for row in rows}
    required = {
        "synthetic",
        "proxy/local",
        "vendor-only",
        "privacy-risk",
        "stale-hash",
        "unknown-threshold",
        "non-crossing measured packages",
    }
    assert required <= classes
    for row in rows:
        if row["evidence_class"] in required:
            assert row["accepted_or_rejected"] == "rejected_as_current_reopen_evidence"


def test_png_exists_and_is_regenerated_by_builder() -> None:
    run_builder()
    png = ROOT / "physicalized-weights/data/phase3_reopen_evidence_flow.png"
    before = png.read_bytes()
    assert before.startswith(b"\x89PNG\r\n\x1a\n")
    run_builder()
    after = png.read_bytes()
    assert after.startswith(b"\x89PNG\r\n\x1a\n")
    assert len(after) > 1000


def test_manifest_lists_phase3_outputs() -> None:
    run_builder()
    with (ROOT / "physicalized-weights/data/phase3_reopen_manifest.csv").open(newline="") as handle:
        rows = list(csv.DictReader(handle))
    paths = {row["artifact_path"] for row in rows}
    required = {
        "physicalized-weights/data/phase3_reopen_claim_matrix.csv",
        "physicalized-weights/data/phase3_reopen_summary.json",
        "physicalized-weights/data/phase3_reopen_evidence_flow.png",
        "physicalized-weights/docs/phase3_reopen_pathway_summary.md",
        "physicalized-weights/docs/final_synthesis.md",
        "physicalized-weights/docs/reproducibility.md",
    }
    assert required <= paths


def run_tests() -> None:
    tests = [
        test_required_inputs_exist,
        test_current_actual_reopen_counts_are_zero,
        test_final_synthesis_includes_phase3_conclusion,
        test_reproducibility_mentions_all_phase3_scripts,
        test_claim_matrix_contains_required_blocked_classes,
        test_png_exists_and_is_regenerated_by_builder,
        test_manifest_lists_phase3_outputs,
    ]
    for test in tests:
        test()
        print(f"PASS {test.__name__}")


if __name__ == "__main__":
    run_tests()
