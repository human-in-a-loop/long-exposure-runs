#!/usr/bin/env python3
# created: 2026-05-12T03:35:00Z
# cycle: 24
# run_id: run-2026-05-11T121649Z
# agent: worker
# milestone: M-TRENDS-1
"""Evaluate synthetic future hardware/workload trend falsification scenarios.

This is a trend-sensitivity harness, not production calibration. It preserves
existing readiness semantics: synthetic scenarios can support or falsify an
architecture assumption, but cannot create production-ready claims.
"""

from __future__ import annotations

import csv
from pathlib import Path
from statistics import mean


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

SCENARIO_OUT = DATA / "future_trend_scenarios.csv"
PHASE_OUT = DATA / "future_trend_architecture_phase_diagram.csv"
THRESHOLD_OUT = DATA / "future_trend_falsification_thresholds.csv"
PRIORITY_OUT = DATA / "future_trend_measurement_priorities.csv"

AXES = [
    "hbm_capacity_multiplier",
    "hbm_bandwidth_multiplier",
    "cxl_p99_latency_multiplier",
    "nvme_remote_latency_multiplier",
    "energy_per_byte_multiplier",
    "recompute_cost_multiplier",
    "validation_security_overhead_multiplier",
    "reuse_probability",
    "branch_fanout",
    "durable_state_lifetime",
    "verification_loop_count",
]


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


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
    print(f"wrote {path.relative_to(ROOT)} rows={len(rows)}")


def f(row: dict[str, str], key: str, default: float = 0.0) -> float:
    value = row.get(key, "")
    return float(value) if value not in ("", None) else default


def canonical_workload(name: str) -> str:
    lower = name.lower()
    if lower.startswith("rag"):
        return "RAG"
    if lower.startswith("batch"):
        return "batch summarization/offline inference control"
    if lower.startswith("code-agent"):
        return "code-agent loop"
    if lower.startswith("verification-heavy"):
        return "verification-heavy"
    if lower.startswith("multi-agent"):
        return "multi-agent branch/merge"
    if lower.startswith("single-turn"):
        return "single-turn chat control"
    return name


def build_context(
    energy_rows: list[dict[str, str]],
    cxl_rows: list[dict[str, str]],
    planning_rows: list[dict[str, str]],
    option_rows: list[dict[str, str]],
    pilot_rows: list[dict[str, str]],
) -> dict[str, object]:
    """Summarize validated upstream artifacts into lightweight scoring context."""
    energy_collapse_rate = 0.0
    if energy_rows:
        changed = [
            row
            for row in energy_rows
            if row.get("option_before") != row.get("option_after")
            or "zero removes energy" in row.get("collapse_reason", "")
        ]
        energy_collapse_rate = len(changed) / len(energy_rows)

    cxl_threshold_by_workload: dict[str, float] = {}
    grouped: dict[str, list[float]] = {}
    for row in cxl_rows:
        if row.get("latency_percentile") != "p99":
            continue
        threshold = f(row, "collapse_threshold", 0.0)
        if threshold <= 0:
            continue
        grouped.setdefault(canonical_workload(row["workload_class"]), []).append(threshold)
    for workload, values in grouped.items():
        cxl_threshold_by_workload[workload] = mean(values)

    planner_by_workload = {
        canonical_workload(row["workload_class"]): {
            "planner_net_value": f(row, "total_net_plan_value", 0.0),
            "positive_reuse_rows": f(row, "positive_reuse_rows", 0.0),
            "dominant_constraint": row.get("dominant_constraint", ""),
        }
        for row in planning_rows
        if row.get("setting") == "baseline"
    }
    readiness_by_workload = {
        canonical_workload(row["workload_class"]): {
            "readiness_label": row.get("readiness_label", ""),
            "security_safe_hit_rate": f(row, "security_safe_hit_rate", 0.0),
            "recommended_option": row.get("option", "A"),
        }
        for row in option_rows
    }
    pilot_options = sorted({
        opt.strip()
        for row in pilot_rows
        for opt in row.get("architecture_options", "").split(";")
        if opt.strip()
    })
    return {
        "energy_collapse_rate": energy_collapse_rate,
        "cxl_threshold_by_workload": cxl_threshold_by_workload,
        "planner_by_workload": planner_by_workload,
        "readiness_by_workload": readiness_by_workload,
        "pilot_options": pilot_options,
    }


def trend_score(base: dict[str, str], trend: dict[str, float], context: dict[str, object]) -> dict[str, object]:
    workload = canonical_workload(base["scenario"])
    planner = context["planner_by_workload"].get(workload, {})  # type: ignore[index, union-attr]
    readiness = context["readiness_by_workload"].get(workload, {})  # type: ignore[index, union-attr]
    cxl_thresholds = context["cxl_threshold_by_workload"]  # type: ignore[assignment]
    cxl_threshold = cxl_thresholds.get(workload, 8.0) if isinstance(cxl_thresholds, dict) else 8.0
    cxl_threshold = float(cxl_threshold or 8.0)
    energy_collapse_rate = float(context["energy_collapse_rate"])
    pilot_options = set(context["pilot_options"])  # type: ignore[arg-type]

    reuse = trend["reuse_probability"]
    branch = trend["branch_fanout"]
    durable = trend["durable_state_lifetime"]
    verify = trend["verification_loop_count"]
    size = f(base, "object_size_units", 1000.0)
    base_retained = f(base, "retained_value_score", 0.0)
    base_energy = max(f(base, "energy_proxy_score", 1.0), 1.0)

    retained = 0.0
    if reuse > 0:
        retained = base_retained
        retained *= reuse / max(f(base, "reuse_probability", 0.1), 0.1)
        retained *= 1.0 + 0.18 * max(branch - 1.0, 0.0)
        retained *= 1.0 + 0.035 * durable
        retained *= 1.0 + 0.16 * verify
        retained *= trend["recompute_cost_multiplier"] ** 0.5
        retained *= 1.0 + clamp(float(planner.get("planner_net_value", 0.0)) / 100.0, -0.15, 0.35)

    movement_cost = (size / 1000.0) * trend["energy_per_byte_multiplier"] / max(trend["hbm_bandwidth_multiplier"], 0.1)
    capacity_relief = 1.0 / max(trend["hbm_capacity_multiplier"], 0.1)
    movement_cost *= 0.8 + capacity_relief
    movement_cost *= 1.0 + 0.1 * energy_collapse_rate
    contention = trend["cxl_p99_latency_multiplier"] * (0.7 + 0.25 * max(branch, 0.0))
    contention *= 8.0 / max(cxl_threshold, 8.0)
    durable_latency = trend["nvme_remote_latency_multiplier"] * max(durable, 0.0) * 0.22
    safe_hit = float(readiness.get("security_safe_hit_rate", 0.0))
    validation = trend["validation_security_overhead_multiplier"] * (1.0 + 0.45 * max(verify, 0.0))
    validation *= 1.0 + max(0.0, 0.75 - safe_hit) * 0.25
    recompute_alt = base_energy / max(trend["recompute_cost_multiplier"], 0.1) / 35.0
    advantage = retained - movement_cost - contention - durable_latency - validation - recompute_alt

    if reuse <= 0 or advantage <= 0:
        option = "A"
        label = "falsified_under_assumption" if base.get("memory_centric_thesis") == "strengthened" else "measurement_required"
        reason = "zero_or_negative_memory_centric_advantage"
    elif branch >= 2 and (durable >= 6 or verify >= 2) and advantage >= 15:
        option = "C"
        label = "contract_ready"
        reason = "trajectory_branch_durable_value_exceeds_costs"
    else:
        option = "B"
        label = "synthetic_supported"
        reason = "object_reuse_value_exceeds_costs"

    if trend["validation_security_overhead_multiplier"] >= 8 and option in {"B", "C"}:
        option = "A" if advantage < 20 else "B"
        label = "falsified_under_assumption" if option == "A" else "synthetic_supported"
        reason = "validation_security_overhead_downgrade"
    if option not in pilot_options:
        option = "A"
        label = "measurement_required"
        reason = "option_not_in_production_pilot_scope"

    return {
        "retained_state_value": round(retained, 4),
        "movement_cost": round(movement_cost, 4),
        "contention_penalty": round(contention + durable_latency, 4),
        "recompute_alternative": round(recompute_alt, 4),
        "validation_security_overhead": round(validation, 4),
        "memory_centric_advantage": round(advantage, 4),
        "option_preferred": option,
        "conclusion_label": label,
        "reason": reason,
        "planner_net_value_context": round(float(planner.get("planner_net_value", 0.0)), 4),
        "security_safe_hit_rate_context": round(safe_hit, 4),
        "cxl_p99_collapse_threshold_context": round(cxl_threshold, 4),
        "energy_sensitivity_collapse_rate_context": round(energy_collapse_rate, 4),
        "pilot_options_context": ";".join(sorted(pilot_options)),
    }


def scenario_rows(cost_rows: list[dict[str, str]], context: dict[str, object]) -> list[dict[str, object]]:
    trend_cases = [
        ("control_zero_reuse_branch", "control", dict(hbm_capacity_multiplier=1, hbm_bandwidth_multiplier=1, cxl_p99_latency_multiplier=1, nvme_remote_latency_multiplier=1, energy_per_byte_multiplier=1, recompute_cost_multiplier=1, validation_security_overhead_multiplier=1, reuse_probability=0, branch_fanout=0, durable_state_lifetime=0, verification_loop_count=0)),
        ("large_hbm_fast_bandwidth", "hardware_A_sufficient", dict(hbm_capacity_multiplier=8, hbm_bandwidth_multiplier=4, cxl_p99_latency_multiplier=0.5, nvme_remote_latency_multiplier=0.8, energy_per_byte_multiplier=0.35, recompute_cost_multiplier=0.45, validation_security_overhead_multiplier=1, reuse_probability=0.1, branch_fanout=0, durable_state_lifetime=1, verification_loop_count=0)),
        ("cheap_recompute", "hardware_A_sufficient", dict(hbm_capacity_multiplier=2, hbm_bandwidth_multiplier=2, cxl_p99_latency_multiplier=0.8, nvme_remote_latency_multiplier=1, energy_per_byte_multiplier=0.5, recompute_cost_multiplier=0.25, validation_security_overhead_multiplier=1, reuse_probability=0.2, branch_fanout=1, durable_state_lifetime=2, verification_loop_count=1)),
        ("low_cxl_zero_reuse", "control", dict(hbm_capacity_multiplier=1, hbm_bandwidth_multiplier=1, cxl_p99_latency_multiplier=0.01, nvme_remote_latency_multiplier=1, energy_per_byte_multiplier=1, recompute_cost_multiplier=1, validation_security_overhead_multiplier=1, reuse_probability=0, branch_fanout=4, durable_state_lifetime=8, verification_loop_count=3)),
        ("pathological_cxl_tail", "hardware_A_sufficient", dict(hbm_capacity_multiplier=1, hbm_bandwidth_multiplier=1, cxl_p99_latency_multiplier=60, nvme_remote_latency_multiplier=2, energy_per_byte_multiplier=1, recompute_cost_multiplier=1, validation_security_overhead_multiplier=1, reuse_probability=0.6, branch_fanout=3, durable_state_lifetime=6, verification_loop_count=2)),
        ("high_validation_security", "control", dict(hbm_capacity_multiplier=1, hbm_bandwidth_multiplier=1, cxl_p99_latency_multiplier=0.5, nvme_remote_latency_multiplier=1, energy_per_byte_multiplier=1, recompute_cost_multiplier=2, validation_security_overhead_multiplier=12, reuse_probability=0.8, branch_fanout=5, durable_state_lifetime=10, verification_loop_count=4)),
        ("high_prefix_tool_reuse", "workload_B_compelling", dict(hbm_capacity_multiplier=1, hbm_bandwidth_multiplier=1, cxl_p99_latency_multiplier=0.7, nvme_remote_latency_multiplier=1, energy_per_byte_multiplier=1, recompute_cost_multiplier=2, validation_security_overhead_multiplier=1, reuse_probability=0.85, branch_fanout=1, durable_state_lifetime=4, verification_loop_count=1)),
        ("branch_durable_verifier_growth", "workload_C_compelling", dict(hbm_capacity_multiplier=1, hbm_bandwidth_multiplier=1, cxl_p99_latency_multiplier=0.6, nvme_remote_latency_multiplier=0.7, energy_per_byte_multiplier=1, recompute_cost_multiplier=2.5, validation_security_overhead_multiplier=1, reuse_probability=0.78, branch_fanout=5, durable_state_lifetime=14, verification_loop_count=5)),
        ("long_lived_workspace", "workload_B_compelling", dict(hbm_capacity_multiplier=1.5, hbm_bandwidth_multiplier=1, cxl_p99_latency_multiplier=0.8, nvme_remote_latency_multiplier=0.5, energy_per_byte_multiplier=1, recompute_cost_multiplier=1.5, validation_security_overhead_multiplier=1.2, reuse_probability=0.65, branch_fanout=2, durable_state_lifetime=20, verification_loop_count=1)),
    ]
    rows: list[dict[str, object]] = []
    for base in cost_rows:
        for scenario_id, family, trend in trend_cases:
            score = trend_score(base, trend, context)
            rows.append({
                "scenario_id": scenario_id,
                "workload_class": base["scenario"],
                "representative_object": base["representative_object"],
                "trend_family": family,
                **trend,
                **score,
                "evidence_boundary": "synthetic_trend_sensitivity_not_measured_evidence",
                "production_ready": "false",
            })
    return rows


def phase_rows(cost_rows: list[dict[str, str]], context: dict[str, object]) -> list[dict[str, object]]:
    base = next(r for r in cost_rows if r["scenario"] == "multi-agent branch/merge run")
    rows: list[dict[str, object]] = []
    for reuse in [0, 0.1, 0.25, 0.5, 0.75, 0.9]:
        for branch in [0, 1, 2, 4, 8]:
            trend = dict(hbm_capacity_multiplier=1, hbm_bandwidth_multiplier=1, cxl_p99_latency_multiplier=1, nvme_remote_latency_multiplier=1, energy_per_byte_multiplier=1, recompute_cost_multiplier=1.5, validation_security_overhead_multiplier=1, reuse_probability=reuse, branch_fanout=branch, durable_state_lifetime=8 if branch else 0, verification_loop_count=3 if branch else 0)
            score = trend_score(base, trend, context)
            rows.append({"x_axis": "reuse_probability", "y_axis": "branch_fanout", **trend, **score, "evidence_boundary": "synthetic_trend_sensitivity_not_measured_evidence", "production_ready": "false"})
    return rows


def threshold_rows(cost_rows: list[dict[str, str]], context: dict[str, object]) -> list[dict[str, object]]:
    base = next(r for r in cost_rows if r["scenario"] == "multi-agent branch/merge run")
    defaults = dict(hbm_capacity_multiplier=1, hbm_bandwidth_multiplier=1, cxl_p99_latency_multiplier=1, nvme_remote_latency_multiplier=1, energy_per_byte_multiplier=1, recompute_cost_multiplier=1.5, validation_security_overhead_multiplier=1, reuse_probability=0.65, branch_fanout=3, durable_state_lifetime=8, verification_loop_count=3)
    probes = [
        ("reuse_probability_min_for_B", "reuse_probability", [0, 0.1, 0.2, 0.35, 0.5, 0.65, 0.8], "B_or_C_becomes_compelling", defaults),
        ("branch_fanout_min_for_C", "branch_fanout", [0, 1, 2, 3, 4, 6, 8], "C_becomes_compelling", defaults),
        ("validation_security_overhead_collapse", "validation_security_overhead_multiplier", [1, 2, 4, 6, 8, 12, 16, 32, 64], "B_or_C_collapses_to_A", defaults),
        ("cxl_p99_latency_collapse", "cxl_p99_latency_multiplier", [0.1, 0.5, 1, 2, 5, 10, 25, 60, 120, 240, 480], "B_or_C_collapses_to_A", defaults),
        ("recompute_cost_min_for_memory_centric", "recompute_cost_multiplier", [0.1, 0.25, 0.5, 1, 1.5, 2, 4], "B_or_C_becomes_compelling", defaults),
        ("durable_lifetime_min_for_C", "durable_state_lifetime", [0, 1, 2, 4, 6, 10, 16, 24], "C_becomes_compelling", {**defaults, "verification_loop_count": 1}),
    ]
    rows: list[dict[str, object]] = []
    for threshold_id, axis, values, condition, probe_defaults in probes:
        selected = None
        selected_score: dict[str, object] | None = None
        for value in values:
            trend = {**probe_defaults, axis: value}
            score = trend_score(base, trend, context)
            if condition == "B_or_C_becomes_compelling" and score["option_preferred"] in {"B", "C"}:
                selected, selected_score = value, score
                break
            if condition == "C_becomes_compelling" and score["option_preferred"] == "C":
                selected, selected_score = value, score
                break
            if condition == "B_or_C_collapses_to_A" and score["option_preferred"] == "A":
                selected, selected_score = value, score
                break
        selected_score = selected_score or trend_score(base, {**probe_defaults, axis: values[-1]}, context)
        rows.append({
            "threshold_id": threshold_id,
            "axis": axis,
            "threshold_value": selected if selected is not None else "not_crossed_in_grid",
            "condition": condition,
            "option_at_threshold": selected_score["option_preferred"],
            "memory_centric_advantage": selected_score["memory_centric_advantage"],
            "planner_net_value_context": selected_score["planner_net_value_context"],
            "security_safe_hit_rate_context": selected_score["security_safe_hit_rate_context"],
            "cxl_p99_collapse_threshold_context": selected_score["cxl_p99_collapse_threshold_context"],
            "energy_sensitivity_collapse_rate_context": selected_score["energy_sensitivity_collapse_rate_context"],
            "pilot_options_context": selected_score["pilot_options_context"],
            "interpretation": interpretation(threshold_id),
            "evidence_boundary": "synthetic_trend_sensitivity_not_measured_evidence",
            "production_ready": "false",
        })
    return rows


def interpretation(threshold_id: str) -> str:
    return {
        "reuse_probability_min_for_B": "if measured reuse stays below this point, memory-object reuse is likely transient or workload-specific",
        "branch_fanout_min_for_C": "trajectory/DAG machinery needs real branch structure; fanout near zero collapses to Option A/B",
        "validation_security_overhead_collapse": "security/provenance cost can falsify reuse even when retained state value is high",
        "cxl_p99_latency_collapse": "warm-tier tail latency can erase retained value and force local recompute/control behavior",
        "recompute_cost_min_for_memory_centric": "cheap recomputation weakens the memory-centric thesis",
        "durable_lifetime_min_for_C": "durable workspace lifetime must be long enough to amortize movement, validation, and coordination",
    }[threshold_id]


def measurement_rows() -> list[dict[str, object]]:
    rows = [
        (1, "joined production reuse probability by object class", "reuse_probability", 95, "separates transient cache effects from durable object reuse"),
        (2, "CXL/pooled-memory p99 under tenant concurrency", "cxl_p99_latency_multiplier", 90, "moves the largest collapse boundary for warm-tier placement"),
        (3, "validation/security/provenance overhead per safe reuse", "validation_security_overhead_multiplier", 88, "can independently downgrade B/C despite high retained value"),
        (4, "branch fanout and merge/discard rates for agent trajectories", "branch_fanout", 82, "distinguishes object-cache reuse from trajectory/DAG architecture need"),
        (5, "durable workspace lifetime and replay frequency", "durable_state_lifetime", 76, "tests whether durable state amortizes coordination and storage latency"),
        (6, "target accelerator energy per tier byte moved", "energy_per_byte_multiplier", 72, "decides whether CL-012 is economic support or only retained-value support"),
        (7, "recompute cost for verifier and tool-output regeneration", "recompute_cost_multiplier", 68, "tests whether cheap recompute makes memory-centric placement a workaround"),
    ]
    return [
        {
            "rank": rank,
            "measurement": measurement,
            "primary_axis": axis,
            "priority_score": score,
            "why_it_matters": why,
            "required_evidence": "real joined production_target telemetry with schema, join, noise-floor, security, and verifier gates",
            "evidence_boundary": "measurement_priority_only_not_measured_evidence",
            "production_ready": "false",
        }
        for rank, measurement, axis, score, why in rows
    ]


def main() -> None:
    cost_rows = read_csv(DATA / "cost_model_scenarios.csv")
    energy_rows = read_csv(DATA / "energy_architecture_sensitivity.csv")
    cxl_rows = read_csv(DATA / "cxl_contention_thresholds.csv")
    planning_rows = read_csv(DATA / "memory_plan_constraint_sensitivity.csv")
    option_rows = read_csv(DATA / "final_architecture_option_readiness.csv")
    pilot_rows = read_csv(DATA / "production_telemetry_pilot_design.csv")
    claims = read_csv(DATA / "final_claim_readiness_matrix.csv")
    assert all(row["production_ready"] == "false" for row in claims), "current package must not contain production-ready claims"
    context = build_context(energy_rows, cxl_rows, planning_rows, option_rows, pilot_rows)

    scenarios = scenario_rows(cost_rows, context)
    phase = phase_rows(cost_rows, context)
    thresholds = threshold_rows(cost_rows, context)
    priorities = measurement_rows()

    context_fields = ["planner_net_value_context", "security_safe_hit_rate_context", "cxl_p99_collapse_threshold_context", "energy_sensitivity_collapse_rate_context", "pilot_options_context"]
    scenario_fields = ["scenario_id", "workload_class", "representative_object", "trend_family", *AXES, "retained_state_value", "movement_cost", "contention_penalty", "recompute_alternative", "validation_security_overhead", "memory_centric_advantage", "option_preferred", "conclusion_label", "reason", *context_fields, "evidence_boundary", "production_ready"]
    phase_fields = ["x_axis", "y_axis", *AXES, "retained_state_value", "movement_cost", "contention_penalty", "recompute_alternative", "validation_security_overhead", "memory_centric_advantage", "option_preferred", "conclusion_label", "reason", *context_fields, "evidence_boundary", "production_ready"]
    threshold_fields = ["threshold_id", "axis", "threshold_value", "condition", "option_at_threshold", "memory_centric_advantage", *context_fields, "interpretation", "evidence_boundary", "production_ready"]
    priority_fields = ["rank", "measurement", "primary_axis", "priority_score", "why_it_matters", "required_evidence", "evidence_boundary", "production_ready"]
    write_csv(SCENARIO_OUT, scenarios, scenario_fields)
    write_csv(PHASE_OUT, phase, phase_fields)
    write_csv(THRESHOLD_OUT, thresholds, threshold_fields)
    write_csv(PRIORITY_OUT, priorities, priority_fields)


if __name__ == "__main__":
    main()
