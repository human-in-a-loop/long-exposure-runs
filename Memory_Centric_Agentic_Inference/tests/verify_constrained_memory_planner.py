# created: 2026-05-11T23:00:00Z
# cycle: 18
# run_id: run-2026-05-11T121649Z
# agent: worker
# milestone: M-PLAN-1

"""Verify M-PLAN-1 constrained memory-planner artifacts."""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

REQUIRED_ACTION_FIELDS = {
    "workload_class",
    "object_id",
    "object_class",
    "selected_option",
    "action",
    "tier",
    "compression_strategy",
    "validation_required",
    "security_decision",
    "constraint_binding",
    "net_plan_value",
    "evidence_label",
}
REQUIRED_CONSTRAINTS = {
    "capacity",
    "security_gate",
    "validation_overhead",
    "queueing_overhead",
    "contention_tail",
    "compression_unsafe",
}
CONTROL_WORKLOADS = {
    "single-turn chat control",
    "batch summarization/offline inference control",
}
OPTION_A = "A_conventional_request_model_kv_serving"
REUSE_ACTIONS = {"keep_hot", "offload_warm", "offload_cold", "compress_or_pointer_preserve"}
BASELINE_CLASSES = {"weights", "KV cache", "intermediate scratch"}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
        rows = list(csv.DictReader(f))
    assert rows, f"{path} is empty"
    return rows


def fnum(value: str) -> float:
    return float(value or 0.0)


def assert_png_nonblank(path: Path) -> None:
    data = path.read_bytes()
    assert data.startswith(b"\x89PNG\r\n\x1a\n"), f"{path} is not a PNG"
    assert len(data) > 10_000, f"{path} is too small to be a useful figure"


def main() -> None:
    actions = read_csv(DATA / "memory_plan_actions.csv")
    summary = read_csv(DATA / "memory_plan_workload_summary.csv")
    infeasible = read_csv(DATA / "memory_plan_infeasible_cases.csv")
    hook_ablation = read_csv(DATA / "memory_plan_hook_ablation.csv")
    sensitivity = read_csv(DATA / "memory_plan_constraint_sensitivity.csv")
    safety_failures = read_csv(DATA / "compression_safety_failures.csv")

    assert REQUIRED_ACTION_FIELDS <= set(actions[0]), set(actions[0])
    workloads = {row["workload_class"] for row in actions}
    object_classes = {row["object_class"] for row in actions if row["object_class"]}
    assert len(workloads) == 6, workloads
    assert len(object_classes) >= 7, object_classes

    action_set = {row["action"] for row in actions}
    assert {"keep_hot", "compress_or_pointer_preserve", "recompute_or_drop"} <= action_set
    assert action_set & {"offload_warm", "offload_cold"}, action_set
    assert REQUIRED_CONSTRAINTS <= {row["constraint_binding"] for row in actions}

    object_action_keys = [
        (
            row["workload_class"],
            row["object_id"],
            row["object_class"],
            row["selected_option"],
            row["action"],
            row["tier"],
            row["compression_strategy"],
            row["security_decision"],
            row["constraint_binding"],
        )
        for row in actions
    ]
    assert len(object_action_keys) == len(set(object_action_keys)), "duplicate object/action plan rows"

    for row in summary:
        if row["workload_class"] in CONTROL_WORKLOADS:
            assert row["planned_option"] == OPTION_A, row
            assert int(row["positive_reuse_rows"]) == 0, row

    for row in actions:
        if row["workload_class"] in CONTROL_WORKLOADS and row["object_class"] in BASELINE_CLASSES:
            assert row["action"] == "keep_hot", row
            assert row["tier"] == "HBM/GPU memory", row
            assert fnum(row["safe_reuse_credit"]) == 0.0, row

    denied = [row for row in actions if row["security_decision"] == "denied_reuse"]
    assert denied, "expected denied security rows"
    for row in denied:
        assert row["action"] == "recompute_or_drop", row
        assert fnum(row["safe_reuse_credit"]) == 0.0, row
        assert row["constraint_binding"] == "security_gate", row

    unsafe_keys = {
        (row["workload_class"], row["object_class"], row["strategy"])
        for row in safety_failures
        if row["valid"] == "false"
    }
    selected_unsafe = [
        row for row in actions
        if (row["workload_class"], row["object_class"], row["compression_strategy"]) in unsafe_keys
    ]
    assert not selected_unsafe, selected_unsafe[:3]

    for row in infeasible:
        assert row["constraint_binding"] not in {"", "value_positive"}, row

    collapsing = [
        row for row in sensitivity
        if row["baseline_option"].startswith("C_") and not row["planned_option"].startswith("C_")
    ]
    assert collapsing, "expected at least one C-to-B/A collapse"

    causal_hooks = [row for row in hook_ablation if int(row["blocked_reuse_actions"]) > 0]
    assert len(causal_hooks) >= 5, causal_hooks

    for fig in [
        DATA / "memory_plan_action_mix.png",
        DATA / "memory_plan_constraint_breakdown.png",
        DATA / "memory_plan_option_transitions.png",
    ]:
        assert_png_nonblank(fig)

    print("verify_constrained_memory_planner: ok")


if __name__ == "__main__":
    main()
