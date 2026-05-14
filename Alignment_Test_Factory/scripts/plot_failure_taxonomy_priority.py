# created: 2026-05-13T21:15:00Z
# cycle: 1
# run_id: run-2026-05-13T204826Z
# agent: worker
# milestone: M-2

"""Render priority and deterministic-scoreability for M-2 failure labels."""

from __future__ import annotations

import csv
import os
from pathlib import Path

import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "data" / "failure_taxonomy_operational_matrix.csv"
OUT_PATH = Path(os.environ.get("FIGURE_OUT", ROOT / "data" / "failure_taxonomy_priority.png"))

PRIORITY_SCORE = {
    "High": 3.0,
    "Medium-high": 2.5,
    "Medium": 2.0,
    "Low": 1.0,
}


def score_determinism(text: str) -> float:
    prefix = text.split(":", 1)[0].strip().lower()
    if prefix == "strong":
        return 3.0
    if prefix == "medium-strong":
        return 2.5
    if prefix == "medium":
        return 2.0
    if prefix == "weak":
        return 1.0
    return 0.5


def short_label(label: str) -> str:
    return label.replace("_", "\n")


def main() -> None:
    with CSV_PATH.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))

    labels = [short_label(row["label"]) for row in rows]
    priorities = [PRIORITY_SCORE[row["prototype_priority"]] for row in rows]
    deterministic = [score_determinism(row["deterministic_scorer"]) for row in rows]
    colors = ["#2b8cbe" if row["primitive_or_composite"] == "primitive" else "#f03b20" for row in rows]

    fig, ax = plt.subplots(figsize=(12, 6.5))
    x = range(len(rows))
    ax.bar(x, priorities, color=colors, alpha=0.82, label="Prototype priority")
    ax.plot(x, deterministic, color="#222222", marker="o", linewidth=2.0, label="Deterministic-scoreability")

    ax.set_ylim(0, 3.25)
    ax.set_yticks([1, 2, 2.5, 3])
    ax.set_yticklabels(["Low", "Medium", "Medium-high", "High"])
    ax.set_xticks(list(x))
    ax.set_xticklabels(labels, rotation=0, ha="center", fontsize=8)
    ax.set_ylabel("Ordinal score")
    ax.set_title("Failure taxonomy prototype priority")
    ax.grid(axis="y", color="#dddddd", linewidth=0.8)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    primitive_patch = plt.Rectangle((0, 0), 1, 1, color="#2b8cbe", alpha=0.82)
    composite_patch = plt.Rectangle((0, 0), 1, 1, color="#f03b20", alpha=0.82)
    ax.legend(
        [primitive_patch, composite_patch, ax.lines[0]],
        ["Primitive label", "Composite label", "Deterministic-scoreability"],
        loc="lower left",
        frameon=False,
    )

    fig.text(
        0.01,
        0.01,
        "Prototype priority and deterministic-scoreability of agentic alignment failure labels; "
        "higher-priority labels should drive the first task-schema examples.",
        fontsize=9,
    )
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT_PATH, dpi=180)


if __name__ == "__main__":
    main()
