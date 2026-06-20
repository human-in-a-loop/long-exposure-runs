#!/usr/bin/env python3
# created: 2026-05-12T12:05:00Z
# cycle: 33
# run_id: run-2026-05-11T121649Z
# agent: worker
# milestone: M-REDACT-1
"""Evaluate redaction privacy and replay-identifiability boundaries."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

VALID = DATA / "redaction_valid_fixture.csv"
INVALID = DATA / "redaction_invalid_fixtures.csv"
REQUIRED = DATA / "redaction_required_join_fields.csv"
TIMEBASE = DATA / "timebase_integrity_results.csv"
GATECHAIN = DATA / "evidence_gatechain_replay_results.csv"
READINESS = DATA / "final_claim_readiness_matrix.csv"

OUT_RESULTS = DATA / "redaction_integrity_results.csv"
OUT_FAILURES = DATA / "redaction_failure_modes.csv"
OUT_JOIN_BOUNDARY = DATA / "redaction_join_replay_boundary.csv"
OUT_CLAIM_BOUNDARY = DATA / "redaction_claim_credit_boundary.csv"

REQUIRED_JOIN_FIELDS = [
    "measurement_run_pseudonym",
    "bundle_pseudonym",
    "collector_pseudonym",
    "tenant_pseudonym",
    "object_pseudonym",
    "workload_label",
    "topology_bucket",
    "security_context_pseudonym",
    "noise_floor_class",
    "clock_domain_pseudonym",
    "interval_id",
]

REPLAY_REASON_BY_FIELD = {
    "tenant_pseudonym": "missing_tenant_pseudonym",
    "workload_label": "removed_workload_label",
    "topology_bucket": "topology_coarsened_past_threshold_replay",
    "security_context_pseudonym": "suppressed_security_context",
    "noise_floor_class": "removed_measurement_noise_metadata",
    "clock_domain_pseudonym": "redacted_clock_domain",
}

ALLOWED_SOURCE_FIXTURES = {"valid-timebase-complete-fixture"}
ALLOWED_EVIDENCE_LABEL = "redaction_integrity_fixture"


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


def parse_collision_count(row: dict[str, str]) -> tuple[int, str, str]:
    raw = row.get("join_key_collision_count", "")
    try:
        value = int(raw or "0")
    except ValueError:
        return 0, "invalid_join_key_collision_count", "join_key_collision_count"
    if value < 0:
        return value, "negative_join_key_collision_count", "join_key_collision_count"
    return value, "", ""


def block(row: dict[str, str]) -> tuple[str, str, str]:
    if not row["source_fixture_id"]:
        return "missing_source_fixture_id", "source_fixture_id", "replay_nonidentifiable"
    if row["source_fixture_id"] not in ALLOWED_SOURCE_FIXTURES:
        return "unknown_source_fixture_id", "source_fixture_id", "replay_nonidentifiable"
    if row["evidence_label"] == "production_target":
        return "fixture_attempted_production_calibration", "evidence_label", "replay_nonidentifiable"
    if row["evidence_label"] != ALLOWED_EVIDENCE_LABEL:
        return "unsupported_evidence_label", "evidence_label", "replay_nonidentifiable"
    if row["raw_tenant_identifier"]:
        return "raw_tenant_identifier_leaked", "raw_tenant_identifier", "privacy_leakage"
    if row["raw_tool_output_uri"]:
        return "raw_tool_output_uri_leaked", "raw_tool_output_uri", "privacy_leakage"
    collision_count, collision_reason, collision_field = parse_collision_count(row)
    if collision_reason:
        return collision_reason, collision_field, "replay_nonidentifiable"
    if collision_count > 0:
        return "irreversible_join_key_collision", "join_key_collision_count", "replay_nonidentifiable"
    if not row["tenant_pseudonym"]:
        return "missing_tenant_pseudonym", "tenant_pseudonym", "replay_nonidentifiable"
    if row["object_pseudonym"] != row["object_pseudonym_interval_2"]:
        return "unstable_object_pseudonym_across_intervals", "object_pseudonym_interval_2", "replay_nonidentifiable"
    if not row["object_pseudonym"]:
        return "missing_object_pseudonym", "object_pseudonym", "replay_nonidentifiable"
    if row["topology_granularity"] not in {"threshold_topology_bucket", "target_topology"}:
        return "topology_coarsened_past_threshold_replay", "topology_granularity", "replay_nonidentifiable"
    for field in REQUIRED_JOIN_FIELDS:
        if not row.get(field, ""):
            return REPLAY_REASON_BY_FIELD.get(field, f"missing_{field}"), field, "replay_nonidentifiable"
    return "", "", ""


def join_fraction(row: dict[str, str]) -> float:
    preserved = 0
    for field in REQUIRED_JOIN_FIELDS:
        if row.get(field, ""):
            preserved += 1
    if row.get("object_pseudonym") != row.get("object_pseudonym_interval_2"):
        preserved -= 1
    collision_count, collision_reason, _ = parse_collision_count(row)
    if collision_reason or collision_count > 0:
        preserved -= 2
    return max(0, preserved) / len(REQUIRED_JOIN_FIELDS)


def evaluate(rows: list[dict[str, str]]) -> list[dict[str, object]]:
    results = []
    for row in rows:
        reason, field, status = block(row)
        admissible = reason == "" and row["case_type"] == "valid_fixture"
        results.append(
            {
                "case_id": row["case_id"],
                "case_type": row["case_type"],
                "policy_profile_id": row["policy_profile_id"],
                "source_fixture_id": row["source_fixture_id"],
                "redaction_admissible": str(admissible).lower(),
                "redaction_status": "redaction_admissible" if admissible else status,
                "join_survival_fraction": f"{join_fraction(row):.3f}",
                "privacy_leakage_absent": str(not row["raw_tenant_identifier"] and not row["raw_tool_output_uri"]).lower(),
                "replay_identifiable": str(admissible).lower(),
                "blocked_field": field,
                "blocked_reason": reason,
                "expected_blocked_reason": row.get("expected_blocked_reason", ""),
                "expected_reason_matched": str((not row.get("expected_blocked_reason")) or row.get("expected_blocked_reason") == reason).lower(),
                "production_calibrated": "false",
                "production_ready": "false",
                "claim_credit_allowed": "false",
                "export_quality_precondition_only": "true",
            }
        )
    return results


def failure_rows(results: list[dict[str, object]]) -> list[dict[str, object]]:
    counts = Counter((str(row["redaction_status"]), str(row["blocked_reason"])) for row in results if row["blocked_reason"])
    return [
        {"redaction_status": status, "blocked_reason": reason, "case_count": count, "fail_closed": "true"}
        for (status, reason), count in sorted(counts.items())
    ]


def join_boundary(results: list[dict[str, object]]) -> list[dict[str, object]]:
    return [
        {
            "case_id": row["case_id"],
            "redaction_admissible": row["redaction_admissible"],
            "join_survival_fraction": row["join_survival_fraction"],
            "redaction_status": row["redaction_status"],
            "blocked_reason": row["blocked_reason"],
            "over_redaction_is_threshold_miss": "false",
            "dc001_dc002_replay_allowed": row["redaction_admissible"],
        }
        for row in results
    ]


def claim_boundary(results: list[dict[str, object]]) -> list[dict[str, object]]:
    gatechain_allowed = any(row["production_claim_credit_allowed"] == "true" for row in read_csv(GATECHAIN))
    return [
        {
            "case_id": row["case_id"],
            "redaction_admissible": row["redaction_admissible"],
            "existing_gatechain_allowed": str(gatechain_allowed).lower(),
            "export_quality_precondition_only": "true",
            "production_calibrated": "false",
            "production_ready": "false",
            "claim_credit_allowed": "false",
            "boundary_reason": "redaction_export_quality_precondition_only" if row["redaction_admissible"] == "true" else row["blocked_reason"],
        }
        for row in results
    ]


def main() -> None:
    required_declared = {row["field_name"] for row in read_csv(REQUIRED)}
    missing = sorted(set(REQUIRED_JOIN_FIELDS) - required_declared)
    if missing:
        raise ValueError(f"missing required redaction join fields: {missing}")
    if not any(row["timing_admissible"] == "true" for row in read_csv(TIMEBASE)):
        raise ValueError("redaction harness requires at least one timing-admissible fixture")
    if any(row["production_ready"] == "true" for row in read_csv(READINESS)):
        raise ValueError("existing final readiness unexpectedly contains production-ready claim")
    results = evaluate(read_csv(VALID) + read_csv(INVALID))
    write_csv(
        OUT_RESULTS,
        results,
        [
            "case_id",
            "case_type",
            "policy_profile_id",
            "source_fixture_id",
            "redaction_admissible",
            "redaction_status",
            "join_survival_fraction",
            "privacy_leakage_absent",
            "replay_identifiable",
            "blocked_field",
            "blocked_reason",
            "expected_blocked_reason",
            "expected_reason_matched",
            "production_calibrated",
            "production_ready",
            "claim_credit_allowed",
            "export_quality_precondition_only",
        ],
    )
    write_csv(OUT_FAILURES, failure_rows(results), ["redaction_status", "blocked_reason", "case_count", "fail_closed"])
    write_csv(
        OUT_JOIN_BOUNDARY,
        join_boundary(results),
        ["case_id", "redaction_admissible", "join_survival_fraction", "redaction_status", "blocked_reason", "over_redaction_is_threshold_miss", "dc001_dc002_replay_allowed"],
    )
    write_csv(
        OUT_CLAIM_BOUNDARY,
        claim_boundary(results),
        ["case_id", "redaction_admissible", "existing_gatechain_allowed", "export_quality_precondition_only", "production_calibrated", "production_ready", "claim_credit_allowed", "boundary_reason"],
    )


if __name__ == "__main__":
    main()
