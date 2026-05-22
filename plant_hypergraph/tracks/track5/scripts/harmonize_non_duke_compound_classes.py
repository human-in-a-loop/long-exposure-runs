#!/usr/bin/env python3
"""Harmonize locally available non-Duke compound/class rows, if any.

created: 2026-05-18T04:35:00+00:00
cycle: 10
run_id: fork-aaf42b4ab956-clone-3-track5-wave4
agent: worker-clone-3
milestone: M4.A-track5-duke-source-ablation
"""
from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "tracks" / "track5" / "data"

DETECTION_SCOPE = (
    "detection/class harmonization only; does not support taxon-level bioactivity, "
    "clinical efficacy, safety, dosage, or therapeutic claim"
)


def main() -> None:
    enrichment = pd.read_parquet(DATA / "track5_enrichment_edges.parquet")
    classes = pd.read_parquet(DATA / "track5_compound_class_membership.parquet")

    local_non_duke_classes = classes[~classes["source"].fillna("").str.contains("Dr. Duke", case=False)]
    non_duke_detections = enrichment[
        (enrichment["edge_type"] == "phytochemical_assertion")
        & (enrichment["retained"])
        & (enrichment["source_class"] != "Dr. Duke")
    ].copy()

    if local_non_duke_classes.empty or non_duke_detections.empty:
        out = pd.DataFrame(
            [
                {
                    "accepted_taxon_key": None,
                    "compound_id": None,
                    "compound_class": None,
                    "source_id": None,
                    "source_class": None,
                    "harmonization_status": "no_local_non_duke_detection_class_rows",
                    "evidence_scope": DETECTION_SCOPE,
                }
            ]
        )
    else:
        out = non_duke_detections.merge(
            local_non_duke_classes[["compound_id", "compound_class", "source"]],
            on="compound_id",
            how="inner",
            suffixes=("_detection", "_class"),
        )
        out = out[
            [
                "accepted_taxon_key",
                "compound_id",
                "compound_class_class",
                "source_id",
                "source_class",
            ]
        ].rename(columns={"compound_class_class": "compound_class"})
        out["harmonization_status"] = "harmonized_non_duke_detection_class"
        out["evidence_scope"] = DETECTION_SCOPE

    out.to_csv(DATA / "non_duke_class_harmonization.tsv", sep="\t", index=False)
    print(f"WROTE: {DATA / 'non_duke_class_harmonization.tsv'} ({len(out)} rows)")


if __name__ == "__main__":
    sys.exit(main())
