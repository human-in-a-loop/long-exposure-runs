#!/usr/bin/env python3
# created: 2026-05-12T17:05:00Z
# cycle: 38
# run_id: run-2026-05-11T121649Z
# agent: worker
# milestone: M-LIVECOLLECT-1
"""Conservative production-side gate evidence collector scaffold."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
MAPPING = DATA / "live_collector_artifact_mapping.csv"

COMMON_IDS = {
    "bundle_id": "bundle-live-collector-fixture",
    "measurement_run_id": "run-live-collector-fixture",
    "collector_id": "collector-live-collector-fixture",
    "topology_id": "topology-live-collector-fixture",
    "workload_id": "workload-live-collector-fixture",
    "model_version": "model-live-collector-fixture",
    "deployment_root_id": "root-live-collector-fixture",
    "claim_id": "claim-live-collector-fixture",
}
MEASUREMENT_START = "2026-05-12T17:00:00Z"
MEASUREMENT_END = "2026-05-12T17:10:00Z"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        raise ValueError(f"{path.relative_to(ROOT)} is empty")
    return rows


def load_json(path: Path | None) -> dict[str, object]:
    if path is None or not path.exists():
        return {}
    with path.open() as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return data


def write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def resolve(base: Path, value: str | None) -> Path | None:
    if not value:
        return None
    path = Path(value)
    if path.is_absolute():
        return path
    return (base / path).resolve()


def load_config(path: Path | None) -> tuple[dict[str, object], Path]:
    if path is None:
        return {}, ROOT
    return load_json(path), path.parent.resolve()


def config_path(config: dict[str, object], base: Path, key: str) -> Path | None:
    return resolve(base, str(config.get(key, "")).strip() or None)


def writable(path: Path) -> bool:
    try:
        path.mkdir(parents=True, exist_ok=True)
        probe = path / ".collector_write_probe"
        probe.write_text("ok")
        probe.unlink()
        return True
    except OSError:
        return False


def material_digest(path: Path | None) -> str:
    if path is None or not path.exists():
        return ""
    return sha256_file(path)


def read_id(config: dict[str, object], base: Path, key: str, id_field: str) -> str:
    value = load_json(config_path(config, base, key)).get(id_field, "")
    return str(value or COMMON_IDS.get(id_field, ""))


def preflight(config: dict[str, object], base: Path, output_root: Path) -> dict[str, object]:
    mapping = read_csv(MAPPING)
    paths = {key: config_path(config, base, key) for key in [
        "production_root_marker",
        "deployment_root_identity_file",
        "collector_identity_file",
        "operator_trust_policy_file",
        "external_attestation_file",
        "telemetry_counter_source_file",
        "time_source_file",
    ]}
    marker = load_json(paths["production_root_marker"])
    collector = load_json(paths["collector_identity_file"])
    attestation = load_json(paths["external_attestation_file"])
    time_source = load_json(paths["time_source_file"])

    collector_id = str(collector.get("collector_id", ""))
    attestation_producer = str(attestation.get("producer_id", ""))
    self_attested = bool(attestation) and (attestation_producer in {collector_id, "production_evidence_collector"} or attestation.get("generated_by_collector") is True)

    checks = {
        "production_root_marker": bool(marker.get("production_root") is True and marker.get("evidence_label") == "production_root"),
        "deployment_root_identity_file": bool(load_json(paths["deployment_root_identity_file"]).get("deployment_root_id")),
        "collector_identity_file": bool(collector_id),
        "operator_trust_policy_file": bool(load_json(paths["operator_trust_policy_file"]).get("externally_produced") is True),
        "external_attestation_file": bool(attestation.get("external_attestation") is True),
        "telemetry_counter_source_file": bool(load_json(paths["telemetry_counter_source_file"]).get("counter_source_id")),
        "time_source_file": bool(time_source.get("status") == "fresh" and time_source.get("stale") is not True),
        "artifact_output_root": writable(output_root),
        "self_attestation_guard": not self_attested,
    }
    source_checks: dict[str, bool] = {}
    source_missing_classes: set[str] = set()
    for gate in mapping:
        source_input = gate["source_input_field"]
        check_name = f"source_material:{source_input}"
        path = config_path(config, base, source_input)
        present = bool(path and path.exists() and path.is_file())
        source_checks[check_name] = present
        if not present:
            source_missing_classes.add(gate["source_class"])
    checks.update(source_checks)
    missing = [name for name, ok in checks.items() if not ok]
    if not checks["production_root_marker"]:
        state = "not_running_in_production_root"
    elif any(name in missing for name in ["collector_identity_file", "telemetry_counter_source_file", "time_source_file", "artifact_output_root"]):
        state = "collector_capability_missing"
    elif any(name in missing for name in ["deployment_root_identity_file", "operator_trust_policy_file", "external_attestation_file", "self_attestation_guard"]):
        state = "operator_material_missing"
    elif source_missing_classes & {"operator_supplied", "external_attestation"}:
        state = "operator_material_missing"
    elif source_missing_classes & {"collector_observed", "derived_from_prior_gate"}:
        state = "collector_capability_missing"
    else:
        state = "candidate_artifacts_emitted"
    if self_attested:
        state = "operator_material_missing"
    return {
        "preflight_state": state,
        "production_artifact_emission_allowed": state == "candidate_artifacts_emitted",
        "missing_checks": ",".join(missing),
        "self_attestation_detected": self_attested,
        "checks": checks,
        "paths": {key: str(value) if value else "" for key, value in paths.items()},
    }


def identity_fields(config: dict[str, object], base: Path, fixture: bool) -> dict[str, str]:
    if fixture:
        return dict(COMMON_IDS)
    return {
        **COMMON_IDS,
        "collector_id": read_id(config, base, "collector_identity_file", "collector_id"),
        "deployment_root_id": read_id(config, base, "deployment_root_identity_file", "deployment_root_id"),
    }


def source_payload_digest(config: dict[str, object], base: Path, source_input: str, fixture: bool) -> str:
    path = config_path(config, base, source_input)
    digest = material_digest(path)
    if digest:
        return digest
    if not fixture:
        raise FileNotFoundError(f"missing source material for {source_input}")
    return sha256_bytes(f"fixture:{source_input}".encode())


def artifact_payload(
    gate: dict[str, str],
    config: dict[str, object],
    base: Path,
    evidence_label: str,
    previous_digests: list[str],
    fixture: bool,
) -> dict[str, object]:
    ids = identity_fields(config, base, fixture)
    source_input = gate["source_input_field"]
    return {
        "artifact_id": f"{ids['bundle_id']}:{gate['gate_name']}",
        "evidence_label": evidence_label,
        **ids,
        "gate_name": gate["gate_name"],
        "gate_status": "pass",
        "source_system": "production_evidence_collector",
        "producer_id": ids["collector_id"],
        "created_at": now_iso(),
        "valid_from": "2026-05-12T16:55:00Z",
        "valid_until": "2026-05-12T17:20:00Z",
        "payload_digest": source_payload_digest(config, base, source_input, fixture),
        "upstream_artifact_digests": ";".join(previous_digests),
        "identity_bindings": "bundle_id,measurement_run_id,collector_id,topology_id,workload_id,model_version,deployment_root_id,claim_id",
        "measurement_window_start": MEASUREMENT_START,
        "measurement_window_end": MEASUREMENT_END,
        "collection_source_class": gate["source_class"],
        "source_input_field": source_input,
        "source_material_digest": source_payload_digest(config, base, source_input, fixture),
        "claim_credit_allowed": False,
        "production_calibrated": False,
        "production_ready": False,
    }


def emit_artifacts(
    config: dict[str, object],
    base: Path,
    output_root: Path,
    evidence_label: str,
    fixture: bool,
) -> dict[str, object]:
    mapping = sorted(read_csv(MAPPING), key=lambda row: int(row["gate_order"]))
    artifact_dir = output_root / "artifacts"
    manifest: dict[str, object] = {
        **identity_fields(config, base, fixture),
        "evidence_label": evidence_label,
        "measurement_window_start": MEASUREMENT_START,
        "measurement_window_end": MEASUREMENT_END,
        "production_calibrated": False,
        "production_ready": False,
        "threshold_success": False,
        "causal_validity_granted": False,
        "claim_credit_allowed": False,
    }
    previous_digests: list[str] = []
    artifacts: list[str] = []
    for gate in mapping:
        payload = artifact_payload(gate, config, base, evidence_label, previous_digests, fixture)
        path = artifact_dir / gate["artifact_filename"]
        write_json(path, payload)
        digest = sha256_file(path)
        manifest[gate["manifest_boolean_field"]] = "true"
        manifest[gate["manifest_evidence_path_field"]] = str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path)
        manifest[gate["manifest_digest_field"]] = digest
        previous_digests.append(digest)
        artifacts.append(str(path))
    manifest_path = output_root / "manifest.json"
    write_json(manifest_path, manifest)
    return {"manifest_path": str(manifest_path), "artifact_count": len(artifacts), "artifacts": artifacts, "evidence_label": evidence_label}


def write_preflight_report(output_root: Path, report: dict[str, object]) -> None:
    write_json(output_root / "preflight_report.json", report)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=["preflight", "emit-artifacts", "dry-run"])
    parser.add_argument("--config", type=Path)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--evidence-label", default="production_target")
    args = parser.parse_args(argv)

    config, base = load_config(args.config)
    output_root = args.output_root.resolve()

    if args.mode == "dry-run":
        if args.evidence_label == "production_target":
            args.evidence_label = "collector_dry_run_fixture"
        result = emit_artifacts(config, base, output_root, args.evidence_label, fixture=True)
        write_json(output_root / "collector_result.json", {"mode": "dry-run", "collector_state": "candidate_artifacts_emitted", **result})
        print(json.dumps({"mode": "dry-run", "collector_state": "candidate_artifacts_emitted", **result}, sort_keys=True))
        return 0

    report = preflight(config, base, output_root)
    write_preflight_report(output_root, report)

    if args.mode == "preflight":
        print(json.dumps({key: report[key] for key in ["preflight_state", "production_artifact_emission_allowed", "missing_checks", "self_attestation_detected"]}, sort_keys=True))
        return 0 if report["production_artifact_emission_allowed"] else 1

    if args.evidence_label != "production_target":
        print("emit-artifacts requires evidence_label=production_target; use dry-run for fixtures", file=sys.stderr)
        return 2
    if not report["production_artifact_emission_allowed"]:
        print(json.dumps({key: report[key] for key in ["preflight_state", "production_artifact_emission_allowed", "missing_checks", "self_attestation_detected"]}, sort_keys=True), file=sys.stderr)
        return 1
    result = emit_artifacts(config, base, output_root, "production_target", fixture=False)
    write_json(output_root / "collector_result.json", {"mode": "emit-artifacts", "collector_state": "candidate_artifacts_emitted", **result})
    print(json.dumps({"mode": "emit-artifacts", "collector_state": "candidate_artifacts_emitted", **result}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
