# created: 2026-05-15T01:30:00Z
# cycle: 6
# run_id: run-2026-05-14T232311Z
# agent: worker
# milestone: M2
#
# Plot residual support for the Euler-tail double-sum telescoping probe.

import argparse
import csv
import os

import matplotlib.pyplot as plt


parser = argparse.ArgumentParser(description="Plot Euler-tail lattice and residual diagnostics.")
parser.add_argument(
    "--out",
    default=os.environ.get("FIGURE_OUT", "data/finite_experiments/euler_tail_lattice_residuals.png"),
    help="Output PNG path. Defaults to FIGURE_OUT or data/finite_experiments/euler_tail_lattice_residuals.png.",
)
args = parser.parse_args()

workspace = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
data_dir = os.path.join(workspace, "data", "finite_experiments")
terms_path = os.path.join(data_dir, "euler_tail_terms.csv")
residuals_path = os.path.join(data_dir, "euler_tail_residuals.csv")

terms = []
with open(terms_path, newline="") as f:
    for row in csv.DictReader(f):
        terms.append(
            {
                "alpha": int(row["alpha"]),
                "n": int(row["n"]),
                "k": int(row["k"]),
                "exponent": int(row["exponent"]),
                "is_pentagonal": int(row["is_pentagonal_exponent"]),
            }
        )

residuals = []
with open(residuals_path, newline="") as f:
    for row in csv.DictReader(f):
        residuals.append(
            {
                "alpha": int(row["alpha"]),
                "degree": int(row["degree"]),
                "residual": int(row["residual"]),
                "is_pentagonal": int(row["is_pentagonal_degree"]),
            }
        )

fig, axes = plt.subplots(2, 2, figsize=(11, 7), gridspec_kw={"height_ratios": [2, 1]})

for alpha in (0, 1):
    ax = axes[0][alpha]
    rows = [row for row in terms if row["alpha"] == alpha]
    colors = ["#2b8cbe" if row["is_pentagonal"] else "#bdbdbd" for row in rows]
    sizes = [36 if row["is_pentagonal"] else 16 for row in rows]
    ax.scatter([row["n"] for row in rows], [row["k"] for row in rows], c=colors, s=sizes, alpha=0.8)
    ax.set_title(f"alpha {alpha}: lattice terms through KMax")
    ax.set_xlabel("n")
    ax.set_ylabel("k")
    ax.grid(True, alpha=0.25)

    ax2 = axes[1][alpha]
    rrows = [row for row in residuals if row["alpha"] == alpha]
    xs = [row["degree"] for row in rrows]
    ys = [row["residual"] for row in rrows]
    colors = ["#2b8cbe" if row["is_pentagonal"] else "#d95f0e" for row in rrows]
    ax2.bar(xs, ys, color=colors, width=0.85)
    ax2.axhline(0, color="black", linewidth=0.8)
    ax2.set_xlabel("degree")
    ax2.set_ylabel("partial - bilateral")
    ax2.grid(True, axis="y", alpha=0.25)

fig.suptitle("Euler-tail double-sum lattice support and finite residuals")
fig.tight_layout()
fig.savefig(args.out, dpi=160)
