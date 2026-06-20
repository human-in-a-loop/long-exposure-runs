#!/usr/bin/env python3
# created: 2026-05-11T23:55:00Z
# cycle: 19
# run_id: run-2026-05-11T121649Z
# agent: worker
# milestone: M-DC12-1
"""Apply host-local DC-001/DC-002 proxy measurements to existing thresholds.

The original synthetic baselines are read-only inputs. This script writes
dc12_* overlay artifacts that preserve proxy-only labels.
"""

from __future__ import annotations

import csv
import statistics
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

BYTE = DATA / "dc12_byte_movement_measurements.csv"
CONTENTION = DATA / "dc12_contention_measurements.csv"
META = DATA / "dc12_local_bench_metadata.csv"
REQS = DATA / "energy_measurement_requirements.csv"
CXL = DATA / "cxl_contention_thresholds.csv"
ENERGY_SENS = DATA / "energy_architecture_sensitivity.csv"
PLAN_SENS = DATA / "memory_plan_constraint_sensitivity.csv"
SECURITY = DATA / "security_enforcement_decisions.csv"
PLAN_SUMMARY = DATA / "memory_plan_workload_summary.csv"

OUT_OVERLAY = DATA / "dc12_proxy_threshold_overlay.csv"
OUT_CLAIMS = DATA / "dc12_claim_update_matrix.csv"
OUT_MISSING = DATA / "dc12_missing_production_telemetry.csv"

OPTION_A = "A_conventional_request_model_kv_serving"
OPTION_B = "B_memory_object_aware_runtime"
OPTION_C = "C_trajectory_dag_memory_fabric"
CONTROL_WORKLOADS = {
    "single-turn chat control",
    "batch summarization/offline inference control",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        raise ValueError(f"{path} is empty")
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


def meta_value(rows: list[dict[str, str]], key: str, default: str = "") -> str:
    for row in rows:
        if row["metadata_key"] == key:
            return row["metadata_value"]
    return default


def option_after_for_threshold(workload: str, object_class: str, crossed: bool) -> str:
    if workload in CONTROL_WORKLOADS:
        return OPTION_A
    if not crossed:
        return ""
    if "branch state" in object_class or "trajectory log" in object_class or "verifier state" in object_class:
        return OPTION_B
    return OPTION_A


def build_dc001_overlay(byte_rows: list[dict[str, str]], power_source: str) -> list[dict[str, object]]:
    sequential = [r for r in byte_rows if r["access_pattern"].startswith("sequential")]
    throughputs = [fnum(r, "throughput_mb_s") for r in sequential]
    mean = statistics.mean(throughputs)
    rel_spread = (max(throughputs) - min(throughputs)) / max(mean, 1e-9)
    below_noise = rel_spread < 0.05 or power_source == "unavailable"
    rows: list[dict[str, object]] = []
    for row in byte_rows:
        rows.append(
            {
                "overlay_id": f"DC001-overlay-{row['measurement_id']}",
                "constant_id": "DC-001",
                "source_threshold_id": "DC001-BYTE-ENERGY-001",
                "workload_class": "host-local proxy microbenchmark",
                "object_class": "bytes moved/read/written",
                "proxy_measurement_id": row["measurement_id"],
                "proxy_pattern": row["access_pattern"],
                "worker_count": row["worker_count"],
                "buffer_size_bytes": row["buffer_size_bytes"],
                "measured_latency_us": row["latency_p95_us"],
                "measured_throughput_mb_s": row["throughput_mb_s"],
                "measured_penalty_units": "",
                "collapse_threshold": "",
                "threshold_crossed": "not_applicable",
                "option_before": "",
                "option_after_proxy": "",
                "claim_effect": "CL-012 proxy_only; no production calibration",
                "production_calibrated": "false",
                "power_source": power_source,
                "below_noise_or_missing_power": str(below_noise).lower(),
                "evidence_label": "host_local_proxy",
            }
        )
    return rows


def build_dc002_overlay(
    contention_rows: list[dict[str, str]],
    cxl_thresholds: list[dict[str, str]],
    plan_summary: list[dict[str, str]],
    power_source: str,
) -> list[dict[str, object]]:
    max_workers = max(int(r["worker_count"]) for r in contention_rows)
    measured = next(r for r in contention_rows if int(r["worker_count"]) == max_workers)
    plan_by_workload = {r["workload_class"]: r for r in plan_summary}
    rows: list[dict[str, object]] = []
    for threshold in cxl_thresholds:
        pct = threshold["latency_percentile"]
        if pct.startswith("p50"):
            measured_us = fnum(measured, "latency_p50_us")
            penalty = measured_us / max(fnum(contention_rows[0], "latency_p50_us"), 1e-9)
        elif pct.startswith("p95"):
            measured_us = fnum(measured, "latency_p95_us")
            penalty = fnum(measured, "contention_proxy_p95_over_1w")
        else:
            measured_us = fnum(measured, "latency_p99_us")
            penalty = fnum(measured, "contention_proxy_p99_over_1w")
        collapse_threshold = fnum(threshold, "collapse_threshold")
        workload = threshold["workload_class"]
        crossed = penalty > collapse_threshold and workload not in CONTROL_WORKLOADS
        plan = plan_by_workload.get(workload, {})
        before = plan.get("planned_option", "")
        after = option_after_for_threshold(workload, threshold["object_class"], crossed)
        if workload in CONTROL_WORKLOADS:
            effect = "control_no_reuse_remains_option_A"
            after = OPTION_A
        elif crossed:
            effect = "proxy_contention_crosses_existing_threshold"
        else:
            effect = "proxy_contention_does_not_cross_existing_threshold"
        rows.append(
            {
                "overlay_id": f"DC002-overlay-{threshold['threshold_id']}",
                "constant_id": "DC-002",
                "source_threshold_id": threshold["threshold_id"],
                "workload_class": workload,
                "object_class": threshold["object_class"],
                "proxy_measurement_id": measured["measurement_id"],
                "proxy_pattern": measured["access_pattern"],
                "worker_count": max_workers,
                "buffer_size_bytes": measured["buffer_size_bytes"],
                "measured_latency_us": round(measured_us, 6),
                "measured_throughput_mb_s": "",
                "measured_penalty_units": round(penalty, 6),
                "collapse_threshold": collapse_threshold,
                "threshold_crossed": str(crossed).lower(),
                "option_before": before,
                "option_after_proxy": after or before,
                "claim_effect": effect,
                "production_calibrated": "false",
                "power_source": power_source,
                "below_noise_or_missing_power": "false",
                "evidence_label": "host_local_proxy",
            }
        )
    return rows


def build_claims(
    overlay: list[dict[str, object]],
    security_rows: list[dict[str, str]],
    power_source: str,
) -> list[dict[str, object]]:
    denied = [r for r in security_rows if r["validation_decision"] == "denied_reuse"]
    denied_credit = sum(fnum(r, "safe_reuse_credit") for r in denied)
    crossed = [r for r in overlay if r["constant_id"] == "DC-002" and r["threshold_crossed"] == "true"]
    non_crossed = [r for r in overlay if r["constant_id"] == "DC-002" and r["threshold_crossed"] == "false"]
    return [
        {
            "claim_id": "CL-012",
            "update_status": "proxy_only" if power_source == "unavailable" else "speculative",
            "production_calibrated": "false",
            "basis": "host-local byte/time proxy; direct power counters unavailable",
            "negative_control_result": "below-noise-or-missing-power does not promote CL-012",
            "affected_rows": len([r for r in overlay if r["constant_id"] == "DC-001"]),
            "evidence_label": "host_local_proxy",
        },
        {
            "claim_id": "CL-004",
            "update_status": "proxy_threshold_overlay",
            "production_calibrated": "false",
            "basis": f"{len(crossed)} DC-002 rows crossed; {len(non_crossed)} did not cross under local contention proxy",
            "negative_control_result": "control workloads remain Option A",
            "affected_rows": len(crossed) + len(non_crossed),
            "evidence_label": "host_local_proxy",
        },
        {
            "claim_id": "CL-005",
            "update_status": "proxy_threshold_overlay",
            "production_calibrated": "false",
            "basis": "trajectory/DAG option updates are allowed only when existing retained-value thresholds are crossed",
            "negative_control_result": "host-local proxy is not treated as CXL production evidence",
            "affected_rows": len([r for r in crossed if str(r["option_before"]).startswith("C_")]),
            "evidence_label": "host_local_proxy",
        },
        {
            "claim_id": "SECURITY-GATE-ENERGY-001",
            "update_status": "validated_negative_control",
            "production_calibrated": "false",
            "basis": f"denied_reuse rows={len(denied)} denied_safe_reuse_credit={round(denied_credit, 6)}",
            "negative_control_result": "security-denied reuse receives zero reuse/energy credit",
            "affected_rows": len(denied),
            "evidence_label": "synthetic_enforcement_plus_host_local_proxy",
        },
    ]


def build_missing_telemetry(requirements: list[dict[str, str]]) -> list[dict[str, object]]:
    required_items = [
        ("accelerator_power_counters", "accelerator/host power counters", "needed to convert time/bytes proxy into measured joules"),
        ("tier_specific_bytes", "bytes by source tier, destination tier, object class", "needed to distinguish HBM, DRAM, CXL, NVMe, and remote movement"),
        ("cxl_pooled_memory_latency", "CXL or pooled-memory p50/p95/p99 under target topology", "needed to replace local DRAM/cache contention proxy"),
        ("tenant_concurrency", "tenant concurrency and queue depth", "needed to measure isolation and contention under production sharing"),
        ("workload_object_labels", "workload_class and object_class labels", "needed to join telemetry to memory-centric planner decisions"),
    ]
    req_text = " | ".join(r["required_telemetry"] for r in requirements)
    return [
        {
            "telemetry_id": item_id,
            "required_production_telemetry": text,
            "why_missing_blocks_calibration": why,
            "present_in_local_proxy": "false",
            "linked_measurement_requirement": "found" if text.split()[0] in req_text else "required",
            "evidence_label": "production_gap",
        }
        for item_id, text, why in required_items
    ]


def main() -> None:
    byte_rows = read_csv(BYTE)
    contention_rows = read_csv(CONTENTION)
    meta_rows = read_csv(META)
    requirements = read_csv(REQS)
    cxl_thresholds = read_csv(CXL)
    _energy_sens = read_csv(ENERGY_SENS)
    _plan_sens = read_csv(PLAN_SENS)
    security_rows = read_csv(SECURITY)
    plan_summary = read_csv(PLAN_SUMMARY)
    power_source = meta_value(meta_rows, "power_source", "unavailable")

    overlay = build_dc001_overlay(byte_rows, power_source)
    overlay.extend(build_dc002_overlay(contention_rows, cxl_thresholds, plan_summary, power_source))
    write_csv(
        OUT_OVERLAY,
        overlay,
        [
            "overlay_id",
            "constant_id",
            "source_threshold_id",
            "workload_class",
            "object_class",
            "proxy_measurement_id",
            "proxy_pattern",
            "worker_count",
            "buffer_size_bytes",
            "measured_latency_us",
            "measured_throughput_mb_s",
            "measured_penalty_units",
            "collapse_threshold",
            "threshold_crossed",
            "option_before",
            "option_after_proxy",
            "claim_effect",
            "production_calibrated",
            "power_source",
            "below_noise_or_missing_power",
            "evidence_label",
        ],
    )
    write_csv(
        OUT_CLAIMS,
        build_claims(overlay, security_rows, power_source),
        [
            "claim_id",
            "update_status",
            "production_calibrated",
            "basis",
            "negative_control_result",
            "affected_rows",
            "evidence_label",
        ],
    )
    write_csv(
        OUT_MISSING,
        build_missing_telemetry(requirements),
        [
            "telemetry_id",
            "required_production_telemetry",
            "why_missing_blocks_calibration",
            "present_in_local_proxy",
            "linked_measurement_requirement",
            "evidence_label",
        ],
    )


if __name__ == "__main__":
    main()
