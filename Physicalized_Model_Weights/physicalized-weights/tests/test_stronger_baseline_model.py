# created: 2026-05-13T06:58:00Z
# cycle: 2
# run_id: run-2026-05-13T015136Z
# agent: worker
# milestone: M-SWBASE-2

from __future__ import annotations

import csv
import importlib.util
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT_DIR = ROOT / "physicalized-weights" / "scripts"
SCRIPT_PATH = SCRIPT_DIR / "stronger_baseline_model.py"
sys.path.insert(0, str(SCRIPT_DIR))
spec = importlib.util.spec_from_file_location("stronger_baseline_model", SCRIPT_PATH)
model = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules["stronger_baseline_model"] = model
spec.loader.exec_module(model)


def comparison_rows() -> list[dict[str, str]]:
    with model.COMPARISON_CSV.open(newline="") as f:
        return list(csv.DictReader(f))


def winner_by_scenario() -> dict[str, dict[str, str]]:
    return {row["scenario_id"]: row for row in comparison_rows() if row["winner"] == "True"}


def test_consumes_exact_workload_rows() -> None:
    workloads = model.read_workloads()
    scenario_ids = {row.scenario_id for row in workloads}
    out_ids = {row["scenario_id"] for row in comparison_rows()}
    assert scenario_ids == out_ids
    assert len(comparison_rows()) == len(workloads) * len(model.ALTERNATIVES)


def test_csv_json_schemas_are_stable() -> None:
    with model.COMPARISON_CSV.open(newline="") as f:
        reader = csv.DictReader(f)
        assert reader.fieldnames == [
            "scenario_id",
            "alternative",
            "raw_requests_per_day",
            "effective_fast_path_requests_per_day",
            "fallback_requests_per_day",
            "feature_extraction_cost_per_day_pj",
            "audit_logging_cost_per_day_pj",
            "update_control_cost_per_day_pj",
            "utilization_adjusted_fixed_substrate_cost_per_day_pj",
            "estimated_energy_per_accepted_request_pj",
            "estimated_latency_per_accepted_request_us",
            "total_daily_cost_proxy_pj",
            "winner",
            "decision_class",
            "mechanism_note",
        ]
    with model.THRESHOLDS_CSV.open(newline="") as f:
        reader = csv.DictReader(f)
        assert reader.fieldnames == ["scenario_id", "threshold_name", "baseline_value", "threshold_value", "unit", "interpretation"]
    summary = json.loads(model.SUMMARY_JSON.read_text())
    assert summary["schema_version"] == 1
    assert summary["milestone_id"] == "M-SWBASE-2"
    assert summary["status"] == "validated"
    assert summary["scenario_count"] == 10


def test_special_cases_do_not_credit_hybrid() -> None:
    winners = winner_by_scenario()
    for scenario_id in ["zero_invocation_control", "fallback_all_control", "frequent_policy_update_regime", "multi_tenant_underutilized_deployment"]:
        assert winners[scenario_id]["alternative"] != "hybrid_physicalized_safety_filter"
        assert winners[scenario_id]["decision_class"] in {"software_dominates", "accelerator_dominates", "hybrid_falsified"}


def test_preserved_case_remains_quantified() -> None:
    winners = winner_by_scenario()
    preserved = winners["high_volume_stable_moderation"]
    assert preserved["alternative"] in model.ALTERNATIVES
    assert preserved["decision_class"] in {"hybrid_preserved", "software_dominates", "accelerator_dominates"}
    with model.THRESHOLDS_CSV.open(newline="") as f:
        thresholds = [row for row in csv.DictReader(f) if row["scenario_id"] == "high_volume_stable_moderation"]
    margin = next(row for row in thresholds if row["threshold_name"] == "current_hybrid_margin_vs_best_baseline")
    margin_value = float(margin["threshold_value"])
    software_threshold = next(row for row in thresholds if row["threshold_name"] == "software_memory_savings_that_erases_hybrid")
    accelerator_threshold = next(row for row in thresholds if row["threshold_name"] == "accelerator_compute_multiplier_that_erases_hybrid")
    if preserved["alternative"] == "hybrid_physicalized_safety_filter":
        assert margin_value > 0
    else:
        assert margin_value < 0
    assert software_threshold["threshold_value"] == "not_erased_by_sweep"
    assert accelerator_threshold["threshold_value"] == "already_erased"


def test_thresholds_mark_erased_or_explicit_boundary() -> None:
    with model.THRESHOLDS_CSV.open(newline="") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 30
    for row in rows:
        assert row["threshold_value"]
    all_fallback = [row for row in rows if row["scenario_id"] == "fallback_all_control"]
    assert any(row["threshold_value"] == "already_erased" for row in all_fallback)


if __name__ == "__main__":
    model.main()
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"PASS {name}")
