#!/usr/bin/env python3
# created: 2026-05-12T07:15:00Z
# cycle: 28
# run_id: run-2026-05-11T121649Z
# agent: worker
# milestone: M-ATTEST-1

from __future__ import annotations

import csv
import hashlib
import hmac
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
SECRET = "test-only-secret-active-a"
SIGNED_FIELDS = [
    "key_id",
    "operator_id",
    "collector_id",
    "schema_version",
    "bundle_id",
    "manifest_digest",
    "payload_digest_set_digest",
    "adapter_conformance_digest",
    "collection_window_start",
    "collection_window_end",
    "issued_at",
    "expires_at",
]
REQUIRED_FIELDS = {
    "key_id",
    "operator_id",
    "collector_id",
    "schema_version",
    "bundle_id",
    "manifest_digest",
    "payload_digest_set_digest",
    "adapter_conformance_digest",
    "collection_window_start",
    "collection_window_end",
    "issued_at",
    "expires_at",
    "signature",
}
EXPECTED_BLOCKS = {
    "missing_signature",
    "unknown_key_id",
    "expired_key",
    "revoked_key",
    "operator_identity_mismatch",
    "collector_identity_mismatch",
    "mismatched_manifest_digest",
    "mismatched_payload_digest_set",
    "stale_collection_window",
    "replayed_bundle_id",
    "fixture_attempted_production_trust",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
        rows = list(csv.DictReader(f))
    assert rows, f"{path.relative_to(ROOT)} is empty"
    return rows


def canonical(obj: object) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def assert_png_nonblank(path: Path) -> None:
    data = path.read_bytes()
    assert data.startswith(b"\x89PNG\r\n\x1a\n"), f"{path.relative_to(ROOT)} is not a PNG"
    assert len(data) > 10_000, f"{path.relative_to(ROOT)} is too small"


def signature_input(row: dict[str, str]) -> str:
    return canonical({field: row[field] for field in SIGNED_FIELDS})


def main() -> None:
    schema = read_csv(DATA / "production_attestation_envelope_schema.csv")
    keys = read_csv(DATA / "production_attestation_key_registry.csv")
    valid_envelopes = read_csv(DATA / "production_attestation_valid_envelopes.csv")
    invalid_envelopes = read_csv(DATA / "production_attestation_invalid_envelopes.csv")
    replay = read_csv(DATA / "production_attestation_replay_registry.csv")
    results = read_csv(DATA / "production_attestation_results.csv")
    failures = read_csv(DATA / "production_attestation_failure_modes.csv")
    boundary = read_csv(DATA / "production_attestation_intake_boundary.csv")
    trace = read_csv(DATA / "production_attestation_traceability_links.csv")

    assert REQUIRED_FIELDS <= {row["field_name"] for row in schema if row["required"] == "true"}
    assert {row["key_state"] for row in keys} >= {"active", "expired", "revoked", "unknown"}
    assert any(row["bundle_id"] == "replayed-intake-bundle-001" for row in replay)

    valid = valid_envelopes[0]
    expected_signature = hmac.new(SECRET.encode("utf-8"), signature_input(valid).encode("utf-8"), hashlib.sha256).hexdigest()
    assert hmac.compare_digest(expected_signature, valid["signature"])
    assert valid["evidence_label"] == "test_attestation_fixture"
    assert valid["attestation_source_trusted"] == "false"
    assert valid["production_trust_established"] == "false"

    valid_result = next(row for row in results if row["case_id"] == "valid-test-attestation")
    assert valid_result["attestation_status"] == "mechanically_valid"
    assert valid_result["signature_checked"] == "true"
    assert valid_result["signature_valid"] == "true"
    assert valid_result["attestation_source_trusted"] == "false"
    assert valid_result["production_trust_established"] == "false"
    assert valid_result["production_target_granted"] == "false"
    assert valid_result["production_calibrated"] == "false"
    assert valid_result["production_ready"] == "false"
    assert valid_result["claim_credit_allowed"] == "false"

    invalid = [row for row in results if row["attestation_status"] == "blocked"]
    assert len(invalid) == len(invalid_envelopes)
    observed = {row["blocked_reason"] for row in invalid}
    assert EXPECTED_BLOCKS <= observed, observed
    for row in invalid:
        if row["expected_blocked_reason"]:
            assert row["expected_blocked_reason"] == row["blocked_reason"]

    assert next(row for row in results if row["case_id"] == "invalid-mismatched-manifest-digest")["manifest_digest_bound"] == "false"
    assert next(row for row in results if row["case_id"] == "invalid-mismatched-payload-digest-set")["payload_digest_set_bound"] == "false"
    assert next(row for row in results if row["case_id"] == "invalid-unknown-key")["blocked_reason"] == "unknown_key_id"
    assert next(row for row in results if row["case_id"] == "invalid-expired-key")["blocked_reason"] == "expired_key"
    assert next(row for row in results if row["case_id"] == "invalid-revoked-key")["blocked_reason"] == "revoked_key"
    assert next(row for row in results if row["case_id"] == "invalid-replayed-bundle-id")["replay_valid"] == "false"

    assert all(row["fail_closed"] == "true" for row in failures)
    assert sum(int(row["invalid_envelope_count"]) for row in failures) == len(invalid)
    assert all(row["attestation_source_trusted"] == "false" for row in boundary)
    assert all(row["production_trust_established"] == "false" for row in boundary)
    assert all(row["production_calibrated"] == "false" for row in boundary)
    assert all(row["production_ready"] == "false" for row in boundary)
    assert all(row["claim_credit_allowed"] == "false" for row in boundary)
    assert any(row["signature_valid"] == "true" and row["attestation_source_trusted"] == "false" for row in boundary)
    assert {row["trace_link_id"] for row in trace} >= {
        "attestation-to-intake-manifest",
        "attestation-to-key-registry",
        "attestation-to-intake-boundary",
        "attestation-to-final-readiness",
    }

    for fig in [
        DATA / "production_attestation_envelope_coverage.png",
        DATA / "production_attestation_failure_modes.png",
        DATA / "production_attestation_boundary.png",
    ]:
        assert_png_nonblank(fig)

    print("OK: production attestation envelope verified.")


if __name__ == "__main__":
    main()
