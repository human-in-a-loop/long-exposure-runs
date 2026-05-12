#!/usr/bin/env python3
# created: 2026-05-12T08:05:00Z
# cycle: 29
# run_id: run-2026-05-11T121649Z
# agent: worker
# milestone: M-TRUSTPOL-1
"""Evaluate operator trust policy fixtures before production signing replacement."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

SCHEMA = DATA / "operator_trust_policy_schema.csv"
PROFILES = DATA / "operator_trust_policy_profiles.csv"
INVALID = DATA / "operator_trust_policy_invalid_profiles.csv"
LIFECYCLE = DATA / "operator_key_lifecycle_matrix.csv"
REPLACEMENT = DATA / "operator_attestation_replacement_map.csv"
ATTEST_RESULTS = DATA / "production_attestation_results.csv"
INTAKE_CUSTODY = DATA / "production_intake_chain_of_custody_requirements.csv"
PREFLIGHT = DATA / "production_telemetry_preflight_checks.csv"

OUT_RESULTS = DATA / "operator_trust_policy_results.csv"
OUT_FAILURES = DATA / "operator_trust_policy_failure_modes.csv"
OUT_BOUNDARY = DATA / "operator_trust_policy_boundary.csv"
OUT_TRACE = DATA / "operator_trust_policy_traceability_links.csv"

SUPPORTED_ROOTS = {"KMS", "HSM", "hardware_attestation", "operator_ca"}
REQUIRED_TRUE = [
    "trust_root_supported",
    "key_non_exportable",
    "access_control_defined",
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
]
REQUIRED_SCHEMA_FIELDS = {
    "trust_root_type",
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


def truthy(row: dict[str, str], field: str) -> bool:
    return row.get(field, "").strip().lower() == "true"


def category(reason: str) -> str:
    if reason in {"fixture_hmac_not_production_root", "unsupported_trust_root"}:
        return "trust_root"
    if reason in {"missing_revocation_path", "exportable_production_key", "missing_rotation_policy"}:
        return "key_custody"
    if reason == "unbound_collector_identity":
        return "collector_identity"
    if reason == "missing_replay_protection":
        return "replay"
    if reason == "missing_audit_log":
        return "audit"
    if reason == "missing_tenant_security_binding":
        return "tenant_security"
    if reason == "policy_attempted_production_trust":
        return "boundary"
    return "policy_completeness"


def classify(row: dict[str, str]) -> str:
    if row["trust_root_type"] == "fixture_hmac" or truthy(row, "fixture_hmac_presented_as_production_root"):
        return "fixture_hmac_not_production_root"
    if row["trust_root_type"] not in SUPPORTED_ROOTS or not truthy(row, "trust_root_supported"):
        return "unsupported_trust_root"
    if not truthy(row, "key_non_exportable"):
        return "exportable_production_key"
    if not row.get("rotation_interval_days", "").isdigit() or int(row["rotation_interval_days"]) <= 0:
        return "missing_rotation_policy"
    if not truthy(row, "revocation_path_defined"):
        return "missing_revocation_path"
    if not (
        truthy(row, "collector_registered")
        and truthy(row, "collector_software_identity_bound")
        and truthy(row, "collector_firmware_identity_bound")
        and truthy(row, "topology_binding_defined")
    ):
        return "unbound_collector_identity"
    if not all(truthy(row, field) for field in ["manifest_digest_binding", "payload_digest_set_binding", "adapter_conformance_digest_binding", "schema_version_binding"]):
        return "missing_telemetry_binding"
    if not (truthy(row, "bundle_id_registry_defined") and truthy(row, "nonce_or_monotonic_sequence_defined")):
        return "missing_replay_protection"
    if not (truthy(row, "tenant_isolation_defined") and truthy(row, "security_context_source_defined") and truthy(row, "retention_authorization_defined")):
        return "missing_tenant_security_binding"
    if not (truthy(row, "append_only_audit_log") and truthy(row, "verifier_identity_defined") and bool(row.get("incident_response_owner", ""))):
        return "missing_audit_log"
    if truthy(row, "attempted_attestation_source_trusted") or truthy(row, "attempted_production_trust_established"):
        return "policy_attempted_production_trust"
    for field in REQUIRED_TRUE:
        if not truthy(row, field):
            return "missing_policy_dimension"
    return ""


def main() -> None:
    schema = read_csv(SCHEMA)
    profiles = read_csv(PROFILES)
    invalid = read_csv(INVALID)
    lifecycle = read_csv(LIFECYCLE)
    replacement = read_csv(REPLACEMENT)
    attest = read_csv(ATTEST_RESULTS)
    custody = read_csv(INTAKE_CUSTODY)
    preflight = read_csv(PREFLIGHT)

    schema_fields = {row["field_name"] for row in schema if row["required"] == "true"}
    if REQUIRED_SCHEMA_FIELDS - schema_fields:
        raise ValueError(f"operator trust policy schema missing {sorted(REQUIRED_SCHEMA_FIELDS - schema_fields)}")
    if not any(row["signature_valid"] == "true" and row["attestation_source_trusted"] == "false" for row in attest):
        raise ValueError("expected M-ATTEST-1 mechanical-validity boundary")
    if not lifecycle or not replacement or not custody or not preflight:
        raise ValueError("required upstream policy inputs are missing")

    rows = profiles + invalid
    results: list[dict[str, object]] = []
    boundary: list[dict[str, object]] = []
    counts: Counter[str] = Counter()

    for row in rows:
        reason = classify(row)
        admissible = reason == ""
        if reason:
            counts[category(reason)] += 1
        results.append(
            {
                "profile_id": row["profile_id"],
                "trust_root_type": row["trust_root_type"],
                "mechanically_valid_signature": row["mechanically_valid_signature"],
                "trust_policy_admissible": str(admissible).lower(),
                "attestation_source_trusted": "false",
                "production_trust_established": "false",
                "production_target_granted": "false",
                "production_calibrated": "false",
                "production_ready": "false",
                "claim_credit_allowed": "false",
                "key_lifecycle_valid": str(truthy(row, "key_non_exportable") and truthy(row, "revocation_path_defined") and row["rotation_interval_days"].isdigit()).lower(),
                "collector_identity_bound": str(
                    truthy(row, "collector_registered")
                    and truthy(row, "collector_software_identity_bound")
                    and truthy(row, "collector_firmware_identity_bound")
                    and truthy(row, "topology_binding_defined")
                ).lower(),
                "telemetry_binding_defined": str(all(truthy(row, field) for field in ["manifest_digest_binding", "payload_digest_set_binding", "adapter_conformance_digest_binding", "schema_version_binding"])).lower(),
                "replay_protection_defined": str(truthy(row, "bundle_id_registry_defined") and truthy(row, "nonce_or_monotonic_sequence_defined")).lower(),
                "tenant_security_binding_defined": str(truthy(row, "tenant_isolation_defined") and truthy(row, "security_context_source_defined") and truthy(row, "retention_authorization_defined")).lower(),
                "auditability_defined": str(truthy(row, "append_only_audit_log") and truthy(row, "verifier_identity_defined") and bool(row.get("incident_response_owner", ""))).lower(),
                "evidence_label": row["evidence_label"],
                "expected_blocked_reason": row.get("expected_blocked_reason", ""),
                "blocked_reason": reason,
            }
        )
        boundary.append(
            {
                "profile_id": row["profile_id"],
                "mechanically_valid_signature": row["mechanically_valid_signature"],
                "trust_policy_admissible": str(admissible).lower(),
                "attestation_source_trusted": "false",
                "production_trust_established": "false",
                "production_calibrated": "false",
                "production_ready": "false",
                "claim_credit_allowed": "false",
                "boundary_reason": "policy admissibility is necessary for future production trust but insufficient without real deployment root, collector evidence, accepted production bundle, and downstream ingestion gates",
            }
        )

    failure_rows = [
        {"failure_category": name, "invalid_profile_count": counts[name], "fail_closed": "true"}
        for name in ["trust_root", "key_custody", "collector_identity", "replay", "audit", "tenant_security", "boundary", "policy_completeness"]
    ]
    trace_rows = [
        {
            "trace_link_id": "trust-policy-to-attestation-envelope",
            "source_artifact": "data/operator_attestation_replacement_map.csv",
            "cited_artifact": "data/production_attestation_results.csv",
            "downstream_use": "mechanical test signatures remain insufficient until a real trust policy and real deployment evidence exist",
        },
        {
            "trace_link_id": "trust-policy-to-intake-custody",
            "source_artifact": "data/operator_trust_policy_results.csv",
            "cited_artifact": "data/production_intake_chain_of_custody_requirements.csv",
            "downstream_use": "policy requirements compose with manifest, checksum, schema, join, noise, provenance, and security custody gates",
        },
        {
            "trace_link_id": "trust-policy-to-deployment-preflight",
            "source_artifact": "data/operator_trust_policy_boundary.csv",
            "cited_artifact": "data/production_telemetry_preflight_checks.csv",
            "downstream_use": "admissible policy profiles still cannot bypass production telemetry preflight and calibration gates",
        },
        {
            "trace_link_id": "trust-policy-to-final-readiness",
            "source_artifact": "data/operator_trust_policy_traceability_links.csv",
            "cited_artifact": "data/final_claim_readiness_matrix.csv",
            "downstream_use": "final claim readiness remains blocked without production_target evidence and downstream security/noise/threshold validation",
        },
    ]

    write_csv(
        OUT_RESULTS,
        results,
        [
            "profile_id",
            "trust_root_type",
            "mechanically_valid_signature",
            "trust_policy_admissible",
            "attestation_source_trusted",
            "production_trust_established",
            "production_target_granted",
            "production_calibrated",
            "production_ready",
            "claim_credit_allowed",
            "key_lifecycle_valid",
            "collector_identity_bound",
            "telemetry_binding_defined",
            "replay_protection_defined",
            "tenant_security_binding_defined",
            "auditability_defined",
            "evidence_label",
            "expected_blocked_reason",
            "blocked_reason",
        ],
    )
    write_csv(OUT_FAILURES, failure_rows, ["failure_category", "invalid_profile_count", "fail_closed"])
    write_csv(
        OUT_BOUNDARY,
        boundary,
        [
            "profile_id",
            "mechanically_valid_signature",
            "trust_policy_admissible",
            "attestation_source_trusted",
            "production_trust_established",
            "production_calibrated",
            "production_ready",
            "claim_credit_allowed",
            "boundary_reason",
        ],
    )
    write_csv(OUT_TRACE, trace_rows, ["trace_link_id", "source_artifact", "cited_artifact", "downstream_use"])


if __name__ == "__main__":
    main()
