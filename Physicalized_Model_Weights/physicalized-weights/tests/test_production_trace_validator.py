# created: 2026-05-13T08:42:00Z
# cycle: 3
# run_id: run-2026-05-13T015136Z
# agent: worker
# milestone: M-TRACE-1

from __future__ import annotations

import csv
import importlib.util
import json
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = ROOT / "physicalized-weights" / "scripts" / "production_trace_validator.py"
DATA_DIR = ROOT / "physicalized-weights" / "data"
spec = importlib.util.spec_from_file_location("production_trace_validator", SCRIPT_PATH)
validator = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules["production_trace_validator"] = validator
spec.loader.exec_module(validator)


def load_summary() -> dict[str, object]:
    return json.loads(validator.SUMMARY_JSON.read_text())


def issue_statuses(result: dict[str, object]) -> set[str]:
    return {issue["status"] for issue in result["issues"]}


def test_valid_fixture_is_schema_valid_but_proxy_energy_blocks_reopen() -> None:
    summary = load_summary()
    valid = next(result for result in summary["traces"] if result["trace_file"].endswith("example_production_trace_valid.csv"))
    assert valid["status"] == "valid_but_insufficient"
    assert valid["requests"] == 6
    assert valid["accepted_fast_path_requests"] == 4
    assert "measured_energy_required" in valid["insufficient_reasons"]
    assert valid["energy_coverage"]["accelerator_measured_rows"] == 6
    assert valid["energy_coverage"]["hybrid_proxy_rows"] == 6


def test_invalid_fixture_rejects_missing_baseline_negative_latency_and_privacy_risk() -> None:
    summary = load_summary()
    invalid = next(result for result in summary["traces"] if result["trace_file"].endswith("example_production_trace_invalid.csv"))
    statuses = issue_statuses(invalid)
    assert invalid["status"] == "invalid_privacy_risk"
    assert "invalid_missing_baseline" in statuses
    assert "invalid_units" in statuses
    assert "invalid_privacy_risk" in statuses
    assert "invalid_inconsistent_policy" in statuses


def test_all_fallback_trace_has_no_fast_path_and_cannot_reopen() -> None:
    path = temp_trace_path("all_fallback")
    write_fixture(
        path,
        [
            row("1000", route_decision="programmable_fallback", fallback_taken="true", hybrid_energy_status="measured", measurement_environment="production"),
            row("2000", route_decision="programmable_fallback", fallback_taken="true", hybrid_energy_status="measured", measurement_environment="production"),
        ],
    )
    result = validator.validate_trace(path, validator.load_schema())
    assert result["status"] == "valid_but_insufficient"
    assert result["accepted_fast_path_requests"] == 0
    assert "zero_accepted_fast_path" in result["insufficient_reasons"]


def test_zero_volume_trace_is_valid_control_not_reopen_candidate() -> None:
    path = temp_trace_path("zero_volume")
    write_fixture(path, [])
    result = validator.validate_trace(path, validator.load_schema())
    assert result["status"] == "valid_but_insufficient"
    assert result["requests"] == 0
    assert "zero_volume" in result["insufficient_reasons"]


def test_mixed_policy_versions_without_update_events_fail_consistency() -> None:
    path = temp_trace_path("mixed_policy")
    write_fixture(
        path,
        [
            row("1000", policy_version_hash="hash:p1", hybrid_energy_status="measured", measurement_environment="production"),
            row("2000", policy_version_hash="hash:p2", hybrid_energy_status="measured", measurement_environment="production"),
        ],
    )
    result = validator.validate_trace(path, validator.load_schema())
    assert result["status"] == "invalid_inconsistent_policy"
    assert "invalid_inconsistent_policy" in issue_statuses(result)


def test_proxy_energy_cannot_satisfy_measured_energy_requirement() -> None:
    path = temp_trace_path("proxy_energy")
    write_fixture(
        path,
        [
            row("1000", accelerator_energy_status="proxy", hybrid_energy_status="measured", measurement_environment="production"),
            row("2000", accelerator_energy_status="proxy", hybrid_energy_status="measured", measurement_environment="production"),
        ],
    )
    result = validator.validate_trace(path, validator.load_schema())
    assert result["status"] == "valid_but_insufficient"
    assert "measured_energy_required" in result["insufficient_reasons"]
    assert result["energy_coverage"]["accelerator_proxy_rows"] == 2


def test_fast_path_credit_requires_audit_and_passing_gates() -> None:
    path = temp_trace_path("bad_fast_path_gates")
    write_fixture(
        path,
        [
            row("1000", audit_logged="false", hybrid_energy_status="measured", measurement_environment="production"),
            row("2000", health_gate_passed="false", hybrid_energy_status="measured", measurement_environment="production"),
            row("3000", drift_gate_passed="false", hybrid_energy_status="measured", measurement_environment="production"),
        ],
    )
    result = validator.validate_trace(path, validator.load_schema())
    assert result["status"] == "invalid_schema"
    assert result["accepted_fast_path_requests"] == 0
    assert "invalid_schema" in issue_statuses(result)


def test_report_schema_is_stable_and_figure_exists() -> None:
    with validator.REPORT_CSV.open(newline="") as f:
        reader = csv.DictReader(f)
        assert reader.fieldnames == [
            "trace_file",
            "status",
            "requests",
            "accepted_fast_path_requests",
            "fallback_frequency",
            "near_threshold_frequency",
            "audit_logging_rate",
            "health_gate_failure_rate",
            "drift_gate_failure_rate",
            "update_count",
            "rollback_count",
            "feature_extract_median_ns",
            "route_median_ns",
            "audit_median_ns",
            "software_baseline_median_ns",
            "accelerator_baseline_median_ns",
            "hybrid_fast_path_median_ns",
            "measured_energy_coverage",
            "issue_count",
            "issues",
        ]
    assert validator.COVERAGE_PNG.exists()
    assert validator.COVERAGE_PNG.stat().st_size > 100


def write_fixture(path: Path, rows: list[dict[str, str]]) -> None:
    fieldnames = [column["name"] for column in validator.load_schema()["columns"]]
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def temp_trace_path(name: str) -> Path:
    directory = Path(tempfile.gettempdir()) / "physicalized_trace_validator_tests"
    directory.mkdir(exist_ok=True)
    return directory / f"{name}.csv"


def row(timestamp_ns: str, **overrides: str) -> dict[str, str]:
    base = {
        "timestamp_ns": timestamp_ns,
        "scenario_id": "unit_test_trace",
        "policy_version_hash": "hash:unit-policy",
        "request_class": "standard",
        "feature_vector_hash": f"hash:unit-{timestamp_ns}",
        "feature_length": "8",
        "route_decision": "physicalized_fast_path",
        "fallback_taken": "false",
        "near_threshold": "false",
        "audit_logged": "true",
        "health_gate_passed": "true",
        "drift_gate_passed": "true",
        "feature_extract_latency_ns": "1000",
        "route_latency_ns": "300",
        "audit_latency_ns": "5000",
        "software_baseline_latency_ns": "9000",
        "accelerator_baseline_latency_ns": "4000",
        "hybrid_fast_path_latency_ns": "1200",
        "accelerator_energy_proxy_or_measured_pj": "500",
        "accelerator_energy_status": "measured",
        "hybrid_energy_proxy_or_measured_pj": "600",
        "hybrid_energy_status": "measured",
        "utilization_fraction": "0.70",
        "update_event": "false",
        "rollback_event": "false",
        "measurement_environment": "production",
    }
    base.update(overrides)
    return base


if __name__ == "__main__":
    validator.main(
        [
            str(DATA_DIR / "example_production_trace_valid.csv"),
            str(DATA_DIR / "example_production_trace_invalid.csv"),
        ]
    )
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"PASS {name}")
