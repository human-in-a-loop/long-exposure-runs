#!/usr/bin/env python3
# created: 2026-05-18T16:05:00+00:00
# cycle: 23
# run_id: run-phytograph-cycle23-track1-reopen-reticulation-evidence
# agent: worker
# milestone: _plan/track1-reticulation-reopen-evidence
"""Tests for the Track 1 accepted-key reticulation reopen package."""
from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CANDIDATES = ROOT / "tracks" / "track1" / "data" / "reticulation_reopen_candidate_events.tsv"
DIAGNOSTICS = ROOT / "tracks" / "track1" / "data" / "reticulation_reopen_join_diagnostics.tsv"
REPORT = ROOT / "tracks" / "track1" / "reports" / "track1_reopen_reticulation_evidence.md"
FIGURE = ROOT / "tracks" / "track1" / "figures" / "reticulation_reopen_join_recovery.png"
PREDICTION_LEDGER = ROOT / "prediction_ledger.tsv"
SPECULATION_LEDGER = ROOT / "speculation_ledger.tsv"

REQUIRED_CANDIDATE_COLUMNS = [
    "source_id",
    "source_name",
    "raw_taxon_name",
    "accepted_key",
    "accepted_name",
    "event_type",
    "evidence_scope",
    "event_shape_status",
    "provenance_url_or_path",
    "license_or_access_note",
    "supporting_text_snippet",
    "join_method",
    "caveat",
]

REQUIRED_DIAGNOSTIC_COLUMNS = [
    "source_name",
    "candidate_rows",
    "accepted_key_rows",
    "event_shaped_rows",
    "exact_name_joins",
    "synonym_rescue_joins",
    "rejected_rows",
    "dominant_rejection_reason",
]

ALLOWED_EVENT_TYPES = {
    "chromosome_count_assertion",
    "hybridization_event",
    "ploidy_state_assertion",
    "polyploidization_event",
    "reticulate_inheritance_evidence",
}

ALLOWED_STATUSES = {
    "chromosome_count_only",
    "event_shaped",
    "ploidy_context_only",
    "rejected_no_accepted_key",
}


def test_reopen_tables_have_required_columns_and_values():
    candidates = pd.read_csv(CANDIDATES, sep="\t").fillna("")
    diagnostics = pd.read_csv(DIAGNOSTICS, sep="\t").fillna("")
    assert list(candidates.columns) == REQUIRED_CANDIDATE_COLUMNS
    assert list(diagnostics.columns) == REQUIRED_DIAGNOSTIC_COLUMNS
    assert set(candidates["event_type"]).issubset(ALLOWED_EVENT_TYPES)
    assert set(candidates["event_shape_status"]).issubset(ALLOWED_STATUSES)
    assert (candidates["source_id"] != "").all()
    assert (candidates["provenance_url_or_path"] != "").all()
    assert (candidates["license_or_access_note"] != "").all()


def test_inferred_synonym_and_rejected_rows_have_caveats():
    candidates = pd.read_csv(CANDIDATES, sep="\t").fillna("")
    caveated = candidates[
        candidates["join_method"].str.contains("synonym|rejected", regex=True)
        | candidates["event_shape_status"].isin(["chromosome_count_only", "ploidy_context_only"])
    ]
    assert not caveated.empty
    assert (caveated["caveat"].str.len() > 20).all()


def test_event_shaped_counts_are_accepted_key_only_and_below_reopen_threshold():
    candidates = pd.read_csv(CANDIDATES, sep="\t").fillna("")
    diagnostics = pd.read_csv(DIAGNOSTICS, sep="\t").fillna("")
    accepted_events = candidates[
        (candidates["accepted_key"] != "") & (candidates["event_shape_status"] == "event_shaped")
    ]
    assert len(accepted_events) == int(diagnostics["event_shaped_rows"].sum())
    assert accepted_events["raw_taxon_name"].nunique() == 3
    assert accepted_events[accepted_events["join_method"] == "exact_name_full_wfo"]["raw_taxon_name"].nunique() == 2
    assert accepted_events["source_name"].nunique() == 1
    assert len(accepted_events) < 30


def test_report_threshold_statement_is_backed_by_diagnostics():
    text = REPORT.read_text()
    diagnostics = pd.read_csv(DIAGNOSTICS, sep="\t").fillna("")
    event_rows = int(diagnostics["event_shaped_rows"].sum())
    exact_rows = int(diagnostics["exact_name_joins"].sum())
    synonym_rows = int(diagnostics["synonym_rescue_joins"].sum())
    assert FIGURE.exists() and FIGURE.stat().st_size > 1000
    assert "determination: `evidence_added_but_threshold_not_met`" in text
    assert "reopen_threshold_met" not in text.split("determination:", 1)[1].splitlines()[0]
    assert event_rows == 6
    assert exact_rows == 13
    assert synonym_rows == 4
    assert "3 accepted-key taxa" in text
    assert "single Wood 2009 source" in text


def test_master_prediction_and_speculation_ledgers_remain_header_only():
    assert len(PREDICTION_LEDGER.read_text().splitlines()) == 1
    assert len(SPECULATION_LEDGER.read_text().splitlines()) == 1
