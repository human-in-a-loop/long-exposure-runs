"""
Tests for the Botanical Atlas Wave-3 builder (M3.A).

Header metadata:
  created: 2026-05-18T03:15:00+00:00
  cycle: 9
  run_id: run-phytograph-cycle9-wave3-atlas
  agent: worker
  milestone: M3.A
"""

from __future__ import annotations

import importlib
import json
import sys
import uuid
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "botanical_atlas_site"))
sys.path.insert(0, str(REPO / "tools"))

import build_atlas  # noqa: E402
import file_counter_claim as cc  # noqa: E402


# --------------------------------------------------------------------------
# Build a small subset Atlas once, share across tests
# --------------------------------------------------------------------------
@pytest.fixture(scope="module")
def small_atlas(tmp_path_factory):
    out = tmp_path_factory.mktemp("atlas_subset")
    build_atlas.SITE = out
    build_atlas.PAGES = out / "pages"
    sub = build_atlas.load_substrate()
    probe6 = build_atlas.load_track6_probes()
    instr = build_atlas.detect_wave3_instruments()
    preds = build_atlas.load_instrument_predictions()
    idx = build_atlas.build_taxon_index(
        sub["nodes"], sub["crosswalk"], sub["synonyms"])
    # Include taxa that exercise the Track 1-6 adapters; the first 100
    # accepted keys alone are not guaranteed to contain sparse prediction rows.
    adapter_keys = set()
    for track_rows in preds.values():
        adapter_keys.update(list(track_rows.keys())[:25])
    idx = idx[
        idx["accepted_taxon_key"].isin(adapter_keys) |
        idx["accepted_taxon_key"].isin(set(idx.head(100)["accepted_taxon_key"]))
    ].copy()
    cov, search = build_atlas.build_pages(
        idx, sub["edges"], probe6, instr, preds, limit=None)
    return {"out": out, "coverage": cov, "search": search, "pages": idx.head(100)}


# --------------------------------------------------------------------------
# Page-contract assertions
# --------------------------------------------------------------------------

def test_every_page_has_six_track_sections(small_atlas):
    pages = list((small_atlas["out"] / "pages").glob("*.json"))
    assert len(pages) >= 50, f"expected >=50 pages, got {len(pages)}"
    for p in pages[:25]:
        page = json.loads(p.read_text())
        assert set(page["tracks"].keys()) == {1, 2, 3, 4, 5, 6} or \
               set(int(k) for k in page["tracks"].keys()) == {1, 2, 3, 4, 5, 6}
        for t in page["tracks"].values():
            assert t["state"] in {"observed", "enriched",
                                  "predicted", "data-limited"}


def test_observed_band_never_cites_inferred_edges(small_atlas):
    """Falsifier (b): no OBSERVED row carries inferred_flag=True."""
    for p in (small_atlas["out"] / "pages").glob("*.json"):
        page = json.loads(p.read_text())
        for sec in page["tracks"].values():
            for row in sec.get("observed", []):
                assert not row.get("inferred_flag"), \
                    f"OBSERVED row {row['edge_id']} carries inferred_flag=True"


def test_predicted_rows_have_confidence(small_atlas):
    """Falsifier (a): every PREDICTED row has a non-null confidence
    OR is rendered via an instrument_pending placeholder."""
    for p in (small_atlas["out"] / "pages").glob("*.json"):
        page = json.loads(p.read_text())
        for sec in page["tracks"].values():
            for row in sec.get("predicted", []):
                assert row.get("confidence") is not None, \
                    f"PREDICTED row {row['edge_id']} missing confidence"


def test_instrument_pending_is_visible(small_atlas):
    """Falsifier (e): merged Wave-3 instrument adapters should not remain
    visible as stale placeholder contracts."""
    for p in (small_atlas["out"] / "pages").glob("*.json"):
        page = json.loads(p.read_text())
        for tid, sec in page["tracks"].items():
            if int(tid) in {1, 3}:
                assert sec["instrument_pending"] is False
                assert sec["instrument_mode"] == "prediction_adapter"
            assert sec["instrument_expected_files"], \
                f"track {tid} has no expected instrument files declared"


def test_existing_track_outputs_are_exposed_as_predictions(small_atlas):
    seen = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0}
    for p in (small_atlas["out"] / "pages").glob("*.json"):
        page = json.loads(p.read_text())
        for tid in seen:
            seen[tid] += len(page["tracks"][str(tid)]["predicted"])
    assert seen[1] > 0, "Track 1 TCI adapter emitted no predictions"
    assert seen[2] > 0, "Track 2 ghost-partner adapter emitted no predictions"
    assert seen[3] > 0, "Track 3 convergence adapter emitted no predictions"
    assert seen[4] > 0, "Track 4 crop-substitution adapter emitted no predictions"
    assert seen[5] > 0, "Track 5 chemodiversity adapter emitted no predictions"
    assert seen[6] > 0, "Track 6 offline-probe adapter emitted no predictions"


def test_every_edge_has_provenance(small_atlas):
    for p in (small_atlas["out"] / "pages").glob("*.json"):
        page = json.loads(p.read_text())
        for sec in page["tracks"].values():
            for klass in ("observed", "enriched", "predicted"):
                for row in sec.get(klass, []):
                    # provenance_pointer OR license OR source_record_id
                    has_prov = any([row.get("provenance_pointer"),
                                    row.get("license"),
                                    row.get("source_record_id")])
                    assert has_prov, f"row {row['edge_id']} has no provenance"


# --------------------------------------------------------------------------
# Search index round-trip
# --------------------------------------------------------------------------

def test_search_index_roundtrip(small_atlas):
    rows = small_atlas["search"]
    assert len(rows) >= 50
    sample = rows[0]
    for required_key in ("k", "n", "u"):
        assert required_key in sample
    # The url slug must address a file on disk
    assert (small_atlas["out"] / "pages" / f"{sample['u']}.json").exists()


# --------------------------------------------------------------------------
# Counter-claim CLI
# --------------------------------------------------------------------------

def test_counter_claim_rejects_missing_target(tmp_path):
    bad = {"accepted_taxon_key": "wfo:wfo-x", "target_kind": "observed_row",
           "reviewer_id": "email:test@example.org", "comment": "no target"}
    with pytest.raises(cc.CounterClaimError):
        cc.validate(bad)


def test_counter_claim_rejects_empty_comment(tmp_path):
    bad = {"accepted_taxon_key": "wfo:wfo-x", "target_edge_id": "e1",
           "target_kind": "observed_row",
           "reviewer_id": "email:test@example.org", "comment": ""}
    with pytest.raises(cc.CounterClaimError):
        cc.validate(bad)


def test_counter_claim_round_trip(tmp_path):
    jsonl = tmp_path / "cc.jsonl"
    payload = {
        "accepted_taxon_key": "wfo:wfo-0000519676-2025-12",
        "target_edge_id":
            "AnachronismCanon:edge:Adansonia_grandidieri::Aepyornis_maximus::Bond&Silander2007",
        "target_kind": "enriched_row",
        "reviewer_id": "email:reviewer@example.org",
        "comment": "Question: is the cited disperser plausibly the *primary* "
                   "agent given current secondary dispersers documented in "
                   "Madagascar?",
    }
    rc = cc.main(["--inline", json.dumps(payload), "--no-ledger",
                  "--jsonl", str(jsonl)])
    assert rc == 0
    lines = jsonl.read_text().strip().split("\n")
    assert len(lines) == 1
    rec = json.loads(lines[0])
    assert rec["target_edge_id"] == payload["target_edge_id"]
    assert "counter_claim_id" in rec
    assert "iso_timestamp" in rec
