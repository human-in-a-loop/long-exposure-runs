# created: 2026-05-13T14:06:00Z
# cycle: 4
# run_id: run-2026-05-13T015136Z
# agent: worker
# milestone: M-INTAKE-1

"""Manual tests for M-INTAKE-1 package intake rehearsal."""

from __future__ import annotations

import csv
import importlib.util
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "physicalized-weights" / "scripts" / "evidence_pack_intake_rehearsal.py"
RESULTS_CSV = ROOT / "physicalized-weights" / "data" / "evidence_pack_intake_rehearsal_results.csv"
SUMMARY_JSON = ROOT / "physicalized-weights" / "data" / "evidence_pack_intake_rehearsal_summary.json"
FLOW_PNG = ROOT / "physicalized-weights" / "data" / "evidence_pack_intake_rehearsal_flow.png"


def load_rehearsal():
    spec = importlib.util.spec_from_file_location("evidence_pack_intake_rehearsal", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules["evidence_pack_intake_rehearsal"] = module
    spec.loader.exec_module(module)
    return module


rehearsal = load_rehearsal()
rehearsal.main()


def rows_by_case() -> dict[str, dict[str, str]]:
    with RESULTS_CSV.open(newline="", encoding="utf-8") as fh:
        return {row["case_id"]: row for row in csv.DictReader(fh)}


def summary() -> dict[str, object]:
    return json.loads(SUMMARY_JSON.read_text(encoding="utf-8"))


def test_shadow_and_canary_pass_intake_and_replay_non_reopening() -> None:
    rows = rows_by_case()
    for case_id in ["shadow_synthetic_filled_non_crossing", "canary_synthetic_filled_non_crossing"]:
        row = rows[case_id]
        assert row["dryrun_status"] == "ready_for_collection_not_evidence"
        assert row["intake_status"] == "intake_passed"
        assert row["replay_status"] == "threshold_evaluable_not_crossed"
        assert row["final_status"] == "threshold_evaluable_not_crossed"
        assert row["actual_reopen_candidate"] == "False"


def test_synthetic_counterfactual_crosses_but_is_not_actual() -> None:
    row = rows_by_case()["synthetic_counterfactual_crossing_non_actual"]
    assert row["intake_status"] == "intake_passed"
    assert row["replay_status"] == "synthetic_counterfactual_crossed"
    assert row["final_status"] == "synthetic_counterfactual_crossed"
    assert row["actual_reopen_candidate"] == "False"
    assert "source_type=synthetic" in row["replay_blocking_reasons"]


def test_handoff_mutations_are_blocked_before_replay() -> None:
    rows = rows_by_case()
    expected = {
        "stale_hash_after_handoff": "intake_hash_blocked",
        "trace_file_alias_after_handoff": "intake_manifest_blocked",
        "manifest_trace_source_mismatch": "intake_manifest_blocked",
        "threshold_mapping_changed_after_dryrun": "intake_threshold_blocked",
        "attestation_changed_after_hash": "intake_attestation_blocked",
        "raw_content_added_after_dryrun": "intake_privacy_blocked",
    }
    for case_id, status in expected.items():
        row = rows[case_id]
        assert row["intake_status"] == status
        assert row["replay_status"] == "not_run"
        assert row["final_status"] == "intake_blocked"
        assert row["blocking_reasons"] != "none"


def test_successful_intake_rows_preserve_hash_and_manifest() -> None:
    for row in rows_by_case().values():
        if row["intake_status"] == "intake_passed":
            assert row["hash_preserved"] == "True"
            assert row["manifest_preserved"] == "True"


def test_trace_file_alias_after_handoff_is_blocked() -> None:
    row = rows_by_case()["trace_file_alias_after_handoff"]
    assert row["intake_status"] == "intake_manifest_blocked"
    assert row["replay_status"] == "not_run"
    assert "manifest_preserved=false:trace_file" in row["blocking_reasons"]


def test_summary_zero_actual_and_required_counts() -> None:
    data = summary()
    assert data["actual_reopen_candidate_count"] == 0
    assert data["successful_intake_count"] >= 2
    assert data["blocked_before_replay_count"] >= 4
    assert data["all_successful_intakes_preserved"] is True
    assert FLOW_PNG.exists()
    assert FLOW_PNG.stat().st_size > 1000


def run() -> None:
    tests = [
        test_shadow_and_canary_pass_intake_and_replay_non_reopening,
        test_synthetic_counterfactual_crosses_but_is_not_actual,
        test_handoff_mutations_are_blocked_before_replay,
        test_successful_intake_rows_preserve_hash_and_manifest,
        test_trace_file_alias_after_handoff_is_blocked,
        test_summary_zero_actual_and_required_counts,
    ]
    for test in tests:
        test()
        print(f"PASS {test.__name__}")


if __name__ == "__main__":
    run()
