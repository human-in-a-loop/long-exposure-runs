#!/usr/bin/env python3
# created: 2026-05-12T19:10:00Z
# cycle: 40
# run_id: run-2026-05-11T121649Z
# agent: worker
# milestone: M-ABI-1
"""Verify memory-object ABI and fail-closed planner contract."""

from __future__ import annotations

import csv
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

EXPECTED_CLASSES = {
    "weights",
    "KV cache",
    "prompt prefix",
    "retrieved context",
    "tool output",
    "branch state",
    "verifier state",
    "trajectory log",
    "durable workspace artifact",
    "semantic cache entry",
}

INVALID_CASES = {
    "missing_object_class": "missing_object_class",
    "missing_producer_id": "missing_mandatory_field_producer_id",
    "missing_lineage_provenance": "missing_lineage_or_provenance",
    "missing_tenant_id": "missing_mandatory_field_tenant_id",
    "missing_reuse_scope": "missing_mandatory_field_reuse_scope",
    "missing_security_label": "missing_mandatory_field_security_label",
    "tenant_reuse_scope_mismatch": "tenant_reuse_scope_mismatch",
    "impossible_lifetime_interval": "impossible_lifetime_interval",
    "dangling_branch_parent": "dangling_branch_parent",
    "verifier_without_checked_target": "verifier_state_without_checked_target",
    "tool_output_without_freshness_source": "tool_output_without_freshness_source",
    "missing_compression_policy": "missing_mandatory_field_compression_policy",
    "invalid_compression_policy": "invalid_compression_policy",
    "lossy_compression_correctness_critical": "lossy_compression_for_correctness_critical_object",
    "residency_hint_exceeds_allowed_tier": "residency_hint_exceeds_allowed_tier",
    "durable_retention_without_policy": "durable_retention_without_policy",
    "missing_evidence_label": "missing_mandatory_field_evidence_label",
    "production_evidence_label_in_runtime_abi": "production_evidence_label_not_runtime_abi",
    "planner_required_field_marked_advisory": "planner_required_field_absent_but_marked_advisory",
}


def run(script: str) -> None:
    subprocess.run([sys.executable, str(ROOT / script)], check=True)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
        rows = list(csv.DictReader(f))
    assert rows, f"{path.relative_to(ROOT)} is empty"
    return rows


def assert_nonblank_png(path: Path) -> None:
    assert path.exists(), f"missing {path.relative_to(ROOT)}"
    assert path.stat().st_size > 1000, f"blank or tiny figure: {path.relative_to(ROOT)}"


def main() -> None:
    run("scripts/build_memory_object_abi.py")
    run("scripts/validate_memory_object_abi.py")
    run("scripts/plot_memory_object_abi.py")

    classes = read_csv(DATA / "memory_object_abi_object_classes.csv")
    class_names = {row["object_class"] for row in classes}
    assert EXPECTED_CLASSES <= class_names

    schema_fields = {row["field"]: row for row in read_csv(DATA / "memory_object_abi_schema.csv")}
    for field in ["object_id", "object_class", "lineage_ids", "tenant_id", "reuse_scope", "security_label", "created_at_step", "expires_at_step", "compression_policy", "allowed_tiers", "evidence_label"]:
        assert field in schema_fields, field
    assert schema_fields["lineage_ids"]["requirement"] == "mandatory"

    results = {row["case_id"]: row for row in read_csv(DATA / "memory_object_abi_validation_results.csv")}
    assert all(row["matched_expected"] == "true" for row in results.values())
    for cls in EXPECTED_CLASSES:
        assert any(row["object_class"] == cls and row["observed_status"] == "accepted" for row in results.values()), cls
    for case_id, reason in INVALID_CASES.items():
        assert results[case_id]["observed_status"] == "rejected", case_id
        assert results[case_id]["primary_reason"] == reason, results[case_id]
    assert results["missing_advisory_residency_hint"]["observed_status"] == "accepted"
    assert results["missing_advisory_residency_hint"]["primary_reason"] == "planner_admissible"

    planner = {row["case_id"]: row for row in read_csv(DATA / "memory_object_abi_planner_boundary.csv")}
    for case_id in INVALID_CASES:
        row = planner[case_id]
        assert row["planner_boundary"] == "rejected", row
        assert row["placement_allowed"] == "false", row
        assert row["reuse_allowed"] == "false", row
        assert row["retention_allowed"] == "false", row
    assert planner["missing_advisory_residency_hint"]["planner_boundary"] == "accepted"
    assert planner["lossy_compression_correctness_critical"]["compression_allowed"] == "false"

    coverage = {row["object_class"]: row for row in read_csv(DATA / "memory_object_abi_option_coverage.csv")}
    for cls in ["weights", "KV cache", "prompt prefix"]:
        assert coverage[cls]["option_a_supported_without_object_abi"] == "true", cls
    for cls in ["retrieved context", "tool output", "semantic cache entry"]:
        assert coverage[cls]["option_b_requires_planner_admissible_object"] == "true", cls
    for cls in ["branch state", "verifier state", "trajectory log", "durable workspace artifact"]:
        assert coverage[cls]["option_c_requires_resolvable_dag_or_object"] == "true", cls
    for row in coverage.values():
        assert row["valid_example_present"] == "true", row
        assert row["production_calibrated"] == "false", row
        assert row["production_ready"] == "false", row
        assert row["threshold_success"] == "false", row
        assert row["causal_validity_granted"] == "false", row
        assert row["claim_credit_allowed"] == "false", row

    failures = {row["failure_mode"] for row in read_csv(DATA / "memory_object_abi_failure_modes.csv")}
    assert set(INVALID_CASES.values()) <= failures

    assert_nonblank_png(DATA / "memory_object_abi_coverage.png")
    assert_nonblank_png(DATA / "memory_object_abi_failure_modes.png")
    assert_nonblank_png(DATA / "memory_object_abi_planner_boundary.png")
    print("OK: memory-object ABI verified.")


if __name__ == "__main__":
    main()
