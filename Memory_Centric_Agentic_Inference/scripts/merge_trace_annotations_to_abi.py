#!/usr/bin/env python3
# created: 2026-05-12T22:05:00Z
# cycle: 45
# run_id: run-2026-05-11T121649Z
# agent: worker
# milestone: M-ANNOT-1
"""Merge validated annotations into trace-derived ABI candidates."""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
sys.path.insert(0, str(ROOT / "scripts"))

from validate_memory_object_abi import classify, known_parent_ids, read_examples  # noqa: E402
from integrate_memory_object_abi import (  # noqa: E402
    option_capabilities,
    planner_action_rows,
    planner_consistency,
    runtime_action_rows,
    runtime_consistency,
)

IN_CANDIDATES = DATA / "trace_to_abi_candidates.jsonl"
IN_LIFT = DATA / "trace_to_abi_lift_results.csv"
IN_ANNOTATIONS = DATA / "memory_object_annotation_examples.jsonl"
ABI_CLASSES = DATA / "memory_object_abi_object_classes.csv"
ABI_EXAMPLES = DATA / "memory_object_abi_examples.jsonl"
RUNTIME_DECISIONS = DATA / "runtime_policy_decisions.csv"
PLANNER_ACTIONS = DATA / "memory_plan_actions.csv"

OUT_RESULTS = DATA / "annotation_merge_results.csv"
OUT_COMPLETED = DATA / "annotation_completed_abi_candidates.jsonl"
OUT_CONFLICTS = DATA / "annotation_conflict_failures.csv"
OUT_INTEGRATION = DATA / "annotation_integration_results.csv"
OUT_BOUNDARY = DATA / "annotation_option_boundary.csv"

PRODUCTION_FIELDS = ["production_calibrated", "production_ready", "threshold_success", "causal_validity_granted", "claim_credit_allowed"]
DOWNSTREAM_ACTIONS = {"placement", "reuse", "compression", "migration", "retention"}
DAG_CLASSES = {"branch state", "verifier state", "trajectory log", "durable workspace artifact"}
OPTION_A = "A_conventional_request_model_kv_serving"
OPTION_B = "B_memory_object_aware_runtime"
OPTION_C = "C_trajectory_dag_memory_fabric"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        raise ValueError(f"{path.relative_to(ROOT)} is empty")
    return rows


def read_jsonl(path: Path) -> list[dict[str, Any]]:
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


def bool_text(value: bool) -> str:
    return str(value).lower()


def list_value(value: Any) -> list[str]:
    if value in ("", None):
        return []
    if isinstance(value, list):
        return [str(v) for v in value if str(v)]
    return [part.strip() for part in str(value).split(";") if part.strip()]


def selected_option(row: dict[str, Any], admitted: bool, opaque: bool = False) -> str:
    if opaque or not admitted:
        return OPTION_A
    return OPTION_C if row.get("object_class") in DAG_CLASSES else OPTION_B


def validate_annotation(candidate: dict[str, Any], ann: dict[str, Any], parents: set[str]) -> tuple[bool, str]:
    fields = ann["fields"]
    cls = ann["annotation_class"]
    if ann["target_case_id"] == "option_a_opaque_legacy_request":
        return True, "option_a_opaque_no_annotation_required"
    if cls == "reuse_scope_annotation":
        scope = str(fields.get("reuse_scope", ""))
        if scope not in {"request", "tenant", f"tenant:{candidate.get('tenant_id')}"}:
            return False, "reuse_scope_widens_trace_security_scope"
    elif cls == "tenant_security_annotation":
        if fields.get("tenant_id") != candidate.get("tenant_id") or fields.get("security_label") != candidate.get("security_label") or fields.get("reuse_scope") == "global":
            return False, "tenant_or_security_scope_widening"
    elif cls == "tool_provenance_annotation":
        lineage = set(list_value(fields.get("lineage_ids")))
        source = str(fields.get("freshness_source_id", ""))
        if not source or source not in lineage or "trace:request-7" not in lineage:
            return False, "provenance_mismatch"
    elif cls == "branch_dependency_annotation":
        parents_supplied = set(list_value(fields.get("parent_object_ids")))
        if not parents_supplied or not parents_supplied <= parents:
            return False, "branch_parent_unresolved_or_conflicting"
    elif cls == "verifier_integrity_annotation":
        target = str(fields.get("checked_target_id", ""))
        if target not in parents:
            return False, "verifier_target_not_observed"
    elif cls == "compression_safety_annotation":
        if str(fields.get("correctness_critical", candidate.get("correctness_critical"))).lower() == "true" and fields.get("compression_policy") == "lossy":
            return False, "lossy_compression_for_correctness_critical_object"
    elif cls == "retention_policy_annotation":
        if not str(fields.get("retention_policy_id", "")):
            return False, "durable_retention_without_policy"
    elif cls == "evidence_label_annotation":
        if fields.get("evidence_label") == "production_target":
            return False, "production_evidence_label_not_runtime_abi"
    return True, "constraint_satisfied"


def merged_candidate(candidate: dict[str, Any], ann: dict[str, Any]) -> dict[str, Any]:
    out = dict(candidate)
    out.update(ann["fields"])
    out["case_id"] = f"{candidate['case_id']}__{ann['annotation_id']}"
    out["object_id"] = f"{candidate.get('object_id', candidate['case_id'])}#annotated:{ann['annotation_id']}"
    out["producer_id"] = candidate.get("producer_id") or "annotation_merge"
    out["evidence_label"] = out.get("evidence_label") or "internal_runtime_contract"
    return out


def main() -> None:
    object_classes = {row["object_class"] for row in read_csv(ABI_CLASSES)}
    parents = known_parent_ids(read_examples(ABI_EXAMPLES))
    candidates = {row["case_id"]: row for row in read_jsonl(IN_CANDIDATES)}
    lift = {row["case_id"]: row for row in read_csv(IN_LIFT)}
    annotations = read_jsonl(IN_ANNOTATIONS)
    capabilities = option_capabilities(read_csv(RUNTIME_DECISIONS), read_csv(PLANNER_ACTIONS))

    results: list[dict[str, object]] = []
    conflicts: list[dict[str, object]] = []
    integrations: list[dict[str, object]] = []
    boundaries: list[dict[str, object]] = []
    completed: list[dict[str, Any]] = []

    for ann in annotations:
        target = str(ann["target_case_id"])
        candidate = candidates[target]
        opaque = target == "option_a_opaque_legacy_request"
        ok, ann_reason = validate_annotation(candidate, ann, parents)
        merged = merged_candidate(candidate, ann) if ok and not opaque else dict(candidate)
        validator_status = "not_run" if opaque else "rejected"
        validator_reason = "not_run_opaque_fallback" if opaque else ann_reason
        if ok and not opaque:
            abi_status, abi_reason, _ = classify(merged, object_classes, parents)
            validator_status = "accepted" if abi_status == "accepted" else "rejected"
            validator_reason = abi_reason
            ok = abi_status == "accepted"
        route = selected_option(merged, ok, opaque)
        runtime_actions = runtime_action_rows(str(ann["annotation_id"]), merged, route, ok and not opaque)
        planner_actions = planner_action_rows(str(ann["annotation_id"]), merged, route, ok and not opaque)
        action_count = sum(1 for row in runtime_actions if row["action_type"] in DOWNSTREAM_ACTIONS)
        if ok and not opaque:
            completed.append(merged)
        if not ok:
            conflicts.append(
                {
                    "annotation_id": ann["annotation_id"],
                    "target_case_id": target,
                    "annotation_class": ann["annotation_class"],
                    "conflict_reason": ann_reason if ann_reason != "constraint_satisfied" else validator_reason,
                    "downstream_memory_action_count": 0,
                    "fail_closed": "true",
                }
            )
        row = {
            "annotation_id": ann["annotation_id"],
            "target_case_id": target,
            "object_class": candidate.get("object_class", "opaque request/model/KV serving state") or "opaque request/model/KV serving state",
            "source_lift_status": lift[target]["lift_status"],
            "annotation_class": ann["annotation_class"],
            "annotation_constraint_status": "accepted" if ok or opaque else "rejected",
            "annotation_reason": ann_reason,
            "validator_status": validator_status,
            "validator_reason": validator_reason,
            "validator_source": "scripts.validate_memory_object_abi.classify" if not opaque else "not_run_for_opaque_option_a",
            "merge_status": "abi_admissible" if ok and not opaque else ("option_a_opaque_fallback" if opaque else "fail_closed"),
            "selected_option": route,
            "downstream_memory_action_count": action_count,
            "runtime_action_count": len(runtime_actions),
            "planner_action_count": len(planner_actions),
            "runtime_prototype_consistency": runtime_consistency(route, ok and not opaque, str(ann["annotation_id"]), capabilities),
            "constrained_planner_consistency": planner_consistency(route, planner_actions, ok and not opaque, str(ann["annotation_id"]), capabilities),
            "option_a_fallback_executable": bool_text(opaque or not ok),
        }
        for field in PRODUCTION_FIELDS:
            row[field] = "false"
        results.append(row)
        integrations.append(row)
        boundaries.append(
            {
                "annotation_id": ann["annotation_id"],
                "target_case_id": target,
                "merge_status": row["merge_status"],
                "selected_option": route,
                "option_a_fallback_executable": row["option_a_fallback_executable"],
                "option_b_or_c_requires_validated_abi": bool_text(route in {OPTION_B, OPTION_C}),
                "downstream_memory_action_count": action_count,
                "boundary_result": "validated_annotation_actions" if ok and not opaque else ("opaque_execute" if opaque else "fail_closed_zero_actions"),
            }
        )

    write_csv(OUT_RESULTS, results, list(results[0]))
    with OUT_COMPLETED.open("w") as f:
        for row in completed:
            f.write(json.dumps(row, sort_keys=True) + "\n")
    print(f"wrote {OUT_COMPLETED.relative_to(ROOT)} rows={len(completed)}")
    write_csv(OUT_CONFLICTS, conflicts, list(conflicts[0]))
    write_csv(OUT_INTEGRATION, integrations, list(integrations[0]))
    write_csv(OUT_BOUNDARY, boundaries, list(boundaries[0]))


if __name__ == "__main__":
    main()
