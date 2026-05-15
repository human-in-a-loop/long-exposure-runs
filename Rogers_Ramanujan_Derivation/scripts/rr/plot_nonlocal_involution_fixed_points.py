# created: 2026-05-15T01:05:00Z
# cycle: 5
# run_id: run-2026-05-14T232311Z
# agent: worker-clone-0
# milestone: M2
#
# Plot fixed/unpaired objects from the nonlocal transformed-involution probe.

import csv
import os
from collections import defaultdict

import matplotlib.pyplot as plt


workspace = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
data_path = os.path.join(workspace, "data", "finite_experiments", "nonlocal_involution_fixed_points.csv")
out_path = os.environ.get(
    "FIGURE_OUT",
    os.path.join(workspace, "data", "finite_experiments", "nonlocal_involution_fixed_points.png"),
)

rows = []
with open(data_path, newline="") as handle:
    for row in csv.DictReader(handle):
        if row["tie_breaker"] == "lex_largest":
            rows.append(row)

max_n = max(int(row["N"]) for row in rows)
rows = [row for row in rows if int(row["N"]) == max_n]

counts = defaultdict(int)
predicted = defaultdict(set)
for row in rows:
    key = (int(row["alpha"]), int(row["exponent"]), row["classification"])
    counts[key] += 1
    if row["predicted_pentagonal"] == "True":
        predicted[int(row["alpha"])].add(int(row["exponent"]))

fig, axes = plt.subplots(2, 1, figsize=(10, 6), sharex=True)
for alpha, ax in enumerate(axes):
    xs_no = []
    ys_no = []
    xs_fixed = []
    ys_fixed = []
    for (a, exp, cls), count in counts.items():
        if a != alpha:
            continue
        if cls == "fixed_predicted":
            xs_fixed.append(exp)
            ys_fixed.append(count)
        else:
            xs_no.append(exp)
            ys_no.append(count)
    ax.bar(xs_no, ys_no, width=0.8, color="#b94a48", label="unpaired non-predicted")
    ax.bar(xs_fixed, ys_fixed, width=0.8, color="#3b7ddd", label="predicted fixed")
    for exp in sorted(predicted[alpha]):
        ax.axvline(exp, color="#222222", linewidth=0.7, alpha=0.25)
    ax.set_ylabel(f"alpha={alpha}\nobjects")
    ax.set_ylim(bottom=0)
    ax.legend(loc="upper right", fontsize=8)
axes[-1].set_xlabel("exponent")
fig.suptitle(f"Nonlocal transfer fixed/unpaired objects at N={max_n}")
fig.tight_layout()
fig.savefig(out_path, dpi=160)
