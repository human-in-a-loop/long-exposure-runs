# created: 2026-05-15T02:50:00Z
# cycle: 8
# run_id: run-2026-05-14T232311Z
# agent: worker
# milestone: M2
#
# Plot cleared finite triangular-transform residuals for the derived
# Bailey-style matrix pairs.

import argparse
import csv
import os

import matplotlib.pyplot as plt


parser = argparse.ArgumentParser(description="Plot Bailey-matrix residual checks.")
parser.add_argument(
    "--out",
    default=os.environ.get("FIGURE_OUT", "data/finite_experiments/bailey_transform_residuals.png"),
    help="Output PNG path. Defaults to FIGURE_OUT or data/finite_experiments/bailey_transform_residuals.png.",
)
args = parser.parse_args()

workspace = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
csv_path = os.path.join(workspace, "data", "finite_experiments", "bailey_transform_residuals.csv")

series = {0: [], 1: []}
with open(csv_path, newline="") as f:
    for row in csv.DictReader(f):
        alpha_case = int(row["alpha_case"])
        series[alpha_case].append((int(row["n"]), int(row["max_abs_coeff"])))

plt.figure(figsize=(8, 4.5))
for alpha_case, points in series.items():
    points = sorted(points)
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    label = "a = 1" if alpha_case == 0 else "a = q"
    plt.plot(xs, ys, marker="o", linewidth=1.8, label=label)

plt.xlabel("triangular row n")
plt.ylabel("max abs coefficient of cleared residual")
plt.title("Bailey-style triangular pair residuals")
plt.ylim(-0.05, 1.0)
plt.grid(True, alpha=0.25)
plt.legend()
plt.tight_layout()
plt.savefig(args.out, dpi=160)
