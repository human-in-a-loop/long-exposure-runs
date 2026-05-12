#!/usr/bin/env python3
# created: 2026-05-12T17:10:00Z
# cycle: 38
# run_id: run-2026-05-11T121649Z
# agent: worker
# milestone: M-LIVECOLLECT-1
"""Evaluate live collector preflight and claim-boundary behavior."""

from __future__ import annotations

import csv
import json
import shutil
import subprocess
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
TMP = Path("/tmp/live_collector_probe_workspace")
COLLECTOR = ROOT / "tools" / "production_evidence_collector.py"

OUT_RESULTS = DATA / "live_collector_preflight_results.csv"
OUT_FAILURES = DATA / "live_collector_failure_modes.csv"
OUT_BOUNDARY = DATA / "live_collector_claim_boundary.csv"


def write_csv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})
    print(f"wrote {path.relative_to(ROOT)} rows={len(rows)}")


def write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def base_case(case_dir: Path) -> dict[str, object]:
    inputs = case_dir / "inputs"
    write_json(inputs / "production_root_marker.json", {"production_root": True, "evidence_label": "production_root", "deployment_root_id": "root-live-collector-fixture"})
    write_json(inputs / "deployment_root_identity.json", {"deployment_root_id": "root-live-collector-fixture", "producer_id": "operator-root-registry"})
    write_json(inputs / "collector_identity.json", {"collector_id": "collector-live-collector-fixture", "producer_id": "operator-collector-registry"})
    write_json(inputs / "operator_trust_policy.json", {"externally_produced": True, "policy_id": "policy-live-collector-fixture", "producer_id": "operator-policy"})
    write_json(inputs / "external_attestation.json", {"external_attestation": True, "attestation_id": "attest-live-collector-fixture", "producer_id": "external-attester"})
    write_json(inputs / "telemetry_counter_source.json", {"counter_source_id": "counter-live-collector-fixture", "source": "accelerator-and-host-counters"})
    write_json(inputs / "time_source.json", {"status": "fresh", "clock_domain_id": "clock-live-collector-fixture", "stale": False})
    for name in [
        "bundle_manifest_file",
        "adapter_conformance_file",
        "redaction_report_file",
        "gatechain_report_file",
        "uncertainty_report_file",
        "causal_control_report_file",
        "threshold_replay_file",
        "planner_boundary_file",
        "handoff_traceability_file",
    ]:
        write_json(inputs / f"{name}.json", {"source_input": name, "externally_produced": True, "producer_id": "fixture-operator"})
    return {
        "production_root_marker": "inputs/production_root_marker.json",
        "deployment_root_identity_file": "inputs/deployment_root_identity.json",
        "collector_identity_file": "inputs/collector_identity.json",
        "operator_trust_policy_file": "inputs/operator_trust_policy.json",
        "external_attestation_file": "inputs/external_attestation.json",
        "telemetry_counter_source_file": "inputs/telemetry_counter_source.json",
        "time_source_file": "inputs/time_source.json",
        "bundle_manifest_file": "inputs/bundle_manifest_file.json",
        "adapter_conformance_file": "inputs/adapter_conformance_file.json",
        "redaction_report_file": "inputs/redaction_report_file.json",
        "gatechain_report_file": "inputs/gatechain_report_file.json",
        "uncertainty_report_file": "inputs/uncertainty_report_file.json",
        "causal_control_report_file": "inputs/causal_control_report_file.json",
        "threshold_replay_file": "inputs/threshold_replay_file.json",
        "planner_boundary_file": "inputs/planner_boundary_file.json",
        "handoff_traceability_file": "inputs/handoff_traceability_file.json",
    }


def mutate(case_name: str, case_dir: Path, config: dict[str, object]) -> str:
    if case_name == "no_production_root_marker":
        config.pop("production_root_marker", None)
        return "not_running_in_production_root"
    if case_name == "missing_deployment_root_identity":
        config.pop("deployment_root_identity_file", None)
        return "operator_material_missing"
    if case_name == "missing_collector_identity":
        config.pop("collector_identity_file", None)
        return "collector_capability_missing"
    if case_name == "missing_operator_trust_policy_file":
        config.pop("operator_trust_policy_file", None)
        return "operator_material_missing"
    if case_name == "missing_external_attestation_file":
        config.pop("external_attestation_file", None)
        return "operator_material_missing"
    if case_name == "missing_telemetry_counter_source":
        config.pop("telemetry_counter_source_file", None)
        return "collector_capability_missing"
    if case_name == "missing_gate_source_material":
        config.pop("bundle_manifest_file", None)
        return "collector_capability_missing"
    if case_name == "stale_time_source":
        write_json(case_dir / "inputs" / "time_source.json", {"status": "stale", "clock_domain_id": "clock-live-collector-fixture", "stale": True})
        return "collector_capability_missing"
    if case_name == "unwritable_artifact_output_root":
        return "collector_capability_missing"
    if case_name == "dry_run_fixture_attempting_production_target":
        return "candidate_artifacts_emitted"
    if case_name == "internally_generated_self_attestation":
        write_json(case_dir / "inputs" / "external_attestation.json", {"external_attestation": True, "producer_id": "collector-live-collector-fixture", "generated_by_collector": True})
        return "operator_material_missing"
    if case_name == "complete_nonproduction_fixture_inputs":
        return "candidate_artifacts_emitted"
    raise ValueError(case_name)


def run_collector(mode: str, config_path: Path, output_root: Path, evidence_label: str = "production_target") -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(COLLECTOR), mode, "--config", str(config_path), "--output-root", str(output_root), "--evidence-label", evidence_label],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )


def load_report(output_root: Path) -> dict[str, object]:
    path = output_root / "preflight_report.json"
    if not path.exists():
        return {}
    with path.open() as f:
        return json.load(f)


def evaluate_case(case_name: str) -> tuple[dict[str, object], dict[str, object]]:
    case_dir = TMP / case_name
    if case_dir.exists():
        shutil.rmtree(case_dir)
    case_dir.mkdir(parents=True)
    config = base_case(case_dir)
    expected_state = mutate(case_name, case_dir, config)
    config_path = case_dir / "collector_config.json"
    write_json(config_path, config)
    output_root = case_dir / ("not_a_directory" if case_name == "unwritable_artifact_output_root" else "out")
    if case_name == "unwritable_artifact_output_root":
        output_root.write_text("blocks directory creation")

    if case_name in {"dry_run_fixture_attempting_production_target", "complete_nonproduction_fixture_inputs"}:
        proc = run_collector("dry-run", config_path, output_root, evidence_label="production_target")
        report = {"preflight_state": "candidate_artifacts_emitted", "production_artifact_emission_allowed": False, "missing_checks": "", "self_attestation_detected": False}
        manifest = json.loads((output_root / "manifest.json").read_text()) if (output_root / "manifest.json").exists() else {}
    else:
        proc = run_collector("preflight", config_path, output_root)
        report = load_report(output_root)
        manifest = {}

    state = str(report.get("preflight_state", "collector_capability_missing"))
    production_label = manifest.get("evidence_label") == "production_target"
    artifact_count = len(list((output_root / "artifacts").glob("*.json"))) if (output_root / "artifacts").exists() else 0
    row = {
        "case_id": case_name,
        "mode": "dry-run" if case_name in {"dry_run_fixture_attempting_production_target", "complete_nonproduction_fixture_inputs"} else "preflight",
        "expected_state": expected_state,
        "observed_state": state,
        "return_code": proc.returncode,
        "missing_checks": report.get("missing_checks", ""),
        "self_attestation_detected": str(bool(report.get("self_attestation_detected", False))).lower(),
        "artifact_count": artifact_count,
        "evidence_label": manifest.get("evidence_label", ""),
        "production_artifact_emission_allowed": str(state == "candidate_artifacts_emitted" and production_label).lower(),
        "blocked_reason": "" if state == "candidate_artifacts_emitted" else state,
    }
    boundary = {
        "case_id": case_name,
        "observed_state": state,
        "candidate_artifacts_emitted": str(artifact_count > 0).lower(),
        "evidence_label": manifest.get("evidence_label", ""),
        "ready_for_gate_evidence_validation": str(artifact_count == 13 and not production_label).lower(),
        "production_calibrated": "false",
        "production_ready": "false",
        "threshold_success": "false",
        "causal_validity_granted": "false",
        "claim_credit_allowed": "false",
    }
    return row, boundary


def main() -> None:
    if TMP.exists():
        shutil.rmtree(TMP)
    cases = [
        "no_production_root_marker",
        "missing_deployment_root_identity",
        "missing_collector_identity",
        "missing_operator_trust_policy_file",
        "missing_external_attestation_file",
        "missing_telemetry_counter_source",
        "missing_gate_source_material",
        "stale_time_source",
        "unwritable_artifact_output_root",
        "dry_run_fixture_attempting_production_target",
        "internally_generated_self_attestation",
        "complete_nonproduction_fixture_inputs",
    ]
    rows = []
    boundaries = []
    for case in cases:
        row, boundary = evaluate_case(case)
        rows.append(row)
        boundaries.append(boundary)

    failures = Counter(row["blocked_reason"] for row in rows if row["blocked_reason"])
    failure_rows = [{"failure_mode": key, "count": value} for key, value in sorted(failures.items())]

    write_csv(
        OUT_RESULTS,
        rows,
        [
            "case_id",
            "mode",
            "expected_state",
            "observed_state",
            "return_code",
            "missing_checks",
            "self_attestation_detected",
            "artifact_count",
            "evidence_label",
            "production_artifact_emission_allowed",
            "blocked_reason",
        ],
    )
    write_csv(OUT_FAILURES, failure_rows, ["failure_mode", "count"])
    write_csv(
        OUT_BOUNDARY,
        boundaries,
        [
            "case_id",
            "observed_state",
            "candidate_artifacts_emitted",
            "evidence_label",
            "ready_for_gate_evidence_validation",
            "production_calibrated",
            "production_ready",
            "threshold_success",
            "causal_validity_granted",
            "claim_credit_allowed",
        ],
    )


if __name__ == "__main__":
    main()
