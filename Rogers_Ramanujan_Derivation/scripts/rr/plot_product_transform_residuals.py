# created: 2026-05-15T00:25:00Z
# cycle: 3
# run_id: run-2026-05-14T232311Z
# agent: worker
# milestone: M2
#
# Plot product-transform candidate first-failure degrees.

import csv
import os
import argparse
from collections import defaultdict

import matplotlib.pyplot as plt


parser = argparse.ArgumentParser(description="Plot product-transform candidate residual first-failure degrees.")
parser.add_argument(
    "--out",
    default=os.environ.get("FIGURE_OUT", "data/finite_experiments/product_transform_residuals.png"),
    help="Output PNG path. Defaults to FIGURE_OUT or data/finite_experiments/product_transform_residuals.png.",
)
args = parser.parse_args()

out = args.out
workspace = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
csv_path = os.path.join(workspace, "data", "finite_experiments", "product_transform_candidates.csv")

rows = []
with open(csv_path, newline="") as f:
    for row in csv.DictReader(f):
        if row["N"] == "":
            continue
        n = int(row["N"])
        if n not in {0, 2, 4, 8, 12, 16, 20, 24}:
            continue
        first = row["first_nonzero_k"]
        first_k = 51 if first == "none_through_KMax" else int(first)
        rows.append(
            {
                "candidate": row["candidate"],
                "alpha": row["alpha"],
                "N": n,
                "parameter": row["parameter"],
                "first_k": first_k,
            }
        )

series = defaultdict(list)
for row in rows:
    name = row["candidate"]
    if name == "H_alpha_N_minus_schur_gaussian_window" and row["parameter"] not in {"1", "2", "3"}:
        continue
    if name == "H_alpha_N_minus_finite_jacobi_triple":
        label = f"alpha {row['alpha']}: finite Jacobi"
    elif name == "H_alpha_N_minus_plain_bilateral_limit":
        label = f"alpha {row['alpha']}: plain bilateral"
    elif name == "H_alpha_N_minus_schur_gaussian_window":
        label = f"alpha {row['alpha']}: Schur shift {row['parameter']}"
    elif name.startswith("negative"):
        label = name.replace("_", " ")
    else:
        continue
    series[label].append((row["N"], row["first_k"]))

plt.figure(figsize=(10, 6))
for label, points in sorted(series.items()):
    points = sorted(points)
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    linestyle = "--" if label.startswith("negative") else "-"
    plt.plot(xs, ys, marker="o", linewidth=1.5, linestyle=linestyle, label=label)

plt.axhline(51, color="black", linewidth=0.8, linestyle=":", label="none through KMax=50")
plt.xlabel("finite cutoff N")
plt.ylabel("first nonzero residual degree k")
plt.title("Product-transform finite identity residuals")
plt.ylim(-1, 54)
plt.grid(True, alpha=0.25)
plt.legend(fontsize=7, ncol=2)
plt.tight_layout()
plt.savefig(out, dpi=160)
