# created: 2026-05-11T12:35:00Z
# cycle: 1
# run_id: run-2026-05-11T121649Z
# agent: worker
# milestone: M-LIFE-1

import csv
import os
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
GRID_PATH = ROOT / "data" / "lifetime_regime_grid.csv"


def read_grid(path):
    with open(path, newline="") as handle:
        rows = list(csv.DictReader(handle))
    for row in rows:
        row["fanout"] = int(float(row["fanout"]))
        row["branch_survival"] = float(row["branch_survival"])
        row["reuse_rate_lambda"] = float(row["reuse_rate_lambda"])
        row["durability_horizon"] = float(row["durability_horizon"])
        for key in ("kv_live_bytes", "branch_live_bytes", "durable_live_bytes", "prefix_expected_bytes", "total_expected_retained_bytes"):
            row[key] = float(row[key])
    return rows


def dominant_code(name):
    return {
        "KV": 0,
        "branch_state": 1,
        "durable_workspace": 2,
        "prefix_cache": 3,
    }[name]


def main():
    rows = read_grid(GRID_PATH)
    reuse_values = sorted({row["reuse_rate_lambda"] for row in rows})
    horizon_values = sorted({row["durability_horizon"] for row in rows})

    fig, axes = plt.subplots(
        len(horizon_values),
        len(reuse_values),
        figsize=(10.5, 8.5),
        sharex=True,
        sharey=True,
        constrained_layout=True,
    )

    fanouts = sorted({row["fanout"] for row in rows})
    survivals = sorted({row["branch_survival"] for row in rows})
    by_panel = defaultdict(dict)
    for row in rows:
        key = (row["durability_horizon"], row["reuse_rate_lambda"])
        by_panel[key][(row["branch_survival"], row["fanout"])] = dominant_code(row["dominant_state"])

    cmap = plt.matplotlib.colors.ListedColormap(["#4c78a8", "#f58518", "#54a24b", "#b279a2"])

    for r, horizon in enumerate(horizon_values):
        for c, reuse in enumerate(reuse_values):
            ax = axes[r][c] if len(horizon_values) > 1 else axes[c]
            matrix = [
                [by_panel[(horizon, reuse)][(survival, fanout)] for fanout in fanouts]
                for survival in survivals
            ]
            ax.imshow(matrix, cmap=cmap, vmin=0, vmax=3, origin="lower", aspect="auto")
            ax.set_title(f"H={horizon:g}, lambda={reuse:g}", fontsize=10)
            ax.set_xticks(range(len(fanouts)), [str(v) for v in fanouts])
            ax.set_yticks(range(len(survivals)), [str(v) for v in survivals])
            if r == len(horizon_values) - 1:
                ax.set_xlabel("branch fanout")
            if c == 0:
                ax.set_ylabel("branch survival")
            ax.grid(color="white", linewidth=0.8)

    labels = ["KV", "branch state", "durable workspace", "prefix cache"]
    handles = [plt.Rectangle((0, 0), 1, 1, color=cmap(i)) for i in range(4)]
    fig.legend(handles, labels, loc="outside lower center", ncol=4, frameon=False)
    fig.suptitle("Dominant retained state across lifetime regimes", fontsize=14)

    out = os.environ.get("FIGURE_OUT", str(ROOT / "data" / "lifetime_regime_plot.png"))
    fig.savefig(out, dpi=180)


if __name__ == "__main__":
    main()
