#!/usr/bin/env python3
# created: 2026-05-18T05:00:00+00:00
# cycle: 10
# run_id: fork-aaf42b4ab956-clone-1-track2-validation-ablation
# agent: worker-clone-1
# milestone: M4.V2
"""Track 2 held-out recovery checks over fixed M3.T2 ranker outputs."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[3]
TRACK = ROOT / "tracks" / "track2"
DATA = TRACK / "data"

SCORES_PATH = DATA / "ghost_partner_candidate_scores.tsv"
HELDOUT_PATH = DATA / "janzen_martin_heldout_recovery_scaffold.tsv"
CROSSWALK_PATH = ROOT / "phytograph_dataset" / "taxon_crosswalk.parquet"
ACCEPTED_PATH = ROOT / "substrate" / "staging" / "taxonomy_backbone" / "accepted_taxa.csv"

KEY_RECOVERY_PATH = DATA / "janzen_martin_accepted_key_recovery.tsv"
EVIDENCE_QUEUE_PATH = DATA / "modern_dispersal_failure_evidence_queue.tsv"
VALIDATION_SCORES_PATH = DATA / "ghost_partner_validation_scores.tsv"


def normalize_name(value: object) -> str:
    return " ".join(str(value or "").lower().replace("_", " ").split())


def clean_optional(value: object) -> str:
    if value is None or pd.isna(value):
        return ""
    text = str(value).strip()
    return "" if text.lower() == "nan" else text


def read_table(path: Path) -> pd.DataFrame:
    if path.suffix == ".parquet":
        return pd.read_parquet(path)
    return pd.read_csv(path)


def build_name_index() -> dict[str, dict[str, str]]:
    frames = []
    if CROSSWALK_PATH.exists():
        crosswalk = read_table(CROSSWALK_PATH)
        for source_col in ["raw_name", "wfo_accepted_name", "gbif_accepted_name", "opentree_accepted_name", "powo_accepted_name"]:
            if source_col in crosswalk.columns:
                part = crosswalk[["accepted_taxon_key", source_col]].copy()
                part = part.rename(columns={source_col: "name"})
                part["source"] = f"taxon_crosswalk.{source_col}"
                frames.append(part)
    if ACCEPTED_PATH.exists():
        accepted = pd.read_csv(ACCEPTED_PATH, dtype=str)
        part = accepted[["accepted_taxon_key", "accepted_name", "family", "genus"]].copy()
        part = part.rename(columns={"accepted_name": "name"})
        part["source"] = "accepted_taxa.accepted_name"
        frames.append(part)

    if not frames:
        return {}

    names = pd.concat(frames, ignore_index=True, sort=False)
    names["normalized_name"] = names["name"].map(normalize_name)
    names["accepted_taxon_key"] = names["accepted_taxon_key"].fillna("").astype(str)
    names = names[names["normalized_name"].ne("")]

    index: dict[str, dict[str, str]] = {}
    for row in names.itertuples(index=False):
        current = index.setdefault(
            row.normalized_name,
            {
                "recovered_accepted_taxon_key": "",
                "accepted_key_recovery_source": "",
                "family": "",
                "genus": "",
            },
        )
        if row.accepted_taxon_key and not current["recovered_accepted_taxon_key"]:
            current["recovered_accepted_taxon_key"] = row.accepted_taxon_key
            current["accepted_key_recovery_source"] = row.source
        for col in ["family", "genus"]:
            value = getattr(row, col, "")
            value = clean_optional(value)
            if value and not current[col]:
                current[col] = value
    return index


def heldout_best_rows(scores: pd.DataFrame, heldout: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for held in heldout.itertuples(index=False):
        name = normalize_name(held.heldout_scientific_name)
        matches = scores[scores["raw_scientific_name"].map(normalize_name).eq(name)].sort_values("rank")
        if matches.empty:
            rows.append(
                {
                    "heldout_scientific_name": held.heldout_scientific_name,
                    "common_name": held.common_name,
                    "candidate_id": "",
                    "candidate_score": "",
                    "candidate_status": "not_present",
                    "best_rank": "",
                    "accepted_taxon_key": "",
                    "modern_failure_support": 0.0,
                    "morphology_support": 0.0,
                    "penalty_living_megafauna_ambiguous": 0.0,
                    "penalty_source_singleton": 0.0,
                    "candidate_class": "",
                    "primary_citation_short": "",
                }
            )
            continue
        row = matches.iloc[0].to_dict()
        rows.append(
            {
                "heldout_scientific_name": held.heldout_scientific_name,
                "common_name": held.common_name,
                "candidate_id": row["candidate_id"],
                "candidate_score": row["candidate_score"],
                "candidate_status": row["candidate_status"],
                "best_rank": row["rank"],
                "accepted_taxon_key": row.get("accepted_taxon_key", ""),
                "modern_failure_support": row.get("modern_failure_support", 0.0),
                "morphology_support": row.get("morphology_support", 0.0),
                "penalty_living_megafauna_ambiguous": row.get("penalty_living_megafauna_ambiguous", 0.0),
                "penalty_source_singleton": row.get("penalty_source_singleton", 0.0),
                "candidate_class": row.get("candidate_class", ""),
                "primary_citation_short": row.get("primary_citation_short", ""),
            }
        )
    return pd.DataFrame(rows)


def recovery_reason(row: pd.Series) -> str:
    reasons = []
    if not row["in_seed_layer"]:
        reasons.append("not_recovered_in_seed_layer")
    if row["accepted_key_status"] == "accepted_key_recovered":
        reasons.append("accepted-key recovered")
    elif row["accepted_key_status"] == "accepted_key_already_present":
        reasons.append("accepted-key already present")
    else:
        reasons.append("accepted-key absent")
    if row["modern_failure_evidence_status"] == "seed_modern_failure_present":
        reasons.append("modern-failure evidence present in seed citation")
    else:
        reasons.append("morphology-only or no explicit modern-failure component")
    if row["living_megafauna_ambiguity"]:
        reasons.append("living-megafauna ambiguous")
    if row["support_class"] == "insufficient_support":
        reasons.append("insufficient support")
    return "; ".join(reasons)


def validation_class(row: pd.Series) -> str:
    if not row["in_seed_layer"]:
        return "not_recovered"
    if row["accepted_key_status"] == "accepted_key_absent":
        return "data_limited"
    if row["modern_failure_evidence_status"] != "seed_modern_failure_present":
        return "insufficient_support"
    if row["living_megafauna_ambiguity"]:
        return "data_limited"
    return "validation_ready"


def build() -> dict[str, int]:
    scores = pd.read_csv(SCORES_PATH, sep="\t").fillna("")
    heldout = pd.read_csv(HELDOUT_PATH, sep="\t").fillna("")
    index = build_name_index()
    best = heldout_best_rows(scores, heldout).fillna("")

    key_rows = []
    validation_rows = []
    for row in best.itertuples(index=False):
        normalized = normalize_name(row.heldout_scientific_name)
        recovered = index.get(normalized, {})
        existing_key = str(row.accepted_taxon_key or "")
        recovered_key = recovered.get("recovered_accepted_taxon_key", "")
        if existing_key:
            key_status = "accepted_key_already_present"
            final_key = existing_key
            source = "m3_track2_candidate_scores.accepted_taxon_key"
        elif recovered_key:
            key_status = "accepted_key_recovered"
            final_key = recovered_key
            source = recovered.get("accepted_key_recovery_source", "")
        else:
            key_status = "accepted_key_absent"
            final_key = ""
            source = ""

        in_seed = bool(row.candidate_id)
        modern_status = (
            "seed_modern_failure_present"
            if float(row.modern_failure_support or 0.0) > 0
            else "needs_independent_modern_failure_check"
        )
        living_ambiguous = float(row.penalty_living_megafauna_ambiguous or 0.0) > 0
        support_class = "insufficient_support" if not in_seed or float(row.modern_failure_support or 0.0) == 0 else "candidate_support_present"
        record = {
            "heldout_scientific_name": row.heldout_scientific_name,
            "common_name": row.common_name,
            "normalized_name": normalized,
            "in_seed_layer": in_seed,
            "candidate_id": row.candidate_id,
            "best_rank": row.best_rank,
            "candidate_score": row.candidate_score,
            "candidate_status": row.candidate_status,
            "original_accepted_taxon_key": existing_key,
            "recovered_accepted_taxon_key": final_key,
            "accepted_key_status": key_status,
            "accepted_key_recovery_source": source,
            "family": clean_optional(recovered.get("family", "")),
            "genus": clean_optional(recovered.get("genus", "")),
            "modern_failure_evidence_status": modern_status,
            "morphology_only": float(row.modern_failure_support or 0.0) == 0,
            "living_megafauna_ambiguity": living_ambiguous,
            "source_singleton": float(row.penalty_source_singleton or 0.0) > 0,
            "support_class": support_class,
            "candidate_class": row.candidate_class,
            "primary_citation_short": row.primary_citation_short,
        }
        record["validation_class"] = validation_class(pd.Series(record))
        record["recovery_reason"] = recovery_reason(pd.Series(record))
        key_rows.append(record)
        validation_rows.append(record)

    key_df = pd.DataFrame(key_rows)
    queue = scores[
        [
            "candidate_id",
            "raw_scientific_name",
            "accepted_taxon_key",
            "candidate_status",
            "candidate_score",
            "modern_failure_support",
            "morphology_support",
            "candidate_class",
            "primary_citation_short",
            "interpretation_caveat",
            "ambiguity_flag",
        ]
    ].copy()
    queue["modern_failure_evidence_status"] = queue["modern_failure_support"].map(
        lambda v: "seed_modern_failure_present" if float(v) > 0 else "needs_independent_modern_failure_check"
    )
    queue["evidence_queue_action"] = queue["modern_failure_evidence_status"].map(
        {
            "seed_modern_failure_present": "verify cited modern dispersal-failure claim independently before validation",
            "needs_independent_modern_failure_check": "targeted literature check required; morphology-only support remains capped",
        }
    )
    queue["inferred_anachronism_claim"] = False
    queue["enters_master_prediction_ledger"] = False

    validation = pd.DataFrame(validation_rows)
    validation["validation_score"] = validation.apply(
        lambda row: round(
            (0.35 if row["accepted_key_status"] != "accepted_key_absent" else 0.0)
            + (0.35 if row["modern_failure_evidence_status"] == "seed_modern_failure_present" else 0.0)
            + (0.20 if row["in_seed_layer"] else 0.0)
            + (0.10 if not row["living_megafauna_ambiguity"] else 0.0),
            3,
        ),
        axis=1,
    )
    validation["inferred_anachronism_claim"] = False
    validation["enters_master_prediction_ledger"] = False

    key_df.to_csv(KEY_RECOVERY_PATH, sep="\t", index=False)
    queue.to_csv(EVIDENCE_QUEUE_PATH, sep="\t", index=False)
    validation.to_csv(VALIDATION_SCORES_PATH, sep="\t", index=False)
    return {
        "heldout_cases": int(len(key_df)),
        "accepted_key_recovered_or_present": int(key_df["accepted_key_status"].ne("accepted_key_absent").sum()),
        "validation_ready": int(validation["validation_class"].eq("validation_ready").sum()),
        "modern_failure_seed_present": int(key_df["modern_failure_evidence_status"].eq("seed_modern_failure_present").sum()),
    }


if __name__ == "__main__":
    result = build()
    print(
        "PASS: Track 2 validation recovery "
        f"({result['heldout_cases']} held-out, {result['validation_ready']} validation-ready)"
    )
    print(f"WROTE: {KEY_RECOVERY_PATH}")
    print(f"WROTE: {EVIDENCE_QUEUE_PATH}")
    print(f"WROTE: {VALIDATION_SCORES_PATH}")
