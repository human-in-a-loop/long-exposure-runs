# created: 2026-05-18T09:10:00+00:00
# cycle: 13
# run_id: run-phytograph-cycle13-source-branch-disposition
# agent: worker
# milestone: _plan/source-branch-disposition-m1-3-m1-6

import csv
import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DISPOSITION = ROOT / "data" / "source_branch_disposition_m1_3_m1_6.tsv"
REPORT = ROOT / "reports" / "source_branch_disposition_m1_3_m1_6.md"


def read_rows():
    with DISPOSITION.open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def test_disposition_rows_exist_for_m1_3_and_m1_6():
    rows = {row["milestone_id"]: row for row in read_rows()}
    assert set(rows) == {"M1.3", "M1.6"}
    assert REPORT.exists()


def test_disposition_rows_have_mechanisms_and_reopen_conditions():
    for row in read_rows():
        assert row["mechanism"].strip()
        assert row["terminal_status"] == "deferred_terminal_data_limited"
        assert row["reopen_condition"].strip()
        assert "tracks/track" in row["downstream_artifacts"]
        assert "data/barrier3_atlas_instrument_contract.tsv" in row["downstream_artifacts"]


def test_master_prediction_and_speculation_ledgers_remain_header_only():
    for rel in ("prediction_ledger.tsv", "speculation_ledger.tsv"):
        lines = (ROOT / rel).read_text(encoding="utf-8").splitlines()
        assert len(lines) == 1
        assert lines[0].strip()


def test_barrier3_contract_counts_remain_unchanged():
    with (ROOT / "data" / "barrier3_atlas_instrument_contract.json").open(encoding="utf-8") as fh:
        contract = json.load(fh)
    rows = {row["track"]: row for row in contract["tracks"]}
    assert (rows["Track 1"]["source_rows"], rows["Track 1"]["atlas_projected_rows"], rows["Track 1"]["taxon_pages_with_rows"]) == (60000, 60000, 60000)
    assert (rows["Track 4"]["source_rows"], rows["Track 4"]["atlas_projected_rows"], rows["Track 4"]["taxon_pages_with_rows"]) == (3, 6, 5)


def test_frozen_substrate_counts_remain_unchanged():
    nodes = pd.read_parquet(ROOT / "phytograph_dataset" / "nodes.parquet")
    edges = pd.read_parquet(ROOT / "phytograph_dataset" / "hyperedges.parquet")
    assert len(nodes) == 363237
    assert len(edges) == 641183
