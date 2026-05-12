#!/usr/bin/env python3
# created: 2026-05-12T16:00:00Z
# cycle: 37
# run_id: run-2026-05-11T121649Z
# agent: worker
# milestone: M-EVIDART-1
"""Build the operator-facing gate evidence artifact contract."""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

OUT_SCHEMA = DATA / "gate_evidence_artifact_schema.csv"
OUT_FIELDS = DATA / "gate_evidence_required_fields.csv"
OUT_GRAPH = DATA / "gate_evidence_dependency_graph.csv"
OUT_CHECKLIST = DATA / "gate_evidence_operator_checklist.csv"

GATES = [
    {
        "order": 1,
        "gate_name": "root_enrollment",
        "manifest_boolean_field": "root_enrolled",
        "payload_source": "deployment-root enrollment record from M-ROOTINT-1",
        "identity_binding": "deployment_root_id, collector_id, firmware_id, topology_id, schema_version, tenant_id, security_context_id",
        "time_window": "enrollment_valid_from/enrollment_valid_until must cover measurement window",
        "upstream_dependency": "none",
        "fail_closed_reason_if_absent": "missing_root_enrollment_evidence",
    },
    {
        "order": 2,
        "gate_name": "attestation_envelope",
        "manifest_boolean_field": "attested",
        "payload_source": "bundle attestation envelope from M-ATTEST-1",
        "identity_binding": "bundle_id, measurement_run_id, collector_id, signer_key_id, manifest_digest",
        "time_window": "signature_valid_from/signature_valid_until must cover manifest and payload capture",
        "upstream_dependency": "root_enrollment",
        "fail_closed_reason_if_absent": "missing_attestation_envelope_evidence",
    },
    {
        "order": 3,
        "gate_name": "trust_policy",
        "manifest_boolean_field": "trust_policy_admissible",
        "payload_source": "operator trust policy evaluation from M-TRUSTPOL-1",
        "identity_binding": "operator_id, deployment_root_id, signer_key_id, hardware_attestation_profile_id",
        "time_window": "policy_valid_from/policy_valid_until must cover attestation and capture",
        "upstream_dependency": "attestation_envelope",
        "fail_closed_reason_if_absent": "missing_trust_policy_evidence",
    },
    {
        "order": 4,
        "gate_name": "intake_custody",
        "manifest_boolean_field": "intake_custody_valid",
        "payload_source": "chain-of-custody admission record from M-INTAKE-1",
        "identity_binding": "bundle_id, measurement_run_id, manifest_digest, payload_digest, operator_id",
        "time_window": "custody_received_at must be inside allowed freshness window",
        "upstream_dependency": "trust_policy",
        "fail_closed_reason_if_absent": "missing_intake_custody_evidence",
    },
    {
        "order": 5,
        "gate_name": "adapter_conformance",
        "manifest_boolean_field": "adapter_conformant",
        "payload_source": "adapter normalization and conformance report from M-PORT-1/M-ADAPTER-1",
        "identity_binding": "adapter_id, schema_version, measurement_run_id, topology_id, workload_id",
        "time_window": "normalized interval bounds must match measurement window",
        "upstream_dependency": "intake_custody",
        "fail_closed_reason_if_absent": "missing_adapter_conformance_evidence",
    },
    {
        "order": 6,
        "gate_name": "timebase_integrity",
        "manifest_boolean_field": "timebase_valid",
        "payload_source": "clock, interval, skew, drift, and observer-overhead report from M-TIMEBASE-1",
        "identity_binding": "collector_id, measurement_run_id, interval_id, clock_domain_id, counter_source_id",
        "time_window": "evidence window must equal or cover measurement interval range",
        "upstream_dependency": "adapter_conformance",
        "fail_closed_reason_if_absent": "missing_timebase_integrity_evidence",
    },
    {
        "order": 7,
        "gate_name": "redaction_integrity",
        "manifest_boolean_field": "redaction_admissible",
        "payload_source": "redaction and replay-identifiability report from M-REDACT-1",
        "identity_binding": "bundle_id, measurement_run_id, tenant_pseudonym_set_id, object_pseudonym_set_id",
        "time_window": "redacted export window must match the validated measurement window",
        "upstream_dependency": "timebase_integrity",
        "fail_closed_reason_if_absent": "missing_redaction_integrity_evidence",
    },
    {
        "order": 8,
        "gate_name": "evidence_gatechain",
        "manifest_boolean_field": "gatechain_passed",
        "payload_source": "ordered promotion-state replay from M-GATECHAIN-1",
        "identity_binding": "bundle_id, measurement_run_id, operator_id, collector_id, schema_version, claim_id",
        "time_window": "gatechain replay timestamp must be after upstream gate evidence and before replay",
        "upstream_dependency": "redaction_integrity",
        "fail_closed_reason_if_absent": "missing_evidence_gatechain_evidence",
    },
    {
        "order": 9,
        "gate_name": "uncertainty_qualification",
        "manifest_boolean_field": "statistically_robust",
        "payload_source": "confidence and threshold qualification report from M-UNCERT-1",
        "identity_binding": "claim_id, measurement_run_id, workload_id, object_id, threshold_id, control_id",
        "time_window": "sample window must match redacted measurement window",
        "upstream_dependency": "evidence_gatechain",
        "fail_closed_reason_if_absent": "missing_uncertainty_qualification_evidence",
    },
    {
        "order": 10,
        "gate_name": "causal_attribution",
        "manifest_boolean_field": "causally_admissible",
        "payload_source": "control-arm and covariate balance report from M-CAUSAL-1",
        "identity_binding": "claim_id, treatment_run_id, control_run_id, workload_id, topology_id, model_version",
        "time_window": "treatment/control windows must be aligned within drift budget",
        "upstream_dependency": "uncertainty_qualification",
        "fail_closed_reason_if_absent": "missing_causal_attribution_evidence",
    },
    {
        "order": 11,
        "gate_name": "dc001_dc002_threshold_replay",
        "manifest_boolean_field": "threshold_passed",
        "payload_source": "DC-001/DC-002 threshold replay output from M-PRODTELEM-1/M-DC12-1",
        "identity_binding": "claim_id, threshold_id, measurement_run_id, workload_id, topology_id",
        "time_window": "threshold replay input window must match causal/uncertainty qualified window",
        "upstream_dependency": "causal_attribution",
        "fail_closed_reason_if_absent": "missing_dc001_dc002_threshold_replay_evidence",
    },
    {
        "order": 12,
        "gate_name": "planner_readiness_boundary",
        "manifest_boolean_field": "planner_boundary_passed",
        "payload_source": "planner/readiness boundary record from M-PLAN-1/M-FINALPKG-1",
        "identity_binding": "claim_id, plan_id, measurement_run_id, option_id, security_context_id",
        "time_window": "planner evaluation must consume the same qualified replay window",
        "upstream_dependency": "dc001_dc002_threshold_replay",
        "fail_closed_reason_if_absent": "missing_planner_readiness_boundary_evidence",
    },
    {
        "order": 13,
        "gate_name": "final_handoff_traceability",
        "manifest_boolean_field": "handoff_traceable",
        "payload_source": "claim-to-evidence traceability record from M-HANDOFF-1",
        "identity_binding": "claim_id, bundle_id, measurement_run_id, artifact_index_id, reproduction_manifest_id",
        "time_window": "handoff record must be generated after all upstream artifacts",
        "upstream_dependency": "planner_readiness_boundary",
        "fail_closed_reason_if_absent": "missing_final_handoff_traceability_evidence",
    },
]


def write_csv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})
    print(f"wrote {path.relative_to(ROOT)} rows={len(rows)}")


def contract_rows() -> list[dict[str, object]]:
    rows = []
    for gate in GATES:
        field = gate["manifest_boolean_field"]
        rows.append(
            {
                **gate,
                "evidence_path_field": f"{field}_evidence_path",
                "digest_field": f"{field}_evidence_sha256",
                "digest_binding": "sha256 over canonical evidence artifact bytes; value must not be copied from artifact payload",
                "required_payload_fields": "artifact_id,evidence_label,bundle_id,measurement_run_id,claim_id,gate_name,gate_status,source_system,producer_id,created_at,valid_from,valid_until,payload_digest,upstream_artifact_digests,identity_bindings,measurement_window_start,measurement_window_end",
            }
        )
    return rows


def required_field_rows() -> list[dict[str, object]]:
    fields = [
        ("artifact_id", "stable evidence artifact identifier", "artifact producer"),
        ("evidence_label", "must be production_target for production replay candidates", "operator source classification"),
        ("bundle_id", "links evidence to manifest bundle", "intake manifest or custody record"),
        ("measurement_run_id", "links all gates to the same measurement run", "collector/intake join key"),
        ("claim_id", "links evidence to a specific architecture claim", "claim registry"),
        ("gate_name", "must equal the expected gate", "validator expected value"),
        ("gate_status", "must be pass/admissible for replay prerequisite", "gate-specific evaluator output"),
        ("source_system", "names producing system or tool", "operator evidence generator"),
        ("producer_id", "person, service, or system identity creating the artifact", "operator custody log"),
        ("created_at", "freshness and order check", "artifact metadata"),
        ("valid_from", "lower evidence validity bound", "artifact metadata or upstream evaluator"),
        ("valid_until", "upper evidence validity bound", "artifact metadata or upstream evaluator"),
        ("payload_digest", "binds raw gate payload or evaluated report", "independently computed digest"),
        ("upstream_artifact_digests", "binds upstream dependency artifacts", "computed from upstream evidence files"),
        ("identity_bindings", "gate-specific IDs that must match manifest and upstream artifacts", "independent gate evidence"),
        ("measurement_window_start", "start of covered measurement interval", "collector/timebase evidence"),
        ("measurement_window_end", "end of covered measurement interval", "collector/timebase evidence"),
    ]
    rows = []
    for gate in GATES:
        for field, purpose, derivation in fields:
            rows.append({"gate_name": gate["gate_name"], "required_field": field, "purpose": purpose, "must_be_derived_from": derivation})
    return rows


def dependency_rows() -> list[dict[str, object]]:
    rows = []
    for gate in GATES:
        upstream = gate["upstream_dependency"]
        rows.append(
            {
                "gate_order": gate["order"],
                "gate_name": gate["gate_name"],
                "upstream_dependency": upstream,
                "dependency_required": str(upstream != "none").lower(),
                "required_link_field": "upstream_artifact_digests" if upstream != "none" else "",
                "failure_if_missing": f"missing_upstream_{upstream}_evidence" if upstream != "none" else "",
            }
        )
    return rows


def checklist_rows() -> list[dict[str, object]]:
    actions = [
        ("produce_artifact", "Generate the gate-specific evidence file from the named source, not from manifest booleans."),
        ("compute_digest", "Compute sha256 over artifact bytes and copy only the digest into the manifest."),
        ("bind_identity", "Verify bundle, measurement, collector, topology, workload/model, claim, and operator IDs match upstream evidence."),
        ("bind_time_window", "Verify artifact validity covers the measurement window and is not stale at replay time."),
        ("bind_dependency", "Record upstream artifact digest links before downstream gates are marked pass."),
        ("preserve_boundary", "Treat evidence_artifact_complete as replay input readiness only; do not mark production_calibrated, production_ready, or claim_credit_allowed."),
    ]
    rows = []
    for gate in GATES:
        for order, (action, check) in enumerate(actions, 1):
            rows.append({"gate_order": gate["order"], "gate_name": gate["gate_name"], "check_order": order, "operator_action": action, "check": check})
    return rows


def main() -> None:
    write_csv(
        OUT_SCHEMA,
        contract_rows(),
        [
            "order",
            "gate_name",
            "manifest_boolean_field",
            "evidence_path_field",
            "digest_field",
            "payload_source",
            "digest_binding",
            "identity_binding",
            "time_window",
            "upstream_dependency",
            "required_payload_fields",
            "fail_closed_reason_if_absent",
        ],
    )
    write_csv(OUT_FIELDS, required_field_rows(), ["gate_name", "required_field", "purpose", "must_be_derived_from"])
    write_csv(OUT_GRAPH, dependency_rows(), ["gate_order", "gate_name", "upstream_dependency", "dependency_required", "required_link_field", "failure_if_missing"])
    write_csv(OUT_CHECKLIST, checklist_rows(), ["gate_order", "gate_name", "check_order", "operator_action", "check"])


if __name__ == "__main__":
    main()
