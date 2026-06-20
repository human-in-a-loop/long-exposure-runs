# created: 2026-05-11T22:45:00Z
# cycle: 18
# run_id: run-2026-05-11T121649Z
# agent: worker
# milestone: M-PLAN-1

"""Greedy constrained memory planner over trace-v3 security decisions.

The planner is intentionally inspectable: every object/action row carries a
single binding constraint and a synthetic-planning evidence label.
"""

from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

TRACE_V3 = DATA / "security_trace_v3_events.csv"
SECURITY_DECISIONS = DATA / "security_enforcement_decisions.csv"
HOOK_MATRIX = DATA / "runtime_compiler_hook_matrix.csv"
RUNTIME_DECISIONS = DATA / "runtime_policy_decisions.csv"
COMPRESSION_SCORES = DATA / "compression_strategy_scores.csv"
COMPRESSION_FAILURES = DATA / "compression_safety_failures.csv"
QUEUE_THRESHOLDS = DATA / "queueing_reversal_thresholds.csv"
CXL_THRESHOLDS = DATA / "cxl_contention_thresholds.csv"
ENERGY_SENSITIVITY = DATA / "energy_architecture_sensitivity.csv"

OUT_ACTIONS = DATA / "memory_plan_actions.csv"
OUT_SUMMARY = DATA / "memory_plan_workload_summary.csv"
OUT_INFEASIBLE = DATA / "memory_plan_infeasible_cases.csv"
OUT_HOOK_ABLATION = DATA / "memory_plan_hook_ablation.csv"
OUT_SENSITIVITY = DATA / "memory_plan_constraint_sensitivity.csv"

OPTION_A = "A_conventional_request_model_kv_serving"
OPTION_B = "B_memory_object_aware_runtime"
OPTION_C = "C_trajectory_dag_memory_fabric"

CONTROL_WORKLOADS = {
    "single-turn chat control",
    "batch summarization/offline inference control",
}
DAG_CLASSES = {"branch state", "verifier state", "trajectory log", "durable workspace"}
OBJECT_REUSE_CLASSES = {"prefix cache", "retrieved context", "semantic cache entry", "tool output"}
BASELINE_CLASSES = {"weights", "KV cache", "intermediate scratch"}
REUSE_ACTIONS = {"keep_hot", "offload_warm", "offload_cold", "compress_or_pointer_preserve"}

ACTION_FIELDS = [
    "workload_class",
    "object_id",
    "object_class",
    "selected_option",
    "baseline_option",
    "action",
    "tier",
    "compression_strategy",
    "validation_required",
    "security_decision",
    "constraint_binding",
    "net_plan_value",
    "safe_reuse_credit",
    "raw_reuse_credit",
    "validation_overhead",
    "queue_overhead",
    "contention_penalty",
    "compression_risk",
    "evidence_label",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        raise ValueError(f"{path} is empty")
    return rows


def write_csv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})
    print(f"wrote {path.relative_to(ROOT)} rows={len(rows)}")


def fnum(value: object, default: float = 0.0) -> float:
    try:
        if value in ("", None):
            return default
        return float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return default


def boolish(value: object) -> bool:
    return str(value).strip().lower() == "true"


def option_rank(option: str) -> int:
    return {OPTION_A: 0, OPTION_B: 1, OPTION_C: 2}.get(option, 0)


def rank_option(rank: int) -> str:
    return [OPTION_A, OPTION_B, OPTION_C][max(0, min(2, rank))]


def short_option(option: str) -> str:
    return {OPTION_A: "A", OPTION_B: "B", OPTION_C: "C"}.get(option, option[:1] or "A")


def load_runtime() -> dict[tuple[str, str], dict[str, str]]:
    return {
        (row["workload_class"], row["object_id"]): row
        for row in read_csv(RUNTIME_DECISIONS)
    }


def load_trace_sizes() -> dict[tuple[str, str], dict[str, str]]:
    rows: dict[tuple[str, str], dict[str, str]] = {}
    for row in read_csv(TRACE_V3):
        oid = row.get("object_id", "")
        cls = row.get("object_class", "")
        if not oid or not cls:
            continue
        key = (row["workload_class"], oid)
        current = rows.get(key)
        if current is None or fnum(row.get("size_units")) > fnum(current.get("size_units")):
            rows[key] = row
    return rows


def load_best_compression() -> tuple[dict[tuple[str, str], dict[str, str]], set[tuple[str, str, str]]]:
    valid: dict[tuple[str, str], dict[str, str]] = {}
    for row in read_csv(COMPRESSION_SCORES):
        if not boolish(row.get("valid")):
            continue
        key = (row["workload_class"], row["object_class"])
        if key not in valid or fnum(row["net_compression_value"]) > fnum(valid[key]["net_compression_value"]):
            valid[key] = row
    unsafe = {
        (row["workload_class"], row["object_class"], row["strategy"])
        for row in read_csv(COMPRESSION_FAILURES)
        if not boolish(row.get("valid"))
    }
    return valid, unsafe


def cxl_downgrade_map() -> dict[tuple[str, str], bool]:
    mapping: dict[tuple[str, str], bool] = defaultdict(bool)
    for row in read_csv(CXL_THRESHOLDS):
        if row["latency_percentile"] not in {"p95", "p99"}:
            continue
        if row["decision"] != "downgrade_warm_tier":
            continue
        for cls in [part.strip() for part in row["object_class"].split(";")]:
            mapping[(row["workload_class"], cls)] = True
    return mapping


def energy_collapse_map() -> dict[str, str]:
    collapse: dict[str, str] = {}
    for row in read_csv(ENERGY_SENSITIVITY):
        if row["dc002_setting"] not in {"DC002_pathological_p99", "DC002_high_p99"}:
            continue
        after = row["option_after"]
        if after in {"A", "B"}:
            collapse[row["workload_class"]] = after
    return collapse


def queue_threshold_labels() -> str:
    rows = read_csv(QUEUE_THRESHOLDS)
    return "; ".join(f"{row['comparison']}:{row['threshold']}" for row in rows)


DECISION_SEVERITY = {
    "denied_reuse": 4,
    "overhead_dominated_reuse": 3,
    "downgraded_reuse": 2,
    "safe_reuse": 1,
    "not_reuse_candidate": 0,
}


def join_unique(values: list[str]) -> str:
    parts: list[str] = []
    for value in values:
        for part in str(value).split(";"):
            part = part.strip()
            if part and part not in parts:
                parts.append(part)
    return "; ".join(parts)


def aggregate_security_decisions(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    grouped: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        if row.get("object_id") and row.get("object_class"):
            grouped[(row["workload_class"], row["object_id"])].append(row)

    aggregated: list[dict[str, str]] = []
    for (_workload, _object_id), group in sorted(grouped.items()):
        base = dict(group[0])
        decision = max(
            (row["validation_decision"] for row in group),
            key=lambda value: DECISION_SEVERITY.get(value, 0),
        )
        safe_total = sum(fnum(row.get("safe_reuse_credit")) for row in group)
        if decision == "denied_reuse":
            safe_total = 0.0
        base.update({
            "trace_id": join_unique([row.get("trace_id", "") for row in group]),
            "time_step": str(max(int(fnum(row.get("time_step"))) for row in group)),
            "event_type": "object_plan",
            "validation_gate_ids": join_unique([row.get("validation_gate_ids", "") for row in group]),
            "validation_decision": decision,
            "failed_gate_ids": join_unique([row.get("failed_gate_ids", "") for row in group]),
            "raw_reuse_credit": str(round(sum(fnum(row.get("raw_reuse_credit")) for row in group), 6)),
            "validation_overhead": str(round(sum(fnum(row.get("validation_overhead")) for row in group), 6)),
            "safe_reuse_credit": str(round(safe_total, 6)),
            "unsafe_positive_credit": str(any(boolish(row.get("unsafe_positive_credit")) for row in group)).lower(),
        })
        aggregated.append(base)
    return aggregated


AGGREGATE_SUM_FIELDS = {
    "net_plan_value",
    "safe_reuse_credit",
    "raw_reuse_credit",
    "validation_overhead",
    "queue_overhead",
    "contention_penalty",
    "compression_risk",
}


def aggregate_action_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    key_fields = [field for field in ACTION_FIELDS if field not in AGGREGATE_SUM_FIELDS]
    grouped: dict[tuple[object, ...], dict[str, object]] = {}
    for row in rows:
        key = tuple(row[field] for field in key_fields)
        if key not in grouped:
            grouped[key] = dict(row)
        else:
            current = grouped[key]
            for field in AGGREGATE_SUM_FIELDS:
                current[field] = round(fnum(current.get(field)) + fnum(row.get(field)), 6)
    return list(grouped.values())


def choose_plan(
    decision: dict[str, str],
    runtime: dict[str, str],
    trace: dict[str, str],
    compression: dict[str, str] | None,
    unsafe: set[tuple[str, str, str]],
    cxl_downgrade: bool,
    energy_collapse: str,
    capacity_multiplier: float = 1.0,
    validation_multiplier: float = 1.0,
    contention_multiplier: float = 1.0,
    missing_hook: str = "",
) -> dict[str, object]:
    workload = decision["workload_class"]
    obj_class = decision["object_class"]
    baseline = runtime.get("runtime_architecture_option", OPTION_A)
    if workload in CONTROL_WORKLOADS:
        baseline = OPTION_A

    raw = fnum(decision.get("raw_reuse_credit"))
    safe = fnum(decision.get("safe_reuse_credit"))
    validation = fnum(decision.get("validation_overhead")) * validation_multiplier
    size = fnum(trace.get("size_units"), 1.0)
    queue_harm = fnum(runtime.get("queue_harm_case_count"), 0.0)
    queue = (queue_harm / 80.0 + (0.16 if baseline == OPTION_C else 0.07 if baseline == OPTION_B else 0.0))
    contention = (0.65 if cxl_downgrade else 0.05 if obj_class in OBJECT_REUSE_CLASSES | DAG_CLASSES else 0.0) * contention_multiplier
    capacity_pressure = size / (90.0 * capacity_multiplier)
    compression_strategy = compression["strategy"] if compression else "keep_hot"
    compression_value = fnum(compression.get("net_compression_value") if compression else 0.0)
    compression_risk = max(0.0, -compression_value) + (0.4 if (workload, obj_class, "lossy_summarize") in unsafe else 0.0)
    validation_required = bool(decision.get("validation_gate_ids"))
    security_decision = decision["validation_decision"]

    selected = baseline
    action = "keep_hot"
    tier = "HBM/GPU memory" if obj_class in {"weights", "KV cache"} else "CPU DRAM"
    binding = "value_positive"

    if missing_hook:
        safe = 0.0
        selected = OPTION_A
        action = "recompute_or_drop"
        tier = "not_retained"
        binding = f"missing_hook:{missing_hook}"
    elif security_decision == "denied_reuse":
        selected = OPTION_A
        action = "recompute_or_drop"
        tier = "not_retained"
        safe = 0.0
        binding = "security_gate"
    elif security_decision == "downgraded_reuse":
        selected = rank_option(max(0, option_rank(baseline) - 1))
        action = "offload_cold"
        tier = "NVMe_or_durable_store"
        binding = "security_gate"
    elif security_decision == "overhead_dominated_reuse":
        selected = OPTION_A
        action = "recompute_or_drop"
        tier = "not_retained"
        binding = "validation_overhead"
    elif workload in CONTROL_WORKLOADS or security_decision == "not_reuse_candidate" or safe <= 0.0:
        selected = OPTION_A
        if obj_class in BASELINE_CLASSES:
            action = "keep_hot"
            tier = "HBM/GPU memory"
        else:
            action = "recompute_or_drop"
            tier = "not_retained"
        binding = "control_or_zero_reuse"
    elif validation > max(0.25, safe * 0.55):
        selected = OPTION_A
        action = "recompute_or_drop"
        tier = "not_retained"
        binding = "validation_overhead"
    elif capacity_pressure > 1.45:
        selected = rank_option(option_rank(baseline) - 1)
        if compression and compression["strategy"] in {"lossless_compress", "summary_plus_pointer", "offload_full"}:
            action = "compress_or_pointer_preserve"
            tier = "CPU DRAM"
            binding = "capacity"
        else:
            action = "offload_cold"
            tier = "NVMe_or_durable_store"
            binding = "capacity"
    elif queue > max(0.35, safe * 0.38):
        selected = rank_option(option_rank(baseline) - 1)
        action = "offload_cold" if obj_class in DAG_CLASSES else "recompute_or_drop"
        tier = "NVMe_or_durable_store" if action == "offload_cold" else "not_retained"
        binding = "queueing_overhead"
    elif cxl_downgrade and obj_class in OBJECT_REUSE_CLASSES | DAG_CLASSES:
        selected = rank_option(option_rank(baseline) - 1)
        action = "offload_cold"
        tier = "NVMe_or_durable_store"
        binding = "contention_tail"
    elif energy_collapse == "A" and baseline == OPTION_C and obj_class in DAG_CLASSES:
        selected = OPTION_A
        action = "recompute_or_drop"
        tier = "not_retained"
        binding = "contention_tail"
    elif (workload, obj_class, "lossy_summarize") in unsafe and obj_class not in BASELINE_CLASSES:
        action = "compress_or_pointer_preserve"
        tier = "CPU DRAM"
        binding = "compression_unsafe"
        compression_strategy = "summary_plus_pointer" if compression_strategy == "lossy_summarize" else compression_strategy
    elif obj_class in DAG_CLASSES:
        selected = OPTION_C if option_rank(baseline) >= 2 else baseline
        action = "keep_hot" if size < 110 else "offload_warm"
        tier = "CPU DRAM" if action == "keep_hot" else "CXL_or_pooled_memory_warm_tier"
    elif obj_class in OBJECT_REUSE_CLASSES:
        selected = OPTION_B if option_rank(baseline) >= 1 else baseline
        action = "keep_hot" if size < 80 else "offload_warm"
        tier = "CPU DRAM" if action == "keep_hot" else "CXL_or_pooled_memory_warm_tier"

    if action == "compress_or_pointer_preserve" and (workload, obj_class, compression_strategy) in unsafe:
        compression_strategy = "lossless_compress"
        binding = "compression_unsafe"
    if security_decision in {"denied_reuse", "not_reuse_candidate"} or action == "recompute_or_drop":
        compression_strategy = "none"

    movement = {"keep_hot": 0.08, "offload_warm": 0.22, "offload_cold": 0.38, "compress_or_pointer_preserve": 0.28, "recompute_or_drop": 0.0}[action]
    net = safe - movement - validation - queue - contention - compression_risk
    if binding in {"security_gate", "control_or_zero_reuse"} or action == "recompute_or_drop":
        net = min(0.0, net)
    if security_decision == "denied_reuse":
        safe = 0.0
        net = 0.0

    return {
        "workload_class": workload,
        "object_id": decision["object_id"],
        "object_class": obj_class,
        "selected_option": selected,
        "baseline_option": baseline,
        "action": action,
        "tier": tier,
        "compression_strategy": compression_strategy,
        "validation_required": str(validation_required).lower(),
        "security_decision": security_decision,
        "constraint_binding": binding,
        "net_plan_value": round(net, 6),
        "safe_reuse_credit": round(safe if action in REUSE_ACTIONS else 0.0, 6),
        "raw_reuse_credit": round(raw, 6),
        "validation_overhead": round(validation, 6),
        "queue_overhead": round(queue, 6),
        "contention_penalty": round(contention, 6),
        "compression_risk": round(compression_risk, 6),
        "evidence_label": "synthetic_planning",
    }


def hook_applies(hook: dict[str, str], obj_class: str, workload: str) -> bool:
    classes = hook["object_classes"]
    regimes = hook["workload_regimes"]
    class_match = "all memory objects" in classes or obj_class in [part.strip() for part in classes.split(";")]
    if "all nontrivial regimes" in regimes:
        workload_match = workload not in CONTROL_WORKLOADS
    else:
        workload_match = workload in regimes or any(part.strip() in workload for part in regimes.split(";"))
    return class_match and workload_match


def build_plans() -> tuple[list[dict[str, object]], list[dict[str, object]], list[dict[str, object]], list[dict[str, object]], list[dict[str, object]]]:
    decisions = [row for row in read_csv(SECURITY_DECISIONS) if row.get("object_id") and row.get("object_class")]
    runtime = load_runtime()
    trace = load_trace_sizes()
    compression, unsafe = load_best_compression()
    cxl = cxl_downgrade_map()
    energy = energy_collapse_map()
    _ = queue_threshold_labels()

    actions: list[dict[str, object]] = []
    for row in decisions:
        key = (row["workload_class"], row["object_id"])
        ckey = (row["workload_class"], row["object_class"])
        actions.append(
            choose_plan(
                row,
                runtime.get(key, {}),
                trace.get(key, {}),
                compression.get(ckey),
                unsafe,
                cxl.get(ckey, False),
                energy.get(row["workload_class"], ""),
            )
        )
    actions = aggregate_action_rows(actions)

    infeasible = [
        {
            "workload_class": row["workload_class"],
            "object_id": row["object_id"],
            "object_class": row["object_class"],
            "selected_option": row["selected_option"],
            "action": row["action"],
            "constraint_binding": row["constraint_binding"],
            "security_decision": row["security_decision"],
            "net_plan_value": row["net_plan_value"],
            "evidence_label": "synthetic_planning",
        }
        for row in actions
        if row["constraint_binding"] != "value_positive"
    ]

    by_workload: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in actions:
        by_workload[str(row["workload_class"])].append(row)

    summary: list[dict[str, object]] = []
    for workload, rows in sorted(by_workload.items()):
        option_counts = Counter(str(row["selected_option"]) for row in rows)
        action_counts = Counter(str(row["action"]) for row in rows)
        constraint_counts = Counter(str(row["constraint_binding"]) for row in rows)
        baseline_rank = max(option_rank(str(row["baseline_option"])) for row in rows)
        planned_rank = max(option_rank(str(row["selected_option"])) for row in rows)
        if workload in CONTROL_WORKLOADS:
            baseline_rank = planned_rank = 0
        summary.append({
            "workload_class": workload,
            "baseline_option": rank_option(baseline_rank),
            "planned_option": rank_option(planned_rank),
            "object_plan_rows": len(rows),
            "object_classes": "; ".join(sorted({str(row["object_class"]) for row in rows})),
            "total_net_plan_value": round(sum(fnum(row["net_plan_value"]) for row in rows), 6),
            "positive_reuse_rows": sum(1 for row in rows if fnum(row["safe_reuse_credit"]) > 0),
            "dominant_action": action_counts.most_common(1)[0][0],
            "dominant_constraint": constraint_counts.most_common(1)[0][0],
            "option_counts": "; ".join(f"{short_option(k)}={v}" for k, v in sorted(option_counts.items())),
            "action_counts": "; ".join(f"{k}={v}" for k, v in sorted(action_counts.items())),
            "constraint_counts": "; ".join(f"{k}={v}" for k, v in sorted(constraint_counts.items())),
            "evidence_label": "synthetic_planning",
        })

    hooks = read_csv(HOOK_MATRIX)
    hook_ablation: list[dict[str, object]] = []
    for hook in hooks:
        affected = [row for row in decisions if hook_applies(hook, row["object_class"], row["workload_class"])]
        base_rows = [row for row in actions if any(row["object_id"] == d["object_id"] and row["workload_class"] == d["workload_class"] for d in affected)]
        lost_value = sum(max(0.0, fnum(row["net_plan_value"])) for row in base_rows)
        reuse_rows = sum(1 for row in base_rows if row["action"] in REUSE_ACTIONS)
        hook_ablation.append({
            "hook": hook["hook"],
            "owner": hook["owner"],
            "affected_plan_rows": len(base_rows),
            "blocked_reuse_actions": reuse_rows,
            "downgrade_count": reuse_rows,
            "lost_net_plan_value": round(lost_value, 6),
            "constraint_binding": f"missing_hook:{hook['hook']}",
            "failure_if_missing": hook["failure_if_missing"],
            "evidence_label": "synthetic_planning",
        })

    sensitivity_settings = [
        ("baseline", 1.0, 1.0, 1.0),
        ("tight_capacity", 0.45, 1.0, 1.0),
        ("high_validation_overhead", 1.0, 8.0, 1.0),
        ("pathological_cxl_p99", 1.0, 1.0, 4.0),
    ]
    sensitivity: list[dict[str, object]] = []
    for setting, cap_mult, val_mult, cont_mult in sensitivity_settings:
        setting_rows = []
        for row in decisions:
            key = (row["workload_class"], row["object_id"])
            ckey = (row["workload_class"], row["object_class"])
            setting_rows.append(
                choose_plan(
                    row,
                    runtime.get(key, {}),
                    trace.get(key, {}),
                    compression.get(ckey),
                    unsafe,
                    cxl.get(ckey, False),
                    energy.get(row["workload_class"], ""),
                    capacity_multiplier=cap_mult,
                    validation_multiplier=val_mult,
                    contention_multiplier=cont_mult,
                )
            )
        for workload, rows in sorted(defaultdict(list, {w: [r for r in setting_rows if r["workload_class"] == w] for w in {r["workload_class"] for r in setting_rows}}).items()):
            baseline_rank = max(option_rank(str(row["baseline_option"])) for row in rows)
            planned_rank = max(option_rank(str(row["selected_option"])) for row in rows)
            if workload in CONTROL_WORKLOADS:
                baseline_rank = planned_rank = 0
            constraints = Counter(str(row["constraint_binding"]) for row in rows)
            sensitivity.append({
                "setting": setting,
                "workload_class": workload,
                "baseline_option": rank_option(baseline_rank),
                "planned_option": rank_option(planned_rank),
                "dominant_constraint": constraints.most_common(1)[0][0],
                "constraint_counts": "; ".join(f"{k}={v}" for k, v in sorted(constraints.items())),
                "total_net_plan_value": round(sum(fnum(row["net_plan_value"]) for row in rows), 6),
                "positive_reuse_rows": sum(1 for row in rows if fnum(row["safe_reuse_credit"]) > 0),
                "evidence_label": "synthetic_planning",
            })

    return actions, summary, infeasible, hook_ablation, sensitivity


def main() -> None:
    actions, summary, infeasible, hook_ablation, sensitivity = build_plans()
    write_csv(OUT_ACTIONS, actions, ACTION_FIELDS)
    write_csv(OUT_SUMMARY, summary, list(summary[0].keys()))
    write_csv(OUT_INFEASIBLE, infeasible, list(infeasible[0].keys()))
    write_csv(OUT_HOOK_ABLATION, hook_ablation, list(hook_ablation[0].keys()))
    write_csv(OUT_SENSITIVITY, sensitivity, list(sensitivity[0].keys()))


if __name__ == "__main__":
    main()
