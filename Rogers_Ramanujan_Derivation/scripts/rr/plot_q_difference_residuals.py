# created: 2026-05-14T23:55:00Z
# cycle: 2
# run_id: run-2026-05-14T232311Z
# agent: worker
# milestone: M2

"""Plot exact q-difference residual and backsolve comparison magnitudes."""

from pathlib import Path
import csv
import os

import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data" / "finite_experiments"
OUT = Path(os.environ.get("FIGURE_OUT", DATA_DIR / "q_difference_residuals.png"))


def main() -> None:
    with (DATA_DIR / "q_difference_residuals.csv").open(newline="") as f:
        residual_rows = list(csv.DictReader(f))
    with (DATA_DIR / "q_difference_backsolve.csv").open(newline="") as f:
        backsolve_rows = list(csv.DictReader(f))

    r_values = sorted({int(row["r"]) for row in residual_rows})
    k_values = sorted({int(row["k"]) for row in residual_rows})
    r_index = {r: i for i, r in enumerate(r_values)}
    k_index = {k: i for i, k in enumerate(k_values)}
    ladder = [[0 for _ in k_values] for _ in r_values]
    for row in residual_rows:
        r = int(row["r"])
        k = int(row["k"])
        residual = abs(int(row["residual"]))
        ladder[r_index[r]][k_index[k]] = max(ladder[r_index[r]][k_index[k]], residual)

    fig, axes = plt.subplots(2, 1, figsize=(10, 7), constrained_layout=True)

    im = axes[0].imshow(ladder, aspect="auto", interpolation="nearest", cmap="viridis")
    axes[0].set_title("Series ladder exact residuals")
    axes[0].set_xlabel("coefficient degree k")
    axes[0].set_ylabel("ladder index r")
    xticks = list(range(0, len(k_values), max(1, len(k_values) // 8)))
    axes[0].set_xticks(xticks)
    axes[0].set_xticklabels([str(k_values[i]) for i in xticks])
    axes[0].set_yticks(range(len(r_values)))
    axes[0].set_yticklabels(r_values)
    fig.colorbar(im, ax=axes[0], label="|residual coefficient|")

    keep = {
        "backsolve_minus_series",
        "backsolve_C0_minus_P14",
        "backsolve_C1_minus_P23",
        "forward_from_products_minus_backsolve",
    }
    selected = [row for row in backsolve_rows if row["comparison"] in keep]
    labels = [f"{row['comparison']} r={row['r']}" for row in selected]
    values = [int(row["max_abs_coeff"]) for row in selected]
    axes[1].bar(range(len(selected)), values)
    axes[1].set_title("Backsolve/product comparison max coefficient magnitudes")
    axes[1].set_ylabel("max |coefficient difference|")
    axes[1].set_xticks(range(len(selected)))
    axes[1].set_xticklabels(labels, rotation=75, ha="right", fontsize=7)

    fig.suptitle("q-difference ladder residuals and product diagnostics")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, dpi=160)


if __name__ == "__main__":
    main()
