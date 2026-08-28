#!/usr/bin/env python3
# ---
# created: 2026-08-28T23:05:00Z
# cycle: 28
# run_id: run-2026-08-28T040704Z
# agent: worker
# milestone: M-GEN-1/collision-model-hash-space-geometry
# ---
"""Per-(rule_type x batch) chi-squared p-value panel figure.

Reads data/collision_model/hash_uniformity_summary.json.
Emits docs/figures/hash_geometry_per_rule_type.png.

One panel per rule_type; x-axis is batch, y-axis is chi-squared p-value
(log-scaled). A horizontal reference line at p=0.05 highlights any
significant departures from hash-uniformity.

Interpreter-guarded /usr/bin/python3.  No PRNG.
"""
from __future__ import annotations

import json
import pathlib
import sys

assert sys.executable == "/usr/bin/python3", sys.executable

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[2]
SUM_PATH = ROOT / "data" / "collision_model" / "hash_uniformity_summary.json"
FIG_PATH = ROOT / "docs" / "figures" / "hash_geometry_per_rule_type.png"

RULE_TYPES = ("harmonic", "rhythmic", "melodic", "form", "arrangement")


def main(argv: list[str]) -> int:
    s = json.loads(SUM_PATH.read_text())
    batches = sorted(s["batches"].keys())
    fig, axes = plt.subplots(1, len(RULE_TYPES), figsize=(3.0 * len(RULE_TYPES), 4.5), sharey=True)
    for ax, rt in zip(axes, RULE_TYPES):
        pvals = []
        for b in batches:
            e = s["batches"][b][rt]
            pvals.append(max(float(e["p_value"]), 1e-6))
        xs = list(range(len(batches)))
        colors = ["#cc4444" if p < 0.05 else "#4477aa" for p in pvals]
        ax.bar(xs, pvals, color=colors)
        ax.set_yscale("log")
        ax.axhline(0.05, color="black", linestyle="--", linewidth=0.8, label="p=0.05")
        ax.set_xticks(xs)
        ax.set_xticklabels([b.replace("batch_", "") for b in batches], rotation=45, ha="right", fontsize=8)
        ax.set_title(rt, fontsize=10)
        ax.set_ylim(1e-6, 2.0)
    axes[0].set_ylabel("chi-squared p-value (log scale)")
    fig.suptitle(
        "Hash-space uniformity per (rule_type x batch) - chi-squared vs uniform-over-K",
        fontsize=11,
    )
    fig.tight_layout(rect=[0, 0, 1, 0.94])
    FIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIG_PATH, dpi=110)
    plt.close(fig)
    print(f"[plot_hash_geometry_panel] wrote {FIG_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
