#!/usr/bin/env python3
"""Track 5 source-density diagnostics + leave-one-source-out coverage probe.
Read-only against tracks/track5/data/.

Dr. Duke dominance is foregrounded per research brief.
"""
from __future__ import annotations
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
T5 = ROOT / "tracks" / "track5" / "data"


def main() -> None:
    enr = pd.read_parquet(T5 / "track5_enrichment_edges.parquet")
    bio = pd.read_parquet(T5 / "track5_bioactivity_assertions.parquet")

    # ---- per-source baseline counts (over enrichment + bioactivity)
    sources = sorted(set(enr["source_id"]).union(bio["source_id"]))
    fam_assertion_threshold = 100

    base = (
        enr.dropna(subset=["family"])
        .groupby(["family", "edge_type"]).size().reset_index(name="n")
    )
    base_cells_ge100 = base[base["n"] >= fam_assertion_threshold]
    n_base_cells_ge100 = len(base_cells_ge100)
    n_base_taxa = enr["accepted_taxon_key"].nunique()
    n_base_compounds = enr["compound_id"].nunique()
    n_base_bioclasses = bio["bioactivity_class"].nunique()

    src_rows = []
    for s in sources:
        sub_enr = enr[enr["source_id"] == s]
        sub_bio = bio[bio["source_id"] == s]
        fams_with = (
            sub_enr.dropna(subset=["family"]).groupby(["family", "edge_type"]).size().reset_index(name="n")
        )
        fams_ge100 = fams_with[fams_with["n"] >= fam_assertion_threshold]["family"].nunique()
        src_rows.append({
            "source_id": s,
            "n_edges": int(len(sub_enr) + len(sub_bio)),
            "n_phyto_edges": int((sub_enr["edge_type"] == "phytochemical_assertion").sum()),
            "n_ethno_edges": int((sub_enr["edge_type"] == "ethnobotanical_use_assertion").sum()),
            "n_bioactivity_edges": int(len(sub_bio)),
            "n_taxa": int(sub_enr["accepted_taxon_key"].nunique()),
            "n_compounds": int(pd.concat([sub_enr["compound_id"], sub_bio["compound_id"]]).nunique()),
            "n_families_with_assertion": int(sub_enr["family"].nunique()),
            "n_families_with_ge100_assertions": int(fams_ge100),
            "share_of_total_edges": round((len(sub_enr) + len(sub_bio)) / (len(enr) + len(bio)), 6),
            "share_of_total_taxa_in_enrichment": round(sub_enr["accepted_taxon_key"].nunique() / max(n_base_taxa, 1), 6),
        })
    src_df = pd.DataFrame(src_rows).sort_values("n_edges", ascending=False)
    src_df.to_csv(T5 / "source_density_diagnostics.tsv", sep="\t", index=False)

    # ---- leave-one-source-out coverage
    loso_rows = []
    # baseline row
    loso_rows.append({
        "source_dropped": "(none — baseline)",
        "surviving_taxa_with_assertion": n_base_taxa,
        "surviving_family_cells_ge100": n_base_cells_ge100,
        "surviving_compounds": n_base_compounds,
        "surviving_bioactivity_classes": n_base_bioclasses,
        "n_taxa_lost": 0,
        "n_family_cells_demoted_below_floor": 0,
    })
    for s in sources:
        rem_enr = enr[enr["source_id"] != s]
        rem_bio = bio[bio["source_id"] != s]
        surv_taxa = rem_enr["accepted_taxon_key"].nunique()
        rem_cells = (
            rem_enr.dropna(subset=["family"]).groupby(["family", "edge_type"]).size().reset_index(name="n")
        )
        surv_cells_ge100 = len(rem_cells[rem_cells["n"] >= fam_assertion_threshold])
        loso_rows.append({
            "source_dropped": s,
            "surviving_taxa_with_assertion": surv_taxa,
            "surviving_family_cells_ge100": surv_cells_ge100,
            "surviving_compounds": int(rem_enr["compound_id"].nunique()),
            "surviving_bioactivity_classes": int(rem_bio["bioactivity_class"].nunique()),
            "n_taxa_lost": n_base_taxa - surv_taxa,
            "n_family_cells_demoted_below_floor": n_base_cells_ge100 - surv_cells_ge100,
        })
    loso_df = pd.DataFrame(loso_rows)
    loso_df.to_csv(T5 / "leave_one_source_out_coverage.tsv", sep="\t", index=False)

    # ---- Dr. Duke dominance per-family audit
    duke_rows = []
    fam_edges = enr.dropna(subset=["family"]).groupby("family")
    for fam, sub in fam_edges:
        n_total = len(sub)
        n_duke = int((sub["source_class"] == "Dr. Duke").sum())
        share = n_duke / n_total if n_total else 0.0
        status = "ge100_baseline" if n_total >= fam_assertion_threshold else "below_100_baseline"
        if n_duke == n_total and n_total > 0:
            status_if_duke_dropped = "lost_entirely"
        elif (n_total - n_duke) < fam_assertion_threshold and n_total >= fam_assertion_threshold:
            status_if_duke_dropped = "demoted_below_100"
        elif (n_total - n_duke) >= fam_assertion_threshold:
            status_if_duke_dropped = "survives_ge100"
        else:
            status_if_duke_dropped = "already_below_100"
        duke_rows.append({
            "family": fam,
            "n_assertions": n_total,
            "n_assertions_from_duke": n_duke,
            "duke_share": round(share, 6),
            "family_status_baseline": status,
            "family_status_if_duke_dropped": status_if_duke_dropped,
        })
    duke_df = pd.DataFrame(duke_rows).sort_values("n_assertions", ascending=False)
    duke_df.to_csv(T5 / "dr_duke_dominance_audit.tsv", sep="\t", index=False)

    # Overall numbers
    overall_duke_share = (enr["source_class"] == "Dr. Duke").mean()
    fams_lost = (duke_df["family_status_if_duke_dropped"] == "lost_entirely").sum()
    fams_demoted = (duke_df["family_status_if_duke_dropped"] == "demoted_below_100").sum()
    print(f"sources covered: {sources}")
    print(f"baseline family-cells (family x edge_type) >=100: {n_base_cells_ge100}")
    print(f"overall Duke share of enrichment edges: {overall_duke_share:.4f}")
    print(f"families completely lost if Duke dropped: {int(fams_lost)}")
    print(f"families demoted below 100 if Duke dropped: {int(fams_demoted)}")


if __name__ == "__main__":
    main()
