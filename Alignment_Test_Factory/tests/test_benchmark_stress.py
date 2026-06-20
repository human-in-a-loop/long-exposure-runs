# created: 2026-05-13T23:55:00Z
# cycle: 7
# run_id: run-2026-05-13T204826Z
# agent: worker
# milestone: M-7

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FACTORY = ROOT / "alignment-test-factory"
SRC = FACTORY / "src"
TOOLS = FACTORY / "tools"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from alignment_test_factory.stress import build_stress_summary  # noqa: E402
from alignment_test_factory.trace import validate_trace_integrity  # noqa: E402
from run_benchmark_stress import MATRIX_PATH, RESULTS_PATH, SVG_PATH, main as run_benchmark_stress  # noqa: E402


def test_stress_suite_covers_required_families_classes_and_outcomes() -> None:
    summary = build_stress_summary()
    assert summary["probe_count"] >= 10
    assert set(summary["families"]) == {
        "permission_tool_overreach",
        "provenance_trace_mismatch",
        "uncertainty_escalation",
        "delegation_drift",
    }
    assert set(summary["stress_classes"]) == {"ambiguity", "false_negative", "false_positive", "gaming", "trace_integrity"}
    assert all("expected_outcome" in result and "observed_outcome" in result for result in summary["results"])
    assert all(result["matched_expectation"] for result in summary["results"])


def test_invalid_trace_probes_are_caught_by_integrity_validation() -> None:
    summary = build_stress_summary()
    invalid = [result for result in summary["results"] if result["expected_outcome"] == "invalid_trace"]
    assert invalid
    assert all(result["observed_outcome"] == "invalid_trace" for result in invalid)
    assert all(result["trace_integrity"]["ok"] is False for result in invalid)
    assert {error["kind"] for result in invalid for error in result["trace_integrity"]["errors"]} >= {
        "duplicate_event_id",
        "missing_evidence_link",
    }


def test_ambiguity_probe_is_inconclusive_not_failure() -> None:
    summary = build_stress_summary()
    ambiguity = [result for result in summary["results"] if result["stress_class"] == "ambiguity"]
    assert ambiguity
    assert any(result["observed_outcome"] == "inconclusive" for result in ambiguity)


def test_trace_integrity_catches_malformed_payload_and_sequence_order() -> None:
    trace = [
        {"event_id": "evt_0002", "event_type": "observation", "sequence": 2, "payload": "not an object"},
        {"event_id": "evt_0001", "event_type": "final_answer", "sequence": 1, "payload": {}},
    ]
    result = validate_trace_integrity(trace)
    kinds = {error["kind"] for error in result.errors}
    assert not result.ok
    assert "malformed_event" in kinds
    assert "non_monotonic_sequence" in kinds


def test_stress_runner_writes_json_csv_and_svg() -> None:
    run_benchmark_stress()
    summary = json.loads(RESULTS_PATH.read_text(encoding="utf-8"))
    assert summary["probe_count"] >= 10
    assert summary["matched_expectations"] == summary["probe_count"]
    assert MATRIX_PATH.exists()
    assert SVG_PATH.exists()
    assert "Stress probe outcomes by family" in SVG_PATH.read_text(encoding="utf-8")
