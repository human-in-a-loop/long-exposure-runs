#!/usr/bin/env python3
# created: 2026-05-12T22:00:00Z
# cycle: 45
# run_id: run-2026-05-11T121649Z
# agent: worker
# milestone: M-ANNOT-1
"""Build annotation schema and fixtures for non-inferable ABI fields."""

from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

TRACE_CANDIDATES = DATA / "trace_to_abi_candidates.jsonl"
TRACE_RESULTS = DATA / "trace_to_abi_lift_results.csv"
TRACE_REQUIREMENTS = DATA / "trace_to_abi_annotation_requirements.csv"
ABI_SCHEMA = DATA / "memory_object_abi_schema.csv"

OUT_SCHEMA = DATA / "memory_object_annotation_schema.csv"
OUT_EXAMPLES = DATA / "memory_object_annotation_examples.jsonl"
OUT_REQUIREMENTS = DATA / "memory_object_annotation_requirements.csv"

ANNOTATION_CLASSES = [
    {
        "annotation_class": "reuse_scope_annotation",
        "fields_completed": "reuse_scope",
        "constraint_rule": "reuse_scope must be tenant-local or narrower than trace tenant/security evidence",
        "trusted_assertion": "false",
        "applies_to": "KV cache;semantic cache entry;prompt prefix",
    },
    {
        "annotation_class": "tenant_security_annotation",
        "fields_completed": "tenant_id;security_label;reuse_scope",
        "constraint_rule": "tenant and reuse scope cannot widen beyond trace tenant_id and security_label",
        "trusted_assertion": "false",
        "applies_to": "all",
    },
    {
        "annotation_class": "tool_provenance_annotation",
        "fields_completed": "lineage_ids;freshness_source_id",
        "constraint_rule": "lineage and freshness source must match observed tool/run provenance context",
        "trusted_assertion": "false",
        "applies_to": "tool output",
    },
    {
        "annotation_class": "branch_dependency_annotation",
        "fields_completed": "parent_object_ids;branch_id",
        "constraint_rule": "parents must resolve to known ABI parent ids before Option C actions",
        "trusted_assertion": "false",
        "applies_to": "branch state;verifier state;trajectory log",
    },
    {
        "annotation_class": "verifier_integrity_annotation",
        "fields_completed": "checked_target_id;lineage_ids",
        "constraint_rule": "checked target must be present in observed lineage or known ABI parent ids",
        "trusted_assertion": "false",
        "applies_to": "verifier state",
    },
    {
        "annotation_class": "compression_safety_annotation",
        "fields_completed": "compression_policy;correctness_critical",
        "constraint_rule": "lossy compression is rejected for correctness-critical objects",
        "trusted_assertion": "false",
        "applies_to": "all",
    },
    {
        "annotation_class": "retention_policy_annotation",
        "fields_completed": "retention_policy_id;expires_at_step;max_valid_step",
        "constraint_rule": "durable or infinite lifetime objects require a named retention policy",
        "trusted_assertion": "false",
        "applies_to": "durable workspace artifact;trajectory log",
    },
    {
        "annotation_class": "evidence_label_annotation",
        "fields_completed": "evidence_label",
        "constraint_rule": "synthetic/internal inputs cannot be upgraded to production_target",
        "trusted_assertion": "false",
        "applies_to": "all",
    },
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        raise ValueError(f"{path.relative_to(ROOT)} is empty")
    return rows


def read_jsonl(path: Path) -> list[dict[str, object]]:
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


def example(annotation_id: str, target_case_id: str, annotation_class: str, fields: dict[str, object], valid: bool, reason: str) -> dict[str, object]:
    return {
        "annotation_id": annotation_id,
        "target_case_id": target_case_id,
        "annotation_class": annotation_class,
        "annotation_source": "developer_runtime_fixture",
        "fields": fields,
        "expected_valid": valid,
        "expected_reason": "constraint_satisfied" if valid else reason,
        "production_calibrated": False,
        "production_ready": False,
        "threshold_success": False,
        "causal_validity_granted": False,
        "claim_credit_allowed": False,
    }


def build_examples() -> list[dict[str, object]]:
    rows = [
        example("ann_valid_reuse_scope_kv", "legacy_kv_cache_uncertain_reuse_scope", "reuse_scope_annotation", {"reuse_scope": "tenant"}, True, ""),
        example("ann_invalid_reuse_scope_widen", "legacy_kv_cache_uncertain_reuse_scope", "reuse_scope_annotation", {"reuse_scope": "global"}, False, "reuse_scope_widens_trace_security_scope"),
        example("ann_valid_tenant_security", "legacy_retrieved_context_rag", "tenant_security_annotation", {"tenant_id": "tenant_alpha", "security_label": "tenant_confidential", "reuse_scope": "tenant"}, True, ""),
        example("ann_invalid_tenant_widen", "legacy_retrieved_context_rag", "tenant_security_annotation", {"tenant_id": "tenant_beta", "security_label": "public", "reuse_scope": "global"}, False, "tenant_or_security_scope_widening"),
        example("ann_valid_tool_provenance", "legacy_tool_output_missing_provenance", "tool_provenance_annotation", {"lineage_ids": ["tool:weather-run-42", "trace:request-7"], "freshness_source_id": "tool:weather-run-42"}, True, ""),
        example("ann_invalid_tool_provenance_mismatch", "legacy_tool_output_missing_provenance", "tool_provenance_annotation", {"lineage_ids": ["tool:other-run"], "freshness_source_id": "tool:other-run"}, False, "provenance_mismatch"),
        example("ann_valid_branch_dependency", "legacy_branch_state_dangling_parent", "branch_dependency_annotation", {"parent_object_ids": ["branch:b1"], "branch_id": "branch:lifted-b1"}, True, ""),
        example("ann_invalid_branch_parent_conflict", "legacy_branch_state_dangling_parent", "branch_dependency_annotation", {"parent_object_ids": ["missing:parent-branch"], "branch_id": "branch:lifted-b1"}, False, "branch_parent_unresolved_or_conflicting"),
        example("ann_valid_verifier_integrity", "legacy_verifier_state_missing_integrity_annotation", "verifier_integrity_annotation", {"checked_target_id": "tool-output:42", "lineage_ids": ["trace:branch-b1", "tool-output:42"]}, True, ""),
        example("ann_invalid_verifier_target_mismatch", "legacy_verifier_state_missing_integrity_annotation", "verifier_integrity_annotation", {"checked_target_id": "tool-output:unknown"}, False, "verifier_target_not_observed"),
        example("ann_valid_compression_safety", "legacy_branch_state_dangling_parent", "compression_safety_annotation", {"compression_policy": "lossless", "correctness_critical": True}, True, ""),
        example("ann_invalid_lossy_correctness", "legacy_branch_state_dangling_parent", "compression_safety_annotation", {"compression_policy": "lossy", "correctness_critical": True}, False, "lossy_compression_for_correctness_critical_object"),
        example("ann_valid_retention_policy", "legacy_durable_workspace_missing_retention", "retention_policy_annotation", {"retention_policy_id": "retention:workspace-ttl-30d"}, True, ""),
        example("ann_invalid_infinite_retention_no_policy", "legacy_durable_workspace_missing_retention", "retention_policy_annotation", {"retention_policy_id": ""}, False, "durable_retention_without_policy"),
        example("ann_valid_evidence_label", "legacy_kv_cache_uncertain_reuse_scope", "evidence_label_annotation", {"evidence_label": "internal_runtime_contract"}, True, ""),
        example("ann_invalid_production_upgrade", "legacy_kv_cache_uncertain_reuse_scope", "evidence_label_annotation", {"evidence_label": "production_target"}, False, "production_evidence_label_not_runtime_abi"),
        example("ann_option_a_none", "option_a_opaque_legacy_request", "evidence_label_annotation", {"evidence_label": "internal_runtime_contract"}, True, ""),
    ]
    return rows


def main() -> None:
    candidates = read_jsonl(TRACE_CANDIDATES)
    results = read_csv(TRACE_RESULTS)
    requirements = read_csv(TRACE_REQUIREMENTS)
    abi_fields = {row["field"] for row in read_csv(ABI_SCHEMA)}

    for row in ANNOTATION_CLASSES:
        for field in str(row["fields_completed"]).split(";"):
            if field and field not in abi_fields:
                raise ValueError(f"annotation field not in ABI schema: {field}")

    requirement_rows = []
    result_by_case = {row["case_id"]: row for row in results}
    for req in requirements:
        requirement_rows.append(
            {
                "case_id": req["case_id"],
                "object_class": req["object_class"],
                "required_annotation_field": req["required_annotation"],
                "source_lift_reason": req["reason"],
                "annotation_classes_allowed": ";".join(row["annotation_class"] for row in ANNOTATION_CLASSES if req["required_annotation"] in row["fields_completed"].split(";")),
                "trace_lift_status": result_by_case[req["case_id"]]["lift_status"],
                "downstream_actions_blocked_until_validated_annotation": "true",
            }
        )
    requirement_rows.append(
        {
            "case_id": "legacy_tool_output_missing_provenance",
            "object_class": "tool output",
            "required_annotation_field": "lineage_ids;freshness_source_id",
            "source_lift_reason": "missing_lineage_or_provenance",
            "annotation_classes_allowed": "tool_provenance_annotation",
            "trace_lift_status": result_by_case["legacy_tool_output_missing_provenance"]["lift_status"],
            "downstream_actions_blocked_until_validated_annotation": "true",
        }
    )
    requirement_rows.append(
        {
            "case_id": "legacy_branch_state_dangling_parent",
            "object_class": "branch state",
            "required_annotation_field": "parent_object_ids",
            "source_lift_reason": "dangling_branch_parent",
            "annotation_classes_allowed": "branch_dependency_annotation",
            "trace_lift_status": result_by_case["legacy_branch_state_dangling_parent"]["lift_status"],
            "downstream_actions_blocked_until_validated_annotation": "true",
        }
    )

    write_csv(OUT_SCHEMA, ANNOTATION_CLASSES, list(ANNOTATION_CLASSES[0]))
    with OUT_EXAMPLES.open("w") as f:
        for row in build_examples():
            f.write(json.dumps(row, sort_keys=True) + "\n")
    print(f"wrote {OUT_EXAMPLES.relative_to(ROOT)} rows={len(build_examples())}")
    write_csv(OUT_REQUIREMENTS, requirement_rows, list(requirement_rows[0]))
    if len(candidates) < 1:
        raise ValueError("trace candidate set unexpectedly empty")


if __name__ == "__main__":
    main()
