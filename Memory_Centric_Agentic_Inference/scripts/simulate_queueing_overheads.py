# created: 2026-05-11T15:08:00Z
# cycle: 8
# run_id: run-2026-05-11T121649Z
# agent: worker
# milestone: M-QUEUE-1

"""Simulate synthetic queueing overheads from trace v2 workload events."""

from __future__ import annotations

import csv
from collections import Counter, defaultdict
from itertools import product
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

OBJECT_EVENTS = {
    "object_create",
    "object_access",
    "object_update",
    "object_place",
    "object_migrate",
    "object_evict",
    "object_recompute",
    "semantic_cache_lookup",
    "semantic_cache_insert",
    "tool_call_result",
    "workspace_write",
    "workspace_compact",
}
MIGRATION_EVENTS = {"object_place", "object_migrate"}
DAG_EVENTS = {"branch_fork", "branch_merge", "branch_discard"}
DURABLE_EVENTS = {"workspace_write", "workspace_compact"}
VERIFIER_EVENTS = {"verifier_start", "verifier_result"}

MULTIPLIERS = [0.0, 0.25, 0.5, 1.0, 2.0, 4.0, 8.0, 16.0]
OPTION_ORDER = [
    "A_conventional_request_model_kv_serving",
    "B_memory_object_aware_runtime",
    "C_trajectory_dag_memory_fabric",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, object]], fields: list[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if fields is None:
        fields = list(rows[0].keys()) if rows else []
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def fnum(value: str, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def queue_delay(arrival_rate: float, service_time: float) -> tuple[float, float]:
    if arrival_rate <= 0 or service_time <= 0:
        return 0.0, 0.0
    rho = arrival_rate * service_time
    if rho >= 0.995:
        return rho, 1_000.0
    mu = 1.0 / service_time
    wq = rho / (mu - arrival_rate)
    return rho, wq


def architecture_base_benefits(summary: dict[str, str], dag: dict[str, str]) -> tuple[float, float]:
    non_kv_share = fnum(summary.get("non_kv_object_size_share", "0"))
    object_count = fnum(summary.get("object_count", "0"))
    max_width = fnum(dag.get("max_dag_width", "0"))
    verifier_results = fnum(dag.get("verifier_results", "0"))
    verifier_delay = fnum(dag.get("mean_verifier_delay", "0"))
    object_classes = summary.get("object_classes", "")
    durable_present = 1.0 if "durable workspace" in object_classes else 0.0
    semantic_present = 1.0 if "semantic cache entry" in object_classes or "retrieved context" in object_classes else 0.0

    object_benefit = 0.55 * object_count * non_kv_share + 1.55 * semantic_present
    dag_benefit = 1.05 * max_width + 0.30 * verifier_results * max(1.0, verifier_delay) + 1.60 * durable_present
    return round(object_benefit, 6), round(dag_benefit, 6)


def reconstruct_rates(events: list[dict[str, str]], summary_rows: list[dict[str, str]], dag_rows: list[dict[str, str]]) -> list[dict[str, object]]:
    events_by_workload: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in events:
        events_by_workload[row["workload_class"]].append(row)
    summary_by_workload = {row["workload_class"]: row for row in summary_rows}
    dag_by_workload = {row["workload_class"]: row for row in dag_rows}

    rows: list[dict[str, object]] = []
    for workload, rows_for_workload in sorted(events_by_workload.items()):
        event_counts = Counter(row["event_type"] for row in rows_for_workload)
        duration = max(int(row["time_step"]) for row in rows_for_workload) or 1
        objects: dict[str, tuple[int, int, float, str]] = {}
        active: dict[str, tuple[float, str]] = {}
        live_peak = 0.0
        active_peak = 0
        for row in sorted(rows_for_workload, key=lambda r: (int(r["time_step"]), r["event_type"])):
            oid = row["object_id"]
            if row["event_type"] == "object_create" and oid:
                size = fnum(row["size_units"])
                cls = row["object_class"]
                active[oid] = (size, cls)
                objects[oid] = (int(row["time_step"]), duration, size, cls)
            if row["event_type"] == "object_evict" and oid and oid in active:
                start, _end, size, cls = objects.get(oid, (0, duration, active[oid][0], active[oid][1]))
                objects[oid] = (start, int(row["time_step"]), size, cls)
                active.pop(oid, None)
            active_peak = max(active_peak, len(active))
            live_peak = max(live_peak, sum(size for size, _cls in active.values()))

        object_count = max(1, len(objects))
        object_events = sum(event_counts[name] for name in OBJECT_EVENTS)
        migration_events = sum(event_counts[name] for name in MIGRATION_EVENTS)
        dag_events = sum(event_counts[name] for name in DAG_EVENTS)
        durable_events = sum(event_counts[name] for name in DURABLE_EVENTS)
        verifier_events = sum(event_counts[name] for name in VERIFIER_EVENTS)
        summary = summary_by_workload[workload]
        dag = dag_by_workload.get(workload, {})
        object_benefit, dag_benefit = architecture_base_benefits(summary, dag)

        rows.append(
            {
                "workload_class": workload,
                "duration_steps": duration,
                "event_count": len(rows_for_workload),
                "event_rate": round(len(rows_for_workload) / duration, 6),
                "metadata_ops": object_events,
                "metadata_ops_per_step": round(object_events / duration, 6),
                "object_policy_ops_per_step": round(object_events / duration, 6),
                "migration_events": migration_events,
                "migration_rate": round(migration_events / duration, 6),
                "migration_events_per_object_lifetime": round(migration_events / object_count, 6),
                "dag_events": dag_events,
                "dag_event_rate": round(dag_events / duration, 6),
                "verifier_events": verifier_events,
                "verifier_event_rate": round(verifier_events / duration, 6),
                "durable_events": durable_events,
                "durable_rate": round(durable_events / duration, 6),
                "active_object_peak": active_peak,
                "live_bytes_peak": round(live_peak, 6),
                "object_count": object_count,
                "max_dag_width": dag.get("max_dag_width", "0"),
                "max_dag_depth": dag.get("max_dag_depth", "0"),
                "mean_verifier_delay": dag.get("mean_verifier_delay", "0"),
                "verifier_results": dag.get("verifier_results", "0"),
                "architecture_option": summary.get("architecture_option", ""),
                "benefit_object_reuse": object_benefit,
                "benefit_branch_verifier_durable": dag_benefit,
                "evidence_label": "synthetic",
            }
        )
    return rows


def score_options(rate: dict[str, object], metadata_st: float, migration_st: float, dag_st: float, durable_st: float, preempt_st: float) -> dict[str, object]:
    metadata_rate = float(rate["metadata_ops_per_step"])
    policy_rate = float(rate["object_policy_ops_per_step"])
    migration_rate = float(rate["migration_rate"])
    dag_rate = float(rate["dag_event_rate"]) * max(1.0, fnum(str(rate["max_dag_width"])))
    verifier_rate = float(rate["verifier_event_rate"]) * max(1.0, fnum(str(rate["mean_verifier_delay"])))
    durable_rate = float(rate["durable_rate"])
    preempt_rate = dag_rate + migration_rate

    rho_registry, w_registry = queue_delay(metadata_rate, metadata_st)
    rho_policy, w_policy = queue_delay(policy_rate, metadata_st * 0.55)
    rho_migration, w_migration = queue_delay(migration_rate, migration_st)
    rho_dag, w_dag = queue_delay(dag_rate, dag_st)
    rho_verifier, w_verifier = queue_delay(verifier_rate, dag_st * 0.7)
    rho_durable, w_durable = queue_delay(durable_rate, durable_st)
    rho_preempt, w_preempt = queue_delay(preempt_rate, preempt_st)

    q_registry = metadata_rate * w_registry
    q_policy = policy_rate * w_policy
    q_migration = migration_rate * w_migration
    q_dag = dag_rate * w_dag
    q_verifier = verifier_rate * w_verifier
    q_durable = durable_rate * w_durable
    q_preempt = preempt_rate * w_preempt

    object_benefit = float(rate["benefit_object_reuse"])
    dag_benefit = float(rate["benefit_branch_verifier_durable"])
    net_a = 0.0
    net_b = object_benefit - (q_registry + q_policy + q_migration)
    net_c = object_benefit + dag_benefit - (q_registry + q_policy + q_migration + q_dag + q_verifier + q_durable + q_preempt)
    nets = {
        "A_conventional_request_model_kv_serving": net_a,
        "B_memory_object_aware_runtime": net_b,
        "C_trajectory_dag_memory_fabric": net_c,
    }
    winner = max(OPTION_ORDER, key=lambda option: (nets[option], -OPTION_ORDER.index(option)))
    overheads = {
        "registry": q_registry,
        "object_policy": q_policy,
        "migration": q_migration,
        "dag_coordination": q_dag,
        "verifier_sync": q_verifier,
        "durable_consistency": q_durable,
        "preemption_checkpoint": q_preempt,
    }
    dominant = max(overheads, key=overheads.get)
    return {
        "rho_registry": round(rho_registry, 6),
        "rho_policy": round(rho_policy, 6),
        "rho_migration": round(rho_migration, 6),
        "rho_dag": round(rho_dag, 6),
        "rho_verifier": round(rho_verifier, 6),
        "rho_durable": round(rho_durable, 6),
        "rho_preempt": round(rho_preempt, 6),
        "q_registry": round(q_registry, 6),
        "q_object_policy": round(q_policy, 6),
        "q_migration": round(q_migration, 6),
        "q_dag": round(q_dag, 6),
        "q_verifier_sync": round(q_verifier, 6),
        "q_durable_consistency": round(q_durable, 6),
        "q_preemption_checkpoint": round(q_preempt, 6),
        "net_A": round(net_a, 6),
        "net_B": round(net_b, 6),
        "net_C": round(net_c, 6),
        "winner": winner,
        "dominant_overhead": dominant,
    }


def sweep(rate_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for rate in rate_rows:
        for metadata, migration, dag, durable, preempt in product(MULTIPLIERS, MULTIPLIERS, MULTIPLIERS, [0.0, 0.5, 1.0, 2.0, 4.0, 8.0], [0.0, 0.5, 1.0, 2.0, 4.0]):
            result = score_options(rate, metadata, migration, dag, durable, preempt)
            rows.append(
                {
                    "workload_class": rate["workload_class"],
                    "metadata_service_time": metadata,
                    "migration_service_time": migration,
                    "dag_coordination_service_time": dag,
                    "durable_write_service_time": durable,
                    "preemption_checkpoint_service_time": preempt,
                    "benefit_object_reuse": rate["benefit_object_reuse"],
                    "benefit_branch_verifier_durable": rate["benefit_branch_verifier_durable"],
                    **result,
                    "evidence_label": "synthetic",
                }
            )
    return rows


def winner_summary(rate_rows: list[dict[str, object]], sweep_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for rate in rate_rows:
        workload = str(rate["workload_class"])
        low = score_options(rate, 0.0, 0.0, 0.0, 0.0, 0.0)
        moderate = score_options(rate, 0.5, 0.5, 0.5, 0.5, 0.5)
        high_object = score_options(rate, 16.0, 16.0, 0.5, 0.5, 0.5)
        high_dag = score_options(rate, 0.5, 0.5, 16.0, 8.0, 4.0)
        object_reversal = ""
        if low["winner"] != "A_conventional_request_model_kv_serving":
            object_reversal = next(
                (
                    multiplier
                    for multiplier in MULTIPLIERS
                    if multiplier > 0
                    and score_options(rate, multiplier, multiplier, 0.5, 0.5, 0.5)["winner"]
                    == "A_conventional_request_model_kv_serving"
                ),
                "",
            )
        dag_reversal = ""
        if low["winner"] == "C_trajectory_dag_memory_fabric":
            dag_reversal = next(
                (
                    multiplier
                    for multiplier in MULTIPLIERS
                    if multiplier > 0
                    and score_options(rate, 0.5, 0.5, multiplier, min(multiplier, 8.0), min(multiplier, 4.0))["winner"]
                    != "C_trajectory_dag_memory_fabric"
                ),
                "",
            )
        rows.append(
            {
                "workload_class": workload,
                "trace_architecture_option": rate["architecture_option"],
                "low_overhead_winner": low["winner"],
                "moderate_overhead_winner": moderate["winner"],
                "high_object_overhead_winner": high_object["winner"],
                "high_dag_overhead_winner": high_dag["winner"],
                "first_object_reversal_metadata_service_time": object_reversal,
                "first_non_C_dag_service_time": dag_reversal,
                "dominant_high_object_overhead": high_object["dominant_overhead"],
                "dominant_high_dag_overhead": high_dag["dominant_overhead"],
                "evidence_label": "synthetic",
            }
        )
    return rows


def failure_modes() -> list[dict[str, object]]:
    return [
        {"failure_mode": "registry_saturation", "overhead_term": "metadata registry", "symptom": "object-aware scheduling reverses to Option A as metadata utilization approaches one", "trace_signal": "metadata_ops_per_step high relative to service-rate knob", "mitigation_or_test": "batch registry updates or coarsen scheduling unit", "evidence_label": "derived"},
        {"failure_mode": "policy_loop_hot_path", "overhead_term": "object policy", "symptom": "per-object decisions dominate small control workloads", "trace_signal": "many object events but zero non-KV retained-value share", "mitigation_or_test": "disable Option B/C on controls", "evidence_label": "derived"},
        {"failure_mode": "migration_queue_saturation", "overhead_term": "migration bandwidth contention", "symptom": "tier moves erase reuse benefit", "trace_signal": "migration_events_per_object_lifetime rises", "mitigation_or_test": "pin hot objects or raise migration threshold", "evidence_label": "derived"},
        {"failure_mode": "dag_coordinator_bottleneck", "overhead_term": "DAG coordination", "symptom": "Option C loses when branch width multiplies coordination events", "trace_signal": "max_dag_width and dag_event_rate high", "mitigation_or_test": "shard trajectory graph by branch subtree", "evidence_label": "derived"},
        {"failure_mode": "verifier_barrier_delay", "overhead_term": "verifier synchronization", "symptom": "retaining verifier state is not enough when barriers serialize progress", "trace_signal": "mean_verifier_delay and verifier_event_rate high", "mitigation_or_test": "asynchronous verifier results with explicit stale-state bounds", "evidence_label": "derived"},
        {"failure_mode": "durable_consistency_amplification", "overhead_term": "durable consistency", "symptom": "workspace correctness writes dominate trajectory benefit", "trace_signal": "workspace_write or workspace_compact rate high", "mitigation_or_test": "append-only logs plus delayed compaction", "evidence_label": "derived"},
        {"failure_mode": "preemption_checkpoint_tax", "overhead_term": "preemption/checkpoint", "symptom": "fine-grained coordination increases checkpoint state", "trace_signal": "migration plus DAG event rates rise together", "mitigation_or_test": "checkpoint only stable trajectory cuts", "evidence_label": "derived"},
    ]


def main() -> None:
    events = read_csv(DATA / "agentic_trace_events_v2.csv")
    summary = read_csv(DATA / "trace_workload_summary.csv")
    dag = read_csv(DATA / "trace_branch_dag_metrics.csv")
    _options = read_csv(DATA / "architecture_options.csv")
    rate_rows = reconstruct_rates(events, summary, dag)
    sweep_rows = sweep(rate_rows)
    winner_rows = winner_summary(rate_rows, sweep_rows)
    failure_rows = failure_modes()

    write_csv(DATA / "queueing_trace_rates.csv", rate_rows)
    write_csv(DATA / "queueing_overhead_sweep.csv", sweep_rows)
    write_csv(DATA / "queueing_architecture_winners.csv", winner_rows)
    write_csv(DATA / "queueing_failure_modes.csv", failure_rows)
    print(f"wrote {DATA / 'queueing_trace_rates.csv'} rows={len(rate_rows)}")
    print(f"wrote {DATA / 'queueing_overhead_sweep.csv'} rows={len(sweep_rows)}")
    print(f"wrote {DATA / 'queueing_architecture_winners.csv'} rows={len(winner_rows)}")
    print(f"wrote {DATA / 'queueing_failure_modes.csv'} rows={len(failure_rows)}")
    for row in winner_rows:
        print(
            "winner",
            row["workload_class"],
            "low=" + str(row["low_overhead_winner"]).split("_")[0],
            "high_object=" + str(row["high_object_overhead_winner"]).split("_")[0],
            "high_dag=" + str(row["high_dag_overhead_winner"]).split("_")[0],
        )


if __name__ == "__main__":
    main()
