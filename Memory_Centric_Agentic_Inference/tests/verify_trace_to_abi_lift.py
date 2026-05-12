#!/usr/bin/env python3
# created: 2026-05-12T18:30:00Z
# cycle: 44
# run_id: run-2026-05-11T121649Z
# agent: worker
# milestone: M-TRACEABI-1
"""Verify legacy trace-to-ABI lifting preserves ABI and production boundaries."""

from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"


def run(script: str) -> None:
    subprocess.run([sys.executable, str(ROOT / script)], check=True)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
        rows = list(csv.DictReader(f))
    assert rows, f"{path.relative_to(ROOT)} is empty"
    return rows


def read_jsonl(path: Path) -> list[dict[str, object]]:
    rows = []
    with path.open() as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    assert rows, f"{path.relative_to(ROOT)} is empty"
    return rows


def as_int(value: str) -> int:
    return int(float(value or 0))


def require_text(path: Path, needles: list[str]) -> None:
    text = path.read_text(encoding="utf-8")
    missing = [needle for needle in needles if needle not in text]
    assert not missing, f"{path.relative_to(ROOT)} missing {missing}"


def assert_nonblank_png(path: Path) -> None:
    assert path.exists(), f"missing {path.relative_to(ROOT)}"
    assert path.stat().st_size > 10_000, f"blank or tiny figure: {path.relative_to(ROOT)}"


def main() -> None:
    run("scripts/build_memory_object_abi.py")
    run("scripts/validate_memory_object_abi.py")
    run("scripts/integrate_memory_object_abi.py")
    run("scripts/lift_trace_to_memory_object_abi.py")
    run("scripts/plot_trace_to_abi_lift.py")

    candidates = {row["case_id"]: row for row in read_jsonl(DATA / "trace_to_abi_candidates.jsonl")}
    results = {row["case_id"]: row for row in read_csv(DATA / "trace_to_abi_lift_results.csv")}
    missing = read_csv(DATA / "trace_to_abi_missing_fields.csv")
    fallbacks = {row["case_id"]: row for row in read_csv(DATA / "trace_to_abi_option_fallbacks.csv")}
    annotations = read_csv(DATA / "trace_to_abi_annotation_requirements.csv")

    expected_statuses = {"abi_admissible", "annotation_required", "fail_closed", "option_a_opaque_fallback"}
    assert expected_statuses <= {row["lift_status"] for row in results.values()}
    assert set(candidates) == set(results)

    for row in results.values():
        assert row["lift_status"] in expected_statuses, row
        if row["lift_status"] in {"annotation_required", "fail_closed"}:
            assert as_int(row["downstream_memory_action_count"]) == 0, row
            assert as_int(row["runtime_action_count"]) == 0, row
            assert as_int(row["planner_action_count"]) == 0, row
            assert row["selected_option"] == "A_conventional_request_model_kv_serving", row
            assert fallbacks[row["case_id"]]["boundary_result"] == "fallback_without_memory_actions", row
        if row["lift_status"] == "abi_admissible":
            assert row["validator_status"] == "accepted", row
            assert row["validator_source"] == "scripts.validate_memory_object_abi.classify", row
            assert row["integration_boundary"] == "eligible_for_existing_abi_integration_replay", row
            assert row["runtime_prototype_consistency"] == "supported_by_runtime_policy_decisions", row
            assert row["constrained_planner_consistency"] == "supported_by_memory_plan_actions", row
            assert row["integration_source"] == "trace_lift_plus_abi_validation_plus_runtime_policy_decisions_plus_memory_plan_actions", row
            assert row["selected_option"] in {"B_memory_object_aware_runtime", "C_trajectory_dag_memory_fabric"}, row
            assert as_int(row["downstream_memory_action_count"]) > 0, row
            assert as_int(row["runtime_action_count"]) >= as_int(row["downstream_memory_action_count"]), row
            assert as_int(row["planner_action_count"]) >= as_int(row["downstream_memory_action_count"]), row
        for field in ["production_calibrated", "production_ready", "threshold_success", "causal_validity_granted", "claim_credit_allowed"]:
            assert row[field] == "false", row

    opt_a = results["option_a_opaque_legacy_request"]
    assert opt_a["lift_status"] == "option_a_opaque_fallback", opt_a
    assert opt_a["validator_status"] == "not_run", opt_a
    assert opt_a["option_a_fallback_executable"] == "true", opt_a
    assert as_int(opt_a["downstream_memory_action_count"]) == 0, opt_a

    mandatory_gaps = [row for row in missing if row["field_category"].startswith("mandatory")]
    assert mandatory_gaps, "expected mandatory missing-field rows"
    assert all(row["defaulted"] == "false" and row["blocks_downstream_actions"] == "true" for row in mandatory_gaps)
    advisory = [row for row in missing if row["field"] == "residency_hint"]
    assert advisory and all(row["field_category"] == "advisory_default_allowed" and row["defaulted"] == "true" for row in advisory)

    required_annotation_fields = {row["required_annotation"] for row in annotations}
    assert {"reuse_scope", "checked_target_id", "retention_policy_id"} <= required_annotation_fields
    for row in annotations:
        assert row["downstream_actions_blocked_until_annotation"] == "true", row

    for field in ["lineage_ids", "reuse_scope", "parent_object_ids", "checked_target_id", "retention_policy_id"]:
        assert any(row["field"] == field for row in missing), field

    require_text(
        ROOT / "memory-centric-agentic" / "trace_to_abi_migration.md",
        [
            "does not modify the ABI validator",
            "no_canonical_trace_csv_found",
            "Option A remains executable without ABI lifting",
            "silently defaulting them would violate the ABI boundary",
            "not production evidence",
            "claim_credit_allowed=false",
        ],
    )

    assert_nonblank_png(DATA / "trace_to_abi_status_counts.png")
    assert_nonblank_png(DATA / "trace_to_abi_missing_fields.png")
    assert_nonblank_png(DATA / "trace_to_abi_option_fallbacks.png")
    print("OK: trace-to-ABI lift verified.")


if __name__ == "__main__":
    main()
