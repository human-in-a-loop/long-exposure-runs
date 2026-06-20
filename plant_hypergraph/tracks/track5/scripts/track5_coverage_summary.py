#!/usr/bin/env python3
"""Track 5 coverage tabulations against the enrichment edges view.
Read-only against tracks/track5/data/ and phytograph_dataset/.
"""
from __future__ import annotations
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
T5 = ROOT / "tracks" / "track5" / "data"


def _dominant(series: pd.Series) -> tuple[str, float]:
    counts = series.value_counts()
    total = counts.sum()
    if total == 0:
        return ("", 0.0)
    return (counts.index[0], float(counts.iloc[0] / total))


def main() -> None:
    enr = pd.read_parquet(T5 / "track5_enrichment_edges.parquet")
    bio = pd.read_parquet(T5 / "track5_bioactivity_assertions.parquet")
    cc = pd.read_parquet(T5 / "track5_compound_class_membership.parquet")

    # ---- per-taxon screening intensity
    grp = enr.groupby("accepted_taxon_key")
    per_taxon = pd.DataFrame({
        "n_assertions": grp.size(),
        "n_sources": grp["source_id"].nunique(),
        "n_compounds": grp["compound_id"].nunique(),
    }).reset_index()
    # papers approximated by distinct source_id (substrate does not preserve per-row paper id)
    per_taxon["n_papers"] = per_taxon["n_sources"]
    dom = grp["source_id"].agg(lambda s: _dominant(s))
    per_taxon["dominant_source"] = [d[0] for d in dom]
    per_taxon["dominant_source_share"] = [d[1] for d in dom]
    per_taxon.to_csv(T5 / "per_taxon_screening_intensity.tsv", sep="\t", index=False)

    # ---- family chemistry coverage summary
    f = enr.groupby("family")
    fam_summary = pd.DataFrame({
        "n_taxa_with_assertion": f["accepted_taxon_key"].nunique(),
        "n_compounds": f["compound_id"].nunique(),
        "n_compound_classes": f["compound_class"].nunique(dropna=True),
        "n_phytochemical_edges": f.apply(lambda d: int((d["edge_type"]=="phytochemical_assertion").sum())),
        "n_ethnobotanical_edges": f.apply(lambda d: int((d["edge_type"]=="ethnobotanical_use_assertion").sum())),
        "n_sources": f["source_id"].nunique(),
    }).reset_index()
    # n_bioactivity_classes: bioactivity is compound-keyed, so family count requires compound -> taxon back-link.
    # We approximate by joining bioactivity compounds against phyto edges' compound_id per family.
    fam_compounds = enr.dropna(subset=["compound_id"]).groupby("family")["compound_id"].apply(set)
    bio_per_compound = bio.groupby("compound_id")["bioactivity_class"].nunique()
    fam_bioclasses = {}
    for fam, cset in fam_compounds.items():
        bcs = set()
        for c in cset:
            if c in bio.index if hasattr(bio,'index') else False:
                pass
        sub = bio[bio["compound_id"].isin(cset)]
        fam_bioclasses[fam] = sub["bioactivity_class"].nunique()
    fam_summary["n_bioactivity_classes"] = fam_summary["family"].map(fam_bioclasses).fillna(0).astype(int)
    fam_summary = fam_summary.sort_values("n_phytochemical_edges", ascending=False)
    fam_summary.to_csv(T5 / "family_chemistry_coverage_summary.tsv", sep="\t", index=False)

    # ---- family x compound_class matrix (long form)
    fcc = (
        enr.dropna(subset=["family", "compound_class"])  # require both
        .groupby(["family", "compound_class"])
        .agg(
            n_taxa=("accepted_taxon_key", "nunique"),
            n_assertions=("edge_id", "count"),
            n_sources=("source_id", "nunique"),
        )
        .reset_index()
        .sort_values(["family", "n_assertions"], ascending=[True, False])
    )
    fcc.to_csv(T5 / "family_compound_class_matrix.tsv", sep="\t", index=False)

    # Summary report to stdout
    print(f"per_taxon_screening_intensity: {len(per_taxon)} taxa")
    print(f"family_chemistry_coverage_summary: {len(fam_summary)} families")
    print(f"family_compound_class_matrix: {len(fcc)} (family, class) cells")
    # family-cells >=100 assertions
    edge_cells = enr.dropna(subset=["family"]).groupby(["family", "edge_type"]).size().reset_index(name="n")
    cells_ge100 = edge_cells[edge_cells["n"] >= 100]
    print(f"family-cells (family x edge_type) with >=100 assertions: {len(cells_ge100)}")


if __name__ == "__main__":
    main()
