#!/usr/bin/env python3
# created: 2026-05-12T06:05:00Z
# cycle: 27
# run_id: run-2026-05-11T121649Z
# agent: worker
# milestone: M-INTAKE-1
"""Evaluate production telemetry intake bundle admission gates."""

from __future__ import annotations

import csv
from collections import Counter
import hashlib
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
sys.path.insert(0, str(ROOT / "scripts"))

from ingest_production_dc12_telemetry import blocked_reason, required_fields, threshold_map  # noqa: E402


MANIFEST_SCHEMA = DATA / "production_intake_bundle_manifest_schema.csv"
VALID = DATA / "production_intake_valid_bundle_manifest.csv"
INVALID = DATA / "production_intake_invalid_bundle_manifests.csv"
PROD_SCHEMA = DATA / "production_dc12_telemetry_schema.csv"
CXL = DATA / "cxl_contention_thresholds.csv"

OUT_RESULTS = DATA / "production_intake_admission_results.csv"
OUT_FAILURES = DATA / "production_intake_failure_modes.csv"
OUT_BOUNDARY = DATA / "production_intake_downstream_boundary.csv"
OUT_TRACE = DATA / "production_intake_traceability_links.csv"

EVIDENCE = "production_intake_fixture"
REQUIRED_SECTIONS = {
    "bundle identity",
    "telemetry payload inventory",
    "join window",
    "provenance",
    "measurement quality",
    "security/privacy",
    "boundary labels",
}
REQUIRED_STREAMS = {
    "adapter conformance admission report",
    "backend-shaped valid adapter profiles",
    "production telemetry schema-shaped payload",
    "deployment join contract",
    "deployment preflight checks",
}


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


def truthy(row: dict[str, str], key: str) -> bool:
    return str(row.get(key, "")).strip().lower() == "true"


def checksum_matches(row: dict[str, str]) -> bool:
    path = ROOT / row.get("file_path", "")
    if not path.is_file() or not row.get("checksum_sha256"):
        return False
    return hashlib.sha256(path.read_bytes()).hexdigest() == row["checksum_sha256"]


def classify(row: dict[str, str], required_fields_: set[str]) -> str:
    for field in required_fields_:
        if row.get(field, "") == "":
            if field == "checksum_sha256":
                return "missing_checksum"
            if field == "adapter_conformance_report_path":
                return "missing_adapter_conformance_pointer"
            if field in {"noise_floor_j", "latency_bucket_width_us", "calibration_method", "counter_resolution"}:
                return "missing_noise_floor"
            if field in {"security_context_source", "retention_authorization", "tenant_label_handling"}:
                return "incomplete_security_provenance_stream"
            return "missing_chain_of_custody"
    if not checksum_matches(row):
        return "checksum_mismatch"
    if row["schema_version"] != "production_dc12_v1":
        return "schema_version_mismatch"
    if row["canonical_schema_target"] not in {
        "production_dc12_telemetry_schema",
        "adapter_conformance_contract",
        "production_telemetry_join_contract",
        "production_telemetry_preflight_checks",
    }:
        return "schema_version_mismatch"
    if not row["join_alias_resolution_status"].startswith("resolved"):
        return "unresolved_join_alias"
    if row["clock_domain"] == "" or row["interval_end_ms"] <= row["interval_start_ms"] or not truthy(row, "collection_window_fresh"):
        return "stale_collection_window"
    if not truthy(row, "unit_valid_input"):
        return "invalid_unit"
    if not truthy(row, "security_provenance_stream_complete"):
        return "incomplete_security_provenance_stream"
    if not truthy(row, "redaction_policy_unambiguous") or row["redaction_policy"] in {"", "operator-defined"}:
        return "ambiguous_redaction_policy"
    if row["evidence_label"] == "production_target" and row["trusted_source_declaration"] != "trusted_real_production_source":
        return "fixture_attempted_production_target"
    return ""


def category(reason: str) -> str:
    if reason in {"missing_checksum", "checksum_mismatch", "missing_chain_of_custody", "fixture_attempted_production_target"}:
        return "custody"
    if reason == "schema_version_mismatch":
        return "schema"
    if reason in {"unresolved_join_alias", "stale_collection_window"}:
        return "join"
    if reason == "missing_noise_floor":
        return "noise"
    if reason == "incomplete_security_provenance_stream":
        return "security"
    if reason == "missing_adapter_conformance_pointer":
        return "provenance"
    if reason == "ambiguous_redaction_policy":
        return "redaction"
    if reason == "invalid_unit":
        return "unit"
    return "custody"


def downstream_probe(row: dict[str, str], prod_schema: list[dict[str, str]], thresholds: dict[str, dict[str, str]]) -> tuple[dict[str, bool], str]:
    probe = {schema_row["field_name"]: "" for schema_row in prod_schema}
    probe.update(
        {
            "fixture_id": row["bundle_id"],
            "fixture_class": "intake_bundle",
            "measurement_run_id": row["measurement_run_id"],
            "evidence_label": EVIDENCE,
            "production_target_id": "intake-fixture-target",
            "hardware_topology_id": "intake-fixture-topology",
            "accelerator_type": "intake-fixture-accelerator",
            "source_tier": "HBM",
            "destination_tier": "CXL_pooled_memory",
            "object_class": "kv_cache_branch_state",
            "workload_class": "code agent with verification loop",
            "architecture_option": "B_memory_object_reuse_and_tiering",
            "reuse_decision": "safe_reuse_candidate",
            "bytes_moved": "536870912",
            "resident_bytes": "1073741824",
            "interval_ms": "1000",
            "joules_measured": "18.5",
            "power_counter_source": "intake_fixture_counter",
            "energy_noise_floor_j": row.get("noise_floor_j", "0.2") or "0.2",
            "latency_p50_us": "8.0",
            "latency_p95_us": "42.0",
            "latency_p99_us": "75.0",
            "tenant_count": "3",
            "queue_depth": "9",
            "security_allowed": "true",
            "provenance_valid": "true",
            "retention_valid": "true",
            "verifier_valid": "true",
            "calibration_candidate": "true",
            "byte_interval_start_ms": row["interval_start_ms"],
            "byte_interval_end_ms": row["interval_end_ms"],
            "power_interval_start_ms": row["interval_start_ms"],
            "power_interval_end_ms": row["interval_end_ms"],
            "constant_id": "DC-001",
            "threshold_id": "DC001-BYTE-ENERGY-001",
        }
    )
    return blocked_reason(probe, required_fields(prod_schema), thresholds)


def main() -> None:
    manifest_schema = read_csv(MANIFEST_SCHEMA)
    valid = read_csv(VALID)
    invalid = read_csv(INVALID)
    prod_schema = read_csv(PROD_SCHEMA)
    thresholds = threshold_map(read_csv(CXL))
    required_manifest_fields = {row["field_name"] for row in manifest_schema if row["required"] == "true"}

    if REQUIRED_SECTIONS - {row["manifest_section"] for row in manifest_schema}:
        raise ValueError("manifest schema missing required section")
    if REQUIRED_STREAMS - {row["stream_class"] for row in valid}:
        raise ValueError("valid manifest missing required stream")

    cases = [("valid-intake-bundle", valid, "")] + [(row["bundle_id"], [row], row["expected_blocked_reason"]) for row in invalid]
    results: list[dict[str, object]] = []
    boundary: list[dict[str, object]] = []
    counts: Counter[str] = Counter()

    for bundle_id, rows, expected in cases:
        reasons = [classify(row, required_manifest_fields) for row in rows]
        block = next((reason for reason in reasons if reason), "")
        if block:
            counts[category(block)] += 1
        status = "blocked" if block else "structurally_admissible"
        representative = rows[0]
        gates, ingestion_reason = downstream_probe(representative, prod_schema, thresholds)
        if not ingestion_reason:
            ingestion_reason = "intake_admission_only_no_claim_credit"
        requested = truthy(representative, "production_target_requested")

        results.append(
            {
                "bundle_id": bundle_id,
                "admission_status": status,
                "payload_rows_seen": len(rows),
                "required_sections_present": str(REQUIRED_SECTIONS <= {r["manifest_section"] for r in manifest_schema}).lower(),
                "required_streams_present": str(REQUIRED_STREAMS <= {r["stream_class"] for r in rows}).lower(),
                "checksum_validation_attempted": "true",
                "checksum_valid": str(all(checksum_matches(r) for r in rows)).lower(),
                "schema_version_checked": "true",
                "schema_version_valid": str(all(r["schema_version"] == "production_dc12_v1" for r in rows)).lower(),
                "join_alias_resolution_attempted": "true",
                "join_alias_valid": str(all(r["join_alias_resolution_status"].startswith("resolved") for r in rows)).lower(),
                "unit_normalization_attempted": str(any(truthy(r, "unit_normalization_attempted") for r in rows)).lower(),
                "unit_valid": str(all(truthy(r, "unit_valid_input") for r in rows)).lower(),
                "noise_metadata_present": str(all(bool(r["noise_floor_j"]) for r in rows)).lower(),
                "security_provenance_complete": str(all(truthy(r, "security_provenance_stream_complete") for r in rows)).lower(),
                "redaction_policy_unambiguous": str(all(truthy(r, "redaction_policy_unambiguous") for r in rows)).lower(),
                "evidence_label": EVIDENCE,
                "production_target_requested": str(requested).lower(),
                "production_target_granted": "false",
                "production_calibrated": "false",
                "production_ready": "false",
                "claim_credit_allowed": "false",
                "expected_blocked_reason": expected,
                "blocked_reason": block,
            }
        )
        boundary.append(
            {
                "bundle_id": bundle_id,
                "admission_status": status,
                "production_target_requested": str(requested).lower(),
                "evidence_label": EVIDENCE,
                "ingestion_gate_schema_valid": str(gates["schema_valid"]).lower(),
                "downstream_ingestion_boundary": ingestion_reason,
                "production_calibrated": "false",
                "production_ready": "false",
                "claim_credit_allowed": "false",
                "boundary_reason": "intake verifies bundle custody only; trusted real production source and ingestion gates remain required",
            }
        )

    failure_rows = [
        {"failure_category": name, "invalid_bundle_count": counts[name], "fail_closed": "true"}
        for name in ["custody", "schema", "join", "noise", "security", "provenance", "redaction", "unit"]
    ]
    trace_rows = [
        {
            "trace_link_id": "intake-to-adapter-conformance",
            "source_artifact": "data/production_intake_valid_bundle_manifest.csv",
            "cited_artifact": "data/adapter_conformance_results.csv",
            "downstream_use": "operator bundle must point at adapter conformance report before ingestion",
        },
        {
            "trace_link_id": "intake-to-production-ingestion",
            "source_artifact": "data/production_intake_admission_results.csv",
            "cited_artifact": "data/production_dc12_ingestion_results.csv",
            "downstream_use": "structural admission precedes but does not satisfy production ingestion gates",
        },
        {
            "trace_link_id": "intake-to-final-readiness",
            "source_artifact": "data/production_intake_downstream_boundary.csv",
            "cited_artifact": "data/final_claim_readiness_matrix.csv",
            "downstream_use": "claim readiness remains blocked without trusted production_target telemetry",
        },
        {
            "trace_link_id": "intake-to-handoff",
            "source_artifact": "data/production_intake_traceability_links.csv",
            "cited_artifact": "data/handoff_claim_traceability.csv",
            "downstream_use": "handoff can cite bundle admission reports without treating them as calibrated evidence",
        },
    ]

    write_csv(
        OUT_RESULTS,
        results,
        [
            "bundle_id",
            "admission_status",
            "payload_rows_seen",
            "required_sections_present",
            "required_streams_present",
            "checksum_validation_attempted",
            "checksum_valid",
            "schema_version_checked",
            "schema_version_valid",
            "join_alias_resolution_attempted",
            "join_alias_valid",
            "unit_normalization_attempted",
            "unit_valid",
            "noise_metadata_present",
            "security_provenance_complete",
            "redaction_policy_unambiguous",
            "evidence_label",
            "production_target_requested",
            "production_target_granted",
            "production_calibrated",
            "production_ready",
            "claim_credit_allowed",
            "expected_blocked_reason",
            "blocked_reason",
        ],
    )
    write_csv(OUT_FAILURES, failure_rows, ["failure_category", "invalid_bundle_count", "fail_closed"])
    write_csv(
        OUT_BOUNDARY,
        boundary,
        [
            "bundle_id",
            "admission_status",
            "production_target_requested",
            "evidence_label",
            "ingestion_gate_schema_valid",
            "downstream_ingestion_boundary",
            "production_calibrated",
            "production_ready",
            "claim_credit_allowed",
            "boundary_reason",
        ],
    )
    write_csv(OUT_TRACE, trace_rows, ["trace_link_id", "source_artifact", "cited_artifact", "downstream_use"])


if __name__ == "__main__":
    main()
