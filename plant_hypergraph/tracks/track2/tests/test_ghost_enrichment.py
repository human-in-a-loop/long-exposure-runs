from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "tracks" / "track2" / "data"


def test_seed_edges_are_not_predictions():
    df = pd.read_parquet(DATA / "ghost_partner_seed_edges.parquet")
    assert len(df) == 31
    assert set(df["prediction_status"]) == {"not_prediction"}
    assert not df["enters_prediction_ledger"].astype(bool).any()
    assert not df["inferred_anachronism_claim"].astype(bool).any()
    assert not df["inferred_flag"].astype(bool).any()


def test_seed_edges_preserve_citation_and_scope():
    df = pd.read_parquet(DATA / "ghost_partner_seed_edges.parquet")
    assert (df["primary_citation_short"].str.len() > 0).all()
    assert (df["primary_citation_page"].str.len() > 0).all()
    assert df["allowed_evidence_scope"].str.contains("cited hypothesis only").all()
    assert df["interpretation_caveat"].str.contains("NOT established anachronism").all()


def test_seed_edges_have_schema_roles_and_candidate_classes():
    df = pd.read_parquet(DATA / "ghost_partner_seed_edges.parquet")
    assert set(df["edge_type"]) == {"anachronism_candidate_edge"}
    assert (df["plant_node_id"].str.len() > 0).all()
    assert (df["fruit_type_node_id"].str.len() > 0).all()
    assert (df["extinct_fauna_node_id"].str.len() > 0).all()
    assert df["candidate_class"].nunique() >= 5


def test_pending_crosswalk_is_retained_not_resolved_locally():
    df = pd.read_parquet(DATA / "ghost_partner_seed_edges.parquet")
    assert int(df["pending_crosswalk"].sum()) == 25
    pending = df[df["pending_crosswalk"]]
    assert pending["accepted_taxon_key"].fillna("").eq("").all()
    assert pending["caveats"].str.contains("canonicalization_status=unresolved").all()


def test_support_context_is_track_local_and_nonpredictive():
    support = pd.read_parquet(DATA / "ghost_partner_support_nodes.parquet")
    ranges = pd.read_parquet(DATA / "ghost_partner_range_context_edges.parquet")
    assert {"extinct_fauna", "paleo_context", "animal_consumer"}.issubset(
        set(support["node_type"])
    )
    assert len(ranges) == 52
    assert set(ranges["prediction_status"]) == {"not_prediction"}
    assert not ranges["enters_prediction_ledger"].astype(bool).any()
