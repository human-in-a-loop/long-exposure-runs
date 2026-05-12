#!/usr/bin/env python3
# created: 2026-05-12T03:36:00Z
# cycle: 24
# run_id: run-2026-05-11T121649Z
# agent: worker
# milestone: M-TRENDS-1

from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def save(path: Path) -> None:
    plt.tight_layout()
    plt.savefig(path, dpi=160)
    plt.close()
    print(path.relative_to(ROOT))


def plot_phase() -> None:
    rows = read_csv(DATA / "future_trend_architecture_phase_diagram.csv")
    reuse_values = sorted({float(r["reuse_probability"]) for r in rows})
    branch_values = sorted({float(r["branch_fanout"]) for r in rows})
    code = {"A": 0, "B": 1, "C": 2}
    matrix = []
    for branch in branch_values:
        matrix.append([code[next(r["option_preferred"] for r in rows if float(r["reuse_probability"]) == reuse and float(r["branch_fanout"]) == branch)] for reuse in reuse_values])
    fig, ax = plt.subplots(figsize=(8.5, 4.8))
    im = ax.imshow(matrix, cmap=plt.colormaps["Set2"].resampled(3), vmin=0, vmax=2, aspect="auto")
    ax.set_xticks(range(len(reuse_values)), [str(v) for v in reuse_values])
    ax.set_yticks(range(len(branch_values)), [str(int(v)) for v in branch_values])
    ax.set_xlabel("prefix/KV/tool-output reuse probability")
    ax.set_ylabel("branch fanout")
    ax.set_title("Option A/B/C preferred regions under synthetic future trends")
    for y, branch in enumerate(branch_values):
        for x, reuse in enumerate(reuse_values):
            opt = next(r["option_preferred"] for r in rows if float(r["reuse_probability"]) == reuse and float(r["branch_fanout"]) == branch)
            ax.text(x, y, opt, ha="center", va="center", fontsize=11)
    cbar = fig.colorbar(im, ax=ax, ticks=[0, 1, 2])
    cbar.ax.set_yticklabels(["A", "B", "C"])
    save(DATA / "future_trend_phase_diagram.png")


def plot_thresholds() -> None:
    rows = read_csv(DATA / "future_trend_falsification_thresholds.csv")
    labels = [r["threshold_id"].replace("_", "\n") for r in rows]
    values = [float(r["memory_centric_advantage"]) for r in rows]
    colors = ["#4C78A8" if r["option_at_threshold"] == "A" else "#F58518" if r["option_at_threshold"] == "B" else "#54A24B" for r in rows]
    fig, ax = plt.subplots(figsize=(10, 5.2))
    bars = ax.bar(range(len(rows)), values, color=colors)
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_xticks(range(len(rows)), labels, rotation=25, ha="right")
    ax.set_ylabel("synthetic memory-centric advantage")
    ax.set_title("Falsification thresholds where mechanisms collapse or become compelling")
    for bar, row in zip(bars, rows):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), f"{row['option_at_threshold']} @ {row['threshold_value']}", ha="center", va="bottom", fontsize=8, rotation=90)
    save(DATA / "future_trend_falsification_thresholds.png")


def plot_priorities() -> None:
    rows = sorted(read_csv(DATA / "future_trend_measurement_priorities.csv"), key=lambda r: int(r["rank"]))
    labels = [r["measurement"] for r in rows]
    scores = [float(r["priority_score"]) for r in rows]
    fig, ax = plt.subplots(figsize=(10, 5.6))
    y = list(range(len(rows)))
    ax.barh(y, scores, color="#72B7B2")
    ax.set_yticks(y, labels)
    ax.invert_yaxis()
    ax.set_xlabel("expected ability to change architecture conclusions")
    ax.set_title("Future production measurements ranked by decision impact")
    for yi, score in zip(y, scores):
        ax.text(score + 1, yi, f"{score:.0f}", va="center")
    ax.set_xlim(0, 105)
    save(DATA / "future_trend_measurement_priorities.png")


def main() -> None:
    plot_phase()
    plot_thresholds()
    plot_priorities()


if __name__ == "__main__":
    main()
