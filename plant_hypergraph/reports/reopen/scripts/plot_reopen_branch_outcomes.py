# created: 2026-05-18T20:05:00+00:00
# updated: 2026-05-18T21:40:00+00:00
# cycle: 28
# run_id: run-phytograph-cycle28-free-tier-recovery-integration
# agent: worker
# milestone: _plan/free-tier-recovery-integration

from pathlib import Path
import os

import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parents[3]
STATUS = ROOT / "data/reopen/reopen_closure_status.tsv"


def main() -> None:
    out = Path(os.environ["FIGURE_OUT"])
    df = pd.read_csv(STATUS, sep="\t")
    severity = {
        "branch_local_threshold_met_reconciliation_pending": 2,
        "evidence_added_but_threshold_not_met": 1,
        "still_data_limited": 0.5,
        "insufficient_non_duke_temporal_evidence_h5_remains_source_biased": 0.5,
        "no_new_qualifying_evidence": 0,
    }
    colors = {
        "branch_local_threshold_met_reconciliation_pending": "#6f4e9b",
        "evidence_added_but_threshold_not_met": "#4c78a8",
        "still_data_limited": "#d18f24",
        "insufficient_non_duke_temporal_evidence_h5_remains_source_biased": "#b26d5d",
        "no_new_qualifying_evidence": "#9aa0a6",
    }
    df["score"] = df["result"].map(severity)

    fig, ax = plt.subplots(figsize=(8.5, 4.8))
    bars = ax.bar(
        df["track"],
        df["score"],
        color=[colors[value] for value in df["result"]],
        edgecolor="#202124",
        linewidth=0.8,
    )
    ax.axhline(2, color="#b3261e", linewidth=1.2, linestyle="--", label="reconciliation threshold")
    ax.set_ylim(0, 2.25)
    ax.set_ylabel("Reopen evidence level")
    ax.set_title("Free-tier recovery branch outcomes")
    ax.set_yticks([0, 1, 2])
    ax.set_yticklabels(["no qualifying evidence", "partial/refined blocker", "threshold met locally"])
    ax.grid(axis="y", color="#e0e0e0", linewidth=0.8)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    labels = {
        "Track 1": "threshold met\nbranch-local",
        "Track 4": "coordinates,\nno BIOCLIM",
        "Track 5": "2 candidates,\nno stratum",
        "Track 6": "none",
    }
    for bar, track in zip(bars, df["track"]):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.06,
            labels[track],
            ha="center",
            va="bottom",
            fontsize=9,
        )

    fig.tight_layout()
    fig.savefig(out, dpi=160)


if __name__ == "__main__":
    main()
