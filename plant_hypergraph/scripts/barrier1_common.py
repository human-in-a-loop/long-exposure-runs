# created: 2026-05-17T21:00:00Z
# cycle: 4
# run_id: run-phytograph-cycle4-barrier1
# agent: worker
# milestone: _plan/barrier1-substrate-freeze
"""Shared helpers for PhytoGraph Barrier 1 substrate canonicalization."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
STAGING = ROOT / "substrate" / "staging"
DATASET = ROOT / "phytograph_dataset"


ALLOWED_NODE_TYPES = {
    "taxon",
    "accepted_name",
    "synonym",
    "common_name",
    "rank",
    "family",
    "genus",
    "species",
    "infraspecific_unit",
    "fruit_type",
    "life_form",
    "trait",
    "region",
    "native_origin_area",
    "introduced_area",
    "habitat",
    "animal_consumer",
    "animal_pollinator",
    "mycorrhizal_partner",
    "herbivore",
    "extinct_fauna",
    "human_use_category",
    "edibility_status",
    "toxicity_caveat",
    "cultivation_status",
    "wild_ancestor",
    "cultivar",
    "landrace",
    "breeder_pedigree_node",
    "vavilov_center",
    "phytochemical_compound",
    "chemical_class",
    "bioactivity_class",
    "ethnobotanical_use_record",
    "image_media",
    "source",
    "story_note",
    "conservation_status",
    "phylo_node",
    "clade_context",
    "chromosome_count",
    "ploidy_state",
    "hybridization_event",
    "polyploidization_event",
    "paleo_context",
    "probe_question",
    "probe_ground_truth",
    "foundation_model_response",
    "prompt_template",
    "confidence_calibration_record",
}


ALLOWED_EDGE_TYPES = {
    "taxonomic_parentage",
    "synonym_cluster",
    "common_name_assertion",
    "missing_rank_bridge",
    "taxonomic_conflict",
    "phylogenetic_or_reticulate_context",
    "fruit_morphology",
    "life_form",
    "habitat_association",
    "native_origin",
    "distribution",
    "introduced_or_invasive_status",
    "animal_consumption_or_dispersal",
    "pollination_partnership",
    "mycorrhizal_partnership",
    "herbivore_defense_relationship",
    "anachronism_candidate_edge",
    "hybridization_event",
    "polyploidization_event",
    "reticulate_inheritance_evidence",
    "chromosome_count_assertion",
    "human_use",
    "edibility_status",
    "toxicity_or_preparation_caveat",
    "cultivation_or_domestication",
    "crop_pedigree",
    "vavilov_center_hyperedge",
    "phytochemical_assertion",
    "chemodiversity_signature",
    "bioactivity_assertion",
    "ethnobotanical_use_assertion",
    "convergence_signature",
    "trait_syndrome",
    "adversarial_probe_edge",
    "probe_calibration_edge",
    "occurrence_provenance",
    "regional_checklist_context",
    "image_evidence",
    "source_assertion",
    "story_or_cultural_note",
    "metadata_missingness",
    "paleoclimate_overlap_edge",
}


BIOLOGY_FORBIDDEN_IMAGE_SCOPES = {
    "taxonomy",
    "distribution",
    "native_status",
    "edibility",
    "toxicity",
    "phytochemistry",
    "ecological_interaction",
    "human_use",
    "biological_importance",
}


def ensure_dirs() -> None:
    DATASET.mkdir(parents=True, exist_ok=True)
    (ROOT / "substrate").mkdir(parents=True, exist_ok=True)


def norm_name(value: Any) -> str:
    if value is None or pd.isna(value):
        return ""
    text = str(value).strip().lower()
    text = re.sub(r"\s+", " ", text)
    return text


def stable_id(prefix: str, *parts: Any) -> str:
    raw = "\u241f".join("" if p is None else str(p) for p in parts)
    return f"{prefix}:{hashlib.sha1(raw.encode('utf-8')).hexdigest()[:20]}"


def json_dumps(value: Any) -> str:
    if value is None:
        return "{}"
    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            return "{}"
        try:
            return json.dumps(json.loads(stripped), sort_keys=True)
        except Exception:
            return json.dumps({"text": stripped}, sort_keys=True)
    return json.dumps(value, sort_keys=True)


def parse_jsonish(value: Any) -> Any:
    if value is None or (not isinstance(value, (dict, list)) and pd.isna(value)):
        return {}
    if isinstance(value, (dict, list)):
        return value
    try:
        return json.loads(str(value))
    except Exception:
        return {"value": str(value)}


def canonical_member_list(
    *,
    edge_type: str,
    raw_scientific_name: Any = "",
    accepted_taxon_key: Any = "",
    role_map: Any = None,
    extra_members: list[Any] | None = None,
) -> list[str]:
    """Build the deduplication member set from the full typed role map."""
    members: list[str] = []

    def add(value: Any) -> None:
        if value is None:
            return
        if isinstance(value, float) and pd.isna(value):
            return
        text = str(value).strip()
        if not text or text.lower() == "nan":
            return
        members.append(text)

    def walk(value: Any) -> None:
        if isinstance(value, dict):
            for inner in value.values():
                walk(inner)
        elif isinstance(value, list):
            for inner in value:
                walk(inner)
        elif isinstance(value, (str, int, float)):
            add(value)

    parsed_role_map = parse_jsonish(role_map)
    walk(parsed_role_map)
    for value in extra_members or []:
        walk(value)

    accepted = "" if accepted_taxon_key is None or pd.isna(accepted_taxon_key) else str(accepted_taxon_key).strip()
    raw_name = "" if raw_scientific_name is None or pd.isna(raw_scientific_name) else str(raw_scientific_name).strip()
    if accepted:
        members.append(accepted)
    elif raw_name:
        members.append(f"raw_name:{norm_name(raw_name)}")

    # Remove unresolved/raw taxon placeholders once an accepted key is known, but keep
    # all non-taxon role members that distinguish biological assertions.
    cleaned: list[str] = []
    for member in members:
        if accepted and (member.startswith("raw_name:") or member.startswith("unresolved_taxon_name:")):
            continue
        cleaned.append(member)
    return sorted(set(cleaned))


def canonical_members_json(**kwargs: Any) -> str:
    return json.dumps(canonical_member_list(**kwargs))


def read_table(path: Path) -> pd.DataFrame:
    if path.suffix == ".parquet":
        return pd.read_parquet(path)
    if path.suffix == ".jsonl":
        rows = []
        with path.open("r", encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if line:
                    rows.append(json.loads(line))
        return pd.DataFrame(rows)
    if path.suffix == ".csv":
        return pd.read_csv(path, dtype=str, low_memory=False)
    return pd.read_csv(path, sep="\t", dtype=str, low_memory=False)


def write_parquet(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(path, index=False)


def write_tsv(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, sep="\t", index=False)


def load_name_maps() -> tuple[dict[str, str], dict[str, str]]:
    accepted = read_table(STAGING / "taxonomy_backbone" / "accepted_taxa.parquet")
    synonyms = read_table(STAGING / "taxonomy_backbone" / "synonym_clusters.parquet")
    accepted_map = {
        norm_name(row.accepted_name): row.accepted_taxon_key
        for row in accepted.itertuples(index=False)
        if norm_name(row.accepted_name)
    }
    synonym_map = {
        norm_name(row.name_string): row.accepted_taxon_key
        for row in synonyms.itertuples(index=False)
        if norm_name(row.name_string)
    }
    return accepted_map, synonym_map


def resolve_name(raw_name: Any, accepted_map: dict[str, str], synonym_map: dict[str, str]) -> tuple[str, str, str]:
    key = norm_name(raw_name)
    if not key:
        return "", "missing_raw_name", "missing raw scientific name"
    if key in accepted_map:
        return accepted_map[key], "accepted_exact", ""
    if key in synonym_map:
        return synonym_map[key], "synonym_exact", ""
    return "", "unresolved", "no exact WFO accepted-name or synonym-cluster match"


def source_group_from_path(path: Path) -> str:
    try:
        rel = path.relative_to(STAGING)
        return rel.parts[0]
    except ValueError:
        return path.parent.name


def first_present(row: pd.Series, names: list[str], default: Any = "") -> Any:
    for name in names:
        if name in row and not pd.isna(row[name]) and str(row[name]) != "":
            return row[name]
    return default


def coerce_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or pd.isna(value) or value == "":
            return default
        if str(value).lower() == "high":
            return 0.9
        if str(value).lower() == "medium":
            return 0.7
        if str(value).lower() == "low":
            return 0.4
        return float(value)
    except Exception:
        return default
