# created: 2026-05-13T09:18:00Z
# cycle: 3
# run_id: run-2026-05-13T015136Z
# agent: worker
# milestone: M-REOPEN-1
"""Compute quantitative reopen thresholds for the downgraded safety/filter case."""

from __future__ import annotations

import csv
import json
import math
import struct
import zlib
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path

import stronger_baseline_model as sb


ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "physicalized-weights" / "data"
DOCS_DIR = ROOT / "physicalized-weights" / "docs"

STRONGER_COMPARISON_CSV = DATA_DIR / "stronger_baseline_comparison.csv"
STRONGER_SUMMARY_JSON = DATA_DIR / "stronger_baseline_summary.json"
WORKLOAD_OVERLAY_CSV = DATA_DIR / "workload_viability_overlay.csv"
TRACE_SCHEMA_JSON = DATA_DIR / "production_trace_schema.json"
LOCAL_OVERHEAD_SUMMARY_JSON = DATA_DIR / "local_overhead_summary.json"

OUTPUT_CSV = DATA_DIR / "reopen_thresholds.csv"
SUMMARY_JSON = DATA_DIR / "reopen_thresholds_summary.json"
OUTPUT_PNG = DATA_DIR / "reopen_thresholds_by_scenario.png"
REPORT_MD = DOCS_DIR / "reopen_thresholds.md"

HYBRID = "hybrid_physicalized_safety_filter"
BASELINES = ("optimized_software_runtime", "programmable_accelerator")
CURRENT_EVIDENCE_STATUS = "modeled_proxy_not_measured_production"


@dataclass(frozen=True)
class ReopenThresholdRow:
    scenario_id: str
    current_winner: str
    current_best_baseline: str
    hybrid_daily_cost_pj_equivalent: float
    best_baseline_daily_cost_pj_equivalent: float
    hybrid_margin_to_best_baseline_pj_equivalent_per_day: float
    required_hybrid_daily_reduction_to_tie_pj_equivalent_per_day: float
    required_hybrid_percent_reduction_to_tie: float | str
    required_best_baseline_daily_degradation_to_tie_pj_equivalent_per_day: float
    required_accepted_fast_path_multiplier_to_tie: float | str
    maximum_fallback_frequency_for_reopen: float | str
    maximum_audit_control_multiplier_for_reopen: float | str
    minimum_utilization_for_reopen: float | str
    reopen_class: str
    evidence_status: str
    threshold_unit: str
    trace_contract_requirement: str


def load_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def comparison_by_scenario() -> dict[str, dict[str, dict[str, str]]]:
    out: dict[str, dict[str, dict[str, str]]] = {}
    for row in load_csv_rows(STRONGER_COMPARISON_CSV):
        out.setdefault(row["scenario_id"], {})[row["alternative"]] = row
    return out


def overlay_by_scenario() -> dict[str, dict[str, str]]:
    return {row["scenario_id"]: row for row in load_csv_rows(WORKLOAD_OVERLAY_CSV)}


def finite(value: float | str) -> bool:
    return isinstance(value, float) and math.isfinite(value)


def round_or_label(value: float | str, digits: int = 6) -> float | str:
    if isinstance(value, str):
        return value
    if math.isinf(value) or math.isnan(value):
        return "not_finite"
    return round(value, digits)


def baseline_and_hybrid(rows: dict[str, dict[str, str]]) -> tuple[dict[str, str], dict[str, str], dict[str, str]]:
    hybrid = rows[HYBRID]
    baseline_rows = [rows[alt] for alt in BASELINES]
    best = min(baseline_rows, key=lambda r: float(r["total_daily_cost_proxy_pj"]))
    winner = min(rows.values(), key=lambda r: float(r["total_daily_cost_proxy_pj"]))
    return winner, best, hybrid


def per_request_delta_for_fast_path(workload: sb.WorkloadRow, p: dict[str, float]) -> float:
    c = sb.common_terms(workload, p)
    fast_compute = c["local_dot"] * 0.18 + c["local_feature"] * 0.22
    fallback_compute = c["software_dot"] * 0.72 + c["offchip_feature"] * 0.60 + c["dispatch"]
    return max(fallback_compute - fast_compute, 0.0)


def derive_fast_path_multiplier(delta: float, workload: sb.WorkloadRow, p: dict[str, float]) -> float | str:
    current_fast = sb.accepted_fast_path_requests(workload)
    raw = workload.raw_requests_per_day
    current_fallback = sb.fallback_requests(workload)
    if delta <= 0:
        return 1.0
    if current_fast <= 0 or raw <= 0:
        return "not_finite_no_accepted_fast_path_volume"
    per_shift_savings = per_request_delta_for_fast_path(workload, p)
    if per_shift_savings <= 0:
        return "not_derivable_no_positive_fast_path_savings"
    extra_fast_needed = delta / per_shift_savings
    if extra_fast_needed > current_fallback + 1e-9:
        return "not_finite_exceeds_fallback_pool"
    return (current_fast + extra_fast_needed) / current_fast


def derive_max_fallback_frequency(delta: float, workload: sb.WorkloadRow, p: dict[str, float]) -> float | str:
    if delta <= 0:
        return round(workload.fallback_frequency, 6)
    raw = workload.raw_requests_per_day
    current_fallback = sb.fallback_requests(workload)
    if raw <= 0 or sb.accepted_fast_path_requests(workload) <= 0:
        return "not_finite_no_volume"
    per_shift_savings = per_request_delta_for_fast_path(workload, p)
    if per_shift_savings <= 0:
        return "not_derivable_no_positive_fast_path_savings"
    fallback_reduction_needed = delta / per_shift_savings
    if fallback_reduction_needed > current_fallback + 1e-9:
        return "not_finite_requires_negative_fallback"
    return max((current_fallback - fallback_reduction_needed) / raw, 0.0)


def derive_max_audit_multiplier(delta: float, workload: sb.WorkloadRow, comparison: dict[str, dict[str, str]]) -> float | str:
    if delta <= 0:
        return 1.0
    hybrid_audit = float(comparison[HYBRID]["audit_logging_cost_per_day_pj"])
    baseline_audit = float(comparison["programmable_accelerator"]["audit_logging_cost_per_day_pj"])
    avoidable_audit_gap = max(hybrid_audit - baseline_audit, 0.0)
    if avoidable_audit_gap <= 0:
        return "not_derivable_no_hybrid_audit_excess"
    required_fraction = delta / avoidable_audit_gap
    if required_fraction > 1.0 + 1e-9:
        return "not_finite_requires_negative_audit_control"
    return max(1.0 - required_fraction, 0.0)


def derive_min_utilization(delta: float, workload: sb.WorkloadRow, comparison: dict[str, dict[str, str]]) -> float | str:
    if delta <= 0:
        return round(workload.utilization, 6)
    fixed_day = float(comparison[HYBRID]["utilization_adjusted_fixed_substrate_cost_per_day_pj"])
    if fixed_day <= 0 or workload.utilization <= 0:
        return "not_derivable_no_fixed_utilization_term"
    if delta > fixed_day + 1e-9:
        return "not_finite_fixed_cost_elimination_insufficient"
    target_fixed = fixed_day - delta
    if target_fixed <= 0:
        return "not_finite_requires_zero_fixed_cost"
    base_fixed_cost = fixed_day * workload.utilization
    required_util = base_fixed_cost / target_fixed
    if required_util > 1.0 + 1e-9:
        return "not_finite_above_full_utilization"
    return max(required_util, workload.utilization)


def classify_reopen(
    workload: sb.WorkloadRow,
    delta: float,
    winner: str,
    trace_schema: dict,
    local_summary: dict,
) -> str:
    accepted_fast = sb.accepted_fast_path_requests(workload)
    if workload.raw_requests_per_day <= 0:
        return "unreopenable_zero_volume"
    if accepted_fast <= 0 or workload.fallback_frequency >= 1.0:
        return "unreopenable_all_fallback"
    measured_energy_required = trace_schema["reopen_requirements"]["required_energy_status"] == "measured"
    production_energy_missing = local_summary["measurement_status"]["programmable_accelerator_energy"] != "measured"
    if measured_energy_required and production_energy_missing:
        if winner == HYBRID and delta < 0:
            return "blocked_by_missing_measured_trace"
        return "blocked_by_missing_measured_trace" if delta <= 0 else "finite_threshold"
    if winner == HYBRID and delta < 0:
        return "already_reopened"
    return "finite_threshold" if delta >= 0 else "indeterminate"


def build_rows() -> list[ReopenThresholdRow]:
    comparisons = comparison_by_scenario()
    overlay = overlay_by_scenario()
    strong_summary = json.loads(STRONGER_SUMMARY_JSON.read_text())
    trace_schema = json.loads(TRACE_SCHEMA_JSON.read_text())
    local_summary = json.loads(LOCAL_OVERHEAD_SUMMARY_JSON.read_text())
    workloads = {row.scenario_id: row for row in sb.read_workloads()}
    p = sb.params()
    if set(comparisons) != set(overlay) or set(comparisons) != set(workloads):
        raise ValueError("scenario sets differ across threshold inputs")
    if strong_summary["winner_counts"].get(HYBRID, 0) != 0:
        raise ValueError("M-REOPEN-1 expects the Phase 2 stronger-baseline hybrid win count to remain zero")

    rows: list[ReopenThresholdRow] = []
    for scenario_id in workloads:
        workload = workloads[scenario_id]
        winner, best, hybrid = baseline_and_hybrid(comparisons[scenario_id])
        hybrid_cost = float(hybrid["total_daily_cost_proxy_pj"])
        best_cost = float(best["total_daily_cost_proxy_pj"])
        delta = hybrid_cost - best_cost
        required_reduction = max(delta, 0.0)
        percent_reduction: float | str = required_reduction / hybrid_cost if hybrid_cost > 0 else "not_finite_zero_hybrid_cost"
        row = ReopenThresholdRow(
            scenario_id=scenario_id,
            current_winner=winner["alternative"],
            current_best_baseline=best["alternative"],
            hybrid_daily_cost_pj_equivalent=round(hybrid_cost, 6),
            best_baseline_daily_cost_pj_equivalent=round(best_cost, 6),
            hybrid_margin_to_best_baseline_pj_equivalent_per_day=round(delta, 6),
            required_hybrid_daily_reduction_to_tie_pj_equivalent_per_day=round(required_reduction, 6),
            required_hybrid_percent_reduction_to_tie=round_or_label(percent_reduction),
            required_best_baseline_daily_degradation_to_tie_pj_equivalent_per_day=round(required_reduction, 6),
            required_accepted_fast_path_multiplier_to_tie=round_or_label(
                derive_fast_path_multiplier(required_reduction, workload, p)
            ),
            maximum_fallback_frequency_for_reopen=round_or_label(
                derive_max_fallback_frequency(required_reduction, workload, p)
            ),
            maximum_audit_control_multiplier_for_reopen=round_or_label(
                derive_max_audit_multiplier(required_reduction, workload, comparisons[scenario_id])
            ),
            minimum_utilization_for_reopen=round_or_label(
                derive_min_utilization(required_reduction, workload, comparisons[scenario_id])
            ),
            reopen_class=classify_reopen(workload, delta, winner["alternative"], trace_schema, local_summary),
            evidence_status=CURRENT_EVIDENCE_STATUS,
            threshold_unit="pJ_equivalent/day for daily costs; fraction for percent/fallback/utilization; multiplier for multiplier fields",
            trace_contract_requirement="valid_reopen_candidate from M-TRACE-1 with measured hybrid and accelerator energy, measured baselines, nonzero accepted fast-path volume, audit logging, health/drift gates, and production or shadow-production environment",
        )
        rows.append(row)
    return rows


def write_csv(rows: list[ReopenThresholdRow]) -> None:
    fields = list(asdict(rows[0]).keys())
    with OUTPUT_CSV.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow(asdict(row))


def png_chunk(kind: bytes, data: bytes) -> bytes:
    return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)


def write_png(rows: list[ReopenThresholdRow]) -> None:
    width, height = 900, 460
    max_threshold = max(row.required_hybrid_daily_reduction_to_tie_pj_equivalent_per_day for row in rows) or 1.0
    pixels = bytearray()
    for y in range(height):
        pixels.append(0)
        for x in range(width):
            color = (248, 248, 244)
            if 60 <= x <= 850 and y == 390:
                color = (70, 70, 70)
            if x == 60 and 45 <= y <= 390:
                color = (70, 70, 70)
            for i, row in enumerate(rows):
                x0 = 82 + i * 78
                x1 = x0 + 34
                if row.reopen_class.startswith("unreopenable"):
                    bar_h = 46
                    bar_color = (120, 120, 120)
                else:
                    normalized = math.log10(row.required_hybrid_daily_reduction_to_tie_pj_equivalent_per_day + 1.0) / math.log10(max_threshold + 1.0)
                    bar_h = int(300 * max(0.0, min(normalized, 1.0)))
                    bar_color = (190, 92, 70) if row.current_best_baseline == "programmable_accelerator" else (72, 115, 182)
                if x0 <= x <= x1 and 390 - bar_h <= y <= 390:
                    color = bar_color
                if row.reopen_class == "blocked_by_missing_measured_trace" and x0 <= x <= x1 and 390 - bar_h - 7 <= y < 390 - bar_h:
                    color = (35, 35, 35)
            if 640 <= x <= 850 and 54 <= y <= 126:
                if y in (54, 126) or x in (640, 850):
                    color = (80, 80, 80)
                elif 654 <= x <= 672 and 70 <= y <= 88:
                    color = (190, 92, 70)
                elif 654 <= x <= 672 and 98 <= y <= 116:
                    color = (120, 120, 120)
            pixels.extend(color)
    data = (
        b"\x89PNG\r\n\x1a\n"
        + png_chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
        + png_chunk(b"IDAT", zlib.compress(bytes(pixels), 9))
        + png_chunk(b"IEND", b"")
    )
    OUTPUT_PNG.write_bytes(data)


def summarize(rows: list[ReopenThresholdRow]) -> dict:
    classes = Counter(row.reopen_class for row in rows)
    current_hybrid_wins = sum(1 for row in rows if row.current_winner == HYBRID)
    finite = [
        row
        for row in rows
        if row.reopen_class in {"finite_threshold", "blocked_by_missing_measured_trace"}
        and row.required_hybrid_daily_reduction_to_tie_pj_equivalent_per_day >= 0
    ]
    high_volume = next(row for row in rows if row.scenario_id == "high_volume_stable_moderation")
    return {
        "schema_version": 1,
        "milestone_id": "M-REOPEN-1",
        "status": "validated",
        "scenario_count": len(rows),
        "current_hybrid_wins": current_hybrid_wins,
        "reopen_class_counts": dict(classes),
        "evidence_status": CURRENT_EVIDENCE_STATUS,
        "threshold_inequality": "measured_hybrid_total < measured_best_programmable_baseline under identical accepted-volume, fallback, audit, update, utilization, latency, and energy accounting",
        "trace_contract": "Only M-TRACE-1 valid_reopen_candidate traces with measured accelerator and hybrid energy can instantiate the threshold.",
        "high_volume_stable_moderation": asdict(high_volume),
        "finite_threshold_count": len(finite),
        "max_required_hybrid_reduction_pj_equivalent_per_day": max(
            row.required_hybrid_daily_reduction_to_tie_pj_equivalent_per_day for row in rows
        ),
        "unit_metadata": {
            "daily_cost": "pJ_equivalent/day",
            "percent_reduction": "fraction",
            "fallback_frequency": "fraction of raw requests",
            "utilization": "fraction",
            "multiplier": "unitless multiplier",
            "note": "Current rows are modeled/proxy thresholds, not measured production reopen evidence.",
        },
        "special_case_conclusions": {
            "zero_invocation_control": next(row.reopen_class for row in rows if row.scenario_id == "zero_invocation_control"),
            "fallback_all_control": next(row.reopen_class for row in rows if row.scenario_id == "fallback_all_control"),
            "proxy_only_trace": "blocked; proxy energy cannot satisfy M-TRACE-1 measured-energy requirement",
            "missing_accelerator_baseline": "blocked; best programmable baseline cannot be formed",
            "failed_health_drift_audit_gates": "blocked; no accepted fast-path credit",
        },
        "figure_caption": "per-scenario reduction or baseline-degradation threshold required to overturn the stronger programmable baseline, with unreopenable zero-volume/all-fallback regimes separated.",
    }


def write_report(rows: list[ReopenThresholdRow], summary: dict) -> None:
    high = summary["high_volume_stable_moderation"]
    lines = [
        "---",
        "created: 2026-05-13T09:18:00Z",
        "cycle: 3",
        "run_id: run-2026-05-13T015136Z",
        "agent: worker",
        "milestone: M-REOPEN-1",
        "---",
        "",
        "# Reopen Thresholds",
        "",
        "A production trace can reopen the downgraded safety/filter performance claim only if:",
        "",
        "`measured_hybrid_total < measured_best_programmable_baseline`",
        "",
        "The comparison must use identical accepted-volume, fallback, audit, update, utilization, latency, and energy accounting. Current modeled/proxy rows do not reopen the claim; they only quantify how far measured production evidence would have to move.",
        "",
        "![per-scenario reduction or baseline-degradation threshold required to overturn the stronger programmable baseline, with unreopenable zero-volume/all-fallback regimes separated](../data/reopen_thresholds_by_scenario.png)",
        "",
        "## Terms and Units",
        "",
        "- `measured_hybrid_total`: daily pJ-equivalent production cost for the hybrid fast path plus feature extraction, audit/control, fallback, update, fixed substrate, and utilization terms.",
        "- `measured_best_programmable_baseline`: lower daily pJ-equivalent production cost of optimized software/runtime and programmable accelerator under the same request stream.",
        "- `hybrid_margin_to_best_baseline`: `hybrid_total - best_baseline_total`; positive means the programmable baseline still wins.",
        "- `required_hybrid_daily_reduction_to_tie`: positive margin the hybrid must remove to tie the best baseline.",
        "- `required_best_baseline_daily_degradation_to_tie`: equal positive margin by which measured baseline cost would have to worsen.",
        "- `required_accepted_fast_path_multiplier_to_tie`: fast-path volume multiplier when the current fallback pool can be shifted to accepted fast-path traffic; otherwise reported as non-finite.",
        "- `maximum_fallback_frequency_for_reopen`, `maximum_audit_control_multiplier_for_reopen`, and `minimum_utilization_for_reopen`: one-variable thresholds holding other modeled terms fixed; non-finite labels mean that knob alone cannot close the gap.",
        "",
        "## Special Cases",
        "",
        "- Zero accepted fast-path volume: no reopen because the fixed path receives no useful credit.",
        "- All fallback: no reopen because accepted fast-path volume is zero.",
        "- Proxy-only energy: no reopen because M-TRACE-1 requires measured hybrid and accelerator energy.",
        "- Missing accelerator baseline: no reopen because the best programmable baseline is undefined.",
        "- Failed health, drift, or audit gates: no accepted fast-path credit.",
        "",
        "## Current Threshold Readout",
        "",
        f"The formerly preserved `high_volume_stable_moderation` scenario requires `{high['required_hybrid_daily_reduction_to_tie_pj_equivalent_per_day']}` pJ-equivalent/day of hybrid reduction, or the same degradation in the best programmable baseline, before it can tie. Its current best baseline remains `{high['current_best_baseline']}` and the current evidence status is `{CURRENT_EVIDENCE_STATUS}`.",
        "",
        "| scenario | class | best baseline | required reduction pJ-eq/day | fast-path multiplier | max fallback | min utilization |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            f"| {row.scenario_id} | {row.reopen_class} | {row.current_best_baseline} | {row.required_hybrid_daily_reduction_to_tie_pj_equivalent_per_day} | {row.required_accepted_fast_path_multiplier_to_tie} | {row.maximum_fallback_frequency_for_reopen} | {row.minimum_utilization_for_reopen} |"
        )
    lines.extend(
        [
            "",
            "## Future Trace Evaluation",
            "",
            "A future serving trace must first pass the M-TRACE-1 validator as `valid_reopen_candidate`. Then the measured trace totals replace the proxy/model terms in this threshold table. If the measured hybrid margin is still positive, the claim remains downgraded; if it is negative under identical accounting, the safety/filter performance claim can be reopened for that scenario only.",
            "",
            "## Limits",
            "",
            "The table is a threshold contract, not new hardware evidence. It keeps Phase 2 stronger-baseline semantics fixed and deliberately does not classify modeled, synthetic, proxy-only, zero-volume, all-fallback, or missing-baseline evidence as reopened.",
            "",
        ]
    )
    REPORT_MD.write_text("\n".join(lines))


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    rows = build_rows()
    write_csv(rows)
    write_png(rows)
    summary = summarize(rows)
    SUMMARY_JSON.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    write_report(rows, summary)
    print(f"wrote {OUTPUT_CSV}")
    print(f"wrote {SUMMARY_JSON}")
    print(f"wrote {OUTPUT_PNG}")
    print(f"wrote {REPORT_MD}")
    print(f"current_hybrid_wins: {summary['current_hybrid_wins']}")
    print(f"reopen_class_counts: {summary['reopen_class_counts']}")


if __name__ == "__main__":
    main()
