#!/usr/bin/env python3
# created: 2026-05-12T12:00:00Z
# cycle: 33
# run_id: run-2026-05-11T121649Z
# agent: worker
# milestone: M-REDACT-1
"""Build redaction/minimization fixtures for replay-identifiable telemetry."""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

INPUTS = [
    DATA / "production_dc12_telemetry_schema.csv",
    DATA / "production_telemetry_join_contract.csv",
    DATA / "evidence_gatechain_traceability_matrix.csv",
    DATA / "timebase_integrity_results.csv",
    DATA / "final_claim_readiness_matrix.csv",
    DATA / "handoff_claim_traceability.csv",
]

OUT_SCHEMA = DATA / "redaction_integrity_schema.csv"
OUT_PROFILES = DATA / "redaction_policy_profiles.csv"
OUT_VALID = DATA / "redaction_valid_fixture.csv"
OUT_INVALID = DATA / "redaction_invalid_fixtures.csv"
OUT_REQUIRED = DATA / "redaction_required_join_fields.csv"

FIELDS = [
    "case_id",
    "case_type",
    "policy_profile_id",
    "source_fixture_id",
    "measurement_run_pseudonym",
    "bundle_pseudonym",
    "collector_pseudonym",
    "tenant_pseudonym",
    "object_pseudonym",
    "object_pseudonym_interval_2",
    "workload_label",
    "topology_bucket",
    "topology_granularity",
    "security_context_pseudonym",
    "noise_floor_class",
    "clock_domain_pseudonym",
    "interval_id",
    "raw_tenant_identifier",
    "raw_tool_output_uri",
    "join_key_collision_count",
    "evidence_label",
    "expected_blocked_reason",
    "notes",
]

REQUIRED_FIELDS = [
    ("measurement_run_pseudonym", "stable_pseudonym", "run identity across redacted streams"),
    ("bundle_pseudonym", "stable_pseudonym", "bundle continuity with intake/attestation/gatechain"),
    ("collector_pseudonym", "stable_pseudonym", "collector continuity without raw collector identity"),
    ("tenant_pseudonym", "stable_pseudonym", "tenant concurrency and isolation replay"),
    ("object_pseudonym", "stable_pseudonym", "object-level reuse and byte movement replay"),
    ("workload_label", "coarsenable_to_threshold_class", "threshold selection and controls"),
    ("topology_bucket", "coarsenable_to_threshold_topology", "target topology and CXL contention replay"),
    ("security_context_pseudonym", "stable_pseudonym", "security/provenance zero-credit enforcement"),
    ("noise_floor_class", "bucketed", "above-noise measurement interpretation"),
    ("clock_domain_pseudonym", "stable_pseudonym", "timebase join and skew interpretation"),
    ("interval_id", "preserve", "counter interval joins"),
]

BASE = {
    "case_id": "valid-minimal-redaction-fixture",
    "case_type": "valid_fixture",
    "policy_profile_id": "profile-minimal-safe-replayable",
    "source_fixture_id": "valid-timebase-complete-fixture",
    "measurement_run_pseudonym": "run-pseudo-001",
    "bundle_pseudonym": "bundle-pseudo-001",
    "collector_pseudonym": "collector-pseudo-001",
    "tenant_pseudonym": "tenant-pseudo-001",
    "object_pseudonym": "object-pseudo-ragctx-001",
    "object_pseudonym_interval_2": "object-pseudo-ragctx-001",
    "workload_label": "RAG",
    "topology_bucket": "target_cxl_pool",
    "topology_granularity": "threshold_topology_bucket",
    "security_context_pseudonym": "security-context-pseudo-001",
    "noise_floor_class": "above_dc12_noise_floor",
    "clock_domain_pseudonym": "clock-domain-pseudo-ptp-a",
    "interval_id": "interval-0001",
    "raw_tenant_identifier": "",
    "raw_tool_output_uri": "",
    "join_key_collision_count": 0,
    "evidence_label": "redaction_integrity_fixture",
    "expected_blocked_reason": "",
    "notes": "minimal fixture preserves replay joins using stable pseudonyms and no raw sensitive identifiers",
}

INVALIDS = [
    ("invalid-unknown-source-fixture", {"source_fixture_id": "not-a-timebase-fixture"}, "unknown_source_fixture_id"),
    ("invalid-missing-source-fixture", {"source_fixture_id": ""}, "missing_source_fixture_id"),
    ("invalid-unsupported-evidence-label", {"evidence_label": "host_local_proxy"}, "unsupported_evidence_label"),
    ("invalid-missing-evidence-label", {"evidence_label": ""}, "unsupported_evidence_label"),
    ("invalid-empty-redaction-policy", {"tenant_pseudonym": "", "object_pseudonym": "", "workload_label": ""}, "missing_tenant_pseudonym"),
    ("invalid-all-fields-raw", {"raw_tenant_identifier": "tenant-prod-acme-payroll", "raw_tool_output_uri": "s3://prod-tool-output/customer/doc"}, "raw_tenant_identifier_leaked"),
    ("invalid-all-fields-suppressed", {"tenant_pseudonym": "", "object_pseudonym": "", "workload_label": "", "topology_bucket": "", "security_context_pseudonym": "", "noise_floor_class": "", "clock_domain_pseudonym": ""}, "missing_tenant_pseudonym"),
    ("invalid-missing-tenant-pseudonym", {"tenant_pseudonym": ""}, "missing_tenant_pseudonym"),
    ("invalid-unstable-object-pseudonym", {"object_pseudonym_interval_2": "object-pseudo-ragctx-rotated"}, "unstable_object_pseudonym_across_intervals"),
    ("invalid-removed-workload-label", {"workload_label": ""}, "removed_workload_label"),
    ("invalid-topology-overcoarsened", {"topology_bucket": "region-wide", "topology_granularity": "region_only"}, "topology_coarsened_past_threshold_replay"),
    ("invalid-suppressed-security-context", {"security_context_pseudonym": ""}, "suppressed_security_context"),
    ("invalid-removed-noise-metadata", {"noise_floor_class": ""}, "removed_measurement_noise_metadata"),
    ("invalid-redacted-clock-domain", {"clock_domain_pseudonym": ""}, "redacted_clock_domain"),
    ("invalid-raw-tenant-identifier", {"raw_tenant_identifier": "tenant-prod-acme-payroll"}, "raw_tenant_identifier_leaked"),
    ("invalid-raw-tool-output-uri", {"raw_tool_output_uri": "s3://prod-tool-output/customer/doc"}, "raw_tool_output_uri_leaked"),
    ("invalid-join-key-collision", {"tenant_pseudonym": "shared-pseudo", "object_pseudonym": "shared-pseudo", "join_key_collision_count": 2}, "irreversible_join_key_collision"),
    ("invalid-negative-join-key-collision", {"join_key_collision_count": -1}, "negative_join_key_collision_count"),
    ("invalid-nonnumeric-join-key-collision", {"join_key_collision_count": "not-an-integer"}, "invalid_join_key_collision_count"),
    ("invalid-fixture-attempted-production-calibration", {"evidence_label": "production_target"}, "fixture_attempted_production_calibration"),
]

PROFILES = [
    ("profile-minimal-safe-replayable", "stable pseudonyms for run/bundle/collector/tenant/object/security/clock; threshold labels bucketed", "true", "false", "false"),
    ("profile-empty-redaction-policy", "policy omits required handling", "false", "false", "true"),
    ("profile-all-fields-raw", "no redaction; raw sensitive identifiers exported", "false", "true", "false"),
    ("profile-all-fields-suppressed", "all potentially sensitive fields removed", "false", "false", "true"),
    ("profile-overcoarsened-topology", "topology only region-wide, below threshold replay granularity", "false", "false", "true"),
    ("profile-unstable-pseudonyms", "pseudonyms rotate inside a replay interval", "false", "false", "true"),
    ("profile-colliding-pseudonyms", "irreversible many-to-one pseudonym collision", "false", "false", "true"),
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


def require_inputs() -> None:
    for path in INPUTS:
        read_csv(path)


def invalid_rows() -> list[dict[str, object]]:
    rows = []
    for case_id, overrides, reason in INVALIDS:
        row = dict(BASE)
        row.update(overrides)
        row.update(
            {
                "case_id": case_id,
                "case_type": "invalid_fixture",
                "policy_profile_id": "profile-" + case_id.removeprefix("invalid-"),
                "expected_blocked_reason": reason,
                "notes": "malformed redaction must fail closed as privacy_leakage or replay_nonidentifiable",
            }
        )
        rows.append(row)
    return rows


def main() -> None:
    require_inputs()
    schema_rows = [
        {
            "field_name": field,
            "required": "true" if field not in {"raw_tenant_identifier", "raw_tool_output_uri", "expected_blocked_reason", "notes"} else "false",
            "redaction_rule": "forbidden_raw" if field.startswith("raw_") else "stable_or_bucketed_for_replay",
            "purpose": "redaction fixture field",
        }
        for field in FIELDS
    ]
    required_rows = [
        {"field_name": field, "allowed_transform": transform, "why_required": why, "raw_identifier_allowed": "false"}
        for field, transform, why in REQUIRED_FIELDS
    ]
    profile_rows = [
        {
            "policy_profile_id": profile_id,
            "description": description,
            "expected_redaction_admissible": admissible,
            "privacy_leakage_expected": leakage,
            "replay_loss_expected": replay_loss,
        }
        for profile_id, description, admissible, leakage, replay_loss in PROFILES
    ]
    write_csv(OUT_SCHEMA, schema_rows, ["field_name", "required", "redaction_rule", "purpose"])
    write_csv(OUT_REQUIRED, required_rows, ["field_name", "allowed_transform", "why_required", "raw_identifier_allowed"])
    write_csv(OUT_PROFILES, profile_rows, ["policy_profile_id", "description", "expected_redaction_admissible", "privacy_leakage_expected", "replay_loss_expected"])
    write_csv(OUT_VALID, [BASE], FIELDS)
    write_csv(OUT_INVALID, invalid_rows(), FIELDS)


if __name__ == "__main__":
    main()
