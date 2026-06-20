# created: 2026-05-13T16:50:00Z
# cycle: 6
# run_id: run-2026-05-13T015136Z
# agent: worker
# milestone: M-PHASE4-SYNTH-1

from __future__ import annotations

import csv
import importlib.util
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "physicalized-weights/scripts/build_phase4_reopen_synthesis.py"


def load_builder():
    spec = importlib.util.spec_from_file_location("build_phase4_reopen_synthesis", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules["build_phase4_reopen_synthesis"] = module
    spec.loader.exec_module(module)
    return module


builder = load_builder()


def run_builder() -> None:
    assert builder.main() == 0


def read_summary() -> dict:
    return json.loads((ROOT / "physicalized-weights/data/phase4_reopen_summary.json").read_text())


def read_claim_rows() -> list[dict[str, str]]:
    with (ROOT / "physicalized-weights/data/phase4_reopen_claim_matrix.csv").open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def read_manifest_rows() -> list[dict[str, str]]:
    with (ROOT / "physicalized-weights/data/phase4_reopen_manifest.csv").open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def test_summary_preserves_non_reopen_accounting() -> None:
    run_builder()
    summary = read_summary()
    assert summary["current_artifacts_reopen"] is False
    assert summary["actual_reopen_candidate_count"] == 0
    assert summary["hypothetical_actual_candidate_control_count"] == 1
    assert "M-LIFECYCLE-1" in summary["integrated_milestones"]


def test_final_synthesis_has_uncertainty_and_lifecycle_rule() -> None:
    run_builder()
    text = (ROOT / "physicalized-weights/docs/final_synthesis.md").read_text(encoding="utf-8")
    assert "Phase 4 Reopen Lifecycle Synthesis" in text
    assert "UCB_alpha(H - B) < 0" in text
    assert "M-LIFECYCLE-1" in text
    assert "hypothetical_actual_candidate_control_count = 1" in text
    assert "not current measured evidence" in text


def test_claim_matrix_contains_required_rows() -> None:
    run_builder()
    rows = read_claim_rows()
    ids = {row["claim_id"] for row in rows}
    required = {
        "phase2_performance_superiority_falsified",
        "hybrid_architecture_still_valid_as_failure_mode_study",
        "production_measurement_required",
        "evidence_pack_replay_required",
        "operator_dryrun_is_non_evidence",
        "intake_rehearsal_is_non_evidence",
        "uncertainty_margin_required",
        "lifecycle_candidate_branch_is_hypothetical_only",
        "current_artifacts_do_not_reopen",
        "future_reopen_condition",
    }
    assert required <= ids


def test_manifest_lists_phase4_outputs() -> None:
    run_builder()
    paths = {row["artifact_path"] for row in read_manifest_rows()}
    required = {
        "physicalized-weights/docs/phase4_reopen_lifecycle_synthesis.md",
        "physicalized-weights/docs/final_synthesis.md",
        "physicalized-weights/docs/reproducibility.md",
        "physicalized-weights/data/phase4_reopen_claim_matrix.csv",
        "physicalized-weights/data/phase4_reopen_manifest.csv",
        "physicalized-weights/data/phase4_reopen_summary.json",
        "physicalized-weights/data/phase4_reopen_lifecycle_flow.png",
    }
    assert required <= paths


def test_manifest_covers_every_claim_support() -> None:
    run_builder()
    paths = {row["artifact_path"] for row in read_manifest_rows()}
    for row in read_claim_rows():
        supports = [item.strip() for item in row["supporting_artifacts"].split(";") if item.strip()]
        assert supports, row["claim_id"]
        for support in supports:
            assert (ROOT / support).exists(), support
            assert support in paths, f"{row['claim_id']} support missing from manifest: {support}"


def test_no_nonactual_claim_is_current_measured_evidence() -> None:
    run_builder()
    rows = read_claim_rows()
    guarded_kinds = {"template_dryrun", "synthetic_safe_handoff_rehearsal", "lifecycle_state_machine_control"}
    for row in rows:
        if row["evidence_kind"] in guarded_kinds:
            assert row["current_measured_evidence"] == "false"
        if "synthetic" in row["evidence_kind"] or "template" in row["evidence_kind"]:
            assert row["claim_class"] in {"non_evidence", "positive_control_only"}


def test_report_and_reproducibility_are_replayable() -> None:
    run_builder()
    report = (ROOT / "physicalized-weights/docs/phase4_reopen_lifecycle_synthesis.md").read_text(encoding="utf-8")
    repro = (ROOT / "physicalized-weights/docs/reproducibility.md").read_text(encoding="utf-8")
    for command in builder.PHASE4_COMMANDS:
        assert command in report
        assert command in repro
    for command in builder.PHASE4_TEST_COMMANDS:
        assert command in report
        assert command in repro


def test_png_exists_and_is_nontrivial() -> None:
    run_builder()
    png = ROOT / "physicalized-weights/data/phase4_reopen_lifecycle_flow.png"
    data = png.read_bytes()
    assert data.startswith(b"\x89PNG\r\n\x1a\n")
    assert len(data) > 1000


def run_tests() -> None:
    tests = [
        test_summary_preserves_non_reopen_accounting,
        test_final_synthesis_has_uncertainty_and_lifecycle_rule,
        test_claim_matrix_contains_required_rows,
        test_manifest_lists_phase4_outputs,
        test_manifest_covers_every_claim_support,
        test_no_nonactual_claim_is_current_measured_evidence,
        test_report_and_reproducibility_are_replayable,
        test_png_exists_and_is_nontrivial,
    ]
    for test in tests:
        test()
        print(f"PASS {test.__name__}")


if __name__ == "__main__":
    run_tests()
