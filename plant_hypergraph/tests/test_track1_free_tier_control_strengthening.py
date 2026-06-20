#!/usr/bin/env python3
# created: 2026-05-18T23:10:00+00:00
# cycle: 30
# run_id: run-phytograph-cycle30-track1-free-tier-control-strengthening
# agent: worker
# milestone: _plan/track1-free-tier-control-strengthening
"""Tests for Track 1 GBIF-sidecar control-strengthening package."""
from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PANEL = ROOT / "tracks" / "track1" / "data" / "free_tier_reticulation_control_panel.tsv"
DIAGNOSTICS = ROOT / "tracks" / "track1" / "data" / "free_tier_reticulation_control_diagnostics.tsv"
LOW_PUBLICATION = ROOT / "tracks" / "track1" / "data" / "free_tier_reticulation_low_publication_controls.tsv"
REPORT = ROOT / "tracks" / "track1" / "reports" / "track1_free_tier_control_strengthening.md"
FIGURE = ROOT / "tracks" / "track1" / "figures" / "track1_free_tier_control_recovery.png"
PREDICTION_LEDGER = ROOT / "prediction_ledger.tsv"
SPECULATION_LEDGER = ROOT / "speculation_ledger.tsv"


def test_control_panel_schema_and_22_event_taxa_retained():
    df = pd.read_csv(PANEL, sep="\t").fillna("")
    assert list(df.columns) == [
        "panel_role",
        "taxon_name",
        "namespace",
        "accepted_key",
        "family",
        "genus",
        "source_group_count",
        "evidence_row_count",
        "gbif_match_status",
        "wfo_projection_status",
        "name_turnover_proxy",
        "publication_proxy",
        "control_match_basis",
        "validation_use",
        "rejection_reason",
    ]
    cases = df[df["panel_role"] == "case_retained_sidecar_event"]
    assert len(cases) == 22
    assert cases["accepted_key"].nunique() == 22
    assert int(cases["evidence_row_count"].sum()) == 23
    assert set(cases["namespace"]).issubset({"gbif_sidecar", "wfo_projected"})


def test_controls_are_separated_by_match_basis_and_remain_unrecovered():
    df = pd.read_csv(PANEL, sep="\t").fillna("")
    controls = df[df["panel_role"].str.contains("control")]
    assert len(controls) >= 17
    assert {"genus_near", "family_near"}.issubset(set(controls["control_match_basis"]))
    assert controls["evidence_row_count"].astype(int).sum() == 0
    assert controls["gbif_match_status"].str.contains("ACCEPTED").all()


def test_diagnostics_include_required_confound_controls():
    diag = pd.read_csv(DIAGNOSTICS, sep="\t").fillna("")
    required = {
        "source_density_control",
        "publication_proxy_control",
        "family_size_control",
        "gbif_wfo_resolution_control",
        "low_publication_control_constructibility",
    }
    assert required.issubset(set(diag["diagnostic"]))
    assert set(diag["pass_fail"]).issubset({"pass", "fail"})
    source_density = diag.set_index("diagnostic").loc["source_density_control"]
    assert source_density["pass_fail"] == "fail"
    assert "targeted-source artifact risk" in source_density["caveat"]


def test_low_publication_controls_record_failures_explicitly():
    low = pd.read_csv(LOW_PUBLICATION, sep="\t").fillna("")
    assert len(low) >= 17
    assert {"candidate_status", "rejection_reason"}.issubset(set(low.columns))
    assert (low["candidate_status"] == "usable_low_publication_control").sum() >= 1
    rejected = low[low["candidate_status"] == "rejected_low_publication_control"]
    assert len(rejected) >= 1
    assert (rejected["rejection_reason"] != "").all()


def test_report_figure_and_master_ledgers_are_conservative():
    text = REPORT.read_text(encoding="utf-8")
    assert "Final status: `sidecar_readiness_uncontrolled`" in text
    assert "`sidecar_control_supported_readiness` is not assigned" in text
    assert "no master prediction or speculation row" in text
    assert "does not reopen WFO-based H1 validation" in text
    assert "validated reticulation prediction" not in text
    assert FIGURE.exists() and FIGURE.stat().st_size > 1000
    assert len(PREDICTION_LEDGER.read_text(encoding="utf-8").splitlines()) == 1
    assert len(SPECULATION_LEDGER.read_text(encoding="utf-8").splitlines()) == 1
