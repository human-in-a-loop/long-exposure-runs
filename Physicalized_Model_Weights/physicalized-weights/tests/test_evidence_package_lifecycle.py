# created: 2026-05-13T15:48:00Z
# cycle: 5
# run_id: run-2026-05-13T015136Z
# agent: worker
# milestone: M-LIFECYCLE-1

"""Direct tests for the evidence-package lifecycle state machine."""

from __future__ import annotations

import csv
import importlib.util
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "physicalized-weights" / "scripts" / "evidence_package_lifecycle.py"
DATA = ROOT / "physicalized-weights" / "data"


def load_module():
    spec = importlib.util.spec_from_file_location("evidence_package_lifecycle", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules["evidence_package_lifecycle"] = module
    spec.loader.exec_module(module)
    return module


lifecycle = load_module()
lifecycle.main()


def read_results() -> dict[str, dict[str, str]]:
    with (DATA / "evidence_package_lifecycle_results.csv").open(newline="", encoding="utf-8") as fh:
        return {row["case_id"]: row for row in csv.DictReader(fh)}


def read_summary() -> dict:
    return json.loads((DATA / "evidence_package_lifecycle_summary.json").read_text(encoding="utf-8"))


def assert_true(value: bool, message: str) -> None:
    if not value:
        raise AssertionError(message)


def test_current_and_nonactual_artifacts_do_not_reopen() -> None:
    summary = read_summary()
    rows = read_results()
    assert_true(summary["actual_reopen_candidate_count"] == 0, "current artifacts must not reopen")
    for case_id, row in rows.items():
        if row["current_artifact"] == "True":
            assert_true(row["actual_reopen_candidate"] == "False", f"{case_id} is current but reopened")
            assert_true(row["terminal_state"] != "actual_reopen_candidate", f"{case_id} reached candidate terminal state")


def test_dryrun_and_intake_cannot_skip_to_reopen() -> None:
    rows = read_results()
    assert_true(rows["dryrun_complete_template_only"]["terminal_state"] == "dryrun_ready_not_evidence", "dry-run skipped state")
    assert_true(rows["intake_shadow_synthetic_non_crossing"]["terminal_state"] == "intake_rehearsed_not_evidence", "shadow intake skipped state")
    assert_true(rows["intake_canary_synthetic_non_crossing"]["terminal_state"] == "intake_rehearsed_not_evidence", "canary intake skipped state")
    assert_true(rows["dryrun_complete_template_only"]["reopen_allowed"] == "False", "dry-run allowed reopen")


def test_stale_hash_and_unknown_threshold_stop_before_uncertainty() -> None:
    rows = read_results()
    for case_id in ("stale_trace_hash", "unknown_threshold_mapping"):
        row = rows[case_id]
        assert_true(row["terminal_state"] == "replay_blocked", f"{case_id} did not replay-block")
        assert_true(row["threshold_evaluated"] == "False", f"{case_id} reached threshold")
        assert_true(row["uncertainty_evaluated"] == "False", f"{case_id} reached uncertainty")


def test_noisy_point_crossing_is_inconclusive() -> None:
    row = read_results()["noisy_point_crossing_actual_like_blocked_by_uncertainty"]
    assert_true(row["terminal_state"] == "uncertainty_inconclusive", "noisy point crossing reopened")
    assert_true(row["reopen_allowed"] == "False", "noisy point crossing allowed reopen")
    assert_true(row["owning_gate"] == "M-UNCERTAINTY-1", "wrong owner for noisy point crossing")


def test_durable_synthetic_crossing_is_nonactual() -> None:
    rows = read_results()
    row = rows["uncertainty_durable_synthetic_control"]
    assert_true(row["terminal_state"] == "statistically_durable_nonactual", "durable synthetic not nonactual")
    assert_true(row["reopen_allowed"] == "False", "durable synthetic allowed reopen")
    crossed = rows["synthetic_counterfactual_threshold_crossing"]
    assert_true(crossed["terminal_state"] == "threshold_crossed_nonactual", "threshold synthetic did not stop as nonactual")


def test_hypothetical_control_is_only_candidate_branch() -> None:
    rows = read_results()
    candidates = [row for row in rows.values() if row["terminal_state"] == "actual_reopen_candidate"]
    assert_true(len(candidates) == 1, f"unexpected candidate branch count: {len(candidates)}")
    candidate = candidates[0]
    assert_true(candidate["case_id"] == "hypothetical_actual_measured_durable_candidate_control", "wrong candidate branch")
    assert_true(candidate["hypothetical_actual_candidate_control"] == "True", "candidate branch not labeled hypothetical")
    assert_true(candidate["actual_reopen_candidate"] == "False", "hypothetical counted as current actual")
    summary = read_summary()
    assert_true(summary["hypothetical_actual_candidate_control_count"] == 1, "missing hypothetical count")


def test_current_candidate_branch_is_not_masked_by_accounting() -> None:
    base = next(row for row in lifecycle.DEFAULT_CASES if row["case_id"] == "hypothetical_actual_measured_durable_candidate_control")
    probe = dict(base)
    probe["case_id"] = "current_actual_candidate_accounting_probe"
    probe["hypothetical_control"] = "false"
    probe["current_artifact"] = "true"
    row = lifecycle.classify(probe)
    assert_true(row["terminal_state"] == "actual_reopen_candidate", "probe did not reach candidate branch")
    assert_true(row["actual_reopen_candidate"] == "True", "candidate flag was masked")
    summary = lifecycle.write_summary([row])
    assert_true(summary["actual_reopen_candidate_count"] == 1, "current candidate count was masked")
    assert_true(summary["current_artifacts_reopen"] is True, "current reopen flag was masked")
    lifecycle.main()


def test_every_row_has_required_terminal_fields() -> None:
    rows = read_results()
    for case_id, row in rows.items():
        for field in ("owning_gate", "terminal_state", "reopen_allowed", "rationale"):
            assert_true(bool(row[field]), f"{case_id} missing {field}")
        assert_true(row["status_matches_expected"] == "True", f"{case_id} expected-state mismatch")


def test_summary_and_png() -> None:
    summary = read_summary()
    png = DATA / "evidence_package_lifecycle_flow.png"
    assert_true(summary["status_mismatches"] == [], "status mismatches present")
    assert_true(summary["terminal_state_counts"]["replay_blocked"] >= 2, "blocked branches undercovered")
    assert_true(summary["terminal_state_counts"]["statistically_durable_nonactual"] >= 1, "durable nonactual undercovered")
    assert_true(png.exists() and png.stat().st_size > 1000, "PNG missing or trivial")


def main() -> None:
    tests = [
        test_current_and_nonactual_artifacts_do_not_reopen,
        test_dryrun_and_intake_cannot_skip_to_reopen,
        test_stale_hash_and_unknown_threshold_stop_before_uncertainty,
        test_noisy_point_crossing_is_inconclusive,
        test_durable_synthetic_crossing_is_nonactual,
        test_hypothetical_control_is_only_candidate_branch,
        test_current_candidate_branch_is_not_masked_by_accounting,
        test_every_row_has_required_terminal_fields,
        test_summary_and_png,
    ]
    for test in tests:
        test()
        print("PASS", test.__name__)


if __name__ == "__main__":
    main()
