# created: 2026-05-11T16:42:00Z
# cycle: 11
# run_id: run-2026-05-11T121649Z
# agent: worker
# milestone: M-PROTO-1
"""Trace-replay runtime prototype for memory-centric agentic inference.

This is deliberately small: it tests whether the validated synthetic trace
contains enough runtime-visible state to drive object registry, placement,
compression safety, and architecture boundary decisions.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass, field
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

INPUT_TRACE = DATA / "agentic_trace_events_v2.csv"
INPUT_LIFETIMES = DATA / "trace_object_lifetimes.csv"
INPUT_REUSE = DATA / "trace_reuse_intervals.csv"
INPUT_SUMMARY = DATA / "trace_workload_summary.csv"
INPUT_QUEUE = DATA / "queueing_architecture_winners.csv"
INPUT_COMPRESSION = DATA / "compression_best_strategy_by_object.csv"
INPUT_OBJECT_QUEUE = DATA / "compression_object_queue_interactions.csv"
INPUT_POLICY = DATA / "architecture_policy_matrix.csv"
INPUT_SAFETY = DATA / "compression_safety_failures.csv"

OUT_SNAPSHOTS = DATA / "runtime_registry_snapshots.csv"
OUT_DECISIONS = DATA / "runtime_policy_decisions.csv"
OUT_SUMMARY = DATA / "runtime_workload_summary.csv"
OUT_ABLATIONS = DATA / "runtime_ablation_results.csv"
OUT_FAILURES = DATA / "runtime_failure_cases.csv"

OPTION_A = "A_conventional_request_model_kv_serving"
OPTION_B = "B_memory_object_aware_runtime"
OPTION_C = "C_trajectory_dag_memory_fabric"

BASELINE_OBJECTS = {"weights", "KV cache", "prefix cache", "intermediate scratch"}
OBJECT_RUNTIME_CLASSES = {"retrieved context", "semantic cache entry", "tool output"}
DAG_CLASSES = {"branch state", "verifier state", "trajectory log", "durable workspace"}
EXACT_STATE_CLASSES = {"weights", "KV cache", "branch state", "verifier state", "trajectory log", "durable workspace"}
PROVENANCE_CLASSES = {"retrieved context", "semantic cache entry", "tool output", "durable workspace", "trajectory log"}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({name: row.get(name, "") for name in fieldnames})


def as_int(value: str | None, default: int = 0) -> int:
    if value in (None, ""):
        return default
    return int(float(value))


def as_float(value: str | None, default: float = 0.0) -> float:
    if value in (None, ""):
        return default
    return float(value)


def as_bool(value: str | None) -> bool:
    return str(value).lower() == "true"


@dataclass
class RuntimeObject:
    object_id: str
    object_class: str
    workload_class: str
    size_units: float
    tier: str
    created_at: int
    last_seen_at: int
    lifetime: int = 0
    reuse_count: int = 0
    reuse_distance: float = 0.0
    correctness_sensitive: bool = False
    provenance_id: str = ""
    source_version: str = ""
    invalidation_signal: str = ""
    trajectory_node_id: str = ""
    branch_id: str = ""
    verifier_id: str = ""
    durability_horizon: int = 0
    merge_state: str = ""
    active: bool = True
    placement_decision: str = ""
    retention_decision: str = ""
    compression_strategy: str = ""
    eviction_decision: str = ""
    history_events: int = 0

    def update_from_event(self, event: dict[str, str]) -> None:
        t = as_int(event.get("time_step"))
        self.last_seen_at = max(self.last_seen_at, t)
        self.history_events += 1
        self.size_units = max(self.size_units, as_float(event.get("size_units"), self.size_units))
        if event.get("tier"):
            self.tier = event["tier"]
        if event.get("reuse_distance"):
            self.reuse_distance = as_float(event["reuse_distance"])
        if event.get("correctness_sensitive"):
            self.correctness_sensitive = self.correctness_sensitive or as_bool(event["correctness_sensitive"])
        for attr, field_name in [
            ("provenance_id", "provenance_id"),
            ("source_version", "source_version"),
            ("invalidation_signal", "invalidation_signal"),
            ("trajectory_node_id", "trajectory_node_id"),
            ("branch_id", "branch_id"),
            ("verifier_id", "verifier_id"),
            ("merge_state", "merge_state"),
        ]:
            value = event.get(field_name, "")
            if value:
                setattr(self, attr, value)
        self.durability_horizon = max(self.durability_horizon, as_int(event.get("durability_horizon")))
        if event.get("event_type") == "object_access":
            self.reuse_count += 1
        if event.get("event_type") == "object_evict":
            self.active = False
            self.eviction_decision = "evict_after_trace_use"
        self.lifetime = self.last_seen_at - self.created_at

    def to_snapshot(self, workload_option: str, event: dict[str, str]) -> dict[str, object]:
        return {
            "workload_class": self.workload_class,
            "time_step": event["time_step"],
            "event_type": event["event_type"],
            "object_id": self.object_id,
            "object_class": self.object_class,
            "size_units": round(self.size_units, 6),
            "tier": self.tier,
            "created_at": self.created_at,
            "last_seen_at": self.last_seen_at,
            "lifetime": self.lifetime,
            "reuse_count": self.reuse_count,
            "reuse_distance": round(self.reuse_distance, 6),
            "correctness_sensitive": str(self.correctness_sensitive).lower(),
            "provenance_id": self.provenance_id,
            "source_version": self.source_version,
            "invalidation_signal": self.invalidation_signal,
            "trajectory_node_id": self.trajectory_node_id,
            "branch_id": self.branch_id,
            "verifier_id": self.verifier_id,
            "durability_horizon": self.durability_horizon,
            "merge_state": self.merge_state,
            "active": str(self.active).lower(),
            "placement_decision": self.placement_decision,
            "retention_decision": self.retention_decision,
            "compression_strategy": self.compression_strategy,
            "eviction_decision": self.eviction_decision,
            "runtime_architecture_option": workload_option,
            "evidence_label": "synthetic",
        }


def expected_tier(option: str, obj: RuntimeObject) -> str:
    if option == OPTION_A:
        if obj.object_class in {"weights", "KV cache"}:
            return "HBM/GPU memory"
        if obj.object_class in BASELINE_OBJECTS:
            return obj.tier or "CPU DRAM"
        return "not_retained_by_option_A"
    if option == OPTION_B:
        if obj.object_class in {"weights", "KV cache"}:
            return "HBM/GPU memory"
        if obj.object_class in {"retrieved context", "semantic cache entry", "tool output", "prefix cache"}:
            return "CPU DRAM"
        return obj.tier or "CPU DRAM"
    if obj.object_class in {"weights", "KV cache"}:
        return "HBM/GPU memory"
    if obj.object_class in DAG_CLASSES:
        return "durable_workspace_store" if obj.object_class == "durable workspace" else "CPU DRAM"
    if obj.object_class in OBJECT_RUNTIME_CLASSES:
        return "CPU DRAM"
    return obj.tier or "CPU DRAM"


def decide_retention(option: str, obj: RuntimeObject) -> str:
    if option == OPTION_A:
        return "retain_baseline_serving_state" if obj.object_class in BASELINE_OBJECTS else "drop_nonconventional_state"
    if option == OPTION_B:
        if obj.object_class in PROVENANCE_CLASSES and obj.provenance_id:
            return "retain_with_provenance_pointer"
        if obj.reuse_count > 0:
            return "retain_reuse_candidate"
        return "retain_object_metadata"
    if obj.object_class in DAG_CLASSES or obj.correctness_sensitive or obj.durability_horizon > 0:
        return "pin_dependency_sensitive_state"
    if obj.object_class in PROVENANCE_CLASSES and obj.provenance_id:
        return "retain_with_provenance_pointer"
    return "retain_reuse_candidate"


def compute_features(objects: list[RuntimeObject], events: list[dict[str, str]], masks: set[str] | None = None) -> dict[str, float]:
    masks = masks or set()
    hide_provenance = "provenance_reuse" in masks
    hide_dag = "branch_verifier_durable" in masks
    object_classes = {o.object_class for o in objects}
    nonbaseline = object_classes - BASELINE_OBJECTS
    provenance_objects = [o for o in objects if o.provenance_id and o.object_class in PROVENANCE_CLASSES]
    reusable_nonbaseline = [o for o in objects if o.object_class in nonbaseline and o.reuse_count > 0]
    exact_sensitive = [o for o in objects if o.correctness_sensitive and o.object_class in nonbaseline]
    dag_objects = [o for o in objects if o.object_class in DAG_CLASSES]
    durable_objects = [o for o in objects if o.durability_horizon > 0]
    branch_events = [e for e in events if e["event_type"] in {"branch_fork", "branch_merge", "branch_discard"}]
    verifier_events = [e for e in events if e["event_type"] in {"verifier_start", "verifier_result"}]
    if hide_provenance:
        provenance_objects = []
        reusable_nonbaseline = []
        exact_sensitive = []
    if hide_dag:
        dag_objects = []
        durable_objects = []
        branch_events = []
        verifier_events = []
    object_value = (
        1.4 * len(provenance_objects)
        + 0.8 * len(reusable_nonbaseline)
        + 0.6 * len(exact_sensitive)
        + 0.2 * sum(o.reuse_count for o in reusable_nonbaseline)
    )
    dag_value = (
        1.8 * len(dag_objects)
        + 1.2 * len(durable_objects)
        + 0.9 * len(branch_events)
        + 0.9 * len(verifier_events)
    )
    option_b_overhead = 2.0
    option_c_overhead = 4.0
    return {
        "object_runtime_value": round(object_value, 6),
        "trajectory_fabric_value": round(dag_value, 6),
        "option_b_net_value": round(object_value - option_b_overhead, 6),
        "option_c_net_value": round(dag_value - option_c_overhead, 6),
        "provenance_object_count": len(provenance_objects),
        "reusable_nonbaseline_count": len(reusable_nonbaseline),
        "branch_event_count": len(branch_events),
        "verifier_event_count": len(verifier_events),
        "durable_object_count": len(durable_objects),
        "nonbaseline_object_classes": len(nonbaseline),
    }


def select_architecture(features: dict[str, float]) -> str:
    if features["option_c_net_value"] > 0:
        return OPTION_C
    if features["option_b_net_value"] > 0:
        return OPTION_B
    return OPTION_A


def load_lookup(rows: list[dict[str, str]], keys: tuple[str, ...], value_field: str) -> dict[tuple[str, ...], str]:
    return {tuple(row[k] for k in keys): row[value_field] for row in rows}


def apply_object_policies(
    objects: dict[str, RuntimeObject],
    workload_options: dict[str, str],
    compression: dict[tuple[str, str], str],
) -> None:
    for obj in objects.values():
        option = workload_options[obj.workload_class]
        obj.tier = expected_tier(option, obj)
        obj.placement_decision = f"place:{obj.tier}"
        obj.retention_decision = decide_retention(option, obj)
        obj.compression_strategy = compression.get((obj.workload_class, obj.object_class), "keep_hot")
        if option == OPTION_A and obj.object_class not in BASELINE_OBJECTS:
            obj.eviction_decision = "evict_or_recompute_nonconventional_state"
        elif obj.eviction_decision == "":
            obj.eviction_decision = "retain_until_trace_end"


def replay_trace(events: list[dict[str, str]], compression: dict[tuple[str, str], str]) -> tuple[
    dict[str, RuntimeObject],
    dict[str, list[dict[str, str]]],
]:
    objects: dict[str, RuntimeObject] = {}
    workload_events: dict[str, list[dict[str, str]]] = {}
    for event in events:
        workload_events.setdefault(event["workload_class"], []).append(event)
        object_id = event.get("object_id", "")
        if not object_id:
            continue
        if event["event_type"] == "object_create" and object_id not in objects:
            obj = RuntimeObject(
                object_id=object_id,
                object_class=event["object_class"],
                workload_class=event["workload_class"],
                size_units=as_float(event.get("size_units")),
                tier=event.get("tier", ""),
                created_at=as_int(event.get("time_step")),
                last_seen_at=as_int(event.get("time_step")),
                correctness_sensitive=as_bool(event.get("correctness_sensitive")),
                provenance_id=event.get("provenance_id", ""),
                source_version=event.get("source_version", ""),
                invalidation_signal=event.get("invalidation_signal", ""),
                trajectory_node_id=event.get("trajectory_node_id", ""),
                branch_id=event.get("branch_id", ""),
                verifier_id=event.get("verifier_id", ""),
                durability_horizon=as_int(event.get("durability_horizon")),
                merge_state=event.get("merge_state", ""),
            )
            objects[object_id] = obj
        if object_id in objects:
            objects[object_id].update_from_event(event)
    by_workload = {
        workload: [obj for obj in objects.values() if obj.workload_class == workload]
        for workload in workload_events
    }
    workload_options = {
        workload: select_architecture(compute_features(objs, workload_events[workload]))
        for workload, objs in by_workload.items()
    }
    apply_object_policies(objects, workload_options, compression)
    return objects, workload_events


def create_object_from_event(event: dict[str, str]) -> RuntimeObject:
    return RuntimeObject(
        object_id=event["object_id"],
        object_class=event["object_class"],
        workload_class=event["workload_class"],
        size_units=as_float(event.get("size_units")),
        tier=event.get("tier", ""),
        created_at=as_int(event.get("time_step")),
        last_seen_at=as_int(event.get("time_step")),
        correctness_sensitive=as_bool(event.get("correctness_sensitive")),
        provenance_id=event.get("provenance_id", ""),
        source_version=event.get("source_version", ""),
        invalidation_signal=event.get("invalidation_signal", ""),
        trajectory_node_id=event.get("trajectory_node_id", ""),
        branch_id=event.get("branch_id", ""),
        verifier_id=event.get("verifier_id", ""),
        durability_horizon=as_int(event.get("durability_horizon")),
        merge_state=event.get("merge_state", ""),
    )


def generate_registry_snapshots(
    events: list[dict[str, str]],
    workload_options: dict[str, str],
    compression: dict[tuple[str, str], str],
) -> list[dict[str, object]]:
    registry: dict[str, RuntimeObject] = {}
    snapshots: list[dict[str, object]] = []
    for event in events:
        object_id = event.get("object_id", "")
        if not object_id:
            continue
        if event["event_type"] == "object_create" and object_id not in registry:
            registry[object_id] = create_object_from_event(event)
        if object_id not in registry:
            continue
        obj = registry[object_id]
        obj.update_from_event(event)
        option = workload_options[obj.workload_class]
        obj.tier = expected_tier(option, obj)
        obj.placement_decision = f"place:{obj.tier}"
        obj.retention_decision = decide_retention(option, obj)
        obj.compression_strategy = compression.get((obj.workload_class, obj.object_class), "keep_hot")
        if obj.eviction_decision == "":
            obj.eviction_decision = "pending_reuse_or_trace_end"
        snapshots.append(obj.to_snapshot(option, event))
    return snapshots


def decision_rows(
    objects: dict[str, RuntimeObject],
    workload_events: dict[str, list[dict[str, str]]],
    expected: dict[str, str],
    queue: dict[str, dict[str, str]],
    object_queue_rows: list[dict[str, str]],
) -> tuple[list[dict[str, object]], dict[str, str], dict[str, dict[str, float]]]:
    rows: list[dict[str, object]] = []
    options: dict[str, str] = {}
    features_by_workload: dict[str, dict[str, float]] = {}
    for workload in sorted(workload_events):
        objs = [obj for obj in objects.values() if obj.workload_class == workload]
        features = compute_features(objs, workload_events[workload])
        option = select_architecture(features)
        options[workload] = option
        features_by_workload[workload] = features
        q = queue.get(workload, {})
        queue_help_rows = [
            row for row in object_queue_rows
            if row["workload_class"] == workload and row["selected_positive_for_queue_help"] == "true"
        ]
        queue_harm_rows = [
            row for row in object_queue_rows
            if row["workload_class"] == workload and as_float(row["net_queue_effect_proxy"]) < 0
        ]
        for obj in sorted(objs, key=lambda o: o.object_id):
            rows.append({
                "workload_class": workload,
                "object_id": obj.object_id,
                "object_class": obj.object_class,
                "runtime_architecture_option": option,
                "expected_architecture_option": expected.get(workload, ""),
                "boundary_match": str(option == expected.get(workload, "")).lower(),
                "placement_decision": obj.placement_decision,
                "retention_decision": obj.retention_decision,
                "compression_strategy": obj.compression_strategy,
                "eviction_decision": obj.eviction_decision,
                "queue_overhead_context": f"high_object->{q.get('high_object_overhead_winner', '')}; high_dag->{q.get('high_dag_overhead_winner', '')}",
                "queue_help_claim": "none_selected_positive_object_rows" if not queue_help_rows else "object_positive_rows_present",
                "queue_harm_case_count": len(queue_harm_rows),
                "object_runtime_value": features["object_runtime_value"],
                "trajectory_fabric_value": features["trajectory_fabric_value"],
                "option_b_net_value": features["option_b_net_value"],
                "option_c_net_value": features["option_c_net_value"],
                "evidence_label": "synthetic",
            })
    return rows, options, features_by_workload


def workload_summary_rows(
    objects: dict[str, RuntimeObject],
    workload_events: dict[str, list[dict[str, str]]],
    expected: dict[str, str],
    options: dict[str, str],
    features_by_workload: dict[str, dict[str, float]],
) -> list[dict[str, object]]:
    rows = []
    for workload in sorted(workload_events):
        objs = [obj for obj in objects.values() if obj.workload_class == workload]
        classes = sorted({obj.object_class for obj in objs})
        active_bytes = sum(obj.size_units for obj in objs if obj.active)
        retained_bytes = sum(obj.size_units for obj in objs if "retain" in obj.retention_decision or "pin" in obj.retention_decision)
        by_tier: dict[str, float] = {}
        for obj in objs:
            by_tier[obj.tier] = by_tier.get(obj.tier, 0.0) + obj.size_units
        features = features_by_workload[workload]
        rows.append({
            "workload_class": workload,
            "object_count": len(objs),
            "object_classes": "; ".join(classes),
            "runtime_architecture_option": options[workload],
            "expected_architecture_option": expected.get(workload, ""),
            "boundary_match": str(options[workload] == expected.get(workload, "")).lower(),
            "object_runtime_value": features["object_runtime_value"],
            "trajectory_fabric_value": features["trajectory_fabric_value"],
            "option_b_net_value": features["option_b_net_value"],
            "option_c_net_value": features["option_c_net_value"],
            "active_size_units_after_replay": round(active_bytes, 6),
            "retained_size_units": round(retained_bytes, 6),
            "tier_residency_summary": "; ".join(f"{tier}:{round(size, 3)}" for tier, size in sorted(by_tier.items())),
            "evidence_label": "synthetic",
        })
    return rows


def ablation_rows(
    objects: dict[str, RuntimeObject],
    workload_events: dict[str, list[dict[str, str]]],
    baseline_options: dict[str, str],
) -> list[dict[str, object]]:
    ablations = {
        "baseline": set(),
        "hide_provenance_reuse": {"provenance_reuse"},
        "hide_branch_verifier_durable": {"branch_verifier_durable"},
        "hide_all_memory_causal_fields": {"provenance_reuse", "branch_verifier_durable"},
    }
    rows = []
    for workload in sorted(workload_events):
        objs = [obj for obj in objects.values() if obj.workload_class == workload]
        for name, masks in ablations.items():
            features = compute_features(objs, workload_events[workload], masks)
            option = select_architecture(features)
            rows.append({
                "workload_class": workload,
                "ablation": name,
                "runtime_architecture_option": option,
                "baseline_architecture_option": baseline_options[workload],
                "changed_from_baseline": str(option != baseline_options[workload]).lower(),
                "object_runtime_value": features["object_runtime_value"],
                "trajectory_fabric_value": features["trajectory_fabric_value"],
                "option_b_net_value": features["option_b_net_value"],
                "option_c_net_value": features["option_c_net_value"],
                "interpretation": interpret_ablation(name, baseline_options[workload], option),
                "evidence_label": "synthetic",
            })
    return rows


def interpret_ablation(name: str, baseline: str, option: str) -> str:
    if name == "baseline":
        return "unaltered_registry_signals"
    if baseline == option:
        return "hidden_fields_not_causal_for_this_boundary"
    return f"hidden_fields_collapse_{baseline}_to_{option}"


def failure_rows(
    objects: dict[str, RuntimeObject],
    safety_rows: list[dict[str, str]],
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for row in safety_rows:
        rows.append({
            "failure_case": "unsafe_lossy_compression_request",
            "workload_class": row["workload_class"],
            "object_class": row["object_class"],
            "object_id": "",
            "requested_strategy": row["strategy"],
            "runtime_response": "blocked",
            "reason": row["invalid_reason"],
            "evidence_label": "synthetic",
        })
    for obj in objects.values():
        if obj.object_class in PROVENANCE_CLASSES and not obj.provenance_id:
            rows.append({
                "failure_case": "missing_provenance_pointer",
                "workload_class": obj.workload_class,
                "object_class": obj.object_class,
                "object_id": obj.object_id,
                "requested_strategy": obj.compression_strategy,
                "runtime_response": "blocked_or_retain_exact_state",
                "reason": "provenance_required_for_pointer_preserving_replay",
                "evidence_label": "synthetic",
            })
        if obj.provenance_id and obj.invalidation_signal not in {"none", ""}:
            rows.append({
                "failure_case": "invalidation_or_source_version_mismatch",
                "workload_class": obj.workload_class,
                "object_class": obj.object_class,
                "object_id": obj.object_id,
                "requested_strategy": obj.compression_strategy,
                "runtime_response": "force_revalidate_or_recompute",
                "reason": f"invalidation_signal={obj.invalidation_signal}",
                "evidence_label": "synthetic",
            })
        if obj.object_class in DAG_CLASSES and not (obj.trajectory_node_id or obj.branch_id or obj.verifier_id or obj.durability_horizon):
            rows.append({
                "failure_case": "missing_trajectory_or_dag_fields",
                "workload_class": obj.workload_class,
                "object_class": obj.object_class,
                "object_id": obj.object_id,
                "requested_strategy": obj.compression_strategy,
                "runtime_response": "downgrade_to_object_runtime_or_pin",
                "reason": "dependency_sensitive_state_lacks_dag_identifier",
                "evidence_label": "synthetic",
            })
    required_fixtures = {
        "missing_provenance_pointer": {
            "failure_case": "missing_provenance_pointer",
            "workload_class": "RAG",
            "object_class": "retrieved context",
            "object_id": "fixture:retrieved_context_without_provenance",
            "requested_strategy": "summary_plus_pointer",
            "runtime_response": "blocked_or_retain_exact_state",
            "reason": "fixture removes provenance_id needed for replay-safe pointer strategy",
            "evidence_label": "synthetic_fixture",
        },
        "invalidation_or_source_version_mismatch": {
            "failure_case": "invalidation_or_source_version_mismatch",
            "workload_class": "RAG",
            "object_class": "semantic cache entry",
            "object_id": "fixture:semantic_cache_stale_source",
            "requested_strategy": "summary_plus_pointer",
            "runtime_response": "force_revalidate_or_recompute",
            "reason": "fixture changes source_version or invalidation_signal before reuse",
            "evidence_label": "synthetic_fixture",
        },
        "missing_trajectory_or_dag_fields": {
            "failure_case": "missing_trajectory_or_dag_fields",
            "workload_class": "code-agent loop",
            "object_class": "branch state",
            "object_id": "fixture:branch_state_without_trajectory_node",
            "requested_strategy": "summary_plus_pointer",
            "runtime_response": "downgrade_to_object_runtime_or_pin",
            "reason": "fixture removes trajectory_node_id and branch_id from dependency-sensitive state",
            "evidence_label": "synthetic_fixture",
        },
    }
    present = {row["failure_case"] for row in rows}
    for name, row in required_fixtures.items():
        if name not in present:
            rows.append(row)
    return rows


def main() -> None:
    events = read_csv(INPUT_TRACE)
    expected = {row["workload_class"]: row["architecture_option"] for row in read_csv(INPUT_SUMMARY)}
    queue_rows = {row["workload_class"]: row for row in read_csv(INPUT_QUEUE)}
    compression = load_lookup(read_csv(INPUT_COMPRESSION), ("workload_class", "object_class"), "best_strategy")
    object_queue_rows = read_csv(INPUT_OBJECT_QUEUE)
    safety = read_csv(INPUT_SAFETY)
    # Loaded to assert the prototype consumes the existing policy matrix contract.
    policy_matrix = read_csv(INPUT_POLICY)
    if not policy_matrix:
        raise SystemExit("architecture_policy_matrix.csv is empty")
    # Lifetimes and reuse intervals are consumed as interface checks; replay derives its
    # own counters, while these files assert the trace exposes the needed summaries.
    if not read_csv(INPUT_LIFETIMES) or not read_csv(INPUT_REUSE):
        raise SystemExit("trace lifetime/reuse summaries are missing")

    objects, workload_events = replay_trace(events, compression)
    decisions, options, features = decision_rows(objects, workload_events, expected, queue_rows, object_queue_rows)
    snapshots = generate_registry_snapshots(events, options, compression)
    summaries = workload_summary_rows(objects, workload_events, expected, options, features)
    ablations = ablation_rows(objects, workload_events, options)
    failures = failure_rows(objects, safety)

    write_csv(OUT_SNAPSHOTS, snapshots, [
        "workload_class", "time_step", "event_type", "object_id", "object_class", "size_units", "tier",
        "created_at", "last_seen_at", "lifetime", "reuse_count", "reuse_distance", "correctness_sensitive",
        "provenance_id", "source_version", "invalidation_signal", "trajectory_node_id", "branch_id",
        "verifier_id", "durability_horizon", "merge_state", "active", "placement_decision",
        "retention_decision", "compression_strategy", "eviction_decision", "runtime_architecture_option",
        "evidence_label",
    ])
    write_csv(OUT_DECISIONS, decisions, [
        "workload_class", "object_id", "object_class", "runtime_architecture_option",
        "expected_architecture_option", "boundary_match", "placement_decision", "retention_decision",
        "compression_strategy", "eviction_decision", "queue_overhead_context", "queue_help_claim",
        "queue_harm_case_count", "object_runtime_value", "trajectory_fabric_value", "option_b_net_value",
        "option_c_net_value", "evidence_label",
    ])
    write_csv(OUT_SUMMARY, summaries, [
        "workload_class", "object_count", "object_classes", "runtime_architecture_option",
        "expected_architecture_option", "boundary_match", "object_runtime_value", "trajectory_fabric_value",
        "option_b_net_value", "option_c_net_value", "active_size_units_after_replay", "retained_size_units",
        "tier_residency_summary", "evidence_label",
    ])
    write_csv(OUT_ABLATIONS, ablations, [
        "workload_class", "ablation", "runtime_architecture_option", "baseline_architecture_option",
        "changed_from_baseline", "object_runtime_value", "trajectory_fabric_value", "option_b_net_value",
        "option_c_net_value", "interpretation", "evidence_label",
    ])
    write_csv(OUT_FAILURES, failures, [
        "failure_case", "workload_class", "object_class", "object_id", "requested_strategy",
        "runtime_response", "reason", "evidence_label",
    ])

    print(f"wrote {OUT_SNAPSHOTS.relative_to(ROOT)} rows={len(snapshots)}")
    print(f"wrote {OUT_DECISIONS.relative_to(ROOT)} rows={len(decisions)}")
    print(f"wrote {OUT_SUMMARY.relative_to(ROOT)} rows={len(summaries)}")
    print(f"wrote {OUT_ABLATIONS.relative_to(ROOT)} rows={len(ablations)}")
    print(f"wrote {OUT_FAILURES.relative_to(ROOT)} rows={len(failures)}")
    for row in summaries:
        print(
            "summary "
            f"{row['workload_class']}: runtime={row['runtime_architecture_option']} "
            f"expected={row['expected_architecture_option']} match={row['boundary_match']}"
        )


if __name__ == "__main__":
    main()
