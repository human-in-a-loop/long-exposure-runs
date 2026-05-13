# created: 2026-05-13T06:52:00Z
# cycle: 2
# run_id: run-2026-05-13T015136Z
# agent: worker
# milestone: M-SWBASE-2
"""Replay validated workload rows through stronger programmable baselines."""

from __future__ import annotations

import csv
import json
import math
import struct
import zlib
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path

import calibrated_breakeven as cal


ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "physicalized-weights" / "data"
DOCS_DIR = ROOT / "physicalized-weights" / "docs"

WORKLOAD_CSV = DATA_DIR / "workload_scenarios.csv"
OVERLAY_CSV = DATA_DIR / "workload_viability_overlay.csv"
CAL_SUMMARY_JSON = DATA_DIR / "calibrated_breakeven_summary.json"

COMPARISON_CSV = DATA_DIR / "stronger_baseline_comparison.csv"
SUMMARY_JSON = DATA_DIR / "stronger_baseline_summary.json"
THRESHOLDS_CSV = DATA_DIR / "stronger_baseline_thresholds.csv"
COMPARISON_PNG = DATA_DIR / "stronger_baseline_workload_comparison.png"
REPORT_MD = DOCS_DIR / "stronger_baseline_comparison.md"

ALTERNATIVES = (
    "optimized_software_runtime",
    "programmable_accelerator",
    "hybrid_physicalized_safety_filter",
)

DECISION_BY_WINNER = {
    "optimized_software_runtime": "software_dominates",
    "programmable_accelerator": "accelerator_dominates",
    "hybrid_physicalized_safety_filter": "hybrid_preserved",
}


@dataclass(frozen=True)
class WorkloadRow:
    scenario_id: str
    description: str
    raw_requests_per_day: float
    effective_fast_path_requests_per_day: float
    fallback_frequency: float
    fail_safe_fraction: float
    near_threshold_frequency: float
    update_interval_days: float
    audit_control_scale: str
    utilization: float
    feature_extraction_us: float
    audit_logging_us: float
    software_memory_savings: float
    workload_classification: str


@dataclass(frozen=True)
class ComparisonRow:
    scenario_id: str
    alternative: str
    raw_requests_per_day: float
    effective_fast_path_requests_per_day: float
    fallback_requests_per_day: float
    feature_extraction_cost_per_day_pj: float
    audit_logging_cost_per_day_pj: float
    update_control_cost_per_day_pj: float
    utilization_adjusted_fixed_substrate_cost_per_day_pj: float
    estimated_energy_per_accepted_request_pj: float
    estimated_latency_per_accepted_request_us: float
    total_daily_cost_proxy_pj: float
    winner: bool
    decision_class: str
    mechanism_note: str


@dataclass(frozen=True)
class ThresholdRow:
    scenario_id: str
    threshold_name: str
    baseline_value: float
    threshold_value: str
    unit: str
    interpretation: str


def read_workloads() -> list[WorkloadRow]:
    with WORKLOAD_CSV.open(newline="") as f:
        rows = [
            WorkloadRow(
                scenario_id=row["scenario_id"],
                description=row["description"],
                raw_requests_per_day=float(row["raw_requests_per_day"]),
                effective_fast_path_requests_per_day=float(row["effective_fast_path_requests_per_day"]),
                fallback_frequency=float(row["fallback_frequency"]),
                fail_safe_fraction=float(row["fail_safe_fraction"]),
                near_threshold_frequency=float(row["near_threshold_frequency"]),
                update_interval_days=float(row["update_interval_days"]),
                audit_control_scale=row["audit_control_scale"],
                utilization=float(row["utilization"]),
                feature_extraction_us=float(row["feature_extraction_us"]),
                audit_logging_us=float(row["audit_logging_us"]),
                software_memory_savings=float(row["software_memory_savings"]),
                workload_classification=row["viability_classification"],
            )
            for row in csv.DictReader(f)
        ]
    with OVERLAY_CSV.open(newline="") as f:
        overlay_ids = {row["scenario_id"] for row in csv.DictReader(f)}
    workload_ids = {row.scenario_id for row in rows}
    if workload_ids != overlay_ids:
        raise ValueError("workload_scenarios.csv and workload_viability_overlay.csv scenario sets differ")
    return rows


def params() -> dict[str, float]:
    return cal.primitive_params(cal.load_assumptions(), cal.probe_metrics())


def accepted_requests(row: WorkloadRow) -> float:
    return max(row.raw_requests_per_day * (1.0 - row.fail_safe_fraction), 0.0)


def accepted_fast_path_requests(row: WorkloadRow) -> float:
    if row.fallback_frequency >= 1.0 or row.effective_fast_path_requests_per_day <= 0.0:
        return 0.0
    return row.effective_fast_path_requests_per_day


def fallback_requests(row: WorkloadRow) -> float:
    return max(row.raw_requests_per_day * row.fallback_frequency, 0.0)


def control_us(scale: str) -> float:
    return {"low": 0.08, "mid": 0.28, "high": 0.95}[scale]


def common_terms(row: WorkloadRow, p: dict[str, float]) -> dict[str, float]:
    raw = row.raw_requests_per_day
    return {
        "feature_day": raw * row.feature_extraction_us * p["pj_per_us_proxy"],
        "audit_day": raw * row.audit_logging_us * p["pj_per_us_proxy"],
        "control_day": raw * control_us(row.audit_control_scale) * p["pj_per_us_proxy"],
        "software_dot": p["python_dot_us"] * p["pj_per_us_proxy"],
        "dispatch": p["dispatch_us"] * p["pj_per_us_proxy"],
        "local_dot": 8.0 * (p["sram_pj"] + p["int8_mac_pj"]),
        "local_feature": 8.0 * p["sram_pj"],
        "offchip_feature": 8.0 * p["dram_pj"] * (1.0 - row.software_memory_savings),
    }


def cost_for(row: WorkloadRow, alternative: str, p: dict[str, float], *, software_savings: float | None = None, accel_multiplier: float = 1.0) -> ComparisonRow:
    if software_savings is not None:
        row = WorkloadRow(**{**asdict(row), "software_memory_savings": software_savings})
    c = common_terms(row, p)
    raw = row.raw_requests_per_day
    accepted = accepted_requests(row)
    fast = accepted_fast_path_requests(row)
    fallback = fallback_requests(row)
    update_factor = 30.0 / max(row.update_interval_days, 1e-9)
    util = max(row.utilization, 1e-9)

    feature_day = c["feature_day"]
    audit_day = c["audit_day"]
    update_day = 0.0
    fixed_day = 0.0
    latency_us = 0.0
    mechanism = ""

    if alternative == "optimized_software_runtime":
        compute = c["software_dot"] * 0.72
        memory = c["offchip_feature"] * 0.60
        per_req = compute + memory
        update_day = 150.0 * update_factor
        total = feature_day + audit_day + raw * per_req + update_day
        latency_us = row.feature_extraction_us + row.audit_logging_us + p["python_dot_us"] * 0.72
        mechanism = "software keeps update flexibility and applies memory/runtime savings to every request"
    elif alternative == "programmable_accelerator":
        compute = c["local_dot"] * 0.32 * accel_multiplier
        memory = c["local_feature"] * 0.42
        per_req = compute + memory + control_us(row.audit_control_scale) * p["pj_per_us_proxy"] * 0.55
        update_day = 650.0 * update_factor
        fixed_day = 10_000.0 / util
        total = feature_day + audit_day * 0.82 + raw * per_req + update_day + fixed_day
        latency_us = row.feature_extraction_us + row.audit_logging_us * 0.82 + 0.22 + control_us(row.audit_control_scale) * 0.55
        mechanism = "programmable accelerator keeps software update path while reducing local compute and audit overhead"
    elif alternative == "hybrid_physicalized_safety_filter":
        fast_compute = c["local_dot"] * 0.18 + c["local_feature"] * 0.22
        fallback_compute = c["software_dot"] * 0.72 + c["offchip_feature"] * 0.60 + c["dispatch"]
        fail_safe = raw * row.fail_safe_fraction * c["dispatch"] * 0.5
        update_day = 4_000.0 * update_factor
        fixed_day = 42_000.0 / util
        control_day = c["control_day"]
        total = feature_day + audit_day + control_day + fast * fast_compute + fallback * fallback_compute + fail_safe + update_day + fixed_day
        latency_us = row.feature_extraction_us + row.audit_logging_us + control_us(row.audit_control_scale) + (
            (fast / accepted) * 0.08 + (fallback / accepted) * (p["python_dot_us"] * 0.72 + p["dispatch_us"])
            if accepted > 0
            else 0.0
        )
        mechanism = "hybrid only receives fixed-compute savings for effective accepted fast-path volume"
    else:
        raise ValueError(alternative)

    if raw <= 0 or accepted <= 0:
        energy = math.inf if total > 0 else 0.0
        latency_us = math.inf
    else:
        energy = total / accepted
    return ComparisonRow(
        scenario_id=row.scenario_id,
        alternative=alternative,
        raw_requests_per_day=round(raw, 6),
        effective_fast_path_requests_per_day=round(fast, 6),
        fallback_requests_per_day=round(fallback, 6),
        feature_extraction_cost_per_day_pj=round(feature_day, 6),
        audit_logging_cost_per_day_pj=round(audit_day, 6),
        update_control_cost_per_day_pj=round(update_day, 6),
        utilization_adjusted_fixed_substrate_cost_per_day_pj=round(fixed_day, 6),
        estimated_energy_per_accepted_request_pj=round(energy, 6) if math.isfinite(energy) else math.inf,
        estimated_latency_per_accepted_request_us=round(latency_us, 6) if math.isfinite(latency_us) else math.inf,
        total_daily_cost_proxy_pj=round(total, 6),
        winner=False,
        decision_class="indeterminate",
        mechanism_note=mechanism,
    )


def classify(row: WorkloadRow, winner: str) -> str:
    if row.raw_requests_per_day <= 0 or accepted_fast_path_requests(row) <= 0 or row.fallback_frequency >= 1.0:
        return "hybrid_falsified" if winner != "hybrid_physicalized_safety_filter" else "indeterminate"
    if row.update_interval_days <= 7 or row.utilization < 0.20:
        return "hybrid_falsified" if winner != "hybrid_physicalized_safety_filter" else "hybrid_weakened"
    if winner == "hybrid_physicalized_safety_filter":
        return "hybrid_preserved" if row.workload_classification == "preserved" else "hybrid_weakened"
    return DECISION_BY_WINNER[winner]


def evaluate_all(workloads: list[WorkloadRow], p: dict[str, float]) -> list[ComparisonRow]:
    out: list[ComparisonRow] = []
    for workload in workloads:
        scenario_rows = [cost_for(workload, alt, p) for alt in ALTERNATIVES]
        winner = min(scenario_rows, key=lambda r: r.total_daily_cost_proxy_pj).alternative
        decision = classify(workload, winner)
        for row in scenario_rows:
            out.append(
                ComparisonRow(
                    **{
                        **asdict(row),
                        "winner": row.alternative == winner,
                        "decision_class": decision if row.alternative == winner else "not_selected",
                    }
                )
            )
    return out


def threshold_rows(workloads: list[WorkloadRow], p: dict[str, float]) -> list[ThresholdRow]:
    rows: list[ThresholdRow] = []
    for workload in workloads:
        base = {alt: cost_for(workload, alt, p).total_daily_cost_proxy_pj for alt in ALTERNATIVES}
        hybrid = base["hybrid_physicalized_safety_filter"]
        best_baseline = min(base["optimized_software_runtime"], base["programmable_accelerator"])
        current_margin = best_baseline - hybrid
        rows.append(
            ThresholdRow(
                workload.scenario_id,
                "current_hybrid_margin_vs_best_baseline",
                0.0,
                str(round(current_margin, 6)),
                "pJ_equivalent/day",
                "positive means hybrid is cheaper; negative means the best programmable baseline already wins",
            )
        )
        erased_at = "not_erased_by_sweep"
        for savings in [i / 100 for i in range(int(workload.software_memory_savings * 100), 81)]:
            sw = cost_for(workload, "optimized_software_runtime", p, software_savings=savings).total_daily_cost_proxy_pj
            if sw <= hybrid:
                erased_at = f"{savings:.2f}"
                break
        rows.append(
            ThresholdRow(
                workload.scenario_id,
                "software_memory_savings_that_erases_hybrid",
                workload.software_memory_savings,
                erased_at,
                "fraction",
                "lowest tested software memory-savings fraction where optimized software matches or beats current hybrid",
            )
        )
        accel_at = "already_erased"
        if base["programmable_accelerator"] > hybrid:
            accel_at = "not_erased_by_0.25x_to_1.00x"
            for pct in range(100, 24, -1):
                mult = pct / 100
                acc = cost_for(workload, "programmable_accelerator", p, accel_multiplier=mult).total_daily_cost_proxy_pj
                if acc <= hybrid:
                    accel_at = f"{mult:.2f}"
                    break
        rows.append(
            ThresholdRow(
                workload.scenario_id,
                "accelerator_compute_multiplier_that_erases_hybrid",
                1.0,
                accel_at,
                "multiplier",
                "multiplier on accelerator compute energy; already_erased means accelerator wins at baseline strength",
            )
        )
    return rows


def write_csv(path: Path, rows: list[ComparisonRow]) -> None:
    fields = list(asdict(rows[0]).keys())
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            data = asdict(row)
            for key, value in list(data.items()):
                if isinstance(value, float) and math.isinf(value):
                    data[key] = "inf"
            writer.writerow(data)


def write_thresholds(rows: list[ThresholdRow]) -> None:
    with THRESHOLDS_CSV.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(asdict(rows[0]).keys()))
        writer.writeheader()
        for row in rows:
            writer.writerow(asdict(row))


def png_chunk(kind: bytes, data: bytes) -> bytes:
    return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)


def write_png(path: Path, rows: list[ComparisonRow]) -> None:
    width, height = 900, 460
    scenario_ids = []
    for row in rows:
        if row.scenario_id not in scenario_ids:
            scenario_ids.append(row.scenario_id)
    finite_costs = [row.total_daily_cost_proxy_pj for row in rows if row.raw_requests_per_day > 0]
    max_cost = max(finite_costs) if finite_costs else 1.0
    colors = {
        "optimized_software_runtime": (72, 115, 182),
        "programmable_accelerator": (70, 150, 90),
        "hybrid_physicalized_safety_filter": (190, 92, 70),
    }
    pixels = bytearray()
    for y in range(height):
        pixels.append(0)
        for x in range(width):
            color = (248, 248, 244)
            if 55 <= x <= 860 and y == 390:
                color = (70, 70, 70)
            if x == 55 and 45 <= y <= 390:
                color = (70, 70, 70)
            for i, sid in enumerate(scenario_ids):
                group_x = 75 + i * 80
                scenario_rows = [row for row in rows if row.scenario_id == sid]
                for j, row in enumerate(scenario_rows):
                    x0 = group_x + j * 18
                    x1 = x0 + 13
                    normalized = 0.0 if row.raw_requests_per_day <= 0 else math.log10(row.total_daily_cost_proxy_pj + 1.0) / math.log10(max_cost + 1.0)
                    bar_h = int(310 * min(max(normalized, 0.0), 1.0))
                    if x0 <= x <= x1 and 390 - bar_h <= y <= 390:
                        color = colors[row.alternative]
                    if row.winner and x0 <= x <= x1 and 390 - bar_h - 6 <= y < 390 - bar_h:
                        color = (20, 20, 20)
            pixels.extend(color)
    data = (
        b"\x89PNG\r\n\x1a\n"
        + png_chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
        + png_chunk(b"IDAT", zlib.compress(bytes(pixels), 9))
        + png_chunk(b"IEND", b"")
    )
    path.write_bytes(data)


def summary(workloads: list[WorkloadRow], rows: list[ComparisonRow], thresholds: list[ThresholdRow]) -> dict:
    winners = [row for row in rows if row.winner]
    counts = Counter(row.alternative for row in winners)
    decisions = Counter(row.decision_class for row in winners)
    preserved = next(row for row in winners if row.scenario_id == "high_volume_stable_moderation")
    preserved_thresholds = [asdict(row) for row in thresholds if row.scenario_id == "high_volume_stable_moderation"]
    cal_summary = json.loads(CAL_SUMMARY_JSON.read_text())
    return {
        "schema_version": 1,
        "milestone_id": "M-SWBASE-2",
        "status": "validated",
        "unit_metadata": {
            "cost_energy": "pJ_equivalent proxy",
            "latency": "microseconds per accepted request",
            "volume": "requests per day",
            "note": "feature extraction and audit logging are charged to every path under the same workload row",
        },
        "scenario_count": len(workloads),
        "winner_counts": dict(counts),
        "decision_class_counts": dict(decisions),
        "preserved_case_winner": preserved.alternative,
        "preserved_case_decision_class": preserved.decision_class,
        "preserved_case_total_daily_cost_proxy_pj": preserved.total_daily_cost_proxy_pj,
        "preserved_case_thresholds": preserved_thresholds,
        "calibrated_context": {
            "previous_safety_filter_decision": cal_summary["safety_filter_decision"],
            "calibrated_hybrid_winner_share": cal_summary["calibrated_hybrid_winner_share"],
        },
        "special_case_results": {
            row.scenario_id: row.decision_class
            for row in winners
            if row.scenario_id
            in {
                "zero_invocation_control",
                "fallback_all_control",
                "frequent_policy_update_regime",
                "multi_tenant_underutilized_deployment",
                "audit_heavy_regulated_deployment",
            }
        },
        "figure_caption": "per-scenario winner and normalized daily cost/energy comparison for optimized software, programmable accelerator, and hybrid physicalized safety filter under identical workload assumptions.",
    }


def write_report(rows: list[ComparisonRow], thresholds: list[ThresholdRow], doc: dict) -> None:
    winners = [row for row in rows if row.winner]
    preserved = next(row for row in winners if row.scenario_id == "high_volume_stable_moderation")
    margin = next(
        row.threshold_value
        for row in thresholds
        if row.scenario_id == "high_volume_stable_moderation" and row.threshold_name == "current_hybrid_margin_vs_best_baseline"
    )
    lines = [
        "---",
        "created: 2026-05-13T06:52:00Z",
        "cycle: 2",
        "run_id: run-2026-05-13T015136Z",
        "agent: worker",
        "milestone: M-SWBASE-2",
        "---",
        "",
        "# Stronger Baseline Comparison",
        "",
        "This comparison replays the exact `M-WORKLOAD-1` workload rows through three alternatives: optimized software/runtime, programmable accelerator, and the validated hybrid safety/filter fast path. Feature extraction, audit logging, raw volume, fallback frequency, update cadence, and utilization are held fixed per scenario.",
        "",
        f"Result: the single previously preserved workload is now `{preserved.decision_class}` with winner `{preserved.alternative}` and a daily hybrid margin of `{margin}` pJ-equivalent/day versus the best programmable baseline. A negative margin means the stronger programmable baseline has already erased the hybrid win; special controls also route away from hybrid.",
        "",
        "![per-scenario winner and normalized daily cost/energy comparison for optimized software, programmable accelerator, and hybrid physicalized safety filter under identical workload assumptions](../data/stronger_baseline_workload_comparison.png)",
        "",
        "## Scenario Winners",
        "",
        "| scenario | winner | decision | total daily cost proxy | energy/request | latency/request |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for row in winners:
        lines.append(
            f"| {row.scenario_id} | {row.alternative} | {row.decision_class} | {row.total_daily_cost_proxy_pj:.3f} | {row.estimated_energy_per_accepted_request_pj} | {row.estimated_latency_per_accepted_request_us} |"
        )
    lines.extend(
        [
            "",
            "## Threshold Readout",
            "",
            "The threshold table records the current hybrid margin, the software memory-savings level that would erase a current hybrid win, and the accelerator compute multiplier that would erase it. `already_erased` means a programmable baseline already wins at the modeled baseline strength.",
            "",
            "## Interpretation",
            "",
            "The prior preserved case was driven by high effective fast-path volume, low fallback rate, slow updates, and low audit/control overhead, but the stronger programmable accelerator baseline still beats it under equal workload accounting. This downgrades the safety/filter physicalization claim for this calibration cycle. Bursty, audit-heavy, frequent-update, all-fallback, zero-volume, and underutilized regimes also select software or the programmable accelerator.",
            "",
            "## Open Limits",
            "",
            "All costs are pJ-equivalent proxies tied to the existing calibration assumptions and local Python overhead probes. Production measurements of feature extraction, audit logging, fallback dispatch, and accelerator latency on the same request features would replace the largest modeled terms.",
            "",
        ]
    )
    REPORT_MD.write_text("\n".join(lines))


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    workloads = read_workloads()
    p = params()
    rows = evaluate_all(workloads, p)
    thresholds = threshold_rows(workloads, p)
    doc = summary(workloads, rows, thresholds)
    write_csv(COMPARISON_CSV, rows)
    write_thresholds(thresholds)
    SUMMARY_JSON.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n")
    write_png(COMPARISON_PNG, rows)
    write_report(rows, thresholds, doc)
    print(f"wrote {COMPARISON_CSV}")
    print(f"wrote {SUMMARY_JSON}")
    print(f"wrote {THRESHOLDS_CSV}")
    print(f"wrote {COMPARISON_PNG}")
    print(f"wrote {REPORT_MD}")
    print(f"preserved_case_winner: {doc['preserved_case_winner']}")


if __name__ == "__main__":
    main()
