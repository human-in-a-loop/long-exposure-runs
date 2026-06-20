"""Validation checks for Track 4 domestication enrichment."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "tracks" / "track4" / "data"


def test_required_outputs_exist():
    required = [
        DATA / "domestication_enrichment_edges.parquet",
        DATA / "crop_cwr_coverage_summary.tsv",
        DATA / "heldout_validation_seed.tsv",
        DATA / "climate_envelope_coverage.tsv",
        DATA / "domestication_key_join_failures.tsv",
        DATA / "track4_enrichment_coverage.png",
        ROOT / "tracks" / "track4" / "docs" / "ENRICHMENT_AUDIT.md",
    ]
    missing = [str(p) for p in required if not p.exists()]
    assert not missing


def test_retained_edges_have_accepted_keys_and_track_namespace():
    edges = pd.read_parquet(DATA / "domestication_enrichment_edges.parquet")
    assert len(edges) > 0
    assert (edges["accepted_taxon_key"].fillna("").astype(str) != "").all()
    assert set(edges["source_group"]) == {"track4_domestication_enrichment"}
    assert not (ROOT / "phytograph_dataset" / "track4_domestication_enrichment_edges.parquet").exists()


def test_canonical_members_preserve_track4_roles():
    edges = pd.read_parquet(DATA / "domestication_enrichment_edges.parquet")
    for _, row in edges.iterrows():
        members = set(json.loads(row["canonical_node_ids_json"]))
        roles = json.loads(row["role_map_json"])
        assert row["accepted_taxon_key"] in members
        assert any(str(member).startswith("source:") for member in members)
        if row["edge_type"] == "crop_pedigree":
            assert roles.get("wild_ancestors")
            assert roles.get("selection_traits")
            assert any(str(member).startswith("wild_ancestor:") for member in members)
            assert any(str(member).startswith("selection_trait:") for member in members)
        if row["edge_type"] == "vavilov_center_hyperedge":
            assert roles.get("vavilov_center")
            assert any(str(member).startswith("vc:") for member in members)


def test_heldout_seed_is_disjoint_from_training_pedigree():
    heldout = pd.read_csv(DATA / "heldout_validation_seed.tsv", sep="\t", dtype=str, keep_default_na=False)
    assert len(heldout) > 0
    assert set(heldout["overlaps_training_pedigree"].astype(str)) <= {"False", "false"}


def test_climate_rows_are_observed_or_data_limited_only():
    climate = pd.read_csv(DATA / "climate_envelope_coverage.tsv", sep="\t", dtype=str, keep_default_na=False)
    assert len(climate) > 0
    assert set(climate["climate_evidence_status"]) <= {"observed", "data-limited"}
    assert "predicted" not in set(climate["climate_evidence_status"])
    data_limited = climate[climate["climate_evidence_status"] == "data-limited"]
    assert (data_limited["shortfall_reason"] != "").all()
