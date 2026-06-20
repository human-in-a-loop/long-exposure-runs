# created: 2026-05-13T08:04:00Z
# cycle: 3
# run_id: run-2026-05-13T015136Z
# agent: worker
# milestone: M-MEASURE-1
"""Deterministic local timing proxy harness for safety-filter overheads.

The emitted timing values are host/Python latency proxies only. Production
accelerator energy, utilization, batching, and failure behavior remain
explicit measurement gaps.
"""

from __future__ import annotations

import csv
import json
import math
import random
import statistics
import struct
import time
import zlib
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "physicalized-weights" / "data"
DOCS_DIR = ROOT / "physicalized-weights" / "docs"

WORKLOAD_CSV = DATA_DIR / "workload_scenarios.csv"
BENCHMARK_CSV = DATA_DIR / "local_overhead_benchmark.csv"
SUMMARY_JSON = DATA_DIR / "local_overhead_summary.json"
GAP_MATRIX_CSV = DATA_DIR / "measurement_gap_matrix.csv"
LATENCY_PNG = DATA_DIR / "local_overhead_latency_distribution.png"
REPORT_MD = DOCS_DIR / "production_measurement_requirements.md"
AUDIT_SCRATCH = DATA_DIR / "local_overhead_benchmark_audit.jsonl"

SEED = 20260513
TRIALS = 7
WEIGHTS = [12, -7, 5, 9, -11, 4, 6, -3]
COMPONENTS = (
    "feature_extraction_proxy",
    "fixed_classifier_proxy",
    "optimized_software_classifier_proxy",
    "route_fallback_decision_proxy",
    "audit_serialization_proxy",
    "append_only_audit_write_proxy",
)


@dataclass(frozen=True)
class Workload:
    scenario_id: str
    raw_requests_per_day: float
    effective_fast_path_requests_per_day: float
    fallback_frequency: float
    near_threshold_frequency: float
    update_interval_days: float
    audit_control_scale: str
    utilization: float
    feature_extraction_us: float
    audit_logging_us: float
    software_memory_savings: float


def read_workloads() -> list[Workload]:
    with WORKLOAD_CSV.open(newline="") as f:
        return [
            Workload(
                scenario_id=row["scenario_id"],
                raw_requests_per_day=float(row["raw_requests_per_day"]),
                effective_fast_path_requests_per_day=float(row["effective_fast_path_requests_per_day"]),
                fallback_frequency=float(row["fallback_frequency"]),
                near_threshold_frequency=float(row["near_threshold_frequency"]),
                update_interval_days=float(row["update_interval_days"]),
                audit_control_scale=row["audit_control_scale"],
                utilization=float(row["utilization"]),
                feature_extraction_us=float(row["feature_extraction_us"]),
                audit_logging_us=float(row["audit_logging_us"]),
                software_memory_savings=float(row["software_memory_savings"]),
            )
            for row in csv.DictReader(f)
        ]


def feature_length(row: Workload) -> int:
    if row.raw_requests_per_day <= 0:
        return 0
    scale = {"low": 0, "mid": 4, "high": 12}[row.audit_control_scale]
    return int(8 + scale + min(24, round(row.near_threshold_frequency * 24)))


def sample_count(row: Workload) -> int:
    if row.raw_requests_per_day <= 0:
        return 0
    return max(24, min(128, int(row.raw_requests_per_day // 10_000) + 24))


def build_requests(row: Workload) -> list[dict[str, object]]:
    count = sample_count(row)
    length = feature_length(row)
    rng = random.Random(f"{SEED}:{row.scenario_id}")
    requests = []
    for idx in range(count):
        fallback = row.fallback_frequency >= 1.0 or rng.random() < row.fallback_frequency
        near_threshold = rng.random() < row.near_threshold_frequency
        base = 7 if near_threshold else rng.randint(-16, 16)
        features = [((base + idx * 3 + j * 5 + rng.randint(-2, 2)) % 33) - 16 for j in range(length)]
        requests.append(
            {
                "request_id": f"{row.scenario_id}-{idx:04d}",
                "features": features,
                "near_threshold": near_threshold,
                "force_fallback": fallback,
                "audit_level": row.audit_control_scale,
            }
        )
    return requests


def extract_features(request: dict[str, object], length: int) -> list[int]:
    payload = request["request_id"] + ":" + request["audit_level"]
    acc = sum(ord(ch) for ch in str(payload))
    return [((acc + i * 17 + length * 3) % 63) - 31 for i in range(length)]


def fixed_classifier(features: list[int]) -> tuple[int, str, int]:
    if not features:
        return -10, "allow", 74
    score = -10 + sum(value * WEIGHTS[i % len(WEIGHTS)] for i, value in enumerate(features[:16]))
    decision = "block" if score >= 64 else "allow"
    return score, decision, abs(score - 64)


def optimized_software_classifier(features: list[int]) -> tuple[int, str, int]:
    score, _decision, _margin = fixed_classifier(features)
    adjusted = score + sum((value * value) % 11 for value in features[:24]) - len(features)
    decision = "block" if adjusted >= 64 else "allow"
    return adjusted, decision, abs(adjusted - 64)


def route_decision(request: dict[str, object], score: int, margin: int) -> str:
    if request["force_fallback"] or request["near_threshold"] or margin < 16:
        return "programmable_fallback"
    return "physicalized_fast_path" if score >= 64 else "physicalized_fast_path"


def audit_row(request: dict[str, object], score: int, route: str) -> dict[str, object]:
    return {
        "request_id": request["request_id"],
        "score": score,
        "route": route,
        "audit_level": request["audit_level"],
        "feature_count": len(request["features"]),
    }


def time_component(component: str, requests: list[dict[str, object]], length: int) -> float:
    if not requests:
        return math.nan
    start = time.perf_counter_ns()
    if component == "feature_extraction_proxy":
        for request in requests:
            extract_features(request, length)
    elif component == "fixed_classifier_proxy":
        for request in requests:
            fixed_classifier(request["features"])
    elif component == "optimized_software_classifier_proxy":
        for request in requests:
            optimized_software_classifier(request["features"])
    elif component == "route_fallback_decision_proxy":
        for request in requests:
            score, _decision, margin = fixed_classifier(request["features"])
            route_decision(request, score, margin)
    elif component == "audit_serialization_proxy":
        for request in requests:
            score, _decision, margin = fixed_classifier(request["features"])
            json.dumps(audit_row(request, score, route_decision(request, score, margin)), sort_keys=True, separators=(",", ":"))
    elif component == "append_only_audit_write_proxy":
        with AUDIT_SCRATCH.open("a") as f:
            for request in requests:
                score, _decision, margin = fixed_classifier(request["features"])
                row = audit_row(request, score, route_decision(request, score, margin))
                f.write(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n")
    else:
        raise ValueError(component)
    return (time.perf_counter_ns() - start) / len(requests)


def summarize(samples: list[float]) -> dict[str, float]:
    valid = [sample for sample in samples if not math.isnan(sample)]
    if not valid:
        return {"median": math.nan, "p10": math.nan, "p90": math.nan, "mean": math.nan}
    ordered = sorted(valid)
    return {
        "median": statistics.median(ordered),
        "p10": ordered[max(0, int((len(ordered) - 1) * 0.10))],
        "p90": ordered[min(len(ordered) - 1, int(math.ceil((len(ordered) - 1) * 0.90)))],
        "mean": statistics.mean(ordered),
    }


def format_float(value: float) -> str:
    return "" if math.isnan(value) else f"{value:.3f}"


def benchmark_rows() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for workload in read_workloads():
        requests = build_requests(workload)
        length = feature_length(workload)
        accepted_fast_path_credit = (
            0.0
            if workload.raw_requests_per_day <= 0 or workload.fallback_frequency >= 1.0
            else workload.effective_fast_path_requests_per_day
        )
        for component in COMPONENTS:
            samples = [time_component(component, requests, length) for _ in range(TRIALS)]
            stats = summarize(samples)
            measurement_status = "not_measured_zero_volume" if not requests else "locally_measured_proxy"
            rows.append(
                {
                    "scenario_id": workload.scenario_id,
                    "component": component,
                    "measurement_status": measurement_status,
                    "sample_count": str(len(requests)),
                    "feature_length": str(length),
                    "fallback_frequency": f"{workload.fallback_frequency:.6f}",
                    "near_threshold_frequency": f"{workload.near_threshold_frequency:.6f}",
                    "accepted_fast_path_credit_per_day": f"{accepted_fast_path_credit:.3f}",
                    "median_ns_per_request": format_float(stats["median"]),
                    "p10_ns_per_request": format_float(stats["p10"]),
                    "p90_ns_per_request": format_float(stats["p90"]),
                    "mean_ns_per_request": format_float(stats["mean"]),
                    "latency_weighted_proxy": format_float(stats["median"] * len(requests) if requests else math.nan),
                    "unit": "nanoseconds_per_request",
                }
            )
    return rows


def gap_rows() -> list[dict[str, str]]:
    return [
        {"quantity": "feature_extraction_latency_per_request", "measurement_status": "locally_measured_proxy", "local_artifact": str(BENCHMARK_CSV.relative_to(ROOT)), "production_requirement": "measure in serving stack on identical request features", "overclaim_guardrail": "local Python timing is not production latency"},
        {"quantity": "feature_extraction_energy_per_request", "measurement_status": "production_required", "local_artifact": "", "production_requirement": "instrument platform power or accelerator counters for feature extraction", "overclaim_guardrail": "no local energy measurement exists"},
        {"quantity": "audit_serialization_logging_latency", "measurement_status": "locally_measured_proxy", "local_artifact": str(BENCHMARK_CSV.relative_to(ROOT)), "production_requirement": "measure production audit serialization, storage, sync, and retention path", "overclaim_guardrail": "append-only local file is only a lower-bound proxy"},
        {"quantity": "audit_storage_cost", "measurement_status": "production_required", "local_artifact": "", "production_requirement": "measure bytes retained, storage tier, replication, and compliance retention", "overclaim_guardrail": "not inferred from local timing"},
        {"quantity": "fallback_dispatch_latency_and_queueing", "measurement_status": "locally_measured_proxy", "local_artifact": str(BENCHMARK_CSV.relative_to(ROOT)), "production_requirement": "measure fallback queue depth and dispatch latency under load", "overclaim_guardrail": "local branch timing excludes queueing"},
        {"quantity": "optimized_software_classifier_latency", "measurement_status": "locally_measured_proxy", "local_artifact": str(BENCHMARK_CSV.relative_to(ROOT)), "production_requirement": "measure optimized implementation on target serving hardware", "overclaim_guardrail": "Python proxy is not optimized production software"},
        {"quantity": "optimized_software_classifier_energy", "measurement_status": "production_required", "local_artifact": "", "production_requirement": "measure energy per accepted request for optimized software baseline", "overclaim_guardrail": "never label as locally measured"},
        {"quantity": "programmable_accelerator_latency", "measurement_status": "production_required", "local_artifact": "", "production_requirement": "measure accelerator latency including batching and host transfer", "overclaim_guardrail": "not produced by this harness"},
        {"quantity": "programmable_accelerator_energy", "measurement_status": "production_required", "local_artifact": "", "production_requirement": "measure accelerator energy with identical features, audit, fallback accounting", "overclaim_guardrail": "never label accelerator energy as locally measured"},
        {"quantity": "programmable_accelerator_utilization_batching", "measurement_status": "production_required", "local_artifact": "", "production_requirement": "measure utilization, batch size, occupancy, and queueing behavior", "overclaim_guardrail": "modeled utilization is not measurement"},
        {"quantity": "hybrid_control_plane_latency", "measurement_status": "modeled_from_prior_artifact", "local_artifact": "physicalized-weights/data/stronger_baseline_summary.json", "production_requirement": "measure register/control path and failure-mode routing in a real integration", "overclaim_guardrail": "prior pJ-equivalent proxy is not production measurement"},
        {"quantity": "update_cadence_rollback_policy_churn", "measurement_status": "modeled_from_prior_artifact", "local_artifact": "physicalized-weights/data/workload_scenarios.csv", "production_requirement": "collect production policy update, rollback, drift, health alarm rates", "overclaim_guardrail": "synthetic workload assumptions are not traces"},
        {"quantity": "durable_hybrid_margin_vs_best_baseline", "measurement_status": "not_measured", "local_artifact": "", "production_requirement": "compute after all production software, accelerator, feature, audit, fallback, update, and utilization measurements exist", "overclaim_guardrail": "local proxy timing cannot reopen the Phase 2 downgrade"},
    ]


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_png(path: Path, rows: list[dict[str, str]]) -> None:
    width, height = 900, 460
    margin_left, margin_bottom, margin_top = 80, 80, 35
    pixels = bytearray([255, 255, 255] * width * height)

    def set_px(x: int, y: int, color: tuple[int, int, int]) -> None:
        if 0 <= x < width and 0 <= y < height:
            idx = (y * width + x) * 3
            pixels[idx : idx + 3] = bytes(color)

    def rect(x0: int, y0: int, x1: int, y1: int, color: tuple[int, int, int]) -> None:
        for y in range(max(0, y0), min(height, y1)):
            for x in range(max(0, x0), min(width, x1)):
                set_px(x, y, color)

    components = list(COMPONENTS)
    medians = defaultdict(list)
    for row in rows:
        if row["median_ns_per_request"]:
            medians[row["component"]].append(float(row["median_ns_per_request"]))
    values = [statistics.median(medians[component]) if medians[component] else 0.0 for component in components]
    max_value = max(values) if values else 1.0
    plot_h = height - margin_bottom - margin_top
    bar_w = 70
    gap = 45
    colors = [(66, 113, 174), (82, 164, 97), (196, 121, 65), (117, 112, 179), (190, 80, 80), (90, 150, 150)]

    rect(margin_left, height - margin_bottom, width - 40, height - margin_bottom + 2, (0, 0, 0))
    rect(margin_left, margin_top, margin_left + 2, height - margin_bottom, (0, 0, 0))
    for idx, value in enumerate(values):
        x0 = margin_left + 30 + idx * (bar_w + gap)
        bar_h = 0 if max_value <= 0 else int((value / max_value) * (plot_h - 20))
        rect(x0, height - margin_bottom - bar_h, x0 + bar_w, height - margin_bottom, colors[idx % len(colors)])
    # Add compact color swatches for component identity; the CSV/JSON carry exact labels.
    for idx, color in enumerate(colors):
        rect(width - 190, 45 + idx * 24, width - 170, 62 + idx * 24, color)

    raw = b"".join(b"\x00" + pixels[y * width * 3 : (y + 1) * width * 3] for y in range(height))
    png = b"\x89PNG\r\n\x1a\n"
    for chunk_type, data in [(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)), (b"IDAT", zlib.compress(raw, 9)), (b"IEND", b"")]:
        png += struct.pack(">I", len(data)) + chunk_type + data + struct.pack(">I", zlib.crc32(chunk_type + data) & 0xFFFFFFFF)
    path.write_bytes(png)


def write_report(summary: dict[str, object]) -> None:
    REPORT_MD.write_text(
        """---
created: 2026-05-13T08:04:00Z
cycle: 3
run_id: run-2026-05-13T015136Z
agent: worker
milestone: M-MEASURE-1
---

# Production Measurement Requirements

`M-SYNTH-2` falsified the current safety/filter performance/economic superiority claim. This cycle does not reopen it; it defines the evidence contract required before it can be reconsidered.

## Required Measurements

| quantity | status | production requirement |
|---|---:|---|
"""
        + "\n".join(
            f"| {row['quantity']} | {row['measurement_status']} | {row['production_requirement']} |"
            for row in gap_rows()
        )
        + f"""

## Local Proxy Harness

The benchmark emits local host/Python timing proxies for feature extraction, fixed classifier evaluation, optimized software classifier evaluation, route/fallback decision, audit serialization, and append-only audit write. Results are in `{BENCHMARK_CSV.relative_to(ROOT)}` and `{SUMMARY_JSON.relative_to(ROOT)}`.

![local proxy latency distributions by overhead component and workload scenario, separating measured timing proxies from production-only energy and accelerator quantities](../data/local_overhead_latency_distribution.png)

## Reopen Criteria

Hybrid physicalization can only be reconsidered if measured optimized software and programmable accelerator baselines lose to hybrid under identical feature extraction, audit, fallback, update, utilization, latency, and energy accounting. The margin must remain positive after uncertainty on production-only quantities, especially accelerator energy/latency, batching behavior, utilization, fallback queueing, and audit storage cost.

## Interpretation

Local timing can decompose control overheads but cannot establish production accelerator energy or durable economic advantage. In this run, control overhead dominance is `{summary['control_overhead_dominates_fixed_classifier']}` because median feature extraction, routing, audit serialization, or audit write proxies exceed the fixed classifier proxy in at least one component aggregate. Accelerator energy status is `{summary['measurement_status']['programmable_accelerator_energy']}`.
""",
        encoding="utf-8",
    )


def build_summary(rows: list[dict[str, str]]) -> dict[str, object]:
    by_component: dict[str, list[float]] = defaultdict(list)
    scenario_ids = []
    zero_volume = {}
    all_fallback = {}
    for row in rows:
        if row["scenario_id"] not in scenario_ids:
            scenario_ids.append(row["scenario_id"])
        if row["median_ns_per_request"]:
            by_component[row["component"]].append(float(row["median_ns_per_request"]))
        if row["scenario_id"] == "zero_invocation_control":
            zero_volume[row["component"]] = row["measurement_status"]
        if row["scenario_id"] == "fallback_all_control" and row["component"] == "route_fallback_decision_proxy":
            all_fallback = {
                "fallback_frequency": row["fallback_frequency"],
                "accepted_fast_path_credit_per_day": row["accepted_fast_path_credit_per_day"],
                "median_ns_per_request": row["median_ns_per_request"],
            }
    medians = {component: statistics.median(values) for component, values in by_component.items() if values}
    fixed = medians.get("fixed_classifier_proxy", math.inf)
    control_values = [
        medians.get("feature_extraction_proxy", 0.0),
        medians.get("route_fallback_decision_proxy", 0.0),
        medians.get("audit_serialization_proxy", 0.0),
        medians.get("append_only_audit_write_proxy", 0.0),
    ]
    return {
        "schema_version": 1,
        "milestone_id": "M-MEASURE-1",
        "status": "validated",
        "seed": SEED,
        "trials": TRIALS,
        "scenario_count": len(scenario_ids),
        "scenario_ids": scenario_ids,
        "component_count": len(COMPONENTS),
        "component_median_ns_per_request": {key: round(value, 3) for key, value in medians.items()},
        "control_overhead_dominates_fixed_classifier": any(value > fixed for value in control_values),
        "measurement_status": {
            "local_latency": "locally_measured_proxy",
            "local_latency_weighted_values": "latency_weighted_proxy",
            "programmable_accelerator_latency": "production_required",
            "programmable_accelerator_energy": "production_required",
            "production_utilization": "production_required",
            "durable_hybrid_margin": "not_measured",
        },
        "special_cases": {
            "zero_invocation_control": zero_volume,
            "fallback_all_control": all_fallback,
        },
        "figure_caption": "local proxy latency distributions by overhead component and workload scenario, separating measured timing proxies from production-only energy and accelerator quantities",
        "interpretation": "local timing decomposes overheads but does not reverse the Phase 2 downgrade or measure production accelerator energy",
    }


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    rows = benchmark_rows()
    write_csv(
        BENCHMARK_CSV,
        rows,
        [
            "scenario_id",
            "component",
            "measurement_status",
            "sample_count",
            "feature_length",
            "fallback_frequency",
            "near_threshold_frequency",
            "accepted_fast_path_credit_per_day",
            "median_ns_per_request",
            "p10_ns_per_request",
            "p90_ns_per_request",
            "mean_ns_per_request",
            "latency_weighted_proxy",
            "unit",
        ],
    )
    gaps = gap_rows()
    write_csv(GAP_MATRIX_CSV, gaps, ["quantity", "measurement_status", "local_artifact", "production_requirement", "overclaim_guardrail"])
    summary = build_summary(rows)
    SUMMARY_JSON.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    write_png(LATENCY_PNG, rows)
    write_report(summary)
    print(f"wrote {BENCHMARK_CSV}")
    print(f"wrote {SUMMARY_JSON}")
    print(f"wrote {GAP_MATRIX_CSV}")
    print(f"wrote {LATENCY_PNG}")
    print(f"wrote {REPORT_MD}")
    print(f"control_overhead_dominates_fixed_classifier: {summary['control_overhead_dominates_fixed_classifier']}")


if __name__ == "__main__":
    main()
