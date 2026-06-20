#!/usr/bin/env python3
# created: 2026-05-18T17:10:00+00:00
# cycle: 24
# run_id: run-phytograph-cycle24-track4-bioclim-validation-reopen
# agent: worker
# milestone: _plan/track4-bioclim-validation-reopen
"""Build Track 4 reopen evidence tables for bioclim validation readiness."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "tracks" / "track4" / "data"
REPORTS = ROOT / "tracks" / "track4" / "reports"
FIGURES = ROOT / "tracks" / "track4" / "figures"

CLIMATE = DATA / "climate_envelope_coverage.tsv"
CWR = DATA / "crop_wild_relative_pairs.tsv"
HELDOUT = DATA / "heldout_validation_seed.tsv"
CANDIDATES = DATA / "crop_substitution_candidates.tsv"

VECTORS_OUT = DATA / "crop_cwr_bioclim_vectors.tsv"
PAIRS_OUT = DATA / "crop_cwr_validation_pairs.tsv"
DIAGNOSTICS_OUT = DATA / "track4_reopen_join_diagnostics.tsv"


VECTOR_COLUMNS = [
    "accepted_key",
    "accepted_name",
    "role",
    "crop_anchor_key",
    "crop_anchor_name",
    "source_name",
    "occurrence_or_range_basis",
    "bioclim_variable",
    "value",
    "aggregation_method",
    "provenance_url_or_path",
    "license_or_access_note",
    "caveat",
]

PAIR_COLUMNS = [
    "crop_key",
    "crop_name",
    "candidate_key",
    "candidate_name",
    "expert_source",
    "expert_relation_type",
    "heldout_status",
    "overlaps_training_evidence",
    "same_genus",
    "validation_allowed",
    "caveat",
]

DIAG_COLUMNS = [
    "source_name",
    "candidate_rows",
    "accepted_key_rows",
    "crop_anchor_rows",
    "cwr_rows",
    "bioclim_vector_rows",
    "heldout_validation_rows",
    "rejected_rows",
    "dominant_rejection_reason",
]


def read_tsv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, sep="\t", dtype=str, keep_default_na=False)


def truthy(value: object) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def genus(name: str) -> str:
    return name.split()[0].lower() if name and name.split() else ""


def build_vectors(climate: pd.DataFrame, cwr: pd.DataFrame) -> pd.DataFrame:
    crop_by_key = {
        row["crop_accepted_taxon_key"]: row["crop_taxon"]
        for _, row in cwr.iterrows()
        if row["crop_accepted_taxon_key"]
    }
    cwr_rows_by_key: dict[str, list[dict[str, str]]] = {}
    for _, row in cwr.iterrows():
        wild_key = row["wild_ancestor_accepted_key"]
        if wild_key:
            cwr_rows_by_key.setdefault(wild_key, []).append(row.to_dict())

    rows: list[dict[str, str]] = []
    accepted = climate[climate["accepted_taxon_key"] != ""].copy()
    for _, row in accepted.iterrows():
        key = row["accepted_taxon_key"]
        name = row["taxon_canonical_name"]
        common = {
            "accepted_key": key,
            "accepted_name": name,
            "source_name": row["envelope_source"],
            "occurrence_or_range_basis": row["occurrence_source"],
            "bioclim_variable": "none_available",
            "value": "",
            "aggregation_method": "not_computed",
            "provenance_url_or_path": "tracks/track4/data/climate_envelope_coverage.tsv",
            "license_or_access_note": row["license"],
            "caveat": "accepted-key climate coverage row only; no observed occurrence coordinates or numeric bioclim values were available in local staging",
        }
        if key in crop_by_key:
            rows.append(
                {
                    **common,
                    "role": "crop_anchor",
                    "crop_anchor_key": key,
                    "crop_anchor_name": crop_by_key[key],
                }
            )
        for cwr_row in cwr_rows_by_key.get(key, []):
            rows.append(
                {
                    **common,
                    "role": "cwr",
                    "crop_anchor_key": cwr_row["crop_accepted_taxon_key"],
                    "crop_anchor_name": cwr_row["crop_taxon"],
                }
            )

    return pd.DataFrame(rows, columns=VECTOR_COLUMNS).drop_duplicates()


def build_pairs(heldout: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, str]] = []
    for _, row in heldout.iterrows():
        has_key = bool(row["accepted_taxon_key"])
        caveats = []
        if not has_key:
            caveats.append("held-out crop lacks Barrier-1 accepted key")
        caveats.append("local held-out source is crop-level only; no candidate-level expert CWR comparator was available")
        if truthy(row["overlaps_training_pedigree"]):
            caveats.append("held-out crop overlaps curated training pedigree evidence")
        rows.append(
            {
                "crop_key": row["accepted_taxon_key"],
                "crop_name": row["crop_taxon"],
                "candidate_key": "",
                "candidate_name": "",
                "expert_source": row["cgiar_or_recommendation_source"],
                "expert_relation_type": "crop_level_program_or_cwr_context",
                "heldout_status": "heldout_crop_only_no_candidate",
                "overlaps_training_evidence": str(truthy(row["overlaps_training_pedigree"])).lower(),
                "same_genus": "not_applicable",
                "validation_allowed": "false",
                "caveat": "; ".join(caveats),
            }
        )
    return pd.DataFrame(rows, columns=PAIR_COLUMNS)


def count_numeric_vectors(vectors: pd.DataFrame) -> int:
    if vectors.empty:
        return 0
    return int((vectors["value"].astype(str).str.strip() != "").sum())


def build_diagnostics(
    climate: pd.DataFrame,
    cwr: pd.DataFrame,
    heldout: pd.DataFrame,
    candidates: pd.DataFrame,
    vectors: pd.DataFrame,
    pairs: pd.DataFrame,
) -> pd.DataFrame:
    vector_count = count_numeric_vectors(vectors)
    validation_allowed = int(pairs["validation_allowed"].eq("true").sum()) if not pairs.empty else 0
    joined_cwr = cwr[cwr["pair_join_status"] == "joined"]
    rows = [
        {
            "source_name": "WorldClim/CHELSA climate-envelope staging",
            "candidate_rows": len(climate),
            "accepted_key_rows": int((climate["accepted_taxon_key"] != "").sum()),
            "crop_anchor_rows": int(vectors["role"].eq("crop_anchor").sum()) if not vectors.empty else 0,
            "cwr_rows": int(vectors["role"].eq("cwr").sum()) if not vectors.empty else 0,
            "bioclim_vector_rows": vector_count,
            "heldout_validation_rows": 0,
            "rejected_rows": int((climate["bioclim_values_present"].astype(str).str.lower() != "true").sum()),
            "dominant_rejection_reason": "no observed occurrence coordinates or numeric bioclim values in local M1.6 staging",
        },
        {
            "source_name": "Track 4 crop-wild-relative pairs",
            "candidate_rows": len(cwr),
            "accepted_key_rows": len(joined_cwr),
            "crop_anchor_rows": int((cwr["crop_accepted_taxon_key"] != "").sum()),
            "cwr_rows": int((cwr["wild_ancestor_accepted_key"] != "").sum()),
            "bioclim_vector_rows": vector_count,
            "heldout_validation_rows": 0,
            "rejected_rows": int((cwr["pair_join_status"] != "joined").sum()),
            "dominant_rejection_reason": "crop and/or wild-relative accepted-key gaps; joined pairs still lack observed bioclim vectors",
        },
        {
            "source_name": "Held-out expert crop set",
            "candidate_rows": len(heldout),
            "accepted_key_rows": int((heldout["accepted_taxon_key"] != "").sum()),
            "crop_anchor_rows": int((heldout["accepted_taxon_key"] != "").sum()),
            "cwr_rows": 0,
            "bioclim_vector_rows": 0,
            "heldout_validation_rows": validation_allowed,
            "rejected_rows": int(len(heldout) - validation_allowed),
            "dominant_rejection_reason": "held-out rows are crop-level expert sources only; no candidate-level comparator without training leakage",
        },
        {
            "source_name": "M3.T4 training-derived candidate rows",
            "candidate_rows": len(candidates),
            "accepted_key_rows": int(((candidates["crop_accepted_taxon_key"] != "") & (candidates["candidate_wild_relative_key"] != "")).sum()),
            "crop_anchor_rows": candidates["crop_accepted_taxon_key"].nunique(),
            "cwr_rows": candidates["candidate_wild_relative_key"].nunique(),
            "bioclim_vector_rows": 0,
            "heldout_validation_rows": 0,
            "rejected_rows": len(candidates),
            "dominant_rejection_reason": "rows derive from training pedigree/CWR evidence and cannot serve as held-out expert comparisons",
        },
    ]
    return pd.DataFrame(rows, columns=DIAG_COLUMNS)


def main() -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)
    FIGURES.mkdir(parents=True, exist_ok=True)

    climate = read_tsv(CLIMATE)
    cwr = read_tsv(CWR)
    heldout = read_tsv(HELDOUT)
    candidates = read_tsv(CANDIDATES)

    vectors = build_vectors(climate, cwr)
    pairs = build_pairs(heldout)
    diagnostics = build_diagnostics(climate, cwr, heldout, candidates, vectors, pairs)

    vectors.to_csv(VECTORS_OUT, sep="\t", index=False)
    pairs.to_csv(PAIRS_OUT, sep="\t", index=False)
    diagnostics.to_csv(DIAGNOSTICS_OUT, sep="\t", index=False)

    print(f"wrote {VECTORS_OUT} ({len(vectors)} rows; numeric vectors={count_numeric_vectors(vectors)})")
    print(f"wrote {PAIRS_OUT} ({len(pairs)} rows; validation_allowed={pairs['validation_allowed'].eq('true').sum()})")
    print(f"wrote {DIAGNOSTICS_OUT} ({len(diagnostics)} rows)")


if __name__ == "__main__":
    main()
