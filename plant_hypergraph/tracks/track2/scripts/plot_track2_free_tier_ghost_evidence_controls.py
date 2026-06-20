#!/usr/bin/env python3
# created: 2026-05-18T23:55:00+00:00
# cycle: 31
# run_id: fork-2f05eabe3800-clone-0-track2-free-tier-ghost-controls
# agent: worker-clone-0
# milestone: M4.V2
"""Plot Track 2 free-tier ghost evidence/control matrix gates."""

from __future__ import annotations

import os
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parents[3]
DATA_PATH = ROOT / "tracks" / "track2" / "data" / "track2_free_tier_ghost_evidence_controls.tsv"
OUT = Path(os.environ.get("FIGURE_OUT", ROOT / "tracks" / "track2" / "figures" / "track2_free_tier_ghost_control_matrix.png"))


def main() -> None:
    df = pd.read_csv(DATA_PATH, sep="\t").fillna("")
    gates = pd.DataFrame(
        {
            "accepted key": df["accepted_key_after_free_tier_recovery"].astype(str).ne(""),
            "independent modern failure": df["modern_failure_independent_free_tier_status"].eq(
                "independent_modern_failure_present"
            ),
            "non-singleton source": df["non_singleton_source_support"].astype(bool),
            "living-megafauna excluded": df["living_megafauna_exclusion_status"].eq(
                "passes_living_megafauna_exclusion"
            ),
            "contract pass": df["passes_validation_contract"].astype(bool),
        }
    )
    counts = gates.groupby(df["row_scope"]).sum().reindex(["canonical_heldout", "local_candidate"])
    totals = df["row_scope"].value_counts().reindex(["canonical_heldout", "local_candidate"])

    fig, axes = plt.subplots(1, 2, figsize=(12.5, 4.8))
    counts.plot(kind="bar", ax=axes[0], width=0.78)
    axes[0].set_title("Rows passing each validation gate")
    axes[0].set_ylabel("Rows")
    axes[0].set_xlabel("Row scope")
    axes[0].set_ylim(0, max(int(totals.max()), 1) + 2)
    axes[0].tick_params(axis="x", labelrotation=0)
    axes[0].legend(fontsize=8, ncol=1)

    status_counts = (
        df.groupby(["row_scope", "final_status"])
        .size()
        .unstack(fill_value=0)
        .reindex(["canonical_heldout", "local_candidate"])
    )
    status_counts.plot(kind="bar", stacked=True, ax=axes[1], width=0.68)
    axes[1].set_title("Final validation-contract status")
    axes[1].set_ylabel("Rows")
    axes[1].set_xlabel("Row scope")
    axes[1].tick_params(axis="x", labelrotation=0)
    axes[1].legend(fontsize=8)

    fig.suptitle("Track 2 free-tier ghost evidence/control matrix", fontsize=12)
    plt.tight_layout()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, dpi=160)
    plt.close(fig)


if __name__ == "__main__":
    main()
