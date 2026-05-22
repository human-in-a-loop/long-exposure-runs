#!/usr/bin/env python3
# created: 2026-05-18T23:10:00+00:00
# cycle: 30
# run_id: run-phytograph-cycle30-track1-free-tier-control-strengthening
# agent: worker
# milestone: _plan/track1-free-tier-control-strengthening
"""Plot Track 1 sidecar control recovery diagnostics."""
from __future__ import annotations

import os
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
PANEL = ROOT / "tracks" / "track1" / "data" / "free_tier_reticulation_control_panel.tsv"


def main() -> None:
    out = Path(os.environ.get("FIGURE_OUT", ROOT / "tracks" / "track1" / "figures" / "track1_free_tier_control_recovery.png"))
    df = pd.read_csv(PANEL, sep="\t").fillna("")
    order = [
        "case",
        "genus_near",
        "family_near",
        "source_density_candidate",
    ]
    df["basis"] = df["control_match_basis"].where(df["control_match_basis"] != "case", "case")
    summary = (
        df.groupby("basis", dropna=False)
        .agg(rows=("accepted_key", "nunique"), mean_sources=("source_group_count", "mean"), recovered=("evidence_row_count", lambda s: (s.astype(int) > 0).sum()))
        .reindex(order)
        .fillna(0)
    )
    fig, ax1 = plt.subplots(figsize=(8, 5))
    x = range(len(summary))
    bars = ax1.bar(x, summary["rows"], color=["#2f6f4e", "#4878a8", "#79a6c9", "#c78d40"], label="taxa")
    ax1.set_ylabel("Taxa count")
    ax1.set_xticks(list(x))
    ax1.set_xticklabels(["cases", "genus-near", "family-near", "source-density\ncandidates"], rotation=0)
    ax1.set_title("Track 1 GBIF-sidecar case/control recovery")
    ax2 = ax1.twinx()
    ax2.plot(list(x), summary["recovered"], color="#8f2d2d", marker="o", linewidth=2, label="recovered event taxa")
    ax2.plot(list(x), summary["mean_sources"], color="#333333", marker="s", linewidth=2, label="mean event source groups")
    ax2.set_ylabel("Recovered taxa / mean event source groups")
    for i, bar in enumerate(bars):
        ax1.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.35, str(int(summary.iloc[i]["rows"])), ha="center", va="bottom", fontsize=9)
    lines, labels = ax2.get_legend_handles_labels()
    ax2.legend(lines, labels, loc="upper right", frameon=False)
    ax1.spines[["top"]].set_visible(False)
    ax2.spines[["top"]].set_visible(False)
    fig.tight_layout()
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=160)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
