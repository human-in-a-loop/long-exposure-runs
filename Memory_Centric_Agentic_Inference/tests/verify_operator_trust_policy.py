#!/usr/bin/env python3
# created: 2026-05-12T08:15:00Z
# cycle: 29
# run_id: run-2026-05-11T121649Z
# agent: worker
# milestone: M-TRUSTPOL-1

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
REQUIRED_DIMENSIONS = {
    "trust_root",
    "key_custody",
    "key_lifecycle",
    "collector_identity",
    "telemetry_binding",
    "replay_protection",
    "tenant_security",
    "auditability",
    "boundary",
}
EXPECTED_BLOCKS = {
    "fixture_hmac_not_production_root",
    "missing_revocation_path",
    "exportable_production_key",
    "unbound_collector_identity",
    "missing_replay_protection",
    "missing_audit_log",
    "missing_tenant_security_binding",
    "unsupported_trust_root",
    "policy_attempted_production_trust",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
        rows = list(csv.DictReader(f))
    assert rows, f"{path.relative_to(ROOT)} is empty"
    return rows


def assert_png_nonblank(path: Path) -> None:
    data = path.read_bytes()
    assert data.startswith(b"\x89PNG\r\n\x1a\n"), f"{path.relative_to(ROOT)} is not a PNG"
    assert len(data) > 10_000, f"{path.relative_to(ROOT)} is too small"


def main() -> None:
    schema = read_csv(DATA / "operator_trust_policy_schema.csv")
    profiles = read_csv(DATA / "operator_trust_policy_profiles.csv")
    invalid_profiles = read_csv(DATA / "operator_trust_policy_invalid_profiles.csv")
    lifecycle = read_csv(DATA / "operator_key_lifecycle_matrix.csv")
    replacement = read_csv(DATA / "operator_attestation_replacement_map.csv")
    results = read_csv(DATA / "operator_trust_policy_results.csv")
    failures = read_csv(DATA / "operator_trust_policy_failure_modes.csv")
    boundary = read_csv(DATA / "operator_trust_policy_boundary.csv")
    trace = read_csv(DATA / "operator_trust_policy_traceability_links.csv")
    attest = read_csv(DATA / "production_attestation_results.csv")

    assert REQUIRED_DIMENSIONS <= {row["policy_dimension"] for row in schema}
    assert {"provision", "activate", "rotate", "revoke", "audit"} <= {row["lifecycle_phase"] for row in lifecycle}
    assert any(row["fixture_mechanism"] == "hmac_sha256_test_fixture" and row["production_replacement"] == "operator_kms_or_hsm_signature" for row in replacement)
    assert {row["input_present"] for row in replacement} <= {"true", "false"}

    complete = next(row for row in results if row["profile_id"] == "complete-kms-policy-fixture")
    assert complete["mechanically_valid_signature"] == "true"
    assert complete["trust_policy_admissible"] == "true"
    assert complete["attestation_source_trusted"] == "false"
    assert complete["production_trust_established"] == "false"
    assert complete["production_target_granted"] == "false"
    assert complete["production_calibrated"] == "false"
    assert complete["production_ready"] == "false"
    assert complete["claim_credit_allowed"] == "false"

    blocked = [row for row in results if row["blocked_reason"]]
    assert len(blocked) == len(invalid_profiles)
    observed = {row["blocked_reason"] for row in blocked}
    assert EXPECTED_BLOCKS <= observed, observed
    for row in blocked:
        if row["expected_blocked_reason"]:
            assert row["expected_blocked_reason"] == row["blocked_reason"]
        assert row["trust_policy_admissible"] == "false"

    hmac_case = next(row for row in results if row["profile_id"] == "invalid-fixture-hmac-production-root")
    assert hmac_case["blocked_reason"] == "fixture_hmac_not_production_root"
    mechanical_only = next(row for row in results if row["profile_id"] == "invalid-mechanical-signature-only")
    assert mechanical_only["mechanically_valid_signature"] == "true"
    assert mechanical_only["trust_policy_admissible"] == "false"
    missing_firmware = next(row for row in results if row["profile_id"] == "invalid-missing-firmware-identity")
    assert missing_firmware["blocked_reason"] == "unbound_collector_identity"
    assert any(row["signature_valid"] == "true" and row["attestation_source_trusted"] == "false" for row in attest)

    assert all(row["fail_closed"] == "true" for row in failures)
    assert sum(int(row["invalid_profile_count"]) for row in failures) == len(blocked)
    assert all(row["attestation_source_trusted"] == "false" for row in boundary)
    assert all(row["production_trust_established"] == "false" for row in boundary)
    assert all(row["production_calibrated"] == "false" for row in boundary)
    assert all(row["production_ready"] == "false" for row in boundary)
    assert all(row["claim_credit_allowed"] == "false" for row in boundary)
    assert any(row["trust_policy_admissible"] == "true" and row["production_ready"] == "false" for row in boundary)
    assert {row["trace_link_id"] for row in trace} >= {
        "trust-policy-to-attestation-envelope",
        "trust-policy-to-intake-custody",
        "trust-policy-to-deployment-preflight",
        "trust-policy-to-final-readiness",
    }

    for fig in [
        DATA / "operator_trust_policy_coverage.png",
        DATA / "operator_trust_policy_failures.png",
        DATA / "operator_trust_policy_boundary.png",
    ]:
        assert_png_nonblank(fig)

    print("OK: operator trust policy verified.")


if __name__ == "__main__":
    main()
