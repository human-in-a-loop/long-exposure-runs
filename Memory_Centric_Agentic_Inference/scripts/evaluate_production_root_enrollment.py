#!/usr/bin/env python3
# created: 2026-05-12T10:10:00Z
# cycle: 31
# run_id: run-2026-05-11T121649Z
# agent: worker
# milestone: M-ROOTINT-1
"""Evaluate deployment-root enrollment fixtures as a pre-gatechain boundary."""

from __future__ import annotations

import csv
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

SCHEMA = DATA / "production_root_enrollment_schema.csv"
VALID = DATA / "production_root_valid_enrollments.csv"
INVALID = DATA / "production_root_invalid_enrollments.csv"
COUNTERS = DATA / "production_root_counter_binding_requirements.csv"
GATECHAIN = DATA / "evidence_gatechain_replay_results.csv"
READINESS = DATA / "final_claim_readiness_matrix.csv"

OUT_RESULTS = DATA / "production_root_enrollment_results.csv"
OUT_FAILURES = DATA / "production_root_failure_modes.csv"
OUT_BOUNDARY = DATA / "production_root_gatechain_boundary.csv"
OUT_TRACE = DATA / "production_root_traceability_links.csv"

EVAL_TIME = datetime.fromisoformat("2026-05-12T10:15:00+00:00")
KNOWN_ROOTS = {"deployment-root-fixture-001"}
KNOWN_KEYS = {"test-key-active-a"}
KNOWN_COLLECTOR_OPERATOR = {"collector-fixture-001": "operator-secops-fixture"}
EXPECTED_TOPOLOGY_ID = "topology-fixture-001"
EXPECTED_TOPOLOGY_VERSION = "topology-v1"
EXPECTED_SCHEMA_VERSION = "production_dc12_schema_v1"
EXPECTED_MEASUREMENT_RUN_ID = "gatechain-run-001"
EXPECTED_BUNDLE_ID = "gatechain-bundle-001"
FIRMWARE_FRESH_AFTER = datetime.fromisoformat("2026-05-12T09:30:00+00:00")
KNOWN_ENROLLMENTS_SEEN = {"root-enroll-fixture-001"}
REQUIRED_FIELDS = [
    "deployment_root_id",
    "root_type",
    "root_status",
    "root_valid_from",
    "root_valid_until",
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


def parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def first_block(row: dict[str, str], seen_valid_ids: set[str]) -> tuple[str, str]:
    for field in REQUIRED_FIELDS:
        if not row.get(field, "").strip():
            if field == "collector_firmware_identity":
                return "missing_collector_firmware_identity", field
            if field in {"tenant_id", "security_context_id"}:
                return "missing_tenant_security_binding", field
            if field == "counter_source_binding":
                return "missing_counter_source_binding", field
            return f"missing_{field}", field
    if row["deployment_root_id"] not in KNOWN_ROOTS:
        return "unknown_deployment_root", "deployment_root_id"
    if row["root_status"] != "active":
        return "inactive_deployment_root", "root_status"
    if row["evidence_label"] == "production_target" or row["root_type"].startswith("production_"):
        return "fixture_attempted_production_root", "evidence_label"
    if row["key_id"] not in KNOWN_KEYS:
        return "unknown_key_id", "key_id"
    if row["collector_id"] in KNOWN_COLLECTOR_OPERATOR and row["operator_id"] != KNOWN_COLLECTOR_OPERATOR[row["collector_id"]]:
        return "duplicate_collector_id_different_operator", "collector_id"
    if row["key_rotation_epoch"].startswith("gap-"):
        return "key_rotation_gap", "key_rotation_epoch"
    if parse_time(row["root_valid_until"]) <= EVAL_TIME:
        return "stale_enrollment_window", "root_valid_until"
    if parse_time(row["firmware_attested_at"]) < FIRMWARE_FRESH_AFTER:
        return "stale_firmware_attestation", "firmware_attested_at"
    if row["topology_id"] != EXPECTED_TOPOLOGY_ID:
        return "topology_id_mismatch", "topology_id"
    if row["topology_version"] != EXPECTED_TOPOLOGY_VERSION:
        return "topology_drift", "topology_version"
    if row["schema_version"] != EXPECTED_SCHEMA_VERSION:
        return "schema_version_mismatch", "schema_version"
    if row["measurement_run_id"] != EXPECTED_MEASUREMENT_RUN_ID:
        return "measurement_run_id_mismatch", "measurement_run_id"
    if row["bundle_id"] != EXPECTED_BUNDLE_ID:
        return "bundle_id_mismatch", "bundle_id"
    if row["enrollment_id"] in seen_valid_ids and row["case_type"] == "invalid_fixture":
        return "replayed_enrollment_id", "enrollment_id"
    if "collector" not in row["counter_source_binding"] or "security" not in row["counter_source_binding"]:
        return "missing_counter_source_binding", "counter_source_binding"
    return "", ""


def evaluate(rows: list[dict[str, str]]) -> list[dict[str, object]]:
    results = []
    seen_valid_ids = set(KNOWN_ENROLLMENTS_SEEN)
    for row in rows:
        reason, field = first_block(row, seen_valid_ids)
        admissible = reason == "" and row["case_type"] == "valid_fixture"
        results.append(
            {
                "case_id": row["case_id"],
                "case_type": row["case_type"],
                "deployment_root_id": row["deployment_root_id"],
                "operator_id": row["operator_id"],
                "collector_id": row["collector_id"],
                "collector_firmware_identity": row["collector_firmware_identity"],
                "topology_id": row["topology_id"],
                "schema_version": row["schema_version"],
                "measurement_run_id": row["measurement_run_id"],
                "bundle_id": row["bundle_id"],
                "evidence_label": row["evidence_label"],
                "enrollment_admissible": str(admissible).lower(),
                "blocked_field": field,
                "blocked_reason": reason,
                "expected_blocked_reason": row.get("expected_blocked_reason", ""),
                "expected_reason_matched": str((not row.get("expected_blocked_reason")) or row.get("expected_blocked_reason") == reason).lower(),
                "production_target_granted": "false",
                "production_calibrated": "false",
                "production_ready": "false",
                "claim_credit_allowed": "false",
                "pre_gatechain_only": "true",
            }
        )
        if admissible:
            seen_valid_ids.add(row["enrollment_id"])
    return results


def failure_rows(results: list[dict[str, object]]) -> list[dict[str, object]]:
    counts = Counter(str(row["blocked_reason"]) for row in results if row["blocked_reason"])
    return [
        {"blocked_reason": reason, "case_count": count, "fail_closed": "true", "pre_gatechain_block": "true"}
        for reason, count in sorted(counts.items())
    ]


def boundary_rows(results: list[dict[str, object]]) -> list[dict[str, object]]:
    gatechain = read_csv(GATECHAIN)
    existing_allowed = any(row["production_claim_credit_allowed"] == "true" for row in gatechain)
    return [
        {
            "case_id": row["case_id"],
            "enrollment_admissible": row["enrollment_admissible"],
            "existing_gatechain_allowed": str(existing_allowed).lower(),
            "evidence_label": row["evidence_label"],
            "production_target_granted": "false",
            "production_calibrated": "false",
            "production_ready": "false",
            "claim_credit_allowed": "false",
            "boundary_reason": "enrollment_precondition_only" if row["enrollment_admissible"] == "true" else row["blocked_reason"],
            "option_bc_contract_ready_only": "true",
        }
        for row in results
    ]


def traceability_rows() -> list[dict[str, object]]:
    return [
        {"trace_link_id": "root-to-trust-policy", "root_artifact": "data/production_root_enrollment_results.csv", "downstream_artifact": "data/operator_trust_policy_results.csv", "required_identifier": "operator_id;collector_id;key_id"},
        {"trace_link_id": "root-to-attestation", "root_artifact": "data/production_root_enrollment_results.csv", "downstream_artifact": "data/production_attestation_results.csv", "required_identifier": "bundle_id;collector_id;key_id"},
        {"trace_link_id": "root-to-intake", "root_artifact": "data/production_root_enrollment_results.csv", "downstream_artifact": "data/production_intake_admission_results.csv", "required_identifier": "bundle_id;schema_version"},
        {"trace_link_id": "root-to-adapter-conformance", "root_artifact": "data/production_root_enrollment_results.csv", "downstream_artifact": "data/adapter_conformance_results.csv", "required_identifier": "collector_id;measurement_run_id;schema_version"},
        {"trace_link_id": "root-to-gatechain", "root_artifact": "data/production_root_enrollment_results.csv", "downstream_artifact": "data/evidence_gatechain_replay_results.csv", "required_identifier": "bundle_id;measurement_run_id;operator_id;collector_id;schema_version"},
    ]


def main() -> None:
    schema = read_csv(SCHEMA)
    counters = read_csv(COUNTERS)
    readiness = read_csv(READINESS)
    rows = read_csv(VALID) + read_csv(INVALID)
    required_names = {row["field_name"] for row in schema if row["required"] == "true"}
    missing = sorted(set(REQUIRED_FIELDS) - required_names)
    if missing:
        raise ValueError(f"schema missing required enrollment fields: {missing}")
    if any(row["blocks_if_missing"] != "true" for row in counters):
        raise ValueError("counter binding requirement must fail closed")
    if any(row["production_ready"] == "true" for row in readiness):
        raise ValueError("existing final readiness unexpectedly contains production-ready claim")

    results = evaluate(rows)
    write_csv(
        OUT_RESULTS,
        results,
        [
            "case_id",
            "case_type",
            "deployment_root_id",
            "operator_id",
            "collector_id",
            "collector_firmware_identity",
            "topology_id",
            "schema_version",
            "measurement_run_id",
            "bundle_id",
            "evidence_label",
            "enrollment_admissible",
            "blocked_field",
            "blocked_reason",
            "expected_blocked_reason",
            "expected_reason_matched",
            "production_target_granted",
            "production_calibrated",
            "production_ready",
            "claim_credit_allowed",
            "pre_gatechain_only",
        ],
    )
    write_csv(OUT_FAILURES, failure_rows(results), ["blocked_reason", "case_count", "fail_closed", "pre_gatechain_block"])
    write_csv(
        OUT_BOUNDARY,
        boundary_rows(results),
        [
            "case_id",
            "enrollment_admissible",
            "existing_gatechain_allowed",
            "evidence_label",
            "production_target_granted",
            "production_calibrated",
            "production_ready",
            "claim_credit_allowed",
            "boundary_reason",
            "option_bc_contract_ready_only",
        ],
    )
    write_csv(OUT_TRACE, traceability_rows(), ["trace_link_id", "root_artifact", "downstream_artifact", "required_identifier"])


if __name__ == "__main__":
    main()
