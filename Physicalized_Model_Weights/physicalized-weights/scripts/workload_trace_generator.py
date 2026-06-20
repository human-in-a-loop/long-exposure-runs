# created: 2026-05-13T06:12:00Z
# cycle: 2
# run_id: run-2026-05-13T015136Z
# agent: worker
# milestone: M-WORKLOAD-1
"""Deterministic workload trace assumptions for the safety-filter fast path."""

from __future__ import annotations

import csv
import json
import math
import random
import struct
import zlib
from dataclasses import asdict, dataclass
from pathlib import Path

import calibrated_breakeven as cal


ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "physicalized-weights" / "data"

EVENTS_CSV = DATA_DIR / "workload_trace_events.csv"
SCENARIOS_CSV = DATA_DIR / "workload_scenarios.csv"
SUMMARY_JSON = DATA_DIR / "workload_summary.json"
OVERLAY_CSV = DATA_DIR / "workload_viability_overlay.csv"
UTILIZATION_PNG = DATA_DIR / "workload_fast_path_utilization.png"

SEED = 20260513
WINDOWS_PER_DAY = 24


@dataclass(frozen=True)
class WorkloadScenario:
    scenario_id: str
    description: str
    source_type: str
    requests_per_day: float
    simulated_days: int
    update_interval_days: float
    base_fallback_rate: float
    near_threshold_rate: float
    stale_policy_rate: float
    drift_rate: float
    audit_failure_rate: float
    fallback_availability: float
    utilization: float
    audit_control_scale: str
    feature_extraction_us: float
    audit_logging_us: float
    burstiness: float
    software_memory_savings: float


@dataclass(frozen=True)
class EventRow:
    scenario_id: str
    window_index: int
    day: int
    request_count: int
    accepted_fast_path_count: int
    programmable_fallback_count: int
    fail_safe_count: int
    near_threshold_count: int
    stale_policy_count: int
    drift_count: int
    audit_failure_count: int
    utilization: float
    policy_update_in_window: bool


@dataclass(frozen=True)
class ScenarioSummary:
    scenario_id: str
    description: str
    source_type: str
    total_requests: int
    simulated_days: int
    raw_requests_per_day: float
    effective_fast_path_requests_per_day: float
    fast_path_fraction: float
    fast_path_utilization: float
    fallback_frequency: float
    fail_safe_fraction: float
    near_threshold_frequency: float
    update_interval_days: float
    audit_control_scale: str
    utilization: float
    feature_extraction_us: float
    audit_logging_us: float
    software_memory_savings: float
    calibrated_winner: str
    viability_classification: str
    classification_reason: str


def scenario_catalog() -> list[WorkloadScenario]:
    return [
        WorkloadScenario(
            "high_volume_stable_moderation",
            "Large stable moderation path with steady reuse, bounded control overhead, and monthly-or-slower policy updates.",
            "modeled",
            1_000_000,
            7,
            90,
            0.002,
            0.003,
            0.001,
            0.001,
            0.0005,
            1.0,
            0.35,
            "low",
            1.5,
            8.8,
            0.15,
            0.0,
        ),
        WorkloadScenario(
            "bursty_consumer_traffic",
            "Consumer traffic with burst windows, moderate near-threshold pressure, and lower average utilization.",
            "modeled",
            500_000,
            7,
            30,
            0.10,
            0.12,
            0.01,
            0.004,
            0.002,
            1.0,
            0.55,
            "mid",
            1.8,
            9.5,
            1.4,
            0.35,
        ),
        WorkloadScenario(
            "low_volume_enterprise_deployment",
            "Small enterprise tenant with slow updates but too little volume to amortize fixed/control costs.",
            "modeled",
            100,
            14,
            90,
            0.05,
            0.05,
            0.002,
            0.001,
            0.001,
            1.0,
            0.25,
            "mid",
            2.0,
            8.8,
            0.7,
            0.2,
        ),
        WorkloadScenario(
            "high_near_threshold_adversarial",
            "Adversarial or ambiguous requests cluster near the threshold and force frequent fallback.",
            "modeled",
            100_000,
            7,
            30,
            0.08,
            0.70,
            0.01,
            0.01,
            0.002,
            1.0,
            0.70,
            "mid",
            1.8,
            9.0,
            0.4,
            0.2,
        ),
        WorkloadScenario(
            "frequent_policy_update_regime",
            "High-volume deployment where weekly policy churn strands fixed-path amortization.",
            "inferred",
            100_000,
            14,
            7,
            0.08,
            0.08,
            0.05,
            0.004,
            0.002,
            1.0,
            0.65,
            "mid",
            1.5,
            8.8,
            0.25,
            0.2,
        ),
        WorkloadScenario(
            "audit_heavy_regulated_deployment",
            "Regulated path where audit logging and control overhead dominate the fixed classifier surface.",
            "local_measured",
            100_000,
            7,
            90,
            0.08,
            0.08,
            0.004,
            0.004,
            0.02,
            1.0,
            0.65,
            "high",
            2.5,
            18.0,
            0.3,
            0.2,
        ),
        WorkloadScenario(
            "fallback_degraded_outage_regime",
            "Fallback service is degraded, so invalid physicalized outputs increasingly become fail-safe events.",
            "modeled",
            200_000,
            7,
            30,
            0.35,
            0.25,
            0.02,
            0.02,
            0.005,
            0.15,
            0.70,
            "mid",
            1.8,
            9.0,
            0.6,
            0.2,
        ),
        WorkloadScenario(
            "multi_tenant_underutilized_deployment",
            "Many small tenants fragment demand and strand the fixed substrate between bursts.",
            "inferred",
            50_000,
            14,
            90,
            0.10,
            0.10,
            0.01,
            0.004,
            0.002,
            1.0,
            0.12,
            "mid",
            2.0,
            9.0,
            1.8,
            0.35,
        ),
        WorkloadScenario(
            "zero_invocation_control",
            "Explicit null case: no requests means no fixed-path amortization.",
            "modeled",
            0,
            7,
            90,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            1.0,
            0.0,
            "low",
            1.5,
            8.8,
            0.0,
            0.2,
        ),
        WorkloadScenario(
            "fallback_all_control",
            "Explicit null case: every request routes away from the physicalized fast path.",
            "modeled",
            100_000,
            7,
            90,
            1.0,
            0.0,
            0.0,
            0.0,
            0.0,
            1.0,
            0.70,
            "mid",
            1.5,
            8.8,
            0.2,
            0.2,
        ),
    ]


def stable_seed(scenario_id: str) -> int:
    return SEED + sum((i + 1) * ord(ch) for i, ch in enumerate(scenario_id))


def bounded_count(rng: random.Random, request_count: int, rate: float) -> int:
    if request_count <= 0 or rate <= 0:
        return 0
    if rate >= 1.0:
        return request_count
    expected = request_count * min(max(rate, 0.0), 1.0)
    jitter = rng.uniform(-0.08, 0.08) * math.sqrt(max(expected, 1.0))
    return max(0, min(request_count, int(round(expected + jitter))))


def window_requests(scenario: WorkloadScenario, window_index: int, rng: random.Random) -> int:
    if scenario.requests_per_day <= 0:
        return 0
    base = scenario.requests_per_day / WINDOWS_PER_DAY
    hour = window_index % WINDOWS_PER_DAY
    diurnal = 0.72 + 0.28 * math.sin((hour - 6) / 24.0 * 2.0 * math.pi) ** 2
    burst = 1.0
    if scenario.burstiness > 0:
        burst += scenario.burstiness * (rng.random() ** 5) * 2.5
        if window_index % 31 == 0:
            burst += scenario.burstiness * 2.0
    return int(round(base * diurnal * burst))


def generate_events(scenarios: list[WorkloadScenario]) -> list[EventRow]:
    rows: list[EventRow] = []
    for scenario in scenarios:
        rng = random.Random(stable_seed(scenario.scenario_id))
        windows = scenario.simulated_days * WINDOWS_PER_DAY
        update_every = max(1, int(round(scenario.update_interval_days * WINDOWS_PER_DAY)))
        for window_index in range(windows):
            request_count = window_requests(scenario, window_index, rng)
            policy_update = request_count > 0 and window_index % update_every == 0
            stale_rate = scenario.stale_policy_rate + (0.20 if policy_update and scenario.update_interval_days <= 7 else 0.0)
            near = bounded_count(rng, request_count, scenario.near_threshold_rate)
            stale = bounded_count(rng, request_count - near, stale_rate)
            drift = bounded_count(rng, request_count - near - stale, scenario.drift_rate)
            audit = bounded_count(rng, request_count - near - stale - drift, scenario.audit_failure_rate)
            base = bounded_count(rng, request_count - near - stale - drift - audit, scenario.base_fallback_rate)
            invalid = min(request_count, near + stale + drift + audit + base)
            fallback_capacity = int(round(invalid * scenario.fallback_availability))
            fallback = min(invalid, fallback_capacity)
            fail_safe = invalid - fallback
            accepted = max(0, request_count - invalid)
            rows.append(
                EventRow(
                    scenario_id=scenario.scenario_id,
                    window_index=window_index,
                    day=window_index // WINDOWS_PER_DAY,
                    request_count=request_count,
                    accepted_fast_path_count=accepted,
                    programmable_fallback_count=fallback,
                    fail_safe_count=fail_safe,
                    near_threshold_count=near,
                    stale_policy_count=stale,
                    drift_count=drift,
                    audit_failure_count=audit,
                    utilization=scenario.utilization,
                    policy_update_in_window=policy_update,
                )
            )
    return rows


def calibrated_winner(scenario: WorkloadScenario, fallback_frequency: float) -> str:
    assumptions = cal.load_assumptions()
    params = cal.primitive_params(assumptions, cal.probe_metrics())
    model_scenario = cal.Scenario(
        requests_per_day=float(scenario.requests_per_day),
        update_interval_days=float(scenario.update_interval_days),
        software_memory_savings=float(scenario.software_memory_savings),
        fallback_frequency=float(min(max(fallback_frequency, 0.0), 1.0)),
        audit_control_scale=scenario.audit_control_scale,
        utilization=float(max(scenario.utilization, 1e-9)),
    )
    rows = cal.evaluate(model_scenario, params)
    return next(row.strategy for row in rows if row.winner)


def classify(scenario: WorkloadScenario, fast_utilization: float, fallback_frequency: float, fail_safe_fraction: float, winner: str) -> tuple[str, str]:
    if scenario.requests_per_day == 0:
        return "falsified", "zero invocation volume gives no amortization"
    if fallback_frequency >= 0.95 or fast_utilization <= 0.02:
        return "falsified", "effective fast-path volume is near zero"
    if scenario.update_interval_days <= 7:
        return "falsified", "weekly-or-faster policy updates strand fixed-path amortization"
    if scenario.utilization < 0.20:
        return "falsified", "multi-tenant underutilization strands the fixed substrate"
    if fail_safe_fraction > 0.10:
        return "speculative", "fallback degradation creates material fail-safe traffic"
    if (
        winner == "hybrid_safety_filter"
        and scenario.requests_per_day >= 100_000
        and fast_utilization >= 0.30
        and fallback_frequency <= 0.10
        and scenario.audit_control_scale != "high"
    ):
        return "preserved", "high effective reuse, slow updates, and bounded fallback preserve the claim"
    if winner == "hybrid_safety_filter" or (fast_utilization >= 0.25 and fallback_frequency <= 0.50 and scenario.update_interval_days >= 30):
        return "weakened", "workload keeps some fast-path reuse but leaves baseline or overhead pressure"
    return "speculative", "calibrated baseline usually wins under this workload shape"


def summarize(scenarios: list[WorkloadScenario], events: list[EventRow]) -> list[ScenarioSummary]:
    by_scenario: dict[str, list[EventRow]] = {scenario.scenario_id: [] for scenario in scenarios}
    for row in events:
        by_scenario[row.scenario_id].append(row)
    out: list[ScenarioSummary] = []
    for scenario in scenarios:
        rows = by_scenario[scenario.scenario_id]
        total = sum(row.request_count for row in rows)
        fast = sum(row.accepted_fast_path_count for row in rows)
        fallback = sum(row.programmable_fallback_count for row in rows)
        fail_safe = sum(row.fail_safe_count for row in rows)
        near = sum(row.near_threshold_count for row in rows)
        raw_rpd = total / scenario.simulated_days if scenario.simulated_days else 0.0
        fast_fraction = fast / total if total else 0.0
        fallback_frequency = (fallback + fail_safe) / total if total else 0.0
        fail_safe_fraction = fail_safe / total if total else 0.0
        fast_utilization = fast_fraction * scenario.utilization
        winner = calibrated_winner(scenario, fallback_frequency)
        viability, reason = classify(scenario, fast_utilization, fallback_frequency, fail_safe_fraction, winner)
        out.append(
            ScenarioSummary(
                scenario_id=scenario.scenario_id,
                description=scenario.description,
                source_type=scenario.source_type,
                total_requests=total,
                simulated_days=scenario.simulated_days,
                raw_requests_per_day=round(raw_rpd, 3),
                effective_fast_path_requests_per_day=round((fast / scenario.simulated_days) * scenario.utilization, 3) if scenario.simulated_days else 0.0,
                fast_path_fraction=round(fast_fraction, 6),
                fast_path_utilization=round(fast_utilization, 6),
                fallback_frequency=round(fallback_frequency, 6),
                fail_safe_fraction=round(fail_safe_fraction, 6),
                near_threshold_frequency=round(near / total, 6) if total else 0.0,
                update_interval_days=scenario.update_interval_days,
                audit_control_scale=scenario.audit_control_scale,
                utilization=scenario.utilization,
                feature_extraction_us=scenario.feature_extraction_us,
                audit_logging_us=scenario.audit_logging_us,
                software_memory_savings=scenario.software_memory_savings,
                calibrated_winner=winner,
                viability_classification=viability,
                classification_reason=reason,
            )
        )
    return out


def write_csv(path: Path, rows: list[object]) -> None:
    fields = list(asdict(rows[0]).keys())
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow(asdict(row))


def write_overlay(path: Path, summaries: list[ScenarioSummary]) -> None:
    fields = [
        "scenario_id",
        "raw_requests_per_day",
        "effective_fast_path_requests_per_day",
        "fast_path_utilization",
        "fallback_frequency",
        "near_threshold_frequency",
        "update_interval_days",
        "audit_control_scale",
        "utilization",
        "calibrated_winner",
        "viability_classification",
        "classification_reason",
    ]
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in summaries:
            data = asdict(row)
            writer.writerow({field: data[field] for field in fields})


def png_chunk(kind: bytes, data: bytes) -> bytes:
    return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)


def write_png(path: Path, summaries: list[ScenarioSummary]) -> None:
    width, height = 900, 460
    pixels = bytearray()
    top, bottom = 70, 370
    left = 70
    bar_w = 28
    gap = 24
    colors = {
        "preserved": (72, 150, 92),
        "weakened": (216, 157, 70),
        "speculative": (93, 132, 190),
        "falsified": (190, 80, 74),
    }
    for y in range(height):
        pixels.append(0)
        for x in range(width):
            color = (248, 248, 244)
            if y == bottom and 45 <= x <= width - 35:
                color = (90, 90, 90)
            if x == 45 and top <= y <= bottom:
                color = (90, 90, 90)
            for i, row in enumerate(summaries):
                x0 = left + i * (bar_w + gap)
                x1 = x0 + bar_w
                fast_h = int((bottom - top) * min(row.fast_path_utilization, 1.0))
                fallback_h = int((bottom - top) * min(row.fallback_frequency, 1.0))
                if x0 <= x <= x1 and bottom - fast_h <= y <= bottom:
                    color = colors[row.viability_classification]
                if x0 + bar_w + 4 <= x <= x0 + bar_w + 12 and bottom - fallback_h <= y <= bottom:
                    color = (80, 80, 80)
            pixels.extend(color)
    raw = bytes(pixels)
    data = (
        b"\x89PNG\r\n\x1a\n"
        + png_chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
        + png_chunk(b"IDAT", zlib.compress(raw, 9))
        + png_chunk(b"IEND", b"")
    )
    path.write_bytes(data)


def write_summary(path: Path, summaries: list[ScenarioSummary]) -> None:
    counts: dict[str, int] = {}
    for row in summaries:
        counts[row.viability_classification] = counts.get(row.viability_classification, 0) + 1
    carry_forward = [
        "scenario_id",
        "raw_requests_per_day",
        "effective_fast_path_requests_per_day",
        "fallback_frequency",
        "near_threshold_frequency",
        "update_interval_days",
        "audit_control_scale",
        "utilization",
        "feature_extraction_us",
        "audit_logging_us",
        "software_memory_savings",
        "viability_classification",
    ]
    doc = {
        "schema_version": 1,
        "milestone_id": "M-WORKLOAD-1",
        "status": "validated",
        "seed": SEED,
        "scenario_count": len(summaries),
        "classification_counts": counts,
        "figure_caption": "fast-path utilization and fallback/fail-safe fraction across workload scenarios, showing where the safety/filter physicalization claim is preserved, weakened, or falsified.",
        "carry_forward_variables_for_M_SWBASE_2": carry_forward,
        "falsification_rules": [
            "fallback_frequency near 1.0 produces no useful physicalized utilization",
            "zero invocation volume produces no amortization",
            "weekly-or-faster policy updates falsify the fixed-path claim under this model",
            "high near-threshold rate increases fallback routing pressure",
            "underutilization strands the fixed substrate",
        ],
        "scenarios": [asdict(row) for row in summaries],
    }
    path.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n")


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    scenarios = scenario_catalog()
    events = generate_events(scenarios)
    summaries = summarize(scenarios, events)
    write_csv(EVENTS_CSV, events)
    write_csv(SCENARIOS_CSV, summaries)
    write_overlay(OVERLAY_CSV, summaries)
    write_summary(SUMMARY_JSON, summaries)
    write_png(UTILIZATION_PNG, summaries)
    print(f"wrote {EVENTS_CSV}")
    print(f"wrote {SCENARIOS_CSV}")
    print(f"wrote {SUMMARY_JSON}")
    print(f"wrote {OVERLAY_CSV}")
    print(f"wrote {UTILIZATION_PNG}")
    print(f"classifications: {json.dumps(json.loads(SUMMARY_JSON.read_text())['classification_counts'], sort_keys=True)}")


if __name__ == "__main__":
    main()
