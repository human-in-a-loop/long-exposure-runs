# created: 2026-05-15T00:45:00Z
# cycle: 4
# run_id: run-2026-05-14T232311Z
# agent: worker
# milestone: M2
#
# Plot signed survivor pattern for transformed Rogers-Ramanujan sums.

import csv
import os
import argparse

import matplotlib.pyplot as plt


def read_rows(path):
    with open(path, newline="") as handle:
        return list(csv.DictReader(handle))


workspace = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
csv_path = os.path.join(workspace, "data", "finite_experiments", "transformed_cancellation_coefficients.csv")
default_out = os.path.join(
    workspace,
    "data",
    "finite_experiments",
    "transformed_cancellation_survivors.png",
)

parser = argparse.ArgumentParser(description="Plot transformed cancellation survivor coefficients.")
parser.add_argument("--out", default=os.environ.get("FIGURE_OUT", default_out))
args = parser.parse_args()

rows = read_rows(csv_path)

nmax = max(int(row["N"]) for row in rows)
fig, axes = plt.subplots(2, 1, figsize=(10, 6), sharex=True)

for axis, alpha in zip(axes, [0, 1]):
    subset = [row for row in rows if int(row["alpha"]) == alpha and int(row["N"]) == nmax]
    xs = [int(row["exponent"]) for row in subset]
    ys = [int(row["signed_coefficient"]) for row in subset]
    colors = ["#1f77b4" if row["is_pentagonal_exponent"] == "True" else "#b8b8b8" for row in subset]
    axis.axhline(0, color="#333333", linewidth=0.8)
    axis.bar(xs, ys, color=colors, width=0.85)
    axis.set_ylabel(f"alpha={alpha}\nsigned coeff.")
    axis.set_ylim(min(ys + [-1]) - 0.5, max(ys + [1]) + 0.5)
    axis.grid(axis="y", alpha=0.25)

axes[-1].set_xlabel("coefficient degree k")
fig.suptitle(f"Signed survivor pattern for H_alpha,N at N={nmax}")
fig.tight_layout(rect=(0, 0, 1, 0.95))

fig.savefig(args.out, dpi=160)
