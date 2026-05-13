# created: 2026-05-13T15:00:00Z
# cycle: 5
# run_id: run-2026-05-13T015136Z
# agent: worker
# milestone: M-UNCERTAINTY-1
"""Direct tests for M-UNCERTAINTY-1."""

from __future__ import annotations

import csv
import importlib.util
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "physicalized-weights" / "scripts" / "reopen_uncertainty_protocol.py"
RESULTS = ROOT / "physicalized-weights" / "data" / "reopen_uncertainty_results.csv"
SUMMARY = ROOT / "physicalized-weights" / "data" / "reopen_uncertainty_summary.json"
PNG = ROOT / "physicalized-weights" / "data" / "reopen_uncertainty_margin_plot.png"


def load_module():
    spec = importlib.util.spec_from_file_location("reopen_uncertainty_protocol", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules["reopen_uncertainty_protocol"] = module
    spec.loader.exec_module(module)
    return module


def rows_by_case() -> dict[str, dict[str, str]]:
    with RESULTS.open(newline="", encoding="utf-8") as f:
        return {row["case_id"]: row for row in csv.DictReader(f)}


def test_point_crossing_wide_uncertainty_is_blocked(rows):
    row = rows["point_crossing_wide_uncertainty"]
    assert row["point_crossing"] == "True"
    assert float(row["delta_mean"]) < 0
    assert float(row["ucb_alpha"]) >= 0
    assert row["classification"] == "point_crossing_not_statistically_durable"
    assert row["actual_reopen_candidate"] == "False"


def test_large_synthetic_margin_is_durable_but_nonactual(rows):
    row = rows["synthetic_large_margin_low_uncertainty"]
    assert float(row["ucb_alpha"]) < 0
    assert row["statistically_durable"] == "True"
    assert row["classification"] == "statistically_durable_nonactual_control"
    assert row["actual_reopen_candidate"] == "False"
    assert "source_actuality=synthetic_control" in row["blocking_reasons"]


def test_zero_volume_and_all_fallback_remain_blocked(rows):
    assert rows["zero_volume_control"]["classification"] == "blocked_zero_volume"
    assert rows["all_fallback_control"]["classification"] == "blocked_all_fallback"
    assert rows["zero_volume_control"]["actual_reopen_candidate"] == "False"
    assert rows["all_fallback_control"]["actual_reopen_candidate"] == "False"


def test_missing_uncertainty_terms_block_evaluation(rows):
    missing_baseline = rows["missing_baseline_uncertainty"]
    missing_guardrail = rows["negative_margin_but_guardrail_missing"]
    missing_shared_instrumentation = rows["high_correlation_without_shared_instrumentation"]
    assert missing_baseline["classification"] == "blocked_missing_uncertainty_terms"
    assert "missing:sigma_baseline" in missing_baseline["blocking_reasons"]
    assert missing_guardrail["classification"] == "blocked_missing_uncertainty_terms"
    assert "missing:guardrail_telemetry_status" in missing_guardrail["blocking_reasons"]
    assert missing_shared_instrumentation["classification"] == "blocked_missing_uncertainty_terms"
    assert "missing:shared_instrumentation_attestation_for_high_rho" in missing_shared_instrumentation["blocking_reasons"]


def test_positive_or_overlapping_ucb_is_not_reopen(rows):
    assert rows["baseline_favored_positive_delta"]["classification"] == "baseline_favored"
    assert rows["baseline_favored_positive_delta"]["actual_reopen_candidate"] == "False"
    assert rows["inconclusive_near_tie"]["classification"] == "inconclusive_overlap"
    assert rows["inconclusive_near_tie"]["actual_reopen_candidate"] == "False"


def test_non_actual_sources_block_even_with_favorable_means(rows):
    row = rows["template_non_actual_source"]
    assert row["classification"] == "blocked_non_actual_source"
    assert row["actual_reopen_candidate"] == "False"
    assert "package_gates_pass=false" in row["blocking_reasons"]


def test_summary_zero_actual_and_png(rows):
    summary = json.loads(SUMMARY.read_text())
    assert summary["case_count"] >= 8
    assert summary["actual_reopen_candidate_count"] == 0
    assert summary["current_artifacts_reopen"] is False
    assert summary["status_mismatches"] == []
    assert PNG.exists()
    assert PNG.stat().st_size > 1000
    classes = summary["classification_counts"]
    for required in [
        "point_crossing_not_statistically_durable",
        "statistically_durable_nonactual_control",
        "baseline_favored",
        "inconclusive_overlap",
        "blocked_missing_uncertainty_terms",
        "blocked_non_actual_source",
        "blocked_zero_volume",
        "blocked_all_fallback",
    ]:
        assert classes.get(required, 0) >= 1


def run() -> None:
    module = load_module()
    module.main()
    rows = rows_by_case()
    tests = [
        test_point_crossing_wide_uncertainty_is_blocked,
        test_large_synthetic_margin_is_durable_but_nonactual,
        test_zero_volume_and_all_fallback_remain_blocked,
        test_missing_uncertainty_terms_block_evaluation,
        test_positive_or_overlapping_ucb_is_not_reopen,
        test_non_actual_sources_block_even_with_favorable_means,
        test_summary_zero_actual_and_png,
    ]
    for test in tests:
        test(rows)
        print(f"PASS {test.__name__}")


if __name__ == "__main__":
    run()
