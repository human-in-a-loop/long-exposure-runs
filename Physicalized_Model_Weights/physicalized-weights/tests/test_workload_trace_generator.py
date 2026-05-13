# created: 2026-05-13T06:20:00Z
# cycle: 2
# run_id: run-2026-05-13T015136Z
# agent: worker
# milestone: M-WORKLOAD-1

from __future__ import annotations

import csv
import importlib.util
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT_DIR = ROOT / "physicalized-weights" / "scripts"
SCRIPT_PATH = SCRIPT_DIR / "workload_trace_generator.py"
sys.path.insert(0, str(SCRIPT_DIR))
spec = importlib.util.spec_from_file_location("workload_trace_generator", SCRIPT_PATH)
workload = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules["workload_trace_generator"] = workload
spec.loader.exec_module(workload)


def summaries_by_id() -> dict[str, dict[str, str]]:
    with workload.SCENARIOS_CSV.open(newline="") as f:
        return {row["scenario_id"]: row for row in csv.DictReader(f)}


def test_all_required_scenarios_are_present() -> None:
    scenario_ids = {scenario.scenario_id for scenario in workload.scenario_catalog()}
    required = {
        "high_volume_stable_moderation",
        "bursty_consumer_traffic",
        "low_volume_enterprise_deployment",
        "high_near_threshold_adversarial",
        "frequent_policy_update_regime",
        "audit_heavy_regulated_deployment",
        "fallback_degraded_outage_regime",
        "multi_tenant_underutilized_deployment",
    }
    assert required.issubset(scenario_ids)


def test_event_generation_is_deterministic_for_fixed_seed() -> None:
    scenarios = workload.scenario_catalog()
    first = workload.generate_events(scenarios)
    second = workload.generate_events(scenarios)
    assert first == second
    assert len(first) == sum(scenario.simulated_days * workload.WINDOWS_PER_DAY for scenario in scenarios)


def test_fallback_frequency_one_produces_no_useful_fast_path() -> None:
    rows = summaries_by_id()
    all_fallback = rows["fallback_all_control"]
    assert float(all_fallback["fallback_frequency"]) == 1.0
    assert float(all_fallback["fast_path_utilization"]) == 0.0
    assert all_fallback["viability_classification"] == "falsified"


def test_zero_invocation_volume_produces_no_physicalization_viability() -> None:
    rows = summaries_by_id()
    zero = rows["zero_invocation_control"]
    assert int(zero["total_requests"]) == 0
    assert zero["viability_classification"] == "falsified"


def test_frequent_policy_updates_weaken_or_falsify_fixed_path() -> None:
    rows = summaries_by_id()
    frequent = rows["frequent_policy_update_regime"]
    assert float(frequent["update_interval_days"]) <= 7
    assert frequent["viability_classification"] in {"weakened", "falsified"}
    assert frequent["viability_classification"] == "falsified"


def test_high_near_threshold_rate_increases_fallback_routing() -> None:
    rows = summaries_by_id()
    adversarial = rows["high_near_threshold_adversarial"]
    stable = rows["high_volume_stable_moderation"]
    assert float(adversarial["near_threshold_frequency"]) > float(stable["near_threshold_frequency"])
    assert float(adversarial["fallback_frequency"]) > float(stable["fallback_frequency"])
    assert adversarial["viability_classification"] in {"speculative", "falsified"}


def test_csv_and_json_schemas_are_stable() -> None:
    with workload.EVENTS_CSV.open(newline="") as f:
        reader = csv.DictReader(f)
        assert reader.fieldnames == [
            "scenario_id",
            "window_index",
            "day",
            "request_count",
            "accepted_fast_path_count",
            "programmable_fallback_count",
            "fail_safe_count",
            "near_threshold_count",
            "stale_policy_count",
            "drift_count",
            "audit_failure_count",
            "utilization",
            "policy_update_in_window",
        ]
        first = next(reader)
        assert first["scenario_id"]

    with workload.SCENARIOS_CSV.open(newline="") as f:
        reader = csv.DictReader(f)
        assert reader.fieldnames == [
            "scenario_id",
            "description",
            "source_type",
            "total_requests",
            "simulated_days",
            "raw_requests_per_day",
            "effective_fast_path_requests_per_day",
            "fast_path_fraction",
            "fast_path_utilization",
            "fallback_frequency",
            "fail_safe_fraction",
            "near_threshold_frequency",
            "update_interval_days",
            "audit_control_scale",
            "utilization",
            "feature_extraction_us",
            "audit_logging_us",
            "software_memory_savings",
            "calibrated_winner",
            "viability_classification",
            "classification_reason",
        ]

    with workload.OVERLAY_CSV.open(newline="") as f:
        reader = csv.DictReader(f)
        assert reader.fieldnames == [
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

    summary = json.loads(workload.SUMMARY_JSON.read_text())
    assert summary["schema_version"] == 1
    assert summary["milestone_id"] == "M-WORKLOAD-1"
    assert summary["status"] == "validated"
    assert summary["classification_counts"]["preserved"] >= 1
    assert "fallback_frequency" in summary["carry_forward_variables_for_M_SWBASE_2"]


if __name__ == "__main__":
    workload.main()
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"PASS {name}")
