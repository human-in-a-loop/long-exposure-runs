#!/usr/bin/env python3
# created: 2026-05-12T10:05:00Z
# cycle: 31
# run_id: run-2026-05-11T121649Z
# agent: worker
# milestone: M-ROOTINT-1
"""Build deployment-root enrollment fixtures for pre-gatechain replay."""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

INPUTS = [
    DATA / "operator_trust_policy_results.csv",
    DATA / "production_attestation_results.csv",
    DATA / "production_intake_admission_results.csv",
    DATA / "adapter_conformance_results.csv",
    DATA / "production_telemetry_collector_spec.csv",
    DATA / "production_telemetry_preflight_checks.csv",
    DATA / "production_dc12_ingestion_results.csv",
    DATA / "evidence_gatechain_replay_results.csv",
]

OUT_SCHEMA = DATA / "production_root_enrollment_schema.csv"
OUT_VALID = DATA / "production_root_valid_enrollments.csv"
OUT_INVALID = DATA / "production_root_invalid_enrollments.csv"
OUT_COUNTERS = DATA / "production_root_counter_binding_requirements.csv"

ENROLLMENT_FIELDS = [
    ("enrollment_id", "Stable enrollment record identifier; replayed IDs are rejected."),
    ("deployment_root_id", "Operator-approved deployment root that anchors collector, key, topology, and schema facts."),
    ("root_type", "Root class such as KMS/HSM/hardware-attestation/fixture-hmac."),
    ("root_status", "Root lifecycle state; active required."),
    ("root_valid_from", "UTC start of admissible root window."),
    ("root_valid_until", "UTC end of admissible root window."),
    ("key_id", "Signing key bound to the deployment root."),
    ("key_rotation_epoch", "Monotonic key rotation epoch with no uncovered collection interval."),
    ("operator_id", "Operator identity bound to policy, enrollment, and gatechain identity."),
    ("collector_id", "Collector identity; unique under one operator/root binding."),
    ("collector_firmware_identity", "Firmware or measurement identity for the collector binary/device."),
    ("firmware_attested_at", "Time at which firmware identity was attested."),
    ("topology_id", "Topology identity used by downstream telemetry joins."),
    ("topology_version", "Version or digest of topology map accepted for the measurement window."),
    ("schema_version", "Production telemetry schema version expected by ingestion."),
    ("measurement_run_id", "Measurement run provenance ID propagated into downstream gatechain identifiers."),
    ("bundle_id", "Bundle identity propagated into attestation, intake, and gatechain stages."),
    ("counter_source_id", "Stable source for power, byte, latency, or security counters."),
    ("counter_source_binding", "Counter binding covers collector, topology, tenant, security context, and measurement run."),
    ("tenant_id", "Tenant identity required for isolation and claim-boundary checks."),
    ("security_context_id", "Security context required for downstream security/provenance gates."),
    ("evidence_label", "Evidence label; fixture labels cannot mimic production_target."),
]

CANONICAL = {
    "enrollment_id": "root-enroll-fixture-001",
    "deployment_root_id": "deployment-root-fixture-001",
    "root_type": "fixture_kms_profile",
    "root_status": "active",
    "root_valid_from": "2026-05-12T09:55:00Z",
    "root_valid_until": "2026-05-12T11:00:00Z",
    "key_id": "test-key-active-a",
    "key_rotation_epoch": "epoch-2026-05-a",
    "operator_id": "operator-secops-fixture",
    "collector_id": "collector-fixture-001",
    "collector_firmware_identity": "collector-fw-fixture-digest-001",
    "firmware_attested_at": "2026-05-12T09:58:00Z",
    "topology_id": "topology-fixture-001",
    "topology_version": "topology-v1",
    "schema_version": "production_dc12_schema_v1",
    "measurement_run_id": "gatechain-run-001",
    "bundle_id": "gatechain-bundle-001",
    "counter_source_id": "counter-source-fixture-001",
    "counter_source_binding": "collector+topology+tenant+security+run",
    "tenant_id": "tenant-fixture-001",
    "security_context_id": "security-context-fixture-001",
    "evidence_label": "deployment_root_enrollment_fixture",
}

INVALID_SPECS = [
    ("invalid-unknown-root", {"deployment_root_id": "unknown-root-999"}, "unknown_deployment_root"),
    ("invalid-unknown-key", {"key_id": "test-key-unknown-a"}, "unknown_key_id"),
    ("invalid-missing-firmware-identity", {"collector_firmware_identity": ""}, "missing_collector_firmware_identity"),
    ("invalid-stale-firmware-attestation", {"firmware_attested_at": "2026-05-12T08:00:00Z"}, "stale_firmware_attestation"),
    ("invalid-duplicate-collector-different-operator", {"operator_id": "operator-other-fixture"}, "duplicate_collector_id_different_operator"),
    ("invalid-key-rotation-gap", {"key_rotation_epoch": "gap-before-epoch-2026-05-a"}, "key_rotation_gap"),
    ("invalid-stale-enrollment-window", {"root_valid_until": "2026-05-12T09:00:00Z"}, "stale_enrollment_window"),
    ("invalid-topology-id-mismatch", {"topology_id": "topology-other-fixture"}, "topology_id_mismatch"),
    ("invalid-topology-drift", {"topology_version": "topology-v0-stale"}, "topology_drift"),
    ("invalid-schema-version-mismatch", {"schema_version": "production_dc12_schema_v0"}, "schema_version_mismatch"),
    ("invalid-measurement-run-id-mismatch", {"measurement_run_id": "gatechain-run-other"}, "measurement_run_id_mismatch"),
    ("invalid-bundle-id-mismatch", {"bundle_id": "gatechain-bundle-other"}, "bundle_id_mismatch"),
    ("invalid-missing-counter-source-binding", {"counter_source_binding": ""}, "missing_counter_source_binding"),
    ("invalid-missing-tenant-security-binding", {"tenant_id": "", "security_context_id": ""}, "missing_tenant_security_binding"),
    ("invalid-replayed-enrollment-id", {"enrollment_id": "root-enroll-fixture-001"}, "replayed_enrollment_id"),
    ("invalid-fixture-attempted-production-root", {"root_type": "production_kms", "evidence_label": "production_target"}, "fixture_attempted_production_root"),
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        raise ValueError(f"{path.relative_to(ROOT)} is empty")
    return rows


def write_csv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})
    print(f"wrote {path.relative_to(ROOT)} rows={len(rows)}")


def require_upstream_inputs() -> None:
    for path in INPUTS:
        read_csv(path)


def valid_enrollment() -> dict[str, object]:
    row = dict(CANONICAL)
    row.update(
        {
            "case_id": "valid-complete-fixture-enrollment",
            "case_type": "valid_fixture",
            "expected_blocked_reason": "",
            "notes": "Complete fixture enrollment proves only pre-gatechain admissibility, not production evidence.",
        }
    )
    return row


def invalid_enrollments() -> list[dict[str, object]]:
    rows = []
    for case_id, overrides, reason in INVALID_SPECS:
        row = dict(CANONICAL)
        row.update(overrides)
        row.update(
            {
                "case_id": case_id,
                "case_type": "invalid_fixture",
                "expected_blocked_reason": reason,
                "notes": "Malformed enrollment must fail closed before downstream gatechain replay.",
            }
        )
        rows.append(row)
    return rows


def counter_requirements() -> list[dict[str, object]]:
    return [
        {
            "requirement_id": "CB-001",
            "counter_family": "accelerator_energy_power",
            "required_binding": "counter_source_id binds collector_id, topology_id, measurement_run_id, tenant_id, and security_context_id",
            "blocks_if_missing": "true",
            "downstream_stage": "production_ingestion_accepted",
        },
        {
            "requirement_id": "CB-002",
            "counter_family": "tier_byte_movement",
            "required_binding": "byte counters share topology_id, schema_version, object_id, and measurement_run_id with bundle lineage",
            "blocks_if_missing": "true",
            "downstream_stage": "threshold_replay_passed",
        },
        {
            "requirement_id": "CB-003",
            "counter_family": "cxl_pooled_memory_latency",
            "required_binding": "latency counters bind to topology_version and collector_firmware_identity",
            "blocks_if_missing": "true",
            "downstream_stage": "noise_floor_passed",
        },
        {
            "requirement_id": "CB-004",
            "counter_family": "security_decision_stream",
            "required_binding": "security stream binds tenant_id and security_context_id to the same measurement_run_id",
            "blocks_if_missing": "true",
            "downstream_stage": "security_provenance_passed",
        },
    ]


def main() -> None:
    require_upstream_inputs()
    schema = [
        {
            "field_name": name,
            "required": "true",
            "stable_across_gatechain": "true" if name in {"bundle_id", "measurement_run_id", "operator_id", "collector_id", "schema_version"} else "false",
            "description": description,
        }
        for name, description in ENROLLMENT_FIELDS
    ]
    fields = ["case_id", "case_type", *[name for name, _ in ENROLLMENT_FIELDS], "expected_blocked_reason", "notes"]
    write_csv(OUT_SCHEMA, schema, ["field_name", "required", "stable_across_gatechain", "description"])
    write_csv(OUT_VALID, [valid_enrollment()], fields)
    write_csv(OUT_INVALID, invalid_enrollments(), fields)
    write_csv(OUT_COUNTERS, counter_requirements(), ["requirement_id", "counter_family", "required_binding", "blocks_if_missing", "downstream_stage"])


if __name__ == "__main__":
    main()
