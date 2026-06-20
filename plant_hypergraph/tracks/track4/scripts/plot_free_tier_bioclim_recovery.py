#!/usr/bin/env python3
# created: 2026-05-18T21:05:00+00:00
# cycle: 28
# run_id: run-phytograph-cycle28-track4-free-tier-bioclim-recovery
# agent: worker
# milestone: _plan/track4-free-tier-bioclim-recovery
"""Plot the Track 4 free-tier BIOCLIM recovery funnel."""

from __future__ import annotations

import os
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "tracks" / "track4" / "data"
OUT = Path(os.environ.get("FIGURE_OUT", ROOT / "tracks" / "track4" / "figures" / "track4_free_tier_bioclim_recovery.png"))


def main() -> None:
    occurrence = pd.read_csv(DATA / "free_tier_occurrence_summary.tsv", sep="\t", dtype=str, keep_default_na=False)
    vectors = pd.read_csv(DATA / "free_tier_bioclim_vectors.tsv", sep="\t", dtype=str, keep_default_na=False)
    comparators = pd.read_csv(DATA / "free_tier_validation_comparators.tsv", sep="\t", dtype=str, keep_default_na=False)

    counts = {
        "queried taxa": occurrence["queried_name"].nunique(),
        "license-compatible\ncoordinates": int(occurrence["license_compatible_records"].astype(int).sum()),
        "post-filter\ncoordinates": int(vectors["n_coordinates_used"].astype(int).sum()),
        "numeric BIOCLIM\nvectors": int((vectors["mean"].astype(str).str.strip() != "").sum()),
        "validation-allowed\ncomparators": int(comparators["validation_allowed"].eq("true").sum()),
    }

    fig, ax = plt.subplots(figsize=(9, 4.8))
    colors = ["#4c78a8", "#59a14f", "#f28e2b", "#e15759", "#b07aa1"]
    bars = ax.bar(list(counts), list(counts.values()), color=colors)
    ax.set_ylabel("count")
    ax.set_title("Track 4 free-tier recovery funnel")
    ax.grid(axis="y", alpha=0.25)
    for bar, value in zip(bars, counts.values()):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + max(counts.values()) * 0.02, str(value), ha="center", va="bottom", fontsize=9)
    ax.set_ylim(0, max(counts.values()) * 1.18 if counts.values() else 1)
    fig.tight_layout()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, dpi=160)
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
