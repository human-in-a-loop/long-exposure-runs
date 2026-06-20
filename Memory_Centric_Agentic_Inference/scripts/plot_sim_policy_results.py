#!/usr/bin/env python3
# created: 2026-05-11T13:21:44Z
# cycle: 4
# run_id: run-2026-05-11T121649Z
# agent: worker
# milestone: M-SIM-1

import csv
import os
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

POLICY_LABELS = {
    "hbm_first_baseline": "HBM first",
    "reuse_aware_tiering": "Reuse aware",
    "branch_verifier_durable_aware": "Branch/verifier/durable",
    "cost_proxy_balanced": "Balanced proxy",
}

OBJECT_COLORS = {
    "weights": "#4c78a8",
    "KV cache": "#f58518",
    "prefix cache": "#54a24b",
    "retrieved context": "#b279a2",
    "semantic cache entry": "#72b7b2",
    "tool output": "#e45756",
    "branch state": "#ff9da6",
    "verifier state": "#9d755d",
    "trajectory log": "#bab0ac",
    "durable workspace": "#59a14f",
    "intermediate scratch": "#edc948",
}


def read_csv(path):
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def short_workload(name):
    return (
        name.replace("single-turn chat control", "single-turn")
        .replace("batch summarization/offline inference control", "batch/offline")
        .replace("RAG with retrieved-context reuse", "RAG")
        .replace("code-agent loop with tool outputs and durable workspace", "code-agent")
        .replace("verification-heavy agent", "verification")
        .replace("multi-agent branch/merge run", "branch/merge")
    )


def plot_policy_results(rows, out_path):
    workloads = []
    policies = []
    scores = defaultdict(dict)
    winners = {}
    for row in rows:
        workload = row["workload_class"]
        policy = row["policy"]
        if workload not in workloads:
            workloads.append(workload)
        if policy not in policies:
            policies.append(policy)
        scores[workload][policy] = float(row["total_score"])
        winners[workload] = row["winning_policy_for_workload"]

    fig, ax = plt.subplots(figsize=(12, 6.5))
    width = 0.18
    x = list(range(len(workloads)))
    offsets = [(-1.5 + i) * width for i in range(len(policies))]
    colors = ["#4c78a8", "#f58518", "#54a24b", "#e45756"]
    for offset, policy, color in zip(offsets, policies, colors):
        vals = [scores[w][policy] for w in workloads]
        bars = ax.bar([v + offset for v in x], vals, width=width, label=POLICY_LABELS.get(policy, policy), color=color)
        for bar, workload in zip(bars, workloads):
            if policy == winners[workload]:
                ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), "*", ha="center", va="bottom", fontsize=12)

    ax.axhline(0, color="#333333", linewidth=0.8)
    ax.set_ylabel("Total synthetic score, higher is better")
    ax.set_title("Policy scores by workload; asterisks mark per-workload winners")
    ax.set_xticks(x)
    ax.set_xticklabels([short_workload(w) for w in workloads], rotation=20, ha="right")
    ax.legend(ncol=2, frameon=False)
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(out_path, dpi=160)
    plt.close(fig)


def plot_object_breakdown(rows, results, out_path):
    winners = {}
    for row in results:
        winners[row["workload_class"]] = row["winning_policy_for_workload"]

    workloads = list(dict.fromkeys(row["workload_class"] for row in results))
    object_classes = sorted({row["object_class"] for row in rows})
    data = defaultdict(lambda: defaultdict(float))
    for row in rows:
        if row["policy"] == winners[row["workload_class"]]:
            data[row["workload_class"]][row["object_class"]] += float(row["total_score_contribution"])

    fig, ax = plt.subplots(figsize=(12, 6.5))
    x = list(range(len(workloads)))
    positives = [0.0] * len(workloads)
    negatives = [0.0] * len(workloads)
    for obj in object_classes:
        vals = [data[w].get(obj, 0.0) for w in workloads]
        pos_vals = [max(0.0, v) for v in vals]
        neg_vals = [min(0.0, v) for v in vals]
        if any(v != 0 for v in pos_vals):
            ax.bar(x, pos_vals, bottom=positives, label=obj, color=OBJECT_COLORS.get(obj))
            positives = [a + b for a, b in zip(positives, pos_vals)]
        if any(v != 0 for v in neg_vals):
            ax.bar(x, neg_vals, bottom=negatives, color=OBJECT_COLORS.get(obj))
            negatives = [a + b for a, b in zip(negatives, neg_vals)]

    ax.axhline(0, color="#333333", linewidth=0.8)
    ax.set_ylabel("Winner score contribution by object class")
    ax.set_title("Object classes driving the winning policy in each workload")
    ax.set_xticks(x)
    ax.set_xticklabels([short_workload(w) for w in workloads], rotation=20, ha="right")
    ax.grid(axis="y", alpha=0.25)
    handles, labels = ax.get_legend_handles_labels()
    dedup = dict(zip(labels, handles))
    ax.legend(dedup.values(), dedup.keys(), ncol=3, frameon=False, fontsize=8)
    fig.tight_layout()
    fig.savefig(out_path, dpi=160)
    plt.close(fig)


def main():
    results = read_csv(DATA / "sim_policy_results.csv")
    breakdown = read_csv(DATA / "sim_policy_object_breakdown.csv")
    out = Path(os.environ.get("FIGURE_OUT", DATA / "sim_policy_results.png"))
    plot_policy_results(results, out)
    second = DATA / "sim_object_breakdown.png"
    plot_object_breakdown(breakdown, results, second)
    print(f"wrote {out.relative_to(ROOT) if out.is_relative_to(ROOT) else out}")
    print(f"wrote {second.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
