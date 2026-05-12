#!/usr/bin/env python3
# created: 2026-05-12T06:00:00Z
# cycle: 27
# run_id: run-2026-05-11T121649Z
# agent: worker
# milestone: M-INTAKE-1
"""Build production telemetry intake bundle manifests and custody fixtures."""

from __future__ import annotations

import csv
import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

SCHEMA = DATA / "production_dc12_telemetry_schema.csv"
JOIN = DATA / "production_telemetry_join_contract.csv"
PREFLIGHT = DATA / "production_telemetry_preflight_checks.csv"
CONFORMANCE = DATA / "adapter_conformance_contract.csv"
ALIASES = DATA / "adapter_join_alias_map.csv"

OUT_SCHEMA = DATA / "production_intake_bundle_manifest_schema.csv"
OUT_VALID = DATA / "production_intake_valid_bundle_manifest.csv"
OUT_INVALID = DATA / "production_intake_invalid_bundle_manifests.csv"
OUT_CUSTODY = DATA / "production_intake_chain_of_custody_requirements.csv"

EVIDENCE = "production_intake_fixture"
SCHEMA_VERSION = "production_dc12_v1"
REQUIRED_SECTIONS = [
    "bundle identity",
    "telemetry payload inventory",
    "join window",
    "provenance",
    "measurement quality",
    "security/privacy",
    "boundary labels",
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


def checksum(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def count_rows(path: Path) -> int:
    with path.open(newline="") as f:
        return sum(1 for _ in csv.DictReader(f))


def manifest_schema() -> list[dict[str, object]]:
    rows = [
        ("bundle identity", "bundle_id", "stable operator bundle identifier", "missing_chain_of_custody"),
        ("bundle identity", "operator_id", "operator-controlled source identifier", "missing_chain_of_custody"),
        ("bundle identity", "collection_environment", "target environment description", "missing_chain_of_custody"),
        ("bundle identity", "schema_version", f"must equal {SCHEMA_VERSION}", "schema_version_mismatch"),
        ("bundle identity", "created_at", "bundle creation timestamp", "missing_chain_of_custody"),
        ("telemetry payload inventory", "file_path", "relative payload path for each stream", "missing_payload_inventory"),
        ("telemetry payload inventory", "stream_class", "required collector or adapter stream class", "missing_payload_inventory"),
        ("telemetry payload inventory", "row_count", "positive payload row count", "missing_payload_inventory"),
        ("telemetry payload inventory", "checksum_sha256", "sha256 over exact payload file", "missing_checksum"),
        ("telemetry payload inventory", "canonical_schema_target", "production schema or adapter conformance target", "schema_version_mismatch"),
        ("join window", "measurement_run_id", "canonical production run id", "missing_join_window"),
        ("join window", "interval_start_ms", "first included interval start", "clock_window_mismatch"),
        ("join window", "interval_end_ms", "last included interval end", "clock_window_mismatch"),
        ("join window", "clock_domain", "declared monotonic clock domain", "clock_window_mismatch"),
        ("join window", "timezone", "timestamp interpretation", "clock_window_mismatch"),
        ("join window", "sampling_cadence_ms", "collector cadence", "clock_window_mismatch"),
        ("provenance", "collector_identity", "collector name and version", "missing_chain_of_custody"),
        ("provenance", "trusted_source_declaration", "declares whether source is real trusted production telemetry", "missing_chain_of_custody"),
        ("provenance", "signing_attestation_placeholder", "operator signature or attestation pointer", "missing_chain_of_custody"),
        ("provenance", "adapter_conformance_report_path", "validated adapter conformance report pointer", "missing_adapter_conformance_pointer"),
        ("measurement quality", "noise_floor_j", "energy-counter noise floor", "missing_noise_floor"),
        ("measurement quality", "latency_bucket_width_us", "latency histogram resolution", "missing_noise_floor"),
        ("measurement quality", "calibration_method", "counter calibration method", "missing_noise_floor"),
        ("measurement quality", "counter_resolution", "counter resolution declaration", "missing_noise_floor"),
        ("measurement quality", "missingness_declaration", "explicit missing data declaration", "missing_payload_inventory"),
        ("security/privacy", "tenant_label_handling", "tenant labels retained, hashed, or redacted", "incomplete_security_provenance_stream"),
        ("security/privacy", "redaction_policy", "unambiguous redaction policy", "ambiguous_redaction_policy"),
        ("security/privacy", "retention_authorization", "retention policy authorization", "incomplete_security_provenance_stream"),
        ("security/privacy", "security_context_source", "source of security/provenance decisions", "incomplete_security_provenance_stream"),
        ("boundary labels", "evidence_label", "intake fixture or production target label", "fixture_attempted_production_target"),
        ("boundary labels", "production_target_requested", "operator request flag only", "fixture_attempted_production_target"),
        ("boundary labels", "admission_status", "pending, structurally_admissible, or blocked", "missing_chain_of_custody"),
    ]
    return [
        {
            "manifest_section": section,
            "field_name": field,
            "required": "true",
            "expectation": expectation,
            "fail_closed_blocked_reason": reason,
        }
        for section, field, expectation, reason in rows
    ]


def payload_inventory() -> list[dict[str, object]]:
    payloads = [
        (DATA / "adapter_conformance_results.csv", "adapter conformance admission report", "adapter_conformance_contract"),
        (DATA / "adapter_backend_profile_fixtures.csv", "backend-shaped valid adapter profiles", "adapter_conformance_contract"),
        (DATA / "production_dc12_valid_fixture.csv", "production telemetry schema-shaped payload", "production_dc12_telemetry_schema"),
        (DATA / "production_telemetry_join_contract.csv", "deployment join contract", "production_telemetry_join_contract"),
        (DATA / "production_telemetry_preflight_checks.csv", "deployment preflight checks", "production_telemetry_preflight_checks"),
    ]
    rows = []
    for path, stream_class, target in payloads:
        rows.append(
            {
                "file_path": str(path.relative_to(ROOT)),
                "stream_class": stream_class,
                "row_count": count_rows(path),
                "checksum_sha256": checksum(path),
                "canonical_schema_target": target,
            }
        )
    return rows


def valid_manifest_rows() -> list[dict[str, object]]:
    common = {
        "bundle_id": "intake-bundle-001",
        "operator_id": "operator-fixture-a",
        "collection_environment": "fixture_target_shape_only",
        "schema_version": SCHEMA_VERSION,
        "created_at": "2026-05-12T06:00:00Z",
        "measurement_run_id": "prod-intake-run-001",
        "interval_start_ms": "1000",
        "interval_end_ms": "2000",
        "clock_domain": "monotonic_ns",
        "timezone": "UTC",
        "sampling_cadence_ms": "1000",
        "collector_identity": "intake-fixture-collector-v1",
        "trusted_source_declaration": "fixture_not_trusted_real_source",
        "signing_attestation_placeholder": "fixture-attestation-placeholder",
        "adapter_conformance_report_path": "data/adapter_conformance_results.csv",
        "noise_floor_j": "0.2",
        "latency_bucket_width_us": "1.0",
        "calibration_method": "fixture_declared_method_not_production_calibration",
        "counter_resolution": "0.01J; 1us; 1B",
        "missingness_declaration": "none_in_fixture",
        "tenant_label_handling": "tenant labels retained in fixture namespace",
        "redaction_policy": "deterministic fixture redaction; no raw tenant secrets",
        "retention_authorization": "fixture retention authorized for protocol validation",
        "security_context_source": "security/provenance/retention/verifier gates",
        "evidence_label": EVIDENCE,
        "production_target_requested": "true",
        "admission_status": "pending",
        "unit_normalization_attempted": "true",
        "unit_declaration": "W; J; B; us; ms",
        "unit_valid_input": "true",
        "join_alias_resolution_status": "resolved",
        "collection_window_fresh": "true",
        "security_provenance_stream_complete": "true",
        "redaction_policy_unambiguous": "true",
    }
    return [{**common, **payload} for payload in payload_inventory()]


def invalid_manifest_rows(valid: list[dict[str, object]]) -> list[dict[str, object]]:
    base = dict(valid[0])
    cases = [
        ("invalid-missing-checksum", "missing_checksum", {"checksum_sha256": ""}),
        ("invalid-checksum-mismatch", "checksum_mismatch", {"checksum_sha256": "0" * 64}),
        ("invalid-schema-version", "schema_version_mismatch", {"schema_version": "production_dc12_v0"}),
        ("invalid-missing-conformance-pointer", "missing_adapter_conformance_pointer", {"adapter_conformance_report_path": ""}),
        ("invalid-unresolved-join-alias", "unresolved_join_alias", {"join_alias_resolution_status": "unresolved:operator_run_id"}),
        ("invalid-missing-noise-floor", "missing_noise_floor", {"noise_floor_j": ""}),
        ("invalid-incomplete-security-stream", "incomplete_security_provenance_stream", {"security_provenance_stream_complete": "false", "security_context_source": ""}),
        ("invalid-stale-collection-window", "stale_collection_window", {"collection_window_fresh": "false", "interval_end_ms": "900"}),
        ("invalid-ambiguous-redaction", "ambiguous_redaction_policy", {"redaction_policy": "operator-defined", "redaction_policy_unambiguous": "false"}),
        ("invalid-unit-declaration", "invalid_unit", {"unit_declaration": "W; kWh; bytes; ns", "unit_valid_input": "false"}),
        ("invalid-production-target-fixture", "fixture_attempted_production_target", {"evidence_label": "production_target", "trusted_source_declaration": "fixture_not_trusted_real_source"}),
    ]
    rows = []
    for case_id, expected, patch in cases:
        row = dict(base)
        row.update(patch)
        row["bundle_id"] = case_id
        row["expected_blocked_reason"] = expected
        rows.append(row)
    return rows


def custody_requirements(join_rows: list[dict[str, str]], alias_rows: list[dict[str, str]]) -> list[dict[str, object]]:
    alias_summary = "; ".join(f"{r['logical_key']}->{r['canonical_field']}" for r in alias_rows)
    rows = [
        ("manifest_sections_complete", "bundle identity; telemetry payload inventory; join window; provenance; measurement quality; security/privacy; boundary labels", "missing sections block admission before ingestion"),
        ("checksums_present", "sha256 for every payload file", "missing or unverifiable checksums block admission"),
        ("schema_version_matched", SCHEMA_VERSION, "schema mismatch blocks admission before unit or threshold replay"),
        ("join_window_declared", "; ".join(r["required_key"] for r in join_rows), "missing run/interval/workload/object/topology/tenant/security joins block admission"),
        ("alias_resolution_declared", alias_summary, "unresolved aliases block admission; canonical schema remains authoritative"),
        ("adapter_conformance_linked", "data/adapter_conformance_results.csv", "missing conformance pointer blocks admission"),
        ("measurement_quality_declared", "noise floor; calibration method; counter resolution; missingness", "missing noise metadata blocks calibration path"),
        ("security_privacy_declared", "tenant handling; redaction; retention; security context source", "ambiguous redaction or missing security provenance blocks admission"),
        ("boundary_preserved", f"fixtures use {EVIDENCE}", "structural admission does not create production_target evidence or claim credit"),
    ]
    return [
        {
            "requirement_id": requirement_id,
            "required_declaration": declaration,
            "fail_closed_consequence": consequence,
            "applies_before_ingestion": "true",
        }
        for requirement_id, declaration, consequence in rows
    ]


def main() -> None:
    schema_rows = read_csv(SCHEMA)
    join_rows = read_csv(JOIN)
    read_csv(PREFLIGHT)
    read_csv(CONFORMANCE)
    alias_rows = read_csv(ALIASES)
    if "measurement_run_id" not in {row["field_name"] for row in schema_rows}:
        raise ValueError("production schema missing measurement_run_id")

    manifest = manifest_schema()
    valid = valid_manifest_rows()
    invalid = invalid_manifest_rows(valid)
    custody = custody_requirements(join_rows, alias_rows)
    manifest_fields = list(valid[0].keys())
    invalid_fields = sorted(set(manifest_fields) | {"expected_blocked_reason"})

    write_csv(OUT_SCHEMA, manifest, ["manifest_section", "field_name", "required", "expectation", "fail_closed_blocked_reason"])
    write_csv(OUT_VALID, valid, manifest_fields)
    write_csv(OUT_INVALID, invalid, invalid_fields)
    write_csv(OUT_CUSTODY, custody, ["requirement_id", "required_declaration", "fail_closed_consequence", "applies_before_ingestion"])


if __name__ == "__main__":
    main()
