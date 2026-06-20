#!/usr/bin/env python3
"""Regression tests for the Track 1 Tree Compatibility Index instrument."""
from __future__ import annotations

import importlib.util
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = ROOT / "tracks" / "track1" / "instruments" / "build_tci.py"
OUT = ROOT / "tracks" / "track1" / "outputs"


def load_module():
    spec = importlib.util.spec_from_file_location("build_tci", str(MODULE_PATH))
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_ploidy_context_is_not_event_shaped_reticulation_evidence():
    mod = load_module()
    assert not mod.is_event_shaped_reticulation_edge(
        "reticulate_inheritance_evidence",
        '{"ploidy_state": "diploid", "taxon": "raw_name:Arabidopsis_thaliana"}',
    )
    assert mod.is_event_shaped_reticulation_edge(
        "reticulate_inheritance_evidence",
        '{"child_taxon": "raw_name:Triticum_aestivum", "parent_taxa": ["raw_name:Triticum_urartu"]}',
    )
    assert mod.is_event_shaped_reticulation_edge("polyploidization_event", "{}")


def test_tci_output_has_no_blank_accepted_key_and_preserves_bounds():
    df = pd.read_csv(OUT / "tci_per_taxon.tsv", sep="\t")
    assert df["accepted_key"].fillna("").ne("").all()
    assert df["tci"].between(0, 1).all()
    assert df["tci_observed"].between(0, 1).all()
    assert df["tci_structural"].between(0, 1).all()


def test_canonical_recovery_is_data_limited_not_validated():
    report = pd.read_csv(OUT / "canonical_recovery_report.tsv", sep="\t")
    core = report[
        report["taxon"].isin(
            [
                "Triticum aestivum",
                "Brassica napus",
                "Spartina anglica",
                "Tragopogon mirus",
                "Tragopogon miscellus",
                "Musa acuminata × balbisiana",
                "Musa acuminata",
                "Musa balbisiana",
            ]
        )
    ]
    assert len(core) == 8
    assert set(core["recovery_status"]) == {"data_limited"}


def test_evidence_partition_outputs_separate_resolved_from_pending_crosswalk():
    resolved = pd.read_csv(OUT / "accepted_key_resolved_reticulation_evidence.tsv", sep="\t")
    pending = pd.read_csv(OUT / "pending_crosswalk_reticulation_evidence.tsv", sep="\t")
    assert len(resolved) == 3
    assert len(pending) == 25
    assert resolved["accepted_taxon_key"].fillna("").ne("").all()
    assert pending["pending_crosswalk"].astype(bool).all()


def test_hotspot_output_is_genus_level_and_marks_data_limited_sufficiency():
    hotspots = pd.read_csv(OUT / "tci_hotspots_genus.tsv", sep="\t")
    assert len(hotspots) > 0
    assert hotspots["hotspot_score"].between(0, 1.5).all()
    assert {"data_limited", "sufficient"}.issuperset(set(hotspots["data_sufficiency"]))
    assert hotspots["genus_key"].fillna("").str.startswith("wfo:").all()
