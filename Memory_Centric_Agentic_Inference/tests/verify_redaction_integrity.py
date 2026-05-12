#!/usr/bin/env python3
# created: 2026-05-12T12:15:00Z
# cycle: 33
# run_id: run-2026-05-11T121649Z
# agent: worker
# milestone: M-REDACT-1

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

REQUIRED_JOIN_FIELDS = {
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
}

EXPECTED_INVALID = {
    "invalid-unknown-source-fixture": "unknown_source_fixture_id",
    "invalid-missing-source-fixture": "missing_source_fixture_id",
    "invalid-unsupported-evidence-label": "unsupported_evidence_label",
    "invalid-missing-evidence-label": "unsupported_evidence_label",
    "invalid-empty-redaction-policy": "missing_tenant_pseudonym",
    "invalid-all-fields-raw": "raw_tenant_identifier_leaked",
    "invalid-all-fields-suppressed": "missing_tenant_pseudonym",
    "invalid-missing-tenant-pseudonym": "missing_tenant_pseudonym",
    "invalid-unstable-object-pseudonym": "unstable_object_pseudonym_across_intervals",
    "invalid-removed-workload-label": "removed_workload_label",
    "invalid-topology-overcoarsened": "topology_coarsened_past_threshold_replay",
    "invalid-suppressed-security-context": "suppressed_security_context",
    "invalid-removed-noise-metadata": "removed_measurement_noise_metadata",
    "invalid-redacted-clock-domain": "redacted_clock_domain",
    "invalid-raw-tenant-identifier": "raw_tenant_identifier_leaked",
    "invalid-raw-tool-output-uri": "raw_tool_output_uri_leaked",
    "invalid-join-key-collision": "irreversible_join_key_collision",
    "invalid-negative-join-key-collision": "negative_join_key_collision_count",
    "invalid-nonnumeric-join-key-collision": "invalid_join_key_collision_count",
    "invalid-fixture-attempted-production-calibration": "fixture_attempted_production_calibration",
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
    required = read_csv(DATA / "redaction_required_join_fields.csv")
    schema = read_csv(DATA / "redaction_integrity_schema.csv")
    valid = read_csv(DATA / "redaction_valid_fixture.csv")
    invalid = read_csv(DATA / "redaction_invalid_fixtures.csv")
    profiles = read_csv(DATA / "redaction_policy_profiles.csv")
    results = read_csv(DATA / "redaction_integrity_results.csv")
    failures = read_csv(DATA / "redaction_failure_modes.csv")
    join_boundary = read_csv(DATA / "redaction_join_replay_boundary.csv")
    claim_boundary = read_csv(DATA / "redaction_claim_credit_boundary.csv")

    required_fields = {row["field_name"] for row in required}
    assert REQUIRED_JOIN_FIELDS <= required_fields
    assert all(row["raw_identifier_allowed"] == "false" for row in required)
    schema_fields = {row["field_name"] for row in schema}
    assert REQUIRED_JOIN_FIELDS <= schema_fields
    assert len(valid) == 1
    assert len(invalid) == len(EXPECTED_INVALID)
    assert any(row["policy_profile_id"] == "profile-all-fields-raw" for row in profiles)
    assert any(row["policy_profile_id"] == "profile-all-fields-suppressed" for row in profiles)

    result = by_case(results)
    complete = result["valid-minimal-redaction-fixture"]
    assert complete["redaction_admissible"] == "true"
    assert complete["redaction_status"] == "redaction_admissible"
    assert complete["join_survival_fraction"] == "1.000"
    assert complete["privacy_leakage_absent"] == "true"
    assert complete["production_calibrated"] == "false"
    assert complete["production_ready"] == "false"
    assert complete["claim_credit_allowed"] == "false"

    for case_id, reason in EXPECTED_INVALID.items():
        row = result[case_id]
        assert row["redaction_admissible"] == "false"
        assert row["blocked_reason"] == reason
        assert row["expected_reason_matched"] == "true"
        assert row["redaction_status"] in {"privacy_leakage", "replay_nonidentifiable"}

    assert result["invalid-raw-tenant-identifier"]["redaction_status"] == "privacy_leakage"
    assert result["invalid-raw-tool-output-uri"]["redaction_status"] == "privacy_leakage"
    assert result["invalid-unknown-source-fixture"]["redaction_status"] == "replay_nonidentifiable"
    assert result["invalid-unsupported-evidence-label"]["redaction_status"] == "replay_nonidentifiable"
    assert result["invalid-removed-workload-label"]["redaction_status"] == "replay_nonidentifiable"
    assert result["invalid-suppressed-security-context"]["redaction_status"] == "replay_nonidentifiable"
    assert result["invalid-removed-noise-metadata"]["redaction_status"] == "replay_nonidentifiable"
    assert result["invalid-redacted-clock-domain"]["redaction_status"] == "replay_nonidentifiable"
    assert result["invalid-all-fields-raw"]["blocked_reason"] == "raw_tenant_identifier_leaked"
    assert result["invalid-all-fields-suppressed"]["blocked_reason"] == "missing_tenant_pseudonym"

    assert all(row["fail_closed"] == "true" for row in failures)
    assert any(row["redaction_status"] == "privacy_leakage" for row in failures)
    assert any(row["redaction_status"] == "replay_nonidentifiable" for row in failures)
    assert all(row["over_redaction_is_threshold_miss"] == "false" for row in join_boundary)
    assert all(row["redaction_status"] != "threshold_failed" for row in join_boundary)
    assert all(row["production_calibrated"] == "false" for row in claim_boundary)
    assert all(row["production_ready"] == "false" for row in claim_boundary)
    assert all(row["claim_credit_allowed"] == "false" for row in claim_boundary)

    for fig in [
        DATA / "redaction_join_survival.png",
        DATA / "redaction_failure_modes.png",
        DATA / "redaction_claim_boundary.png",
    ]:
        assert_png_nonblank(fig)

    print("OK: redaction integrity verified.")


if __name__ == "__main__":
    main()
