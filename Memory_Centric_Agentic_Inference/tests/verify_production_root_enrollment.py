#!/usr/bin/env python3
# created: 2026-05-12T10:20:00Z
# cycle: 31
# run_id: run-2026-05-11T121649Z
# agent: worker
# milestone: M-ROOTINT-1

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

REQUIRED_FIELDS = {
    "deployment_root_id",
    "root_type",
    "root_status",
    "key_id",
    "key_rotation_epoch",
    "operator_id",
    "collector_id",
    "collector_firmware_identity",
    "topology_id",
    "topology_version",
    "schema_version",
    "measurement_run_id",
    "bundle_id",
    "counter_source_id",
    "counter_source_binding",
    "tenant_id",
    "security_context_id",
    "evidence_label",
}

EXPECTED_INVALID = {
    "invalid-unknown-root": "unknown_deployment_root",
    "invalid-unknown-key": "unknown_key_id",
    "invalid-missing-firmware-identity": "missing_collector_firmware_identity",
    "invalid-stale-firmware-attestation": "stale_firmware_attestation",
    "invalid-duplicate-collector-different-operator": "duplicate_collector_id_different_operator",
    "invalid-key-rotation-gap": "key_rotation_gap",
    "invalid-topology-id-mismatch": "topology_id_mismatch",
    "invalid-stale-enrollment-window": "stale_enrollment_window",
    "invalid-topology-drift": "topology_drift",
    "invalid-schema-version-mismatch": "schema_version_mismatch",
    "invalid-measurement-run-id-mismatch": "measurement_run_id_mismatch",
    "invalid-bundle-id-mismatch": "bundle_id_mismatch",
    "invalid-missing-counter-source-binding": "missing_counter_source_binding",
    "invalid-missing-tenant-security-binding": "missing_tenant_security_binding",
    "invalid-replayed-enrollment-id": "replayed_enrollment_id",
    "invalid-fixture-attempted-production-root": "fixture_attempted_production_root",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
        rows = list(csv.DictReader(f))
    assert rows, f"{path.relative_to(ROOT)} is empty"
    return rows


def by_case(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    return {row["case_id"]: row for row in rows}


def assert_png_nonblank(path: Path) -> None:
    data = path.read_bytes()
    assert data.startswith(b"\x89PNG\r\n\x1a\n"), f"{path.relative_to(ROOT)} is not a PNG"
    assert len(data) > 10_000, f"{path.relative_to(ROOT)} is too small"


def main() -> None:
    schema = read_csv(DATA / "production_root_enrollment_schema.csv")
    valid = read_csv(DATA / "production_root_valid_enrollments.csv")
    invalid = read_csv(DATA / "production_root_invalid_enrollments.csv")
    counters = read_csv(DATA / "production_root_counter_binding_requirements.csv")
    results = read_csv(DATA / "production_root_enrollment_results.csv")
    failures = read_csv(DATA / "production_root_failure_modes.csv")
    boundary = read_csv(DATA / "production_root_gatechain_boundary.csv")
    trace = read_csv(DATA / "production_root_traceability_links.csv")

    schema_fields = {row["field_name"] for row in schema if row["required"] == "true"}
    assert REQUIRED_FIELDS <= schema_fields
    assert {"bundle_id", "measurement_run_id", "operator_id", "collector_id", "schema_version"} <= {
        row["field_name"] for row in schema if row["stable_across_gatechain"] == "true"
    }
    assert len(valid) == 1
    assert len(invalid) == len(EXPECTED_INVALID)
    assert all(row["blocks_if_missing"] == "true" for row in counters)

    result = by_case(results)
    complete = result["valid-complete-fixture-enrollment"]
    assert complete["enrollment_admissible"] == "true"
    assert complete["pre_gatechain_only"] == "true"
    assert complete["production_target_granted"] == "false"
    assert complete["production_calibrated"] == "false"
    assert complete["production_ready"] == "false"
    assert complete["claim_credit_allowed"] == "false"

    assert sum(1 for row in results if row["enrollment_admissible"] == "true") == 1
    for case_id, reason in EXPECTED_INVALID.items():
        assert result[case_id]["enrollment_admissible"] == "false"
        assert result[case_id]["blocked_reason"] == reason
        assert result[case_id]["expected_reason_matched"] == "true"

    assert all(row["blocked_reason"] for row in results if row["case_type"] == "invalid_fixture")
    assert all(row["fail_closed"] == "true" and row["pre_gatechain_block"] == "true" for row in failures)
    assert all(row["claim_credit_allowed"] == "false" for row in boundary)
    assert all(row["production_target_granted"] == "false" for row in boundary)
    assert all(row["production_calibrated"] == "false" for row in boundary)
    assert all(row["production_ready"] == "false" for row in boundary)
    assert result["invalid-schema-version-mismatch"]["blocked_field"] == "schema_version"
    assert result["invalid-duplicate-collector-different-operator"]["blocked_field"] == "collector_id"
    assert result["invalid-measurement-run-id-mismatch"]["blocked_field"] == "measurement_run_id"
    assert result["invalid-bundle-id-mismatch"]["blocked_field"] == "bundle_id"
    assert result["invalid-topology-id-mismatch"]["blocked_field"] == "topology_id"
    assert result["invalid-unknown-key"]["blocked_field"] == "key_id"
    assert result["invalid-stale-firmware-attestation"]["blocked_field"] == "firmware_attested_at"

    assert {row["trace_link_id"] for row in trace} >= {
        "root-to-trust-policy",
        "root-to-attestation",
        "root-to-intake",
        "root-to-adapter-conformance",
        "root-to-gatechain",
    }

    for fig in [
        DATA / "production_root_enrollment_coverage.png",
        DATA / "production_root_failure_modes.png",
        DATA / "production_root_gatechain_boundary.png",
    ]:
        assert_png_nonblank(fig)

    print("OK: production root enrollment verified.")


if __name__ == "__main__":
    main()
