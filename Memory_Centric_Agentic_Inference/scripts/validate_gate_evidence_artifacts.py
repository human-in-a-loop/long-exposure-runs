#!/usr/bin/env python3
# created: 2026-05-12T16:05:00Z
# cycle: 37
# run_id: run-2026-05-11T121649Z
# agent: worker
# milestone: M-EVIDART-1
"""Validate gate evidence artifact structure before production-target replay."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
INPUT_ROOT = DATA / "production_target_bundle"
SCHEMA = DATA / "gate_evidence_artifact_schema.csv"

OUT_RESULTS = DATA / "gate_evidence_artifact_validation_results.csv"
OUT_FAILURES = DATA / "gate_evidence_failure_modes.csv"
OUT_BOUNDARY = DATA / "gate_evidence_replay_readiness_boundary.csv"

COMMON_IDS = ["bundle_id", "measurement_run_id", "collector_id", "topology_id", "workload_id", "model_version", "deployment_root_id", "claim_id"]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})
    print(f"wrote {path.relative_to(ROOT)} rows={len(rows)}")


def parse_time(value: str) -> datetime | None:
    if not value:
        return None
    text = value.replace("Z", "+00:00")
    try:
        dt = datetime.fromisoformat(text)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def truthy(value: object) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes", "pass", "passed", "admissible"}


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_manifest(path: Path) -> dict[str, object]:
    if path.suffix == ".json":
        with path.open() as f:
            data = json.load(f)
        if not isinstance(data, dict):
            raise ValueError(f"{path} must contain a JSON object")
        return data
    with path.open(newline="") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        raise ValueError(f"{path} is empty")
    return dict(rows[0])


def discover_manifests() -> list[tuple[Path, dict[str, object]]]:
    if not INPUT_ROOT.exists():
        return []
    paths = sorted(INPUT_ROOT.rglob("manifest.json")) + sorted(INPUT_ROOT.rglob("manifest.csv"))
    return [(path, load_manifest(path)) for path in paths]


def load_schema() -> list[dict[str, str]]:
    rows = read_csv(SCHEMA)
    if not rows:
        raise ValueError("gate evidence schema has no rows")
    return sorted(rows, key=lambda row: int(row["order"]))


def evidence_for_path(path_text: str, virtual: dict[str, dict[str, object]]) -> tuple[dict[str, object] | None, str, Path | None]:
    if path_text in virtual:
        return virtual[path_text], hashlib.sha256(json.dumps(virtual[path_text], sort_keys=True).encode()).hexdigest(), None
    path = (ROOT / path_text).resolve()
    if ROOT not in path.parents and path != ROOT:
        return None, "", None
    if not path.exists():
        return None, "", path
    try:
        with path.open() as f:
            payload = json.load(f)
        if not isinstance(payload, dict):
            return None, sha256_path(path), path
        return payload, sha256_path(path), path
    except (OSError, json.JSONDecodeError):
        return None, sha256_path(path), path


def validate_manifest(
    manifest_path: str,
    manifest: dict[str, object],
    schema: list[dict[str, str]],
    virtual: dict[str, dict[str, object]] | None = None,
) -> tuple[list[dict[str, object]], dict[str, object]]:
    virtual = virtual or {}
    bundle_id = str(manifest.get("bundle_id", Path(manifest_path).parent.name))
    measurement_start = parse_time(str(manifest.get("measurement_window_start", "")))
    measurement_end = parse_time(str(manifest.get("measurement_window_end", "")))
    upstream_passed: dict[str, str] = {}
    rows: list[dict[str, object]] = []
    first_failure = ""
    first_gate = ""

    for gate in schema:
        gate_name = gate["gate_name"]
        bool_field = gate["manifest_boolean_field"]
        path_field = gate["evidence_path_field"]
        digest_field = gate["digest_field"]
        path_text = str(manifest.get(path_field, "")).strip()
        gate_declared = truthy(manifest.get(bool_field, ""))
        evidence_payload = None
        actual_digest = ""
        passed = True
        reason = ""

        if str(manifest.get("evidence_label", "")) != "production_target":
            passed = False
            reason = "non_production_evidence_label"
        elif not gate_declared:
            passed = False
            reason = "manifest_gate_boolean_not_true"
        elif not path_text:
            passed = False
            reason = "missing_evidence_path"
        else:
            evidence_payload, actual_digest, _ = evidence_for_path(path_text, virtual)
            if evidence_payload is None:
                passed = False
                reason = "nonexistent_evidence_file"
            elif str(manifest.get(digest_field, "")) != actual_digest:
                passed = False
                reason = "digest_mismatch"

        if passed and evidence_payload is not None:
            required_fields = [field.strip() for field in gate["required_payload_fields"].split(",") if field.strip()]
            optional_empty_fields = {"upstream_artifact_digests"}
            missing_fields = [
                field
                for field in required_fields
                if field not in evidence_payload
                or (field not in optional_empty_fields and str(evidence_payload.get(field, "")).strip() == "")
            ]
            if missing_fields:
                passed = False
                reason = "missing_required_payload_field"
            elif evidence_payload.get("evidence_label") != "production_target":
                passed = False
                reason = "non_production_evidence_label"
            elif evidence_payload.get("gate_name") != gate_name:
                passed = False
                reason = "gate_order_mismatch"
            elif evidence_payload.get("gate_status") not in {"pass", "passed", "admissible", True}:
                passed = False
                reason = "artifact_gate_status_not_pass"
            else:
                for key in COMMON_IDS:
                    if key in manifest and key in evidence_payload and str(manifest[key]) != str(evidence_payload[key]):
                        passed = False
                        if key == "deployment_root_id":
                            reason = "root_identity_mismatch"
                        elif key == "collector_id":
                            reason = "collector_identity_mismatch"
                        elif key in {"topology_id", "workload_id", "model_version"}:
                            reason = "topology_model_workload_mismatch"
                        else:
                            reason = f"{key}_identity_mismatch"
                        break
        if passed and evidence_payload is not None and measurement_start and measurement_end:
            valid_from = parse_time(str(evidence_payload.get("valid_from", "")))
            valid_until = parse_time(str(evidence_payload.get("valid_until", "")))
            if not valid_from or not valid_until or valid_from > measurement_start or valid_until < measurement_end:
                passed = False
                reason = "evidence_window_outside_measurement_window"

        upstream = gate["upstream_dependency"]
        if passed and upstream != "none" and upstream not in upstream_passed:
            passed = False
            reason = "downstream_artifact_without_upstream_dependency"
        if passed and evidence_payload is not None and upstream != "none":
            upstream_digest = upstream_passed[upstream]
            linked = str(evidence_payload.get("upstream_artifact_digests", ""))
            if upstream_digest not in linked:
                passed = False
                reason = "downstream_artifact_without_upstream_dependency"

        if passed:
            upstream_passed[gate_name] = actual_digest
        elif not first_failure:
            first_failure = reason
            first_gate = gate_name

        rows.append(
            {
                "bundle_id": bundle_id,
                "manifest_path": manifest_path,
                "gate_order": gate["order"],
                "gate_name": gate_name,
                "manifest_declares_pass": str(gate_declared).lower(),
                "evidence_path": path_text,
                "artifact_present": str(bool(evidence_payload)).lower(),
                "digest_matches": str(bool(evidence_payload) and str(manifest.get(digest_field, "")) == actual_digest).lower(),
                "identity_matches": str(passed or reason not in {"root_identity_mismatch", "collector_identity_mismatch", "topology_model_workload_mismatch"}).lower(),
                "time_window_valid": str(passed or reason != "evidence_window_outside_measurement_window").lower(),
                "upstream_dependency_satisfied": str(passed or reason != "downstream_artifact_without_upstream_dependency").lower(),
                "artifact_validation_passed": str(passed).lower(),
                "blocked_reason": reason,
            }
        )
        if not passed:
            break

    complete = not first_failure and len(upstream_passed) == len(schema)
    boundary = {
        "bundle_id": bundle_id,
        "manifest_path": manifest_path,
        "evidence_label": manifest.get("evidence_label", ""),
        "evidence_artifact_complete": str(complete).lower(),
        "first_failed_gate": first_gate,
        "blocked_reason": first_failure,
        "ready_for_production_target_replay": str(complete and manifest.get("evidence_label") == "production_target").lower(),
        "production_calibrated": "false",
        "production_ready": "false",
        "threshold_success": "false",
        "causal_validity_granted": "false",
        "claim_credit_allowed": "false",
    }
    return rows, boundary


def artifact(gate: str, previous_digests: list[str], overrides: dict[str, object] | None = None) -> dict[str, object]:
    base: dict[str, object] = {
        "artifact_id": f"artifact-{gate}",
        "evidence_label": "production_target",
        "bundle_id": "fixture-complete-linked-artifacts",
        "measurement_run_id": "run-prod-001",
        "collector_id": "collector-prod-001",
        "topology_id": "topology-prod-001",
        "workload_id": "workload-prod-001",
        "model_version": "model-prod-001",
        "deployment_root_id": "root-prod-001",
        "claim_id": "claim-prod-001",
        "gate_name": gate,
        "gate_status": "pass",
        "source_system": "offline-operator-kit-fixture",
        "producer_id": "operator-fixture",
        "created_at": "2026-05-12T16:00:00Z",
        "valid_from": "2026-05-12T15:00:00Z",
        "valid_until": "2026-05-12T17:00:00Z",
        "payload_digest": f"payload-digest-{gate}",
        "upstream_artifact_digests": ";".join(previous_digests),
        "identity_bindings": "bundle_id,measurement_run_id,collector_id,topology_id,workload_id,model_version,deployment_root_id,claim_id",
        "measurement_window_start": "2026-05-12T15:10:00Z",
        "measurement_window_end": "2026-05-12T15:50:00Z",
    }
    if overrides:
        base.update(overrides)
    return base


def complete_fixture(schema: list[dict[str, str]], defect: str = "") -> tuple[dict[str, object], dict[str, dict[str, object]]]:
    manifest: dict[str, object] = {
        "bundle_id": "fixture-complete-linked-artifacts",
        "evidence_label": "production_target",
        "measurement_run_id": "run-prod-001",
        "collector_id": "collector-prod-001",
        "topology_id": "topology-prod-001",
        "workload_id": "workload-prod-001",
        "model_version": "model-prod-001",
        "deployment_root_id": "root-prod-001",
        "claim_id": "claim-prod-001",
        "measurement_window_start": "2026-05-12T15:10:00Z",
        "measurement_window_end": "2026-05-12T15:50:00Z",
    }
    virtual: dict[str, dict[str, object]] = {}
    previous: list[str] = []
    for gate in schema:
        bool_field = gate["manifest_boolean_field"]
        path_field = gate["evidence_path_field"]
        digest_field = gate["digest_field"]
        path = f"virtual/{gate['gate_name']}.json"
        overrides: dict[str, object] = {}
        if defect == "root_identity_mismatch" and gate["gate_name"] == "root_enrollment":
            overrides["deployment_root_id"] = "root-other"
        if defect == "collector_identity_mismatch" and gate["gate_name"] == "timebase_integrity":
            overrides["collector_id"] = "collector-other"
        if defect == "topology_model_workload_mismatch" and gate["gate_name"] == "causal_attribution":
            overrides["topology_id"] = "topology-other"
        if defect == "evidence_window_outside_measurement_window" and gate["gate_name"] == "timebase_integrity":
            overrides["valid_until"] = "2026-05-12T15:20:00Z"
        payload = artifact(gate["gate_name"], previous, overrides)
        digest = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()
        virtual[path] = payload
        manifest[bool_field] = "true"
        manifest[path_field] = path
        manifest[digest_field] = digest
        if defect == "missing_evidence_path" and gate["gate_name"] == "root_enrollment":
            manifest[path_field] = ""
        if defect == "nonexistent_evidence_file" and gate["gate_name"] == "root_enrollment":
            manifest[path_field] = "virtual/does-not-exist.json"
        if defect == "digest_mismatch" and gate["gate_name"] == "root_enrollment":
            manifest[digest_field] = "0" * 64
        if defect == "manifest_only_gate_boolean" and gate["gate_name"] == "root_enrollment":
            manifest[path_field] = ""
            manifest[digest_field] = ""
        if defect == "missing_required_payload_field" and gate["gate_name"] == "root_enrollment":
            virtual[path].pop("payload_digest", None)
            manifest[digest_field] = hashlib.sha256(json.dumps(virtual[path], sort_keys=True).encode()).hexdigest()
        if defect == "downstream_artifact_without_upstream_dependency" and gate["gate_name"] == "attestation_envelope":
            virtual[path]["upstream_artifact_digests"] = ""
            manifest[digest_field] = hashlib.sha256(json.dumps(virtual[path], sort_keys=True).encode()).hexdigest()
        if defect == "artifact_with_non_production_evidence_label_attempting_promotion":
            manifest["evidence_label"] = "synthetic_production_fixture"
        previous.append(hashlib.sha256(json.dumps(virtual[path], sort_keys=True).encode()).hexdigest())
    return manifest, virtual


def defect_probe_rows(schema: list[dict[str, str]]) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    defects = [
        "manifest_only_gate_boolean",
        "missing_evidence_path",
        "nonexistent_evidence_file",
        "digest_mismatch",
        "missing_required_payload_field",
        "evidence_window_outside_measurement_window",
        "root_identity_mismatch",
        "collector_identity_mismatch",
        "topology_model_workload_mismatch",
        "downstream_artifact_without_upstream_dependency",
        "artifact_with_non_production_evidence_label_attempting_promotion",
        "",
    ]
    rows: list[dict[str, object]] = []
    boundaries: list[dict[str, object]] = []
    for defect in defects:
        manifest, virtual = complete_fixture(schema, defect)
        label = defect or "complete_linked_artifacts"
        manifest["bundle_id"] = f"probe-{label}"
        for payload in virtual.values():
            payload["bundle_id"] = manifest["bundle_id"]
        # Rebuild upstream links and digests after bundle_id override.
        previous: list[str] = []
        for gate in schema:
            path = str(manifest.get(gate["evidence_path_field"], ""))
            if path in virtual:
                if not (defect == "downstream_artifact_without_upstream_dependency" and gate["gate_name"] == "attestation_envelope"):
                    virtual[path]["upstream_artifact_digests"] = ";".join(previous)
                digest = hashlib.sha256(json.dumps(virtual[path], sort_keys=True).encode()).hexdigest()
                if defect != "digest_mismatch":
                    manifest[gate["digest_field"]] = digest
                previous.append(digest)
        result_rows, boundary = validate_manifest(f"defect_probe/{label}/manifest.json", manifest, schema, virtual)
        rows.extend(result_rows)
        boundaries.append(boundary)
    return rows, boundaries


def main() -> None:
    schema = load_schema()
    results: list[dict[str, object]] = []
    boundaries: list[dict[str, object]] = []
    for path, manifest in discover_manifests():
        rows, boundary = validate_manifest(str(path.relative_to(ROOT)), manifest, schema)
        results.extend(rows)
        boundaries.append(boundary)

    probe_results, probe_boundaries = defect_probe_rows(schema)
    results.extend(probe_results)
    boundaries.extend(probe_boundaries)

    counts = Counter(row["blocked_reason"] or "none" for row in results if row["artifact_validation_passed"] == "false")
    failure_rows = [{"failure_mode": key, "count": value} for key, value in sorted(counts.items())]

    write_csv(
        OUT_RESULTS,
        results,
        [
            "bundle_id",
            "manifest_path",
            "gate_order",
            "gate_name",
            "manifest_declares_pass",
            "evidence_path",
            "artifact_present",
            "digest_matches",
            "identity_matches",
            "time_window_valid",
            "upstream_dependency_satisfied",
            "artifact_validation_passed",
            "blocked_reason",
        ],
    )
    write_csv(OUT_FAILURES, failure_rows, ["failure_mode", "count"])
    write_csv(
        OUT_BOUNDARY,
        boundaries,
        [
            "bundle_id",
            "manifest_path",
            "evidence_label",
            "evidence_artifact_complete",
            "first_failed_gate",
            "blocked_reason",
            "ready_for_production_target_replay",
            "production_calibrated",
            "production_ready",
            "threshold_success",
            "causal_validity_granted",
            "claim_credit_allowed",
        ],
    )


if __name__ == "__main__":
    main()
