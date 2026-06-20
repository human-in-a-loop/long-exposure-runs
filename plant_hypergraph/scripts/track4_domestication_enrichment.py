#!/usr/bin/env python3
# created: 2026-05-17T23:58:00Z
# cycle: 8
# run_id: run-phytograph-cycle8-track4-domestication-enrichment
# agent: worker
# milestone: M2.T4
"""Build Track 4 domestication enrichment from frozen Barrier 1 outputs.

This script deliberately does not normalize names independently. It uses only
Barrier 1 accepted keys from `phytograph_dataset/synonym_resolution.parquet`
and `phytograph_dataset/nodes.parquet`, then joins the M1.6 domestication
staging tables into Track 4 namespace outputs.
"""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import pandas as pd

from barrier1_common import canonical_members_json, norm_name, stable_id


ROOT = Path(__file__).resolve().parents[1]
STAGING = ROOT / "substrate" / "staging" / "domestication_sources"
DATASET = ROOT / "phytograph_dataset"
OUT = ROOT / "tracks" / "track4"
OUT_DATA = OUT / "data"
OUT_DOCS = OUT / "docs"

EDGE_FILES = [
    STAGING / "edges" / "crop_pedigree.tsv",
    STAGING / "edges" / "vavilov_center_hyperedge.tsv",
    STAGING / "edges" / "cultivation_or_domestication.tsv",
]
HELDOUT = STAGING / "heldout_validation_set.tsv"
CLIMATE = STAGING / "climate_envelopes" / "per_taxon_bioclim.tsv"
WILD_NODES = STAGING / "nodes" / "wild_ancestor.tsv"


def read_tsv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, sep="\t", dtype=str, keep_default_na=False)


def load_key_map() -> dict[str, str]:
    """Load exact accepted-key authority from Barrier 1 artifacts."""
    key_map: dict[str, str] = {}

    syn = pd.read_parquet(
        DATASET / "synonym_resolution.parquet",
        columns=["normalized_name_key", "accepted_taxon_key"],
    )
    syn["accepted_taxon_key"] = syn["accepted_taxon_key"].fillna("").astype(str)
    for name, group in syn[syn["accepted_taxon_key"] != ""].groupby("normalized_name_key"):
        keys = sorted(set(group["accepted_taxon_key"]))
        if len(keys) == 1:
            key_map[str(name)] = keys[0]

    nodes = pd.read_parquet(DATASET / "nodes.parquet", columns=["label", "accepted_taxon_key"])
    nodes["accepted_taxon_key"] = nodes["accepted_taxon_key"].fillna("").astype(str)
    nodes["label"] = nodes["label"].fillna("").astype(str)
    node_subset = nodes[(nodes["accepted_taxon_key"] != "") & (nodes["label"] != "")]
    for label, accepted_key in zip(node_subset["label"], node_subset["accepted_taxon_key"]):
        key_map.setdefault(norm_name(label), accepted_key)

    return key_map


def load_wild_node_taxa() -> dict[str, str]:
    wild = read_tsv(WILD_NODES)
    return dict(zip(wild["node_id"], wild["canonical_taxon"]))


def resolve(name: str, key_map: dict[str, str]) -> str:
    return key_map.get(norm_name(name), "")


def parse_json(value: Any) -> Any:
    if value is None or value == "":
        return {}
    return json.loads(value)


def normalize_species_key(raw: str) -> str:
    text = raw.strip()
    if "(" in text:
        text = text.split("(", 1)[0].strip()
    lower = text.lower()
    for marker in (" subsp.", " var.", " cv.", " f.", " group"):
        idx = lower.find(marker)
        if idx > 0:
            text = text[:idx].strip()
            lower = text.lower()
    parts = text.split()
    if len(parts) < 2:
        return ""
    if parts[1].lower() == "x" and len(parts) >= 3:
        return f"{parts[0].lower()} {parts[2].lower()}"
    return f"{parts[0].lower()} {parts[1].lower()}"


def role_members_for_edge(edge_type: str, roles: dict[str, Any], accepted_key: str) -> dict[str, Any]:
    typed: dict[str, Any] = {}
    source = roles.get("source", "")
    region = roles.get("region", "")
    if edge_type == "crop_pedigree":
        typed["crop"] = accepted_key
        typed["wild_ancestors"] = roles.get("wild_ancestors", [])
        typed["selection_traits"] = [f"selection_trait:{t}" for t in roles.get("selection_traits", [])]
        typed["region"] = region
        typed["source"] = f"source:{source}"
    elif edge_type == "vavilov_center_hyperedge":
        typed["crop"] = accepted_key
        typed["vavilov_center"] = roles.get("vavilov_center", "")
        typed["region"] = region
        typed["source"] = f"source:{source}"
    elif edge_type == "cultivation_or_domestication":
        typed["crop"] = accepted_key
        typed["cultivation_status"] = roles.get("cultivation_status", "")
        typed["region"] = region
        typed["source"] = f"source:{source}"
    else:
        typed.update(roles)
    return typed


def build_edges(key_map: dict[str, str], wild_taxa: dict[str, str]) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    retained: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    cwr_rows: list[dict[str, Any]] = []

    for path in EDGE_FILES:
        source_df = read_tsv(path)
        for row_index, row in source_df.iterrows():
            edge_type = row["edge_type"]
            raw_name = row["raw_scientific_name"]
            accepted_key = resolve(raw_name, key_map)
            roles = parse_json(row["node_roles_json"])
            wild_nodes = roles.get("wild_ancestors", []) if isinstance(roles, dict) else []
            wild_joined = 0
            wild_total = len(wild_nodes)
            wild_role_details = []
            for node_id in wild_nodes:
                taxon_name = wild_taxa.get(node_id, "")
                wild_key = resolve(taxon_name, key_map) if taxon_name else ""
                if wild_key:
                    wild_joined += 1
                wild_role_details.append(
                    {
                        "wild_ancestor_node": node_id,
                        "wild_ancestor_name": taxon_name,
                        "wild_ancestor_accepted_key": wild_key,
                        "join_status": "joined" if wild_key else "unjoined",
                    }
                )
                if edge_type == "crop_pedigree":
                    cwr_rows.append(
                        {
                            "crop_taxon": raw_name,
                            "crop_accepted_taxon_key": accepted_key,
                            "wild_ancestor_node": node_id,
                            "wild_ancestor_name": taxon_name,
                            "wild_ancestor_accepted_key": wild_key,
                            "pair_join_status": "joined" if accepted_key and wild_key else "data-limited",
                            "source_id": row["source_id"],
                        }
                    )

            if not accepted_key:
                failures.append(
                    {
                        "input_table": str(path.relative_to(ROOT)),
                        "row_index": row_index,
                        "edge_type": edge_type,
                        "raw_scientific_name": raw_name,
                        "normalized_name_key": norm_name(raw_name),
                        "failure_reason": "no Barrier 1 accepted key for focal taxon",
                        "source_id": row["source_id"],
                    }
                )
                continue

            typed_roles = role_members_for_edge(edge_type, roles, accepted_key)
            if wild_role_details:
                typed_roles["wild_ancestor_resolution"] = wild_role_details
            edge_id = stable_id("track4_enrichment_edge", edge_type, raw_name, row["source_id"], row_index)
            canonical_json = canonical_members_json(
                edge_type=edge_type,
                raw_scientific_name=raw_name,
                accepted_taxon_key=accepted_key,
                role_map=typed_roles,
                extra_members=[row["source_id"]],
            )
            caveats = parse_json(row.get("caveats_json", "{}"))
            caveats["wave2_track4_scope"] = "observed enrichment only; no crop-substitution prediction"
            if wild_total and wild_joined < wild_total:
                caveats["cwr_pair_shortfall"] = f"{wild_total - wild_joined} of {wild_total} wild ancestor roles lack accepted keys"
            retained.append(
                {
                    "edge_id": edge_id,
                    "edge_type": edge_type,
                    "canonical_node_ids_json": canonical_json,
                    "raw_node_ids_json": json.dumps([row.get("canonical_node_id", "")], sort_keys=True),
                    "role_map_json": json.dumps(typed_roles, sort_keys=True),
                    "raw_scientific_name": raw_name,
                    "accepted_taxon_key": accepted_key,
                    "source_group": "track4_domestication_enrichment",
                    "source_id": row["source_id"],
                    "source_record_id": f"{path.stem}:{row_index}",
                    "access_date": row["access_date"],
                    "license": row["license"],
                    "provenance_pointer": row["attribution"],
                    "allowed_evidence_scope": row["allowed_evidence_scope"],
                    "caveats": json.dumps(caveats, sort_keys=True),
                    "temporal_annotation": row.get("temporal_annotation", "{}") or "{}",
                    "confidence": row["confidence"],
                    "source_reliability": row["source_reliability"],
                    "pending_crosswalk": False,
                    "evidence_multiplicity_allowed": False,
                    "inferred_flag": False,
                    "wild_ancestor_count": wild_total,
                    "wild_ancestor_joined_count": wild_joined,
                    "evidence_status": "observed",
                }
            )

    return pd.DataFrame(retained), pd.DataFrame(failures), pd.DataFrame(cwr_rows)


def build_climate(key_map: dict[str, str]) -> tuple[pd.DataFrame, pd.DataFrame]:
    climate = read_tsv(CLIMATE)
    out_rows = []
    failures = []
    bio_cols = [c for c in climate.columns if c.startswith("bio")]
    for idx, row in climate.iterrows():
        taxon = row["taxon_canonical_name"]
        accepted_key = resolve(taxon, key_map)
        has_values = any(str(row[c]).strip().upper() not in {"", "NA", "NAN"} for c in bio_cols)
        status = "observed" if accepted_key and has_values and int(row.get("n_occurrences", "0") or 0) > 0 else "data-limited"
        out_rows.append(
            {
                "taxon_canonical_name": taxon,
                "accepted_taxon_key": accepted_key,
                "n_occurrences": row["n_occurrences"],
                "occurrence_source": row["occurrence_source"],
                "envelope_source": row["envelope_source"],
                "envelope_version": row["envelope_version"],
                "extraction_date": row["extraction_date"],
                "climate_evidence_status": status,
                "bioclim_values_present": has_values,
                "shortfall_reason": "" if status == "observed" else "bioclim extraction unavailable in M1.6 staging",
                "license": row["license"],
                "attribution": row["attribution"],
            }
        )
        if not accepted_key:
            failures.append(
                {
                    "input_table": str(CLIMATE.relative_to(ROOT)),
                    "row_index": idx,
                    "edge_type": "climate_envelope",
                    "raw_scientific_name": taxon,
                    "normalized_name_key": norm_name(taxon),
                    "failure_reason": "no Barrier 1 accepted key for climate-envelope taxon",
                    "source_id": row["envelope_source"],
                }
            )
    return pd.DataFrame(out_rows), pd.DataFrame(failures)


def build_heldout(key_map: dict[str, str], training_edges: pd.DataFrame) -> pd.DataFrame:
    heldout = read_tsv(HELDOUT)
    train_species = {normalize_species_key(v) for v in training_edges["raw_scientific_name"].tolist()}
    train_species.discard("")
    rows = []
    for idx, row in heldout.iterrows():
        crop = row["crop_taxon"]
        species_key = normalize_species_key(crop)
        rows.append(
            {
                "crop_taxon": crop,
                "accepted_taxon_key": resolve(crop, key_map),
                "species_key": species_key,
                "heldout_class": row["heldout_class"],
                "cgiar_or_recommendation_source": row["cgiar_or_recommendation_source"],
                "region_of_practical_relevance": row["region_of_practical_relevance"],
                "notes": row["notes"],
                "overlaps_training_pedigree": species_key in train_species,
                "row_index": idx,
            }
        )
    return pd.DataFrame(rows)


def write_summary(
    edges: pd.DataFrame,
    failures: pd.DataFrame,
    cwr: pd.DataFrame,
    heldout: pd.DataFrame,
    climate: pd.DataFrame,
) -> pd.DataFrame:
    records = []
    for edge_type, total in [
        ("crop_pedigree", 43),
        ("vavilov_center_hyperedge", 43),
        ("cultivation_or_domestication", 104),
    ]:
        joined = int((edges["edge_type"] == edge_type).sum()) if not edges.empty else 0
        records.append(
            {
                "category": edge_type,
                "staged_rows": total,
                "joined_rows": joined,
                "unjoined_rows": total - joined,
                "shortfall": "focal accepted-key gaps" if total - joined else "",
            }
        )
    records.append(
        {
            "category": "crop_wild_relative_pairs",
            "staged_rows": len(cwr),
            "joined_rows": int((cwr["pair_join_status"] == "joined").sum()) if not cwr.empty else 0,
            "unjoined_rows": int((cwr["pair_join_status"] != "joined").sum()) if not cwr.empty else 0,
            "shortfall": "crop and/or wild ancestor accepted-key gaps",
        }
    )
    records.append(
        {
            "category": "heldout_validation_seed",
            "staged_rows": len(heldout),
            "joined_rows": int((heldout["accepted_taxon_key"] != "").sum()),
            "unjoined_rows": int((heldout["accepted_taxon_key"] == "").sum()),
            "shortfall": "held-out focal accepted-key gaps",
        }
    )
    records.append(
        {
            "category": "climate_envelope",
            "staged_rows": len(climate),
            "joined_rows": int((climate["accepted_taxon_key"] != "").sum()),
            "unjoined_rows": int((climate["accepted_taxon_key"] == "").sum()),
            "shortfall": "all rows data-limited until occurrence coordinates and bioclim values are extracted",
        }
    )
    summary = pd.DataFrame(records)
    summary.to_csv(OUT_DATA / "crop_cwr_coverage_summary.tsv", sep="\t", index=False)
    return summary


def write_figure(summary: pd.DataFrame) -> None:
    fig_path = OUT_DATA / "track4_enrichment_coverage.png"
    plot_df = summary[summary["category"].isin(["crop_pedigree", "vavilov_center_hyperedge", "crop_wild_relative_pairs", "heldout_validation_seed", "climate_envelope"])]
    x = range(len(plot_df))
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.bar(x, plot_df["joined_rows"], label="joined", color="#2b7a78")
    ax.bar(x, plot_df["unjoined_rows"], bottom=plot_df["joined_rows"], label="unjoined/data-limited", color="#b65f3a")
    ax.set_xticks(list(x))
    ax.set_xticklabels(plot_df["category"], rotation=25, ha="right")
    ax.set_ylabel("rows")
    ax.set_title("Track 4 enrichment coverage against Barrier 1 accepted keys")
    ax.legend()
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(fig_path, dpi=180)
    plt.close(fig)


def write_audit(summary: pd.DataFrame, edges: pd.DataFrame, failures: pd.DataFrame, cwr: pd.DataFrame, heldout: pd.DataFrame, climate: pd.DataFrame) -> None:
    counts = Counter(edges["edge_type"]) if not edges.empty else Counter()
    cwr_joined = int((cwr["pair_join_status"] == "joined").sum()) if not cwr.empty else 0
    climate_observed = int((climate["climate_evidence_status"] == "observed").sum())
    heldout_overlap = int(heldout["overlaps_training_pedigree"].sum())
    OUT_DOCS.mkdir(parents=True, exist_ok=True)
    text = f"""---
created: 2026-05-17T23:58:00Z
cycle: 8
run_id: run-phytograph-cycle8-track4-domestication-enrichment
agent: worker
milestone: M2.T4
---

# Track 4 Domestication Enrichment Audit

## Scope

This Wave 2 enrichment attaches local M1.6 domestication staging rows to the validated Barrier 1 substrate. It does not write to `phytograph_dataset/`, does not broaden schema v1.0, does not run a Crop Substitution Engine, and does not independently normalize synonyms.

## Generated Artifacts

| Artifact | Purpose |
|---|---|
| `tracks/track4/data/domestication_enrichment_edges.parquet` | Retained observed Track 4 hyperedges with accepted focal taxon keys. |
| `tracks/track4/data/crop_cwr_coverage_summary.tsv` | Joined vs unjoined coverage by evidence category. |
| `tracks/track4/data/heldout_validation_seed.tsv` | Held-out validation seed rows for later Track 4 validation. |
| `tracks/track4/data/climate_envelope_coverage.tsv` | Climate-envelope availability and data-limited status by taxon. |
| `tracks/track4/data/domestication_key_join_failures.tsv` | Rows excluded from retained edge output because Barrier 1 had no accepted focal key. |
| `tracks/track4/data/track4_enrichment_coverage.png` | Joined vs unjoined coverage figure. |

## Counts

| Category | Staged rows | Joined rows | Unjoined rows | Shortfall |
|---|---:|---:|---:|---|
"""
    for _, row in summary.iterrows():
        text += f"| {row['category']} | {row['staged_rows']} | {row['joined_rows']} | {row['unjoined_rows']} | {row['shortfall']} |\n"
    text += f"""
Retained hyperedges by type: crop_pedigree={counts.get('crop_pedigree', 0)}, vavilov_center_hyperedge={counts.get('vavilov_center_hyperedge', 0)}, cultivation_or_domestication={counts.get('cultivation_or_domestication', 0)}.

## Evidence Distinctions

Crop pedigree rows retain crop, wild ancestor, selection trait, Vavilov/region, and source roles in `role_map_json` and `canonical_node_ids_json`. Vavilov-center rows are separate from current distribution evidence and carry contested-center caveats from M1.6. Climate rows are not converted into predictions; they are marked `observed` only when accepted keys, occurrence counts, and bioclim values are present, otherwise `data-limited`.

## Data-Limited Gaps

Focal accepted-key gaps dominate this branch: {len(failures)} staged rows could not be retained as Track 4 hyperedges or keyed climate evidence because Barrier 1 had no accepted key for the focal name. CWR-pair coverage is sparse: {cwr_joined} of {len(cwr)} crop-wild ancestor pairs have both crop and wild ancestor accepted keys. Bioclim coverage remains unavailable: {climate_observed} of {len(climate)} rows have observed climate vectors; the rest are placeholders awaiting occurrence-coordinate extraction.

## Held-Out Validation Seed

The held-out seed table contains {len(heldout)} rows. Species-level overlap with retained crop-pedigree training evidence is {heldout_overlap}; this must remain zero before Wave 4 validation uses the seed set.

## Figure

![Track 4 joined and unjoined enrichment counts by evidence category. Bars show row counts for crop pedigree, Vavilov-center, CWR-pair, held-out seed, and climate-envelope rows against Barrier 1 accepted keys.](../data/track4_enrichment_coverage.png)

## Readiness Judgment

Track 4 is ready for Barrier 2 as a data-limited enrichment layer, not as a predictive instrument. It provides nonzero observed crop-pedigree and Vavilov-center edges with accepted focal keys, but the later Crop Substitution Engine must treat CWR-pair coverage and climate envelopes as incomplete rather than inferred.
"""
    (OUT_DOCS / "ENRICHMENT_AUDIT.md").write_text(text)


def main() -> None:
    OUT_DATA.mkdir(parents=True, exist_ok=True)
    OUT_DOCS.mkdir(parents=True, exist_ok=True)

    key_map = load_key_map()
    wild_taxa = load_wild_node_taxa()
    edges, edge_failures, cwr = build_edges(key_map, wild_taxa)
    climate, climate_failures = build_climate(key_map)
    failures = pd.concat([edge_failures, climate_failures], ignore_index=True)
    heldout = build_heldout(key_map, edges[edges["edge_type"] == "crop_pedigree"] if not edges.empty else edges)
    summary = write_summary(edges, failures, cwr, heldout, climate)

    edges.to_parquet(OUT_DATA / "domestication_enrichment_edges.parquet", index=False)
    cwr.to_csv(OUT_DATA / "crop_wild_relative_pairs.tsv", sep="\t", index=False)
    heldout.to_csv(OUT_DATA / "heldout_validation_seed.tsv", sep="\t", index=False)
    climate.to_csv(OUT_DATA / "climate_envelope_coverage.tsv", sep="\t", index=False)
    failures.to_csv(OUT_DATA / "domestication_key_join_failures.tsv", sep="\t", index=False)
    write_figure(summary)
    write_audit(summary, edges, failures, cwr, heldout, climate)

    print(f"retained_edges={len(edges)}")
    print("retained_by_type=" + json.dumps(dict(Counter(edges["edge_type"])), sort_keys=True))
    print(f"join_failures={len(failures)}")
    print(f"cwr_pairs={len(cwr)} joined={int((cwr['pair_join_status'] == 'joined').sum()) if not cwr.empty else 0}")
    print(f"heldout_rows={len(heldout)} overlaps_training={int(heldout['overlaps_training_pedigree'].sum())}")
    print(f"climate_rows={len(climate)} observed={int((climate['climate_evidence_status'] == 'observed').sum())}")


if __name__ == "__main__":
    main()
