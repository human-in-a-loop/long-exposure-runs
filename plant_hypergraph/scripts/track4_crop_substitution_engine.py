#!/usr/bin/env python3
# created: 2026-05-18T02:05:00Z
# cycle: 9
# run_id: fork-e08673192f98-clone-3-track4-crop-substitution-engine
# agent: worker
# milestone: M3.T4
"""Build a data-limited first Track 4 Crop Substitution Engine.

The current Barrier 2 Track 4 inputs contain observed pedigree/CWR evidence
but zero observed bioclim vectors. This instrument therefore ranks only
pedigree-supported wild relatives and explicitly marks climate matching as
not computable. It does not write to the frozen substrate and does not
independently normalize synonyms.
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import pandas as pd

from barrier1_common import stable_id


ROOT = Path(__file__).resolve().parents[1]
TRACK = ROOT / "tracks" / "track4"
DATA = TRACK / "data"
DOC = TRACK / "track4_domestication_hypergraph.md"

EDGES = DATA / "domestication_enrichment_edges.parquet"
CWR = DATA / "crop_wild_relative_pairs.tsv"
CLIMATE = DATA / "climate_envelope_coverage.tsv"
HELDOUT = DATA / "heldout_validation_seed.tsv"
SUMMARY = DATA / "crop_cwr_coverage_summary.tsv"

CANDIDATES_OUT = DATA / "crop_substitution_candidates.tsv"
AVAILABILITY_OUT = DATA / "crop_substitution_data_availability.tsv"
SUMMARY_OUT = DATA / "crop_substitution_engine_summary.json"
PLOT_OUT = DATA / "crop_substitution_data_availability.png"


def read_tsv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, sep="\t", dtype=str, keep_default_na=False)


def parse_json(value: Any) -> Any:
    if value is None or value == "":
        return {}
    return json.loads(str(value))


def load_inputs() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    return (
        pd.read_parquet(EDGES),
        read_tsv(CWR),
        read_tsv(CLIMATE),
        read_tsv(HELDOUT),
        read_tsv(SUMMARY),
    )


def climate_lookup(climate: pd.DataFrame) -> dict[str, dict[str, str]]:
    out: dict[str, dict[str, str]] = {}
    for _, row in climate.iterrows():
        key = row.get("accepted_taxon_key", "")
        name = row.get("taxon_canonical_name", "")
        record = {
            "taxon_canonical_name": name,
            "accepted_taxon_key": key,
            "climate_evidence_status": row.get("climate_evidence_status", ""),
            "bioclim_values_present": row.get("bioclim_values_present", ""),
            "shortfall_reason": row.get("shortfall_reason", ""),
        }
        if key:
            out[key] = record
        if name:
            out[f"name:{name}"] = record
    return out


def vavilov_by_crop(edges: pd.DataFrame) -> dict[str, dict[str, str]]:
    out: dict[str, dict[str, str]] = {}
    subset = edges[edges["edge_type"] == "vavilov_center_hyperedge"]
    for _, row in subset.iterrows():
        roles = parse_json(row["role_map_json"])
        out[row["accepted_taxon_key"]] = {
            "vavilov_center": roles.get("vavilov_center", ""),
            "vavilov_region": roles.get("region", ""),
            "vavilov_source_id": row.get("source_id", ""),
        }
    return out


def cwr_join_set(cwr: pd.DataFrame) -> set[tuple[str, str]]:
    joined = cwr[cwr["pair_join_status"] == "joined"]
    return {
        (row["crop_accepted_taxon_key"], row["wild_ancestor_accepted_key"])
        for _, row in joined.iterrows()
        if row["crop_accepted_taxon_key"] and row["wild_ancestor_accepted_key"]
    }


def score_candidate(
    selection_traits: list[str],
    has_joined_pair: bool,
    has_vavilov_context: bool,
) -> tuple[float, dict[str, float]]:
    """Return a non-climate score with interpretable components.

    Special point: when observed climate vectors are absent, climate is not
    assigned zero. It is excluded from the denominator and carried as a
    non-computable axis.
    """

    components = {
        "pedigree_component": 1.0,
        "joined_cwr_component": 1.0 if has_joined_pair else 0.0,
        "selection_trait_component": min(len(selection_traits), 3) / 3.0,
        "vavilov_context_component": 1.0 if has_vavilov_context else 0.0,
    }
    weights = {
        "pedigree_component": 0.45,
        "joined_cwr_component": 0.25,
        "selection_trait_component": 0.20,
        "vavilov_context_component": 0.10,
    }
    score = sum(components[name] * weight for name, weight in weights.items())
    return round(score, 6), components


def build_candidates(edges: pd.DataFrame, cwr: pd.DataFrame, climate: pd.DataFrame) -> pd.DataFrame:
    climate_by_key = climate_lookup(climate)
    joined_pairs = cwr_join_set(cwr)
    vavilov = vavilov_by_crop(edges)
    rows: list[dict[str, Any]] = []
    pedigree_edges = edges[edges["edge_type"] == "crop_pedigree"].copy()

    for _, row in pedigree_edges.iterrows():
        roles = parse_json(row["role_map_json"])
        crop_key = row["accepted_taxon_key"]
        crop_name = row["raw_scientific_name"]
        selection_traits = list(roles.get("selection_traits", []))
        wild_resolution = roles.get("wild_ancestor_resolution", [])
        crop_climate = climate_by_key.get(crop_key, {})

        for candidate in wild_resolution:
            wild_key = candidate.get("wild_ancestor_accepted_key", "")
            wild_name = candidate.get("wild_ancestor_name", "")
            if not wild_key:
                continue
            wild_climate = climate_by_key.get(wild_key) or climate_by_key.get(f"name:{wild_name}", {})
            has_joined_pair = (crop_key, wild_key) in joined_pairs
            vavilov_context = vavilov.get(crop_key, {})
            score, components = score_candidate(selection_traits, has_joined_pair, bool(vavilov_context))
            candidate_id = stable_id("track4_crop_substitution_candidate", crop_key, wild_key, row["edge_id"])
            rows.append(
                {
                    "candidate_id": candidate_id,
                    "track": "Track 4",
                    "crop_taxon": crop_name,
                    "crop_accepted_taxon_key": crop_key,
                    "candidate_wild_relative": wild_name,
                    "candidate_wild_relative_key": wild_key,
                    "candidate_wild_ancestor_node": candidate.get("wild_ancestor_node", ""),
                    "rank_within_crop": 0,
                    "substitution_score_non_climate": score,
                    "pedigree_component": components["pedigree_component"],
                    "joined_cwr_component": components["joined_cwr_component"],
                    "selection_trait_component": components["selection_trait_component"],
                    "vavilov_context_component": components["vavilov_context_component"],
                    "climate_match_status": "not_computable_no_observed_bioclim_vectors",
                    "climate_component": "",
                    "score_basis": "pedigree_cwr_selection_vavilov_only",
                    "selection_traits_json": json.dumps(selection_traits, sort_keys=True),
                    "vavilov_center": vavilov_context.get("vavilov_center", ""),
                    "vavilov_region": vavilov_context.get("vavilov_region", ""),
                    "supporting_edge_id": row["edge_id"],
                    "supporting_source_id": row["source_id"],
                    "allowed_evidence_scope": row["allowed_evidence_scope"],
                    "prediction_status": "pending_data_limited",
                    "validation_ready": False,
                    "expected_validation_source": "Wave 4 CGIAR/FAO held-out expert comparison after CWR and climate recovery",
                    "claim_boundary": "candidate ranking only; not a validated crop-substitution recommendation",
                    "crop_climate_status": crop_climate.get("climate_evidence_status", "missing"),
                    "wild_relative_climate_status": wild_climate.get("climate_evidence_status", "missing"),
                    "climate_shortfall_reason": "observed bioclim vectors absent for all Track 4 rows",
                }
            )

    candidates = pd.DataFrame(rows)
    if candidates.empty:
        return candidates
    candidates = candidates.sort_values(
        ["crop_taxon", "substitution_score_non_climate", "candidate_wild_relative"],
        ascending=[True, False, True],
    ).reset_index(drop=True)
    candidates["rank_within_crop"] = candidates.groupby("crop_taxon").cumcount() + 1
    return candidates


def build_availability(
    edges: pd.DataFrame,
    cwr: pd.DataFrame,
    climate: pd.DataFrame,
    heldout: pd.DataFrame,
    candidates: pd.DataFrame,
) -> pd.DataFrame:
    crop_edges = edges[edges["edge_type"] == "crop_pedigree"]
    crop_keys = sorted(set(crop_edges["accepted_taxon_key"].tolist()) | set(heldout["accepted_taxon_key"].tolist()))
    rows: list[dict[str, Any]] = []
    candidate_counts = Counter(candidates["crop_accepted_taxon_key"]) if not candidates.empty else Counter()
    joined_cwr_counts = Counter(
        cwr.loc[cwr["pair_join_status"] == "joined", "crop_accepted_taxon_key"].tolist()
    )
    climate_by_key = climate_lookup(climate)
    crop_name_by_key = {
        row["accepted_taxon_key"]: row["raw_scientific_name"]
        for _, row in crop_edges.iterrows()
        if row["accepted_taxon_key"]
    }
    for _, row in heldout.iterrows():
        if row["accepted_taxon_key"]:
            crop_name_by_key.setdefault(row["accepted_taxon_key"], row["crop_taxon"])

    for crop_key in crop_keys:
        if not crop_key:
            continue
        climate_record = climate_by_key.get(crop_key, {})
        has_pedigree = crop_key in set(crop_edges["accepted_taxon_key"])
        n_candidates = int(candidate_counts[crop_key])
        status = "candidate_scored_pedigree_only" if n_candidates else "data_limited_no_scored_candidate"
        rows.append(
            {
                "crop_taxon": crop_name_by_key.get(crop_key, ""),
                "crop_accepted_taxon_key": crop_key,
                "has_retained_crop_pedigree": has_pedigree,
                "joined_cwr_pair_count": int(joined_cwr_counts[crop_key]),
                "scored_candidate_count": n_candidates,
                "climate_evidence_status": climate_record.get("climate_evidence_status", "missing"),
                "bioclim_values_present": climate_record.get("bioclim_values_present", "False"),
                "instrument_status": status,
                "shortfall_reason": "no observed climate vectors; many held-out crops lack accepted keys or retained pedigree evidence"
                if status.startswith("data_limited")
                else "climate excluded from score; pedigree/CWR evidence only",
            }
        )
    return pd.DataFrame(rows).sort_values(["instrument_status", "crop_taxon"]).reset_index(drop=True)


def write_plot(availability: pd.DataFrame) -> None:
    plot_df = availability.sort_values("crop_taxon")
    fig, ax = plt.subplots(figsize=(10, 5))
    x = range(len(plot_df))
    ax.bar(x, plot_df["scored_candidate_count"].astype(int), label="scored candidates", color="#3b6f8f")
    ax.bar(x, plot_df["joined_cwr_pair_count"].astype(int), bottom=plot_df["scored_candidate_count"].astype(int), label="joined CWR pairs", color="#8a9b45")
    observed = plot_df["bioclim_values_present"].astype(str).str.lower().eq("true").astype(int)
    ax.plot(list(x), observed, color="#b65f3a", marker="o", label="observed climate vectors")
    ax.set_xticks(list(x))
    ax.set_xticklabels(plot_df["crop_taxon"], rotation=35, ha="right")
    ax.set_ylabel("count")
    ax.set_title("Track 4 Crop Substitution Engine data availability")
    ax.grid(axis="y", alpha=0.25)
    ax.legend()
    fig.tight_layout()
    fig.savefig(PLOT_OUT, dpi=180)
    plt.close(fig)


def write_report(
    candidates: pd.DataFrame,
    availability: pd.DataFrame,
    summary: pd.DataFrame,
    edges: pd.DataFrame,
    climate: pd.DataFrame,
    heldout: pd.DataFrame,
) -> None:
    counts = Counter(edges["edge_type"])
    observed_climate = int(climate["bioclim_values_present"].astype(str).str.lower().eq("true").sum())
    candidate_count = len(candidates)
    crop_count = candidates["crop_accepted_taxon_key"].nunique() if candidate_count else 0
    heldout_keyed = int((heldout["accepted_taxon_key"] != "").sum())
    joined_cwr = int(summary.loc[summary["category"] == "crop_wild_relative_pairs", "joined_rows"].iloc[0])
    total_cwr = int(summary.loc[summary["category"] == "crop_wild_relative_pairs", "staged_rows"].iloc[0])

    top_rows = ""
    if candidates.empty:
        top_rows = "| none | none | none | 0 | data-limited |\n"
    else:
        for _, row in candidates.iterrows():
            top_rows += (
                f"| {row['crop_taxon']} | {row['candidate_wild_relative']} | "
                f"{row['rank_within_crop']} | {row['substitution_score_non_climate']} | "
                f"{row['claim_boundary']} |\n"
            )

    availability_rows = ""
    for _, row in availability.iterrows():
        availability_rows += (
            f"| {row['crop_taxon']} | {row['has_retained_crop_pedigree']} | "
            f"{row['scored_candidate_count']} | {row['climate_evidence_status']} | "
            f"{row['instrument_status']} |\n"
        )

    text = f"""---
created: 2026-05-18T02:05:00Z
cycle: 9
run_id: fork-e08673192f98-clone-3-track4-crop-substitution-engine
agent: worker
milestone: M3.T4
---

# Track 4 Domestication Hypergraph

## Scope

This artifact is the first data-limited Crop Substitution Engine for Track 4. It reads only the frozen Barrier 2 Track 4 enrichment namespace and does not write to `phytograph_dataset/`, does not broaden `phytograph_schema.md`, and does not independently normalize synonyms.

The engine emits candidate wild relatives only where observed pedigree/CWR evidence is already joined to Barrier 1 accepted keys. It does not make climate-match recommendations because Track 4 currently has {observed_climate} observed bioclim vectors.

## Instrument Outputs

| Artifact | Purpose |
|---|---|
| `tracks/track4/data/crop_substitution_candidates.tsv` | Ranked data-limited wild-relative candidates from joined pedigree/CWR evidence. |
| `tracks/track4/data/crop_substitution_data_availability.tsv` | Per-crop readiness and shortfall table. |
| `tracks/track4/data/crop_substitution_engine_summary.json` | Machine-readable count summary for Barrier 3. |
| `tracks/track4/data/crop_substitution_data_availability.png` | Plot of candidate counts, joined CWR pairs, and observed climate-vector availability. |
| `scripts/track4_crop_substitution_engine.py` | Reproducible builder for the instrument outputs. |

## Mechanism

For each retained `crop_pedigree` edge, the instrument extracts joined wild-ancestor roles and scores each crop-wild relative pair by a non-climate evidence score:

`score = 0.45 * pedigree + 0.25 * joined_CWR + 0.20 * selection_trait_coverage + 0.10 * Vavilov_context`

Climate is not assigned a zero score. At the special point where observed bioclim vectors equal zero, climate is outside the denominator and is recorded as `not_computable_no_observed_bioclim_vectors`.

## Counts

| Quantity | Count |
|---|---:|
| Retained Track 4 hyperedges | {len(edges)} |
| Retained crop-pedigree edges | {counts.get('crop_pedigree', 0)} |
| Joined CWR pairs | {joined_cwr} / {total_cwr} |
| Scored candidates | {candidate_count} |
| Crops with scored candidates | {crop_count} |
| Held-out validation rows with accepted keys | {heldout_keyed} / {len(heldout)} |
| Observed bioclim vectors | {observed_climate} / {len(climate)} |

## Ranked Candidates

| Crop | Candidate wild relative | Rank | Non-climate score | Boundary |
|---|---|---:|---:|---|
{top_rows}
## Data Availability

| Crop | Retained pedigree? | Scored candidates | Climate status | Instrument status |
|---|---:|---:|---|---|
{availability_rows}
## Evidence Boundary

Rows in `crop_substitution_candidates.tsv` are `pending_data_limited` candidate rankings, not validated recommendations. The ranking supports only this claim: given the current retained Track 4 evidence, these wild relatives are the only candidate substitutes with joined pedigree/CWR support. It does not support suitability under a target climate envelope, cultivar performance, edibility, native range, or deployment advice.

## Data-Limited Findings

- Climate matching is unavailable because all Track 4 climate rows have `bioclim_values_present=False`.
- The current instrument can score only {crop_count} crops with retained crop-pedigree evidence.
- The held-out validation seed remains mostly unkeyed at Barrier 1 scale, so Wave 4 validation must either recover accepted keys/CWR evidence first or mark those cases data-limited.
- A sister-species baseline and multi-parent-edge ablation are not run here; they are Wave 4 falsification work.

## Figure

![Track 4 Crop Substitution Engine data availability: scored candidates and joined CWR pairs by crop, with observed climate-vector availability overlaid.](data/crop_substitution_data_availability.png)

## Barrier 3 Readiness

Track 4 is ready for Barrier 3 integration as a queryable, data-limited instrument. The Atlas may expose the candidate rows only if it preserves `prediction_status=pending_data_limited`, `climate_match_status=not_computable_no_observed_bioclim_vectors`, and the evidence boundary above.
"""
    DOC.write_text(text)


def write_summary_json(candidates: pd.DataFrame, availability: pd.DataFrame, climate: pd.DataFrame) -> None:
    observed_climate = int(climate["bioclim_values_present"].astype(str).str.lower().eq("true").sum())
    payload = {
        "milestone": "M3.T4",
        "instrument": "Track 4 Crop Substitution Engine",
        "status": "ready_data_limited",
        "candidate_rows": int(len(candidates)),
        "crops_with_candidates": int(candidates["crop_accepted_taxon_key"].nunique()) if not candidates.empty else 0,
        "availability_rows": int(len(availability)),
        "observed_bioclim_vectors": observed_climate,
        "climate_claims_emitted": False,
        "score_basis": "pedigree_cwr_selection_vavilov_only",
    }
    SUMMARY_OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def main() -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    edges, cwr, climate, heldout, summary = load_inputs()
    candidates = build_candidates(edges, cwr, climate)
    availability = build_availability(edges, cwr, climate, heldout, candidates)

    candidates.to_csv(CANDIDATES_OUT, sep="\t", index=False)
    availability.to_csv(AVAILABILITY_OUT, sep="\t", index=False)
    write_plot(availability)
    write_summary_json(candidates, availability, climate)
    write_report(candidates, availability, summary, edges, climate, heldout)

    print(f"candidate_rows={len(candidates)}")
    print(f"crops_with_candidates={candidates['crop_accepted_taxon_key'].nunique() if not candidates.empty else 0}")
    print(f"observed_bioclim_vectors={int(climate['bioclim_values_present'].astype(str).str.lower().eq('true').sum())}")
    print(f"wrote={CANDIDATES_OUT.relative_to(ROOT)}")
    print(f"wrote={DOC.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
