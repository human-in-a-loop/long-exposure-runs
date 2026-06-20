# created: 2026-05-17T21:35:00Z
# cycle: 4
# run_id: run-phytograph-cycle4-barrier1
# agent: worker
# milestone: _plan/barrier1-substrate-freeze

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from validate_barrier1_substrate import validate_edges_df, validate_heldout_leakage  # noqa: E402


def test_representative_wave1_rows_survive_with_provenance_and_scope():
    edges = pd.read_parquet(ROOT / "phytograph_dataset" / "hyperedges.parquet")
    for edge_type in ["taxonomic_parentage", "anachronism_candidate_edge", "trait_syndrome", "phytochemical_assertion"]:
        subset = edges[edges["edge_type"] == edge_type]
        assert len(subset) > 0
        assert subset["source_id"].astype(str).str.len().gt(0).all()
        assert subset["allowed_evidence_scope"].astype(str).str.len().gt(0).all()


def test_negative_missing_allowed_scope_fails():
    row = {
        "edge_id": "bad:scope",
        "edge_type": "trait_syndrome",
        "source_id": "test",
        "access_date": "2026-05-17",
        "license": "test",
        "provenance_pointer": "test",
        "allowed_evidence_scope": "",
        "caveats": "test",
        "inferred_flag": False,
    }
    assert any("allowed_evidence_scope" in err for err in validate_edges_df(pd.DataFrame([row])))


def test_negative_inferred_anachronism_fails():
    row = {
        "edge_id": "bad:anach",
        "edge_type": "anachronism_candidate_edge",
        "source_id": "test",
        "access_date": "2026-05-17",
        "license": "test",
        "provenance_pointer": "test",
        "allowed_evidence_scope": "source-stated assertion only",
        "caveats": "test",
        "inferred_flag": True,
    }
    assert any("inferred anachronism" in err for err in validate_edges_df(pd.DataFrame([row])))


def test_negative_image_biological_scope_fails():
    row = {
        "edge_id": "bad:image",
        "edge_type": "image_evidence",
        "source_id": "test",
        "access_date": "2026-05-17",
        "license": "CC-BY",
        "provenance_pointer": "test",
        "allowed_evidence_scope": "media_display;taxonomy",
        "caveats": "test",
        "inferred_flag": False,
    }
    assert any("image edge" in err for err in validate_edges_df(pd.DataFrame([row])))


def test_regression_no_convergence_signature_and_no_heldout_leakage():
    edges = pd.read_parquet(ROOT / "phytograph_dataset" / "hyperedges.parquet")
    assert int((edges["edge_type"] == "convergence_signature").sum()) == 0
    assert validate_heldout_leakage() == []

