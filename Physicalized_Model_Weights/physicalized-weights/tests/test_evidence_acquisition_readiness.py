# created: 2026-05-13T12:32:00Z
# cycle: 4
# run_id: run-2026-05-13T015136Z
# agent: worker
# milestone: M-ACQUIRE-1

"""Manual tests for the M-ACQUIRE-1 readiness evaluator."""

from __future__ import annotations

import csv
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "physicalized-weights" / "scripts" / "evidence_acquisition_readiness.py"
spec = importlib.util.spec_from_file_location("evidence_acquisition_readiness", SCRIPT)
readiness = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(readiness)


def regenerate() -> tuple[list[dict[str, str]], dict]:
    readiness.main()
    with readiness.RESULTS_CSV.open(newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    summary = json.loads(readiness.SUMMARY_JSON.read_text())
    return rows, summary


def by_id(rows: list[dict[str, str]], design_id: str) -> dict[str, str]:
    for row in rows:
        if row["design_id"] == design_id:
            return row
    raise AssertionError(f"missing design {design_id}")


def test_full_shadow_and_canary_are_ready_but_not_evidence() -> None:
    rows, summary = regenerate()
    for design_id in [
        "shadow_dual_run_full_instrumentation",
        "canary_ab_full_instrumentation",
    ]:
        row = by_id(rows, design_id)
        assert row["readiness_class"] == "ready_to_collect_candidate"
        assert row["actual_reopen_candidate"] == "False"
        assert row["is_evidence"] == "False"
    assert summary["ready_to_collect_candidate_count"] == 2
    assert summary["actual_reopen_candidate_count"] == 0
    assert summary["readiness_is_evidence"] is False


def test_known_bad_designs_are_blocked_or_diagnostic_only() -> None:
    rows, _ = regenerate()
    expected = {
        "sampled_logs_no_counterfactual": "inadmissible_design",
        "vendor_benchmark_plus_local_proxy": "diagnostic_only",
        "canary_ab_privacy_risk_raw_content": "inadmissible_design",
        "single_path_production_fast_path_only": "inadmissible_design",
        "synthetic_replay_scaled_volume": "diagnostic_only",
        "shadow_dual_run_unknown_threshold_mapping": "inadmissible_design",
        "canary_ab_missing_provenance_attestation": "inadmissible_design",
    }
    for design_id, readiness_class in expected.items():
        row = by_id(rows, design_id)
        assert row["readiness_class"] == readiness_class
        assert row["downstream_gate_failures"] != "none"
        assert row["actual_reopen_candidate"] == "False"
    vendor_proxy = by_id(rows, "vendor_benchmark_plus_local_proxy")
    assert "C19:admissible_ingestion_path" in vendor_proxy["blocking_reasons"]
    assert "production_or_shadow_or_canary_source" in vendor_proxy["downstream_gate_failures"]


def test_missing_measured_energy_is_repairable_before_collection() -> None:
    rows, _ = regenerate()
    row = by_id(rows, "shadow_dual_run_missing_energy")
    assert row["readiness_class"] == "repair_required_before_collection"
    assert "C11:measured_terms" in row["repair_actions"]
    assert row["fatal_missing_count"] == "0"


def test_every_criterion_maps_to_validated_downstream_gate() -> None:
    criteria = readiness.read_csv(readiness.CRITERIA_CSV)
    for row in criteria:
        assert row["gate_dependency"] in readiness.VALID_GATE_DEPENDENCIES
        assert row["downstream_gate_failure"]
        assert row["evidence_pack_field"]
    _, summary = regenerate()
    assert set(summary["validated_gate_dependencies"]) == readiness.VALID_GATE_DEPENDENCIES


def test_png_and_summary_preserve_no_reopen() -> None:
    _, summary = regenerate()
    assert readiness.MATRIX_PNG.exists()
    assert readiness.MATRIX_PNG.stat().st_size > 1000
    assert summary["current_artifacts_reopen"] is False
    assert "threshold_crossed" in summary["future_reopen_condition"]


def run() -> None:
    tests = [
        test_full_shadow_and_canary_are_ready_but_not_evidence,
        test_known_bad_designs_are_blocked_or_diagnostic_only,
        test_missing_measured_energy_is_repairable_before_collection,
        test_every_criterion_maps_to_validated_downstream_gate,
        test_png_and_summary_preserve_no_reopen,
    ]
    for test in tests:
        test()
        print(f"PASS {test.__name__}")


if __name__ == "__main__":
    run()
