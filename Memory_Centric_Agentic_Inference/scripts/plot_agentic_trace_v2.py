# created: 2026-05-11T14:36:00Z
# cycle: 7
# run_id: run-2026-05-11T121649Z
# agent: worker
# milestone: M-TRACE-1

"""Plot synthetic trace v2 summaries."""

from __future__ import annotations

import csv
import os
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def save(fig: plt.Figure, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)
    print(f"wrote {path}")


def plot_lifetimes(out: Path) -> None:
    rows = read_csv(DATA / "trace_object_lifetimes.csv")
    workloads = sorted({r["workload_class"] for r in rows})
    fig, ax = plt.subplots(figsize=(12, 6))
    data = []
    labels = []
    for workload in workloads:
        vals = [int(r["lifetime"]) for r in rows if r["workload_class"] == workload]
        data.append(vals)
        labels.append(workload.replace(" ", "\n"))
    ax.boxplot(data, tick_labels=labels, showfliers=False)
    ax.set_title("Synthetic trace v2 object lifetime distributions")
    ax.set_ylabel("Lifetime (time steps)")
    ax.tick_params(axis="x", labelsize=8)
    ax.grid(axis="y", alpha=0.25)
    save(fig, out)


def plot_live_bytes(out: Path) -> None:
    events = read_csv(DATA / "agentic_trace_events_v2.csv")
    creates = {}
    end_by_object = {}
    run_end = defaultdict(int)
    for row in events:
        t = int(row["time_step"])
        run_end[row["run_id"]] = max(run_end[row["run_id"]], t)
        oid = row["object_id"]
        if row["event_type"] == "object_create" and oid:
            creates[oid] = row
        if row["event_type"] == "object_evict" and oid:
            end_by_object[oid] = t
    workloads = sorted({r["workload_class"] for r in events})
    classes = ["KV cache", "retrieved context", "tool output", "branch state", "verifier state", "trajectory log", "durable workspace", "semantic cache entry", "other"]
    fig, axes = plt.subplots(3, 2, figsize=(13, 9), sharex=False)
    axes = axes.ravel()
    for ax, workload in zip(axes, workloads):
        run = next(r["run_id"] for r in events if r["workload_class"] == workload)
        max_t = run_end[run]
        series = {cls: [0] * (max_t + 1) for cls in classes}
        for oid, row in creates.items():
            if row["workload_class"] != workload:
                continue
            cls = row["object_class"] if row["object_class"] in classes else "other"
            birth = int(row["time_step"])
            end = end_by_object.get(oid, max_t)
            size = int(row["size_units"])
            for t in range(birth, min(end, max_t) + 1):
                series[cls][t] += size
        xs = list(range(max_t + 1))
        stack = [series[cls] for cls in classes if any(series[cls])]
        labels = [cls for cls in classes if any(series[cls])]
        ax.stackplot(xs, stack, labels=labels, alpha=0.85)
        ax.set_title(workload, fontsize=9)
        ax.set_ylabel("Live size units")
        ax.grid(axis="y", alpha=0.2)
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=4, fontsize=8)
    fig.suptitle("Synthetic trace v2 live bytes by object class", y=0.995)
    fig.subplots_adjust(bottom=0.16)
    save(fig, out)


def plot_dag_metrics(out: Path) -> None:
    rows = read_csv(DATA / "trace_branch_dag_metrics.csv")
    workloads = [r["workload_class"] for r in rows]
    width = [float(r["max_dag_width"]) for r in rows]
    delay = [float(r["mean_verifier_delay"]) for r in rows]
    merge = [float(r["merge_rate"]) for r in rows]
    discard = [float(r["discard_rate"]) for r in rows]
    x = range(len(workloads))
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.bar([i - 0.3 for i in x], width, width=0.2, label="max DAG width")
    ax.bar([i - 0.1 for i in x], delay, width=0.2, label="mean verifier delay")
    ax.bar([i + 0.1 for i in x], merge, width=0.2, label="merge rate")
    ax.bar([i + 0.3 for i in x], discard, width=0.2, label="discard rate")
    ax.set_xticks(list(x), [w.replace(" ", "\n") for w in workloads], fontsize=8)
    ax.set_ylabel("Synthetic metric value")
    ax.set_title("Synthetic trace v2 branch, verifier, merge, and discard metrics")
    ax.grid(axis="y", alpha=0.25)
    ax.legend(fontsize=8)
    save(fig, out)


def main() -> None:
    env_out = os.environ.get("FIGURE_OUT")
    plot_lifetimes(Path(env_out) if env_out else DATA / "trace_lifetime_distributions.png")
    plot_live_bytes(DATA / "trace_live_bytes_by_object.png")
    plot_dag_metrics(DATA / "trace_branch_dag_metrics.png")


if __name__ == "__main__":
    main()
