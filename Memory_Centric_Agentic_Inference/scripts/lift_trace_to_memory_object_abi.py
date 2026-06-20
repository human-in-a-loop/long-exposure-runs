#!/usr/bin/env python3
# created: 2026-05-12T18:15:00Z
# cycle: 44
# run_id: run-2026-05-11T121649Z
# agent: worker
# milestone: M-TRACEABI-1
"""Lift conventional trace/runtime/planner artifacts into ABI candidates."""

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

TRACE_SOURCES = [
    DATA / "synthetic_trace_v2.csv",
    DATA / "synthetic_trace_v3.csv",
    DATA / "security_trace_v3.csv",
]
RUNTIME_DECISIONS = DATA / "runtime_policy_decisions.csv"
PLANNER_ACTIONS = DATA / "memory_plan_actions.csv"
ABI_CLASSES = DATA / "memory_object_abi_object_classes.csv"
ABI_EXAMPLES = DATA / "memory_object_abi_examples.jsonl"

OUT_CANDIDATES = DATA / "trace_to_abi_candidates.jsonl"
OUT_RESULTS = DATA / "trace_to_abi_lift_results.csv"
OUT_MISSING = DATA / "trace_to_abi_missing_fields.csv"
OUT_FALLBACKS = DATA / "trace_to_abi_option_fallbacks.csv"
OUT_ANNOTATIONS = DATA / "trace_to_abi_annotation_requirements.csv"

PRODUCTION_FIELDS = [
    "production_calibrated",
    "production_ready",
    "threshold_success",
    "causal_validity_granted",
    "claim_credit_allowed",
]

DOWNSTREAM_ACTIONS = {"placement", "reuse", "compression", "migration", "retention"}
ANNOTATION_FAILURES = {
    "missing_mandatory_field_reuse_scope",
    "missing_mandatory_field_security_label",
    "verifier_state_without_checked_target",
    "durable_retention_without_policy",
}
DAG_CLASSES = {"branch state", "verifier state", "trajectory log", "durable workspace artifact"}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
        rows = list(csv.DictReader(f))
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


def runtime_support() -> dict[str, str]:
    rows = read_csv(RUNTIME_DECISIONS)
    by_class = {row["object_class"]: row for row in rows if row.get("object_class")}
    return {
        "runtime_options": ";".join(sorted({row["runtime_architecture_option"] for row in rows if row.get("runtime_architecture_option")})),
        "kv_source_id": by_class.get("KV cache", rows[0])["object_id"],
        "prefix_source_id": by_class.get("prefix cache", by_class.get("prompt prefix", rows[0]))["object_id"],
        "evidence_label": "internal_runtime_contract",
    }


def planner_support() -> dict[str, str]:
    rows = read_csv(PLANNER_ACTIONS)
    return {
        "planner_options": ";".join(sorted({row["selected_option"] for row in rows if row.get("selected_option")})),
        "planner_actions": ";".join(sorted({row["action"] for row in rows if row.get("action")})),
    }


def base(case_id: str, object_class: str, **updates: object) -> dict[str, object]:
    row: dict[str, object] = {
        "case_id": case_id,
        "object_id": case_id.replace("legacy_", "trace:").replace("_", "-"),
        "object_class": object_class,
        "producer_id": "legacy_trace_lifter",
        "lineage_ids": ["trace:request-7"],
        "tenant_id": "tenant_alpha",
        "reuse_scope": "tenant",
        "security_label": "tenant_confidential",
        "created_at_step": 0,
        "expires_at_step": 64,
        "min_valid_step": 0,
        "max_valid_step": 64,
        "correctness_critical": False,
        "compression_policy": "lossless",
        "residency_hint": "CPU DRAM",
        "allowed_tiers": ["HBM/GPU memory", "CPU DRAM", "NVMe", "remote object store"],
        "retention_policy_id": "",
        "branch_id": "",
        "parent_object_ids": [],
        "checked_target_id": "",
        "freshness_source_id": "trace:source-v1",
        "evidence_label": "internal_runtime_contract",
        "trace_source_kind": "legacy_runtime_planner_fixture",
        "field_derivation_summary": "",
        "expected_lift_status": "",
    }
    row.update(updates)
    return row


def conventional_rows() -> list[dict[str, object]]:
    runtime = runtime_support()
    planner = planner_support()
    no_trace_note = "canonical_trace_csv_absent; derived from runtime_policy_decisions and memory_plan_actions fixtures"
    return [
        base(
            "legacy_prompt_prefix_context_segment",
            "prompt prefix",
            lineage_ids=["trace:request-7", runtime["prefix_source_id"]],
            freshness_source_id="trace:prompt-template-v2",
            field_derivation_summary="prompt identity, tenant, lifetime, and source version derived from request/runtime trace",
            expected_lift_status="abi_admissible",
        ),
        base(
            "legacy_retrieved_context_rag",
            "retrieved context",
            lineage_ids=["trace:retrieval-q7", "index:docs-v4"],
            freshness_source_id="index:docs-v4",
            compression_policy="summary_pointer",
            field_derivation_summary="retrieval index id and freshness source are present in RAG-like trace",
            expected_lift_status="abi_admissible",
        ),
        base(
            "legacy_tool_output_missing_provenance",
            "tool output",
            lineage_ids=[],
            freshness_source_id="",
            compression_policy="summary_pointer",
            field_derivation_summary="tool output value observed but source run/provenance missing",
            expected_lift_status="fail_closed",
        ),
        base(
            "legacy_kv_cache_uncertain_reuse_scope",
            "KV cache",
            lineage_ids=["trace:request-7", runtime["kv_source_id"]],
            reuse_scope="",
            freshness_source_id="",
            field_derivation_summary="KV object observed but reuse authorization scope is absent from conventional trace",
            expected_lift_status="annotation_required",
        ),
        base(
            "legacy_branch_state_dangling_parent",
            "branch state",
            branch_id="branch:lifted-b1",
            parent_object_ids=["missing:parent-branch"],
            lineage_ids=["trace:branch-b1"],
            correctness_critical=True,
            field_derivation_summary="branch id observed but parent/dependency object is unresolved",
            expected_lift_status="fail_closed",
        ),
        base(
            "legacy_verifier_state_missing_integrity_annotation",
            "verifier state",
            branch_id="branch:lifted-b1",
            parent_object_ids=["branch:b1"],
            checked_target_id="",
            correctness_critical=True,
            field_derivation_summary="verifier event observed but checked target and integrity binding require runtime annotation",
            expected_lift_status="annotation_required",
        ),
        base(
            "legacy_durable_workspace_missing_retention",
            "durable workspace artifact",
            expires_at_step="inf",
            max_valid_step="inf",
            retention_policy_id="",
            lineage_ids=["workspace:file-a"],
            compression_policy="summary_pointer",
            field_derivation_summary="durable artifact observed but retention policy is not inferable from request trace",
            expected_lift_status="annotation_required",
        ),
        base(
            "legacy_retrieved_context_advisory_no_residency",
            "retrieved context",
            lineage_ids=["trace:retrieval-q8", "index:docs-v4"],
            freshness_source_id="index:docs-v4",
            compression_policy="summary_pointer",
            residency_hint="",
            field_derivation_summary="advisory residency hint absent; validator-permitted default can be used after validation",
            expected_lift_status="abi_admissible",
        ),
        {
            "case_id": "option_a_opaque_legacy_request",
            "object_id": "opaque:request-7",
            "object_class": "",
            "trace_source_kind": "opaque_conventional_request",
            "field_derivation_summary": f"no ABI lifting attempted; Option A remains executable; {no_trace_note}; planner={planner['planner_actions']}",
            "expected_lift_status": "option_a_opaque_fallback",
        },
    ]


def missing_fields(row: dict[str, object], reason: str, status: str) -> list[dict[str, object]]:
    mapped: dict[str, tuple[str, str]] = {
        "missing_lineage_or_provenance": ("lineage_ids", "mandatory_provenance"),
        "tool_output_without_freshness_source": ("freshness_source_id", "mandatory_freshness"),
        "missing_mandatory_field_reuse_scope": ("reuse_scope", "mandatory_security_reuse"),
        "dangling_branch_parent": ("parent_object_ids", "mandatory_branch_dependency"),
        "verifier_state_without_checked_target": ("checked_target_id", "mandatory_verifier_integrity"),
        "durable_retention_without_policy": ("retention_policy_id", "mandatory_retention"),
        "planner_admissible": ("", ""),
        "option_a_opaque": ("all_abi_fields", "opaque_fallback"),
    }
    fields, category = mapped.get(reason, ("unknown", "validator_failure"))
    if status == "abi_admissible" and row.get("residency_hint", "") == "":
        fields, category = "residency_hint", "advisory_default_allowed"
    if not fields:
        return []
    return [
        {
            "case_id": row["case_id"],
            "object_class": row.get("object_class", "opaque request"),
            "field": field,
            "field_category": category,
            "validator_reason": reason,
            "lift_status": status,
            "defaulted": bool_text(category == "advisory_default_allowed"),
            "blocks_downstream_actions": bool_text(status in {"annotation_required", "fail_closed"}),
        }
        for field in str(fields).split(";")
    ]


def classify_lift(row: dict[str, object], object_classes: set[str], parents: set[str]) -> tuple[str, str, str]:
    if row["case_id"] == "option_a_opaque_legacy_request":
        return "option_a_opaque_fallback", "option_a_opaque", "not_run_opaque_fallback"
    abi_status, reason, action = classify(row, object_classes, parents)
    if abi_status == "accepted":
        return "abi_admissible", reason, action
    if reason in ANNOTATION_FAILURES:
        return "annotation_required", reason, "blocked_pending_annotation"
    return "fail_closed", reason, "blocked_non_liftable"


def option_route(row: dict[str, object], status: str) -> str:
    if status == "option_a_opaque_fallback":
        return "A_conventional_request_model_kv_serving"
    if status != "abi_admissible":
        return "A_conventional_request_model_kv_serving"
    return "C_trajectory_dag_memory_fabric" if row.get("object_class") in DAG_CLASSES else "B_memory_object_aware_runtime"


def main() -> None:
    class_rows = read_csv(ABI_CLASSES)
    object_classes = {row["object_class"] for row in class_rows}
    parents = known_parent_ids(read_examples(ABI_EXAMPLES))
    capabilities = option_capabilities(read_csv(RUNTIME_DECISIONS), read_csv(PLANNER_ACTIONS))
    trace_source = next((path for path in TRACE_SOURCES if path.exists()), None)
    trace_source_note = trace_source.name if trace_source else "no_canonical_trace_csv_found"

    candidates = conventional_rows()
    OUT_CANDIDATES.parent.mkdir(parents=True, exist_ok=True)
    with OUT_CANDIDATES.open("w") as f:
        for row in candidates:
            f.write(json.dumps(row, sort_keys=True) + "\n")
    print(f"wrote {OUT_CANDIDATES.relative_to(ROOT)} rows={len(candidates)}")

    results: list[dict[str, object]] = []
    missing: list[dict[str, object]] = []
    fallbacks: list[dict[str, object]] = []
    annotations: list[dict[str, object]] = []

    for row in candidates:
        status, reason, validator_action = classify_lift(row, object_classes, parents)
        selected_option = option_route(row, status)
        admitted = status == "abi_admissible"
        runtime_actions = runtime_action_rows(str(row["case_id"]), row, selected_option, admitted)
        planner_actions = planner_action_rows(str(row["case_id"]), row, selected_option, admitted)
        runtime_support = runtime_consistency(selected_option, admitted, str(row["case_id"]), capabilities)
        planner_support = planner_consistency(selected_option, planner_actions, admitted, str(row["case_id"]), capabilities)
        action_count = sum(1 for action in runtime_actions if action["action_type"] in DOWNSTREAM_ACTIONS)
        option_a_fallback = status != "abi_admissible" or selected_option.startswith("A_")
        source = "scripts.validate_memory_object_abi.classify" if status != "option_a_opaque_fallback" else "not_run_for_opaque_option_a"
        result = {
            "case_id": row["case_id"],
            "object_id": row.get("object_id", ""),
            "object_class": row.get("object_class", "opaque request/model/KV serving state") or "opaque request/model/KV serving state",
            "lift_status": status,
            "validator_status": "accepted" if status == "abi_admissible" else ("not_run" if status == "option_a_opaque_fallback" else "rejected"),
            "validator_reason": reason,
            "validator_source": source,
            "selected_option": selected_option,
            "option_a_fallback_executable": bool_text(option_a_fallback),
            "annotation_required": bool_text(status == "annotation_required"),
            "fail_closed": bool_text(status == "fail_closed"),
            "downstream_memory_action_count": action_count,
            "runtime_action_count": len(runtime_actions),
            "planner_action_count": len(planner_actions),
            "trace_source": trace_source_note,
            "evidence_label": row.get("evidence_label", "internal_runtime_contract"),
            "integration_boundary": "eligible_for_existing_abi_integration_replay" if status == "abi_admissible" else "blocked_before_integration_or_opaque_option_a",
            "runtime_prototype_consistency": runtime_support,
            "constrained_planner_consistency": planner_support,
            "integration_source": "trace_lift_plus_abi_validation_plus_runtime_policy_decisions_plus_memory_plan_actions",
        }
        for field in PRODUCTION_FIELDS:
            result[field] = "false"
        results.append(result)
        missing.extend(missing_fields(row, reason, status))
        if status == "annotation_required":
            annotations.append(
                {
                    "case_id": row["case_id"],
                    "object_class": row.get("object_class", ""),
                    "required_annotation": ";".join(m["field"] for m in missing_fields(row, reason, status)),
                    "reason": reason,
                    "downstream_actions_blocked_until_annotation": "true",
                }
            )
        fallbacks.append(
            {
                "case_id": row["case_id"],
                "lift_status": status,
                "selected_option": selected_option,
                "option_a_fallback_executable": bool_text(option_a_fallback),
                "option_b_or_c_requires_admissible_abi": bool_text(selected_option.startswith(("B_", "C_"))),
                "downstream_memory_action_count": action_count,
                "boundary_result": "admitted_object_actions" if status == "abi_admissible" else ("opaque_execute" if status == "option_a_opaque_fallback" else "fallback_without_memory_actions"),
            }
        )

    write_csv(OUT_RESULTS, results, list(results[0]))
    write_csv(
        OUT_MISSING,
        missing,
        ["case_id", "object_class", "field", "field_category", "validator_reason", "lift_status", "defaulted", "blocks_downstream_actions"],
    )
    write_csv(OUT_FALLBACKS, fallbacks, list(fallbacks[0]))
    write_csv(
        OUT_ANNOTATIONS,
        annotations,
        ["case_id", "object_class", "required_annotation", "reason", "downstream_actions_blocked_until_annotation"],
    )


if __name__ == "__main__":
    main()
