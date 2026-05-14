# created: 2026-05-13T20:52:25Z
# cycle: 1
# run_id: run-2026-05-13T204826Z
# agent: worker
# milestone: M-1
"""Render the M-1 landscape coverage matrix heatmap."""

from __future__ import annotations

import os
import csv
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap


ROOT = Path(__file__).resolve().parents[1]
MATRIX_PATH = ROOT / "data" / "landscape_gap_matrix.csv"
DEFAULT_OUT = ROOT / "data" / "landscape_gap_matrix.png"

COVERAGE_SCORE = {
    "unknown": 0,
    "not_targeted": 1,
    "weak": 2,
    "partial": 3,
    "strong": 4,
}


def main() -> None:
    out_path = Path(os.environ.get("FIGURE_OUT", DEFAULT_OUT))
    tools = ["Inspect", "garak", "HarmBench", "JailbreakBench"]
    with MATRIX_PATH.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    values = [[COVERAGE_SCORE[row[tool]] for tool in tools] for row in rows]

    fig_height = max(6, 0.45 * len(rows) + 1.8)
    fig, ax = plt.subplots(figsize=(9.5, fig_height))
    cmap = ListedColormap(["#f2f2f2", "#dedede", "#b8d8c8", "#62a87c", "#1f6f43"])
    image = ax.imshow(values, aspect="auto", vmin=0, vmax=4, cmap=cmap)

    ax.set_xticks(range(len(tools)), labels=tools)
    ax.set_yticks(range(len(rows)), labels=[row["capability"] for row in rows])
    ax.tick_params(axis="x", top=True, bottom=False, labeltop=True, labelbottom=False)
    ax.tick_params(axis="y", labelsize=9)
    ax.set_title("Agentic Alignment Test-Factory Coverage by Existing Tools", pad=22)

    for row_idx, row in enumerate(values):
        for col_idx, score in enumerate(row):
            label = [k for k, v in COVERAGE_SCORE.items() if v == score][0].replace("_", " ")
            ax.text(col_idx, row_idx, label, ha="center", va="center", fontsize=8, color="#111111")

    ax.set_xticks([x - 0.5 for x in range(1, len(tools))], minor=True)
    ax.set_yticks([y - 0.5 for y in range(1, len(rows))], minor=True)
    ax.grid(which="minor", color="white", linewidth=1.5)
    ax.tick_params(which="minor", bottom=False, left=False)

    cbar = fig.colorbar(image, ax=ax, fraction=0.028, pad=0.02)
    cbar.set_ticks(range(5), labels=["unknown", "not targeted", "weak", "partial", "strong"])
    cbar.ax.tick_params(labelsize=8)

    caption = (
        "Coverage of agentic alignment test-factory needs by existing open "
        "evaluation/red-team tools; darker cells indicate stronger direct support."
    )
    fig.text(0.02, 0.015, caption, ha="left", va="bottom", fontsize=9)
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=180)


if __name__ == "__main__":
    main()
