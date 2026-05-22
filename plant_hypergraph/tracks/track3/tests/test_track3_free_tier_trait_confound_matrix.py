# created: 2026-05-18T23:50:00+00:00
# cycle: 30
# run_id: run-phytograph-cycle30-track3-free-tier-trait-confound-matrix
# agent: worker
# milestone: _plan/track3-free-tier-trait-confound-matrix

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pandas as pd


WORKSPACE = Path(__file__).resolve().parents[3]
TRACK3 = WORKSPACE / "tracks" / "track3"
DATA = TRACK3 / "data"
FIGURES = TRACK3 / "figures"
REPORTS = TRACK3 / "reports"
SCRIPT = TRACK3 / "scripts" / "build_free_tier_trait_confound_matrix.py"


def regenerate() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    subprocess.run(["python3", str(SCRIPT)], cwd=WORKSPACE, check=True)
    matrix = pd.read_csv(DATA / "track3_free_tier_trait_taxon_matrix.tsv", sep="\t")
    diag = pd.read_csv(DATA / "track3_free_tier_trait_confound_diagnostics.tsv", sep="\t")
    ready = pd.read_csv(DATA / "track3_free_tier_trait_readiness.tsv", sep="\t")
    return matrix, diag, ready


def test_outputs_exist_and_matrix_has_required_columns():
    matrix, diag, ready = regenerate()
    required = [
        "trait",
        "accepted_taxon_key",
        "family_key",
        "family_label",
        "source_id",
        "source_edge_count_for_taxon_trait",
        "total_track3_edge_count_for_taxon",
        "trait_family_carrier_count",
        "trait_family_share",
        "family_total_track3_taxa",
        "pending_crosswalk_excluded_count_for_trait",
        "accepted_resolution_share_for_trait",
        "row_class_from_wave4",
        "CP_min",
        "controlled_readiness_status",
    ]
    assert list(matrix.columns) == required
    assert len(matrix) == 3069
    assert len(diag) == 15
    assert len(ready) == 15

    for path in [
        DATA / "track3_free_tier_trait_confound_summary.json",
        FIGURES / "track3_free_tier_trait_confound_matrix.png",
        REPORTS / "track3_free_tier_trait_confound_matrix.md",
    ]:
        assert path.exists(), f"missing artifact: {path}"
        assert path.stat().st_size > 0, f"empty artifact: {path}"


def test_every_accepted_canonical_carrier_is_represented_once():
    matrix, _, _ = regenerate()
    edges = pd.read_parquet(DATA / "convergence_trait_edges.parquet")
    canonical = {
        "c4_photosynthesis",
        "cam_photosynthesis",
        "succulence",
        "fleshy_fruit",
        "drupe",
        "samara",
        "capsule",
        "achene",
        "follicle",
        "aril",
        "elaiosome",
        "myrmecochory",
        "ant_domatia",
        "carnivory",
        "parasitism",
    }
    accepted = edges[
        edges["trait"].isin(canonical)
        & (~edges["pending_crosswalk"].astype(bool))
        & (edges["accepted_taxon_key"].fillna("").astype(str).str.strip() != "")
    ][["trait", "accepted_taxon_key"]].drop_duplicates()
    assert len(matrix) == len(accepted)
    assert not matrix.duplicated(["trait", "accepted_taxon_key"]).any()


def test_drupe_and_capsule_are_not_upgraded():
    _, diag, ready = regenerate()
    dc = ready[ready["trait"].isin(["drupe", "capsule"])].set_index("trait")
    assert set(dc["controlled_readiness_status"]) == {"data_limited_pending_prior"}
    assert dc.loc["drupe", "CP_min"] >= 2.0
    assert dc.loc["capsule", "CP_min"] >= 2.0
    assert dc["blocker_classification"].str.contains("projection_loss", regex=False).all()
    assert dc["blocker_classification"].str.contains("single_source_dominated", regex=False).all()

    diag_dc = diag[diag["trait"].isin(["drupe", "capsule"])]
    assert (diag_dc["family_size_baseline_z"] >= 2.0).all()
    assert (diag_dc["sampling_density_baseline_z"] >= 2.0).all()


def test_canonical_weak_traits_have_explicit_blockers():
    _, _, ready = regenerate()
    blockers = ready.set_index("trait")["blocker_classification"]
    assert "projection_loss" in blockers["c4_photosynthesis"]
    assert "sampling_density_dominated" in blockers["fleshy_fruit"]
    assert "family_dominance" in blockers["samara"]
    assert "zero_carrier" in blockers["ant_domatia"]
    assert "zero_carrier" in blockers["carnivory"]
    assert "zero_carrier" in blockers["parasitism"]
    assert not ready["controlled_readiness_status"].eq("controlled_convergence_ready").any()


def test_report_summary_and_master_ledgers_are_conservative():
    regenerate()
    summary = json.loads((DATA / "track3_free_tier_trait_confound_summary.json").read_text())
    assert summary["h3_decision"] == "confound_limited"
    assert summary["controlled_convergence_ready_traits"] == []
    assert summary["drupe_status"] == "data_limited_pending_prior"
    assert summary["capsule_status"] == "data_limited_pending_prior"

    report = (REPORTS / "track3_free_tier_trait_confound_matrix.md").read_text()
    assert "H3 remains `confound_limited`" in report
    assert "Controlled-ready traits: none." in report
    assert "No row from this branch enters the master prediction ledger." in report

    assert len((WORKSPACE / "prediction_ledger.tsv").read_text().splitlines()) == 1
    assert len((WORKSPACE / "speculation_ledger.tsv").read_text().splitlines()) == 1
