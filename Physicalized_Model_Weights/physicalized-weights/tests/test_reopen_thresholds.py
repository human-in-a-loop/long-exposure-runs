# created: 2026-05-13T09:18:00Z
# cycle: 3
# run_id: run-2026-05-13T015136Z
# agent: worker
# milestone: M-REOPEN-1
"""Tests for the M-REOPEN-1 threshold model."""

from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "physicalized-weights" / "scripts" / "reopen_thresholds.py"
WOLFRAM_SCRIPT = ROOT / "physicalized-weights" / "scripts" / "symbolic_reopen_thresholds.wls"
CSV_PATH = ROOT / "physicalized-weights" / "data" / "reopen_thresholds.csv"
SUMMARY_PATH = ROOT / "physicalized-weights" / "data" / "reopen_thresholds_summary.json"
PNG_PATH = ROOT / "physicalized-weights" / "data" / "reopen_thresholds_by_scenario.png"
SYMBOLIC_PATH = ROOT / "physicalized-weights" / "data" / "symbolic_reopen_thresholds.json"

EXPECTED_FIELDS = [
    "scenario_id",
    "current_winner",
    "current_best_baseline",
    "hybrid_daily_cost_pj_equivalent",
    "best_baseline_daily_cost_pj_equivalent",
    "hybrid_margin_to_best_baseline_pj_equivalent_per_day",
    "required_hybrid_daily_reduction_to_tie_pj_equivalent_per_day",
    "required_hybrid_percent_reduction_to_tie",
    "required_best_baseline_daily_degradation_to_tie_pj_equivalent_per_day",
    "required_accepted_fast_path_multiplier_to_tie",
    "maximum_fallback_frequency_for_reopen",
    "maximum_audit_control_multiplier_for_reopen",
    "minimum_utilization_for_reopen",
    "reopen_class",
    "evidence_status",
    "threshold_unit",
    "trace_contract_requirement",
]


def run_model() -> tuple[list[dict[str, str]], dict]:
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    with CSV_PATH.open(newline="") as f:
        rows = list(csv.DictReader(f))
    summary = json.loads(SUMMARY_PATH.read_text())
    return rows, summary


def by_id(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    return {row["scenario_id"]: row for row in rows}


def test_output_schema_is_stable_and_figure_exists() -> None:
    rows, summary = run_model()
    assert rows
    assert list(rows[0].keys()) == EXPECTED_FIELDS
    assert summary["schema_version"] == 1
    assert summary["milestone_id"] == "M-REOPEN-1"
    assert PNG_PATH.exists()
    assert PNG_PATH.read_bytes().startswith(b"\x89PNG\r\n\x1a\n")


def test_formerly_preserved_case_has_positive_threshold() -> None:
    rows, summary = run_model()
    high = by_id(rows)["high_volume_stable_moderation"]
    assert high["current_winner"] == "programmable_accelerator"
    assert high["current_best_baseline"] == "programmable_accelerator"
    assert float(high["required_hybrid_daily_reduction_to_tie_pj_equivalent_per_day"]) > 0.0
    assert float(high["required_best_baseline_daily_degradation_to_tie_pj_equivalent_per_day"]) > 0.0
    assert summary["high_volume_stable_moderation"]["reopen_class"] == "finite_threshold"


def test_current_hybrid_wins_remain_zero_and_proxy_status_cannot_reopen() -> None:
    rows, summary = run_model()
    assert summary["current_hybrid_wins"] == 0
    assert all(row["current_winner"] != "hybrid_physicalized_safety_filter" for row in rows)
    assert all(row["evidence_status"] == "modeled_proxy_not_measured_production" for row in rows)
    assert all(row["reopen_class"] != "already_reopened" for row in rows)


def test_zero_volume_and_all_fallback_are_unreopenable() -> None:
    rows, summary = run_model()
    indexed = by_id(rows)
    assert indexed["zero_invocation_control"]["reopen_class"] == "unreopenable_zero_volume"
    assert indexed["zero_invocation_control"]["required_accepted_fast_path_multiplier_to_tie"] == "not_finite_no_accepted_fast_path_volume"
    assert indexed["fallback_all_control"]["reopen_class"] == "unreopenable_all_fallback"
    assert indexed["fallback_all_control"]["maximum_fallback_frequency_for_reopen"] == "not_finite_no_volume"
    assert summary["special_case_conclusions"]["proxy_only_trace"].startswith("blocked")
    assert summary["special_case_conclusions"]["missing_accelerator_baseline"].startswith("blocked")


def test_finite_thresholds_are_nonnegative_and_units_are_explicit() -> None:
    rows, _summary = run_model()
    for row in rows:
        if row["reopen_class"] == "finite_threshold":
            assert float(row["required_hybrid_daily_reduction_to_tie_pj_equivalent_per_day"]) >= 0.0
            assert float(row["required_best_baseline_daily_degradation_to_tie_pj_equivalent_per_day"]) >= 0.0
            assert "pJ_equivalent/day" in row["threshold_unit"]
            assert "fraction" in row["threshold_unit"]
            assert "multiplier" in row["threshold_unit"]
            assert "valid_reopen_candidate" in row["trace_contract_requirement"]


def test_symbolic_special_point_conclusions_are_present() -> None:
    subprocess.run(["wolfram-batch", "-script", str(WOLFRAM_SCRIPT)], cwd=ROOT, check=True)
    symbolic = json.loads(SYMBOLIC_PATH.read_text())
    points = symbolic["special_points"]
    assert "Veff_equals_0" in points
    assert "V_equals_0" in points
    assert "H_per_req_ge_B_per_req" in points
    assert "fallback_frequency_equals_1" in points
    assert "Veff" in symbolic["solved_condition"]


def main() -> None:
    tests = [
        test_output_schema_is_stable_and_figure_exists,
        test_formerly_preserved_case_has_positive_threshold,
        test_current_hybrid_wins_remain_zero_and_proxy_status_cannot_reopen,
        test_zero_volume_and_all_fallback_are_unreopenable,
        test_finite_thresholds_are_nonnegative_and_units_are_explicit,
        test_symbolic_special_point_conclusions_are_present,
    ]
    for test in tests:
        test()
        print(f"PASS {test.__name__}")


if __name__ == "__main__":
    main()
