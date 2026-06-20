#!/usr/bin/env python3
# created: 2026-05-12T20:00:00Z
# cycle: 41
# run_id: run-2026-05-11T121649Z
# agent: worker
# milestone: M-ABIINT-1
"""Replay ABI validation results through runtime/planner action gates."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

EXAMPLES = DATA / "memory_object_abi_examples.jsonl"
VALIDATION = DATA / "memory_object_abi_validation_results.csv"
RUNTIME_DECISIONS = DATA / "runtime_policy_decisions.csv"
PLANNER_ACTIONS = DATA / "memory_plan_actions.csv"

OUT_RESULTS = DATA / "memory_object_abi_integration_results.csv"
OUT_RUNTIME = DATA / "memory_object_abi_runtime_actions.csv"
OUT_PLANNER = DATA / "memory_object_abi_planner_actions.csv"
OUT_FAILURES = DATA / "memory_object_abi_integration_failure_modes.csv"
OUT_BOUNDARY = DATA / "memory_object_abi_option_boundary.csv"

OPTION_A = "A_conventional_request_model_kv_serving"
OPTION_B = "B_memory_object_aware_runtime"
OPTION_C = "C_trajectory_dag_memory_fabric"

DAG_CLASSES = {"branch state", "verifier state", "trajectory log", "durable workspace artifact"}
OPTION_A_OBJECTS = {"weights", "KV cache", "prompt prefix"}
DOWNSTREAM_ACTIONS = {"placement", "reuse", "compression", "migration", "retention"}
PLANNER_ACTION_SUPPORT = {
    "placement": {"keep_hot", "offload_warm", "offload_cold", "compress_or_pointer_preserve"},
    "reuse": {"keep_hot", "offload_warm", "offload_cold", "compress_or_pointer_preserve"},
    "compression": {"compress_or_pointer_preserve"},
    "migration": {"offload_warm", "offload_cold"},
    "retention": {"keep_hot", "offload_warm", "offload_cold", "compress_or_pointer_preserve"},
}


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


def bool_text(value: bool) -> str:
    return str(value).lower()


def list_value(value: Any) -> list[str]:
    if value in ("", None):
        return []
    if isinstance(value, list):
        return [str(v) for v in value if str(v)]
    return [part.strip() for part in str(value).split(";") if part.strip()]


def option_capabilities(runtime_rows: list[dict[str, str]], planner_rows: list[dict[str, str]]) -> dict[str, object]:
    runtime_options = {
        row["runtime_architecture_option"]
        for row in runtime_rows
        if row.get("runtime_architecture_option")
    }
    planner_options = {
        option
        for row in planner_rows
        for option in (row.get("selected_option", ""), row.get("baseline_option", ""))
        if option
    }
    planner_actions = {row["action"] for row in planner_rows if row.get("action")}
    required_options = {OPTION_A, OPTION_B, OPTION_C}
    missing_runtime = required_options - runtime_options
    missing_planner = required_options - planner_options
    missing_actions = {
        action_type
        for action_type, supported_actions in PLANNER_ACTION_SUPPORT.items()
        if not (supported_actions & planner_actions)
    }
    if missing_runtime:
        raise ValueError(f"runtime prototype outputs lack options: {sorted(missing_runtime)}")
    if missing_planner:
        raise ValueError(f"constrained planner outputs lack options: {sorted(missing_planner)}")
    if missing_actions:
        raise ValueError(f"constrained planner outputs lack action support for: {sorted(missing_actions)}")
    return {
        "runtime_options": runtime_options,
        "planner_options": planner_options,
        "planner_actions": planner_actions,
    }


def runtime_consistency(option: str, admitted: bool, case_id: str, capabilities: dict[str, object]) -> str:
    runtime_options = capabilities["runtime_options"]
    if not admitted:
        return "not_checked_rejected_before_runtime"
    if case_id == "option_a_opaque_baseline":
        return "opaque_supported_by_runtime_policy_decisions"
    return "supported_by_runtime_policy_decisions" if option in runtime_options else "unsupported_runtime_option"


def planner_consistency(option: str, plans: list[dict[str, object]], admitted: bool, case_id: str, capabilities: dict[str, object]) -> str:
    planner_options = capabilities["planner_options"]
    planner_actions = capabilities["planner_actions"]
    if not admitted:
        return "not_checked_rejected_before_planner"
    if case_id == "option_a_opaque_baseline":
        return "opaque_supported_by_memory_plan_actions" if option in planner_options else "unsupported_planner_option"
    required = {
        str(plan["downstream_action_type"])
        for plan in plans
        if str(plan["downstream_action_type"]) in DOWNSTREAM_ACTIONS
    }
    unsupported = {
        action_type
        for action_type in required
        if not (PLANNER_ACTION_SUPPORT[action_type] & planner_actions)
    }
    if option not in planner_options:
        return "unsupported_planner_option"
    if unsupported:
        return "unsupported_planner_action_vocab:" + ";".join(sorted(unsupported))
    return "supported_by_memory_plan_actions"


def choose_option(case_id: str, object_class: str, status: str) -> str:
    if case_id == "option_a_opaque_baseline":
        return OPTION_A
    if object_class in DAG_CLASSES:
        return OPTION_C
    if status == "accepted" and object_class in OPTION_A_OBJECTS:
        return OPTION_A
    return OPTION_B


def default_tier(row: dict[str, Any]) -> tuple[str, str]:
    hint = str(row.get("residency_hint", ""))
    if hint:
        return hint, "residency_hint"
    tiers = list_value(row.get("allowed_tiers"))
    if "CPU DRAM" in tiers:
        return "CPU DRAM", "default_no_residency_hint"
    return (tiers[0] if tiers else "not_placed", "default_first_allowed_tier")


def runtime_action_rows(case_id: str, row: dict[str, Any], option: str, admitted: bool) -> list[dict[str, object]]:
    if option == OPTION_A and case_id == "option_a_opaque_baseline":
        return [
            {
                "case_id": case_id,
                "object_id": "opaque_request",
                "object_class": "opaque request/model/KV serving state",
                "selected_option": option,
                "action_type": "opaque_execute",
                "action": "serve_without_memory_object_abi",
                "tier": "baseline_serving_path",
                "emitted": "true",
                "evidence_label": "synthetic_integration",
            }
        ]
    if not admitted:
        return []
    tier, reason = default_tier(row)
    object_class = str(row["object_class"])
    actions = [
        ("placement", f"place:{tier}", tier),
        ("reuse", "authorize_scope:" + str(row.get("reuse_scope", "")), tier),
        ("compression", "compression_policy:" + str(row.get("compression_policy", "none")), tier),
        ("retention", "retain_until:" + str(row.get("expires_at_step", "")), tier),
    ]
    if option == OPTION_C:
        actions.insert(1, ("migration", "resolve_branch_dependencies", tier))
    if reason.startswith("default"):
        actions[0] = ("placement", f"place:{tier}:{reason}", tier)
    return [
        {
            "case_id": case_id,
            "object_id": row["object_id"],
            "object_class": object_class,
            "selected_option": option,
            "action_type": action_type,
            "action": action,
            "tier": tier,
            "emitted": "true",
            "evidence_label": "synthetic_integration",
        }
        for action_type, action, tier in actions
    ]


def planner_action_rows(case_id: str, row: dict[str, Any], option: str, admitted: bool) -> list[dict[str, object]]:
    if option == OPTION_A and case_id == "option_a_opaque_baseline":
        return [
            {
                "case_id": case_id,
                "object_id": "opaque_request",
                "object_class": "opaque request/model/KV serving state",
                "selected_option": option,
                "planner_action": "baseline_request_schedule",
                "constraint_binding": "option_a_opaque",
                "downstream_action_type": "opaque_execute",
                "emitted": "true",
                "production_calibrated": "false",
                "production_ready": "false",
                "threshold_success": "false",
                "causal_validity_granted": "false",
                "claim_credit_allowed": "false",
            }
        ]
    if not admitted:
        return []
    tier, reason = default_tier(row)
    planner_action = "admit_for_option_c_dag_planning" if option == OPTION_C else "admit_for_option_b_object_planning"
    return [
        {
            "case_id": case_id,
            "object_id": row["object_id"],
            "object_class": row["object_class"],
            "selected_option": option,
            "planner_action": planner_action,
            "constraint_binding": reason,
            "downstream_action_type": action_type,
            "emitted": "true",
            "production_calibrated": "false",
            "production_ready": "false",
            "threshold_success": "false",
            "causal_validity_granted": "false",
            "claim_credit_allowed": "false",
        }
        for action_type in (["placement", "migration", "reuse", "compression", "retention"] if option == OPTION_C else ["placement", "reuse", "compression", "retention"])
    ]


def selected_cases(examples: list[dict[str, Any]]) -> list[dict[str, Any]]:
    wanted = {
        "valid_retrieved_context",
        "valid_branch_state",
        "missing_advisory_residency_hint",
        "missing_object_class",
        "tenant_reuse_scope_mismatch",
        "lossy_compression_correctness_critical",
        "dangling_branch_parent",
        "durable_retention_without_policy",
        "production_evidence_label_in_runtime_abi",
    }
    rows = [row for row in examples if row["case_id"] in wanted]
    rows.append(
        {
            "case_id": "option_a_opaque_baseline",
            "object_id": "",
            "object_class": "",
            "expected_status": "accepted",
            "evidence_label": "synthetic_integration",
            "allowed_tiers": [],
            "residency_hint": "",
        }
    )
    return rows


def main() -> None:
    examples = {row["case_id"]: row for row in read_examples(EXAMPLES)}
    validation = {row["case_id"]: row for row in read_csv(VALIDATION)}
    capabilities = option_capabilities(read_csv(RUNTIME_DECISIONS), read_csv(PLANNER_ACTIONS))

    integration_rows: list[dict[str, object]] = []
    runtime_rows: list[dict[str, object]] = []
    planner_rows: list[dict[str, object]] = []
    boundary_rows: list[dict[str, object]] = []

    for row in selected_cases(list(examples.values())):
        case_id = str(row["case_id"])
        observed = "accepted" if case_id == "option_a_opaque_baseline" else validation[case_id]["observed_status"]
        reason = "option_a_opaque" if case_id == "option_a_opaque_baseline" else validation[case_id]["primary_reason"]
        object_class = str(row.get("object_class", ""))
        option = choose_option(case_id, object_class, observed)
        admitted = bool(observed == "accepted" and (option == OPTION_A or case_id == "option_a_opaque_baseline" or object_class))
        actions = runtime_action_rows(case_id, row, option, admitted)
        plans = planner_action_rows(case_id, row, option, admitted)
        runtime_support = runtime_consistency(option, admitted, case_id, capabilities)
        planner_support = planner_consistency(option, plans, admitted, case_id, capabilities)
        downstream_count = sum(1 for action in actions if action["action_type"] in DOWNSTREAM_ACTIONS)
        tier, placement_reason = default_tier(row)
        rejected = observed != "accepted"
        integration_rows.append(
            {
                "case_id": case_id,
                "object_id": row.get("object_id", ""),
                "object_class": object_class or "opaque request/model/KV serving state",
                "selected_option": option,
                "abi_status": observed,
                "primary_reason": reason,
                "admitted_to_runtime": bool_text(admitted),
                "runtime_action_count": len(actions),
                "planner_action_count": len(plans),
                "downstream_memory_action_count": downstream_count,
                "placement_policy": placement_reason if admitted else "none_fail_closed",
                "selected_tier": tier if admitted else "not_placed",
                "runtime_prototype_consistency": runtime_support,
                "constrained_planner_consistency": planner_support,
                "integration_source": "abi_validation_plus_runtime_policy_decisions_plus_memory_plan_actions",
                "option_boundary": "opaque_baseline" if case_id == "option_a_opaque_baseline" else ("object_admitted" if admitted else "abi_rejected"),
                "production_calibrated": "false",
                "production_ready": "false",
                "threshold_success": "false",
                "causal_validity_granted": "false",
                "claim_credit_allowed": "false",
            }
        )
        boundary_rows.append(
            {
                "case_id": case_id,
                "selected_option": option,
                "abi_contract_state": "opaque_absent" if case_id == "option_a_opaque_baseline" else observed,
                "option_a_executable": bool_text(option == OPTION_A and case_id == "option_a_opaque_baseline"),
                "option_b_requires_admissible_object": bool_text(option == OPTION_B),
                "option_c_requires_admissible_dag": bool_text(option == OPTION_C),
                "object_level_admissible": bool_text(admitted and option in {OPTION_B, OPTION_C}),
                "downstream_memory_action_count": downstream_count,
                "runtime_prototype_consistency": runtime_support,
                "constrained_planner_consistency": planner_support,
                "boundary_result": "allowed_opaque" if case_id == "option_a_opaque_baseline" else ("allowed_object_actions" if admitted else "blocked_before_actions"),
                "production_calibrated": "false",
                "production_ready": "false",
                "threshold_success": "false",
                "causal_validity_granted": "false",
                "claim_credit_allowed": "false",
            }
        )
        runtime_rows.extend(actions)
        planner_rows.extend(plans)
        if rejected:
            assert downstream_count == 0, f"{case_id} emitted downstream actions"

    failures = Counter(str(row["primary_reason"]) for row in integration_rows if row["abi_status"] == "rejected")
    failure_rows = [
        {"failure_mode": reason, "blocked_case_count": count, "downstream_memory_action_count": 0}
        for reason, count in sorted(failures.items())
    ]

    write_csv(
        OUT_RESULTS,
        integration_rows,
        [
            "case_id",
            "object_id",
            "object_class",
            "selected_option",
            "abi_status",
            "primary_reason",
            "admitted_to_runtime",
            "runtime_action_count",
            "planner_action_count",
            "downstream_memory_action_count",
            "placement_policy",
            "selected_tier",
            "runtime_prototype_consistency",
            "constrained_planner_consistency",
            "integration_source",
            "option_boundary",
            "production_calibrated",
            "production_ready",
            "threshold_success",
            "causal_validity_granted",
            "claim_credit_allowed",
        ],
    )
    write_csv(
        OUT_RUNTIME,
        runtime_rows,
        ["case_id", "object_id", "object_class", "selected_option", "action_type", "action", "tier", "emitted", "evidence_label"],
    )
    write_csv(
        OUT_PLANNER,
        planner_rows,
        [
            "case_id",
            "object_id",
            "object_class",
            "selected_option",
            "planner_action",
            "constraint_binding",
            "downstream_action_type",
            "emitted",
            "production_calibrated",
            "production_ready",
            "threshold_success",
            "causal_validity_granted",
            "claim_credit_allowed",
        ],
    )
    write_csv(OUT_FAILURES, failure_rows, ["failure_mode", "blocked_case_count", "downstream_memory_action_count"])
    write_csv(
        OUT_BOUNDARY,
        boundary_rows,
        [
            "case_id",
            "selected_option",
            "abi_contract_state",
            "option_a_executable",
            "option_b_requires_admissible_object",
            "option_c_requires_admissible_dag",
            "object_level_admissible",
            "downstream_memory_action_count",
            "runtime_prototype_consistency",
            "constrained_planner_consistency",
            "boundary_result",
            "production_calibrated",
            "production_ready",
            "threshold_success",
            "causal_validity_granted",
            "claim_credit_allowed",
        ],
    )


if __name__ == "__main__":
    main()
