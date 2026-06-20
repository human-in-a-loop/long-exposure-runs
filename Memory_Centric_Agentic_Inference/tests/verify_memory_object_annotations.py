#!/usr/bin/env python3
# created: 2026-05-12T22:15:00Z
# cycle: 45
# run_id: run-2026-05-11T121649Z
# agent: worker
# milestone: M-ANNOT-1
"""Verify annotation contract and merge boundary."""

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


def assert_nonblank_png(path: Path) -> None:
    assert path.exists(), f"missing {path.relative_to(ROOT)}"
    assert path.stat().st_size > 10_000, f"blank or tiny figure: {path.relative_to(ROOT)}"


def require_text(path: Path, needles: list[str]) -> None:
    text = path.read_text(encoding="utf-8")
    missing = [needle for needle in needles if needle not in text]
    assert not missing, f"{path.relative_to(ROOT)} missing {missing}"


def main() -> None:
    run("scripts/build_memory_object_abi.py")
    run("scripts/validate_memory_object_abi.py")
    run("scripts/integrate_memory_object_abi.py")
    run("scripts/lift_trace_to_memory_object_abi.py")
    run("scripts/build_memory_object_annotations.py")
    run("scripts/merge_trace_annotations_to_abi.py")
    run("scripts/plot_memory_object_annotations.py")

    schema = read_csv(DATA / "memory_object_annotation_schema.csv")
    examples = read_jsonl(DATA / "memory_object_annotation_examples.jsonl")
    requirements = read_csv(DATA / "memory_object_annotation_requirements.csv")
    results = {row["annotation_id"]: row for row in read_csv(DATA / "annotation_merge_results.csv")}
    completed = read_jsonl(DATA / "annotation_completed_abi_candidates.jsonl")
    conflicts = read_csv(DATA / "annotation_conflict_failures.csv")
    boundary = {row["annotation_id"]: row for row in read_csv(DATA / "annotation_option_boundary.csv")}

    required_classes = {
        "reuse_scope_annotation",
        "tenant_security_annotation",
        "tool_provenance_annotation",
        "branch_dependency_annotation",
        "verifier_integrity_annotation",
        "compression_safety_annotation",
        "retention_policy_annotation",
        "evidence_label_annotation",
    }
    assert required_classes == {row["annotation_class"] for row in schema}
    assert all(row["trusted_assertion"] == "false" for row in schema)
    assert {row["annotation_id"] for row in examples} == set(results)
    assert requirements and all(row["downstream_actions_blocked_until_validated_annotation"] == "true" for row in requirements)

    expected_completed = {
        "ann_valid_reuse_scope_kv",
        "ann_valid_tool_provenance",
        "ann_valid_branch_dependency",
        "ann_valid_verifier_integrity",
        "ann_valid_retention_policy",
    }
    for ann_id in expected_completed:
        row = results[ann_id]
        assert row["merge_status"] == "abi_admissible", row
        assert row["validator_status"] == "accepted", row
        assert row["validator_source"] == "scripts.validate_memory_object_abi.classify", row
        assert row["selected_option"] in {"B_memory_object_aware_runtime", "C_trajectory_dag_memory_fabric"}, row
        assert as_int(row["downstream_memory_action_count"]) > 0, row
        assert row["runtime_prototype_consistency"] == "supported_by_runtime_policy_decisions", row
        assert row["constrained_planner_consistency"] == "supported_by_memory_plan_actions", row

    completed_ids = {row["case_id"].split("__", 1)[1] for row in completed}
    assert expected_completed <= completed_ids

    conflict_reasons = {row["conflict_reason"] for row in conflicts}
    for reason in [
        "reuse_scope_widens_trace_security_scope",
        "tenant_or_security_scope_widening",
        "provenance_mismatch",
        "branch_parent_unresolved_or_conflicting",
        "verifier_target_not_observed",
        "lossy_compression_for_correctness_critical_object",
        "durable_retention_without_policy",
        "production_evidence_label_not_runtime_abi",
    ]:
        assert reason in conflict_reasons, reason
    for row in conflicts:
        assert row["fail_closed"] == "true", row
        assert as_int(row["downstream_memory_action_count"]) == 0, row
        result = results[row["annotation_id"]]
        assert result["merge_status"] == "fail_closed", result
        assert as_int(result["runtime_action_count"]) == 0, result
        assert as_int(result["planner_action_count"]) == 0, result
        assert boundary[row["annotation_id"]]["boundary_result"] == "fail_closed_zero_actions", result

    assert results["ann_invalid_reuse_scope_widen"]["merge_status"] == "fail_closed"
    assert results["ann_invalid_lossy_correctness"]["validator_status"] == "rejected"
    assert results["ann_valid_branch_dependency"]["selected_option"] == "C_trajectory_dag_memory_fabric"
    assert results["ann_invalid_branch_parent_conflict"]["selected_option"] == "A_conventional_request_model_kv_serving"

    opt_a = results["ann_option_a_none"]
    assert opt_a["merge_status"] == "option_a_opaque_fallback", opt_a
    assert opt_a["validator_status"] == "not_run", opt_a
    assert opt_a["option_a_fallback_executable"] == "true", opt_a
    assert as_int(opt_a["downstream_memory_action_count"]) == 0, opt_a

    for row in results.values():
        for field in ["production_calibrated", "production_ready", "threshold_success", "causal_validity_granted", "claim_credit_allowed"]:
            assert row[field] == "false", row

    require_text(
        ROOT / "memory-centric-agentic" / "memory_object_annotation_contract.md",
        [
            "constraints, not trust",
            "trace lift -> annotation requirements -> annotation merge -> ABI validation -> integration replay -> action gating",
            "fails closed",
            "Option A",
            "production_calibrated=false",
        ],
    )
    assert_nonblank_png(DATA / "memory_object_annotation_status.png")
    assert_nonblank_png(DATA / "memory_object_annotation_conflicts.png")
    assert_nonblank_png(DATA / "memory_object_annotation_option_boundary.png")
    print("OK: memory-object annotations verified.")


if __name__ == "__main__":
    main()
