#!/usr/bin/env python3
# created: 2026-05-12T08:00:00Z
# cycle: 29
# run_id: run-2026-05-11T121649Z
# agent: worker
# milestone: M-TRUSTPOL-1
"""Build fixture operator trust policies for production signing replacement."""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

ATTEST_SCHEMA = DATA / "production_attestation_envelope_schema.csv"
ATTEST_RESULTS = DATA / "production_attestation_results.csv"
CUSTODY = DATA / "production_intake_chain_of_custody_requirements.csv"
PREFLIGHT = DATA / "production_telemetry_preflight_checks.csv"

OUT_SCHEMA = DATA / "operator_trust_policy_schema.csv"
OUT_PROFILES = DATA / "operator_trust_policy_profiles.csv"
OUT_INVALID = DATA / "operator_trust_policy_invalid_profiles.csv"
OUT_LIFECYCLE = DATA / "operator_key_lifecycle_matrix.csv"
OUT_REPLACEMENT = DATA / "operator_attestation_replacement_map.csv"

PROFILE_FIELDS = [
    "profile_id",
    "policy_scope",
    "evidence_label",
    "trust_root_type",
    "trust_root_supported",
    "fixture_hmac_presented_as_production_root",
    "key_non_exportable",
    "access_control_defined",
    "rotation_interval_days",
    "revocation_path_defined",
    "collector_registered",
    "collector_software_identity_bound",
    "collector_firmware_identity_bound",
    "topology_binding_defined",
    "manifest_digest_binding",
    "payload_digest_set_binding",
    "adapter_conformance_digest_binding",
    "schema_version_binding",
    "bundle_id_registry_defined",
    "nonce_or_monotonic_sequence_defined",
    "tenant_isolation_defined",
    "security_context_source_defined",
    "retention_authorization_defined",
    "append_only_audit_log",
    "verifier_identity_defined",
    "incident_response_owner",
    "mechanically_valid_signature",
    "attempted_attestation_source_trusted",
    "attempted_production_trust_established",
    "expected_blocked_reason",
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


def schema_rows() -> list[dict[str, str]]:
    dimensions = [
        ("trust_root_type", "trust_root", "KMS, HSM, hardware attestation, or operator CA; fixture HMAC and unsupported placeholders fail closed"),
        ("trust_root_supported", "trust_root", "declares whether the root class is production-supported"),
        ("key_non_exportable", "key_custody", "production signing key material must be non-exportable"),
        ("access_control_defined", "key_custody", "operator access control and signer authorization must be named"),
        ("rotation_interval_days", "key_custody", "key rotation interval must be non-empty and positive"),
        ("revocation_path_defined", "key_lifecycle", "revocation distribution and enforcement path must be defined"),
        ("collector_registered", "collector_identity", "collector must be registered to the operator trust domain"),
        ("collector_software_identity_bound", "collector_identity", "collector software identity must be bound to attestation"),
        ("collector_firmware_identity_bound", "collector_identity", "hardware or firmware identity must be bound when used"),
        ("topology_binding_defined", "collector_identity", "collector identity must bind to topology or deployment target"),
        ("manifest_digest_binding", "telemetry_binding", "manifest digest binding from attestation envelope is required"),
        ("payload_digest_set_binding", "telemetry_binding", "payload digest-set binding from attestation envelope is required"),
        ("adapter_conformance_digest_binding", "telemetry_binding", "adapter conformance digest binding is required"),
        ("schema_version_binding", "telemetry_binding", "schema version binding is required"),
        ("bundle_id_registry_defined", "replay_protection", "bundle ID registry must exist"),
        ("nonce_or_monotonic_sequence_defined", "replay_protection", "nonce or monotonic sequence policy must exist"),
        ("tenant_isolation_defined", "tenant_security", "tenant isolation boundary must be declared"),
        ("security_context_source_defined", "tenant_security", "security context source must be declared"),
        ("retention_authorization_defined", "tenant_security", "retention authorization must be declared"),
        ("append_only_audit_log", "auditability", "append-only audit log must capture signing and verification"),
        ("verifier_identity_defined", "auditability", "verifier identity must be recorded"),
        ("incident_response_owner", "auditability", "incident response owner must be named"),
        ("production_limitation", "boundary", "policy admissibility does not grant production calibration or claim credit"),
    ]
    return [
        {
            "field_name": field,
            "policy_dimension": dimension,
            "required": "true",
            "admissibility_rule": rule,
            "production_limitation": "policy fixture only; not production trust evidence",
        }
        for field, dimension, rule in dimensions
    ]


def complete_profile() -> dict[str, object]:
    return {
        "profile_id": "complete-kms-policy-fixture",
        "policy_scope": "operator signing replacement design",
        "evidence_label": "operator_trust_policy_fixture",
        "trust_root_type": "KMS",
        "trust_root_supported": "true",
        "fixture_hmac_presented_as_production_root": "false",
        "key_non_exportable": "true",
        "access_control_defined": "true",
        "rotation_interval_days": "90",
        "revocation_path_defined": "true",
        "collector_registered": "true",
        "collector_software_identity_bound": "true",
        "collector_firmware_identity_bound": "true",
        "topology_binding_defined": "true",
        "manifest_digest_binding": "true",
        "payload_digest_set_binding": "true",
        "adapter_conformance_digest_binding": "true",
        "schema_version_binding": "true",
        "bundle_id_registry_defined": "true",
        "nonce_or_monotonic_sequence_defined": "true",
        "tenant_isolation_defined": "true",
        "security_context_source_defined": "true",
        "retention_authorization_defined": "true",
        "append_only_audit_log": "true",
        "verifier_identity_defined": "true",
        "incident_response_owner": "operator-secops-fixture",
        "mechanically_valid_signature": "true",
        "attempted_attestation_source_trusted": "false",
        "attempted_production_trust_established": "false",
        "expected_blocked_reason": "",
    }


def invalid_profiles(base: dict[str, object]) -> list[dict[str, object]]:
    cases = [
        ("invalid-fixture-hmac-production-root", {"trust_root_type": "fixture_hmac", "fixture_hmac_presented_as_production_root": "true"}, "fixture_hmac_not_production_root"),
        ("invalid-missing-revocation-path", {"revocation_path_defined": "false"}, "missing_revocation_path"),
        ("invalid-exportable-production-key", {"key_non_exportable": "false"}, "exportable_production_key"),
        ("invalid-unbound-collector-identity", {"collector_registered": "false", "collector_software_identity_bound": "false", "collector_firmware_identity_bound": "false"}, "unbound_collector_identity"),
        ("invalid-missing-firmware-identity", {"collector_firmware_identity_bound": "false"}, "unbound_collector_identity"),
        ("invalid-missing-replay-protection", {"bundle_id_registry_defined": "false", "nonce_or_monotonic_sequence_defined": "false"}, "missing_replay_protection"),
        ("invalid-missing-audit-log", {"append_only_audit_log": "false"}, "missing_audit_log"),
        ("invalid-missing-tenant-security-binding", {"tenant_isolation_defined": "false", "security_context_source_defined": "false"}, "missing_tenant_security_binding"),
        ("invalid-unsupported-trust-root", {"trust_root_type": "unsupported_placeholder", "trust_root_supported": "false"}, "unsupported_trust_root"),
        ("invalid-policy-attempts-production-trust", {"attempted_attestation_source_trusted": "true", "attempted_production_trust_established": "true"}, "policy_attempted_production_trust"),
        ("invalid-mechanical-signature-only", {"trust_root_type": "unsupported_placeholder", "trust_root_supported": "false", "mechanically_valid_signature": "true"}, "unsupported_trust_root"),
    ]
    rows = []
    for profile_id, changes, reason in cases:
        row = dict(base)
        row.update(changes)
        row["profile_id"] = profile_id
        row["expected_blocked_reason"] = reason
        rows.append(row)
    return rows


def lifecycle_rows() -> list[dict[str, str]]:
    return [
        {"lifecycle_phase": "provision", "required_control": "root generated inside KMS/HSM or attested hardware root", "pass_condition": "key material non-exportable and operator access control defined", "fail_closed_reason": "exportable_production_key"},
        {"lifecycle_phase": "activate", "required_control": "collector identity, topology, schema, and telemetry digest bindings registered", "pass_condition": "collector identity and telemetry bundle bindings are present", "fail_closed_reason": "unbound_collector_identity"},
        {"lifecycle_phase": "rotate", "required_control": "rotation interval and signer transition policy", "pass_condition": "rotation_interval_days is positive", "fail_closed_reason": "missing_rotation_policy"},
        {"lifecycle_phase": "revoke", "required_control": "revocation publication and verifier enforcement", "pass_condition": "revocation_path_defined=true", "fail_closed_reason": "missing_revocation_path"},
        {"lifecycle_phase": "audit", "required_control": "append-only signing and verification log", "pass_condition": "audit log, verifier identity, and incident owner are defined", "fail_closed_reason": "missing_audit_log"},
    ]


def replacement_map(attest_schema: list[dict[str, str]], custody: list[dict[str, str]], preflight: list[dict[str, str]]) -> list[dict[str, str]]:
    attestation_fields = {row["field_name"] for row in attest_schema}
    custody_ids = {row["requirement_id"] for row in custody}
    preflight_ids = {row["check_id"] for row in preflight}
    rows = [
        ("attestation_type", "hmac_sha256_test_fixture", "operator_kms_or_hsm_signature", "trust_root_type in KMS/HSM/operator_ca/hardware_attestation", "M-ATTEST-1"),
        ("key_id", "test-key-active-a", "operator managed non-exportable key identifier", "key lifecycle controls pass", "M-TRUSTPOL-1"),
        ("signature", "fixture HMAC over canonical fields", "production signature or hardware attestation evidence", "mechanical verification plus admissible trust policy", "M-ATTEST-1"),
        ("collector_id", "intake-fixture-collector-v1", "registered collector identity bound to software/firmware/topology", "collector identity controls pass", "M-PRODDEPLOY-1"),
        ("manifest_digest", "test fixture digest", "digest over production intake manifest", "manifest_sections_complete in custody gate", "M-INTAKE-1"),
        ("payload_digest_set_digest", "test fixture payload digest set", "digest over production payload checksums", "checksums_present in custody gate", "M-INTAKE-1"),
        ("adapter_conformance_digest", "digest over conformance fixture", "digest over accepted adapter conformance report", "adapter conformance accepted before intake", "M-PORT-1"),
        ("bundle_id", "intake-bundle-001", "production bundle ID with replay registry and nonce/sequence", "bundle ID registry and sequence controls pass", "M-TRUSTPOL-1"),
        ("tenant_security_context", "fixture declarations", "tenant isolation and security context source", "tenant/security preflight and retention authorization pass", "M-SECOPS-1"),
        ("production_limitation", "test_attestation_fixture", "production_target evidence only after downstream ingestion gates", "policy admissibility alone grants no calibration", "M-FINALPKG-1"),
    ]
    rows_out = []
    for field, fixture, replacement, gate, dependency in rows:
        input_present = (
            field in attestation_fields
            or field == "attestation_type"
            or field == "tenant_security_context" and bool(preflight_ids)
            or field == "production_limitation" and bool(custody_ids)
        )
        rows_out.append(
        {
            "replacement_field": field,
            "fixture_mechanism": fixture,
            "production_replacement": replacement,
            "required_gate": gate,
            "upstream_dependency": dependency,
            "input_present": str(input_present).lower(),
        }
        )
    return rows_out


def main() -> None:
    attest_schema = read_csv(ATTEST_SCHEMA)
    attest_results = read_csv(ATTEST_RESULTS)
    custody = read_csv(CUSTODY)
    preflight = read_csv(PREFLIGHT)
    if not any(row["signature_valid"] == "true" and row["attestation_source_trusted"] == "false" for row in attest_results):
        raise ValueError("expected mechanically valid but untrusted attestation fixture")
    if not any(row["required_declaration"].startswith("bundle identity") for row in custody):
        raise ValueError("intake custody requirements missing bundle identity declaration")
    if not any(row["blocks_calibration"] == "true" for row in preflight):
        raise ValueError("production preflight checks must block calibration when incomplete")

    complete = complete_profile()
    write_csv(OUT_SCHEMA, schema_rows(), ["field_name", "policy_dimension", "required", "admissibility_rule", "production_limitation"])
    write_csv(OUT_PROFILES, [complete], PROFILE_FIELDS)
    write_csv(OUT_INVALID, invalid_profiles(complete), PROFILE_FIELDS)
    write_csv(OUT_LIFECYCLE, lifecycle_rows(), ["lifecycle_phase", "required_control", "pass_condition", "fail_closed_reason"])
    write_csv(OUT_REPLACEMENT, replacement_map(attest_schema, custody, preflight), ["replacement_field", "fixture_mechanism", "production_replacement", "required_gate", "upstream_dependency", "input_present"])


if __name__ == "__main__":
    main()
