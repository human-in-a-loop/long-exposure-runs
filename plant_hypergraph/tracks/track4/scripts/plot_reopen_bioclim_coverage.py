#!/usr/bin/env python3
# created: 2026-05-18T17:10:00+00:00
# cycle: 24
# run_id: run-phytograph-cycle24-track4-bioclim-validation-reopen
# agent: worker
# milestone: _plan/track4-bioclim-validation-reopen
"""Plot Track 4 reopen coverage diagnostics."""

from __future__ import annotations

import os
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parents[3]
DIAGNOSTICS = ROOT / "tracks" / "track4" / "data" / "track4_reopen_join_diagnostics.tsv"


def main() -> None:
    out = Path(os.environ.get("FIGURE_OUT", ROOT / "tracks" / "track4" / "figures" / "track4_reopen_bioclim_coverage.png"))
    df = pd.read_csv(DIAGNOSTICS, sep="\t")
    labels = [
        "Climate\nstaging",
        "CWR\npairs",
        "Held-out\nset",
        "Training\ncandidates",
    ]
    x = range(len(df))

    fig, ax = plt.subplots(figsize=(10.5, 5.6))
    bottom = [0] * len(df)
    series = [
        ("accepted_key_rows", "accepted-key rows", "#2b7a78"),
        ("bioclim_vector_rows", "numeric bioclim rows", "#5b8fb9"),
        ("heldout_validation_rows", "validation-allowed held-outs", "#9f7aea"),
        ("rejected_rows", "rejected/nonqualifying rows", "#b85c38"),
    ]
    for column, label, color in series:
        values = df[column].astype(int).tolist()
        ax.bar(x, values, bottom=bottom, label=label, color=color)
        bottom = [a + b for a, b in zip(bottom, values)]

    ax.set_xticks(list(x))
    ax.set_xticklabels(labels)
    ax.set_ylabel("Rows")
    ax.set_title("Track 4 reopen evidence coverage")
    ax.legend(loc="upper right", frameon=False)
    ax.grid(axis="y", alpha=0.25)
    ax.text(
        0.01,
        0.96,
        "Numeric bioclim vectors = 0; validation-allowed held-out pairs = 0",
        transform=ax.transAxes,
        ha="left",
        va="top",
        fontsize=10,
        bbox={"boxstyle": "round,pad=0.25", "facecolor": "white", "edgecolor": "#cccccc", "alpha": 0.9},
    )
    fig.tight_layout()
    fig.savefig(out, dpi=160)


if __name__ == "__main__":
    main()
