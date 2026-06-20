#!/usr/bin/env python3
# created: 2026-05-12T15:05:00Z
# cycle: 36
# run_id: run-2026-05-11T121649Z
# agent: worker
# milestone: M-PRODREPLAY-1
"""Replay real production-target telemetry bundles through the full evidence chain."""

from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
INPUT_ROOT = DATA / "production_target_bundle"

OUT_RESULTS = DATA / "production_target_replay_results.csv"
OUT_TRACE = DATA / "production_target_replay_gate_trace.csv"
OUT_BOUNDARY = DATA / "production_target_replay_claim_boundary.csv"
OUT_ABSENCE = DATA / "production_target_replay_absence_report.csv"

GATES = [
    ("root_enrollment", "root_enrolled"),
    ("attestation_envelope", "attested"),
    ("trust_policy", "trust_policy_admissible"),
    ("intake_custody", "intake_custody_valid"),
    ("adapter_conformance", "adapter_conformant"),
    ("timebase_integrity", "timebase_valid"),
    ("redaction_integrity", "redaction_admissible"),
    ("evidence_gatechain", "gatechain_passed"),
    ("uncertainty_qualification", "statistically_robust"),
    ("causal_attribution", "causally_admissible"),
    ("dc001_dc002_threshold_replay", "threshold_passed"),
    ("planner_readiness_boundary", "planner_boundary_passed"),
    ("final_handoff_traceability", "handoff_traceable"),
]

NEGATIVE_CONTROL_FILES = [
    ("data/production_dc12_threshold_replay.csv", "fixture_id"),
    ("data/evidence_gatechain_replay_results.csv", "path_id"),
    ("data/uncertainty_valid_fixture.csv", "case_id"),
    ("data/uncertainty_invalid_fixtures.csv", "case_id"),
    ("data/uncertainty_evaluation_results.csv", "case_id"),
    ("data/causal_valid_fixture.csv", "case_id"),
    ("data/causal_invalid_fixtures.csv", "case_id"),
    ("data/causal_attribution_results.csv", "case_id"),
    ("data/production_intake_admission_results.csv", "bundle_id"),
    ("data/production_attestation_results.csv", "case_id"),
    ("data/operator_trust_policy_results.csv", "profile_id"),
    ("data/adapter_conformance_results.csv", "fixture_case_id"),
    ("data/dc12_claim_update_matrix.csv", "claim_id"),
]


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


def truthy(value: object) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes", "pass", "passed"}


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


def first_failed_gate(manifest: dict[str, object]) -> tuple[str, str]:
    if manifest.get("evidence_label") != "production_target":
        return "evidence_label", "non_production_evidence_label"
    for gate_name, field in GATES:
        if not truthy(manifest.get(field, "")):
            return gate_name, f"failed_{gate_name}"
        evidence_path = str(manifest.get(f"{field}_evidence_path", "")).strip()
        if not evidence_path:
            return gate_name, f"missing_{gate_name}_evidence"
        resolved = (ROOT / evidence_path).resolve()
        if ROOT not in resolved.parents and resolved != ROOT:
            return gate_name, f"invalid_{gate_name}_evidence_path"
        if not resolved.exists():
            return gate_name, f"missing_{gate_name}_evidence"
    return "", ""


def replay_manifest(path: Path, manifest: dict[str, object]) -> tuple[dict[str, object], list[dict[str, object]], dict[str, object]]:
    bundle_id = str(manifest.get("bundle_id") or path.parent.name)
    failed_gate, reason = first_failed_gate(manifest)
    candidate = failed_gate == ""
    state = "real_telemetry_claim_support_candidate" if candidate else "real_telemetry_rejected"
    trace = []
    prior_failed = False
    for order, (gate_name, field) in enumerate(GATES, 1):
        passed = not prior_failed and truthy(manifest.get(field, ""))
        if manifest.get("evidence_label") != "production_target":
            passed = False
        if gate_name == failed_gate:
            prior_failed = True
        trace.append(
            {
                "bundle_id": bundle_id,
                "candidate_source": str(path.relative_to(ROOT)),
                "gate_order": order,
                "gate_name": gate_name,
                "gate_passed": str(passed).lower(),
                "blocked_here": str(gate_name == failed_gate).lower(),
                "blocked_reason": reason if gate_name == failed_gate else "",
                "replay_state": state,
            }
        )
    result = {
        "bundle_id": bundle_id,
        "candidate_source": str(path.relative_to(ROOT)),
        "evidence_label": manifest.get("evidence_label", ""),
        "replay_state": state,
        "first_failed_gate": failed_gate,
        "blocked_reason": reason,
        "threshold_replay_attempted": str(candidate).lower(),
        "readiness_update_allowed": str(candidate).lower(),
        "production_calibrated": str(candidate).lower(),
        "production_ready": "false",
        "claim_credit_allowed": str(candidate).lower(),
        "claim_support_candidate": str(candidate).lower(),
    }
    boundary = {
        "bundle_id": bundle_id,
        "evidence_label": manifest.get("evidence_label", ""),
        "replay_state": state,
        "first_failed_gate": failed_gate,
        "boundary_reason": "all_real_production_replay_gates_passed" if candidate else reason,
        "production_calibrated": str(candidate).lower(),
        "production_ready": "false",
        "claim_credit_allowed": str(candidate).lower(),
        "claim_support_candidate": str(candidate).lower(),
        "automatic_architecture_endorsement": "false",
    }
    return result, trace, boundary


def negative_controls() -> list[dict[str, object]]:
    controls: list[dict[str, object]] = []
    seen: set[tuple[str, str]] = set()
    for rel, id_field in NEGATIVE_CONTROL_FILES:
        path = ROOT / rel
        if not path.exists():
            continue
        for row in read_csv(path):
            label = row.get("evidence_label", "")
            if not label or label == "production_target":
                continue
            key = (label, rel)
            if key in seen:
                continue
            seen.add(key)
            controls.append(
                {
                    "bundle_id": f"negative-control-{label}",
                    "candidate_source": rel,
                    "evidence_label": label,
                    "replay_state": "real_telemetry_rejected",
                    "first_failed_gate": "evidence_label",
                    "blocked_reason": "non_production_evidence_label",
                    "threshold_replay_attempted": "false",
                    "readiness_update_allowed": "false",
                    "production_calibrated": "false",
                    "production_ready": "false",
                    "claim_credit_allowed": "false",
                    "claim_support_candidate": "false",
                    "source_id": row.get(id_field, ""),
                }
            )
    return controls


def absence_row(real_count: int, production_count: int) -> dict[str, object]:
    state = "no_real_telemetry_available" if production_count == 0 else "real_telemetry_present"
    return {
        "search_root": str(INPUT_ROOT.relative_to(ROOT)),
        "manifest_count": real_count,
        "production_target_manifest_count": production_count,
        "absence_state": state,
        "blocked_reason": "no_production_target_bundle_found" if production_count == 0 else "",
        "production_calibrated": "false" if production_count == 0 else "",
        "production_ready": "false" if production_count == 0 else "",
        "claim_credit_allowed": "false" if production_count == 0 else "",
    }


def main() -> None:
    manifests = discover_manifests()
    production_manifests = [(path, item) for path, item in manifests if item.get("evidence_label") == "production_target"]
    results: list[dict[str, object]] = []
    traces: list[dict[str, object]] = []
    boundaries: list[dict[str, object]] = []

    for path, manifest in manifests:
        result, trace, boundary = replay_manifest(path, manifest)
        results.append(result)
        traces.extend(trace)
        boundaries.append(boundary)

    if not production_manifests:
        results.append(
            {
                "bundle_id": "no-real-production-target-bundle",
                "candidate_source": str(INPUT_ROOT.relative_to(ROOT)),
                "evidence_label": "",
                "replay_state": "no_real_telemetry_available",
                "first_failed_gate": "input_discovery",
                "blocked_reason": "no_production_target_bundle_found",
                "threshold_replay_attempted": "false",
                "readiness_update_allowed": "false",
                "production_calibrated": "false",
                "production_ready": "false",
                "claim_credit_allowed": "false",
                "claim_support_candidate": "false",
            }
        )
        boundaries.append(
            {
                "bundle_id": "no-real-production-target-bundle",
                "evidence_label": "",
                "replay_state": "no_real_telemetry_available",
                "first_failed_gate": "input_discovery",
                "boundary_reason": "no_production_target_bundle_found",
                "production_calibrated": "false",
                "production_ready": "false",
                "claim_credit_allowed": "false",
                "claim_support_candidate": "false",
                "automatic_architecture_endorsement": "false",
            }
        )

    controls = negative_controls()
    results.extend(controls)
    for control in controls:
        boundaries.append(
            {
                "bundle_id": control["bundle_id"],
                "evidence_label": control["evidence_label"],
                "replay_state": control["replay_state"],
                "first_failed_gate": "evidence_label",
                "boundary_reason": "non_production_evidence_label",
                "production_calibrated": "false",
                "production_ready": "false",
                "claim_credit_allowed": "false",
                "claim_support_candidate": "false",
                "automatic_architecture_endorsement": "false",
            }
        )

    if not traces:
        traces.append(
            {
                "bundle_id": "no-real-production-target-bundle",
                "candidate_source": str(INPUT_ROOT.relative_to(ROOT)),
                "gate_order": 0,
                "gate_name": "input_discovery",
                "gate_passed": "false",
                "blocked_here": "true",
                "blocked_reason": "no_production_target_bundle_found",
                "replay_state": "no_real_telemetry_available",
            }
        )

    write_csv(
        OUT_RESULTS,
        results,
        [
            "bundle_id",
            "candidate_source",
            "evidence_label",
            "replay_state",
            "first_failed_gate",
            "blocked_reason",
            "threshold_replay_attempted",
            "readiness_update_allowed",
            "production_calibrated",
            "production_ready",
            "claim_credit_allowed",
            "claim_support_candidate",
            "source_id",
        ],
    )
    write_csv(
        OUT_TRACE,
        traces,
        ["bundle_id", "candidate_source", "gate_order", "gate_name", "gate_passed", "blocked_here", "blocked_reason", "replay_state"],
    )
    write_csv(
        OUT_BOUNDARY,
        boundaries,
        [
            "bundle_id",
            "evidence_label",
            "replay_state",
            "first_failed_gate",
            "boundary_reason",
            "production_calibrated",
            "production_ready",
            "claim_credit_allowed",
            "claim_support_candidate",
            "automatic_architecture_endorsement",
        ],
    )
    write_csv(
        OUT_ABSENCE,
        [absence_row(len(manifests), len(production_manifests))],
        [
            "search_root",
            "manifest_count",
            "production_target_manifest_count",
            "absence_state",
            "blocked_reason",
            "production_calibrated",
            "production_ready",
            "claim_credit_allowed",
        ],
    )


if __name__ == "__main__":
    main()
