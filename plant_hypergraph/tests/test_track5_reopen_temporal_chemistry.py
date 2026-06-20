"""Focused checks for the Track 5 non-Duke temporal chemistry reopen package."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "tracks" / "track5" / "data"
REPORT = ROOT / "tracks" / "track5" / "reports" / "track5_reopen_temporal_chemistry_evidence.md"
FIGURE = ROOT / "tracks" / "track5" / "figures" / "track5_reopen_non_duke_temporal_coverage.png"

EVIDENCE_COLUMNS = {
    "source_name",
    "source_record_id",
    "raw_taxon_name",
    "accepted_key",
    "accepted_name",
    "compound_name",
    "chemical_class",
    "evidence_scope",
    "plant_part",
    "discovery_or_isolation_year",
    "date_basis",
    "provenance_url_or_path",
    "license_or_access_note",
    "training_visibility",
    "heldout_label",
    "caveat",
}

HOLDOUT_COLUMNS = {
    "holdout_taxon",
    "accepted_key",
    "target_compound_or_class",
    "target_year",
    "non_duke_evidence_before_year",
    "non_duke_evidence_after_year",
    "duke_only_before_year",
    "training_label_hidden",
    "validation_allowed",
    "dominant_failure_reason",
}

DIAG_COLUMNS = {
    "source_name",
    "candidate_rows",
    "accepted_key_rows",
    "dated_rows",
    "non_duke_rows",
    "heldout_taxa_covered",
    "chemical_classes_covered",
    "rejected_rows",
    "dominant_rejection_reason",
}


def read_tsv(name: str) -> pd.DataFrame:
    return pd.read_csv(DATA / name, sep="\t", dtype=str, keep_default_na=False)


def test_required_columns_and_vocabularies():
    evidence = read_tsv("non_duke_temporal_taxon_compound_evidence.tsv")
    holdouts = read_tsv("track5_reopen_temporal_holdout_matrix.tsv")
    diagnostics = read_tsv("track5_reopen_source_diagnostics.tsv")

    assert EVIDENCE_COLUMNS <= set(evidence.columns)
    assert HOLDOUT_COLUMNS <= set(holdouts.columns)
    assert DIAG_COLUMNS <= set(diagnostics.columns)

    assert set(holdouts["validation_allowed"]) <= {"true", "false"}
    assert set(holdouts["training_label_hidden"]) <= {"true", "false"}
    assert set(holdouts["non_duke_evidence_before_year"]) <= {"true", "false"}
    assert set(holdouts["non_duke_evidence_after_year"]) <= {"true", "false"}
    if len(evidence):
        assert set(evidence["training_visibility"]) <= {
            "training_allowed_pre_target",
            "heldout_target_label",
            "blocked_missing_temporal_basis",
            "blocked_missing_accepted_key",
        }


def test_no_qualifying_non_duke_dated_evidence_is_promoted():
    evidence = read_tsv("non_duke_temporal_taxon_compound_evidence.tsv")
    diagnostics = read_tsv("track5_reopen_source_diagnostics.tsv")

    qualifying = evidence[
        (evidence["accepted_key"] != "")
        & (evidence["discovery_or_isolation_year"] != "")
        & (~evidence["source_name"].str.contains("Duke", case=False, na=False))
    ]
    assert qualifying.empty
    assert diagnostics.loc[
        diagnostics["source_name"] != "Dr. Duke Phytochemical and Ethnobotanical Databases",
        "candidate_rows",
    ].astype(int).sum() == 0
    assert diagnostics["dated_rows"].astype(int).sum() == 0


def test_holdout_matrix_blocks_target_label_leakage():
    holdouts = read_tsv("track5_reopen_temporal_holdout_matrix.tsv")
    canonical = {"Taxus brevifolia", "Catharanthus roseus", "Cinchona officinalis", "Artemisia annua"}
    assert canonical <= set(holdouts["holdout_taxon"])
    assert set(holdouts["training_label_hidden"]) == {"true"}
    assert set(holdouts["validation_allowed"]) == {"false"}
    assert set(holdouts["non_duke_evidence_before_year"]) == {"false"}
    assert set(holdouts["non_duke_evidence_after_year"]) == {"false"}
    assert (holdouts.loc[holdouts["validation_allowed"] == "false", "dominant_failure_reason"].str.len() > 20).all()


def test_report_evidence_firewall_and_determination():
    text = REPORT.read_text(encoding="utf-8")
    lower = text.lower()
    assert "determination: `no_new_qualifying_evidence`." in text
    assert "chemodiversity predictor was not rerun" in lower
    assert "|n ∩ d| = 0" in lower
    forbidden = [
        "clinical efficacy is",
        "safe dosage",
        "treats ",
        "cures ",
        "new bioactivity",
        "validated phytochemical novelty",
    ]
    assert not any(term in lower for term in forbidden)


def test_master_ledgers_and_figure_state():
    assert len((ROOT / "prediction_ledger.tsv").read_text(encoding="utf-8").splitlines()) == 1
    assert len((ROOT / "speculation_ledger.tsv").read_text(encoding="utf-8").splitlines()) == 1
    assert FIGURE.exists()
    assert FIGURE.stat().st_size > 1000
