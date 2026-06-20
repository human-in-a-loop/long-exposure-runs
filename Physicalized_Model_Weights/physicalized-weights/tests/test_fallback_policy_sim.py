# created: 2026-05-13T02:54:00Z
# cycle: 1
# run_id: run-2026-05-13T015136Z
# agent: worker
# milestone: M-ARCH-1

from __future__ import annotations

import csv
import importlib.util
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = ROOT / "physicalized-weights" / "scripts" / "fallback_policy_sim.py"
spec = importlib.util.spec_from_file_location("fallback_policy_sim", SCRIPT_PATH)
sim = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules["fallback_policy_sim"] = sim
spec.loader.exec_module(sim)


def records_by_id() -> dict[str, object]:
    return {record.case_id: record for record in sim.simulate_cases()}


def test_stale_policy_version_cannot_use_fast_path() -> None:
    record = records_by_id()["stale_policy_version"]
    assert record.route == "programmable_fallback"
    assert record.reason == "stale_policy_version"
    assert not record.physicalized_output_valid


def test_low_confidence_routes_to_fallback() -> None:
    rows = records_by_id()
    assert rows["low_confidence"].route == "programmable_fallback"
    assert rows["low_confidence"].reason == "low_confidence"
    assert rows["zero_confidence"].route == "programmable_fallback"
    assert rows["zero_confidence"].reason == "low_confidence"


def test_failed_health_check_routes_away_from_physicalized_output() -> None:
    record = records_by_id()["failed_health_check"]
    assert record.route == "programmable_fallback"
    assert record.reason == "health_check_failed"
    assert not record.physicalized_output_valid


def test_invalid_classifier_and_unavailable_fallback_enters_fail_safe() -> None:
    rows = records_by_id()
    enforce = rows["fallback_unavailable_and_classifier_invalid"]
    monitor = rows["monitor_mode_fail_safe"]
    assert enforce.route == "fail_safe"
    assert enforce.action == "fail_closed_block"
    assert enforce.fail_safe
    assert monitor.route == "fail_safe"
    assert monitor.action == "fail_safe_escalate"
    assert monitor.fail_safe


def test_audit_logging_fields_present_for_every_case() -> None:
    for record in sim.simulate_cases():
        assert record.audit_request_id
        assert record.audit_route == record.route
        assert record.audit_reason == record.reason
        assert record.audit_policy_version == record.observed_policy_version
        assert record.audit_required_policy_version == record.required_policy_version
        assert record.audit_confidence_q15 == record.confidence_q15


def test_csv_and_json_schemas_are_stable(tmp_path: Path) -> None:
    records = sim.simulate_cases()
    csv_path = tmp_path / "cases.csv"
    json_path = tmp_path / "summary.json"
    sim.write_csv(records, csv_path)
    sim.write_summary(records, json_path)

    with csv_path.open(newline="") as f:
        reader = csv.DictReader(f)
        assert reader.fieldnames == [
            "case_id",
            "description",
            "route",
            "action",
            "reason",
            "physicalized_output_valid",
            "fallback_used",
            "fail_safe",
            "classifier_available",
            "fallback_available",
            "audit_logging_available",
            "confidence_q15",
            "threshold_q15",
            "observed_policy_version",
            "required_policy_version",
            "classifier_health",
            "drift_status",
            "enforce_mode",
            "audit_request_id",
            "audit_route",
            "audit_reason",
            "audit_policy_version",
            "audit_required_policy_version",
            "audit_confidence_q15",
        ]
        rows = list(reader)
        assert len(rows) >= 7
        assert {row["route"] for row in rows} == {"physicalized_fast_path", "programmable_fallback", "fail_safe"}

    summary = json.loads(json_path.read_text())
    assert summary["schema_version"] == 1
    assert summary["case_count"] == len(records)
    assert "healthy_high_confidence" in summary["physicalized_path_cases"]
    assert "low_confidence" in summary["fallback_cases"]
    assert "fallback_unavailable_and_classifier_invalid" in summary["fail_closed_cases"]
