#!/usr/bin/env python3
"""Regression tests for Track 1 Barrier 4 accepted-key recovery closure."""
from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "tracks" / "track1" / "scripts" / "track1_barrier4_key_recovery.py"
RECOVERY = ROOT / "tracks" / "track1" / "data" / "barrier4_canonical_key_recovery.tsv"
RESCUED = ROOT / "tracks" / "track1" / "data" / "barrier4_rescued_reticulation_edges.tsv"
STATUS = ROOT / "tracks" / "track1" / "data" / "canonical_seed_case_status.tsv"
REPORT = ROOT / "tracks" / "track1" / "reports" / "track1_barrier4_closure.md"

FROZEN_INPUTS = [
    ROOT / "substrate" / "staging" / "taxonomy_backbone" / "accepted_taxa.parquet",
    ROOT / "substrate" / "staging" / "taxonomy_backbone" / "synonym_clusters.parquet",
    ROOT / "phytograph_dataset" / "nodes.parquet",
    ROOT / "phytograph_dataset" / "hyperedges.parquet",
]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def run_script() -> None:
    subprocess.run(["python3", str(SCRIPT)], cwd=ROOT, check=True)


def test_script_does_not_mutate_frozen_substrate_files():
    before = {path: sha256(path) for path in FROZEN_INPUTS}
    run_script()
    after = {path: sha256(path) for path in FROZEN_INPUTS}
    assert before == after


def test_current_accepted_subset_statuses_are_reproduced():
    run_script()
    recovery = pd.read_csv(RECOVERY, sep="\t").fillna("")
    current = pd.read_csv(STATUS, sep="\t").fillna("")
    expected = dict(zip(current["canonical_seed_taxon"], current["status"]))
    for seed, status in expected.items():
        observed = recovery.loc[recovery["seed_taxon"] == seed, "current_status"].iloc[0]
        assert observed == status
    assert (recovery["current_accepted_key"] == "").all()


def test_full_wfo_rescue_statuses_are_deterministic():
    run_script()
    recovery = pd.read_csv(RECOVERY, sep="\t").fillna("")
    statuses = dict(zip(recovery["seed_taxon"], recovery["rescue_status"]))
    assert statuses == {
        "Triticum aestivum": "rescued_exact_full_wfo_taxon",
        "Brassica napus": "rescued_exact_full_wfo_taxon",
        "Spartina anglica": "rescued_synonym_to_full_wfo_taxon",
        "Tragopogon mirus": "not_recovered_absent_from_full_wfo",
        "Tragopogon miscellus": "not_recovered_absent_from_full_wfo",
        "Musa acuminata × balbisiana": "not_recovered_absent_from_full_wfo",
        "Musa acuminata": "rescued_exact_full_wfo_taxon",
        "Musa balbisiana": "rescued_exact_full_wfo_taxon",
    }
    assert (recovery["rescued_accepted_key"].fillna("") != "").sum() == 5
    assert (
        (recovery["rescued_accepted_key"].fillna("") != "")
        & (recovery["event_shaped_edges_attached"].astype(int) > 0)
    ).sum() == 3


def test_chromosome_and_ploidy_rows_are_not_promoted_to_event_evidence():
    run_script()
    rescued = pd.read_csv(RESCUED, sep="\t").fillna("")
    non_events = rescued[rescued["edge_type"].isin(["chromosome_count_assertion", "ploidy_state_assertion"])]
    assert not non_events.empty
    assert set(non_events["event_shaped_edge"].astype(str).str.lower()) == {"false"}
    events = rescued[rescued["edge_type"].isin(["hybridization_event", "polyploidization_event"])]
    assert set(events["event_shaped_edge"].astype(str).str.lower()) == {"true"}


def test_report_keeps_h1_data_limited_below_validation_threshold():
    run_script()
    text = REPORT.read_text()
    assert "H1 closure status: `data-limited`" in text
    assert "Validation threshold for closure refinement: at least 5 canonical seeds" in text
    recovery = pd.read_csv(RECOVERY, sep="\t").fillna("")
    canonical_event_rescued = (
        (recovery["rescued_accepted_key"] != "")
        & (recovery["event_shaped_edges_attached"].astype(int) > 0)
    ).sum()
    assert canonical_event_rescued < 5
