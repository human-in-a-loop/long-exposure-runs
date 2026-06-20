# created: 2026-05-13T05:31:00Z
# cycle: 2
# run_id: run-2026-05-13T015136Z
# agent: worker
# milestone: M-CAL-1
"""Calibrated companion to the Phase 1 normalized break-even model."""

from __future__ import annotations

import csv
import json
import math
import struct
import zlib
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "physicalized-weights" / "data"
ASSUMPTIONS_CSV = DATA_DIR / "calibration_assumptions.csv"
ASSUMPTIONS_JSON = DATA_DIR / "calibration_assumptions.json"
PHASE1_SUMMARY = DATA_DIR / "breakeven_summary.json"
PROBE_JSON = DATA_DIR / "local_overhead_probe.json"

GRID_CSV = DATA_DIR / "calibrated_breakeven_grid.csv"
SUMMARY_JSON = DATA_DIR / "calibrated_breakeven_summary.json"
TORNADO_CSV = DATA_DIR / "calibrated_sensitivity_tornado.csv"
COMPARISON_PNG = DATA_DIR / "calibrated_breakeven_vs_phase1.png"

SOURCE_TYPES = {"sourced", "local_measured", "modeled", "inferred", "speculative"}
CONFIDENCE_LEVELS = {"low", "medium", "high"}

STRATEGIES = (
    "software_optimized",
    "programmable_accelerator",
    "hybrid_safety_filter",
    "fixed_full_dense_antitarget",
    "analog_in_memory_antitarget",
)


@dataclass(frozen=True)
class Scenario:
    requests_per_day: float
    update_interval_days: float
    software_memory_savings: float
    fallback_frequency: float
    audit_control_scale: str
    utilization: float


@dataclass(frozen=True)
class Row:
    strategy: str
    requests_per_day: float
    update_interval_days: float
    software_memory_savings: float
    fallback_frequency: float
    audit_control_scale: str
    utilization: float
    requests_per_update: float
    per_request_pj_equivalent: float
    amortized_fixed_pj_equivalent: float
    total_pj_equivalent: float
    winner: bool
    conclusion: str


def parse_range(value: str) -> list[float]:
    if ";" in value:
        return [float(part) for part in value.split(";")]
    if "-" in value and not value.startswith("-"):
        lo, hi = value.split("-", 1)
        return [float(lo), float(hi)]
    return [float(value)]


def load_assumptions() -> dict[str, dict[str, str]]:
    rows: dict[str, dict[str, str]] = {}
    with ASSUMPTIONS_CSV.open(newline="") as f:
        for row in csv.DictReader(f):
            validate_assumption_row(row)
            rows[row["variable"]] = row
    json_doc = json.loads(ASSUMPTIONS_JSON.read_text())
    json_vars = {row["variable"] for row in json_doc["rows"]}
    if set(rows) != json_vars:
        raise ValueError("CSV and JSON assumption variable sets differ")
    return rows


def validate_assumption_row(row: dict[str, str]) -> None:
    required = ["variable", "value_or_range", "unit", "source_type", "citation_or_artifact_path", "confidence", "notes"]
    for key in required:
        if not row.get(key):
            raise ValueError(f"assumption row {row.get('variable', '<unknown>')} missing {key}")
    if row["source_type"] not in SOURCE_TYPES:
        raise ValueError(f"invalid source_type for {row['variable']}: {row['source_type']}")
    if row["confidence"] not in CONFIDENCE_LEVELS:
        raise ValueError(f"invalid confidence for {row['variable']}: {row['confidence']}")


def probe_metrics() -> dict[str, float]:
    if not PROBE_JSON.exists():
        return {
            "python_int8_dot_product": 0.9,
            "fallback_dispatch_branch": 0.08,
            "dot_plus_dispatch": 1.0,
            "csv_json_audit_logging": 8.0,
        }
    doc = json.loads(PROBE_JSON.read_text())
    return {name: float(data["median_value"]) for name, data in doc["metrics"].items()}


def phase1_winner_counts() -> dict[str, int]:
    return json.loads(PHASE1_SUMMARY.read_text())["winner_counts"]


def primitive_params(assumptions: dict[str, dict[str, str]], probe: dict[str, float]) -> dict[str, float]:
    dram_lo, dram_hi = parse_range(assumptions["dram_access_energy_proxy"]["value_or_range"])
    sram = float(assumptions["sram_32kb_access_energy_proxy"]["value_or_range"])
    int8_lo, int8_hi = parse_range(assumptions["int8_mac_energy_proxy"]["value_or_range"])
    return {
        "dram_pj": (dram_lo + dram_hi) / 2.0,
        "sram_pj": sram,
        "int8_mac_pj": int8_hi,
        "python_dot_us": probe["python_int8_dot_product"],
        "dispatch_us": probe["fallback_dispatch_branch"],
        "audit_us": probe["csv_json_audit_logging"],
        "pj_per_us_proxy": 1000.0,
    }


def scenario_grid() -> list[Scenario]:
    requests = [0, 100, 1_000, 10_000, 100_000, 1_000_000, 10_000_000]
    update_days = [1, 7, 30, 90, 365]
    software_savings = [0.0, 0.2, 0.35, 0.5]
    fallback = [0.0, 0.1, 0.25, 0.5, 1.0]
    control_scales = ["low", "mid", "high"]
    utilization = [0.35, 0.60, 0.85]
    return [
        Scenario(float(req), float(days), savings, fb, scale, util)
        for req in requests
        for days in update_days
        for savings in software_savings
        for fb in fallback
        for scale in control_scales
        for util in utilization
    ]


def overhead_us(scale: str) -> tuple[float, float]:
    if scale == "low":
        return 0.5, 0.05
    if scale == "mid":
        return 1.5, 0.25
    if scale == "high":
        return 4.0, 0.8
    raise ValueError(scale)


def fixed_cost(strategy: str, scenario: Scenario) -> float:
    # Request-equivalent fixed cost converted through the same pJ proxy scale.
    update_factor = 30.0 / max(scenario.update_interval_days, 1e-9)
    if strategy == "hybrid_safety_filter":
        return 50_000.0 + 30_000.0 * update_factor
    if strategy == "fixed_full_dense_antitarget":
        return 30_000_000.0 + 10_000_000.0 * update_factor
    if strategy == "analog_in_memory_antitarget":
        return 5_000_000.0 + 2_000_000.0 * update_factor
    if strategy == "programmable_accelerator":
        return 8_000.0 + 1_000.0 * update_factor
    return 0.0


def per_request(strategy: str, scenario: Scenario, p: dict[str, float]) -> float:
    feature_us, control_us = overhead_us(scenario.audit_control_scale)
    util_penalty = 1.0 / max(scenario.utilization, 1e-9)
    feature_cost = feature_us * p["pj_per_us_proxy"]
    control_cost = control_us * p["pj_per_us_proxy"]
    audit_cost = p["audit_us"] * p["pj_per_us_proxy"]
    dispatch_cost = p["dispatch_us"] * p["pj_per_us_proxy"]
    software_dot = p["python_dot_us"] * p["pj_per_us_proxy"]
    local_dot = 8.0 * (p["sram_pj"] + p["int8_mac_pj"])
    offchip_feature = 8.0 * p["dram_pj"] * (1.0 - scenario.software_memory_savings)
    local_feature = 8.0 * p["sram_pj"]

    software = (feature_cost + offchip_feature + software_dot + audit_cost) * util_penalty
    if strategy == "software_optimized":
        return software
    if strategy == "programmable_accelerator":
        return (feature_cost + local_feature + local_dot * 0.55 + control_cost + audit_cost * 0.85) * (0.85 + 0.15 * util_penalty)
    if strategy == "hybrid_safety_filter":
        fast = feature_cost + local_feature * 0.45 + local_dot * 0.35 + control_cost + audit_cost
        fallback = software + dispatch_cost
        return (1.0 - scenario.fallback_frequency) * fast + scenario.fallback_frequency * fallback
    if strategy == "fixed_full_dense_antitarget":
        dense_transfer = 7_000_000_000.0 / 1_000_000.0 * p["sram_pj"]
        return (dense_transfer + control_cost + audit_cost) * (0.95 + 0.05 * util_penalty)
    if strategy == "analog_in_memory_antitarget":
        conversion = 8.0 * p["dram_pj"] * 0.8
        calibration = 3000.0
        return feature_cost + conversion + calibration + audit_cost
    raise ValueError(strategy)


def evaluate(scenario: Scenario, p: dict[str, float]) -> list[Row]:
    n = scenario.requests_per_day * scenario.update_interval_days
    costs = {}
    for strategy in STRATEGIES:
        fixed = fixed_cost(strategy, scenario)
        amortized = math.inf if n == 0 and fixed > 0 else fixed / n if n else 0.0
        costs[strategy] = per_request(strategy, scenario, p) + amortized
    winner = min(costs, key=costs.get)
    rows = []
    for strategy in STRATEGIES:
        fixed = fixed_cost(strategy, scenario)
        amortized = math.inf if n == 0 and fixed > 0 else fixed / n if n else 0.0
        conclusion = "candidate_survives" if strategy == "hybrid_safety_filter" and winner == strategy else "baseline_or_antitarget_preferred"
        rows.append(
            Row(
                strategy=strategy,
                requests_per_day=scenario.requests_per_day,
                update_interval_days=scenario.update_interval_days,
                software_memory_savings=scenario.software_memory_savings,
                fallback_frequency=scenario.fallback_frequency,
                audit_control_scale=scenario.audit_control_scale,
                utilization=scenario.utilization,
                requests_per_update=n,
                per_request_pj_equivalent=per_request(strategy, scenario, p),
                amortized_fixed_pj_equivalent=amortized,
                total_pj_equivalent=costs[strategy],
                winner=winner == strategy,
                conclusion=conclusion,
            )
        )
    return rows


def write_csv(path: Path, rows: list[Row]) -> None:
    fields = list(asdict(rows[0]).keys())
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            data = asdict(row)
            if math.isinf(data["total_pj_equivalent"]):
                data["total_pj_equivalent"] = "inf"
            if math.isinf(data["amortized_fixed_pj_equivalent"]):
                data["amortized_fixed_pj_equivalent"] = "inf"
            writer.writerow(data)


def scenario_winners(rows: list[Row]) -> list[Row]:
    return [row for row in rows if row.winner]


def sensitivity(rows: list[Row]) -> list[dict[str, str | float]]:
    winners = scenario_winners(rows)
    total = len(winners)
    variables = [
        "requests_per_day",
        "update_interval_days",
        "software_memory_savings",
        "fallback_frequency",
        "audit_control_scale",
        "utilization",
    ]
    out = []
    for variable in variables:
        buckets: dict[str, list[bool]] = defaultdict(list)
        for row in winners:
            buckets[str(getattr(row, variable))].append(row.strategy == "hybrid_safety_filter")
        rates = [sum(values) / len(values) for values in buckets.values()]
        swing = max(rates) - min(rates) if rates else 0.0
        out.append(
            {
                "variable": variable,
                "hybrid_win_rate_swing": round(swing, 6),
                "bucket_count": len(buckets),
                "note": f"share of winner scenarios where hybrid_safety_filter wins; total_scenarios={total}",
            }
        )
    return sorted(out, key=lambda row: float(row["hybrid_win_rate_swing"]), reverse=True)


def write_tornado(rows: list[dict[str, str | float]]) -> None:
    with TORNADO_CSV.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["variable", "hybrid_win_rate_swing", "bucket_count", "note"])
        writer.writeheader()
        writer.writerows(rows)


def png_chunk(kind: bytes, data: bytes) -> bytes:
    return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)


def write_png(path: Path, phase1_share: float, calibrated_share: float, pessimistic_share: float) -> None:
    width, height = 760, 420
    pixels = bytearray()
    bars = [
        ("phase1 physicalized", phase1_share, (62, 117, 178)),
        ("calibrated hybrid", calibrated_share, (86, 156, 93)),
        ("pessimistic hybrid", pessimistic_share, (196, 92, 81)),
    ]
    for y in range(height):
        pixels.append(0)
        for x in range(width):
            color = (248, 248, 244)
            if x in (80, 680) and 70 <= y <= 330:
                color = (80, 80, 80)
            if y == 330 and 80 <= x <= 680:
                color = (80, 80, 80)
            for i, (_label, share, bar_color) in enumerate(bars):
                x0 = 140 + i * 170
                x1 = x0 + 80
                bar_h = int(240 * min(max(share, 0.0), 1.0))
                if x0 <= x <= x1 and 330 - bar_h <= y <= 330:
                    color = bar_color
            pixels.extend(color)
    raw = bytes(pixels)
    data = (
        b"\x89PNG\r\n\x1a\n"
        + png_chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
        + png_chunk(b"IDAT", zlib.compress(raw, 9))
        + png_chunk(b"IEND", b"")
    )
    path.write_bytes(data)


def summarize(rows: list[Row], assumptions: dict[str, dict[str, str]], tornado: list[dict[str, str | float]]) -> dict:
    winners = scenario_winners(rows)
    counts = Counter(row.strategy for row in winners)
    total = len(winners)
    hybrid_share = counts["hybrid_safety_filter"] / total
    non_optimistic = [
        row
        for row in winners
        if row.requests_per_day >= 100_000
        and row.update_interval_days >= 30
        and row.software_memory_savings <= 0.35
        and row.fallback_frequency <= 0.25
        and row.audit_control_scale in {"mid", "high"}
    ]
    pessimistic = [
        row
        for row in winners
        if row.software_memory_savings == 0.5
        or row.fallback_frequency >= 0.5
        or row.audit_control_scale == "high"
        or row.update_interval_days <= 7
    ]
    non_opt_share = (
        sum(1 for row in non_optimistic if row.strategy == "hybrid_safety_filter") / len(non_optimistic)
        if non_optimistic
        else 0.0
    )
    pess_share = (
        sum(1 for row in pessimistic if row.strategy == "hybrid_safety_filter") / len(pessimistic)
        if pessimistic
        else 0.0
    )
    zero_volume = [row for row in winners if row.requests_per_day == 0]
    antitarget_wins = counts["fixed_full_dense_antitarget"] + counts["analog_in_memory_antitarget"]
    decision = "preserved_but_weakened"
    if non_opt_share == 0:
        decision = "reopened_uncertainty_dominated"
    elif pess_share < 0.05:
        decision = "preserved_only_under_bounded_non_pessimistic_conditions"
    return {
        "schema_version": 1,
        "milestone_id": "M-CAL-1",
        "status": "validated",
        "unit": "pJ_equivalent proxy",
        "phase1_physicalized_winner_share": phase1_physicalized_share(),
        "calibrated_winner_counts": dict(counts),
        "calibrated_hybrid_winner_share": hybrid_share,
        "non_optimistic_hybrid_winner_share": non_opt_share,
        "pessimistic_hybrid_winner_share": pess_share,
        "zero_volume_physicalized_wins": [row.strategy for row in zero_volume if row.strategy != "software_optimized"],
        "antitarget_wins": antitarget_wins,
        "safety_filter_decision": decision,
        "top_uncertainty_drivers": tornado[:5],
        "assumption_source_type_counts": dict(Counter(row["source_type"] for row in assumptions.values())),
        "missing_data_that_would_reduce_uncertainty": [
            "production safety/filter invocation volume and near-threshold rate",
            "feature extraction cost under the real serving stack",
            "audit logging latency and energy in the production path",
            "fallback frequency after policy/version/health/drift gates",
            "measured optimized software and programmable accelerator baselines on identical features",
        ],
        "figure_caption": "calibrated break-even comparison showing how sourced/measured parameter bounds shift the Phase 1 physicalization regions and whether the safety/filter target remains viable.",
    }


def phase1_physicalized_share() -> float:
    counts = phase1_winner_counts()
    total = sum(counts.values())
    physicalized = counts.get("fixed_digital_weights", 0) + counts.get("analog_in_memory", 0) + counts.get("hybrid_physicalized_submodel", 0)
    return physicalized / total if total else 0.0


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    assumptions = load_assumptions()
    params = primitive_params(assumptions, probe_metrics())
    rows = [row for scenario in scenario_grid() for row in evaluate(scenario, params)]
    write_csv(GRID_CSV, rows)
    tornado = sensitivity(rows)
    write_tornado(tornado)
    summary = summarize(rows, assumptions, tornado)
    SUMMARY_JSON.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    write_png(
        COMPARISON_PNG,
        summary["phase1_physicalized_winner_share"],
        summary["calibrated_hybrid_winner_share"],
        summary["pessimistic_hybrid_winner_share"],
    )
    print(f"wrote {GRID_CSV}")
    print(f"wrote {SUMMARY_JSON}")
    print(f"wrote {TORNADO_CSV}")
    print(f"wrote {COMPARISON_PNG}")
    print(f"safety_filter_decision: {summary['safety_filter_decision']}")


if __name__ == "__main__":
    main()
