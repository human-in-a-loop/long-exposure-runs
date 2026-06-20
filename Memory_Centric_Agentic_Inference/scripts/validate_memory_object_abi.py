#!/usr/bin/env python3
# created: 2026-05-12T19:05:00Z
# cycle: 40
# run_id: run-2026-05-11T121649Z
# agent: worker
# milestone: M-ABI-1
"""Validate memory-object ABI examples and planner boundaries."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

IN_CLASSES = DATA / "memory_object_abi_object_classes.csv"
IN_EXAMPLES = DATA / "memory_object_abi_examples.jsonl"

OUT_RESULTS = DATA / "memory_object_abi_validation_results.csv"
OUT_FAILURES = DATA / "memory_object_abi_failure_modes.csv"
OUT_PLANNER = DATA / "memory_object_abi_planner_boundary.csv"
OUT_COVERAGE = DATA / "memory_object_abi_option_coverage.csv"

OPTION_A = "A_conventional_request_model_kv_serving"
OPTION_B = "B_memory_object_aware_runtime"
OPTION_C = "C_trajectory_dag_memory_fabric"

DAG_CLASSES = {"branch state", "verifier state", "trajectory log", "durable workspace artifact"}
FRESHNESS_CLASSES = {"retrieved context", "tool output", "semantic cache entry", "prompt prefix", "weights"}
DURABLE_CLASSES = {"trajectory log", "durable workspace artifact"}
COMPRESSION_POLICIES = {"none", "lossless", "lossy", "summary_pointer", "recompute"}
RUNTIME_EVIDENCE_LABELS = {"synthetic_contract", "internal_runtime_contract"}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        raise ValueError(f"{path.relative_to(ROOT)} is empty")
    return rows


def read_examples(path: Path) -> list[dict[str, Any]]:
    rows = []
    with path.open() as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    if not rows:
        raise ValueError(f"{path.relative_to(ROOT)} is empty")
    return rows


def write_csv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})
    print(f"wrote {path.relative_to(ROOT)} rows={len(rows)}")


def list_value(value: Any) -> list[str]:
    if value in ("", None):
        return []
    if isinstance(value, list):
        return [str(v) for v in value if str(v)]
    return [part.strip() for part in str(value).split(";") if part.strip()]


def step_value(value: Any) -> float:
    if value == "inf":
        return float("inf")
    return float(value)


def known_parent_ids(examples: list[dict[str, Any]]) -> set[str]:
    ids = {str(row["object_id"]) for row in examples if str(row.get("expected_status")) == "accepted"}
    ids |= {"kv:r0", "branch:b1", "tool-output:42", "request:r0", "model:llm-v1"}
    return ids


def classify(row: dict[str, Any], object_classes: set[str], parents: set[str]) -> tuple[str, str, str]:
    object_class = str(row.get("object_class", ""))
    overrides = row.get("field_override", {})
    if not object_class:
        return "rejected", "missing_object_class", "reject_before_planning"
    if object_class not in object_classes:
        return "rejected", "unknown_object_class", "reject_before_planning"
    for field in ("producer_id", "tenant_id", "reuse_scope", "security_label"):
        if not str(row.get(field, "")):
            return "rejected", f"missing_mandatory_field_{field}", "reject_before_planning"
    if not list_value(row.get("lineage_ids")):
        if isinstance(overrides, dict) and overrides.get("lineage_ids") == "advisory":
            return "rejected", "planner_required_field_absent_but_marked_advisory", "reject_before_planning"
        return "rejected", "missing_lineage_or_provenance", "reject_before_planning"
    tenant_id = str(row.get("tenant_id", ""))
    reuse_scope = str(row.get("reuse_scope", ""))
    if reuse_scope.startswith("tenant:") and reuse_scope.split(":", 1)[1] != tenant_id:
        return "rejected", "tenant_reuse_scope_mismatch", "reject_before_reuse"
    try:
        created = step_value(row.get("created_at_step"))
        expires = step_value(row.get("expires_at_step"))
        min_valid = step_value(row.get("min_valid_step"))
        max_valid = step_value(row.get("max_valid_step"))
    except (TypeError, ValueError):
        return "rejected", "invalid_lifetime_numeric_domain", "reject_before_planning"
    if created > expires or min_valid > max_valid:
        return "rejected", "impossible_lifetime_interval", "reject_before_planning"
    if created == expires and object_class not in {"trajectory log"}:
        return "rejected", "zero_lifetime_for_reusable_state", "reject_before_retention"
    if object_class in DAG_CLASSES:
        parent_ids = list_value(row.get("parent_object_ids"))
        if object_class in {"branch state", "verifier state"} and not parent_ids:
            return "rejected", "missing_branch_parent", "reject_before_dag_scheduling"
        for parent in parent_ids:
            if parent not in parents:
                return "rejected", "dangling_branch_parent", "reject_before_dag_scheduling"
    if object_class == "verifier state" and not str(row.get("checked_target_id", "")):
        return "rejected", "verifier_state_without_checked_target", "reject_before_dag_scheduling"
    if object_class in FRESHNESS_CLASSES and not str(row.get("freshness_source_id", "")):
        if object_class == "tool output":
            return "rejected", "tool_output_without_freshness_source", "reject_before_reuse"
        return "rejected", "missing_freshness_source", "reject_before_reuse"
    compression_policy = str(row.get("compression_policy", ""))
    if not compression_policy:
        return "rejected", "missing_mandatory_field_compression_policy", "reject_before_compression"
    if compression_policy not in COMPRESSION_POLICIES:
        return "rejected", "invalid_compression_policy", "reject_before_compression"
    if str(row.get("correctness_critical")).lower() == "true" and row.get("compression_policy") == "lossy":
        return "rejected", "lossy_compression_for_correctness_critical_object", "reject_before_compression"
    residency_hint = str(row.get("residency_hint", ""))
    if residency_hint and residency_hint not in set(list_value(row.get("allowed_tiers"))):
        return "rejected", "residency_hint_exceeds_allowed_tier", "reject_before_placement"
    if (object_class in DURABLE_CLASSES or row.get("expires_at_step") == "inf" or row.get("max_valid_step") == "inf") and not str(row.get("retention_policy_id", "")):
        return "rejected", "durable_retention_without_policy", "reject_before_retention"
    evidence_label = str(row.get("evidence_label", ""))
    if not evidence_label:
        return "rejected", "missing_mandatory_field_evidence_label", "reject_before_planning"
    if evidence_label == "production_target":
        return "rejected", "production_evidence_label_not_runtime_abi", "reject_before_planning"
    if evidence_label not in RUNTIME_EVIDENCE_LABELS:
        return "rejected", "invalid_runtime_evidence_label", "reject_before_planning"
    if object_class in DAG_CLASSES:
        return "accepted", "planner_admissible", "admit_for_option_c_dag_planning"
    return "accepted", "planner_admissible", "admit_for_option_b_object_planning"


def option_coverage(class_rows: list[dict[str, str]], results: list[dict[str, object]]) -> list[dict[str, object]]:
    accepted_classes = {str(row["object_class"]) for row in results if row["observed_status"] == "accepted"}
    out = []
    for row in class_rows:
        cls = row["object_class"]
        options = set(row["architecture_options"].split("/"))
        out.append(
            {
                "object_class": cls,
                "option_a_supported_without_object_abi": str("A" in options).lower(),
                "option_b_requires_planner_admissible_object": str("B" in options and cls not in {"weights", "KV cache", "prompt prefix"}).lower(),
                "option_c_requires_resolvable_dag_or_object": str("C" in options and cls in accepted_classes).lower(),
                "valid_example_present": str(cls in accepted_classes).lower(),
                "production_calibrated": "false",
                "production_ready": "false",
                "threshold_success": "false",
                "causal_validity_granted": "false",
                "claim_credit_allowed": "false",
            }
        )
    return out


def main() -> None:
    class_rows = read_csv(IN_CLASSES)
    object_classes = {row["object_class"] for row in class_rows}
    examples = read_examples(IN_EXAMPLES)
    parents = known_parent_ids(examples)
    results = []
    planner = []
    for row in examples:
        status, reason, action = classify(row, object_classes, parents)
        matched = status == row["expected_status"] and (status == "accepted" or reason == row["expected_reason"])
        results.append(
            {
                "case_id": row["case_id"],
                "object_id": row["object_id"],
                "object_class": row.get("object_class", ""),
                "expected_status": row["expected_status"],
                "observed_status": status,
                "matched_expected": str(matched).lower(),
                "primary_reason": reason,
                "planner_action": action,
                "evidence_label": row["evidence_label"],
            }
        )
        planner.append(
            {
                "case_id": row["case_id"],
                "contract_state": "complete_safe_contract" if status == "accepted" else reason,
                "planner_boundary": "accepted" if status == "accepted" else "rejected",
                "placement_allowed": str(status == "accepted").lower(),
                "reuse_allowed": str(status == "accepted").lower(),
                "compression_allowed": str(status == "accepted" and row.get("compression_policy") != "lossy").lower(),
                "retention_allowed": str(status == "accepted").lower(),
                "planner_action": action,
                "production_calibrated": "false",
                "production_ready": "false",
                "threshold_success": "false",
                "causal_validity_granted": "false",
                "claim_credit_allowed": "false",
            }
        )
    failures = Counter(str(row["primary_reason"]) for row in results if row["observed_status"] != "accepted")
    failure_rows = [{"failure_mode": key, "count": value} for key, value in sorted(failures.items())]
    coverage = option_coverage(class_rows, results)
    write_csv(OUT_RESULTS, results, list(results[0]))
    write_csv(OUT_FAILURES, failure_rows, ["failure_mode", "count"])
    write_csv(OUT_PLANNER, planner, list(planner[0]))
    write_csv(OUT_COVERAGE, coverage, list(coverage[0]))


if __name__ == "__main__":
    main()
