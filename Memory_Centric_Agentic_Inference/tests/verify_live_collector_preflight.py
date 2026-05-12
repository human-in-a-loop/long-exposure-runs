#!/usr/bin/env python3
# created: 2026-05-12T17:20:00Z
# cycle: 38
# run_id: run-2026-05-11T121649Z
# agent: worker
# milestone: M-LIVECOLLECT-1
"""Verify live collector preflight and artifact emission boundaries."""

from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
PROBE = Path("/tmp/live_collector_probe_workspace")


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


def main() -> None:
    run("scripts/build_live_collector_contract.py")
    run("scripts/evaluate_live_collector_preflight.py")
    run("scripts/plot_live_collector_preflight.py")

    capability = read_csv(DATA / "live_collector_capability_matrix.csv")
    classes = {row["collection_source_class"] for row in capability}
    assert {"collector_observed", "operator_supplied", "external_attestation", "derived_from_prior_gate"} <= classes
    assert len(capability) == 13

    results = {row["case_id"]: row for row in read_csv(DATA / "live_collector_preflight_results.csv")}
    assert results["no_production_root_marker"]["observed_state"] == "not_running_in_production_root"
    assert results["no_production_root_marker"]["production_artifact_emission_allowed"] == "false"
    assert results["missing_collector_identity"]["observed_state"] == "collector_capability_missing"
    assert results["missing_operator_trust_policy_file"]["observed_state"] == "operator_material_missing"
    assert results["missing_external_attestation_file"]["observed_state"] == "operator_material_missing"
    assert results["missing_telemetry_counter_source"]["observed_state"] == "collector_capability_missing"
    assert results["missing_gate_source_material"]["observed_state"] == "collector_capability_missing"
    assert "source_material:bundle_manifest_file" in results["missing_gate_source_material"]["missing_checks"]
    assert results["stale_time_source"]["observed_state"] == "collector_capability_missing"
    assert results["unwritable_artifact_output_root"]["observed_state"] == "collector_capability_missing"
    assert results["internally_generated_self_attestation"]["self_attestation_detected"] == "true"
    assert results["internally_generated_self_attestation"]["observed_state"] == "operator_material_missing"

    dry = results["dry_run_fixture_attempting_production_target"]
    assert dry["evidence_label"] == "collector_dry_run_fixture", dry
    assert dry["artifact_count"] == "13", dry
    assert dry["production_artifact_emission_allowed"] == "false", dry

    complete = results["complete_nonproduction_fixture_inputs"]
    assert complete["artifact_count"] == "13", complete
    assert complete["evidence_label"] == "collector_dry_run_fixture", complete

    manifest = json.loads((PROBE / "complete_nonproduction_fixture_inputs" / "out" / "manifest.json").read_text())
    assert manifest["evidence_label"] != "production_target"
    for row in read_csv(DATA / "live_collector_artifact_mapping.csv"):
        assert manifest[row["manifest_boolean_field"]] == "true", row
        artifact_path = ROOT / manifest[row["manifest_evidence_path_field"]]
        payload = json.loads(artifact_path.read_text())
        for field in row["required_payload_fields"].split(","):
            assert field in payload, (row["gate_name"], field)
            if field != "upstream_artifact_digests" or row["upstream_dependency"] != "none":
                assert str(payload[field]).strip() != "", (row["gate_name"], field)
        assert payload["evidence_label"] == "collector_dry_run_fixture"
        assert payload["claim_credit_allowed"] is False

    missing_source_config = PROBE / "missing_gate_source_material" / "collector_config.json"
    missing_source_out = PROBE / "missing_gate_source_material" / "emit_out"
    proc = subprocess.run(
        [
            sys.executable,
            str(ROOT / "tools" / "production_evidence_collector.py"),
            "emit-artifacts",
            "--config",
            str(missing_source_config),
            "--output-root",
            str(missing_source_out),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    assert proc.returncode != 0, proc.stdout
    assert not (missing_source_out / "manifest.json").exists()

    boundaries = read_csv(DATA / "live_collector_claim_boundary.csv")
    for row in boundaries:
        assert row["production_calibrated"] == "false", row
        assert row["production_ready"] == "false", row
        assert row["threshold_success"] == "false", row
        assert row["causal_validity_granted"] == "false", row
        assert row["claim_credit_allowed"] == "false", row

    failures = {row["failure_mode"] for row in read_csv(DATA / "live_collector_failure_modes.csv")}
    assert {"not_running_in_production_root", "collector_capability_missing", "operator_material_missing"} <= failures

    assert_nonblank_png(DATA / "live_collector_capability_matrix.png")
    assert_nonblank_png(DATA / "live_collector_failure_modes.png")
    assert_nonblank_png(DATA / "live_collector_claim_boundary.png")
    print("OK: live collector preflight verified.")


if __name__ == "__main__":
    main()
