#!/usr/bin/env python3
# created: 2026-05-12T16:15:00Z
# cycle: 37
# run_id: run-2026-05-11T121649Z
# agent: worker
# milestone: M-EVIDART-1
"""Verify gate evidence artifact contract and validation boundaries."""

from __future__ import annotations

import csv
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
INPUT_ROOT = DATA / "production_target_bundle"

REPLAY_GATES = [
    "root_enrollment",
    "attestation_envelope",
    "trust_policy",
    "intake_custody",
    "adapter_conformance",
    "timebase_integrity",
    "redaction_integrity",
    "evidence_gatechain",
    "uncertainty_qualification",
    "causal_attribution",
    "dc001_dc002_threshold_replay",
    "planner_readiness_boundary",
    "final_handoff_traceability",
]


def run(script: str) -> None:
    subprocess.run([sys.executable, str(ROOT / script)], check=True)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
        rows = list(csv.DictReader(f))
    assert rows, f"{path.relative_to(ROOT)} is empty"
    return rows


def assert_nonblank_png(path: Path) -> None:
    assert path.exists(), f"missing {path.relative_to(ROOT)}"
    assert path.stat().st_size > 1000, f"blank or tiny figure: {path.relative_to(ROOT)}"


def verify_missing_required_payload_fields_rejected(schema: list[dict[str, str]]) -> None:
    bundle_root = INPUT_ROOT / "missing_required_payload_fields_probe"
    if bundle_root.exists():
        shutil.rmtree(bundle_root)
    bundle_root.mkdir(parents=True)
    manifest = {
        "bundle_id": "missing-required-payload-fields-probe",
        "evidence_label": "production_target",
        "measurement_run_id": "run-prod-001",
        "collector_id": "collector-prod-001",
        "topology_id": "topology-prod-001",
        "workload_id": "workload-prod-001",
        "model_version": "model-prod-001",
        "deployment_root_id": "root-prod-001",
        "claim_id": "claim-prod-001",
        "measurement_window_start": "2026-05-12T15:10:00Z",
        "measurement_window_end": "2026-05-12T15:50:00Z",
    }
    previous_digests: list[str] = []
    for row in schema:
        gate_name = row["gate_name"]
        payload = {
            "artifact_id": f"missing-fields-{gate_name}",
            "evidence_label": "production_target",
            "gate_name": gate_name,
            "gate_status": "pass",
            "valid_from": "2026-05-12T15:00:00Z",
            "valid_until": "2026-05-12T17:00:00Z",
            "upstream_artifact_digests": ";".join(previous_digests),
        }
        artifact_path = bundle_root / f"{gate_name}.json"
        artifact_path.write_text(json.dumps(payload, sort_keys=True))
        digest = hashlib.sha256(artifact_path.read_bytes()).hexdigest()
        manifest[row["manifest_boolean_field"]] = "true"
        manifest[row["evidence_path_field"]] = str(artifact_path.relative_to(ROOT))
        manifest[row["digest_field"]] = digest
        previous_digests.append(digest)
    (bundle_root / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True))

    try:
        run("scripts/validate_gate_evidence_artifacts.py")
        boundary = read_csv(DATA / "gate_evidence_replay_readiness_boundary.csv")
        probe = {row["bundle_id"]: row for row in boundary}["missing-required-payload-fields-probe"]
        assert probe["evidence_artifact_complete"] == "false", probe
        assert probe["ready_for_production_target_replay"] == "false", probe
        assert probe["blocked_reason"] == "missing_required_payload_field", probe
        assert probe["claim_credit_allowed"] == "false", probe
    finally:
        shutil.rmtree(bundle_root)
        run("scripts/validate_gate_evidence_artifacts.py")
        run("scripts/plot_gate_evidence_artifacts.py")


def main() -> None:
    run("scripts/build_gate_evidence_artifact_contract.py")
    run("scripts/validate_gate_evidence_artifacts.py")
    run("scripts/plot_gate_evidence_artifacts.py")

    schema = read_csv(DATA / "gate_evidence_artifact_schema.csv")
    assert [row["gate_name"] for row in schema] == REPLAY_GATES
    for row in schema:
        assert row["evidence_path_field"].endswith("_evidence_path"), row
        assert row["digest_field"].endswith("_evidence_sha256"), row
        assert row["payload_source"], row
        assert row["identity_binding"], row
        assert row["time_window"], row
        assert row["fail_closed_reason_if_absent"].startswith("missing_"), row
    verify_missing_required_payload_fields_rejected(schema)

    fields = read_csv(DATA / "gate_evidence_required_fields.csv")
    by_gate = {gate: set() for gate in REPLAY_GATES}
    for row in fields:
        if row["gate_name"] in by_gate:
            by_gate[row["gate_name"]].add(row["required_field"])
    for gate, required in by_gate.items():
        assert {"artifact_id", "evidence_label", "payload_digest", "upstream_artifact_digests", "identity_bindings"} <= required, gate

    boundary = read_csv(DATA / "gate_evidence_replay_readiness_boundary.csv")
    by_bundle = {row["bundle_id"]: row for row in boundary}
    required_failures = {
        "probe-manifest_only_gate_boolean": "missing_evidence_path",
        "probe-digest_mismatch": "digest_mismatch",
        "probe-missing_required_payload_field": "missing_required_payload_field",
        "probe-root_identity_mismatch": "root_identity_mismatch",
        "probe-collector_identity_mismatch": "collector_identity_mismatch",
        "probe-topology_model_workload_mismatch": "topology_model_workload_mismatch",
        "probe-evidence_window_outside_measurement_window": "evidence_window_outside_measurement_window",
        "probe-downstream_artifact_without_upstream_dependency": "downstream_artifact_without_upstream_dependency",
        "probe-artifact_with_non_production_evidence_label_attempting_promotion": "non_production_evidence_label",
    }
    for bundle_id, reason in required_failures.items():
        assert bundle_id in by_bundle, bundle_id
        row = by_bundle[bundle_id]
        assert row["evidence_artifact_complete"] == "false", row
        assert row["blocked_reason"] == reason, row

    complete = by_bundle["probe-complete_linked_artifacts"]
    assert complete["evidence_artifact_complete"] == "true", complete
    assert complete["ready_for_production_target_replay"] == "true", complete
    for row in boundary:
        assert row["production_calibrated"] == "false", row
        assert row["production_ready"] == "false", row
        assert row["threshold_success"] == "false", row
        assert row["causal_validity_granted"] == "false", row
        assert row["claim_credit_allowed"] == "false", row

    failures = {row["failure_mode"] for row in read_csv(DATA / "gate_evidence_failure_modes.csv")}
    for reason in set(required_failures.values()):
        assert reason in failures, reason

    assert_nonblank_png(DATA / "gate_evidence_dependency_graph.png")
    assert_nonblank_png(DATA / "gate_evidence_failure_modes.png")
    assert_nonblank_png(DATA / "gate_evidence_replay_readiness_boundary.png")
    print("OK: gate evidence artifact kit verified.")


if __name__ == "__main__":
    main()
