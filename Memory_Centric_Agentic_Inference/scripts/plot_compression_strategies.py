# created: 2026-05-11T15:38:00Z
# cycle: 9
# run_id: run-2026-05-11T121649Z
# agent: worker
# milestone: M-COMP-1

"""Plot synthetic compression/offload strategy outputs."""

from __future__ import annotations

import csv
import os
from pathlib import Path

import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

STRATEGY_COLORS = {
    "keep_hot": "#4c78a8",
    "lossless_compress": "#54a24b",
    "lossy_summarize": "#e45756",
    "summary_plus_pointer": "#f58518",
    "offload_full": "#72b7b2",
    "recompute_on_demand": "#b279a2",
}
STRATEGY_ORDER = list(STRATEGY_COLORS)
WORKLOAD_ORDER = [
    "single-turn chat control",
    "batch summarization/offline inference control",
    "RAG",
    "code-agent loop",
    "verification-heavy",
    "multi-agent branch/merge",
]
OBJECT_ORDER = [
    "weights",
    "KV cache",
    "prefix cache",
    "retrieved context",
    "semantic cache entry",
    "tool output",
    "intermediate scratch",
    "branch state",
    "verifier state",
    "trajectory log",
    "durable workspace",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def fnum(value: str, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def short_workload(name: str) -> str:
    return {
        "single-turn chat control": "single-turn\ncontrol",
        "batch summarization/offline inference control": "batch/offline\ncontrol",
        "RAG": "RAG",
        "code-agent loop": "code-agent\nloop",
        "verification-heavy": "verification\nheavy",
        "multi-agent branch/merge": "branch/merge",
    }.get(name, name.replace(" ", "\n"))


def short_object(name: str) -> str:
    return {
        "semantic cache entry": "semantic\ncache",
        "intermediate scratch": "scratch",
        "retrieved context": "retrieved\ncontext",
        "durable workspace": "durable\nworkspace",
        "trajectory log": "trajectory\nlog",
        "verifier state": "verifier\nstate",
        "branch state": "branch\nstate",
        "tool output": "tool\noutput",
        "prefix cache": "prefix\ncache",
        "KV cache": "KV\ncache",
    }.get(name, name)


def plot_strategy_matrix(out_path: Path) -> None:
    rows = read_csv(DATA / "compression_best_strategy_by_object.csv")
    best = {(row["workload_class"], row["object_class"]): row["best_strategy"] for row in rows}
    fig, ax = plt.subplots(figsize=(12.2, 5.8))
    matrix = []
    for workload in WORKLOAD_ORDER:
        matrix.append([STRATEGY_ORDER.index(best.get((workload, obj), "keep_hot")) for obj in OBJECT_ORDER])
    cmap = plt.matplotlib.colors.ListedColormap([STRATEGY_COLORS[name] for name in STRATEGY_ORDER])
    ax.imshow(matrix, cmap=cmap, vmin=0, vmax=len(STRATEGY_ORDER) - 1, aspect="auto")
    ax.set_xticks(range(len(OBJECT_ORDER)))
    ax.set_xticklabels([short_object(obj) for obj in OBJECT_ORDER], rotation=35, ha="right")
    ax.set_yticks(range(len(WORKLOAD_ORDER)))
    ax.set_yticklabels([short_workload(w) for w in WORKLOAD_ORDER])
    for y, workload in enumerate(WORKLOAD_ORDER):
        for x, obj in enumerate(OBJECT_ORDER):
            label = best.get((workload, obj), "")
            if label:
                ax.text(x, y, label.split("_")[0][:4], ha="center", va="center", fontsize=7, color="black")
            else:
                ax.text(x, y, "n/a", ha="center", va="center", fontsize=7, color="#555555")
    handles = [plt.Rectangle((0, 0), 1, 1, color=color, label=name) for name, color in STRATEGY_COLORS.items()]
    ax.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.5, 1.25), ncol=3, fontsize=8)
    ax.set_title("Best compression/offload/recompute strategy by workload and object class")
    fig.tight_layout()
    fig.savefig(out_path, dpi=180)
    plt.close(fig)
    print(f"wrote {out_path}")


def plot_safety_vs_savings(out_path: Path) -> None:
    rows = read_csv(DATA / "compression_strategy_scores.csv")
    fig, ax = plt.subplots(figsize=(9.5, 6.2))
    for strategy in STRATEGY_ORDER:
        items = [row for row in rows if row["strategy"] == strategy]
        x = [fnum(row["bytes_saved_proxy"]) for row in items]
        y = [fnum(row["correctness_loss_risk_proxy"]) + fnum(row["provenance_risk_proxy"]) for row in items]
        colors = ["#888888" if row["valid"] == "false" else STRATEGY_COLORS[strategy] for row in items]
        ax.scatter(x, y, s=28, alpha=0.72, color=colors, label=strategy)
    ax.set_xlabel("byte-saving proxy")
    ax.set_ylabel("correctness + provenance risk proxy")
    ax.set_title("Byte-saving proxy versus correctness/provenance risk by strategy")
    ax.grid(alpha=0.25)
    ax.legend(ncol=2, fontsize=8)
    fig.tight_layout()
    fig.savefig(out_path, dpi=180)
    plt.close(fig)
    print(f"wrote {out_path}")


def plot_queue_relief(out_path: Path) -> None:
    rows = read_csv(DATA / "compression_object_queue_interactions.csv")
    rows = [
        row
        for row in rows
        if row["object_threshold_relevant"] == "true"
        or row["dag_threshold_relevant"] == "true"
        or row["interaction"] == "can_worsen_or_cause_reversal"
    ]
    rows = sorted(rows, key=lambda row: fnum(row["net_queue_effect_proxy"]))
    if len(rows) > 24:
        rows = rows[:12] + rows[-12:]
    labels = [
        f"{short_workload(row['workload_class']).replace(chr(10), ' ')}\n"
        f"{short_object(row['object_class']).replace(chr(10), ' ')}\n"
        f"{row['strategy'].replace('_', ' ')}"
        for row in rows
    ]
    relief = [fnum(row["queue_relief_proxy"]) for row in rows]
    overhead = [fnum(row["added_reconstruction_metadata_proxy"]) for row in rows]
    x = list(range(len(rows)))
    width = 0.42
    fig, ax = plt.subplots(figsize=(14.5, 7.1))
    ax.bar([i - width / 2 for i in x], relief, width, color="#54a24b", label="queue relief proxy")
    ax.bar([i + width / 2 for i in x], overhead, width, color="#e45756", label="added reconstruction + metadata")
    for i, row in enumerate(rows):
        marker = "+"
        if row["selected_positive_for_queue_help"] != "true":
            marker = "!" if row["interaction"] == "can_worsen_or_cause_reversal" else "."
        ax.text(i, max(relief[i], overhead[i]) + 0.08, marker, ha="center", fontsize=11)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=65, ha="right", fontsize=7)
    ax.set_ylabel("synthetic proxy units")
    ax.set_title("Object-selective queue relief versus reconstruction/metadata overhead")
    ax.legend()
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(out_path, dpi=180)
    plt.close(fig)
    print(f"wrote {out_path}")


def main() -> None:
    out = Path(os.environ.get("FIGURE_OUT", DATA / "compression_strategy_matrix.png"))
    plot_strategy_matrix(out)
    plot_safety_vs_savings(DATA / "compression_safety_vs_savings.png")
    plot_queue_relief(DATA / "compression_queue_relief.png")


if __name__ == "__main__":
    main()
