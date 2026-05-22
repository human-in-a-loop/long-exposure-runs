# created: 2026-05-17T21:00:00Z
# cycle: 4
# run_id: run-phytograph-cycle4-barrier1
# agent: worker
# milestone: _plan/barrier1-substrate-freeze
"""Merge Wave-1 staging rows into canonical Barrier-1 PhytoGraph tables."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

from barrier1_common import (
    DATASET,
    ROOT,
    STAGING,
    coerce_float,
    canonical_member_list,
    canonical_members_json,
    ensure_dirs,
    first_present,
    json_dumps,
    load_name_maps,
    parse_jsonish,
    read_table,
    resolve_name,
    source_group_from_path,
    stable_id,
    write_parquet,
    write_tsv,
)


RUN_ID = "run-phytograph-cycle4-barrier1"


EDGE_FILES = [
    STAGING / "reticulation_sources" / "normalized" / "chromosome_count_assertions.tsv",
    STAGING / "reticulation_sources" / "normalized" / "hybridization_events.tsv",
    STAGING / "reticulation_sources" / "normalized" / "polyploidization_events.tsv",
    STAGING / "reticulation_sources" / "normalized" / "ploidy_state_assertions.tsv",
    STAGING / "reticulation_sources" / "normalized" / "reticulate_inheritance_evidence.tsv",
    STAGING / "paleobotany_sources" / "anachronism_canon" / "anachronism_candidate_edges.jsonl",
    STAGING / "paleobotany_sources" / "faurby_svenning" / "distribution_edges.jsonl",
    STAGING / "convergence_sources" / "data" / "staged_edges.tsv",
    STAGING / "domestication_sources" / "edges" / "crop_pedigree.tsv",
    STAGING / "domestication_sources" / "edges" / "cultivation_or_domestication.tsv",
    STAGING / "domestication_sources" / "edges" / "vavilov_center_hyperedge.tsv",
    STAGING / "chemodiversity_ethnobotany_sources" / "phytochemical_assertion_edges.tsv",
    STAGING / "chemodiversity_ethnobotany_sources" / "bioactivity_assertion_edges.tsv",
    STAGING / "chemodiversity_ethnobotany_sources" / "ethnobotanical_use_assertion_edges.tsv",
    STAGING / "wikidata_commons" / "data" / "image_evidence_edges.tsv",
]

NODE_FILES = [
    STAGING / "paleobotany_sources" / "faurby_svenning" / "region_nodes.jsonl",
    STAGING / "paleobotany_sources" / "faurby_svenning" / "taxon_nodes.jsonl",
    STAGING / "paleobotany_sources" / "lqe" / "extinct_fauna.jsonl",
    STAGING / "paleobotany_sources" / "lqe" / "paleo_context.jsonl",
    STAGING / "paleobotany_sources" / "pbdb" / "extinct_fauna.jsonl",
    STAGING / "paleobotany_sources" / "pbdb" / "paleo_context.jsonl",
    STAGING / "paleobotany_sources" / "iucn" / "animal_consumer_disperser.jsonl",
    STAGING / "paleobotany_sources" / "anachronism_canon" / "taxon_stubs.jsonl",
    STAGING / "paleobotany_sources" / "anachronism_canon" / "fruit_type_stubs.jsonl",
    STAGING / "convergence_sources" / "data" / "staged_nodes.tsv",
    STAGING / "domestication_sources" / "nodes" / "breeder_pedigree_node.tsv",
    STAGING / "domestication_sources" / "nodes" / "cultivar.tsv",
    STAGING / "domestication_sources" / "nodes" / "landrace.tsv",
    STAGING / "domestication_sources" / "nodes" / "vavilov_center.tsv",
    STAGING / "domestication_sources" / "nodes" / "wild_ancestor.tsv",
    STAGING / "chemodiversity_ethnobotany_sources" / "phytochemical_compound_nodes.tsv",
    STAGING / "chemodiversity_ethnobotany_sources" / "chemical_class_nodes.tsv",
    STAGING / "chemodiversity_ethnobotany_sources" / "bioactivity_class_nodes.tsv",
    STAGING / "chemodiversity_ethnobotany_sources" / "ethnobotanical_use_record_nodes.tsv",
]


def node_row(
    node_id: str,
    node_type: str,
    label: str,
    source_group: str,
    source_id: str = "",
    raw: Any = None,
    accepted_taxon_key: str = "",
) -> dict[str, Any]:
    return {
        "node_id": node_id,
        "node_type": node_type,
        "label": label,
        "accepted_taxon_key": accepted_taxon_key,
        "source_group": source_group,
        "source_id": source_id,
        "raw_payload_json": json_dumps(raw or {}),
    }


def build_taxonomy_nodes_edges() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    accepted = read_table(STAGING / "taxonomy_backbone" / "accepted_taxa.parquet")
    synonyms = read_table(STAGING / "taxonomy_backbone" / "synonym_clusters.parquet")
    conflicts = read_table(STAGING / "taxonomy_backbone" / "taxonomic_conflicts.parquet")

    rank_to_type = {
        "family": "family",
        "genus": "genus",
        "species": "species",
        "variety": "infraspecific_unit",
        "subspecies": "infraspecific_unit",
        "form": "infraspecific_unit",
    }
    accepted_nodes = pd.DataFrame(
        {
            "node_id": accepted["accepted_taxon_key"],
            "node_type": accepted["rank"].str.lower().map(rank_to_type).fillna("taxon"),
            "label": accepted["accepted_name"],
            "accepted_taxon_key": accepted["accepted_taxon_key"],
            "source_group": "taxonomy_backbone",
            "source_id": accepted["source_identifier"],
            "raw_payload_json": "{}",
        }
    )
    synonym_node_id = "synonym:" + synonyms["source_name_id"].astype(str)
    synonym_nodes = pd.DataFrame(
        {
            "node_id": synonym_node_id,
            "node_type": "synonym",
            "label": synonyms["name_string"],
            "accepted_taxon_key": synonyms["accepted_taxon_key"],
            "source_group": "taxonomy_backbone",
            "source_id": synonyms["source_identifier"],
            "raw_payload_json": "{}",
        }
    )
    parent = "wfo:" + accepted["parent_wfo_id"].fillna("").astype(str)
    parent_members = [
        json.dumps(sorted([child, par])) if par != "wfo:" else json.dumps([child])
        for child, par in zip(accepted["accepted_taxon_key"], parent)
    ]
    parent_edges = pd.DataFrame(
        {
            "edge_id": [stable_id("edge:taxonomic_parentage", c, p) for c, p in zip(accepted["accepted_taxon_key"], parent)],
            "edge_type": "taxonomic_parentage",
            "canonical_node_ids_json": parent_members,
            "raw_node_ids_json": parent_members,
            "role_map_json": "{}",
            "raw_scientific_name": accepted["accepted_name"],
            "accepted_taxon_key": accepted["accepted_taxon_key"],
            "source_group": "taxonomy_backbone",
            "source_id": accepted["source_identifier"],
            "source_record_id": accepted["source_identifier"],
            "access_date": accepted["access_date"],
            "license": accepted["license"],
            "provenance_pointer": accepted["provenance_url"],
            "allowed_evidence_scope": "hierarchy consistency under WFO operational backbone only",
            "caveats": "WFO anchor is operational, not taxonomic adjudication over other backbones.",
            "temporal_annotation": "",
            "confidence": 0.9,
            "source_reliability": 0.9,
            "pending_crosswalk": False,
            "evidence_multiplicity_allowed": False,
            "inferred_flag": False,
        }
    )
    syn_members = [json.dumps(sorted([a, s])) for a, s in zip(synonyms["accepted_taxon_key"], synonym_node_id)]
    synonym_edges = pd.DataFrame(
        {
            "edge_id": [stable_id("edge:synonym_cluster", a, s, sid) for a, s, sid in zip(synonyms["accepted_taxon_key"], synonym_node_id, synonyms["source_identifier"])],
            "edge_type": "synonym_cluster",
            "canonical_node_ids_json": syn_members,
            "raw_node_ids_json": syn_members,
            "role_map_json": "{}",
            "raw_scientific_name": synonyms["name_string"],
            "accepted_taxon_key": synonyms["accepted_taxon_key"],
            "source_group": "taxonomy_backbone",
            "source_id": synonyms["source_identifier"],
            "source_record_id": synonyms["source_name_id"],
            "access_date": synonyms["access_date"],
            "license": synonyms["license"],
            "provenance_pointer": synonyms["provenance_url"],
            "allowed_evidence_scope": synonyms["allowed_evidence_scope"],
            "caveats": "Name normalization only.",
            "temporal_annotation": "",
            "confidence": 0.9,
            "source_reliability": 0.9,
            "pending_crosswalk": False,
            "evidence_multiplicity_allowed": False,
            "inferred_flag": False,
        }
    )
    conflict_edges = pd.DataFrame(
        {
            "edge_id": [stable_id("edge:taxonomic_conflict", a, e) for a, e in zip(conflicts["accepted_taxon_key"], conflicts["evidence"])],
            "edge_type": "taxonomic_conflict",
            "canonical_node_ids_json": conflicts["accepted_taxon_key"].map(lambda x: json.dumps([x])),
            "raw_node_ids_json": conflicts["accepted_taxon_key"].map(lambda x: json.dumps([x])),
            "role_map_json": "{}",
            "raw_scientific_name": "",
            "accepted_taxon_key": conflicts["accepted_taxon_key"],
            "source_group": "taxonomy_backbone",
            "source_id": conflicts["source_identifier"],
            "source_record_id": conflicts["source_identifier"],
            "access_date": conflicts["access_date"],
            "license": conflicts["license"],
            "provenance_pointer": "taxonomy_backbone/taxonomic_conflicts.parquet",
            "allowed_evidence_scope": "acknowledged disagreement across backbones only",
            "caveats": conflicts["evidence"].astype(str),
            "temporal_annotation": "",
            "confidence": 0.7,
            "source_reliability": 0.85,
            "pending_crosswalk": False,
            "evidence_multiplicity_allowed": False,
            "inferred_flag": False,
        }
    )
    nodes = pd.concat([accepted_nodes, synonym_nodes], ignore_index=True, sort=False).to_dict("records")
    edges = pd.concat([parent_edges, synonym_edges, conflict_edges], ignore_index=True, sort=False).to_dict("records")
    return nodes, edges


def make_edge(
    *,
    edge_id: str,
    edge_type: str,
    members: list[str],
    role_map: dict[str, Any],
    source_group: str,
    source_id: str,
    source_record_id: str,
    access_date: str,
    license: str,
    provenance_pointer: str,
    allowed_evidence_scope: str,
    caveats: str,
    temporal_annotation: str,
    confidence: float,
    source_reliability: float,
    raw_scientific_name: str,
    accepted_taxon_key: str,
    pending_crosswalk: bool = False,
    evidence_multiplicity_allowed: bool = False,
    inferred_flag: bool = False,
) -> dict[str, Any]:
    canonical_members = canonical_member_list(
        edge_type=edge_type,
        raw_scientific_name=raw_scientific_name,
        accepted_taxon_key=accepted_taxon_key,
        role_map=role_map,
        extra_members=members,
    )
    return {
        "edge_id": edge_id,
        "edge_type": edge_type,
        "canonical_node_ids_json": json.dumps(canonical_members),
        "raw_node_ids_json": json.dumps(members),
        "role_map_json": json_dumps(role_map),
        "raw_scientific_name": raw_scientific_name,
        "accepted_taxon_key": accepted_taxon_key,
        "source_group": source_group,
        "source_id": source_id,
        "source_record_id": source_record_id,
        "access_date": access_date,
        "license": license,
        "provenance_pointer": provenance_pointer,
        "allowed_evidence_scope": allowed_evidence_scope,
        "caveats": caveats,
        "temporal_annotation": "" if pd.isna(temporal_annotation) else str(temporal_annotation),
        "confidence": confidence,
        "source_reliability": source_reliability,
        "pending_crosswalk": bool(pending_crosswalk),
        "evidence_multiplicity_allowed": bool(evidence_multiplicity_allowed),
        "inferred_flag": bool(inferred_flag),
    }


def add_member_nodes_from_role_map(nodes: list[dict[str, Any]], edge: dict[str, Any], role_map: Any) -> None:
    def walk(value: Any) -> None:
        if isinstance(value, dict):
            for inner in value.values():
                walk(inner)
        elif isinstance(value, list):
            for inner in value:
                walk(inner)
        elif isinstance(value, str) and ":" in value:
            prefix = value.split(":", 1)[0]
            type_map = {
                "trait": "trait",
                "fruit_type": "fruit_type",
                "wild_ancestor": "wild_ancestor",
                "cultivar": "cultivar",
                "landrace": "landrace",
                "vc": "vavilov_center",
                "source": "source",
                "commons_media": "image_media",
                "wikidata": "taxon",
                "raw_name": "taxon",
            }
            node_type = type_map.get(prefix, "source" if prefix in {"ccdb", "austraits_6_0_0"} else "taxon")
            nodes.append(node_row(value, node_type, value.split(":", 1)[1], edge["source_group"], edge["source_id"]))

    walk(role_map)


def convert_json_edge(path: Path, row: pd.Series, accepted_map: dict[str, str], synonym_map: dict[str, str]) -> dict[str, Any]:
    source_group = source_group_from_path(path)
    provenance = row.get("provenance", {}) if isinstance(row.get("provenance", {}), dict) else {}
    caveats = row.get("C", {}) if isinstance(row.get("C", {}), dict) else {}
    temporal = row.get("T", {}) if isinstance(row.get("T", {}), dict) else {}
    members_raw = row.get("members", [])
    members: list[str] = []
    raw_name = ""
    role_map: dict[str, Any] = {}
    if isinstance(members_raw, list):
        for member in members_raw:
            if isinstance(member, dict):
                node_id = str(member.get("node_id", ""))
                role = str(member.get("role", "member"))
                members.append(node_id)
                role_map.setdefault(role, []).append(node_id)
                if member.get("node_type") == "taxon" and not raw_name:
                    raw_name = node_id.rsplit(":", 1)[-1].replace("_", " ")
    accepted, status, reason = resolve_name(raw_name, accepted_map, synonym_map)
    if reason:
        caveats = {**caveats, "canonicalization_status": status, "ambiguity_reason": reason}
    return make_edge(
        edge_id=str(row.get("edge_id") or stable_id("edge", path, len(members), raw_name)),
        edge_type=str(row.get("edge_type", "")),
        members=members,
        role_map=role_map,
        source_group=source_group,
        source_id=str(provenance.get("source_id", "")),
        source_record_id=str(provenance.get("source_id", row.get("edge_id", ""))),
        access_date=str(provenance.get("access_date", "")),
        license=str(provenance.get("license", "")),
        provenance_pointer=str(provenance.get("source_name", path.relative_to(ROOT))),
        allowed_evidence_scope=("cited hypothesis only; not inferred by Barrier 1" if row.get("edge_type") == "anachronism_candidate_edge" else "source-stated edge assertion only"),
        caveats=json_dumps(caveats),
        temporal_annotation=json_dumps(temporal),
        confidence=coerce_float(provenance.get("confidence"), 0.7),
        source_reliability=coerce_float(provenance.get("source_reliability"), 0.7),
        raw_scientific_name=raw_name,
        accepted_taxon_key=accepted,
        pending_crosswalk=not bool(accepted),
        inferred_flag=False,
    )


def convert_tabular_edge(path: Path, row: pd.Series, accepted_map: dict[str, str], synonym_map: dict[str, str]) -> dict[str, Any]:
    source_group = source_group_from_path(path)
    edge_type = str(first_present(row, ["edge_type"]))
    raw_name = str(first_present(row, ["raw_scientific_name", "taxon_name", "taxon_label_raw", "taxon_name_matched", "taxon_node_id"]))
    accepted, status, reason = resolve_name(raw_name, accepted_map, synonym_map)
    source_id = str(first_present(row, ["source_id", "source_name", "source_node_id", "wikidata_qid"], source_group))
    source_record_id = str(first_present(row, ["source_record_id", "observation_id", "edge_id", "source_identifier"], ""))
    role_map = parse_jsonish(first_present(row, ["node_roles_json", "role_map_json"], "{}"))
    if not role_map:
        role_map = {}
    members: list[str] = []
    if isinstance(role_map, dict):
        for value in role_map.values():
            if isinstance(value, list):
                members.extend(str(v) for v in value)
            elif isinstance(value, str):
                members.append(value)
    canonical_node = str(first_present(row, ["canonical_node_id", "taxon_node_id"], ""))
    if canonical_node:
        members.append(canonical_node)
    if accepted:
        members.append(accepted)
    if edge_type == "phytochemical_assertion":
        members.extend([str(row.get("compound_id", "")), str(row.get("plant_part", "")), str(row.get("taxon_id_if_available", ""))])
    elif edge_type == "bioactivity_assertion":
        members.extend([str(row.get("compound_id", "")), str(row.get("bioactivity_class", ""))])
    elif edge_type == "ethnobotanical_use_assertion":
        members.extend([str(row.get("taxon_id_if_available", "")), str(row.get("people_group", "")), str(row.get("region", "")), str(row.get("use_category", "")), str(row.get("plant_part", ""))])
    elif edge_type == "image_evidence":
        members.extend([str(row.get("taxon_node_id", "")), str(row.get("image_media_node_id", "")), str(row.get("source_node_id", ""))])
    members = [m for m in members if m and m.lower() != "nan"]

    caveats = str(first_present(row, ["caveats_json", "caveats", "caveat"], ""))
    if reason:
        caveats = f"{caveats}; canonicalization_status={status}; ambiguity_reason={reason}".strip("; ")
    allowed_scope = str(first_present(row, ["allowed_evidence_scope"], "source-stated assertion only"))
    if edge_type == "image_evidence" and "media_display" not in allowed_scope:
        allowed_scope = "media_display;weak_morphology_inspection"

    return make_edge(
        edge_id=str(first_present(row, ["edge_id"], stable_id("edge", path, source_record_id, raw_name, edge_type))),
        edge_type=edge_type,
        members=members,
        role_map=role_map,
        source_group=source_group,
        source_id=source_id,
        source_record_id=source_record_id,
        access_date=str(first_present(row, ["access_date", "retrieved_at"], "")),
        license=str(first_present(row, ["license", "license_class", "license_short_name"], "")),
        provenance_pointer=str(first_present(row, ["provenance_url", "source_url", "commons_page_url", "citation", "source_citation"], path.relative_to(ROOT))),
        allowed_evidence_scope=allowed_scope,
        caveats=caveats,
        temporal_annotation=str(first_present(row, ["temporal_annotation"], "")),
        confidence=coerce_float(first_present(row, ["confidence", "confidence_level"], 0.7), 0.7),
        source_reliability=coerce_float(first_present(row, ["source_reliability"], 0.7), 0.7),
        raw_scientific_name=raw_name,
        accepted_taxon_key=accepted,
        pending_crosswalk=not bool(accepted),
        evidence_multiplicity_allowed=edge_type in {"chromosome_count_assertion", "phytochemical_assertion", "ethnobotanical_use_assertion", "bioactivity_assertion"},
        inferred_flag="inferred" in caveats.lower() and "not inferred" not in caveats.lower(),
    )


def convert_tabular_edges_frame(path: Path, df: pd.DataFrame, accepted_map: dict[str, str], synonym_map: dict[str, str]) -> pd.DataFrame:
    source_group = source_group_from_path(path)
    raw_col = next((c for c in ["raw_scientific_name", "taxon_name", "taxon_label_raw", "taxon_node_id"] if c in df.columns), None)
    if len(df) > 100000:
        raw_name_fast = df[raw_col].fillna("").astype(str) if raw_col else pd.Series([""] * len(df))
        edge_type_fast = df["edge_type"].astype(str)
        edge_id_fast = df["edge_id"].fillna("").astype(str) if "edge_id" in df.columns else pd.Series([stable_id("edge", path, i) for i in range(len(df))])
        source_id_fast = df["source_id"].fillna(source_group).astype(str) if "source_id" in df.columns else df["source_name"].fillna(source_group).astype(str) if "source_name" in df.columns else pd.Series([source_group] * len(df))
        record_fast = df["source_record_id"].fillna("").astype(str) if "source_record_id" in df.columns else df["observation_id"].fillna("").astype(str) if "observation_id" in df.columns else edge_id_fast
        access_fast = df["access_date"].fillna("").astype(str) if "access_date" in df.columns else pd.Series([""] * len(df))
        license_fast = df["license"].fillna("").astype(str) if "license" in df.columns else df["license_class"].fillna("").astype(str) if "license_class" in df.columns else pd.Series(["license-missing-in-source-row"] * len(df))
        license_fast = license_fast.where(license_fast.str.strip() != "", "license-missing-in-source-row")
        scope_fast = df["allowed_evidence_scope"].fillna("source-stated assertion only").astype(str) if "allowed_evidence_scope" in df.columns else pd.Series(["source-stated assertion only"] * len(df))
        caveats_fast = df["caveats"].fillna("").astype(str) if "caveats" in df.columns else pd.Series([""] * len(df))
        confidence_fast = df["confidence"].map(lambda x: coerce_float(x, 0.7)) if "confidence" in df.columns else pd.Series([0.7] * len(df))
        reliability_fast = df["source_reliability"].map(lambda x: coerce_float(x, 0.7)) if "source_reliability" in df.columns else pd.Series([0.7] * len(df))
        role_map_fast = df["role_map_json"].fillna("{}").astype(str) if "role_map_json" in df.columns else df["node_roles_json"].fillna("{}").astype(str) if "node_roles_json" in df.columns else pd.Series(["{}"] * len(df))
        extra_cols = [c for c in ["canonical_node_id", "taxon_node_id", "compound_id", "chemical_class", "plant_part", "use_category", "people_group", "region", "bioactivity_class", "image_media_node_id", "source_node_id"] if c in df.columns]
        canonical_json = [
            canonical_members_json(
                edge_type=edge_type_fast.iloc[i],
                raw_scientific_name=raw_name_fast.iloc[i],
                accepted_taxon_key="",
                role_map=role_map_fast.iloc[i],
                extra_members=[df[c].iloc[i] for c in extra_cols],
            )
            for i in range(len(df))
        ]
        raw_json = [canonical_members_json(edge_type=edge_type_fast.iloc[i], raw_scientific_name=raw_name_fast.iloc[i], role_map=role_map_fast.iloc[i], extra_members=[df[c].iloc[i] for c in extra_cols]) for i in range(len(df))]
        return pd.DataFrame(
            {
                "edge_id": edge_id_fast,
                "edge_type": edge_type_fast,
                "canonical_node_ids_json": canonical_json,
                "raw_node_ids_json": raw_json,
                "role_map_json": role_map_fast,
                "raw_scientific_name": raw_name_fast,
                "accepted_taxon_key": "",
                "source_group": source_group,
                "source_id": source_id_fast,
                "source_record_id": record_fast,
                "access_date": access_fast,
                "license": license_fast,
                "provenance_pointer": df["source_url"].fillna("").astype(str) if "source_url" in df.columns else df["citation"].fillna("").astype(str) if "citation" in df.columns else str(path.relative_to(ROOT)),
                "allowed_evidence_scope": scope_fast,
                "caveats": caveats_fast,
                "temporal_annotation": "",
                "confidence": confidence_fast.astype(float),
                "source_reliability": reliability_fast.astype(float),
                "pending_crosswalk": True,
                "evidence_multiplicity_allowed": edge_type_fast.isin({"phytochemical_assertion", "ethnobotanical_use_assertion", "bioactivity_assertion"}),
                "inferred_flag": False,
            }
        )
    edge_type = df["edge_type"].astype(str) if "edge_type" in df.columns else pd.Series([""] * len(df))
    raw_name = df[raw_col].fillna("").astype(str) if raw_col else pd.Series([""] * len(df))
    normalized = raw_name.str.strip().str.lower()
    accepted = normalized.map(accepted_map).fillna(normalized.map(synonym_map)).fillna("")
    source_id = (
        df[[c for c in ["source_id", "source_name", "source_node_id", "wikidata_qid"] if c in df.columns]]
        .bfill(axis=1)
        .iloc[:, 0]
        .fillna(source_group)
        .astype(str)
        if any(c in df.columns for c in ["source_id", "source_name", "source_node_id", "wikidata_qid"])
        else pd.Series([source_group] * len(df))
    )
    source_record_id = (
        df[[c for c in ["source_record_id", "observation_id", "edge_id", "source_identifier"] if c in df.columns]]
        .bfill(axis=1)
        .iloc[:, 0]
        .fillna("")
        .astype(str)
        if any(c in df.columns for c in ["source_record_id", "observation_id", "edge_id", "source_identifier"])
        else pd.Series([""] * len(df))
    )
    edge_ids = df["edge_id"].fillna("").astype(str) if "edge_id" in df.columns else pd.Series([""] * len(df))
    missing_edge_id = edge_ids == ""
    if missing_edge_id.any():
        edge_ids.loc[missing_edge_id] = [
            stable_id("edge", path, i, source_record_id.iloc[i], raw_name.iloc[i], edge_type.iloc[i])
            for i in list(edge_ids[missing_edge_id].index)
        ]
    access_date = (
        df[[c for c in ["access_date", "retrieved_at"] if c in df.columns]].bfill(axis=1).iloc[:, 0].fillna("").astype(str)
        if any(c in df.columns for c in ["access_date", "retrieved_at"])
        else pd.Series([""] * len(df))
    )
    license_col = (
        df[[c for c in ["license", "license_class", "license_short_name"] if c in df.columns]].bfill(axis=1).iloc[:, 0].fillna("").astype(str)
        if any(c in df.columns for c in ["license", "license_class", "license_short_name"])
        else pd.Series([""] * len(df))
    )
    license_col = license_col.where(license_col.str.strip() != "", "license-missing-in-source-row")
    allowed = df["allowed_evidence_scope"].fillna("source-stated assertion only").astype(str) if "allowed_evidence_scope" in df.columns else pd.Series(["source-stated assertion only"] * len(df))
    caveats = (
        df[[c for c in ["caveats_json", "caveats", "caveat"] if c in df.columns]].bfill(axis=1).iloc[:, 0].fillna("").astype(str)
        if any(c in df.columns for c in ["caveats_json", "caveats", "caveat"])
        else pd.Series([""] * len(df))
    )
    provenance = (
        df[[c for c in ["provenance_url", "source_url", "commons_page_url", "citation", "source_citation"] if c in df.columns]]
        .bfill(axis=1)
        .iloc[:, 0]
        .fillna(str(path.relative_to(ROOT)))
        .astype(str)
        if any(c in df.columns for c in ["provenance_url", "source_url", "commons_page_url", "citation", "source_citation"])
        else pd.Series([str(path.relative_to(ROOT))] * len(df))
    )
    confidence = df["confidence"].map(lambda x: coerce_float(x, 0.7)) if "confidence" in df.columns else pd.Series([0.7] * len(df))
    reliability = df["source_reliability"].map(lambda x: coerce_float(x, 0.7)) if "source_reliability" in df.columns else pd.Series([0.7] * len(df))

    role_map_json = (
        df["role_map_json"].fillna("{}").astype(str)
        if "role_map_json" in df.columns
        else df["node_roles_json"].fillna("{}").astype(str)
        if "node_roles_json" in df.columns
        else pd.Series(["{}"] * len(df))
    )
    extra_cols = [c for c in ["canonical_node_id", "taxon_node_id", "compound_id", "chemical_class", "plant_part", "use_category", "people_group", "region", "bioactivity_class", "image_media_node_id", "source_node_id"] if c in df.columns]
    canonical_json = [
        canonical_members_json(
            edge_type=edge_type.iloc[i],
            raw_scientific_name=raw_name.iloc[i],
            accepted_taxon_key=accepted.iloc[i],
            role_map=role_map_json.iloc[i],
            extra_members=[df[c].iloc[i] for c in extra_cols],
        )
        for i in range(len(df))
    ]
    raw_node_json = [
        canonical_members_json(
            edge_type=edge_type.iloc[i],
            raw_scientific_name=raw_name.iloc[i],
            role_map=role_map_json.iloc[i],
            extra_members=[df[c].iloc[i] for c in extra_cols],
        )
        for i in range(len(df))
    ]
    temporal = df["temporal_annotation"].fillna("").astype(str) if "temporal_annotation" in df.columns else pd.Series([""] * len(df))
    allowed = allowed.where(~((edge_type == "image_evidence") & ~allowed.str.contains("media_display", na=False)), "media_display;weak_morphology_inspection")
    out = pd.DataFrame(
        {
            "edge_id": edge_ids,
            "edge_type": edge_type,
            "canonical_node_ids_json": canonical_json,
            "raw_node_ids_json": raw_node_json,
            "role_map_json": role_map_json,
            "raw_scientific_name": raw_name,
            "accepted_taxon_key": accepted,
            "source_group": source_group,
            "source_id": source_id,
            "source_record_id": source_record_id,
            "access_date": access_date,
            "license": license_col,
            "provenance_pointer": provenance,
            "allowed_evidence_scope": allowed,
            "caveats": caveats,
            "temporal_annotation": temporal,
            "confidence": confidence.astype(float),
            "source_reliability": reliability.astype(float),
            "pending_crosswalk": ~accepted.astype(bool),
            "evidence_multiplicity_allowed": edge_type.isin({"chromosome_count_assertion", "phytochemical_assertion", "ethnobotanical_use_assertion", "bioactivity_assertion"}),
            "inferred_flag": caveats.str.lower().str.contains("inferred", na=False) & ~caveats.str.lower().str.contains("not inferred", na=False),
        }
    )
    return out


def build_nodes_from_file(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    source_group = source_group_from_path(path)
    df = read_table(path)
    if "row_kind" in df.columns:
        df = df[df["row_kind"].fillna("node").isin(["node", "Node", ""])]
    if df.empty:
        return pd.DataFrame()
    id_cols = [c for c in ["node_id", "id", "compound_id", "record_id", "vocabulary_id", "source_record_id"] if c in df.columns]
    if id_cols:
        node_id = df[id_cols].bfill(axis=1).iloc[:, 0].fillna("").astype(str)
    else:
        node_id = pd.Series([stable_id(path.stem, i, path) for i in range(len(df))])
    label_cols = [c for c in ["label", "compound_label", "name", "value", "use_text_normalized"] if c in df.columns]
    label = df[label_cols].bfill(axis=1).iloc[:, 0].fillna(node_id).astype(str) if label_cols else node_id
    node_type = df["node_type"].fillna(path.stem).astype(str) if "node_type" in df.columns else pd.Series([path.stem] * len(df))
    node_type = node_type.replace({"unresolved_taxon_name": "taxon"})
    source_cols = [c for c in ["source_id", "source_name"] if c in df.columns]
    source_id = df[source_cols].bfill(axis=1).iloc[:, 0].fillna("").astype(str) if source_cols else pd.Series([""] * len(df))
    out = pd.DataFrame(
        {
            "node_id": node_id,
            "node_type": node_type,
            "label": label,
            "accepted_taxon_key": "",
            "source_group": source_group,
            "source_id": source_id,
            "raw_payload_json": "{}",
        }
    )
    return out


def build_crosswalk() -> pd.DataFrame:
    crosswalk = read_table(STAGING / "taxonomy_backbone" / "source_crosswalk.parquet").copy()
    wikidata = read_table(STAGING / "wikidata_commons" / "data" / "wikidata_taxon_crosswalk.tsv")
    accepted_map, synonym_map = load_name_maps()
    rows = []
    for _, row in wikidata.iterrows():
        accepted, status, reason = resolve_name(row.get("taxon_name"), accepted_map, synonym_map)
        rows.append(
            {
                "accepted_taxon_key": accepted,
                "wfo_id": "",
                "ott_id": "",
                "powo_id": row.get("powo_id", ""),
                "gbif_taxon_key": "",
                "qid": row.get("wikidata_qid", ""),
                "wikidata_url": row.get("wikidata_url", ""),
                "raw_name": row.get("taxon_name", ""),
                "match_method": f"wikidata_name_{status}",
                "ambiguity_reason": reason,
                "source": "wikidata_commons",
                "source_identifier": row.get("wikidata_qid", ""),
                "access_date": str(row.get("retrieved_at", ""))[:10],
                "license": "Wikidata CC0; Commons licenses per media row",
                "ingest_clone_id": "fork-e34b5b2c1c6c-clone-7",
            }
        )
    crosswalk["qid"] = ""
    crosswalk["wikidata_url"] = ""
    crosswalk["raw_name"] = crosswalk["wfo_accepted_name"]
    crosswalk["ambiguity_reason"] = ""
    return pd.concat([crosswalk, pd.DataFrame(rows)], ignore_index=True, sort=False)


def build_source_registry(edges: pd.DataFrame) -> pd.DataFrame:
    staging_dirs = [p for p in STAGING.iterdir() if p.is_dir() and p.name != "taxonomy_backbone_smoke"]
    rows = []
    for directory in staging_dirs:
        ingest = directory / "INGEST_AUDIT.md"
        rows.append(
            {
                "source_group": directory.name,
                "ingest_audit_path": str(ingest.relative_to(ROOT)) if ingest.exists() else "",
                "rows_in_hyperedges": int((edges["source_group"] == directory.name).sum()) if not edges.empty else 0,
                "status": "merged" if ingest.exists() else "metadata_only",
            }
        )
    return pd.DataFrame(rows)


def main() -> None:
    ensure_dirs()
    accepted_map, synonym_map = load_name_maps()
    print("loaded name maps", flush=True)
    nodes, edges = build_taxonomy_nodes_edges()
    print(f"built taxonomy nodes={len(nodes)} edges={len(edges)}", flush=True)
    node_frames = [pd.DataFrame(nodes)]
    edge_frames = [pd.DataFrame(edges)]

    for path in NODE_FILES:
        frame = build_nodes_from_file(path)
        if not frame.empty:
            node_frames.append(frame)
            print(f"node frame {path.relative_to(ROOT)} rows={len(frame)}", flush=True)

    json_edges: list[dict[str, Any]] = []
    for path in EDGE_FILES:
        if not path.exists():
            continue
        df = read_table(path)
        if path.suffix == ".jsonl":
            for _, row in df.iterrows():
                json_edges.append(convert_json_edge(path, row, accepted_map, synonym_map))
            print(f"json edge file {path.relative_to(ROOT)} rows={len(df)}", flush=True)
        else:
            frame = convert_tabular_edges_frame(path, df, accepted_map, synonym_map)
            edge_frames.append(frame)
            print(f"edge frame {path.relative_to(ROOT)} rows={len(frame)}", flush=True)
    if json_edges:
        edge_frames.append(pd.DataFrame(json_edges))

    nodes_df = pd.concat(node_frames, ignore_index=True, sort=False).drop_duplicates(subset=["node_id"], keep="first")
    edges_df = pd.concat(edge_frames, ignore_index=True, sort=False).drop_duplicates(subset=["edge_id"], keep="first")
    print(f"concatenated nodes={len(nodes_df)} edges={len(edges_df)}", flush=True)
    provenance_df = edges_df[
        [
            "edge_id",
            "source_group",
            "source_id",
            "source_record_id",
            "access_date",
            "license",
            "provenance_pointer",
            "confidence",
            "source_reliability",
        ]
    ].copy()
    caveats_df = edges_df[["edge_id", "caveats", "allowed_evidence_scope", "temporal_annotation", "pending_crosswalk"]].copy()
    crosswalk_df = build_crosswalk()
    source_registry = build_source_registry(edges_df)

    write_parquet(nodes_df, DATASET / "nodes.parquet")
    write_parquet(edges_df, DATASET / "hyperedges.parquet")
    write_parquet(crosswalk_df, DATASET / "taxon_crosswalk.parquet")
    write_parquet(provenance_df, DATASET / "provenance.parquet")
    write_parquet(caveats_df, DATASET / "caveats.parquet")
    write_parquet(source_registry, DATASET / "source_registry.parquet")

    summary = pd.DataFrame(
        [
            {"table": "nodes", "rows": len(nodes_df)},
            {"table": "hyperedges", "rows": len(edges_df)},
            {"table": "taxon_crosswalk", "rows": len(crosswalk_df)},
            {"table": "provenance", "rows": len(provenance_df)},
            {"table": "caveats", "rows": len(caveats_df)},
            {"table": "source_registry", "rows": len(source_registry)},
        ]
    )
    write_tsv(summary, ROOT / "substrate" / "barrier1_merge_counts.tsv")
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
