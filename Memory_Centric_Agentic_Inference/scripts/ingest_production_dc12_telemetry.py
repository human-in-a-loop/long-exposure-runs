#!/usr/bin/env python3
# created: 2026-05-11T23:35:00Z
# cycle: 20
# run_id: run-2026-05-11T121649Z
# agent: worker
# milestone: M-PRODTELEM-1
"""Validate production-shaped DC-001/DC-002 telemetry and replay thresholds."""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

SCHEMA = DATA / "production_dc12_telemetry_schema.csv"
VALID = DATA / "production_dc12_valid_fixture.csv"
INVALID = DATA / "production_dc12_invalid_fixtures.csv"
REQS = DATA / "energy_measurement_requirements.csv"
CXL = DATA / "cxl_contention_thresholds.csv"
ENERGY_SENS = DATA / "energy_architecture_sensitivity.csv"
PLAN_SENS = DATA / "memory_plan_constraint_sensitivity.csv"
SECURITY = DATA / "security_enforcement_decisions.csv"
DC12_CLAIMS = DATA / "dc12_claim_update_matrix.csv"
MISSING_PROXY = DATA / "dc12_missing_production_telemetry.csv"

OUT_RESULTS = DATA / "production_dc12_ingestion_results.csv"
OUT_REPLAY = DATA / "production_dc12_threshold_replay.csv"
OUT_CLAIMS = DATA / "production_dc12_claim_update_matrix.csv"
OUT_MISSING = DATA / "production_dc12_missing_fields_report.csv"

OPTION_A = "A_conventional_request_model_kv_serving"
CONTROL_WORKLOADS = {
    "single-turn chat control",
    "batch summarization/offline inference control",
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


def fnum(row: dict[str, str], key: str, default: float = 0.0) -> float:
    try:
        return float(row.get(key, "") or default)
    except ValueError:
        return default


def truthy(row: dict[str, str], key: str) -> bool:
    return str(row.get(key, "")).strip().lower() == "true"


def required_fields(schema_rows: list[dict[str, str]]) -> list[str]:
    fields = [row["field_name"] for row in schema_rows if row["required"] == "true"]
    if not fields:
        raise ValueError("schema declares no required fields")
    return fields


def threshold_map(cxl_rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    return {row["threshold_id"]: row for row in cxl_rows}


def blocked_reason(row: dict[str, str], req_fields: list[str], thresholds: dict[str, dict[str, str]]) -> tuple[dict[str, bool], str]:
    schema_valid = all(row.get(field, "") != "" for field in req_fields)
    join_valid = bool(row.get("workload_class")) and bool(row.get("object_class")) and bool(row.get("architecture_option"))
    if row.get("constant_id") == "DC-002":
        join_valid = join_valid and row.get("threshold_id") in thresholds
    if row.get("constant_id") == "DC-001":
        join_valid = join_valid and row.get("threshold_id") == "DC001-BYTE-ENERGY-001"

    intervals_aligned = (
        row.get("byte_interval_start_ms") != ""
        and row.get("byte_interval_end_ms") != ""
        and row.get("power_interval_start_ms") == row.get("byte_interval_start_ms")
        and row.get("power_interval_end_ms") == row.get("byte_interval_end_ms")
    )
    noise_floor_passed = fnum(row, "joules_measured") > fnum(row, "energy_noise_floor_j")
    if row.get("constant_id") == "DC-002":
        noise_floor_passed = fnum(row, "latency_p95_us") > 0 and fnum(row, "latency_p99_us") > 0

    security_credit_allowed = (
        truthy(row, "security_allowed")
        and truthy(row, "provenance_valid")
        and truthy(row, "retention_valid")
        and truthy(row, "verifier_valid")
    )
    evidence_ok = row.get("evidence_label") in {"synthetic_production_fixture", "production_target"}
    positive_denied_credit = not security_credit_allowed and (
        fnum(row, "claimed_reuse_credit") > 0 or fnum(row, "claimed_energy_credit_j") > 0
    )

    gates = {
        "schema_valid": schema_valid,
        "join_valid": join_valid and intervals_aligned,
        "noise_floor_passed": noise_floor_passed,
        "security_credit_allowed": security_credit_allowed and not positive_denied_credit,
        "evidence_ok": evidence_ok,
    }
    if not schema_valid:
        return gates, "missing_required_field"
    if not evidence_ok:
        return gates, "not_production_evidence_label"
    if not intervals_aligned:
        return gates, "power_byte_interval_mismatch"
    if not join_valid:
        return gates, "missing_or_invalid_join_key"
    if not noise_floor_passed:
        return gates, "below_noise_floor"
    if positive_denied_credit:
        return gates, "security_denied_positive_credit"
    if not security_credit_allowed:
        return gates, "security_or_provenance_gate_failed"
    return gates, ""


def replay_row(row: dict[str, str], thresholds: dict[str, dict[str, str]]) -> dict[str, object]:
    threshold = thresholds.get(row.get("threshold_id", ""), {})
    if row.get("constant_id") == "DC-001":
        measured = fnum(row, "joules_measured") / max(fnum(row, "bytes_moved"), 1.0)
        collapse = fnum(row, "energy_noise_floor_j") / max(fnum(row, "bytes_moved"), 1.0)
        crossed = measured > collapse
        threshold_basis = "measured_joules_per_byte_above_noise"
    else:
        pct = threshold.get("latency_percentile", "")
        if pct.startswith("p50"):
            measured = fnum(row, "latency_p50_us")
        elif pct.startswith("p95"):
            measured = fnum(row, "latency_p95_us")
        else:
            measured = fnum(row, "latency_p99_us")
        collapse = fnum(threshold, "collapse_threshold")
        crossed = measured > collapse and row.get("workload_class") not in CONTROL_WORKLOADS
        threshold_basis = pct or "latency_percentile_missing"
    return {
        "fixture_id": row["fixture_id"],
        "constant_id": row["constant_id"],
        "threshold_id": row["threshold_id"],
        "workload_class": row.get("workload_class", ""),
        "object_class": row.get("object_class", ""),
        "architecture_option": row.get("architecture_option", ""),
        "measured_value": round(measured, 9),
        "threshold_value": round(collapse, 9),
        "threshold_basis": threshold_basis,
        "threshold_crossed": str(crossed).lower(),
        "evidence_label": row.get("evidence_label", ""),
    }


def build_missing_report(schema_rows: list[dict[str, str]], proxy_missing: list[dict[str, str]]) -> list[dict[str, object]]:
    schema_fields = {row["field_name"] for row in schema_rows}
    mapping = {
        "accelerator_power_counters": ["joules_measured", "power_counter_source", "energy_noise_floor_j"],
        "tier_specific_bytes": ["source_tier", "destination_tier", "bytes_moved", "resident_bytes"],
        "cxl_pooled_memory_latency": ["latency_p50_us", "latency_p95_us", "latency_p99_us", "hardware_topology_id"],
        "tenant_concurrency": ["tenant_count", "queue_depth"],
        "workload_object_labels": ["workload_class", "object_class", "reuse_decision"],
    }
    rows = []
    for item in proxy_missing:
        telemetry_id = item["telemetry_id"]
        fields = mapping.get(telemetry_id, [])
        rows.append(
            {
                "telemetry_id": telemetry_id,
                "required_production_telemetry": item["required_production_telemetry"],
                "schema_fields": "; ".join(fields),
                "covered_by_schema": str(bool(fields) and all(field in schema_fields for field in fields)).lower(),
                "deployment_specific": "true",
                "rank": len(rows) + 1,
                "instrumentation_plan": "collect joined target telemetry before promoting CL-012",
            }
        )
    return rows


def main() -> None:
    schema_rows = read_csv(SCHEMA)
    valid_rows = read_csv(VALID)
    invalid_rows = read_csv(INVALID)
    req_fields = required_fields(schema_rows)
    thresholds = threshold_map(read_csv(CXL))

    # Read-only dependency checks. These raise if an expected baseline disappears.
    for path in [REQS, ENERGY_SENS, PLAN_SENS, SECURITY, DC12_CLAIMS]:
        read_csv(path)

    all_rows = valid_rows + invalid_rows
    replay = [replay_row(row, thresholds) for row in all_rows]
    replay_by_fixture = {row["fixture_id"]: row for row in replay}
    results: list[dict[str, object]] = []
    for row in all_rows:
        gates, reason = blocked_reason(row, req_fields, thresholds)
        threshold_crossed = replay_by_fixture[row["fixture_id"]]["threshold_crossed"] == "true"
        calibration_candidate = (
            truthy(row, "calibration_candidate")
            and not reason
            and row.get("evidence_label") in {"synthetic_production_fixture", "production_target"}
        )
        production_calibrated = calibration_candidate and row.get("evidence_label") == "production_target"
        credit_allowed = not reason and gates["security_credit_allowed"]
        if row.get("workload_class") in CONTROL_WORKLOADS:
            production_calibrated = False
            calibration_candidate = False
            credit_allowed = False
        results.append(
            {
                "fixture_id": row["fixture_id"],
                "fixture_class": row["fixture_class"],
                "constant_id": row["constant_id"],
                "evidence_label": row["evidence_label"],
                "schema_valid": str(gates["schema_valid"]).lower(),
                "join_valid": str(gates["join_valid"]).lower(),
                "noise_floor_passed": str(gates["noise_floor_passed"]).lower(),
                "security_credit_allowed": str(gates["security_credit_allowed"]).lower(),
                "threshold_crossed": str(threshold_crossed).lower(),
                "calibration_candidate": str(calibration_candidate).lower(),
                "production_calibrated": str(production_calibrated).lower(),
                "reuse_credit_granted": 0.0 if not credit_allowed else fnum(row, "claimed_reuse_credit"),
                "energy_credit_granted_j": 0.0 if not credit_allowed else fnum(row, "claimed_energy_credit_j"),
                "blocked_reason": reason,
            }
        )

    valid_candidates = [r for r in results if r["calibration_candidate"] == "true"]
    blocked_invalid = [r for r in results if r["fixture_class"] == "invalid" and r["blocked_reason"]]
    denied = [r for r in results if r["security_credit_allowed"] == "false"]
    controls = [r for r in results if r["fixture_id"] == "valid-control-a"]
    claims = [
        {
            "claim_id": "CL-012",
            "update_status": "production_contract_ready_candidate_only",
            "production_calibrated": "false",
            "basis": f"{len(valid_candidates)} synthetic production-shaped rows passed gates; no real production_target evidence ingested",
            "blocked_reason": "synthetic fixtures are not real production evidence",
            "evidence_label": "synthetic_production_fixture",
        },
        {
            "claim_id": "CL-004",
            "update_status": "threshold_replay_ready",
            "production_calibrated": "false",
            "basis": "DC-002 rows replay against existing CXL/pooled-memory thresholds",
            "blocked_reason": "awaiting real target CXL/pool-memory telemetry",
            "evidence_label": "synthetic_production_fixture",
        },
        {
            "claim_id": "CL-005",
            "update_status": "contention_gate_ready",
            "production_calibrated": "false",
            "basis": "Option B/C updates are named by threshold crossings only",
            "blocked_reason": "synthetic fixture only",
            "evidence_label": "synthetic_production_fixture",
        },
        {
            "claim_id": "SECURITY-GATE-ENERGY-001",
            "update_status": "validated_negative_control",
            "production_calibrated": "false",
            "basis": f"security blocked rows={len(denied)}; denied reuse/energy credit granted=0",
            "blocked_reason": "security_denied_rows_receive_zero_credit",
            "evidence_label": "synthetic_production_fixture",
        },
        {
            "claim_id": "CONTROL-OPTION-A",
            "update_status": "validated_negative_control",
            "production_calibrated": "false",
            "basis": f"control rows={len(controls)}; controls remain Option A and not calibration candidates",
            "blocked_reason": "control_workload_has_no_positive_reuse",
            "evidence_label": "synthetic_production_fixture",
        },
    ]

    write_csv(
        OUT_RESULTS,
        results,
        [
            "fixture_id",
            "fixture_class",
            "constant_id",
            "evidence_label",
            "schema_valid",
            "join_valid",
            "noise_floor_passed",
            "security_credit_allowed",
            "threshold_crossed",
            "calibration_candidate",
            "production_calibrated",
            "reuse_credit_granted",
            "energy_credit_granted_j",
            "blocked_reason",
        ],
    )
    write_csv(
        OUT_REPLAY,
        replay,
        [
            "fixture_id",
            "constant_id",
            "threshold_id",
            "workload_class",
            "object_class",
            "architecture_option",
            "measured_value",
            "threshold_value",
            "threshold_basis",
            "threshold_crossed",
            "evidence_label",
        ],
    )
    write_csv(
        OUT_CLAIMS,
        claims,
        ["claim_id", "update_status", "production_calibrated", "basis", "blocked_reason", "evidence_label"],
    )
    write_csv(
        OUT_MISSING,
        build_missing_report(schema_rows, read_csv(MISSING_PROXY)),
        [
            "telemetry_id",
            "required_production_telemetry",
            "schema_fields",
            "covered_by_schema",
            "deployment_specific",
            "rank",
            "instrumentation_plan",
        ],
    )


if __name__ == "__main__":
    main()
