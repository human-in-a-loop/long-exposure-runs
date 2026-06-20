# created: 2026-05-13T09:54:00Z
# cycle: 3
# run_id: run-2026-05-13T015136Z
# agent: worker
# milestone: M-INGEST-1

from __future__ import annotations

import csv
import importlib.util
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = ROOT / "physicalized-weights" / "scripts" / "trace_ingestion_path_evaluator.py"
spec = importlib.util.spec_from_file_location("trace_ingestion_path_evaluator", SCRIPT_PATH)
evaluator = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules["trace_ingestion_path_evaluator"] = evaluator
spec.loader.exec_module(evaluator)


def load_scores() -> dict[str, dict[str, str]]:
    with evaluator.SCORES_CSV.open(newline="") as f:
        return {row["path_id"]: row for row in csv.DictReader(f)}


def load_summary() -> dict[str, object]:
    return json.loads(evaluator.SUMMARY_JSON.read_text())


def test_synthetic_fixture_only_cannot_be_reopen_candidate() -> None:
    scores = load_scores()
    row = scores["synthetic_fixture_only"]
    assert row["classification"] == "valid_but_insufficient"
    assert row["can_evaluate_m_reopen_1"] == "False"
    assert row["actual_reopened"] == "False"


def test_vendor_benchmark_lacks_identical_workload_accounting() -> None:
    scores = load_scores()
    row = scores["accelerator_vendor_benchmark_only"]
    assert row["classification"] == "valid_but_insufficient"
    assert row["primary_blocker"] == "missing_same_workload_counterfactual_baseline"
    assert row["fallback_audit_update_accounting"] == "0"


def test_privacy_risk_raw_logs_are_inadmissible() -> None:
    scores = load_scores()
    row = scores["privacy_risk_raw_logs"]
    assert row["classification"] == "inadmissible"
    assert row["primary_blocker"] == "privacy_risk_raw_or_sensitive_columns"
    assert row["privacy_safety"] == "0"


def test_sampled_production_logs_without_baselines_are_insufficient() -> None:
    scores = load_scores()
    row = scores["sampled_production_logs_without_baselines"]
    assert row["classification"] == "valid_but_insufficient"
    assert row["measured_accelerator_baseline_coverage"] == "0"
    assert row["counterfactual_baseline_validity"] == "0"


def test_only_instrumented_dual_run_paths_can_be_reopen_candidate_paths() -> None:
    summary = load_summary()
    assert summary["can_evaluate_m_reopen_1"] == [
        "shadow_production_dual_run",
        "canary_ab_dual_instrumented",
    ]
    assert summary["classification_counts"]["reopen_candidate_path"] == 2


def test_no_path_is_actual_reopened() -> None:
    summary = load_summary()
    scores = load_scores()
    assert summary["actual_reopened_count"] == 0
    assert all(row["actual_reopened"] == "False" for row in scores.values())


def test_output_schemas_are_stable_and_figure_exists() -> None:
    with evaluator.PATHS_CSV.open(newline="") as f:
        assert csv.DictReader(f).fieldnames == [
            "path_id",
            "description",
            "environment",
            "schema_complete",
            "measured_hybrid_coverage",
            "measured_accelerator_baseline_coverage",
            "measured_energy_coverage",
            "accepted_fast_path_validity",
            "fallback_audit_update_accounting",
            "policy_consistency",
            "privacy_safety",
            "workload_fidelity",
            "threshold_evaluability",
            "counterfactual_baseline_validity",
            "contains_privacy_risk",
            "identical_workload_accounting",
            "production_or_shadow",
            "missing_fields_or_gaps",
            "recommended_next_instrumentation",
        ]
    with evaluator.SCORES_CSV.open(newline="") as f:
        assert csv.DictReader(f).fieldnames == [
            "path_id",
            "classification",
            "actual_reopened",
            "total_score",
            "max_score",
            "schema_completeness",
            "measured_hybrid_coverage",
            "measured_accelerator_baseline_coverage",
            "measured_energy_coverage",
            "accepted_fast_path_validity",
            "fallback_audit_update_accounting",
            "policy_consistency",
            "privacy_safety",
            "workload_fidelity",
            "threshold_evaluability",
            "counterfactual_baseline_validity",
            "can_pass_m_trace_1",
            "can_evaluate_m_reopen_1",
            "primary_blocker",
        ]
    assert evaluator.OUTPUT_PNG.exists()
    assert evaluator.OUTPUT_PNG.stat().st_size > 100


if __name__ == "__main__":
    evaluator.main()
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"PASS {name}")
