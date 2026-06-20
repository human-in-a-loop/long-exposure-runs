# created: 2026-05-11T12:22:00Z
# cycle: 1
# run_id: run-2026-05-11T121649Z
# agent: worker
# milestone: M-TAX-1

import csv
from pathlib import Path
import os

import matplotlib.pyplot as plt


LEVELS = {"none": 0, "minor": 1, "major": 2, "dominant": 3}


def main() -> None:
    here = Path(__file__).resolve().parent
    csv_path = here / "taxonomy_coverage.csv"
    out_path = Path(os.environ.get("FIGURE_OUT", here / "taxonomy_coverage.png"))

    with csv_path.open(newline="") as f:
        rows = list(csv.DictReader(f))

    columns = [name for name in rows[0].keys() if name != "workload_class"]
    workloads = [row["workload_class"] for row in rows]
    values = [[LEVELS[row[col]] for col in columns] for row in rows]

    fig_width = max(11, 0.72 * len(columns))
    fig_height = max(5.5, 0.48 * len(workloads))
    fig, ax = plt.subplots(figsize=(fig_width, fig_height))
    im = ax.imshow(values, cmap="YlGnBu", vmin=0, vmax=3, aspect="auto")

    ax.set_xticks(range(len(columns)))
    ax.set_xticklabels(columns, rotation=40, ha="right")
    ax.set_yticks(range(len(workloads)))
    ax.set_yticklabels(workloads)
    ax.set_title("Memory-object coverage by workload class")

    for row in range(len(workloads)):
        for col in range(len(columns)):
            value = values[row][col]
            label = next(k for k, v in LEVELS.items() if v == value)
            ax.text(col, row, label, ha="center", va="center", fontsize=7, color="black")

    cbar = fig.colorbar(im, ax=ax, ticks=[0, 1, 2, 3])
    cbar.ax.set_yticklabels(["none", "minor", "major", "dominant"])
    cbar.set_label("Relative importance")
    ax.set_xlabel("Memory object class")
    ax.set_ylabel("Workload class")
    fig.tight_layout()
    fig.savefig(out_path, dpi=180)


if __name__ == "__main__":
    main()
