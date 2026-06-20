# created: 2026-05-13T05:38:00Z
# cycle: 2
# run_id: run-2026-05-13T015136Z
# agent: worker
# milestone: M-CAL-1

from __future__ import annotations

import csv
import importlib.util
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = ROOT / "physicalized-weights" / "scripts" / "calibrated_breakeven.py"
spec = importlib.util.spec_from_file_location("calibrated_breakeven", SCRIPT_PATH)
cal = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules["calibrated_breakeven"] = cal
spec.loader.exec_module(cal)


def test_assumption_rows_include_required_metadata() -> None:
    assumptions = cal.load_assumptions()
    assert len(assumptions) >= 12
    for row in assumptions.values():
        assert row["unit"]
        assert row["source_type"] in cal.SOURCE_TYPES
        assert row["confidence"] in cal.CONFIDENCE_LEVELS
        assert row["citation_or_artifact_path"]


def test_calibrated_model_rejects_zero_volume_physicalization() -> None:
    summary = json.loads(cal.SUMMARY_JSON.read_text())
    assert summary["zero_volume_physicalized_wins"] == []


def test_pessimistic_software_runtime_savings_do_not_improve_physicalization() -> None:
    with cal.GRID_CSV.open(newline="") as f:
        rows = list(csv.DictReader(f))
    winner_rows = [row for row in rows if row["winner"] == "True"]
    by_savings: dict[str, list[str]] = {}
    for row in winner_rows:
        by_savings.setdefault(row["software_memory_savings"], []).append(row["strategy"])
    low = by_savings["0.0"].count("hybrid_safety_filter") / len(by_savings["0.0"])
    high = by_savings["0.5"].count("hybrid_safety_filter") / len(by_savings["0.5"])
    assert high <= low


def test_missing_unit_metadata_fails_validation() -> None:
    bad = {
        "variable": "bad_probe",
        "value_or_range": "1",
        "unit": "",
        "source_type": "modeled",
        "citation_or_artifact_path": "probe",
        "confidence": "low",
        "notes": "probe",
    }
    try:
        cal.validate_assumption_row(bad)
    except ValueError as exc:
        assert "missing unit" in str(exc)
    else:
        raise AssertionError("missing unit metadata did not fail validation")


def test_summary_reports_top_uncertainty_drivers() -> None:
    summary = json.loads(cal.SUMMARY_JSON.read_text())
    drivers = summary["top_uncertainty_drivers"]
    assert drivers
    assert drivers[0]["variable"] == "fallback_frequency"
    assert all("hybrid_win_rate_swing" in row for row in drivers)
    assert summary["safety_filter_decision"] in {
        "preserved_but_weakened",
        "preserved_only_under_bounded_non_pessimistic_conditions",
        "reopened_uncertainty_dominated",
    }


def test_csv_and_json_schemas_are_stable() -> None:
    with cal.GRID_CSV.open(newline="") as f:
        reader = csv.DictReader(f)
        assert reader.fieldnames == [
            "strategy",
            "requests_per_day",
            "update_interval_days",
            "software_memory_savings",
            "fallback_frequency",
            "audit_control_scale",
            "utilization",
            "requests_per_update",
            "per_request_pj_equivalent",
            "amortized_fixed_pj_equivalent",
            "total_pj_equivalent",
            "winner",
            "conclusion",
        ]
        first = next(reader)
        assert first["strategy"] in cal.STRATEGIES
        assert first["audit_control_scale"] in {"low", "mid", "high"}

    with cal.TORNADO_CSV.open(newline="") as f:
        reader = csv.DictReader(f)
        assert reader.fieldnames == ["variable", "hybrid_win_rate_swing", "bucket_count", "note"]
        assert next(reader)["variable"]

    summary = json.loads(cal.SUMMARY_JSON.read_text())
    assert summary["schema_version"] == 1
    assert summary["milestone_id"] == "M-CAL-1"
    assert summary["status"] == "validated"
    assert summary["unit"] == "pJ_equivalent proxy"


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"PASS {name}")
