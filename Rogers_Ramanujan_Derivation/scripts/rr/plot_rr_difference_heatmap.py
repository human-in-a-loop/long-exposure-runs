# created: 2026-05-14T23:31:00Z
# cycle: 1
# run_id: run-2026-05-14T232311Z
# agent: worker
# milestone: M1

import csv
import os
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


workspace = Path(__file__).resolve().parents[2]
infile = workspace / "data/finite_experiments/rr_differences.csv"
out = Path(os.environ.get("FIGURE_OUT", "data/finite_experiments/rr_difference_heatmap.png"))
outfile = out if out.is_absolute() else workspace / out

rows = []
with open(infile, newline="") as f:
    for row in csv.DictReader(f):
        rows.append((row["comparison"], int(row["k"]), int(row["difference"])))

comparisons = []
for comparison, _, _ in rows:
    if comparison not in comparisons:
        comparisons.append(comparison)

kmax = max(k for _, k, _ in rows)
matrix = np.zeros((len(comparisons), kmax + 1), dtype=float)
for comparison, k, difference in rows:
    matrix[comparisons.index(comparison), k] = difference

signed_log = np.sign(matrix) * np.log10(np.abs(matrix) + 1)
limit = max(1.0, float(np.max(np.abs(signed_log))))

fig_height = 1.1 + 0.48 * len(comparisons)
fig, ax = plt.subplots(figsize=(11, fig_height))
im = ax.imshow(signed_log, aspect="auto", cmap="coolwarm", vmin=-limit, vmax=limit, interpolation="nearest")
ax.set_xlabel("coefficient degree k")
ax.set_ylabel("comparison")
ax.set_yticks(np.arange(len(comparisons)))
ax.set_yticklabels(comparisons)
ax.set_title("Rogers-Ramanujan finite coefficient differences")
ax.set_xticks(np.arange(0, kmax + 1, 5))
cbar = fig.colorbar(im, ax=ax, pad=0.015)
cbar.set_label("sign(diff) log10(|diff|+1)")
fig.tight_layout()
fig.savefig(outfile, dpi=180)
