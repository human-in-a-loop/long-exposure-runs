#!/usr/bin/env python3
"""
Track 5 chemodiversity enrichment — project Barrier 1 substrate's Track 5 edges into
the tracks/track5/ namespace.

Wave 2 M2.T5. Read-only against phytograph_dataset/.

Inputs:
  - phytograph_dataset/hyperedges.parquet
  - phytograph_dataset/nodes.parquet
  - phytograph_dataset/provenance.parquet
  - data/m1_7_raw/duke_source/FARMACY_NEW.csv (for compound -> CHEMCLASS mapping)

Outputs (under tracks/track5/data/):
  - track5_enrichment_edges.parquet           (resolved phyto + ethno; pending_crosswalk=False)
  - track5_bioactivity_assertions.parquet     (compound-level bioactivity; taxon FORBIDDEN)
  - track5_compound_class_membership.parquet  (Duke CHEMCLASS source-attributed)
  - track5_taxon_to_family.parquet            (helper view, derived from taxonomic_parentage)

No predictions. No `chemodiversity_signature` edges. No synonym renormalization.
No paid API calls. No writes outside tracks/track5/.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
SUBSTRATE = ROOT / "phytograph_dataset"
OUT = ROOT / "tracks" / "track5" / "data"
FARMACY = ROOT / "data" / "m1_7_raw" / "duke_source" / "FARMACY_NEW.csv"

TRACK5_EDGE_TYPES = {
    "phytochemical_assertion",
    "ethnobotanical_use_assertion",
    "bioactivity_assertion",
}

ALLOWED_SCOPES = {
    "phytochemical_assertion": {
        "Supports detection of this compound in this raw taxon label by this source.",
    },
    "ethnobotanical_use_assertion": {
        "Supports recorded human-use label in this source.",
        "Supports recorded use by the named people group as represented in NAEB.",
    },
    "bioactivity_assertion": {
        "Supports source-recorded bioactivity or assay annotation for the compound.",
    },
}


def _read_substrate() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    he = pd.read_parquet(SUBSTRATE / "hyperedges.parquet")
    nodes = pd.read_parquet(SUBSTRATE / "nodes.parquet")
    prov = pd.read_parquet(SUBSTRATE / "provenance.parquet")
    return he, nodes, prov


def _build_taxon_to_family(he: pd.DataFrame, nodes: pd.DataFrame) -> pd.DataFrame:
    par = he[he["edge_type"] == "taxonomic_parentage"]
    child2parent: dict[str, str] = {}
    for c in par["canonical_node_ids_json"]:
        arr = json.loads(c) if isinstance(c, str) else c
        if isinstance(arr, list) and len(arr) == 2:
            child2parent[arr[0]] = arr[1]
    fam_ids = set(nodes.loc[nodes["node_type"] == "family", "node_id"])
    fam_label = dict(
        zip(
            nodes.loc[nodes["node_type"] == "family", "node_id"],
            nodes.loc[nodes["node_type"] == "family", "label"],
        )
    )

    def find_family(k: str) -> str | None:
        cur = k
        for _ in range(20):
            if cur in fam_ids:
                return cur
            nxt = child2parent.get(cur)
            if nxt is None or nxt == cur:
                return None
            cur = nxt
        return None

    accepted_keys = set(
        nodes.loc[nodes["node_type"].isin(["species", "taxon", "genus", "infraspecific_unit", "cultivar"]), "node_id"]
    )
    rows = []
    for k in accepted_keys:
        fid = find_family(k)
        rows.append(
            {
                "accepted_taxon_key": k,
                "family_id": fid,
                "family": fam_label.get(fid) if fid else None,
            }
        )
    return pd.DataFrame(rows)


def _parse_members(s: str) -> list[str]:
    if not isinstance(s, str):
        return []
    try:
        v = json.loads(s)
    except Exception:
        return []
    return v if isinstance(v, list) else []


def _project_phyto_ethno(he: pd.DataFrame, taxon2fam: pd.DataFrame) -> pd.DataFrame:
    sel = he[
        he["edge_type"].isin({"phytochemical_assertion", "ethnobotanical_use_assertion"})
        & (~he["pending_crosswalk"])
    ].copy()
    fam_map = dict(zip(taxon2fam["accepted_taxon_key"], taxon2fam["family"]))
    rows = []
    for r in sel.itertuples(index=False):
        members = _parse_members(r.canonical_node_ids_json)
        compound_id = next((m for m in members if m.startswith("DUKE_CHEM:") or m.startswith("CHEBI:")), None)
        # plant part / role tokens: any member that is not a taxon key, not a compound, not a class hash
        non_struct = [
            m
            for m in members
            if not m.startswith("wfo:") and not m.startswith("DUKE_CHEM:") and not m.startswith("CHEBI:")
        ]
        plant_part = None
        people_or_region = None
        sovereignty_fields = {}
        if r.edge_type == "phytochemical_assertion":
            # Convention: non_struct entries are plant_part labels (e.g., 'Aril', 'Leaf', 'Seed')
            plant_part = non_struct[0] if non_struct else None
        else:
            # ethnobotanical_use_assertion: canonical = [region_or_people, "ethnobotanical_use",
            #                                            use_category, taxon_key]
            if non_struct:
                people_or_region = non_struct[0]
            # preserve all non-struct tokens as sovereignty payload
            sovereignty_fields = {
                "people_or_region": people_or_region,
                "use_category_tokens": non_struct,
                "source_id": r.source_id,
                "license": r.license,
                "access_date": r.access_date,
                "source_record_id": r.source_record_id,
            }
        # source class — minimal taxonomy of source type
        if r.source_id and "Duke" in r.source_id:
            source_class = "Dr. Duke"
        elif r.source_id and "NAEB" in r.source_id:
            source_class = "NAEB"
        else:
            source_class = r.source_id or "unknown"
        rows.append(
            {
                "edge_id": r.edge_id,
                "edge_type": r.edge_type,
                "accepted_taxon_key": r.accepted_taxon_key,
                "family": fam_map.get(r.accepted_taxon_key),
                "compound_id": compound_id,
                "compound_class": None,  # joined later from compound_class_membership
                "bioactivity_class": None,  # not applicable to phyto/ethno
                "plant_part": plant_part,
                "concentration": None,  # not preserved in substrate canonical; flagged data-limited
                "source_id": r.source_id,
                "source_class": source_class,
                "license": r.license,
                "access_date": r.access_date,
                "evidence_scope": r.allowed_evidence_scope,
                "sovereignty_fields_json": json.dumps(sovereignty_fields, sort_keys=True) if sovereignty_fields else "{}",
                "retained": True,
                "pending_crosswalk": bool(r.pending_crosswalk),
            }
        )
    return pd.DataFrame(rows)


def _project_bioactivity(he: pd.DataFrame) -> pd.DataFrame:
    sel = he[he["edge_type"] == "bioactivity_assertion"].copy()
    rows = []
    for r in sel.itertuples(index=False):
        members = _parse_members(r.canonical_node_ids_json)
        compound_id = next((m for m in members if m.startswith("DUKE_CHEM:") or m.startswith("CHEBI:")), None)
        bioactivity_class = next(
            (m for m in members if not (m.startswith("DUKE_CHEM:") or m.startswith("CHEBI:") or m.startswith("wfo:"))),
            None,
        )
        # Firewall: bioactivity is keyed at compound level. accepted_taxon_key is intentionally empty.
        assert (r.accepted_taxon_key or "") == "", (
            "FIREWALL VIOLATION: bioactivity_assertion row carries a taxon key — would silently leak "
            "compound bioactivity into a taxon-keyed clinical-efficacy implication."
        )
        rows.append(
            {
                "edge_id": r.edge_id,
                "edge_type": "bioactivity_assertion",
                "compound_id": compound_id,
                "bioactivity_class": bioactivity_class,
                "source_id": r.source_id,
                "license": r.license,
                "access_date": r.access_date,
                "evidence_scope": (
                    "compound bioactivity literature; does not support clinical efficacy"
                ),
                "schema_evidence_scope": r.allowed_evidence_scope,
                "retained": True,
            }
        )
    return pd.DataFrame(rows)


def _build_compound_class_membership() -> pd.DataFrame:
    rows = []
    seen = set()
    with FARMACY.open() as f:
        rd = csv.DictReader(f)
        for row in rd:
            chemid = (row.get("CHEMID") or row.get("CHEM") or "").strip()
            cls = (row.get("CHEMCLASS") or "").strip()
            if not chemid or not cls:
                continue
            compound_id = f"DUKE_CHEM:{chemid}"
            key = (compound_id, cls)
            if key in seen:
                continue
            seen.add(key)
            rows.append(
                {
                    "compound_id": compound_id,
                    "compound_class": cls,
                    "source": "Dr. Duke FARMACY_NEW.CHEMCLASS",
                    "license": "CC0",
                }
            )
    return pd.DataFrame(rows)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    he, nodes, prov = _read_substrate()

    taxon2fam = _build_taxon_to_family(he, nodes)
    taxon2fam.to_parquet(OUT / "track5_taxon_to_family.parquet", index=False)
    print(f"taxon_to_family rows: {len(taxon2fam)}, mapped to family: {taxon2fam['family'].notna().sum()}")

    enr = _project_phyto_ethno(he, taxon2fam)
    # Attach compound_class via Duke CHEMCLASS join (left-join keeps None for unclassified compounds)
    cc = _build_compound_class_membership()
    cc.to_parquet(OUT / "track5_compound_class_membership.parquet", index=False)
    print(f"compound_class_membership rows: {len(cc)} (distinct compounds: {cc['compound_id'].nunique()})")

    # For the enrichment edges, attach a single compound_class via first match
    cc_first = cc.drop_duplicates("compound_id", keep="first")[["compound_id", "compound_class"]]
    enr = enr.drop(columns=["compound_class"]).merge(cc_first, on="compound_id", how="left")
    enr.to_parquet(OUT / "track5_enrichment_edges.parquet", index=False)
    print(
        f"enrichment_edges rows: {len(enr)} "
        f"(phyto={int((enr['edge_type']=='phytochemical_assertion').sum())}, "
        f"ethno={int((enr['edge_type']=='ethnobotanical_use_assertion').sum())})"
    )

    bio = _project_bioactivity(he)
    bio.to_parquet(OUT / "track5_bioactivity_assertions.parquet", index=False)
    print(f"bioactivity_assertions rows: {len(bio)}")


if __name__ == "__main__":
    main()
