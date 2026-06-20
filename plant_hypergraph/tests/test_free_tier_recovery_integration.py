#!/usr/bin/env python3
# created: 2026-05-18T21:40:00+00:00
# cycle: 28
# run_id: run-phytograph-cycle28-free-tier-recovery-integration
# agent: worker
# milestone: _plan/free-tier-recovery-integration

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
STATUS = ROOT / "data/reopen/reopen_closure_status.tsv"
REPORT = ROOT / "reports/reopen/free_tier_recovery_integration.md"
PREDICTION_LEDGER = ROOT / "prediction_ledger.tsv"
SPECULATION_LEDGER = ROOT / "speculation_ledger.tsv"


def test_free_tier_statuses_reconcile_branch_outcomes():
    df = pd.read_csv(STATUS, sep="\t", dtype=str)
    status = dict(zip(df["track"], df["result"]))
    assert status["Track 1"] == "branch_local_threshold_met_reconciliation_pending"
    assert status["Track 4"] == "still_data_limited"
    assert status["Track 5"] == "insufficient_non_duke_temporal_evidence_h5_remains_source_biased"
    assert status["Track 6"] == "no_new_qualifying_evidence"
    assert "reconciliation_pending_non_promotion" in df[df["track"] == "Track 1"]["master_ledger_action"].iloc[0]


def test_integration_report_preserves_conflict_boundary():
    text = REPORT.read_text(encoding="utf-8")
    assert "22 distinct accepted-key taxa" in text
    assert "GBIF accepted keys are reconciled against the frozen WFO-oriented accepted-key namespace" in text
    assert "0 numeric BIOCLIM vectors" in text
    assert "two accepted-key manual non-Duke candidates" in text
    assert "No master prediction or speculation row" not in text
    assert "validated prediction" not in text


def test_master_ledgers_remain_header_only_after_free_tier_merge():
    assert len(PREDICTION_LEDGER.read_text(encoding="utf-8").splitlines()) == 1
    assert len(SPECULATION_LEDGER.read_text(encoding="utf-8").splitlines()) == 1
