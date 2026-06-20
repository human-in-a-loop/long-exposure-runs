#!/usr/bin/env python3
# created: 2026-05-12T19:02:00Z
# cycle: 40
# run_id: run-2026-05-11T121649Z
# agent: worker
# milestone: M-ABI-1
"""Build memory-object ABI schema, class maps, and contract examples."""

from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

OUT_SCHEMA = DATA / "memory_object_abi_schema.csv"
OUT_CLASSES = DATA / "memory_object_abi_object_classes.csv"
OUT_LIFETIME = DATA / "memory_object_abi_lifetime_hints.csv"
OUT_SECURITY = DATA / "memory_object_abi_security_fields.csv"
OUT_EXAMPLES = DATA / "memory_object_abi_examples.jsonl"


ABI_FIELDS = [
    ("object_id", "string", "mandatory", "all", "stable object identifier inside the agent run"),
    ("object_class", "enum", "mandatory", "all", "validated memory-object class"),
    ("producer_id", "string", "mandatory", "all", "runtime/compiler/tool/verifier component that produced the object"),
    ("lineage_ids", "list", "mandatory", "B/C", "parent object, source, request, or artifact ids needed for provenance"),
    ("tenant_id", "string", "mandatory", "B/C", "tenant or isolation domain for reuse authorization"),
    ("reuse_scope", "enum", "mandatory", "B/C", "private_run, tenant, deployment, or public_immutable"),
    ("security_label", "enum", "mandatory", "B/C", "isolation and sensitivity label bound to policy"),
    ("created_at_step", "integer", "mandatory", "B/C", "logical creation step"),
    ("expires_at_step", "integer_or_inf", "mandatory", "B/C", "logical expiry bound; inf only for durable policy"),
    ("min_valid_step", "integer", "mandatory", "B/C", "earliest step where the object may be reused"),
    ("max_valid_step", "integer_or_inf", "mandatory", "B/C", "latest step where the object may be reused"),
    ("correctness_critical", "boolean", "mandatory", "B/C", "whether lossy transformation can change correctness"),
    ("compression_policy", "enum", "mandatory", "B/C", "none, lossless, lossy, summary_pointer, or recompute"),
    ("residency_hint", "enum", "advisory", "B/C", "preferred tier; must not exceed class-allowed tier"),
    ("allowed_tiers", "list", "mandatory", "B/C", "tiers permitted by class, policy, and security"),
    ("retention_policy_id", "string", "mandatory_if_durable", "durable", "required for durable or infinite-retention objects"),
    ("branch_id", "string", "mandatory_if_branch", "C", "branch membership for branch/verifier/trajectory objects"),
    ("parent_object_ids", "list", "mandatory_if_branch", "C", "parent memory objects in the trajectory DAG"),
    ("checked_target_id", "string", "mandatory_if_verifier", "C", "object or branch checked by verifier state"),
    ("freshness_source_id", "string", "mandatory_if_tool_or_retrieval", "B/C", "source version, tool run, retrieval index, or invalidation source"),
    ("evidence_label", "enum", "mandatory", "all", "synthetic_contract or internal_runtime_contract only; not production_target"),
]


OBJECT_CLASSES = [
    ("weights", "A/B/C", "model_version", "HBM/GPU memory; CPU DRAM; NVMe", "lossless", "no"),
    ("KV cache", "A/B/C", "request_or_branch_interval", "HBM/GPU memory; CPU DRAM; pooled memory", "lossless", "no"),
    ("prompt prefix", "A/B/C", "prefix_identity_window", "HBM/GPU memory; CPU DRAM; shared cache service", "lossless", "no"),
    ("retrieved context", "B/C", "source_version_window", "CPU DRAM; NVMe; remote object store", "summary_pointer", "no"),
    ("tool output", "B/C", "tool_freshness_window", "CPU DRAM; NVMe; durable workspace store; remote object store", "summary_pointer", "maybe"),
    ("branch state", "C", "branch_survival_interval", "HBM/GPU memory; CPU DRAM; NVMe", "lossless", "no"),
    ("verifier state", "C", "verification_validity_window", "CPU DRAM; NVMe; durable workspace store", "lossless", "maybe"),
    ("trajectory log", "C", "run_retention_window", "NVMe; durable workspace store; remote object store", "lossless", "yes"),
    ("durable workspace artifact", "C", "retention_policy_window", "durable workspace store; remote object store; NVMe", "summary_pointer", "yes"),
    ("semantic cache entry", "B/C", "invalidation_policy_window", "CPU DRAM; shared cache service; NVMe", "summary_pointer", "no"),
]


LIFETIME_HINTS = [
    ("instantaneous_event", "created_at_step == expires_at_step", "valid only for log/event objects; rejected for reusable state"),
    ("bounded_interval", "created_at_step < expires_at_step", "normal reusable object interval"),
    ("branch_bound", "expires_at_step follows branch merge/discard", "requires branch_id and parent_object_ids"),
    ("verifier_bound", "expires_at_step follows checked target validity", "requires checked_target_id"),
    ("freshness_bound", "expires_at_step follows source invalidation", "requires freshness_source_id"),
    ("durable_policy_bound", "expires_at_step may be inf", "requires retention_policy_id"),
]


SECURITY_FIELDS = [
    ("tenant_id", "mandatory", "blocks cross-tenant reuse when absent or mismatched"),
    ("reuse_scope", "mandatory", "private_run < tenant < deployment < public_immutable; planner may narrow but not widen"),
    ("security_label", "mandatory", "binds object to isolation/provenance policy"),
    ("lineage_ids", "mandatory", "prevents untraceable reuse, retention, or compression"),
    ("freshness_source_id", "mandatory for tool/retrieval/cache", "prevents stale tool and retrieval reuse"),
    ("retention_policy_id", "mandatory for durable/infinite retention", "prevents unbounded durable storage"),
]


BASE = {
    "producer_id": "runtime_registry",
    "lineage_ids": ["request:r0"],
    "tenant_id": "tenant_alpha",
    "reuse_scope": "tenant",
    "security_label": "tenant_confidential",
    "created_at_step": 0,
    "expires_at_step": 128,
    "min_valid_step": 0,
    "max_valid_step": 128,
    "correctness_critical": False,
    "compression_policy": "lossless",
    "residency_hint": "CPU DRAM",
    "allowed_tiers": ["HBM/GPU memory", "CPU DRAM", "NVMe", "remote object store"],
    "retention_policy_id": "",
    "branch_id": "",
    "parent_object_ids": [],
    "checked_target_id": "",
    "freshness_source_id": "source:v1",
    "evidence_label": "synthetic_contract",
}


VALID_EXAMPLES = [
    ("valid_weights", "weights", {"freshness_source_id": "model:llm-v1", "residency_hint": "HBM/GPU memory"}),
    ("valid_kv_cache", "KV cache", {"lineage_ids": ["request:r0", "model:llm-v1"], "reuse_scope": "private_run", "freshness_source_id": ""}),
    ("valid_prompt_prefix", "prompt prefix", {"lineage_ids": ["prefix:system-v1"], "freshness_source_id": "prefix:system-v1"}),
    ("valid_retrieved_context", "retrieved context", {"lineage_ids": ["retrieval:q7", "index:docs-v4"], "freshness_source_id": "index:docs-v4", "compression_policy": "summary_pointer"}),
    ("valid_tool_output", "tool output", {"lineage_ids": ["tool:web-check:42"], "freshness_source_id": "tool-run:42", "compression_policy": "summary_pointer"}),
    ("valid_branch_state", "branch state", {"branch_id": "branch:b1", "parent_object_ids": ["kv:r0"], "lineage_ids": ["branch-parent:root"], "correctness_critical": True}),
    ("valid_verifier_state", "verifier state", {"branch_id": "branch:b1", "parent_object_ids": ["branch:b1"], "checked_target_id": "tool-output:42", "correctness_critical": True}),
    ("valid_trajectory_log", "trajectory log", {"expires_at_step": "inf", "max_valid_step": "inf", "retention_policy_id": "retain:run-log-30d", "lineage_ids": ["run:agent-7"], "compression_policy": "lossless"}),
    ("valid_durable_workspace_artifact", "durable workspace artifact", {"expires_at_step": "inf", "max_valid_step": "inf", "retention_policy_id": "retain:workspace-90d", "lineage_ids": ["workspace:file-a"], "compression_policy": "summary_pointer"}),
    ("valid_semantic_cache_entry", "semantic cache entry", {"lineage_ids": ["semantic-key:k9", "index:docs-v4"], "freshness_source_id": "invalidation-policy:docs-v4", "compression_policy": "summary_pointer"}),
]


INVALID_EXAMPLES = [
    ("missing_object_class", "", {"object_class": ""}, "missing_object_class"),
    ("missing_producer_id", "retrieved context", {"producer_id": ""}, "missing_mandatory_field_producer_id"),
    ("missing_lineage_provenance", "retrieved context", {"lineage_ids": []}, "missing_lineage_or_provenance"),
    ("missing_tenant_id", "retrieved context", {"tenant_id": ""}, "missing_mandatory_field_tenant_id"),
    ("missing_reuse_scope", "retrieved context", {"reuse_scope": ""}, "missing_mandatory_field_reuse_scope"),
    ("missing_security_label", "retrieved context", {"security_label": ""}, "missing_mandatory_field_security_label"),
    ("tenant_reuse_scope_mismatch", "semantic cache entry", {"tenant_id": "tenant_alpha", "reuse_scope": "tenant:tenant_beta"}, "tenant_reuse_scope_mismatch"),
    ("impossible_lifetime_interval", "KV cache", {"created_at_step": 20, "expires_at_step": 10}, "impossible_lifetime_interval"),
    ("dangling_branch_parent", "branch state", {"branch_id": "branch:b2", "parent_object_ids": ["missing:parent"]}, "dangling_branch_parent"),
    ("verifier_without_checked_target", "verifier state", {"branch_id": "branch:b1", "parent_object_ids": ["branch:b1"], "checked_target_id": ""}, "verifier_state_without_checked_target"),
    ("tool_output_without_freshness_source", "tool output", {"freshness_source_id": ""}, "tool_output_without_freshness_source"),
    ("missing_compression_policy", "retrieved context", {"compression_policy": ""}, "missing_mandatory_field_compression_policy"),
    ("invalid_compression_policy", "retrieved context", {"compression_policy": "magic_lossy"}, "invalid_compression_policy"),
    ("lossy_compression_correctness_critical", "verifier state", {"branch_id": "branch:b1", "parent_object_ids": ["branch:b1"], "correctness_critical": True, "compression_policy": "lossy", "checked_target_id": "branch:b1"}, "lossy_compression_for_correctness_critical_object"),
    ("residency_hint_exceeds_allowed_tier", "retrieved context", {"allowed_tiers": ["CPU DRAM", "NVMe"], "residency_hint": "HBM/GPU memory"}, "residency_hint_exceeds_allowed_tier"),
    ("missing_advisory_residency_hint", "retrieved context", {"residency_hint": ""}, "planner_admissible"),
    ("durable_retention_without_policy", "durable workspace artifact", {"expires_at_step": "inf", "max_valid_step": "inf", "retention_policy_id": ""}, "durable_retention_without_policy"),
    ("missing_evidence_label", "retrieved context", {"evidence_label": ""}, "missing_mandatory_field_evidence_label"),
    ("production_evidence_label_in_runtime_abi", "retrieved context", {"evidence_label": "production_target"}, "production_evidence_label_not_runtime_abi"),
    ("planner_required_field_marked_advisory", "semantic cache entry", {"lineage_ids": [], "field_override": {"lineage_ids": "advisory"}}, "planner_required_field_absent_but_marked_advisory"),
]


def write_csv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})
    print(f"wrote {path.relative_to(ROOT)} rows={len(rows)}")


def make_example(case_id: str, object_class: str, updates: dict[str, object], expected_status: str, expected_reason: str) -> dict[str, object]:
    row = dict(BASE)
    row.update({
        "case_id": case_id,
        "object_id": case_id.replace("valid_", "obj_").replace("missing_", "bad_"),
        "object_class": object_class,
        "expected_status": expected_status,
        "expected_reason": expected_reason,
    })
    row.update(updates)
    return row


def examples() -> list[dict[str, object]]:
    rows = [make_example(case_id, object_class, updates, "accepted", "planner_admissible") for case_id, object_class, updates in VALID_EXAMPLES]
    for case_id, object_class, updates, reason in INVALID_EXAMPLES:
        expected_status = "accepted" if case_id == "missing_advisory_residency_hint" else "rejected"
        rows.append(make_example(case_id, object_class, updates, expected_status, reason))
    return rows


def main() -> None:
    write_csv(
        OUT_SCHEMA,
        [{"field": a, "type": b, "requirement": c, "applies_to": d, "description": e} for a, b, c, d, e in ABI_FIELDS],
        ["field", "type", "requirement", "applies_to", "description"],
    )
    write_csv(
        OUT_CLASSES,
        [
            {
                "object_class": name,
                "architecture_options": options,
                "lifetime_driver": driver,
                "allowed_tiers": tiers,
                "safe_compression": compression,
                "durable_policy_required": durable,
            }
            for name, options, driver, tiers, compression, durable in OBJECT_CLASSES
        ],
        ["object_class", "architecture_options", "lifetime_driver", "allowed_tiers", "safe_compression", "durable_policy_required"],
    )
    write_csv(
        OUT_LIFETIME,
        [{"hint": a, "condition": b, "planner_semantics": c} for a, b, c in LIFETIME_HINTS],
        ["hint", "condition", "planner_semantics"],
    )
    write_csv(
        OUT_SECURITY,
        [{"field": a, "requirement": b, "fail_closed_semantics": c} for a, b, c in SECURITY_FIELDS],
        ["field", "requirement", "fail_closed_semantics"],
    )
    rows = examples()
    OUT_EXAMPLES.parent.mkdir(parents=True, exist_ok=True)
    with OUT_EXAMPLES.open("w") as f:
        for row in rows:
            f.write(json.dumps(row, sort_keys=True) + "\n")
    print(f"wrote {OUT_EXAMPLES.relative_to(ROOT)} rows={len(rows)}")


if __name__ == "__main__":
    main()
