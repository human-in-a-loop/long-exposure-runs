#!/usr/bin/env python3
"""Track 5 enrichment conformance checks.
Read-only. Exits 0 on pass, nonzero on fail.
"""
from __future__ import annotations
from pathlib import Path
import sys
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
T5 = ROOT / "tracks" / "track5" / "data"
SUBSTRATE = ROOT / "phytograph_dataset"

ALLOWED_SCOPES = {
    "phytochemical_assertion": {
        "Supports detection of this compound in this raw taxon label by this source.",
    },
    "ethnobotanical_use_assertion": {
        "Supports recorded human-use label in this source.",
        "Supports recorded use by the named people group as represented in NAEB.",
    },
    "bioactivity_assertion": {
        "Supports source-recorded bioactivity or assay annotation for the compound.",
    },
}


def fail(msg: str) -> None:
    print(f"FAIL: {msg}")
    sys.exit(1)


def main() -> None:
    enr = pd.read_parquet(T5 / "track5_enrichment_edges.parquet")
    bio = pd.read_parquet(T5 / "track5_bioactivity_assertions.parquet")
    he = pd.read_parquet(SUBSTRATE / "hyperedges.parquet")
    nodes = pd.read_parquet(SUBSTRATE / "nodes.parquet")

    # (1) every retained row's accepted_taxon_key is non-blank
    blanks = (enr["accepted_taxon_key"].fillna("") == "").sum()
    if blanks:
        fail(f"{blanks} enrichment rows have blank accepted_taxon_key")

    # (2) every retained row resolves to a known accepted-taxon-class node
    accepted_node_ids = set(
        nodes.loc[
            nodes["node_type"].isin(["species", "taxon", "genus", "infraspecific_unit", "cultivar"]),
            "node_id",
        ]
    )
    unknown = (~enr["accepted_taxon_key"].isin(accepted_node_ids)).sum()
    if unknown:
        fail(f"{unknown} enrichment rows reference accepted_taxon_key not in nodes.parquet")

    # (3) no row carries pending_crosswalk = True
    if enr["pending_crosswalk"].any():
        fail("at least one enrichment row has pending_crosswalk=True")

    # (4) allowed_evidence_scope matches schema
    for et in ["phytochemical_assertion", "ethnobotanical_use_assertion"]:
        sub = enr[enr["edge_type"] == et]
        bad = (~sub["evidence_scope"].isin(ALLOWED_SCOPES[et])).sum()
        if bad:
            fail(f"{bad} {et} rows have evidence_scope outside schema-permitted strings")
    # bioactivity: schema-permitted string lives on the substrate row; we relabel evidence_scope on projection
    bad_bio = (~bio["schema_evidence_scope"].isin(ALLOWED_SCOPES["bioactivity_assertion"])).sum()
    if bad_bio:
        fail(f"{bad_bio} bioactivity rows have schema_evidence_scope outside allowed set")

    # (5) bioactivity must be compound-keyed, not taxon-keyed
    if "accepted_taxon_key" in bio.columns:
        fail("bioactivity projection has accepted_taxon_key column — firewall violation")
    if bio["compound_id"].isna().any():
        fail("bioactivity rows are missing compound_id (firewall: bioactivity is compound-level)")

    # (6) row-count consistency: enrichment edges should equal substrate's resolved phyto+ethno count
    expected_enr = int(
        he[
            (he["edge_type"].isin({"phytochemical_assertion", "ethnobotanical_use_assertion"}))
            & (~he["pending_crosswalk"])
        ].shape[0]
    )
    if len(enr) != expected_enr:
        fail(f"enrichment row count {len(enr)} != substrate resolved-Track5 count {expected_enr}")
    expected_bio = int((he["edge_type"] == "bioactivity_assertion").shape[0])
    expected_bio = int((he["edge_type"] == "bioactivity_assertion").sum())
    if len(bio) != expected_bio:
        fail(f"bioactivity row count {len(bio)} != substrate bioactivity_assertion count {expected_bio}")

    # (7) edge_id round-trip: every enrichment edge_id exists in substrate
    substrate_ids = set(he["edge_id"])
    if not set(enr["edge_id"]).issubset(substrate_ids):
        fail("enrichment edge_ids include ids not in substrate")
    if not set(bio["edge_id"]).issubset(substrate_ids):
        fail("bioactivity edge_ids include ids not in substrate")

    # (8) sovereignty audit zero failures
    sov_audit_path = T5 / "sovereignty_field_audit.tsv"
    if sov_audit_path.exists():
        sov = pd.read_csv(sov_audit_path, sep="\t")
        if (sov["total_missing_field_failures"] > 0).any():
            fail("sovereignty audit reports nonzero missing-required-field rows")
    else:
        fail("sovereignty_field_audit.tsv missing")

    # (9) no chemodiversity_signature edges anywhere in track5 outputs
    if (enr["edge_type"] == "chemodiversity_signature").any():
        fail("chemodiversity_signature edges present in enrichment view — prohibited at Wave 2")

    print(
        f"PASS: track5 enrichment ({len(enr)} resolved phyto+ethno rows; {len(bio)} compound-level "
        f"bioactivity rows; sovereignty zero-missing)."
    )


if __name__ == "__main__":
    main()
