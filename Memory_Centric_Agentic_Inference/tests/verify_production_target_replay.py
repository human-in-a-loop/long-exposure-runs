#!/usr/bin/env python3
# created: 2026-05-12T15:15:00Z
# cycle: 36
# run_id: run-2026-05-11T121649Z
# agent: worker
# milestone: M-PRODREPLAY-1
"""Verify real production-target replay fail-closed boundaries."""

from __future__ import annotations

import csv
import json
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
INPUT_ROOT = DATA / "production_target_bundle"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
        rows = list(csv.DictReader(f))
    assert rows, f"{path.relative_to(ROOT)} is empty"
    return rows


def assert_nonblank_png(path: Path) -> None:
    assert path.exists(), f"missing {path.relative_to(ROOT)}"
    assert path.stat().st_size > 1000, f"blank or tiny figure: {path.relative_to(ROOT)}"


def run_script(script: str) -> None:
    subprocess.run([sys.executable, str(ROOT / script)], check=True)


def verify_manifest_only_production_target_rejected() -> None:
    case_dir = INPUT_ROOT / "manifest_only_all_true"
    manifest = {
        "bundle_id": "manifest-only-all-true",
        "evidence_label": "production_target",
    }
    gates = [
        "root_enrolled",
        "attested",
        "trust_policy_admissible",
        "intake_custody_valid",
        "adapter_conformant",
        "timebase_valid",
        "redaction_admissible",
        "gatechain_passed",
        "statistically_robust",
        "causally_admissible",
        "threshold_passed",
        "planner_boundary_passed",
        "handoff_traceable",
    ]
    for gate in gates:
        manifest[gate] = "true"

    try:
        case_dir.mkdir(parents=True, exist_ok=True)
        with (case_dir / "manifest.json").open("w") as f:
            json.dump(manifest, f, indent=2, sort_keys=True)
        run_script("scripts/run_production_target_replay.py")
        forged_results = read_csv(DATA / "production_target_replay_results.csv")
        rows = [row for row in forged_results if row["bundle_id"] == "manifest-only-all-true"]
        assert rows, "forged production_target manifest was not evaluated"
        row = rows[0]
        assert row["replay_state"] == "real_telemetry_rejected", row
        assert row["first_failed_gate"] == "root_enrollment", row
        assert row["blocked_reason"] == "missing_root_enrollment_evidence", row
        assert row["claim_support_candidate"] == "false", row
        assert row["claim_credit_allowed"] == "false", row
    finally:
        if case_dir.exists():
            shutil.rmtree(case_dir)
        run_script("scripts/run_production_target_replay.py")
        run_script("scripts/plot_production_target_replay.py")


def main() -> None:
    results = read_csv(DATA / "production_target_replay_results.csv")
    trace = read_csv(DATA / "production_target_replay_gate_trace.csv")
    boundary = read_csv(DATA / "production_target_replay_claim_boundary.csv")
    absence = read_csv(DATA / "production_target_replay_absence_report.csv")

    absence_state = absence[0]["absence_state"]
    if absence_state == "no_real_telemetry_available":
        absence_rows = [row for row in results if row["replay_state"] == "no_real_telemetry_available"]
        assert absence_rows, "absence did not materialize in replay results"
        assert absence_rows[0]["blocked_reason"] == "no_production_target_bundle_found"
        assert absence_rows[0]["production_calibrated"] == "false"
        assert absence_rows[0]["production_ready"] == "false"
        assert absence_rows[0]["claim_credit_allowed"] == "false"

    non_production = [row for row in results if row["evidence_label"] and row["evidence_label"] != "production_target"]
    assert non_production, "negative controls for non-production labels are missing"
    required_labels = {
        "synthetic_production_fixture",
        "host_local_proxy",
        "adapter_conformance_fixture",
        "production_intake_fixture",
        "test_attestation_fixture",
        "operator_trust_policy_fixture",
        "uncertainty_fixture",
        "causal_fixture",
    }
    seen = {row["evidence_label"] for row in non_production}
    missing = required_labels - seen
    assert not missing, f"missing negative-control labels: {sorted(missing)}"
    for row in non_production:
        assert row["production_calibrated"] == "false", row
        assert row["production_ready"] == "false", row
        assert row["claim_credit_allowed"] == "false", row
        assert row["claim_support_candidate"] == "false", row

    for row in results:
        if row["replay_state"] == "real_telemetry_rejected":
            assert row["threshold_replay_attempted"] == "false", row
            assert row["readiness_update_allowed"] == "false", row
            assert row["claim_credit_allowed"] == "false", row

    causal = read_csv(DATA / "causal_attribution_results.csv")
    robust_invalid = [row for row in causal if row["robust_statistical_effect"] == "true" and row["causal_status"] != "causally_admissible"]
    assert robust_invalid, "expected robust-but-causally-invalid causal controls"
    assert all(row["readiness_update_allowed"] == "false" and row["claim_credit_allowed"] == "false" for row in robust_invalid)

    candidates = [row for row in results if row["claim_support_candidate"] == "true"]
    for row in candidates:
        assert row["evidence_label"] == "production_target", row
        assert row["first_failed_gate"] == "", row
    assert all(row["automatic_architecture_endorsement"] == "false" for row in boundary)
    assert trace, "gate trace missing"
    assert_nonblank_png(DATA / "production_target_replay_gate_trace.png")
    assert_nonblank_png(DATA / "production_target_replay_claim_boundary.png")
    verify_manifest_only_production_target_rejected()
    print("OK: production target replay verified.")


if __name__ == "__main__":
    main()
