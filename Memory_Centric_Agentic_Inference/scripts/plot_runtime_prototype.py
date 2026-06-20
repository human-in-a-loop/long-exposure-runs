# created: 2026-05-11T16:43:00Z
# cycle: 11
# run_id: run-2026-05-11T121649Z
# agent: worker
# milestone: M-PROTO-1
"""Plot outputs for the M-PROTO-1 runtime prototype."""

from __future__ import annotations

import csv
import os
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = Path(os.environ.get("FIGURE_OUT", DATA / "runtime_architecture_boundary.png"))

OPTION_LABELS = {
    "A_conventional_request_model_kv_serving": "A",
    "B_memory_object_aware_runtime": "B",
    "C_trajectory_dag_memory_fabric": "C",
}
OPTION_SCORE = {
    "A_conventional_request_model_kv_serving": 0,
    "B_memory_object_aware_runtime": 1,
    "C_trajectory_dag_memory_fabric": 2,
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def savefig(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(path, dpi=160)
    plt.close()
    print(f"wrote {path}")


def plot_boundary(path: Path) -> None:
    rows = read_csv(DATA / "runtime_workload_summary.csv")
    workloads = [r["workload_class"] for r in rows]
    y_runtime = [OPTION_SCORE[r["runtime_architecture_option"]] for r in rows]
    y_expected = [OPTION_SCORE[r["expected_architecture_option"]] for r in rows]
    x = range(len(workloads))
    plt.figure(figsize=(11, 4.8))
    plt.scatter(x, y_expected, marker="s", s=95, label="validated expected", color="#4c78a8")
    plt.scatter(x, y_runtime, marker="o", s=50, label="runtime prototype", color="#f58518")
    for i, (a, b) in enumerate(zip(y_expected, y_runtime)):
        plt.plot([i, i], [a, b], color="#999999", linewidth=1)
    plt.xticks(list(x), workloads, rotation=25, ha="right")
    plt.yticks([0, 1, 2], ["Option A", "Option B", "Option C"])
    plt.ylim(-0.35, 2.35)
    plt.ylabel("architecture option")
    plt.title("Runtime architecture boundary reproduction")
    plt.legend(loc="upper left")
    plt.grid(axis="y", alpha=0.25)
    savefig(path)


def plot_residency(path: Path) -> None:
    rows = read_csv(DATA / "runtime_registry_snapshots.csv")
    latest: dict[str, dict[str, str]] = {}
    for row in rows:
        latest[row["object_id"]] = row
    by_tier: dict[str, float] = defaultdict(float)
    classes_by_tier: dict[str, set[str]] = defaultdict(set)
    for row in latest.values():
        tier = row["tier"] or "unknown"
        by_tier[tier] += float(row["size_units"] or 0)
        classes_by_tier[tier].add(row["object_class"])
    tiers = sorted(by_tier, key=by_tier.get, reverse=True)
    values = [by_tier[t] for t in tiers]
    colors = ["#4c78a8", "#f58518", "#54a24b", "#b279a2", "#e45756", "#72b7b2"]
    plt.figure(figsize=(10, 5.2))
    bars = plt.bar(tiers, values, color=colors[: len(tiers)])
    for bar, tier in zip(bars, tiers):
        label = f"{len(classes_by_tier[tier])} classes"
        plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), label, ha="center", va="bottom", fontsize=9)
    plt.xticks(rotation=20, ha="right")
    plt.ylabel("synthetic retained size units")
    plt.title("Runtime object residency after trace replay")
    plt.grid(axis="y", alpha=0.25)
    savefig(path)


def plot_ablations(path: Path) -> None:
    rows = read_csv(DATA / "runtime_ablation_results.csv")
    workloads = sorted({r["workload_class"] for r in rows})
    ablations = [
        "baseline",
        "hide_provenance_reuse",
        "hide_branch_verifier_durable",
        "hide_all_memory_causal_fields",
    ]
    width = 0.18
    plt.figure(figsize=(12, 5.2))
    for j, ablation in enumerate(ablations):
        ys = [
            OPTION_SCORE[next(r["runtime_architecture_option"] for r in rows if r["workload_class"] == w and r["ablation"] == ablation)]
            for w in workloads
        ]
        xs = [i + (j - 1.5) * width for i in range(len(workloads))]
        plt.bar(xs, ys, width=width, label=ablation.replace("_", " "))
    plt.xticks(range(len(workloads)), workloads, rotation=25, ha="right")
    plt.yticks([0, 1, 2], ["Option A", "Option B", "Option C"])
    plt.ylabel("selected option")
    plt.title("Architecture option changes under hidden causal fields")
    plt.legend(loc="upper left", ncol=2, fontsize=8)
    plt.grid(axis="y", alpha=0.25)
    savefig(path)


def main() -> None:
    if OUT.name == "runtime_architecture_boundary.png":
        plot_boundary(DATA / "runtime_architecture_boundary.png")
        plot_residency(DATA / "runtime_object_residency.png")
        plot_ablations(DATA / "runtime_ablation_effects.png")
    elif OUT.name == "runtime_object_residency.png":
        plot_residency(OUT)
    elif OUT.name == "runtime_ablation_effects.png":
        plot_ablations(OUT)
    else:
        plot_boundary(OUT)


if __name__ == "__main__":
    main()
