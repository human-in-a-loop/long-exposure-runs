# created: 2026-05-15T01:05:00Z
# cycle: fork-88b3b9161814-clone-1
# run_id: run-2026-05-14T232311Z
# agent: worker-clone-1
# milestone: M2
#
# Plot stable coefficients generated from the H_{alpha,N} recurrence.

import argparse
import csv
import os

import matplotlib.pyplot as plt


workspace = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
default_csv = os.path.join(workspace, "data", "finite_experiments", "mod5_state_tables.csv")
default_out = os.path.join(workspace, "data", "finite_experiments", "mod5_state_support.png")

parser = argparse.ArgumentParser(description="Plot modulo-5 support for stable H coefficients.")
parser.add_argument("--csv", default=default_csv)
parser.add_argument("--out", default=os.environ.get("FIGURE_OUT", default_out))
args = parser.parse_args()

with open(args.csv, newline="") as handle:
    rows = list(csv.DictReader(handle))

by_alpha = {}
for row in rows:
    alpha = int(row["alpha"])
    k = int(row["k"])
    n = int(row["N"])
    if n == k + 1 or (k == 0 and n == 1):
        by_alpha.setdefault(alpha, {})[k] = row

palette = {
    0: "#1b9e77",
    1: "#d95f02",
    2: "#7570b3",
    3: "#e7298a",
    4: "#66a61e",
}

fig, axes = plt.subplots(2, 1, figsize=(10, 6), sharex=True)

for axis, alpha in zip(axes, [0, 1]):
    rows_alpha = [by_alpha[alpha][k] for k in sorted(by_alpha[alpha])]
    xs = [int(row["k"]) for row in rows_alpha]
    ys = [int(row["stable_c_alpha_k"]) for row in rows_alpha]
    colors = [palette[int(row["k_mod_5"])] for row in rows_alpha]
    predicted = [int(row["k"]) for row in rows_alpha if row["predicted_j_values"]]

    axis.axhline(0, color="#333333", linewidth=0.8)
    axis.bar(xs, ys, color=colors, width=0.82)
    for k in predicted:
        axis.plot(k, 1.18, marker="v", color="#111111", markersize=4)
    axis.set_ylabel(f"alpha={alpha}\nstable coeff.")
    axis.set_ylim(-1.45, 1.45)
    axis.grid(axis="y", alpha=0.25)

axes[-1].set_xlabel("coefficient degree k")
fig.suptitle("Stable coefficients from H recurrence by residue class mod 5")
fig.text(
    0.5,
    0.01,
    "Bars show c_alpha(k); color is k mod 5; black markers indicate predicted bilateral exponents.",
    ha="center",
    fontsize=9,
)
fig.tight_layout(rect=(0, 0.035, 1, 0.95))
fig.savefig(args.out, dpi=160)
