#!/usr/bin/env python3
# created: 2026-05-18T22:20:00+00:00
# cycle: 29
# run_id: run-phytograph-cycle29-track1-free-tier-namespace-reconciliation
# agent: worker
# milestone: _plan/track1-free-tier-namespace-reconciliation
"""Tests for Track 1 GBIF-to-WFO namespace reconciliation."""
from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CROSSWALK = ROOT / "tracks" / "track1" / "data" / "free_tier_reticulation_namespace_crosswalk.tsv"
EVIDENCE = ROOT / "tracks" / "track1" / "data" / "free_tier_reticulation_reconciled_evidence.tsv"
CONTROLS = ROOT / "tracks" / "track1" / "data" / "free_tier_reticulation_reconciled_controls.tsv"
REPORT = ROOT / "tracks" / "track1" / "reports" / "track1_free_tier_namespace_reconciliation.md"
FIGURE = ROOT / "tracks" / "track1" / "figures" / "track1_free_tier_namespace_reconciliation.png"
PREDICTION_LEDGER = ROOT / "prediction_ledger.tsv"
SPECULATION_LEDGER = ROOT / "speculation_ledger.tsv"


def test_crosswalk_schema_and_all_22_gbif_taxa_accounted_for():
    df = pd.read_csv(CROSSWALK, sep="\t").fillna("")
    assert list(df.columns) == [
        "gbif_taxon_key",
        "gbif_scientific_name",
        "gbif_status",
        "gbif_rank",
        "wfo_candidate_key",
        "wfo_candidate_name",
        "match_type",
        "match_confidence",
        "accepted_key_basis",
        "crosswalk_status",
        "rejection_reason",
        "source_url",
        "access_date",
    ]
    assert len(df) == 22
    assert df["gbif_taxon_key"].nunique() == 22
    assert set(df["accepted_key_basis"]) == {"wfo_projected", "gbif_sidecar"}


def test_wfo_projected_sidecar_and_unresolved_rows_are_labeled():
    crosswalk = pd.read_csv(CROSSWALK, sep="\t").fillna("")
    projected = crosswalk[crosswalk["accepted_key_basis"] == "wfo_projected"]
    sidecar = crosswalk[crosswalk["accepted_key_basis"] == "gbif_sidecar"]
    assert len(projected) >= 1
    assert (projected["wfo_candidate_key"].str.startswith("wfo:")).all()
    assert (projected["wfo_candidate_name"] != "").all()
    assert len(sidecar) >= 15
    assert (sidecar["crosswalk_status"] == "gbif_sidecar_admitted").all()
    assert (sidecar["rejection_reason"] != "").all()


def test_reconciled_evidence_preserves_threshold_counts_and_rejections():
    evidence = pd.read_csv(EVIDENCE, sep="\t").fillna("")
    retained = evidence[evidence["validation_use"] == "track1_readiness_diagnostic"]
    rejected = evidence[evidence["accepted_key_basis"] == "rejected"]
    assert len(evidence) == 24
    assert retained["gbif_taxon_key"].nunique() == 22
    assert retained["source_group"].nunique() == 11
    assert set(retained["accepted_key_basis"]).issubset({"wfo_projected", "gbif_sidecar"})
    assert (retained["no_promotion_flag"].astype(str).str.lower() == "true").all()
    assert len(rejected) >= 1
    assert (rejected["rejection_reason"] != "").all()


def test_controls_remain_represented_and_unrecovered():
    controls = pd.read_csv(CONTROLS, sep="\t").fillna("")
    assert len(controls) == 17
    assert set(controls["accepted_key_basis"]) == {"gbif_control_basis"}
    assert controls["usable_event_shaped_evidence_count"].astype(int).sum() == 0
    assert set(controls["control_recovered"].astype(str).str.lower()) == {"false"}


def test_report_figure_and_master_ledgers_are_conservative():
    text = REPORT.read_text(encoding="utf-8")
    assert "wfo_projected_evidence" in text
    assert "gbif_sidecar_evidence" in text
    assert "rejected_or_unresolved_evidence" in text
    assert "WFO projection alone is insufficient" in text
    assert "no master prediction or speculation row" in text
    assert "validated reticulation prediction" not in text
    assert FIGURE.exists() and FIGURE.stat().st_size > 1000
    assert len(PREDICTION_LEDGER.read_text(encoding="utf-8").splitlines()) == 1
    assert len(SPECULATION_LEDGER.read_text(encoding="utf-8").splitlines()) == 1
