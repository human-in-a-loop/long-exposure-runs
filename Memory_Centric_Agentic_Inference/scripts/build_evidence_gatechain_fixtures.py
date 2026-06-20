#!/usr/bin/env python3
# created: 2026-05-12T09:05:00Z
# cycle: 30
# run_id: run-2026-05-11T121649Z
# agent: worker
# milestone: M-GATECHAIN-1
"""Build fixture paths for end-to-end production evidence gatechain replay."""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

INPUTS = {
    "trust": DATA / "operator_trust_policy_results.csv",
    "attest": DATA / "production_attestation_results.csv",
    "intake": DATA / "production_intake_admission_results.csv",
    "conformance": DATA / "adapter_conformance_results.csv",
    "adapter": DATA / "telemetry_adapter_normalized_rows.csv",
    "ingestion": DATA / "production_dc12_ingestion_results.csv",
    "threshold": DATA / "production_dc12_threshold_replay.csv",
    "readiness": DATA / "final_claim_readiness_matrix.csv",
    "handoff": DATA / "handoff_claim_traceability.csv",
}

OUT_SCHEMA = DATA / "evidence_gatechain_state_schema.csv"
OUT_RULES = DATA / "evidence_gatechain_transition_rules.csv"
OUT_VALID = DATA / "evidence_gatechain_valid_fixture_paths.csv"
OUT_INVALID = DATA / "evidence_gatechain_invalid_fixture_paths.csv"

REQUIRED_STATES = [
    "raw_bundle_seen",
    "attestation_mechanically_valid",
    "trust_policy_admissible",
    "intake_structurally_admissible",
    "adapter_conformant",
    "adapter_normalized",
    "production_ingestion_accepted",
    "security_provenance_passed",
    "noise_floor_passed",
    "threshold_replay_passed",
    "planner_update_eligible",
    "final_readiness_update_eligible",
    "handoff_traceable",
    "production_claim_credit_allowed",
]

CANONICAL = {
    "bundle_id": "gatechain-bundle-001",
    "measurement_run_id": "gatechain-run-001",
    "operator_id": "operator-secops-fixture",
    "collector_id": "collector-fixture-001",
    "schema_version": "production_dc12_schema_v1",
    "claim_id": "CL-012",
}

STATE_TO_SOURCE = {
    "attestation_mechanically_valid": "data/production_attestation_results.csv",
    "trust_policy_admissible": "data/operator_trust_policy_results.csv",
    "intake_structurally_admissible": "data/production_intake_admission_results.csv",
    "adapter_conformant": "data/adapter_conformance_results.csv",
    "adapter_normalized": "data/telemetry_adapter_normalized_rows.csv",
    "production_ingestion_accepted": "data/production_dc12_ingestion_results.csv",
    "security_provenance_passed": "data/production_dc12_ingestion_results.csv",
    "noise_floor_passed": "data/production_dc12_ingestion_results.csv",
    "threshold_replay_passed": "data/production_dc12_threshold_replay.csv",
    "planner_update_eligible": "data/final_claim_readiness_matrix.csv",
    "final_readiness_update_eligible": "data/final_claim_readiness_matrix.csv",
    "handoff_traceable": "data/handoff_claim_traceability.csv",
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


def first(rows: list[dict[str, str]], predicate, label: str) -> dict[str, str]:
    for row in rows:
        if predicate(row):
            return row
    raise ValueError(f"missing upstream fixture row: {label}")


def state_schema() -> list[dict[str, object]]:
    descriptions = {
        "raw_bundle_seen": "A candidate telemetry bundle exists and has a stable path identity.",
        "attestation_mechanically_valid": "Test or production envelope signature and digest bindings mechanically verify.",
        "trust_policy_admissible": "Operator trust policy is complete enough to be admissible.",
        "intake_structurally_admissible": "Bundle manifest passes structural intake custody checks.",
        "adapter_conformant": "Collector/backend profile passes portability conformance.",
        "adapter_normalized": "Adapter-shaped telemetry has normalized canonical fields.",
        "production_ingestion_accepted": "Production telemetry ingestion accepts the row as eligible evidence.",
        "security_provenance_passed": "Security, provenance, retention, and verifier gates allow credit accounting.",
        "noise_floor_passed": "Measurement exceeds declared noise floor.",
        "threshold_replay_passed": "DC-001/DC-002 threshold replay crosses a configured threshold.",
        "planner_update_eligible": "Planner/runtime update may consider the measurement without granting final claim credit.",
        "final_readiness_update_eligible": "Final readiness matrix may update only after all prior production gates pass.",
        "handoff_traceable": "Claim traceability links evidence, narrative, validation, figures, and limitations.",
        "production_claim_credit_allowed": "Claim credit may be granted only for real production_target evidence after all gates pass.",
    }
    return [
        {
            "state_order": idx + 1,
            "state_id": state,
            "required": "true",
            "description": descriptions[state],
            "source_artifact": STATE_TO_SOURCE.get(state, "future production bundle"),
            "blocks_if_missing": "true",
        }
        for idx, state in enumerate(REQUIRED_STATES)
    ]


def transition_rules() -> list[dict[str, object]]:
    rows = []
    for idx, state in enumerate(REQUIRED_STATES):
        prev = "" if idx == 0 else REQUIRED_STATES[idx - 1]
        rows.append(
            {
                "transition_order": idx + 1,
                "from_state": prev,
                "to_state": state,
                "required_previous_state": prev,
                "required_identifier_continuity": "bundle_id;measurement_run_id;operator_id;collector_id;schema_version" if idx else "",
                "required_evidence_label": "production_target" if state in {"production_ingestion_accepted", "production_claim_credit_allowed"} else "any",
                "dominates_threshold": "true" if state in {"security_provenance_passed", "noise_floor_passed"} else "false",
                "blocked_reason_if_missing": "missing_required_state" if idx else "",
            }
        )
    return rows


def build_path_rows(path_id: str, case_type: str, evidence_label: str, states: list[str], **overrides: str) -> list[dict[str, object]]:
    rows = []
    ids = {**CANONICAL, **overrides}
    for seq, state in enumerate(states, 1):
        state_evidence = overrides.get(f"{state}_evidence_label", evidence_label)
        rows.append(
            {
                "path_id": path_id,
                "case_type": case_type,
                "step_order": seq,
                "state_id": state,
                "bundle_id": ids["bundle_id"],
                "measurement_run_id": ids["measurement_run_id"],
                "operator_id": ids["operator_id"],
                "collector_id": ids["collector_id"],
                "schema_version": ids["schema_version"],
                "claim_id": ids["claim_id"],
                "evidence_label": state_evidence,
                "state_passed": "true",
                "source_artifact": STATE_TO_SOURCE.get(state, "future production bundle"),
                "notes": "current fixture path exercises gate ordering but remains non-production evidence",
            }
        )
    return rows


def invalid_specs() -> list[dict[str, object]]:
    base = REQUIRED_STATES[:-1]
    return [
        {"path_id": "invalid-empty-path", "states": [], "expected_blocked_reason": "empty_path"},
        {"path_id": "invalid-failed-attestation", "states": base, "expected_blocked_reason": "failed_attestation_mechanically_valid", "failed_step": "attestation_mechanically_valid"},
        {"path_id": "invalid-skipped-attestation", "states": [s for s in base if s != "attestation_mechanically_valid"], "expected_blocked_reason": "skipped_attestation"},
        {"path_id": "invalid-skipped-trust-policy", "states": [s for s in base if s != "trust_policy_admissible"], "expected_blocked_reason": "skipped_trust_policy"},
        {"path_id": "invalid-skipped-intake", "states": [s for s in base if s != "intake_structurally_admissible"], "expected_blocked_reason": "skipped_intake"},
        {"path_id": "invalid-skipped-adapter-conformance", "states": [s for s in base if s != "adapter_conformant"], "expected_blocked_reason": "skipped_adapter_conformance"},
        {"path_id": "invalid-out-of-order-threshold", "states": base[:6] + ["threshold_replay_passed"] + base[6:9] + base[10:], "expected_blocked_reason": "out_of_order_state"},
        {"path_id": "invalid-mismatched-bundle-id", "states": base, "expected_blocked_reason": "mismatched_bundle_id", "mismatch_step": "intake_structurally_admissible", "bundle_id": "wrong-bundle"},
        {"path_id": "invalid-mismatched-measurement-run-id", "states": base, "expected_blocked_reason": "mismatched_measurement_run_id", "mismatch_step": "adapter_normalized", "measurement_run_id": "wrong-run"},
        {"path_id": "invalid-mismatched-operator-id", "states": base, "expected_blocked_reason": "mismatched_operator_id", "mismatch_step": "trust_policy_admissible", "operator_id": "wrong-operator"},
        {"path_id": "invalid-mismatched-collector-id", "states": base, "expected_blocked_reason": "mismatched_collector_id", "mismatch_step": "attestation_mechanically_valid", "collector_id": "wrong-collector"},
        {"path_id": "invalid-mismatched-schema-version", "states": base, "expected_blocked_reason": "mismatched_schema_version", "mismatch_step": "production_ingestion_accepted", "schema_version": "wrong-schema"},
        {"path_id": "invalid-fixture-evidence-production-ingestion", "states": base, "expected_blocked_reason": "non_production_evidence_label", "evidence_label": "production_intake_fixture"},
        {"path_id": "invalid-proxy-evidence-threshold-credit", "states": base, "expected_blocked_reason": "proxy_evidence_threshold_credit_blocked", "evidence_label": "host_local_proxy"},
        {"path_id": "invalid-threshold-without-security", "states": [s for s in base if s != "security_provenance_passed"], "expected_blocked_reason": "threshold_without_security_provenance"},
        {"path_id": "invalid-threshold-without-noise-floor", "states": [s for s in base if s != "noise_floor_passed"], "expected_blocked_reason": "threshold_without_noise_floor"},
        {"path_id": "invalid-final-readiness-without-handoff", "states": [s for s in base if s != "handoff_traceable"], "expected_blocked_reason": "final_readiness_without_handoff_traceability"},
    ]


def main() -> None:
    upstream = {name: read_csv(path) for name, path in INPUTS.items()}
    first(upstream["attest"], lambda r: truthy(r, "signature_valid"), "mechanically valid attestation")
    first(upstream["trust"], lambda r: truthy(r, "trust_policy_admissible"), "admissible trust policy")
    first(upstream["intake"], lambda r: r["admission_status"] == "structurally_admissible", "structurally admissible intake")
    first(upstream["conformance"], lambda r: r["status"] == "pass", "adapter conformance pass")
    first(upstream["adapter"], lambda r: r["fixture_class"] == "valid", "normalized adapter row")
    first(upstream["ingestion"], lambda r: truthy(r, "schema_valid") and truthy(r, "join_valid"), "ingestion valid row")
    first(upstream["threshold"], lambda r: truthy(r, "threshold_crossed"), "threshold replay pass")
    first(upstream["readiness"], lambda r: r["claim_id"] == CANONICAL["claim_id"], "final readiness claim")
    first(upstream["handoff"], lambda r: r["claim_id"] == CANONICAL["claim_id"], "handoff traceability claim")

    valid = []
    valid += build_path_rows("valid-current-fixture-quarantined", "valid_fixture_boundary", "operator_trust_policy_fixture", REQUIRED_STATES[:-1])
    valid += build_path_rows("valid-synthetic-production-shaped-quarantined", "valid_fixture_boundary", "synthetic_production_fixture", REQUIRED_STATES[:-1])

    invalid = []
    for spec in invalid_specs():
        states = spec["states"]
        if not states:
            invalid.append(
                {
                    "path_id": spec["path_id"],
                    "case_type": "invalid_path",
                    "step_order": "",
                    "state_id": "",
                    **CANONICAL,
                    "evidence_label": "",
                    "state_passed": "false",
                    "source_artifact": "",
                    "expected_blocked_reason": spec["expected_blocked_reason"],
                    "notes": "empty path must fail before any gate",
                }
            )
            continue
        rows = build_path_rows(spec["path_id"], "invalid_path", spec.get("evidence_label", "production_target"), states)
        mismatch_step = spec.get("mismatch_step")
        if mismatch_step:
            for row in rows:
                if row["state_id"] == mismatch_step:
                    for key in ["bundle_id", "measurement_run_id", "operator_id", "collector_id", "schema_version"]:
                        if key in spec:
                            row[key] = spec[key]
                    row["notes"] = "identifier continuity probe"
        failed_step = spec.get("failed_step")
        if failed_step:
            for row in rows:
                if row["state_id"] == failed_step:
                    row["state_passed"] = "false"
                    row["notes"] = "failed gate probe"
        for row in rows:
            row["expected_blocked_reason"] = spec["expected_blocked_reason"]
        invalid += rows

    common_fields = [
        "path_id",
        "case_type",
        "step_order",
        "state_id",
        "bundle_id",
        "measurement_run_id",
        "operator_id",
        "collector_id",
        "schema_version",
        "claim_id",
        "evidence_label",
        "state_passed",
        "source_artifact",
        "notes",
    ]
    write_csv(OUT_SCHEMA, state_schema(), ["state_order", "state_id", "required", "description", "source_artifact", "blocks_if_missing"])
    write_csv(OUT_RULES, transition_rules(), ["transition_order", "from_state", "to_state", "required_previous_state", "required_identifier_continuity", "required_evidence_label", "dominates_threshold", "blocked_reason_if_missing"])
    write_csv(OUT_VALID, valid, common_fields)
    write_csv(OUT_INVALID, invalid, common_fields + ["expected_blocked_reason"])


if __name__ == "__main__":
    main()
