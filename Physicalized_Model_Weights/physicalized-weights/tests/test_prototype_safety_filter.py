# created: 2026-05-13T03:32:00Z
# cycle: 1
# run_id: run-2026-05-13T015136Z
# agent: worker
# milestone: M-PROTO-1
"""Tests for the M-PROTO-1 safety-filter prototype."""

from __future__ import annotations

import csv
import importlib.util
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "physicalized-weights" / "scripts" / "prototype_safety_filter.py"
DATA_DIR = ROOT / "physicalized-weights" / "data"

spec = importlib.util.spec_from_file_location("prototype_safety_filter", SCRIPT)
proto = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules["prototype_safety_filter"] = proto
spec.loader.exec_module(proto)


def load_routes() -> dict[str, dict[str, str]]:
    with (DATA_DIR / "prototype_route_results.csv").open(newline="") as handle:
        return {row["case_id"]: row for row in csv.DictReader(handle)}


def test_golden_model_edge_cases() -> None:
    expected = {
        "all_zero_bias_allow": (-10, "allow", 74, 74),
        "max_signed_features": (1895, "block", 1831, 1831),
        "min_signed_features": (-1930, "allow", 1994, 1994),
        "threshold_equal": (64, "block", 0, 0),
        "near_threshold_allow": (63, "allow", 1, 1),
        "near_threshold_block": (65, "block", 1, 1),
    }
    cases = {case.case_id: case for case in proto.vector_cases()}
    for case_id, values in expected.items():
        assert proto.classify(cases[case_id].features) == values


def test_hdl_simulation_matches_golden_vectors() -> None:
    with (DATA_DIR / "hdl_sim_results.csv").open(newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert rows
    assert {row["match"] for row in rows} == {"true"}
    routes = load_routes()
    for row in rows:
        assert int(row["score"]) == int(routes[row["case_id"]]["score"])
        assert int(row["margin"]) == int(routes[row["case_id"]]["margin"])


def test_low_confidence_routes_to_fallback() -> None:
    routes = load_routes()
    for case_id in ["threshold_equal", "near_threshold_allow", "near_threshold_block"]:
        assert routes[case_id]["route"] == "programmable_fallback"
        assert routes[case_id]["reason"] == "low_confidence"


def test_stale_version_or_failed_health_routes_away_from_fast_path() -> None:
    routes = load_routes()
    assert routes["stale_version_high_confidence"]["route"] == "programmable_fallback"
    assert routes["stale_version_high_confidence"]["reason"] == "stale_policy_version"
    assert routes["failed_health_high_confidence"]["route"] == "programmable_fallback"
    assert routes["failed_health_high_confidence"]["reason"] == "health_check_failed"


def test_classifier_and_fallback_unavailable_enters_fail_safe() -> None:
    routes = load_routes()
    enforce = routes["classifier_and_fallback_unavailable"]
    monitor = routes["monitor_mode_unavailable"]
    assert enforce["route"] == "fail_safe"
    assert enforce["action"] == "fail_closed_block"
    assert monitor["route"] == "fail_safe"
    assert monitor["action"] == "fail_safe_escalate"


def test_csv_and_json_schemas_are_stable() -> None:
    with (DATA_DIR / "prototype_route_results.csv").open(newline="") as handle:
        route_reader = csv.DictReader(handle)
        assert route_reader.fieldnames == [
            "case_id",
            "features",
            "score",
            "decision",
            "margin",
            "confidence",
            "route",
            "action",
            "reason",
            "physicalized_output_valid",
            "fallback_used",
            "fail_safe",
            "classifier_available",
            "fallback_available",
            "audit_logging_available",
            "observed_policy_version",
            "required_policy_version",
            "classifier_health",
            "drift_status",
            "enforce_mode",
            "audit_request_id",
        ]
    with (DATA_DIR / "prototype_summary.json").open() as handle:
        summary = json.load(handle)
    assert summary["schema_version"] == 1
    assert summary["route_counts"] == {
        "physicalized_fast_path": 6,
        "programmable_fallback": 8,
        "fail_safe": 2,
    }
    assert summary["case_count"] == 16


def run_tests() -> None:
    for name, func in sorted(globals().items()):
        if name.startswith("test_") and callable(func):
            func()
            print(f"PASS {name}")


if __name__ == "__main__":
    run_tests()
