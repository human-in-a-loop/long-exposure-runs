# created: 2026-05-11T13:02:00Z
# cycle: 3
# run_id: run-2026-05-11T121649Z
# agent: worker
# milestone: M-COST-1

from pathlib import Path
import csv
import os

import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "cost_model_sensitivity.csv"
OUT = Path(os.environ.get("FIGURE_OUT", ROOT / "data" / "cost_model_sensitivity.png"))


def to_float(value: str) -> float:
    return float(value.replace("*^", "e"))


def main() -> None:
    rows = []
    with DATA.open(newline="") as f:
        for row in csv.DictReader(f):
            rows.append(
                {
                    "reuse": float(row["reuse_probability"]),
                    "transfer": float(row["transfer_cost_ratio"]),
                    "benefit": to_float(row["net_memory_centric_benefit"]),
                    "driver": row["dominant_benefit_driver"],
                }
            )

    reuse_values = sorted({r["reuse"] for r in rows}, reverse=True)
    transfer_values = sorted({r["transfer"] for r in rows})
    means = []
    winners = {}
    for reuse in reuse_values:
        row_values = []
        for transfer in transfer_values:
            cell = [r for r in rows if r["reuse"] == reuse and r["transfer"] == transfer]
            row_values.append(sum(r["benefit"] for r in cell) / len(cell))
            counts = {}
            for r in cell:
                counts[r["driver"]] = counts.get(r["driver"], 0) + 1
            winners[(reuse, transfer)] = max(counts.items(), key=lambda item: item[1])[0]
        means.append(row_values)

    fig, ax = plt.subplots(figsize=(8, 5.2), constrained_layout=True)
    image = ax.imshow(means, cmap="viridis", aspect="auto")

    ax.set_xticks(range(len(transfer_values)))
    ax.set_xticklabels([str(c) for c in transfer_values])
    ax.set_yticks(range(len(reuse_values)))
    ax.set_yticklabels([str(r) for r in reuse_values])
    ax.set_xlabel("Synthetic transfer cost ratio")
    ax.set_ylabel("Reuse probability")
    ax.set_title("Memory-centric placement benefit regimes")

    for y, reuse in enumerate(reuse_values):
        for x, transfer in enumerate(transfer_values):
            value = means[y][x]
            driver = winners[(reuse, transfer)]
            label = driver.replace("_", "\n")
            ax.text(x, y, f"{value:.1f}\n{label}", ha="center", va="center", color="white", fontsize=8)

    cbar = fig.colorbar(image, ax=ax)
    cbar.set_label("Mean synthetic net benefit")
    fig.savefig(OUT, dpi=180)


if __name__ == "__main__":
    main()
