# created: 2026-05-11T14:36:00Z
# cycle: 7
# run_id: run-2026-05-11T121649Z
# agent: worker
# milestone: M-TRACE-1

"""Generate deterministic synthetic trace v2 for agentic memory objects."""

from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path
from random import Random

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
PROJECT = ROOT / "memory-centric-agentic"
SEED = 20260511

FIELDS = [
    "trace_id",
    "run_id",
    "workload_class",
    "time_step",
    "event_type",
    "object_id",
    "object_class",
    "size_units",
    "tier",
    "parent_object_id",
    "trajectory_node_id",
    "branch_id",
    "provenance_id",
    "reuse_distance",
    "reuse_probability_hint",
    "correctness_sensitive",
    "recompute_cost_hint",
    "loss_cost_hint",
    "durability_horizon",
    "verifier_id",
    "merge_state",
    "source_version",
    "invalidation_signal",
    "evidence_label",
]

WORKLOADS = [
    {
        "name": "single-turn chat control",
        "taxonomy": "single-turn chat",
        "steps": 26,
        "objects": ["weights", "KV cache", "prefix cache", "intermediate scratch"],
        "branch": 0,
        "tools": 0,
        "verifiers": 0,
        "durable": 0,
        "rag": False,
        "architecture": "A_conventional_request_model_kv_serving",
    },
    {
        "name": "batch summarization/offline inference control",
        "taxonomy": "batch summarization",
        "steps": 40,
        "objects": ["weights", "KV cache", "intermediate scratch"],
        "branch": 0,
        "tools": 0,
        "verifiers": 0,
        "durable": 0,
        "rag": False,
        "architecture": "A_conventional_request_model_kv_serving",
    },
    {
        "name": "RAG",
        "taxonomy": "RAG",
        "steps": 60,
        "objects": ["weights", "KV cache", "prefix cache", "retrieved context", "semantic cache entry", "tool output"],
        "branch": 0,
        "tools": 1,
        "verifiers": 0,
        "durable": 1,
        "rag": True,
        "architecture": "B_memory_object_aware_runtime",
    },
    {
        "name": "code-agent loop",
        "taxonomy": "code-agent loop",
        "steps": 85,
        "objects": ["weights", "KV cache", "prefix cache", "tool output", "branch state", "verifier state", "trajectory log", "durable workspace"],
        "branch": 2,
        "tools": 3,
        "verifiers": 2,
        "durable": 3,
        "rag": False,
        "architecture": "C_trajectory_dag_memory_fabric",
    },
    {
        "name": "verification-heavy",
        "taxonomy": "verification-heavy agent",
        "steps": 80,
        "objects": ["weights", "KV cache", "branch state", "verifier state", "tool output", "trajectory log"],
        "branch": 3,
        "tools": 2,
        "verifiers": 4,
        "durable": 1,
        "rag": False,
        "architecture": "C_trajectory_dag_memory_fabric",
    },
    {
        "name": "multi-agent branch/merge",
        "taxonomy": "multi-agent branch/merge run",
        "steps": 95,
        "objects": ["weights", "KV cache", "prefix cache", "branch state", "verifier state", "trajectory log", "durable workspace", "tool output"],
        "branch": 4,
        "tools": 3,
        "verifiers": 3,
        "durable": 4,
        "rag": False,
        "architecture": "C_trajectory_dag_memory_fabric",
    },
]

SIZE = {
    "weights": 900,
    "KV cache": 20,
    "prefix cache": 40,
    "retrieved context": 55,
    "tool output": 70,
    "intermediate scratch": 25,
    "branch state": 65,
    "verifier state": 50,
    "trajectory log": 35,
    "durable workspace": 80,
    "semantic cache entry": 45,
}

TIER = {
    "weights": "HBM/GPU memory",
    "KV cache": "HBM/GPU memory",
    "prefix cache": "CPU DRAM",
    "retrieved context": "CPU DRAM",
    "tool output": "durable workspace",
    "intermediate scratch": "CPU DRAM",
    "branch state": "CPU DRAM",
    "verifier state": "CPU DRAM",
    "trajectory log": "NVMe",
    "durable workspace": "NVMe",
    "semantic cache entry": "remote object store",
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


def event(base: dict[str, object], t: int, event_type: str, **kw: object) -> dict[str, object]:
    row = {field: "" for field in FIELDS}
    row.update(base)
    row.update({"time_step": t, "event_type": event_type, "evidence_label": "synthetic"})
    row.update(kw)
    return row


def make_object_id(run_id: str, object_class: str, n: int) -> str:
    return f"{run_id}:{object_class.replace(' ', '_').replace('/', '_')}:{n}"


def generate_trace(config: dict[str, object], rng: Random) -> list[dict[str, object]]:
    name = str(config["name"])
    run_id = name.lower().replace("/", "_").replace(" ", "_")
    base = {"trace_id": f"trace-v2-{run_id}", "run_id": run_id, "workload_class": name}
    events: list[dict[str, object]] = [event(base, 0, "run_start", source_version="synthetic_v2")]
    active: dict[str, str] = {}
    birth_time: dict[str, int] = {}
    last_access: dict[str, int] = {}
    counts: defaultdict[str, int] = defaultdict(int)

    def create(cls: str, t: int, parent: str = "", branch: str = "", node: str = "", prov: str = "") -> str:
        counts[cls] += 1
        oid = make_object_id(run_id, cls, counts[cls])
        active[oid] = cls
        birth_time[oid] = t
        correct = str(cls in {"retrieved context", "tool output", "branch state", "verifier state", "trajectory log", "durable workspace", "semantic cache entry"}).lower()
        horizon = 0
        if cls in {"durable workspace", "trajectory log", "tool output"}:
            horizon = int(config["steps"]) * (2 if config["architecture"] == "C_trajectory_dag_memory_fabric" else 1)
        events.append(event(base, t, "object_create", object_id=oid, object_class=cls, size_units=SIZE[cls] + rng.randint(0, 12), tier=TIER[cls], parent_object_id=parent, trajectory_node_id=node, branch_id=branch, provenance_id=prov, reuse_probability_hint=0.25 if cls in {"KV cache", "intermediate scratch"} else 0.72, correctness_sensitive=correct, recompute_cost_hint=SIZE[cls] // 3, loss_cost_hint=SIZE[cls] if correct == "true" else 0, durability_horizon=horizon, source_version="synthetic_v2", invalidation_signal="none"))
        events.append(event(base, t + 1, "object_place", object_id=oid, object_class=cls, size_units=SIZE[cls], tier=TIER[cls], trajectory_node_id=node, branch_id=branch, provenance_id=prov, correctness_sensitive=correct, durability_horizon=horizon, source_version="synthetic_v2", invalidation_signal="none"))
        last_access[oid] = t + 1
        return oid

    weights = create("weights", 1)
    prefix = create("prefix cache", 2) if "prefix cache" in config["objects"] else ""
    kv = create("KV cache", 3)
    scratch = create("intermediate scratch", 4) if "intermediate scratch" in config["objects"] else ""
    if scratch:
        events.append(event(base, 10, "object_update", object_id=scratch, object_class="intermediate scratch", size_units=SIZE["intermediate scratch"] + 5, tier=TIER["intermediate scratch"], correctness_sensitive="false", source_version="synthetic_v2"))

    if config["rag"]:
        sem = create("semantic cache entry", 8, prov="prov:corpus:v1")
        ret = create("retrieved context", 9, parent=sem, prov="prov:corpus:v1")
        events.append(event(base, 12, "semantic_cache_lookup", object_id=sem, object_class="semantic cache entry", size_units=SIZE["semantic cache entry"], tier=TIER["semantic cache entry"], provenance_id="prov:corpus:v1", reuse_distance=4, reuse_probability_hint=0.81, correctness_sensitive="true", recompute_cost_hint=30, loss_cost_hint=90, source_version="corpus:v1", invalidation_signal="none"))
        events.append(event(base, 16, "semantic_cache_insert", object_id=sem, object_class="semantic cache entry", size_units=SIZE["semantic cache entry"], tier=TIER["semantic cache entry"], provenance_id="prov:corpus:v1", reuse_probability_hint=0.81, correctness_sensitive="true", source_version="corpus:v1", invalidation_signal="none"))
        events.append(event(base, 22, "tool_call_start", trajectory_node_id="rag-node-1", source_version="synthetic_v2"))
        tool = create("tool output", 24, parent=ret, node="rag-node-1", prov="prov:retriever:1")
        events.append(event(base, 26, "tool_call_result", object_id=tool, object_class="tool output", size_units=SIZE["tool output"], tier=TIER["tool output"], trajectory_node_id="rag-node-1", provenance_id="prov:retriever:1", correctness_sensitive="true", durability_horizon=int(config["steps"]), source_version="retriever:v1", invalidation_signal="none"))

    branch_ids = []
    for b in range(int(config["branch"])):
        t = 12 + b * 9
        bid = f"{run_id}:branch:{b + 1}"
        node = f"{run_id}:node:{b + 1}"
        branch_ids.append(bid)
        events.append(event(base, t, "branch_fork", trajectory_node_id=node, branch_id=bid, merge_state="forked", source_version="synthetic_v2"))
        create("branch state", t + 1, parent=kv, branch=bid, node=node, prov=f"prov:{bid}")
        create("trajectory log", t + 2, parent=kv, branch=bid, node=node, prov=f"prov:{bid}")

    for i in range(int(config["tools"])):
        t = 18 + i * 13
        bid = branch_ids[i % len(branch_ids)] if branch_ids else ""
        node = f"{run_id}:tool-node:{i + 1}"
        events.append(event(base, t, "tool_call_start", trajectory_node_id=node, branch_id=bid, source_version="synthetic_v2"))
        oid = create("tool output", t + 2, branch=bid, node=node, prov=f"prov:tool:{i + 1}")
        events.append(event(base, t + 3, "tool_call_result", object_id=oid, object_class="tool output", size_units=SIZE["tool output"], tier=TIER["tool output"], trajectory_node_id=node, branch_id=bid, provenance_id=f"prov:tool:{i + 1}", correctness_sensitive="true", durability_horizon=int(config["steps"]), source_version="tool:v1", invalidation_signal="none"))

    for i in range(int(config["verifiers"])):
        t = 25 + i * 11
        bid = branch_ids[i % len(branch_ids)] if branch_ids else ""
        vid = f"{run_id}:verifier:{i + 1}"
        node = f"{run_id}:verify-node:{i + 1}"
        events.append(event(base, t, "verifier_start", trajectory_node_id=node, branch_id=bid, verifier_id=vid, source_version="synthetic_v2"))
        oid = create("verifier state", t + 1, branch=bid, node=node, prov=f"prov:{vid}")
        events.append(event(base, t + 5 + i % 3, "verifier_result", object_id=oid, object_class="verifier state", size_units=SIZE["verifier state"], tier=TIER["verifier state"], trajectory_node_id=node, branch_id=bid, provenance_id=f"prov:{vid}", verifier_id=vid, merge_state="accepted" if i % 2 == 0 else "rejected", correctness_sensitive="true", loss_cost_hint=130, source_version="verifier:v1", invalidation_signal="none"))

    for i in range(int(config["durable"])):
        t = 30 + i * 12
        cls = "durable workspace" if "durable workspace" in config["objects"] else "tool output"
        oid = create(cls, t, node=f"{run_id}:workspace-node:{i + 1}", prov=f"prov:workspace:{i + 1}")
        events.append(event(base, t + 1, "workspace_write", object_id=oid, object_class=cls, size_units=SIZE[cls] + i * 10, tier=TIER[cls], trajectory_node_id=f"{run_id}:workspace-node:{i + 1}", provenance_id=f"prov:workspace:{i + 1}", correctness_sensitive="true", durability_horizon=int(config["steps"]) * 2, source_version=f"workspace:v{i + 1}", invalidation_signal="none"))
        if i == int(config["durable"]) - 1 and cls == "durable workspace":
            events.append(event(base, t + 5, "workspace_compact", object_id=oid, object_class=cls, size_units=max(20, SIZE[cls] - 15), tier=TIER[cls], trajectory_node_id=f"{run_id}:workspace-node:{i + 1}", provenance_id=f"prov:workspace:{i + 1}", correctness_sensitive="true", durability_horizon=int(config["steps"]) * 2, source_version=f"workspace:v{i + 1}", invalidation_signal="none"))

    for t in range(8, int(config["steps"]), 5):
        for oid, cls in list(active.items()):
            if t <= birth_time.get(oid, t):
                continue
            if cls == "weights" or (cls == "KV cache" and t % 2 == 0) or (cls in {"prefix cache", "retrieved context", "semantic cache entry"} and t % 3 == 0) or (cls in {"tool output", "verifier state", "trajectory log", "durable workspace", "branch state"} and config["architecture"] == "C_trajectory_dag_memory_fabric" and t % 4 == 0):
                rd = max(0, t - last_access.get(oid, t))
                last_access[oid] = t
                events.append(event(base, t, "object_access", object_id=oid, object_class=cls, size_units=SIZE[cls], tier=TIER[cls], reuse_distance=rd, reuse_probability_hint=0.75 if cls != "intermediate scratch" else 0.1, correctness_sensitive=str(cls not in {"weights", "KV cache", "prefix cache", "intermediate scratch"}).lower(), recompute_cost_hint=SIZE[cls] // 3, loss_cost_hint=SIZE[cls] if cls not in {"weights", "KV cache", "prefix cache", "intermediate scratch"} else 0, durability_horizon=int(config["steps"]) if cls in {"tool output", "trajectory log", "durable workspace"} else 0, source_version="synthetic_v2", invalidation_signal="none"))

    for idx, bid in enumerate(branch_ids):
        t = int(config["steps"]) - 16 + idx * 3
        events.append(event(base, t, "branch_merge" if idx % 2 == 0 else "branch_discard", branch_id=bid, trajectory_node_id=f"{run_id}:merge-node:{idx + 1}", merge_state="merged" if idx % 2 == 0 else "discarded", source_version="synthetic_v2"))

    for oid, cls in list(active.items()):
        if cls in {"weights", "durable workspace", "trajectory log", "tool output"} and config["architecture"] != "A_conventional_request_model_kv_serving":
            continue
        events.append(event(base, int(config["steps"]) - 2, "object_evict", object_id=oid, object_class=cls, size_units=SIZE[cls], tier=TIER[cls], correctness_sensitive=str(cls not in {"weights", "KV cache", "prefix cache", "intermediate scratch"}).lower(), source_version="synthetic_v2", invalidation_signal="none"))

    if config["architecture"] == "C_trajectory_dag_memory_fabric":
        migrated = [oid for oid, cls in active.items() if cls in {"branch state", "verifier state", "trajectory log"}]
        for oid in migrated[:3]:
            events.append(event(base, int(config["steps"]) - 8, "object_migrate", object_id=oid, object_class=active[oid], size_units=SIZE[active[oid]], tier="NVMe", correctness_sensitive="true", source_version="synthetic_v2", invalidation_signal="none"))

    events.append(event(base, int(config["steps"]), "run_end", source_version="synthetic_v2"))
    # Stable time-only sort preserves generation order for same-step create/access pairs.
    events.sort(key=lambda r: int(r["time_step"]))
    return events


def derive(events: list[dict[str, object]], arch_by_workload: dict[str, str]) -> tuple[list[dict[str, object]], list[dict[str, object]], list[dict[str, object]], list[dict[str, object]]]:
    creates: dict[str, dict[str, object]] = {}
    ends: dict[str, int] = {}
    accesses: defaultdict[str, list[int]] = defaultdict(list)
    sizes: dict[str, int] = {}
    workloads: dict[str, str] = {}
    classes: dict[str, str] = {}
    run_end: dict[str, int] = {}
    branch_events: defaultdict[str, list[dict[str, object]]] = defaultdict(list)
    verifier_starts: dict[str, int] = {}
    verifier_delays: defaultdict[str, list[int]] = defaultdict(list)
    provenance_req = provenance_ok = 0

    for row in events:
        t = int(row["time_step"])
        run = str(row["run_id"])
        run_end[run] = max(run_end.get(run, 0), t)
        oid = str(row["object_id"])
        if row["event_type"] == "object_create" and oid:
            creates[oid] = row
            sizes[oid] = int(row["size_units"])
            workloads[oid] = str(row["workload_class"])
            classes[oid] = str(row["object_class"])
        if row["event_type"] in {"object_evict", "run_end"} and oid:
            ends[oid] = t
        if row["event_type"] == "object_access" and oid:
            accesses[oid].append(t)
        if row["event_type"] in {"branch_fork", "branch_merge", "branch_discard"}:
            branch_events[str(row["workload_class"])].append(row)
        if row["event_type"] == "verifier_start":
            verifier_starts[str(row["verifier_id"])] = t
        if row["event_type"] == "verifier_result":
            vid = str(row["verifier_id"])
            if vid in verifier_starts:
                verifier_delays[str(row["workload_class"])].append(t - verifier_starts[vid])
        if row["event_type"] in {"semantic_cache_lookup", "semantic_cache_insert", "tool_call_result", "workspace_write"}:
            provenance_req += 1
            if row["provenance_id"]:
                provenance_ok += 1

    lifetimes = []
    for oid, created in creates.items():
        run = str(created["run_id"])
        end = ends.get(oid, run_end[run])
        lifetimes.append({
            "object_id": oid,
            "run_id": run,
            "workload_class": workloads[oid],
            "object_class": classes[oid],
            "birth_time": created["time_step"],
            "end_time": end,
            "lifetime": end - int(created["time_step"]),
            "size_units": sizes[oid],
            "evicted": str(oid in ends).lower(),
            "evidence_label": "synthetic",
        })

    reuse_rows = []
    for oid, times in accesses.items():
        prev = None
        for t in times:
            if prev is not None:
                reuse_rows.append({
                    "object_id": oid,
                    "run_id": str(creates.get(oid, {}).get("run_id", "")),
                    "workload_class": workloads.get(oid, ""),
                    "object_class": classes.get(oid, ""),
                    "access_time": t,
                    "previous_access_time": prev,
                    "reuse_distance": t - prev,
                    "evidence_label": "synthetic",
                })
            prev = t

    dag_rows = []
    for workload in {str(r["workload_class"]) for r in events}:
        active = 0
        max_width = 0
        forks = merges = discards = 0
        for row in sorted(branch_events[workload], key=lambda r: int(r["time_step"])):
            if row["event_type"] == "branch_fork":
                forks += 1
                active += 1
            elif row["event_type"] == "branch_merge":
                merges += 1
                active = max(0, active - 1)
            elif row["event_type"] == "branch_discard":
                discards += 1
                active = max(0, active - 1)
            max_width = max(max_width, active)
        delays = verifier_delays.get(workload, [])
        dag_rows.append({
            "workload_class": workload,
            "branch_forks": forks,
            "branch_merges": merges,
            "branch_discards": discards,
            "max_dag_width": max_width,
            "max_dag_depth": forks if forks else 0,
            "mean_verifier_delay": round(sum(delays) / len(delays), 3) if delays else 0,
            "verifier_results": len(delays),
            "merge_rate": round(merges / forks, 3) if forks else 0,
            "discard_rate": round(discards / forks, 3) if forks else 0,
            "evidence_label": "synthetic",
        })

    summary_rows = []
    for workload in sorted({str(r["workload_class"]) for r in events}):
        wl_events = [r for r in events if r["workload_class"] == workload]
        wl_life = [r for r in lifetimes if r["workload_class"] == workload]
        non_kv = sum(int(r["size_units"]) for r in wl_life if r["object_class"] not in {"weights", "KV cache", "prefix cache", "intermediate scratch"})
        total = sum(int(r["size_units"]) for r in wl_life)
        dag = next(r for r in dag_rows if r["workload_class"] == workload)
        summary_rows.append({
            "workload_class": workload,
            "event_count": len(wl_events),
            "object_count": len(wl_life),
            "object_classes": "; ".join(sorted({str(r["object_class"]) for r in wl_life})),
            "architecture_option": arch_by_workload.get(workload, ""),
            "non_kv_object_size_share": round(non_kv / total, 4) if total else 0,
            "max_dag_width": dag["max_dag_width"],
            "verifier_results": dag["verifier_results"],
            "provenance_coverage": round(provenance_ok / provenance_req, 4) if provenance_req else 1,
            "evidence_label": "synthetic",
        })
    return lifetimes, reuse_rows, dag_rows, summary_rows


def invalid_cases() -> list[dict[str, object]]:
    base = {"trace_id": "trace-invalid", "run_id": "invalid-run", "workload_class": "invalid fixture"}
    return [
        event(base, 5, "object_access", object_id="missing-object", object_class="KV cache", size_units=1, correctness_sensitive="false", source_version="fixture"),
        event(base, 6, "object_evict", object_id="late-birth", object_class="KV cache", size_units=1, correctness_sensitive="false", source_version="fixture"),
        event(base, 8, "object_create", object_id="late-birth", object_class="KV cache", size_units=1, correctness_sensitive="false", source_version="fixture"),
        event(base, 9, "object_access", object_id="late-birth", object_class="KV cache", size_units=1, correctness_sensitive="false", source_version="fixture"),
        event(base, 10, "branch_merge", branch_id="branch-without-fork", merge_state="merged", source_version="fixture"),
        event(base, 11, "verifier_result", verifier_id="verifier-without-start", merge_state="accepted", source_version="fixture"),
        event(base, 12, "workspace_write", object_id="workspace-no-horizon", object_class="durable workspace", size_units=5, provenance_id="prov:bad", correctness_sensitive="true", durability_horizon=0, source_version="fixture"),
        event(base, 13, "semantic_cache_lookup", object_id="semantic-no-prov", object_class="semantic cache entry", size_units=5, correctness_sensitive="true", source_version="fixture", invalidation_signal=""),
    ]


def main() -> None:
    DATA.mkdir(exist_ok=True)
    rng = Random(SEED)
    object_rows = read_csv(PROJECT / "memory_objects.csv")
    arch_rows = read_csv(DATA / "architecture_options.csv")
    taxonomy_classes = {r["object_class"] for r in object_rows}
    arch_by_workload = {}
    for row in arch_rows:
        for workload in row["target_workloads"].split("; "):
            arch_by_workload[workload] = row["architecture_option"]
    arch_by_workload.update({
        "RAG": "B_memory_object_aware_runtime",
        "code-agent loop": "C_trajectory_dag_memory_fabric",
        "verification-heavy": "C_trajectory_dag_memory_fabric",
        "multi-agent branch/merge": "C_trajectory_dag_memory_fabric",
    })

    events: list[dict[str, object]] = []
    for config in WORKLOADS:
        events.extend(generate_trace(config, rng))
    used_classes = {str(r["object_class"]) for r in events if r["object_class"]}
    missing = sorted(taxonomy_classes - used_classes)
    if missing:
        raise SystemExit(f"missing taxonomy object classes in generated traces: {missing}")

    lifetimes, reuse_rows, dag_rows, summary_rows = derive(events, arch_by_workload)
    schema_rows = [{"check_name": "generated_by", "status": "pass", "detail": "generate_agentic_trace_v2.py", "evidence_label": "synthetic"}]
    schema_rows.append({"check_name": "event_count", "status": "pass" if len(events) >= 500 else "fail", "detail": str(len(events)), "evidence_label": "synthetic"})
    schema_rows.append({"check_name": "workload_count", "status": "pass" if len(summary_rows) >= 6 else "fail", "detail": str(len(summary_rows)), "evidence_label": "synthetic"})
    schema_rows.append({"check_name": "object_class_count", "status": "pass" if len(used_classes) >= 11 else "fail", "detail": str(len(used_classes)), "evidence_label": "synthetic"})

    write_csv(DATA / "agentic_trace_events_v2.csv", events, FIELDS)
    write_csv(DATA / "trace_object_lifetimes.csv", lifetimes)
    write_csv(DATA / "trace_reuse_intervals.csv", reuse_rows)
    write_csv(DATA / "trace_branch_dag_metrics.csv", dag_rows)
    write_csv(DATA / "trace_workload_summary.csv", summary_rows)
    write_csv(DATA / "trace_schema_validation.csv", schema_rows)
    write_csv(DATA / "trace_invalid_cases.csv", invalid_cases(), FIELDS)
    print(f"seed={SEED}")
    print(f"events={len(events)}")
    print(f"lifetimes={len(lifetimes)}")
    print(f"reuse_intervals={len(reuse_rows)}")
    print(f"dag_rows={len(dag_rows)}")
    print(f"summary_rows={len(summary_rows)}")


if __name__ == "__main__":
    main()
