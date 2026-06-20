#!/usr/bin/env python3
# created: 2026-05-12T20:15:00Z
# cycle: 41
# run_id: run-2026-05-11T121649Z
# agent: worker
# milestone: M-ABIINT-1
"""Verify ABI validation gates runtime and constrained-planner actions."""

from __future__ import annotations

import csv
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


def as_int(value: str) -> int:
    return int(float(value or 0))


def assert_nonblank_png(path: Path) -> None:
    assert path.exists(), f"missing {path.relative_to(ROOT)}"
    assert path.stat().st_size > 1000, f"blank or tiny figure: {path.relative_to(ROOT)}"


def assert_no_production_credit(rows: list[dict[str, str]]) -> None:
    fields = ["production_calibrated", "production_ready", "threshold_success", "causal_validity_granted", "claim_credit_allowed"]
    for row in rows:
        for field in fields:
            if field in row:
                assert row[field] == "false", row


def main() -> None:
    run("scripts/build_memory_object_abi.py")
    run("scripts/validate_memory_object_abi.py")
    run("scripts/integrate_memory_object_abi.py")
    run("scripts/plot_memory_object_abi_integration.py")

    results = {row["case_id"]: row for row in read_csv(DATA / "memory_object_abi_integration_results.csv")}
    runtime = read_csv(DATA / "memory_object_abi_runtime_actions.csv")
    planner = read_csv(DATA / "memory_object_abi_planner_actions.csv")
    boundary = {row["case_id"]: row for row in read_csv(DATA / "memory_object_abi_option_boundary.csv")}
    failures = read_csv(DATA / "memory_object_abi_integration_failure_modes.csv")

    for case_id, row in results.items():
        if row["abi_status"] == "rejected":
            assert as_int(row["downstream_memory_action_count"]) == 0, row
            assert as_int(row["runtime_action_count"]) == 0, row
            assert as_int(row["planner_action_count"]) == 0, row
            assert row["runtime_prototype_consistency"] == "not_checked_rejected_before_runtime", row
            assert row["constrained_planner_consistency"] == "not_checked_rejected_before_planner", row
            assert boundary[case_id]["boundary_result"] == "blocked_before_actions", row

    advisory = results["missing_advisory_residency_hint"]
    assert advisory["abi_status"] == "accepted", advisory
    assert advisory["admitted_to_runtime"] == "true", advisory
    assert advisory["placement_policy"] == "default_no_residency_hint", advisory
    assert advisory["runtime_prototype_consistency"] == "supported_by_runtime_policy_decisions", advisory
    assert advisory["constrained_planner_consistency"] == "supported_by_memory_plan_actions", advisory
    assert as_int(advisory["downstream_memory_action_count"]) > 0, advisory

    opt_b = results["valid_retrieved_context"]
    assert opt_b["selected_option"] == "B_memory_object_aware_runtime", opt_b
    assert opt_b["admitted_to_runtime"] == "true", opt_b
    assert opt_b["runtime_prototype_consistency"] == "supported_by_runtime_policy_decisions", opt_b
    assert opt_b["constrained_planner_consistency"] == "supported_by_memory_plan_actions", opt_b
    assert as_int(opt_b["planner_action_count"]) >= 4, opt_b

    opt_c = results["valid_branch_state"]
    assert opt_c["selected_option"] == "C_trajectory_dag_memory_fabric", opt_c
    assert opt_c["admitted_to_runtime"] == "true", opt_c
    assert opt_c["runtime_prototype_consistency"] == "supported_by_runtime_policy_decisions", opt_c
    assert opt_c["constrained_planner_consistency"] == "supported_by_memory_plan_actions", opt_c
    assert any(row["case_id"] == "valid_branch_state" and row["downstream_action_type"] == "migration" for row in planner), opt_c

    opt_a = results["option_a_opaque_baseline"]
    assert opt_a["selected_option"] == "A_conventional_request_model_kv_serving", opt_a
    assert opt_a["option_boundary"] == "opaque_baseline", opt_a
    assert opt_a["runtime_prototype_consistency"] == "opaque_supported_by_runtime_policy_decisions", opt_a
    assert opt_a["constrained_planner_consistency"] == "opaque_supported_by_memory_plan_actions", opt_a
    assert boundary["option_a_opaque_baseline"]["option_a_executable"] == "true"
    assert not any(row["case_id"] == "option_a_opaque_baseline" and row.get("action_type") in {"placement", "reuse", "compression", "migration", "retention"} for row in runtime)

    assert failures
    assert all(as_int(row["downstream_memory_action_count"]) == 0 for row in failures)
    assert_no_production_credit(list(results.values()))
    assert_no_production_credit(planner)
    assert_no_production_credit(list(boundary.values()))

    assert_nonblank_png(DATA / "memory_object_abi_integration_actions.png")
    assert_nonblank_png(DATA / "memory_object_abi_option_boundary.png")
    assert_nonblank_png(DATA / "memory_object_abi_integration_failures.png")
    print("OK: memory-object ABI integration verified.")


if __name__ == "__main__":
    main()
