#!/usr/bin/env python3
# created: 2026-05-18T21:05:00+00:00
# cycle: 28
# run_id: run-phytograph-cycle28-track1-free-tier-reticulation-recovery
# agent: worker
# milestone: _plan/track1-free-tier-reticulation-recovery
"""Tests for the Track 1 free-tier reticulation recovery branch."""
from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PANEL = ROOT / "tracks" / "track1" / "data" / "free_tier_reticulation_panel.tsv"
EVIDENCE = ROOT / "tracks" / "track1" / "data" / "free_tier_reticulation_evidence.tsv"
DIAG = ROOT / "tracks" / "track1" / "data" / "free_tier_reticulation_join_diagnostics.tsv"
REPORT = ROOT / "tracks" / "track1" / "reports" / "track1_free_tier_reticulation_recovery.md"
FIGURE = ROOT / "tracks" / "track1" / "figures" / "free_tier_reticulation_recovery_matrix.png"
PREDICTION_LEDGER = ROOT / "prediction_ledger.tsv"
SPECULATION_LEDGER = ROOT / "speculation_ledger.tsv"


def test_panel_size_roles_and_accepted_key_attempts():
    panel = pd.read_csv(PANEL, sep="\t").fillna("")
    assert 30 <= len(panel) <= 50
    assert (panel["accepted_key"] != "").all()
    assert (panel["panel_role"] == "canonical_positive").sum() >= 20
    assert (panel["panel_role"] == "matched_control").sum() >= 10
    assert (panel["matched_control_for"] != "").sum() >= 10


def test_evidence_columns_threshold_and_independent_sources():
    evidence = pd.read_csv(EVIDENCE, sep="\t").fillna("")
    required = [
        "input_name",
        "accepted_key",
        "accepted_name",
        "family",
        "evidence_class",
        "event_shape",
        "parent_taxa_named",
        "ploidy_or_chromosome_evidence",
        "source_title",
        "source_url_or_doi",
        "source_type",
        "source_year",
        "independent_source_group",
        "license_or_access_note",
        "join_status",
        "support_status",
        "caveat",
    ]
    assert list(evidence.columns) == required
    usable = evidence[evidence["support_status"] == "accepted_key_event_shaped"]
    parent_named = usable["parent_taxa_named"].astype(str).str.lower() == "true"
    ploidy_supported = usable["ploidy_or_chromosome_evidence"].astype(str).str.lower() == "true"
    assert usable["input_name"].nunique() >= 15
    assert usable[parent_named | ploidy_supported]["input_name"].nunique() >= 8
    assert usable["independent_source_group"].nunique() >= 3
    assert (usable["source_url_or_doi"].str.len() > 10).all()


def test_controls_lower_than_canonical_event_recovery():
    panel = pd.read_csv(PANEL, sep="\t").fillna("")
    positives = panel[panel["panel_role"] == "canonical_positive"]
    controls = panel[panel["panel_role"] == "matched_control"]
    positive_rate = (positives["usable_event_shaped_evidence_count"] > 0).mean()
    control_rate = (controls["usable_event_shaped_evidence_count"] > 0).mean()
    assert positive_rate >= 0.65
    assert control_rate <= 0.15
    assert positive_rate - control_rate >= 0.50


def test_diagnostics_cover_four_source_groups_per_taxon():
    panel = pd.read_csv(PANEL, sep="\t").fillna("")
    diag = pd.read_csv(DIAG, sep="\t").fillna("")
    assert len(diag) == len(panel) * 4
    assert set(diag["source_group"]) == {
        "gbif_species_api",
        "crossref_metadata",
        "openalex_metadata",
        "curated_open_literature",
    }
    assert (diag[diag["source_group"] == "gbif_species_api"]["accepted_key_match"].astype(str).str.lower() == "true").all()


def test_report_figure_and_ledgers_are_conservative():
    text = REPORT.read_text()
    assert "determination: `threshold_met`" in text
    assert "branch-local" in text
    assert "no master prediction or speculation row" in text
    assert "new hybridization discovered" not in text
    assert "validated prediction" not in text
    assert FIGURE.exists() and FIGURE.stat().st_size > 1000
    assert len(PREDICTION_LEDGER.read_text().splitlines()) == 1
    assert len(SPECULATION_LEDGER.read_text().splitlines()) == 1
