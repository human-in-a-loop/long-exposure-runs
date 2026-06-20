# created: 2026-05-12T00:45:00Z
# cycle: 21
# run_id: run-2026-05-11T121649Z
# agent: worker
# milestone: M-FINALPKG-1

from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

INPUTS = {
    "claims": DATA / "synthesis_claims_register.csv",
    "architecture": DATA / "synthesis_architecture_decision_matrix.csv",
    "agenda": DATA / "research_agenda_ranked.csv",
    "energy": DATA / "energy_claim_update_matrix.csv",
    "security": DATA / "security_architecture_decision_updates.csv",
    "planner": DATA / "memory_plan_constraint_sensitivity.csv",
    "dc12_proxy": DATA / "dc12_claim_update_matrix.csv",
    "production_claims": DATA / "production_dc12_claim_update_matrix.csv",
    "production_ingestion": DATA / "production_dc12_ingestion_results.csv",
    "missing_telemetry": DATA / "production_dc12_missing_fields_report.csv",
}

READINESS_ORDER = {
    "validated_mechanism": 0,
    "synthetic_supported": 1,
    "host_local_proxy_only": 2,
    "contract_ready": 3,
    "production_calibration_required": 4,
    "production_ready": 5,
    "blocked": -1,
}

CLAIM_CONSTANT_LINKS = {
    "CL-004": {"DC-002"},
    "CL-005": {"DC-002"},
    "CL-012": {"DC-001", "DC-002"},
}


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


def as_bool(value: object) -> bool:
    return str(value).strip().lower() == "true"


def require_columns(name: str, rows: list[dict[str, str]], required: set[str], blocked: list[dict[str, object]]) -> None:
    fields = set(rows[0].keys()) if rows else set()
    missing = sorted(required - fields)
    if not rows or missing:
        blocked.append(
            {
                "claim_id": f"SCHEMA-{name}",
                "claim": f"{name} input has missing required columns: {';'.join(missing) if missing else 'empty'}",
                "blocker_type": "schema_gap",
                "source_artifact": str(INPUTS[name].relative_to(ROOT)),
                "required_resolution": "Preserve upstream schema or document an explicit migration before final package synthesis.",
                "readiness_label": "blocked",
            }
        )


def production_gate(row: dict[str, str]) -> tuple[bool, str]:
    required = [
        "schema_valid",
        "join_valid",
        "noise_floor_passed",
        "security_credit_allowed",
        "threshold_crossed",
        "calibration_candidate",
        "production_calibrated",
    ]
    for field in required:
        if not as_bool(row.get(field)):
            return False, field
    if row.get("evidence_label") != "production_target":
        return False, "not_production_target"
    return True, "all_production_gates_passed"


def readiness_for_claim(claim_id: str, claim_type: str, prod_rows: list[dict[str, str]], proxy_rows: list[dict[str, str]]) -> tuple[str, str, bool]:
    linked_constants = CLAIM_CONSTANT_LINKS.get(claim_id, set())
    relevant_prod = [
        r
        for r in prod_rows
        if r.get("claim_id") == claim_id or (r.get("constant_id") in linked_constants)
    ]
    production_ready = any(production_gate(r)[0] for r in relevant_prod)
    if production_ready:
        return "production_ready", "direct production_target row passed schema, joins, noise, security, and threshold gates", True

    if any(r.get("claim_id") == claim_id and r.get("evidence_label") == "host_local_proxy" for r in proxy_rows):
        return "host_local_proxy_only", "host-local proxy evidence exists but cannot calibrate production claims", False

    if claim_id in {"CL-012"}:
        return "production_calibration_required", "energy/economics claim remains blocked on direct target power, bytes, contention, tenant, workload, and security joins", False

    if any(r.get("claim_id") == claim_id for r in prod_rows):
        return "contract_ready", "production telemetry contract can ingest candidate rows but current evidence is synthetic fixture only", False

    if claim_type in {"validated_artifact", "derived"}:
        return "validated_mechanism", "validated by prior milestone artifacts but not production telemetry", False

    return "synthetic_supported", "supported by simulation, synthetic sensitivity, or synthetic enforcement evidence", False


def build() -> None:
    blocked: list[dict[str, object]] = []
    tables = {name: read_csv(path) for name, path in INPUTS.items()}
    require_columns("claims", tables["claims"], {"claim_id", "claim", "claim_type", "supporting_artifacts"}, blocked)
    require_columns("architecture", tables["architecture"], {"workload_class", "final_option", "option_short", "dominant_reversal_mechanism"}, blocked)
    require_columns("agenda", tables["agenda"], {"rank", "question_or_experiment", "expected_evidence_type", "risk_retired"}, blocked)
    require_columns("production_ingestion", tables["production_ingestion"], {"evidence_label", "schema_valid", "join_valid", "noise_floor_passed", "security_credit_allowed", "threshold_crossed", "calibration_candidate", "production_calibrated"}, blocked)

    production_claim_rows = tables["production_claims"]
    ingestion_rows = tables["production_ingestion"]
    proxy_rows = tables["dc12_proxy"]

    claim_rows: list[dict[str, object]] = []
    for claim in tables["claims"]:
        claim_id = claim["claim_id"]
        label, basis, production_ready = readiness_for_claim(claim_id, claim.get("claim_type", ""), production_claim_rows + ingestion_rows, proxy_rows)
        gate_status = "production_ready" if production_ready else "fail_closed_without_production_target"
        claim_rows.append(
            {
                "claim_id": claim_id,
                "claim": claim["claim"],
                "claim_type": claim.get("claim_type", ""),
                "readiness_label": label,
                "production_ready": str(production_ready).lower(),
                "evidence_classes": claim.get("claim_type", "") + "; " + "; ".join(sorted({r.get("evidence_label", "") for r in production_claim_rows + proxy_rows if r.get("claim_id") == claim_id} - {""})),
                "gate_status": gate_status,
                "basis": basis,
                "supporting_artifacts": claim.get("supporting_artifacts", ""),
                "falsification_condition": claim.get("falsification_condition", ""),
            }
        )

    for row in production_claim_rows:
        label = "contract_ready" if not as_bool(row.get("production_calibrated")) else "production_ready"
        claim_rows.append(
            {
                "claim_id": row.get("claim_id", ""),
                "claim": row.get("basis", ""),
                "claim_type": "production_telemetry_contract",
                "readiness_label": label,
                "production_ready": str(as_bool(row.get("production_calibrated")) and row.get("evidence_label") == "production_target").lower(),
                "evidence_classes": row.get("evidence_label", ""),
                "gate_status": "fail_closed_without_production_target" if row.get("evidence_label") != "production_target" else "production_target_seen",
                "basis": row.get("blocked_reason", "") or row.get("update_status", ""),
                "supporting_artifacts": "data/production_dc12_claim_update_matrix.csv; data/production_dc12_ingestion_results.csv",
                "falsification_condition": "A synthetic/proxy row becomes production_ready or real production_target row fails required gates.",
            }
        )

    option_rows: list[dict[str, object]] = []
    planner_by_workload = {r["workload_class"]: r for r in tables["planner"] if r.get("setting") == "baseline"}
    security_by_workload = {r["workload_class"]: r for r in tables["security"]}
    for arch in tables["architecture"]:
        workload = arch["workload_class"]
        planner = planner_by_workload.get(workload, {})
        security = security_by_workload.get(workload, {})
        blockers = []
        text = " ".join([arch.get("dominant_reversal_mechanism", ""), planner.get("dominant_constraint", ""), planner.get("constraint_counts", "")]).lower()
        for word in ["security", "queueing", "contention", "validation", "compression", "control_or_zero_reuse"]:
            if word in text:
                blockers.append(word)
        option = planner.get("planned_option") or arch.get("final_option", "")
        short = "A" if option.startswith("A_") else "B" if option.startswith("B_") else "C" if option.startswith("C_") else arch.get("option_short", "")
        production_ready = False
        readiness = "validated_mechanism" if short == "A" else "production_calibration_required"
        if "control" in workload or short == "A":
            readiness = "validated_mechanism"
        elif set(blockers) & {"security", "queueing", "contention", "validation", "compression"}:
            readiness = "contract_ready"
        option_rows.append(
            {
                "workload_class": workload,
                "option": short,
                "recommended_option": option,
                "readiness_label": readiness,
                "production_ready": str(production_ready).lower(),
                "dominant_positive_mechanism": arch.get("dominant_positive_mechanism", ""),
                "known_blockers": ";".join(blockers) if blockers else "none_named",
                "security_adjusted_value_proxy": arch.get("security_adjusted_value_proxy", ""),
                "planner_net_value": planner.get("total_net_plan_value", ""),
                "security_safe_hit_rate": security.get("safe_hit_rate", ""),
                "basis": "Option B/C remain mechanism-valid and contract-ready only until production_target telemetry passes all gates.",
            }
        )

    experiment_rows: list[dict[str, object]] = []
    missing = tables["missing_telemetry"]
    missing_text = "; ".join(
        f"{r.get('telemetry_id', '').strip()}:{r.get('schema_fields', '').strip()}"
        for r in missing
        if r.get("telemetry_id", "").strip() or r.get("schema_fields", "").strip()
    )
    for row in tables["agenda"]:
        rank = int(float(row.get("rank", len(experiment_rows) + 1)))
        experiment_rows.append(
            {
                "rank": rank,
                "experiment": row.get("question_or_experiment", ""),
                "expected_evidence_type": row.get("expected_evidence_type", ""),
                "unblocks_claims": "CL-002;CL-003;CL-004;CL-005;CL-012" if rank <= 3 else "CL-002;CL-003",
                "required_telemetry": missing_text if rank <= 3 else "workload/object labels; provenance/security decisions",
                "priority_score": max(1, 12 - rank),
                "risk_retired": row.get("risk_retired", ""),
                "production_boundary": "Must emit evidence_label=production_target and pass production_dc12 ingestion gates before claim promotion.",
            }
        )
    experiment_rows.extend(
        [
            {
                "rank": len(experiment_rows) + 1,
                "experiment": "Joint DC-001/DC-002 production telemetry drop-in replay",
                "expected_evidence_type": "production_target",
                "unblocks_claims": "CL-004;CL-005;CL-012",
                "required_telemetry": missing_text,
                "priority_score": 12,
                "risk_retired": "whether contract-ready energy/contention claims survive real target counters and joins",
                "production_boundary": "Only this evidence class can produce production_ready rows.",
            }
        ]
    )
    experiment_rows = sorted(experiment_rows, key=lambda r: (-int(r["priority_score"]), int(r["rank"])))
    for i, row in enumerate(experiment_rows, 1):
        row["rank"] = i

    for row in ingestion_rows:
        ready, reason = production_gate(row)
        if not ready:
            blocked.append(
                {
                    "claim_id": row.get("constant_id", row.get("fixture_id", "")),
                    "claim": f"Production calibration rejected for {row.get('fixture_id', '')}",
                    "blocker_type": reason,
                    "source_artifact": "data/production_dc12_ingestion_results.csv",
                    "required_resolution": "Provide real production_target telemetry with all required fields, joins, noise, threshold, and security/provenance gates passing.",
                    "readiness_label": "blocked" if row.get("fixture_class") == "invalid" else "production_calibration_required",
                }
            )

    write_csv(
        DATA / "final_claim_readiness_matrix.csv",
        claim_rows,
        ["claim_id", "claim", "claim_type", "readiness_label", "production_ready", "evidence_classes", "gate_status", "basis", "supporting_artifacts", "falsification_condition"],
    )
    write_csv(
        DATA / "final_architecture_option_readiness.csv",
        option_rows,
        ["workload_class", "option", "recommended_option", "readiness_label", "production_ready", "dominant_positive_mechanism", "known_blockers", "security_adjusted_value_proxy", "planner_net_value", "security_safe_hit_rate", "basis"],
    )
    write_csv(
        DATA / "final_production_experiment_backlog.csv",
        experiment_rows,
        ["rank", "experiment", "expected_evidence_type", "unblocks_claims", "required_telemetry", "priority_score", "risk_retired", "production_boundary"],
    )
    write_csv(
        DATA / "final_blocked_claims.csv",
        blocked,
        ["claim_id", "claim", "blocker_type", "source_artifact", "required_resolution", "readiness_label"],
    )

    print(f"claim_rows={len(claim_rows)}")
    print(f"option_rows={len(option_rows)}")
    print(f"experiment_rows={len(experiment_rows)}")
    print(f"blocked_rows={len(blocked)}")


if __name__ == "__main__":
    build()
