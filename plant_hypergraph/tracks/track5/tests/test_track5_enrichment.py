#!/usr/bin/env python3
"""Pytest cases for Track 5 enrichment projection."""
from __future__ import annotations
from pathlib import Path
import json
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[3]
T5 = ROOT / "tracks" / "track5" / "data"

REQUIRED_ENR_COLS = {
    "edge_id", "edge_type", "accepted_taxon_key", "family", "compound_id", "compound_class",
    "plant_part", "source_id", "source_class", "license", "access_date", "evidence_scope",
    "sovereignty_fields_json", "retained", "pending_crosswalk",
}
ALLOWED_SCOPES = {
    "phytochemical_assertion": {
        "Supports detection of this compound in this raw taxon label by this source.",
    },
    "ethnobotanical_use_assertion": {
        "Supports recorded human-use label in this source.",
        "Supports recorded use by the named people group as represented in NAEB.",
    },
}


@pytest.fixture(scope="module")
def enr() -> pd.DataFrame:
    return pd.read_parquet(T5 / "track5_enrichment_edges.parquet")


@pytest.fixture(scope="module")
def bio() -> pd.DataFrame:
    return pd.read_parquet(T5 / "track5_bioactivity_assertions.parquet")


def test_required_columns_present(enr):
    missing = REQUIRED_ENR_COLS - set(enr.columns)
    assert not missing, f"missing enrichment columns: {missing}"


def test_no_pending_crosswalk(enr):
    assert not enr["pending_crosswalk"].any()


def test_no_blank_accepted_keys(enr):
    assert (enr["accepted_taxon_key"].fillna("") != "").all()


def test_allowed_evidence_scope(enr):
    for et, scopes in ALLOWED_SCOPES.items():
        sub = enr[enr["edge_type"] == et]
        assert sub["evidence_scope"].isin(scopes).all(), f"out-of-schema evidence_scope in {et}"


def test_bioactivity_is_compound_keyed(bio):
    # firewall: no taxon-keyed column on bioactivity
    assert "accepted_taxon_key" not in bio.columns
    assert bio["compound_id"].notna().all()
    # evidence_scope must explicitly disclaim clinical efficacy
    assert (bio["evidence_scope"].str.contains("does not support clinical efficacy")).all()


def test_no_chemodiversity_signature_edges_emitted(enr):
    assert not (enr["edge_type"] == "chemodiversity_signature").any()


def test_dr_duke_dominance_audit_well_formed():
    duke = pd.read_csv(T5 / "dr_duke_dominance_audit.tsv", sep="\t")
    assert len(duke) > 0
    assert ((duke["duke_share"] >= 0) & (duke["duke_share"] <= 1)).all()


def test_loso_duke_removal_is_non_trivial():
    """Sanity check, NOT a normative claim: removing Duke should demote at least one family-cell."""
    loso = pd.read_csv(T5 / "leave_one_source_out_coverage.tsv", sep="\t")
    duke_row = loso[loso["source_dropped"].str.contains("Duke", na=False)]
    assert len(duke_row) == 1
    assert int(duke_row["n_family_cells_demoted_below_floor"].iloc[0]) >= 1


def test_sovereignty_audit_zero_failures():
    sov = pd.read_csv(T5 / "sovereignty_field_audit.tsv", sep="\t")
    assert (sov["total_missing_field_failures"] == 0).all()


def test_substrate_is_read_only(tmp_path, monkeypatch):
    """Guard: importing/running the projection must not write under phytograph_dataset/."""
    import os
    sub = ROOT / "phytograph_dataset"
    mtimes_before = {p: p.stat().st_mtime_ns for p in sub.iterdir() if p.is_file()}
    # importlib re-runs side-effect-free imports only; we don't invoke main()
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "track5_project_enrichment_imp",
        str(ROOT / "tracks" / "track5" / "scripts" / "track5_project_enrichment.py"),
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mtimes_after = {p: p.stat().st_mtime_ns for p in sub.iterdir() if p.is_file()}
    assert mtimes_before == mtimes_after, "phytograph_dataset/ was modified during projection import"
