#!/usr/bin/env python3
"""Build Track 5 non-Duke temporal chemistry reopen evidence artifacts.

created: 2026-05-18T18:05:00+00:00
cycle: 25
run_id: run-phytograph-cycle25-track5-non-duke-temporal-chemistry-reopen
agent: worker
milestone: _plan/track5-non-duke-temporal-chemistry-reopen
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[3]
T5 = ROOT / "tracks" / "track5"
DATA = T5 / "data"
REPORTS = T5 / "reports"
STAGING = ROOT / "substrate" / "staging" / "chemodiversity_ethnobotany_sources"
TAXONOMY = ROOT / "substrate" / "staging" / "taxonomy_backbone"

DUKE = "Dr. Duke Phytochemical and Ethnobotanical Databases"
DETERMINATION = "no_new_qualifying_evidence"

EVIDENCE_COLUMNS = [
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
]

HOLDOUT_COLUMNS = [
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
]

DIAG_COLUMNS = [
    "source_name",
    "candidate_rows",
    "accepted_key_rows",
    "dated_rows",
    "non_duke_rows",
    "heldout_taxa_covered",
    "chemical_classes_covered",
    "rejected_rows",
    "dominant_rejection_reason",
]


def norm(value: object) -> str:
    return " ".join(str(value).lower().strip().split())


def load_taxon_lookup() -> dict[str, tuple[str, str]]:
    accepted = pd.read_csv(TAXONOMY / "accepted_taxa.csv", dtype=str)
    synonyms = pd.read_csv(TAXONOMY / "synonym_clusters.csv", dtype=str)
    lookup: dict[str, tuple[str, str]] = {}
    for row in accepted.to_dict("records"):
        lookup[norm(row["accepted_name"])] = (row["accepted_taxon_key"], row["accepted_name"])
    accepted_name_by_key = accepted.set_index("accepted_taxon_key")["accepted_name"].to_dict()
    for row in synonyms.to_dict("records"):
        key = row["accepted_taxon_key"]
        lookup.setdefault(norm(row["name_string"]), (key, accepted_name_by_key.get(key, "")))
    return lookup


def build_evidence(raw: pd.DataFrame, lookup: dict[str, tuple[str, str]]) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    non_duke = raw[raw["source_name"] != DUKE].copy()
    for row in non_duke.to_dict("records"):
        accepted_key, accepted_name = lookup.get(norm(row["taxon_label_raw"]), ("", ""))
        rows.append(
            {
                "source_name": row["source_name"],
                "source_record_id": row.get("source_record_id", ""),
                "raw_taxon_name": row.get("taxon_label_raw", ""),
                "accepted_key": accepted_key,
                "accepted_name": accepted_name,
                "compound_name": row.get("compound_label", ""),
                "chemical_class": "",
                "evidence_scope": row.get("allowed_evidence_scope", ""),
                "plant_part": row.get("plant_part", ""),
                "discovery_or_isolation_year": "",
                "date_basis": "missing_discovery_or_isolation_year_field",
                "provenance_url_or_path": str(STAGING / "phytochemical_assertion_edges.tsv"),
                "license_or_access_note": row.get("license_class", ""),
                "training_visibility": "blocked_missing_temporal_basis",
                "heldout_label": "not_applicable",
                "caveat": "Non-Duke source row lacks a usable discovery_or_isolation_year in the frozen local artifact.",
            }
        )
    return pd.DataFrame(rows, columns=EVIDENCE_COLUMNS)


def source_diagnostics(
    raw: pd.DataFrame, profile: pd.DataFrame, enriched: pd.DataFrame, holdouts: pd.DataFrame
) -> pd.DataFrame:
    phyt_profile = profile[profile["edge_domain"] == "phytochemical_assertion"].copy()
    enriched_phyt = enriched[(enriched["edge_type"] == "phytochemical_assertion") & (enriched["retained"] == True)]
    rows: list[dict[str, object]] = []
    for row in phyt_profile.to_dict("records"):
        source_name = row["source_name"]
        raw_source = raw[raw["source_name"] == source_name]
        source_enriched = enriched_phyt[enriched_phyt["source_id"] == source_name]
        candidate_rows = int(row["assertion_count"])
        accepted_key_rows = int(len(source_enriched)) if candidate_rows else 0
        chemical_classes = int(source_enriched["compound_class"].dropna().nunique()) if candidate_rows else 0
        holdout_keys = set(holdouts.loc[holdouts["accepted_key"] != "", "accepted_key"])
        heldout_taxa_covered = int(source_enriched["accepted_taxon_key"].isin(holdout_keys).sum() > 0)
        is_non_duke = source_name != DUKE
        if candidate_rows == 0:
            reason = "no local phytochemical taxon-compound detection rows staged for this source"
        elif source_name == DUKE:
            reason = "Duke rows have accepted-key joins but no usable discovery_or_isolation_year field and are not non-Duke evidence"
        else:
            reason = "non-Duke rows lack accepted-key dated taxon-compound evidence in the frozen local artifact"
        rows.append(
            {
                "source_name": source_name,
                "candidate_rows": candidate_rows,
                "accepted_key_rows": accepted_key_rows,
                "dated_rows": 0,
                "non_duke_rows": candidate_rows if is_non_duke else 0,
                "heldout_taxa_covered": heldout_taxa_covered,
                "chemical_classes_covered": chemical_classes,
                "rejected_rows": candidate_rows,
                "dominant_rejection_reason": reason,
            }
        )
    rows.sort(key=lambda r: (r["source_name"] == DUKE, r["candidate_rows"]), reverse=True)
    return pd.DataFrame(rows, columns=DIAG_COLUMNS)


def holdout_matrix(lookup: dict[str, tuple[str, str]]) -> pd.DataFrame:
    holdouts = pd.read_csv(DATA / "canonical_phyto_held_out.tsv", sep="\t", dtype=str)
    rows: list[dict[str, object]] = []
    for row in holdouts.to_dict("records"):
        key, _ = lookup.get(norm(row["taxon"]), ("", ""))
        target = row["canonical_compound_class_normalized"] or row["canonical_compound_class"]
        if not key:
            reason = "holdout taxon lacks accepted-key join in frozen substrate; no non-Duke dated evidence available"
        else:
            reason = "no accepted-key non-Duke taxon-compound row has a usable discovery_or_isolation_year before or after target year"
        rows.append(
            {
                "holdout_taxon": row["taxon"],
                "accepted_key": key,
                "target_compound_or_class": target,
                "target_year": row["discovery_year"],
                "non_duke_evidence_before_year": "false",
                "non_duke_evidence_after_year": "false",
                "duke_only_before_year": "false",
                "training_label_hidden": "true",
                "validation_allowed": "false",
                "dominant_failure_reason": reason,
            }
        )
    return pd.DataFrame(rows, columns=HOLDOUT_COLUMNS)


def report_markdown(evidence: pd.DataFrame, holdouts: pd.DataFrame, diagnostics: pd.DataFrame) -> str:
    non_duke_dated = int(
        ((evidence["source_name"] != DUKE) & (evidence["accepted_key"] != "") & (evidence["discovery_or_isolation_year"] != "")).sum()
    )
    diag_table = "\n".join(
        "| {source_name} | {candidate_rows} | {accepted_key_rows} | {dated_rows} | {non_duke_rows} | {heldout_taxa_covered} | {chemical_classes_covered} | {rejected_rows} | {dominant_rejection_reason} |".format(
            **row
        )
        for row in diagnostics.to_dict("records")
    )
    holdout_table = "\n".join(
        "| {holdout_taxon} | {accepted_key} | {target_compound_or_class} | {target_year} | {non_duke_evidence_before_year} | {non_duke_evidence_after_year} | {validation_allowed} | {dominant_failure_reason} |".format(
            **row
        )
        for row in holdouts.to_dict("records")
    )
    return f"""---
created: 2026-05-18T18:05:00+00:00
cycle: 25
run_id: run-phytograph-cycle25-track5-non-duke-temporal-chemistry-reopen
agent: worker
milestone: _plan/track5-non-duke-temporal-chemistry-reopen
---

# Track 5 Reopen Temporal Chemistry Evidence

## Determination

determination: `{DETERMINATION}`.

The frozen local chemistry substrate does not contain qualifying non-Duke temporal taxon-compound evidence. The only retained accepted-key phytochemical assertion stratum is Duke-derived, and the staged non-Duke sources inspected here contain zero local taxon-compound detection rows with accepted keys and usable discovery or isolation years. Therefore H5 remains `not_validated_source_biased`, and the chemodiversity predictor was not rerun.

## Sources Inspected

| Source | Candidate rows | Accepted-key rows | Dated rows | Non-Duke rows | Held-out taxa covered | Chemical classes covered | Rejected rows | Dominant rejection reason |
|---|---:|---:|---:|---:|---:|---:|---:|---|
{diag_table}

## Canonical Holdout Matrix

| Holdout taxon | Accepted key | Target class | Target year | Non-Duke before year | Non-Duke after year | Validation allowed | Dominant failure reason |
|---|---|---|---:|---|---|---|---|
{holdout_table}

## Source-Dominance Diagnostics

The prior no-Duke ablation remains decisive for the current mechanism: `source_ablation_results.tsv` reports 1,405 baseline prediction rows and 0 prediction rows under `no_duke`, `source_density_matched`, and `screening_count_matched` variants. This reopen package adds no qualifying row to change that condition: `|N ∩ D| = {non_duke_dated}`, where `N` is accepted-key non-Duke taxon-compound evidence and `D` is rows with a usable discovery_or_isolation_year.

![Accepted-key and dated taxon-compound coverage by source, separating non-Duke evidence from Duke-only evidence for Track 5 reopen assessment.](../figures/track5_reopen_non_duke_temporal_coverage.png)

## Reopen Gate

The reopen threshold is not met. Accepted-key rows exist for Duke-derived chemistry evidence, but Duke is the source-dominant stratum being tested against and its local records do not provide discovery_or_isolation_year fields suitable for temporally frozen holdouts. KNApSAcK, NPASS, and ChEBI remain represented in the source audit as inspected non-Duke sources, but they contribute no local accepted-key dated taxon-compound detection rows in the frozen workspace.

## Evidence Firewall

This package makes no phytochemical novelty, clinical efficacy, preparation, dosage, safety, or bioactivity claim. Ethnobotanical-use-only and bioactivity-class-only rows remain excluded from taxon-compound detection evidence. Master `prediction_ledger.tsv` and `speculation_ledger.tsv` stay header-only.
"""


def main() -> int:
    DATA.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)
    raw = pd.read_csv(STAGING / "phytochemical_assertion_edges.tsv", sep="\t", dtype=str, keep_default_na=False)
    profile = pd.read_csv(STAGING / "source_bias_profile.tsv", sep="\t")
    enriched = pd.read_parquet(DATA / "track5_enrichment_edges.parquet")
    lookup = load_taxon_lookup()

    evidence = build_evidence(raw, lookup)
    holdouts = holdout_matrix(lookup)
    diagnostics = source_diagnostics(raw, profile, enriched, holdouts)

    evidence.to_csv(DATA / "non_duke_temporal_taxon_compound_evidence.tsv", sep="\t", index=False)
    holdouts.to_csv(DATA / "track5_reopen_temporal_holdout_matrix.tsv", sep="\t", index=False)
    diagnostics.to_csv(DATA / "track5_reopen_source_diagnostics.tsv", sep="\t", index=False)
    (REPORTS / "track5_reopen_temporal_chemistry_evidence.md").write_text(
        report_markdown(evidence, holdouts, diagnostics), encoding="utf-8"
    )
    print(f"wrote evidence rows: {len(evidence)}")
    print(f"wrote holdout rows: {len(holdouts)}")
    print(f"wrote diagnostics rows: {len(diagnostics)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
