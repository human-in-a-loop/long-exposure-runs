#!/usr/bin/env python3
# created: 2026-05-12T03:37:00Z
# cycle: 24
# run_id: run-2026-05-11T121649Z
# agent: worker
# milestone: M-TRENDS-1

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
AXES = {
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
}
CONTEXT_COLUMNS = {
    "planner_net_value_context",
    "security_safe_hit_rate_context",
    "cxl_p99_collapse_threshold_context",
    "energy_sensitivity_collapse_rate_context",
    "pilot_options_context",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def require_columns(rows: list[dict[str, str]], cols: set[str], path: Path) -> None:
    assert rows, f"{path} is empty"
    missing = cols - set(rows[0])
    assert not missing, f"{path} missing columns {sorted(missing)}"


def test_future_trends() -> None:
    scenarios = read_csv(DATA / "future_trend_scenarios.csv")
    phase = read_csv(DATA / "future_trend_architecture_phase_diagram.csv")
    thresholds = read_csv(DATA / "future_trend_falsification_thresholds.csv")
    priorities = read_csv(DATA / "future_trend_measurement_priorities.csv")

    require_columns(scenarios, AXES | CONTEXT_COLUMNS | {"scenario_id", "workload_class", "trend_family", "memory_centric_advantage", "option_preferred", "conclusion_label", "evidence_boundary", "production_ready"}, DATA / "future_trend_scenarios.csv")
    require_columns(phase, AXES | CONTEXT_COLUMNS | {"x_axis", "y_axis", "option_preferred", "production_ready"}, DATA / "future_trend_architecture_phase_diagram.csv")
    require_columns(thresholds, CONTEXT_COLUMNS | {"threshold_id", "axis", "threshold_value", "condition", "option_at_threshold", "interpretation", "production_ready"}, DATA / "future_trend_falsification_thresholds.csv")
    require_columns(priorities, {"rank", "measurement", "primary_axis", "priority_score", "required_evidence", "production_ready"}, DATA / "future_trend_measurement_priorities.csv")

    all_rows = scenarios + phase + thresholds + priorities
    assert all(row["production_ready"] == "false" for row in all_rows), "synthetic trend rows must never be production-ready"
    assert all("synthetic" in row.get("evidence_boundary", "") or "measurement_priority_only" in row.get("evidence_boundary", "") for row in all_rows), "missing synthetic/measurement boundary"
    context_rows = scenarios + phase + thresholds
    assert any(float(r["planner_net_value_context"]) > 0 for r in context_rows), "planner context did not propagate"
    assert any(float(r["security_safe_hit_rate_context"]) > 0 for r in context_rows), "readiness/security context did not propagate"
    assert any(float(r["cxl_p99_collapse_threshold_context"]) > 8 for r in context_rows), "CXL threshold context did not propagate"
    assert all(float(r["energy_sensitivity_collapse_rate_context"]) > 0 for r in context_rows), "energy sensitivity context did not propagate"
    assert all({"A", "B", "C"} <= set(r["pilot_options_context"].split(";")) for r in context_rows), "pilot scope context did not propagate"

    zero_controls = [r for r in scenarios + phase if float(r["reuse_probability"]) == 0.0 and float(r["branch_fanout"]) == 0.0]
    assert zero_controls, "missing zero reuse/fanout controls"
    assert all(r["option_preferred"] == "A" for r in zero_controls), zero_controls[:3]

    high_overhead = [r for r in scenarios if r["scenario_id"] == "high_validation_security"]
    assert high_overhead, "missing high validation/security scenario"
    assert not any(r["option_preferred"] == "C" for r in high_overhead), "high overhead must downgrade trajectory/DAG preference"

    low_cxl_zero_reuse = [r for r in scenarios if r["scenario_id"] == "low_cxl_zero_reuse"]
    assert low_cxl_zero_reuse, "missing low-CXL zero-reuse control"
    assert all(r["option_preferred"] == "A" for r in low_cxl_zero_reuse), "low CXL latency alone cannot create reuse value"

    compelling = [r for r in scenarios if r["trend_family"] in {"workload_B_compelling", "workload_C_compelling"} and r["option_preferred"] in {"B", "C"}]
    assert len(compelling) >= 3, "need at least three B/C-compelling synthetic regimes"
    assert all(r["conclusion_label"] in {"synthetic_supported", "contract_ready"} for r in compelling), compelling[:3]

    option_a_regimes = [r for r in scenarios if r["trend_family"] == "hardware_A_sufficient" and r["option_preferred"] == "A"]
    assert len(option_a_regimes) >= 3, "need at least three Option-A-sufficient regimes"

    assert len(thresholds) >= 5, "need at least five falsification thresholds"
    required_threshold_axes = {"reuse_probability", "branch_fanout", "validation_security_overhead_multiplier", "cxl_p99_latency_multiplier", "recompute_cost_multiplier"}
    assert required_threshold_axes <= {r["axis"] for r in thresholds}, sorted(required_threshold_axes - {r["axis"] for r in thresholds})
    assert all(r["threshold_value"] != "not_crossed_in_grid" for r in thresholds), "threshold probes must cross within the synthetic grid"

    priority_ranks = [int(r["rank"]) for r in priorities]
    assert priority_ranks == sorted(priority_ranks) and priority_ranks[0] == 1, "measurement priorities must be ranked"
    assert all("production_target" in r["required_evidence"] for r in priorities), "priorities must require production_target telemetry"

    for path in [
        DATA / "future_trend_phase_diagram.png",
        DATA / "future_trend_falsification_thresholds.png",
        DATA / "future_trend_measurement_priorities.png",
    ]:
        assert path.exists(), path
        assert path.stat().st_size > 10_000, f"{path} looks blank or trivial"


if __name__ == "__main__":
    test_future_trends()
    print("OK: future trend falsification harness verified.")
