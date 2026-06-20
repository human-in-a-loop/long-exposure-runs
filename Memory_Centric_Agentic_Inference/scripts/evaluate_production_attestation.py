#!/usr/bin/env python3
# created: 2026-05-12T07:05:00Z
# cycle: 28
# run_id: run-2026-05-11T121649Z
# agent: worker
# milestone: M-ATTEST-1
"""Evaluate test-only attestation envelopes for intake bundles."""

from __future__ import annotations

import csv
from collections import Counter
import hashlib
import hmac
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

VALID_MANIFEST = DATA / "production_intake_valid_bundle_manifest.csv"
KEYS = DATA / "production_attestation_key_registry.csv"
SCHEMA = DATA / "production_attestation_envelope_schema.csv"
VALID = DATA / "production_attestation_valid_envelopes.csv"
INVALID = DATA / "production_attestation_invalid_envelopes.csv"
REPLAY = DATA / "production_attestation_replay_registry.csv"
INTAKE_RESULTS = DATA / "production_intake_admission_results.csv"

OUT_RESULTS = DATA / "production_attestation_results.csv"
OUT_FAILURES = DATA / "production_attestation_failure_modes.csv"
OUT_BOUNDARY = DATA / "production_attestation_intake_boundary.csv"
OUT_TRACE = DATA / "production_attestation_traceability_links.csv"

EVIDENCE = "test_attestation_fixture"
SCHEMA_VERSION = "production_dc12_v1"
EVALUATION_TIME = "2026-05-12T07:30:00Z"
SECRETS = {
    "test-key-active-a": "test-only-secret-active-a",
    "test-key-expired-a": "test-only-secret-expired-a",
    "test-key-revoked-a": "test-only-secret-revoked-a",
}
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


def canonical(obj: object) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def file_digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def truthy(row: dict[str, str], key: str) -> bool:
    return row.get(key, "").strip().lower() == "true"


def patched_manifest(rows: list[dict[str, str]], envelope: dict[str, str]) -> list[dict[str, str]]:
    patched = []
    for row in rows:
        item = dict(row)
        item["bundle_id"] = envelope["bundle_id"]
        item["operator_id"] = envelope["operator_id"]
        item["collector_identity"] = envelope["collector_id"]
        item["schema_version"] = envelope["schema_version"]
        item["interval_start_ms"] = envelope["collection_window_start"]
        item["interval_end_ms"] = envelope["collection_window_end"]
        patched.append(item)
    return sorted(patched, key=lambda r: r["file_path"])


def manifest_digest(rows: list[dict[str, str]], envelope: dict[str, str]) -> str:
    return sha256_text(canonical(patched_manifest(rows, envelope)))


def payload_digest_set_digest(rows: list[dict[str, str]]) -> str:
    payloads = [
        {
            "file_path": row["file_path"],
            "row_count": row["row_count"],
            "checksum_sha256": row["checksum_sha256"],
            "canonical_schema_target": row["canonical_schema_target"],
        }
        for row in rows
    ]
    return sha256_text(canonical(sorted(payloads, key=lambda r: r["file_path"])))


def adapter_conformance_digest(rows: list[dict[str, str]]) -> str:
    return file_digest(ROOT / rows[0]["adapter_conformance_report_path"])


def signature_input(row: dict[str, str]) -> str:
    return canonical({field: row[field] for field in SIGNED_FIELDS})


def signature_valid(row: dict[str, str]) -> bool:
    secret = SECRETS.get(row["key_id"])
    if not secret or not row.get("signature"):
        return False
    expected = hmac.new(secret.encode("utf-8"), signature_input(row).encode("utf-8"), hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, row["signature"])


def category(reason: str) -> str:
    if reason in {"missing_signature", "signature_verification_failed"}:
        return "signature"
    if reason in {"unknown_key_id", "expired_key", "revoked_key"}:
        return "key"
    if reason in {"mismatched_manifest_digest", "mismatched_payload_digest_set", "mismatched_adapter_conformance_digest"}:
        return "digest"
    if reason in {"operator_identity_mismatch", "collector_identity_mismatch", "schema_version_mismatch"}:
        return "identity"
    if reason == "stale_collection_window":
        return "expiry"
    if reason == "replayed_bundle_id":
        return "replay"
    return "boundary"


def classify(
    row: dict[str, str],
    keys: dict[str, dict[str, str]],
    replayed: set[str],
    manifest_rows: list[dict[str, str]],
    expected_payload_digest: str,
    expected_adapter_digest: str,
) -> str:
    for field in REQUIRED_FIELDS:
        if not row.get(field, ""):
            if field == "signature":
                return "missing_signature"
            return "missing_attestation_field"
    key = keys.get(row["key_id"])
    if not key or key["key_state"] == "unknown":
        return "unknown_key_id"
    if key["key_state"] == "expired" or row["expires_at"] <= EVALUATION_TIME:
        return "expired_key"
    if key["key_state"] == "revoked":
        return "revoked_key"
    if key["operator_id"] and row["operator_id"] != key["operator_id"]:
        return "operator_identity_mismatch"
    if key["collector_id"] and row["collector_id"] != key["collector_id"]:
        return "collector_identity_mismatch"
    if row["schema_version"] != SCHEMA_VERSION:
        return "schema_version_mismatch"
    if row["manifest_digest"] != manifest_digest(manifest_rows, row):
        return "mismatched_manifest_digest"
    if row["payload_digest_set_digest"] != expected_payload_digest:
        return "mismatched_payload_digest_set"
    if row["adapter_conformance_digest"] != expected_adapter_digest:
        return "mismatched_adapter_conformance_digest"
    if row["collection_window_end"] <= row["collection_window_start"]:
        return "stale_collection_window"
    if row["bundle_id"] in replayed:
        return "replayed_bundle_id"
    if not signature_valid(row):
        return "signature_verification_failed"
    if truthy(row, "production_trust_established"):
        return "fixture_attempted_production_trust"
    return ""


def main() -> None:
    manifest_rows = read_csv(VALID_MANIFEST)
    key_rows = read_csv(KEYS)
    schema = read_csv(SCHEMA)
    valid = read_csv(VALID)
    invalid = read_csv(INVALID)
    replay = read_csv(REPLAY)
    intake = read_csv(INTAKE_RESULTS)
    keys = {row["key_id"]: row for row in key_rows if row["key_state"] != "unknown"}
    replayed = {row["bundle_id"] for row in replay if row["previous_admission_status"] == "structurally_admissible"}
    expected_payload_digest = payload_digest_set_digest(manifest_rows)
    expected_adapter_digest = adapter_conformance_digest(manifest_rows)
    valid_intake_status = next(row["admission_status"] for row in intake if row["bundle_id"] == "valid-intake-bundle")

    schema_fields = {row["field_name"] for row in schema if row["required"] == "true"}
    if REQUIRED_FIELDS - schema_fields:
        raise ValueError("attestation schema missing required fields")

    cases = valid + invalid
    results: list[dict[str, object]] = []
    boundary: list[dict[str, object]] = []
    counts: Counter[str] = Counter()

    for row in cases:
        block = classify(row, keys, replayed, manifest_rows, expected_payload_digest, expected_adapter_digest)
        if block:
            counts[category(block)] += 1
        sig_checked = "true" if row.get("signature") else "false"
        sig_valid = signature_valid(row)
        status = "mechanically_valid" if not block else "blocked"
        trusted = "false"
        production_trust = "false"
        results.append(
            {
                "case_id": row["case_id"],
                "bundle_id": row["bundle_id"],
                "attestation_status": status,
                "key_id": row["key_id"],
                "key_state": keys.get(row["key_id"], {"key_state": "unknown"})["key_state"],
                "signature_checked": sig_checked,
                "signature_valid": str(sig_valid).lower(),
                "manifest_digest_bound": str(row["manifest_digest"] == manifest_digest(manifest_rows, row)).lower(),
                "payload_digest_set_bound": str(row["payload_digest_set_digest"] == expected_payload_digest).lower(),
                "adapter_conformance_digest_bound": str(row["adapter_conformance_digest"] == expected_adapter_digest).lower(),
                "operator_identity_valid": str(row["operator_id"] == manifest_rows[0]["operator_id"]).lower(),
                "collector_identity_valid": str(row["collector_id"] == manifest_rows[0]["collector_identity"]).lower(),
                "collection_window_valid": str(row["collection_window_end"] > row["collection_window_start"]).lower(),
                "replay_checked": "true",
                "replay_valid": str(row["bundle_id"] not in replayed).lower(),
                "evidence_label": EVIDENCE,
                "attestation_source_trusted": trusted,
                "production_trust_established": production_trust,
                "production_target_granted": "false",
                "production_calibrated": "false",
                "production_ready": "false",
                "claim_credit_allowed": "false",
                "expected_blocked_reason": row.get("expected_blocked_reason", ""),
                "blocked_reason": block,
            }
        )
        boundary.append(
            {
                "case_id": row["case_id"],
                "bundle_id": row["bundle_id"],
                "attestation_status": status,
                "intake_admission_reference": valid_intake_status,
                "signature_valid": str(sig_valid).lower(),
                "attestation_source_trusted": trusted,
                "production_trust_established": production_trust,
                "production_calibrated": "false",
                "production_ready": "false",
                "claim_credit_allowed": "false",
                "boundary_reason": "test signature validity is executable custody plumbing, not trusted production operator attestation",
            }
        )

    failure_rows = [
        {"failure_category": name, "invalid_envelope_count": counts[name], "fail_closed": "true"}
        for name in ["signature", "key", "digest", "identity", "expiry", "replay", "boundary"]
    ]
    trace_rows = [
        {
            "trace_link_id": "attestation-to-intake-manifest",
            "source_artifact": "data/production_attestation_valid_envelopes.csv",
            "cited_artifact": "data/production_intake_valid_bundle_manifest.csv",
            "downstream_use": "attestation envelope binds manifest identity, collection window, and payload checksums",
        },
        {
            "trace_link_id": "attestation-to-key-registry",
            "source_artifact": "data/production_attestation_results.csv",
            "cited_artifact": "data/production_attestation_key_registry.csv",
            "downstream_use": "key state gates unknown, expired, and revoked fixture keys before intake claim credit",
        },
        {
            "trace_link_id": "attestation-to-intake-boundary",
            "source_artifact": "data/production_attestation_intake_boundary.csv",
            "cited_artifact": "data/production_intake_admission_results.csv",
            "downstream_use": "mechanical signature validity remains upstream of structural admission and production ingestion",
        },
        {
            "trace_link_id": "attestation-to-final-readiness",
            "source_artifact": "data/production_attestation_traceability_links.csv",
            "cited_artifact": "data/final_claim_readiness_matrix.csv",
            "downstream_use": "final readiness remains blocked without trusted production_target telemetry and downstream gates",
        },
    ]

    write_csv(
        OUT_RESULTS,
        results,
        [
            "case_id",
            "bundle_id",
            "attestation_status",
            "key_id",
            "key_state",
            "signature_checked",
            "signature_valid",
            "manifest_digest_bound",
            "payload_digest_set_bound",
            "adapter_conformance_digest_bound",
            "operator_identity_valid",
            "collector_identity_valid",
            "collection_window_valid",
            "replay_checked",
            "replay_valid",
            "evidence_label",
            "attestation_source_trusted",
            "production_trust_established",
            "production_target_granted",
            "production_calibrated",
            "production_ready",
            "claim_credit_allowed",
            "expected_blocked_reason",
            "blocked_reason",
        ],
    )
    write_csv(OUT_FAILURES, failure_rows, ["failure_category", "invalid_envelope_count", "fail_closed"])
    write_csv(
        OUT_BOUNDARY,
        boundary,
        [
            "case_id",
            "bundle_id",
            "attestation_status",
            "intake_admission_reference",
            "signature_valid",
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
