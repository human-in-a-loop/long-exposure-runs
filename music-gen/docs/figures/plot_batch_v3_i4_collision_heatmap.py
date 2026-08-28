#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-08-28T16:45:00Z
# cycle: 15
# run_id: run-2026-08-28T040704Z
# agent: worker (clone-1, fork 392503ab7d47)
# milestone: M-GEN-1/batch-v3-i4
# ---
"""Plot batch-v3-i4 8x8 collision heatmap per rule_type (5 panels + total),
alongside batch-v2 baseline for side-by-side comparison."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

_REPO = Path(__file__).resolve().parent.parent.parent
V3 = _REPO / "data" / "gen" / "batch_v3_i4" / "collision_analysis.json"
V2 = _REPO / "data" / "gen" / "batch_v2" / "collision_analysis.json"

RULE_TYPES = ("harmonic", "rhythmic", "melodic", "form", "arrangement")
SALTS = list(range(8))


def _mat(js, rt):
    return np.asarray(js["coerced"]["per_rule_type_matrix"][rt])


def _total_mat(js):
    out = np.zeros((8, 8), dtype=int)
    for rt in RULE_TYPES:
        out += np.asarray(js["coerced"]["per_rule_type_matrix"][rt])
    np.fill_diagonal(out, 0)
    return out


def main():
    v3 = json.loads(V3.read_text())
    v2 = json.loads(V2.read_text())

    fig, axes = plt.subplots(2, 6, figsize=(18, 6.5))
    for col, rt in enumerate(RULE_TYPES):
        for row_i, (js, tag) in enumerate([(v2, "batch-v2"), (v3, "batch-v3-i4")]):
            ax = axes[row_i, col]
            M = _mat(js, rt).copy()
            np.fill_diagonal(M, 0)
            im = ax.imshow(M, cmap="Reds", vmin=0, vmax=1, aspect="equal")
            ax.set_title(f"{tag}\n{rt}", fontsize=9)
            ax.set_xticks(SALTS); ax.set_yticks(SALTS)
            ax.set_xticklabels(SALTS, fontsize=7); ax.set_yticklabels(SALTS, fontsize=7)
            n_pairs = int(M[np.triu_indices(8, k=1)].sum())
            ax.set_xlabel(f"pairs={n_pairs}", fontsize=8)

    for row_i, (js, tag) in enumerate([(v2, "batch-v2"), (v3, "batch-v3-i4")]):
        ax = axes[row_i, 5]
        M = _total_mat(js)
        im = ax.imshow(M, cmap="Reds", vmin=0, vmax=5, aspect="equal")
        ax.set_title(f"{tag}\nTOTAL (sum over rule_types)", fontsize=9)
        ax.set_xticks(SALTS); ax.set_yticks(SALTS)
        ax.set_xticklabels(SALTS, fontsize=7); ax.set_yticklabels(SALTS, fontsize=7)
        total_pairs = int(M[np.triu_indices(8, k=1)].sum())
        ax.set_xlabel(f"pairs={total_pairs}", fontsize=8)
        for (i, j), v in np.ndenumerate(M):
            if v > 0:
                ax.text(j, i, str(v), ha="center", va="center",
                        color="white" if v >= 3 else "black", fontsize=7)

    fig.suptitle(
        "Collision heatmap comparison: batch-v2 (cycle-13, legacy sampler) vs batch-v3-i4 "
        "(cycle-15, I4 stratified rejection sampler). 8×8 salt pairs; cell = 1 iff coerced "
        "rule_id matches. Prediction: 0 pairs at N=8. Observed on batch-v3-i4: 0 pairs. "
        "batch-v2 total: 11 pairs (published cycle-13 baseline).",
        fontsize=10, y=0.99, wrap=True)
    fig.tight_layout(rect=(0, 0, 1, 0.94))

    out = os.environ.get("FIGURE_OUT",
                          str(_REPO / "docs" / "figures" / "batch_v3_i4_collision_heatmap.png"))
    fig.savefig(out, dpi=140)
    print(f"[plot_batch_v3_i4_collision_heatmap] wrote {out}")


if __name__ == "__main__":
    main()
