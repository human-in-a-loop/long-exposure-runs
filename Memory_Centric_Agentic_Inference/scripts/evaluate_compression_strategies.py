# created: 2026-05-11T15:38:00Z
# cycle: 9
# run_id: run-2026-05-11T121649Z
# agent: worker
# milestone: M-COMP-1

"""Evaluate synthetic compression/offload strategies over trace v2 objects."""

from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
PROJECT = ROOT / "memory-centric-agentic"

STRATEGIES = [
    "keep_hot",
    "lossless_compress",
    "lossy_summarize",
    "summary_plus_pointer",
    "offload_full",
    "recompute_on_demand",
]

ARCH_SHORT = {
    "A_conventional_request_model_kv_serving": "A",
    "B_memory_object_aware_runtime": "B",
    "C_trajectory_dag_memory_fabric": "C",
}

LOSSY_UNSAFE_CLASSES = {
    "retrieved context",
    "semantic cache entry",
    "tool output",
    "verifier state",
    "branch state",
    "trajectory log",
    "durable workspace",
}

REPLAY_CLASSES = {
    "tool output",
    "verifier state",
    "branch state",
    "trajectory log",
    "durable workspace",
}

STRATEGY = {
    "keep_hot": {"bytes_saved": 0.0, "metadata": 0.02, "reconstruct": 0.0, "transfer": 0.0, "queue": 0.0, "loss": 0.0, "prov": 0.0},
    "lossless_compress": {"bytes_saved": 0.38, "metadata": 0.10, "reconstruct": 0.15, "transfer": 0.30, "queue": 0.30, "loss": 0.0, "prov": 0.0},
    "lossy_summarize": {"bytes_saved": 0.72, "metadata": 0.16, "reconstruct": 0.20, "transfer": 0.44, "queue": 0.42, "loss": 0.55, "prov": 0.45},
    "summary_plus_pointer": {"bytes_saved": 0.58, "metadata": 0.24, "reconstruct": 0.28, "transfer": 0.36, "queue": 0.34, "loss": 0.04, "prov": 0.08},
    "offload_full": {"bytes_saved": 0.82, "metadata": 0.18, "reconstruct": 0.45, "transfer": 0.22, "queue": 0.22, "loss": 0.0, "prov": 0.03},
    "recompute_on_demand": {"bytes_saved": 0.88, "metadata": 0.08, "reconstruct": 0.72, "transfer": 0.12, "queue": 0.18, "loss": 0.12, "prov": 0.16},
}


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


def fnum(value: str | float | int | None, default: float = 0.0) -> float:
    try:
        return float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return default


def boolish(value: str) -> bool:
    return value.strip().lower() == "true"


def architecture_short(value: str) -> str:
    return ARCH_SHORT.get(value, value[:1] or "A")


def object_aggregates() -> list[dict[str, object]]:
    lifetimes = read_csv(DATA / "trace_object_lifetimes.csv")
    reuse_rows = read_csv(DATA / "trace_reuse_intervals.csv")
    events = read_csv(DATA / "agentic_trace_events_v2.csv")
    summary = {row["workload_class"]: row for row in read_csv(DATA / "trace_workload_summary.csv")}

    reuse_by_key: dict[tuple[str, str], list[float]] = defaultdict(list)
    for row in reuse_rows:
        reuse_by_key[(row["workload_class"], row["object_class"])].append(fnum(row["reuse_distance"]))

    event_stats: dict[tuple[str, str], dict[str, float]] = defaultdict(lambda: defaultdict(float))
    objects_seen: dict[tuple[str, str], set[str]] = defaultdict(set)
    for row in events:
        key = (row["workload_class"], row["object_class"])
        if not row["object_class"]:
            continue
        if row["object_id"]:
            objects_seen[key].add(row["object_id"])
        if boolish(row["correctness_sensitive"]):
            event_stats[key]["correctness_events"] += 1
        if row["provenance_id"]:
            event_stats[key]["provenance_events"] += 1
        if row["invalidation_signal"] and row["invalidation_signal"] != "none":
            event_stats[key]["invalidation_events"] += 1
        if fnum(row["durability_horizon"]) > 0:
            event_stats[key]["durable_events"] += 1
        event_stats[key]["events"] += 1

    grouped: dict[tuple[str, str], dict[str, float]] = defaultdict(lambda: defaultdict(float))
    for row in lifetimes:
        key = (row["workload_class"], row["object_class"])
        grouped[key]["object_count"] += 1
        grouped[key]["total_size"] += fnum(row["size_units"])
        grouped[key]["lifetime_sum"] += fnum(row["lifetime"])

    rows: list[dict[str, object]] = []
    for (workload, object_class), values in sorted(grouped.items()):
        count = max(values["object_count"], 1.0)
        stats = event_stats[(workload, object_class)]
        events_count = max(stats["events"], 1.0)
        reuse_values = reuse_by_key[(workload, object_class)]
        provenance_coverage = stats["provenance_events"] / events_count
        correctness_share = stats["correctness_events"] / events_count
        avg_lifetime = values["lifetime_sum"] / count
        avg_reuse_distance = sum(reuse_values) / len(reuse_values) if reuse_values else 0.0
        architecture = summary.get(workload, {}).get("architecture_option", "")
        rows.append(
            {
                "workload_class": workload,
                "object_class": object_class,
                "object_count": int(count),
                "total_size": round(values["total_size"], 6),
                "avg_lifetime": round(avg_lifetime, 6),
                "reuse_count": len(reuse_values),
                "avg_reuse_distance": round(avg_reuse_distance, 6),
                "correctness_sensitive_share": round(correctness_share, 6),
                "provenance_coverage": round(provenance_coverage, 6),
                "invalidation_events": int(stats["invalidation_events"]),
                "durable_events": int(stats["durable_events"]),
                "architecture_option": architecture,
                "architecture_short": architecture_short(architecture),
            }
        )
    return rows


def capacity_pressure(row: dict[str, object]) -> float:
    size_term = min(1.0, fnum(row["total_size"]) / 1800.0)
    life_term = min(1.0, fnum(row["avg_lifetime"]) / 80.0)
    arch_term = {"A": 0.18, "B": 0.40, "C": 0.55}.get(str(row["architecture_short"]), 0.25)
    return round(0.18 + 0.44 * size_term + 0.20 * life_term + arch_term, 6)


def reuse_pressure(row: dict[str, object]) -> float:
    reuse_count = fnum(row["reuse_count"])
    object_count = max(1.0, fnum(row["object_count"]))
    reuse_density = min(1.0, reuse_count / (object_count * 3.0))
    distance_term = min(1.0, fnum(row["avg_reuse_distance"]) / 15.0)
    return round(0.55 * reuse_density + 0.45 * distance_term, 6)


def provenance_need(row: dict[str, object]) -> float:
    cls = str(row["object_class"])
    base = 0.70 if cls in LOSSY_UNSAFE_CLASSES else 0.20
    if cls in {"retrieved context", "semantic cache entry"}:
        base = 0.82
    if cls in REPLAY_CLASSES:
        base = 0.92
    return round(max(base, fnum(row["provenance_coverage"])), 6)


def validity(row: dict[str, object], strategy: str) -> tuple[bool, str]:
    cls = str(row["object_class"])
    correctness = fnum(row["correctness_sensitive_share"]) > 0.0 or cls in REPLAY_CLASSES
    needs_prov = cls in LOSSY_UNSAFE_CLASSES or provenance_need(row) >= 0.75
    has_pointer = fnum(row["provenance_coverage"]) > 0.0
    if strategy == "lossy_summarize" and correctness and (needs_prov or not has_pointer):
        return False, "lossy_without_replay_safe_pointer"
    if strategy == "lossy_summarize" and cls in {"weights", "KV cache"}:
        return False, "lossy_changes_exact_model_or_continuation_state"
    if strategy == "summary_plus_pointer" and needs_prov and not has_pointer:
        return False, "pointer_strategy_missing_provenance"
    if strategy == "recompute_on_demand" and cls in REPLAY_CLASSES and not has_pointer:
        return False, "recompute_missing_authoritative_source"
    return True, ""


def score(row: dict[str, object], strategy: str) -> dict[str, object]:
    valid, reason = validity(row, strategy)
    coeff = STRATEGY[strategy]
    cap = capacity_pressure(row)
    reuse = reuse_pressure(row)
    prov_need = provenance_need(row)
    correct = max(fnum(row["correctness_sensitive_share"]), 1.0 if str(row["object_class"]) in REPLAY_CLASSES else 0.0)
    size_scale = min(2.0, fnum(row["total_size"]) / 900.0)
    arch = str(row["architecture_short"])

    bytes_saved = coeff["bytes_saved"] * size_scale
    transfer_avoided = coeff["transfer"] * reuse * (0.55 + 0.45 * size_scale)
    queue_relief = coeff["queue"] * (0.7 if arch in {"B", "C"} else 0.25) * (0.6 + 0.4 * size_scale)
    reconstruction_cost = coeff["reconstruct"] * (0.35 + reuse + 0.35 * correct)
    metadata_cost = coeff["metadata"] * (1.0 + 0.55 * prov_need + (0.4 if strategy == "summary_plus_pointer" else 0.0))
    provenance_risk = coeff["prov"] * prov_need * (1.0 - min(1.0, fnum(row["provenance_coverage"])))
    correctness_loss = coeff["loss"] * correct * (1.0 + 0.6 * prov_need)
    representation_benefit = 0.0
    if strategy == "summary_plus_pointer" and str(row["object_class"]) in LOSSY_UNSAFE_CLASSES:
        representation_benefit = 0.45 * prov_need + 0.25 * correct
    if strategy == "offload_full" and str(row["object_class"]) in {"durable workspace", "trajectory log"}:
        representation_benefit = 0.18 * prov_need

    net = (
        bytes_saved * cap
        + transfer_avoided
        + queue_relief
        + representation_benefit
        - reconstruction_cost
        - metadata_cost
        - provenance_risk
        - correctness_loss
    )
    if not valid:
        net = -999.0

    return {
        "workload_class": row["workload_class"],
        "object_class": row["object_class"],
        "strategy": strategy,
        "valid": str(valid).lower(),
        "invalid_reason": reason,
        "object_count": row["object_count"],
        "total_size": row["total_size"],
        "capacity_pressure": cap,
        "reuse_pressure": reuse,
        "correctness_sensitive_share": row["correctness_sensitive_share"],
        "provenance_need": prov_need,
        "provenance_coverage": row["provenance_coverage"],
        "bytes_saved_proxy": round(bytes_saved, 6),
        "transfer_avoided_proxy": round(transfer_avoided, 6),
        "queue_relief_proxy": round(queue_relief, 6),
        "representation_preservation_benefit_proxy": round(representation_benefit, 6),
        "reconstruction_cost_proxy": round(reconstruction_cost, 6),
        "metadata_cost_proxy": round(metadata_cost, 6),
        "provenance_risk_proxy": round(provenance_risk, 6),
        "correctness_loss_risk_proxy": round(correctness_loss, 6),
        "net_compression_value": round(net, 6),
        "architecture_option": row["architecture_option"],
        "evidence_label": "synthetic",
    }


def queue_threshold_context(workload: str, winners: dict[str, dict[str, str]]) -> dict[str, str]:
    win = winners.get(workload, {})
    return {
        "trace_architecture_option": win.get("trace_architecture_option", ""),
        "high_object_overhead_winner": win.get("high_object_overhead_winner", ""),
        "high_dag_overhead_winner": win.get("high_dag_overhead_winner", ""),
    }


def object_queue_interactions(scores: list[dict[str, object]]) -> list[dict[str, object]]:
    winners = {row["workload_class"]: row for row in read_csv(DATA / "queueing_architecture_winners.csv")}
    rows: list[dict[str, object]] = []
    for item in sorted(scores, key=lambda r: (str(r["workload_class"]), str(r["object_class"]), str(r["strategy"]))):
        if item["valid"] != "true" or item["strategy"] == "keep_hot":
            continue
        workload = str(item["workload_class"])
        strategy = str(item["strategy"])
        ctx = queue_threshold_context(workload, winners)
        arch = ctx["trace_architecture_option"]
        high_object = ctx["high_object_overhead_winner"]
        high_dag = ctx["high_dag_overhead_winner"]
        relief = fnum(item["queue_relief_proxy"])
        overhead = fnum(item["metadata_cost_proxy"]) + fnum(item["reconstruction_cost_proxy"])
        net = relief - overhead
        object_threshold_relevant = (
            architecture_short(arch) in {"B", "C"}
            and architecture_short(high_object) == "A"
            and strategy in {"lossless_compress", "summary_plus_pointer"}
        )
        dag_threshold_relevant = (
            architecture_short(arch) == "C"
            and architecture_short(high_dag) == "B"
            and strategy in {"summary_plus_pointer", "offload_full"}
        )
        selected_positive = net > 0.0 and (object_threshold_relevant or dag_threshold_relevant)
        if selected_positive and object_threshold_relevant:
            interaction = "helps_avoid_object_overhead_reversal"
        elif selected_positive and dag_threshold_relevant:
            interaction = "helps_shift_C_state_to_B_when_DAG_overhead_high"
        elif net < -0.25 and (object_threshold_relevant or dag_threshold_relevant):
            interaction = "can_worsen_or_cause_reversal"
        else:
            interaction = "local_tradeoff_only"
        rows.append(
            {
                "workload_class": workload,
                "object_class": item["object_class"],
                "strategy": strategy,
                "trace_architecture_option": arch,
                "high_object_overhead_winner": high_object,
                "high_dag_overhead_winner": high_dag,
                "queue_relief_proxy": round(relief, 6),
                "added_reconstruction_metadata_proxy": round(overhead, 6),
                "net_queue_effect_proxy": round(net, 6),
                "object_threshold_relevant": str(object_threshold_relevant).lower(),
                "dag_threshold_relevant": str(dag_threshold_relevant).lower(),
                "selected_positive_for_queue_help": str(selected_positive).lower(),
                "interaction": interaction,
                "evidence_label": "synthetic",
            }
        )
    return rows


def queue_interactions(object_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    winners = {row["workload_class"]: row for row in read_csv(DATA / "queueing_architecture_winners.csv")}
    grouped: dict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)
    for row in object_rows:
        grouped[(str(row["workload_class"]), str(row["strategy"]))].append(row)

    rows: list[dict[str, object]] = []
    for (workload, strategy), items in sorted(grouped.items()):
        ctx = queue_threshold_context(workload, winners)
        arch = ctx["trace_architecture_option"]
        if architecture_short(arch) == "A":
            continue
        relief = sum(fnum(item["queue_relief_proxy"]) for item in items)
        overhead = sum(fnum(item["added_reconstruction_metadata_proxy"]) for item in items)
        net = relief - overhead
        positive_items = [item for item in items if str(item["selected_positive_for_queue_help"]) == "true"]
        positive_labels = {str(item["interaction"]) for item in positive_items}
        positive_relief = sum(fnum(item["queue_relief_proxy"]) for item in positive_items)
        positive_net = sum(fnum(item["net_queue_effect_proxy"]) for item in positive_items)
        high_object = ctx["high_object_overhead_winner"]
        high_dag = ctx["high_dag_overhead_winner"]
        if "helps_avoid_object_overhead_reversal" in positive_labels:
            interaction = "helps_avoid_object_overhead_reversal"
            reported_relief = positive_relief
            reported_net = positive_net
            reported_overhead = positive_relief - positive_net
        elif "helps_shift_C_state_to_B_when_DAG_overhead_high" in positive_labels:
            interaction = "helps_shift_C_state_to_B_when_DAG_overhead_high"
            reported_relief = positive_relief
            reported_net = positive_net
            reported_overhead = positive_relief - positive_net
        elif net < -0.75:
            interaction = "can_worsen_or_cause_reversal"
            reported_relief = relief
            reported_net = net
            reported_overhead = overhead
        else:
            interaction = "local_tradeoff_only"
            reported_relief = relief
            reported_net = net
            reported_overhead = overhead
        evidence = "; ".join(
            f"{item['object_class']}:{round(fnum(item['net_queue_effect_proxy']), 6)}" for item in positive_items
        )
        rows.append(
            {
                "workload_class": workload,
                "strategy": strategy,
                "trace_architecture_option": arch,
                "high_object_overhead_winner": high_object,
                "high_dag_overhead_winner": high_dag,
                "queue_relief_proxy_sum": round(reported_relief, 6),
                "added_reconstruction_metadata_proxy_sum": round(reported_overhead, 6),
                "net_queue_effect_proxy": round(reported_net, 6),
                "positive_object_count": len(positive_items),
                "positive_object_evidence": evidence,
                "raw_strategy_queue_relief_proxy_sum": round(relief, 6),
                "raw_strategy_added_overhead_proxy_sum": round(overhead, 6),
                "raw_strategy_net_queue_effect_proxy": round(net, 6),
                "interaction": interaction,
                "evidence_label": "synthetic",
            }
        )
    return rows


def main() -> None:
    aggregates = object_aggregates()
    scores = [score(row, strategy) for row in aggregates for strategy in STRATEGIES]
    best_rows = []
    safety_failures = []
    for row in scores:
        if row["valid"] == "false":
            safety_failures.append(row)
    by_object: dict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)
    for row in scores:
        by_object[(str(row["workload_class"]), str(row["object_class"]))].append(row)
    for key, rows in sorted(by_object.items()):
        best = max(rows, key=lambda r: fnum(r["net_compression_value"]))
        best_rows.append(
            {
                "workload_class": key[0],
                "object_class": key[1],
                "best_strategy": best["strategy"],
                "net_compression_value": best["net_compression_value"],
                "capacity_pressure": best["capacity_pressure"],
                "reuse_pressure": best["reuse_pressure"],
                "provenance_need": best["provenance_need"],
                "correctness_sensitive_share": best["correctness_sensitive_share"],
                "architecture_option": best["architecture_option"],
                "evidence_label": "synthetic",
            }
        )

    workload_summary = []
    by_workload: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in best_rows:
        by_workload[str(row["workload_class"])].append(row)
    for workload, rows in sorted(by_workload.items()):
        strategy_counts = {strategy: 0 for strategy in STRATEGIES}
        for row in rows:
            strategy_counts[str(row["best_strategy"])] += 1
        workload_summary.append(
            {
                "workload_class": workload,
                "object_classes_evaluated": len(rows),
                "best_strategy_counts": "; ".join(f"{k}={v}" for k, v in strategy_counts.items() if v),
                "ordinary_control_boundary": str(workload in {"single-turn chat control", "batch summarization/offline inference control"}).lower(),
                "rag_provenance_boundary": str(workload == "RAG" and any(r["best_strategy"] == "summary_plus_pointer" for r in rows)).lower(),
                "agentic_replay_boundary": str(any(r["best_strategy"] == "summary_plus_pointer" for r in rows) and workload not in {"RAG", "single-turn chat control", "batch summarization/offline inference control"}).lower(),
                "evidence_label": "synthetic",
            }
        )

    write_csv(DATA / "compression_strategy_scores.csv", scores)
    write_csv(DATA / "compression_best_strategy_by_object.csv", best_rows)
    write_csv(DATA / "compression_workload_summary.csv", workload_summary)
    write_csv(DATA / "compression_safety_failures.csv", safety_failures)
    object_queue_rows = object_queue_interactions(scores)
    write_csv(DATA / "compression_object_queue_interactions.csv", object_queue_rows)
    write_csv(DATA / "compression_queue_interactions.csv", queue_interactions(object_queue_rows))

    print(f"wrote {DATA / 'compression_strategy_scores.csv'} rows={len(scores)}")
    print(f"wrote {DATA / 'compression_best_strategy_by_object.csv'} rows={len(best_rows)}")
    print(f"wrote {DATA / 'compression_workload_summary.csv'} rows={len(workload_summary)}")
    print(f"wrote {DATA / 'compression_safety_failures.csv'} rows={len(safety_failures)}")
    print(f"wrote {DATA / 'compression_object_queue_interactions.csv'} rows={len(object_queue_rows)}")
    print(f"wrote {DATA / 'compression_queue_interactions.csv'}")
    for row in workload_summary:
        print(f"summary {row['workload_class']}: {row['best_strategy_counts']}")


if __name__ == "__main__":
    main()
