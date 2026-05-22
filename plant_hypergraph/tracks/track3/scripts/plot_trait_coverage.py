"""Plot per-trait accepted-taxon coverage by top-10 families (Wave 2, Track 3)."""
from __future__ import annotations

import os
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = Path(os.environ.get("FIGURE_OUT", str(DATA / "track3_trait_coverage_by_family.png")))


def main():
    df = pq.read_table(DATA / "convergence_trait_edges.parquet").to_pandas()
    resolved = df[(df["pending_crosswalk"] == False) & (df["family_label"] != "")]
    canonical_order = [
        "fleshy_fruit", "capsule", "drupe", "achene", "follicle", "samara",
        "aril", "myrmecochory", "elaiosome", "c4_photosynthesis",
        "cam_photosynthesis", "succulence",
    ]
    traits = [t for t in canonical_order if t in resolved["trait"].unique()]

    # Build counts: trait -> family -> n_taxa (top 10 per trait, rest into 'other_families')
    rows = []
    for t in traits:
        sub = resolved[resolved["trait"] == t]
        fam_counts = (
            sub.groupby("family_label")["accepted_taxon_key"].nunique().sort_values(ascending=False)
        )
        top = fam_counts.head(10)
        rest_sum = int(fam_counts.iloc[10:].sum()) if len(fam_counts) > 10 else 0
        for fam, n in top.items():
            rows.append({"trait": t, "family": fam, "n_taxa": int(n)})
        if rest_sum > 0:
            rows.append({"trait": t, "family": "other_families", "n_taxa": rest_sum})

    pivot = pd.DataFrame(rows).pivot_table(
        index="trait", columns="family", values="n_taxa", fill_value=0
    ).loc[traits]

    fig, ax = plt.subplots(figsize=(12, 7))
    pivot.plot(kind="barh", stacked=True, ax=ax, cmap="tab20", legend=False)
    ax.set_xlabel("Accepted taxa (resolved, by family)")
    ax.set_ylabel("Track 3 trait")
    ax.set_title(
        "Per-trait accepted-taxon coverage by top-10 families\n"
        "Wave 2 Track 3 enrichment over frozen Barrier 1 substrate\n"
        "(no convergence_signature rows inferred)"
    )
    # legend outside
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles, labels, bbox_to_anchor=(1.01, 1), loc="upper left",
              fontsize=7, ncol=1, title="family")
    plt.tight_layout()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(OUT, dpi=150, bbox_inches="tight")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
