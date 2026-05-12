#!/usr/bin/env python3
# created: 2026-05-12T07:00:00Z
# cycle: 28
# run_id: run-2026-05-11T121649Z
# agent: worker
# milestone: M-ATTEST-1
"""Build test-only attestation envelopes for production intake bundles."""

from __future__ import annotations

import csv
import hashlib
import hmac
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

VALID_MANIFEST = DATA / "production_intake_valid_bundle_manifest.csv"
INVALID_MANIFEST = DATA / "production_intake_invalid_bundle_manifests.csv"
CUSTODY = DATA / "production_intake_chain_of_custody_requirements.csv"

OUT_KEYS = DATA / "production_attestation_key_registry.csv"
OUT_SCHEMA = DATA / "production_attestation_envelope_schema.csv"
OUT_VALID = DATA / "production_attestation_valid_envelopes.csv"
OUT_INVALID = DATA / "production_attestation_invalid_envelopes.csv"
OUT_REPLAY = DATA / "production_attestation_replay_registry.csv"

EVIDENCE = "test_attestation_fixture"
SCHEMA_VERSION = "production_dc12_v1"
ACTIVE_KEY = "test-key-active-a"
EXPIRED_KEY = "test-key-expired-a"
REVOKED_KEY = "test-key-revoked-a"
UNKNOWN_KEY = "test-key-unknown-a"
SECRETS = {
    ACTIVE_KEY: "test-only-secret-active-a",
    EXPIRED_KEY: "test-only-secret-expired-a",
    REVOKED_KEY: "test-only-secret-revoked-a",
}
ENVELOPE_FIELDS = [
    "case_id",
    "key_id",
    "attestation_type",
    "evidence_label",
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
    "signature_algorithm",
    "signature_input_version",
    "signature",
    "attestation_source_trusted",
    "production_trust_established",
    "expected_blocked_reason",
]
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
    report_path = ROOT / rows[0]["adapter_conformance_report_path"]
    return file_digest(report_path)


def signature_input(row: dict[str, str]) -> str:
    return canonical({field: row[field] for field in SIGNED_FIELDS})


def sign(row: dict[str, str], key_id: str | None = None) -> str:
    secret = SECRETS[key_id or row["key_id"]]
    return hmac.new(secret.encode("utf-8"), signature_input(row).encode("utf-8"), hashlib.sha256).hexdigest()


def schema_rows() -> list[dict[str, str]]:
    expectations = {
        "key_id": "registry key identifier; unknown IDs fail closed",
        "operator_id": "operator identity bound to the intake manifest",
        "collector_id": "collector identity bound to the intake manifest",
        "schema_version": f"must equal {SCHEMA_VERSION}",
        "bundle_id": "bundle ID bound into signature input and replay registry",
        "manifest_digest": "sha256 over canonicalized manifest rows",
        "payload_digest_set_digest": "sha256 over manifest payload path/count/checksum/target set",
        "adapter_conformance_digest": "sha256 over adapter conformance report",
        "collection_window_start": "signed collection interval start",
        "collection_window_end": "signed collection interval end",
        "issued_at": "test signature issue timestamp",
        "expires_at": "test signature expiry timestamp",
        "signature": "HMAC-SHA256 over signed envelope fields",
    }
    rows = []
    for field in ENVELOPE_FIELDS:
        rows.append(
            {
                "field_name": field,
                "required": "true" if field not in {"expected_blocked_reason"} else "false",
                "binding": expectations.get(field, "fixture metadata or boundary label"),
                "fixture_scope": "test_attestation_fixture",
            }
        )
    return rows


def key_registry() -> list[dict[str, str]]:
    return [
        {
            "key_id": ACTIVE_KEY,
            "key_label": "fixture active operator signing key",
            "key_state": "active",
            "operator_id": "operator-fixture-a",
            "collector_id": "intake-fixture-collector-v1",
            "valid_from": "2026-05-12T00:00:00Z",
            "expires_at": "2026-05-13T00:00:00Z",
            "attestation_source_trusted": "false",
            "key_material_label": "test-only shared secret in fixture builder",
        },
        {
            "key_id": EXPIRED_KEY,
            "key_label": "fixture expired operator signing key",
            "key_state": "expired",
            "operator_id": "operator-fixture-a",
            "collector_id": "intake-fixture-collector-v1",
            "valid_from": "2026-05-10T00:00:00Z",
            "expires_at": "2026-05-11T00:00:00Z",
            "attestation_source_trusted": "false",
            "key_material_label": "test-only shared secret in fixture builder",
        },
        {
            "key_id": REVOKED_KEY,
            "key_label": "fixture revoked operator signing key",
            "key_state": "revoked",
            "operator_id": "operator-fixture-a",
            "collector_id": "intake-fixture-collector-v1",
            "valid_from": "2026-05-12T00:00:00Z",
            "expires_at": "2026-05-13T00:00:00Z",
            "attestation_source_trusted": "false",
            "key_material_label": "test-only shared secret in fixture builder",
        },
        {
            "key_id": UNKNOWN_KEY,
            "key_label": "fixture unknown key marker, intentionally absent from signing secrets",
            "key_state": "unknown",
            "operator_id": "",
            "collector_id": "",
            "valid_from": "",
            "expires_at": "",
            "attestation_source_trusted": "false",
            "key_material_label": "no key material registered",
        },
    ]


def base_envelope(rows: list[dict[str, str]]) -> dict[str, str]:
    first = rows[0]
    row = {
        "case_id": "valid-test-attestation",
        "key_id": ACTIVE_KEY,
        "attestation_type": "hmac_sha256_test_fixture",
        "evidence_label": EVIDENCE,
        "operator_id": first["operator_id"],
        "collector_id": first["collector_identity"],
        "schema_version": first["schema_version"],
        "bundle_id": first["bundle_id"],
        "manifest_digest": "",
        "payload_digest_set_digest": payload_digest_set_digest(rows),
        "adapter_conformance_digest": adapter_conformance_digest(rows),
        "collection_window_start": first["interval_start_ms"],
        "collection_window_end": first["interval_end_ms"],
        "issued_at": "2026-05-12T07:00:00Z",
        "expires_at": "2026-05-13T07:00:00Z",
        "signature_algorithm": "HMAC-SHA256",
        "signature_input_version": "attestation-envelope-v1",
        "signature": "",
        "attestation_source_trusted": "false",
        "production_trust_established": "false",
        "expected_blocked_reason": "",
    }
    row["manifest_digest"] = manifest_digest(rows, row)
    row["signature"] = sign(row)
    return row


def signed_case(rows: list[dict[str, str]], patch: dict[str, str], expected: str) -> dict[str, str]:
    row = base_envelope(rows)
    row.update(patch)
    row["case_id"] = patch.get("case_id", row["case_id"])
    row["expected_blocked_reason"] = expected
    if patch.get("recompute_manifest_digest") == "true":
        row["manifest_digest"] = manifest_digest(rows, row)
    if row["key_id"] in SECRETS:
        row["signature"] = sign(row)
    else:
        row["signature"] = "0" * 64
    return row


def invalid_envelopes(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    base = base_envelope(rows)
    tampered_manifest = dict(base)
    tampered_manifest["manifest_digest"] = "1" * 64
    tampered_manifest["signature"] = sign(tampered_manifest)
    tampered_manifest["case_id"] = "invalid-mismatched-manifest-digest"
    tampered_manifest["expected_blocked_reason"] = "mismatched_manifest_digest"

    tampered_payload = dict(base)
    tampered_payload["payload_digest_set_digest"] = "2" * 64
    tampered_payload["signature"] = sign(tampered_payload)
    tampered_payload["case_id"] = "invalid-mismatched-payload-digest-set"
    tampered_payload["expected_blocked_reason"] = "mismatched_payload_digest_set"

    cases = [
        {**base, "case_id": "invalid-missing-signature", "signature": "", "expected_blocked_reason": "missing_signature"},
        signed_case(rows, {"case_id": "invalid-unknown-key", "key_id": UNKNOWN_KEY}, "unknown_key_id"),
        signed_case(rows, {"case_id": "invalid-expired-key", "key_id": EXPIRED_KEY, "expires_at": "2026-05-11T07:00:00Z"}, "expired_key"),
        signed_case(rows, {"case_id": "invalid-revoked-key", "key_id": REVOKED_KEY}, "revoked_key"),
        signed_case(rows, {"case_id": "invalid-wrong-operator", "operator_id": "operator-fixture-b", "recompute_manifest_digest": "true"}, "operator_identity_mismatch"),
        signed_case(rows, {"case_id": "invalid-wrong-collector", "collector_id": "intake-fixture-collector-v2", "recompute_manifest_digest": "true"}, "collector_identity_mismatch"),
        tampered_manifest,
        tampered_payload,
        signed_case(rows, {"case_id": "invalid-stale-collection-window", "collection_window_start": "2000", "collection_window_end": "1000", "recompute_manifest_digest": "true"}, "stale_collection_window"),
        signed_case(rows, {"case_id": "invalid-replayed-bundle-id", "bundle_id": "replayed-intake-bundle-001", "recompute_manifest_digest": "true"}, "replayed_bundle_id"),
        signed_case(rows, {"case_id": "invalid-fixture-production-trust", "production_trust_established": "true"}, "fixture_attempted_production_trust"),
    ]
    return cases


def replay_registry() -> list[dict[str, str]]:
    return [
        {
            "bundle_id": "replayed-intake-bundle-001",
            "previous_admission_status": "structurally_admissible",
            "first_seen_at": "2026-05-12T06:55:00Z",
            "replay_action": "block_reuse_of_bundle_id",
        }
    ]


def main() -> None:
    valid = read_csv(VALID_MANIFEST)
    read_csv(INVALID_MANIFEST)
    read_csv(CUSTODY)
    valid_envelope = base_envelope(valid)
    write_csv(OUT_KEYS, key_registry(), ["key_id", "key_label", "key_state", "operator_id", "collector_id", "valid_from", "expires_at", "attestation_source_trusted", "key_material_label"])
    write_csv(OUT_SCHEMA, schema_rows(), ["field_name", "required", "binding", "fixture_scope"])
    write_csv(OUT_VALID, [valid_envelope], ENVELOPE_FIELDS)
    write_csv(OUT_INVALID, invalid_envelopes(valid), ENVELOPE_FIELDS)
    write_csv(OUT_REPLAY, replay_registry(), ["bundle_id", "previous_admission_status", "first_seen_at", "replay_action"])


if __name__ == "__main__":
    main()
