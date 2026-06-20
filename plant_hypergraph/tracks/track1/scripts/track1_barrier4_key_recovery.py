#!/usr/bin/env python3
"""
created: 2026-05-18T12:00:00+00:00
cycle: 20
run_id: fork-0b556d9370a2-clone-0-track1-barrier4-closure
agent: worker
milestone: _plan/track1-barrier4-closure

Track 1 Barrier 4 sidecar accepted-key recovery probe.

Reads the frozen 60k accepted-key resolver and the cached full WFO Plant List
dump. Writes Track 1-local sidecar tables only; it does not mutate the frozen
substrate or promote any prediction ledger rows.
"""
from __future__ import annotations

import json
import math
import zipfile
from pathlib import Path

import pandas as pd

WORKSPACE = Path(__file__).resolve().parents[3]
TRACK1 = WORKSPACE / "tracks" / "track1"
DATA = TRACK1 / "data"
TAXONOMY = WORKSPACE / "substrate" / "staging" / "taxonomy_backbone"

CURRENT_STATUS = DATA / "canonical_seed_case_status.tsv"
ENRICHMENT = DATA / "reticulation_enrichment_edges.parquet"
ACCEPTED = TAXONOMY / "accepted_taxa.parquet"
SYNONYMS = TAXONOMY / "synonym_clusters.parquet"
WFO_ZIP = TAXONOMY / "raw" / "wfo" / "wfo_plantlist_2025-12.zip"

RECOVERY_TSV = DATA / "barrier4_canonical_key_recovery.tsv"
RESCUED_EDGES_TSV = DATA / "barrier4_rescued_reticulation_edges.tsv"

CANONICAL_SEEDS = [
    "Triticum aestivum",
    "Brassica napus",
    "Spartina anglica",
    "Tragopogon mirus",
    "Tragopogon miscellus",
    "Musa acuminata × balbisiana",
    "Musa acuminata",
    "Musa balbisiana",
]

EVENT_EDGE_TYPES = {
    "hybridization_event",
    "polyploidization_event",
    "reticulate_inheritance_evidence",
}


def normalize_name(value: str) -> str:
    return " ".join(str(value).strip().lower().replace("×", "x").split())


def wfo_key(wfo_id: str) -> str:
    return f"wfo:{wfo_id}"


def load_current_status() -> pd.DataFrame:
    df = pd.read_csv(CURRENT_STATUS, sep="\t", dtype=str).fillna("")
    present = set(df["canonical_seed_taxon"])
    rows = []
    for seed in CANONICAL_SEEDS:
        if seed in present:
            rows.append(df[df["canonical_seed_taxon"] == seed].iloc[0].to_dict())
        else:
            rows.append(
                {
                    "canonical_seed_taxon": seed,
                    "status": "missing_from_staging",
                    "accepted_taxon_key": "",
                    "edge_types_attached": "",
                    "row_count": "0",
                }
            )
    return pd.DataFrame(rows)


def current_subset_lookup() -> dict[str, str]:
    accepted = pd.read_parquet(ACCEPTED, columns=["accepted_taxon_key", "accepted_name"])
    synonyms = pd.read_parquet(SYNONYMS, columns=["accepted_taxon_key", "name_string"])
    lookup = {}
    for key, name in zip(accepted["accepted_taxon_key"], accepted["accepted_name"]):
        lookup.setdefault(normalize_name(name), key)
    for key, name in zip(synonyms["accepted_taxon_key"], synonyms["name_string"]):
        lookup.setdefault(normalize_name(name), key)
    return lookup


def full_wfo_lookup(seeds: list[str]) -> dict[str, dict[str, str]]:
    wanted = {normalize_name(seed): seed for seed in seeds}
    with zipfile.ZipFile(WFO_ZIP) as archive:
        name_hits = []
        for chunk in pd.read_csv(
            archive.open("name.tsv"),
            sep="\t",
            dtype=str,
            chunksize=200_000,
            usecols=["ID", "scientificName", "rank"],
        ):
            norm = chunk["scientificName"].fillna("").map(normalize_name)
            hit = chunk[norm.isin(wanted)].copy()
            if not hit.empty:
                hit["_seed_taxon"] = norm[norm.isin(wanted)].map(wanted).loc[hit.index]
                name_hits.append(hit)
        names = pd.concat(name_hits, ignore_index=True) if name_hits else pd.DataFrame()
        name_ids = set(names["ID"]) if not names.empty else set()

        taxon_hits = []
        for chunk in pd.read_csv(
            archive.open("taxon.tsv"),
            sep="\t",
            dtype=str,
            chunksize=200_000,
            usecols=["ID", "nameID", "parentID", "link"],
        ):
            hit = chunk[chunk["nameID"].isin(name_ids)].copy()
            if not hit.empty:
                taxon_hits.append(hit)
        taxa = pd.concat(taxon_hits, ignore_index=True) if taxon_hits else pd.DataFrame()

        synonym_hits = []
        for chunk in pd.read_csv(
            archive.open("synonym.tsv"),
            sep="\t",
            dtype=str,
            chunksize=200_000,
            usecols=["ID", "taxonID", "nameID", "link"],
        ):
            hit = chunk[chunk["nameID"].isin(name_ids)].copy()
            if not hit.empty:
                synonym_hits.append(hit)
        synonyms = pd.concat(synonym_hits, ignore_index=True) if synonym_hits else pd.DataFrame()

    out = {
        seed: {
            "full_wfo_name_hit": "false",
            "full_wfo_taxon_hit": "false",
            "rescued_accepted_key": "",
            "rescue_status": "not_recovered_absent_from_full_wfo",
            "wfo_name_id": "",
            "wfo_taxon_id": "",
            "wfo_synonym_taxon_id": "",
        }
        for seed in seeds
    }
    if names.empty:
        return out

    taxon_by_name = {}
    if not taxa.empty:
        taxon_by_name = dict(zip(taxa["nameID"], taxa["ID"]))
    synonym_by_name = {}
    if not synonyms.empty:
        synonym_by_name = dict(zip(synonyms["nameID"], synonyms["taxonID"]))

    for _, row in names.iterrows():
        seed = row["_seed_taxon"]
        name_id = row["ID"]
        out[seed]["full_wfo_name_hit"] = "true"
        out[seed]["wfo_name_id"] = name_id
        if name_id in taxon_by_name:
            taxon_id = taxon_by_name[name_id]
            out[seed]["full_wfo_taxon_hit"] = "true"
            out[seed]["wfo_taxon_id"] = taxon_id
            out[seed]["rescued_accepted_key"] = wfo_key(taxon_id)
            out[seed]["rescue_status"] = "rescued_exact_full_wfo_taxon"
        elif name_id in synonym_by_name:
            taxon_id = synonym_by_name[name_id]
            out[seed]["wfo_synonym_taxon_id"] = taxon_id
            out[seed]["rescued_accepted_key"] = wfo_key(taxon_id)
            out[seed]["rescue_status"] = "rescued_synonym_to_full_wfo_taxon"
        else:
            out[seed]["rescue_status"] = "name_only_no_full_wfo_taxon"
    return out


def is_event_shaped(edge_type: str, node_roles_json: str) -> bool:
    if edge_type in {"hybridization_event", "polyploidization_event"}:
        return True
    if edge_type != "reticulate_inheritance_evidence":
        return False
    try:
        roles = json.loads(node_roles_json) if isinstance(node_roles_json, str) else {}
    except Exception:
        roles = {}
    return any(k in roles for k in ("child_taxon", "parent_taxa", "parent_taxon", "reticulate_parent"))


def blocker_class(current_status: str, rescue_status: str, event_count: int) -> str:
    if current_status == "missing_from_staging":
        return "absent_raw_name"
    if rescue_status == "rescued_exact_full_wfo_taxon":
        return "frozen_subset_truncation" if event_count else "frozen_subset_truncation_non_event_only"
    if rescue_status == "rescued_synonym_to_full_wfo_taxon":
        return "name_status_mismatch"
    if rescue_status == "name_only_no_full_wfo_taxon":
        return "name_only_without_taxon_row"
    return "absent_from_full_wfo_exact_lookup"


def main() -> None:
    current = load_current_status()
    frozen_lookup = current_subset_lookup()
    full_lookup = full_wfo_lookup(CANONICAL_SEEDS)
    edges = pd.read_parquet(ENRICHMENT).fillna("")

    records = []
    rescued_edges = []
    for _, seed_row in current.iterrows():
        seed = seed_row["canonical_seed_taxon"]
        current_status = seed_row["status"]
        current_key = seed_row.get("accepted_taxon_key", "")
        frozen_key = frozen_lookup.get(normalize_name(seed), "")
        if not current_key and frozen_key:
            current_key = frozen_key
            current_status = "resolved"

        seed_edges = edges[edges["raw_scientific_name"] == seed].copy()
        edge_types = sorted(set(seed_edges["edge_type"])) if not seed_edges.empty else []
        event_count = sum(
            1
            for _, edge in seed_edges.iterrows()
            if is_event_shaped(edge["edge_type"], edge.get("node_roles_json", ""))
        )
        lookup = full_lookup[seed]
        rescued_key = lookup["rescued_accepted_key"]
        status = lookup["rescue_status"]
        if current_key:
            status = "already_resolved_in_frozen_subset"
            rescued_key = current_key

        record = {
            "seed_taxon": seed,
            "current_status": current_status,
            "current_accepted_key": current_key,
            "full_wfo_name_hit": lookup["full_wfo_name_hit"],
            "full_wfo_taxon_hit": lookup["full_wfo_taxon_hit"],
            "rescued_accepted_key": rescued_key,
            "rescue_status": status,
            "edge_types_attached": ",".join(edge_types),
            "event_shaped_edges_attached": str(event_count),
            "blocker_class": blocker_class(current_status, lookup["rescue_status"], event_count),
        }
        records.append(record)

        if rescued_key and not seed_edges.empty:
            sidecar = seed_edges.copy()
            sidecar["rescued_accepted_key"] = rescued_key
            sidecar["rescue_basis"] = "full_wfo_cached_dump"
            sidecar["event_shaped_edge"] = [
                is_event_shaped(edge.edge_type, getattr(edge, "node_roles_json", ""))
                for edge in sidecar.itertuples(index=False)
            ]
            rescued_edges.append(sidecar)

    recovery = pd.DataFrame(records)
    RECOVERY_TSV.parent.mkdir(parents=True, exist_ok=True)
    recovery.to_csv(RECOVERY_TSV, sep="\t", index=False)

    if rescued_edges:
        cols = [
            "edge_type",
            "raw_scientific_name",
            "accepted_taxon_key",
            "rescued_accepted_key",
            "pending_crosswalk",
            "source_id",
            "allowed_evidence_scope",
            "caveats_json",
            "node_roles_json",
            "rescue_basis",
            "event_shaped_edge",
        ]
        out = pd.concat(rescued_edges, ignore_index=True)
        out.to_csv(RESCUED_EDGES_TSV, sep="\t", index=False, columns=[c for c in cols if c in out.columns])
    elif RESCUED_EDGES_TSV.exists():
        RESCUED_EDGES_TSV.unlink()

    current_resolved = int((recovery["current_accepted_key"].fillna("") != "").sum())
    sidecar_rescued = int((recovery["rescued_accepted_key"].fillna("") != "").sum())
    event_rescued = int(
        (
            (recovery["rescued_accepted_key"].fillna("") != "")
            & (recovery["event_shaped_edges_attached"].astype(int) > 0)
        ).sum()
    )
    print(
        f"WROTE: {RECOVERY_TSV} "
        f"(current_resolved={current_resolved}, sidecar_resolved={sidecar_rescued}, "
        f"event_shaped_resolved={event_rescued})"
    )
    if rescued_edges:
        print(f"WROTE: {RESCUED_EDGES_TSV}")


if __name__ == "__main__":
    main()
