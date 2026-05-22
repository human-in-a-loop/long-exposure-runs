# created: 2026-05-17T21:30:00Z
# cycle: 4
# run_id: run-phytograph-cycle4-barrier1
# agent: worker
# milestone: _plan/barrier1-substrate-freeze
"""Validate the frozen Barrier-1 PhytoGraph substrate."""

from __future__ import annotations

import sys
from pathlib import Path
import json

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from barrier1_common import ALLOWED_EDGE_TYPES, ALLOWED_NODE_TYPES, BIOLOGY_FORBIDDEN_IMAGE_SCOPES, DATASET, load_name_maps, norm_name  # noqa: E402


REQUIRED_EDGE_FIELDS = ["source_id", "access_date", "license", "provenance_pointer", "allowed_evidence_scope", "caveats"]


def validate_edges_df(edges: pd.DataFrame) -> list[str]:
    errors: list[str] = []
    bad_edge_types = sorted(set(edges["edge_type"].dropna()) - ALLOWED_EDGE_TYPES)
    if bad_edge_types:
        errors.append(f"unknown edge types: {bad_edge_types}")
    for field in REQUIRED_EDGE_FIELDS:
        missing = edges[field].isna() | (edges[field].astype(str).str.strip() == "")
        if missing.any():
            errors.append(f"{field} missing on {int(missing.sum())} retained edges")
    inferred_anach = edges[(edges["edge_type"] == "anachronism_candidate_edge") & (edges["inferred_flag"].fillna(False).astype(bool))]
    if len(inferred_anach):
        errors.append(f"inferred anachronism_candidate_edge rows present: {len(inferred_anach)}")
    convergence = edges[edges["edge_type"] == "convergence_signature"]
    if len(convergence):
        errors.append(f"pre-instrument convergence_signature rows present: {len(convergence)}")
    image = edges[edges["edge_type"] == "image_evidence"]
    for _, row in image.iterrows():
        allowed = str(row["allowed_evidence_scope"]).lower()
        if any(scope in allowed for scope in BIOLOGY_FORBIDDEN_IMAGE_SCOPES):
            errors.append(f"image edge {row['edge_id']} has forbidden allowed scope: {row['allowed_evidence_scope']}")
            break
    ethno = edges[edges["edge_type"] == "ethnobotanical_use_assertion"]
    if len(ethno):
        missing_ethno_scope = ethno["provenance_pointer"].astype(str).str.strip().eq("")
        if missing_ethno_scope.any():
            errors.append(f"ethnobotanical provenance pointer missing on {int(missing_ethno_scope.sum())} rows")
    accepted_map, synonym_map = load_name_maps()
    raw_scientific_name = edges["raw_scientific_name"] if "raw_scientific_name" in edges.columns else pd.Series([""] * len(edges), index=edges.index)
    accepted_taxon_key = edges["accepted_taxon_key"] if "accepted_taxon_key" in edges.columns else pd.Series([""] * len(edges), index=edges.index)
    pending_crosswalk = edges["pending_crosswalk"] if "pending_crosswalk" in edges.columns else pd.Series([False] * len(edges), index=edges.index)
    canonical_node_ids_json = edges["canonical_node_ids_json"] if "canonical_node_ids_json" in edges.columns else pd.Series(["[]"] * len(edges), index=edges.index)
    normalized = raw_scientific_name.fillna("").astype(str).map(norm_name)
    resolved = normalized.map(accepted_map).fillna(normalized.map(synonym_map)).fillna("")
    should_be_resolved = resolved.astype(str).str.len().gt(0)
    missing_propagation = edges[
        should_be_resolved
        & (
            accepted_taxon_key.fillna("").astype(str).eq("")
            | pending_crosswalk.fillna(True).astype(bool)
        )
    ]
    if len(missing_propagation):
        errors.append(f"resolved accepted keys not propagated on {len(missing_propagation)} retained edges")
    missing_member = [
        row.edge_id
        for value, key in zip(canonical_node_ids_json[should_be_resolved], resolved[should_be_resolved])
        if str(key) not in _member_set(value)
    ]
    if missing_member:
        errors.append(f"accepted key missing from canonical members on {len(missing_member)} retained edges")
    unresolved = edges[~should_be_resolved]
    bad_unresolved = unresolved[
        raw_scientific_name[~should_be_resolved].fillna("").astype(str).str.strip().ne("")
        & ~unresolved["caveats"].fillna("").astype(str).str.contains("ambiguity_reason=", regex=False)
    ]
    if len(bad_unresolved):
        errors.append(f"unresolved retained edges lack machine-readable ambiguity_reason: {len(bad_unresolved)}")
    multi_member_edge_types = {
        "trait_syndrome",
        "fruit_morphology",
        "life_form",
        "phytochemical_assertion",
        "ethnobotanical_use_assertion",
        "bioactivity_assertion",
        "crop_pedigree",
        "vavilov_center_hyperedge",
        "anachronism_candidate_edge",
        "image_evidence",
    }
    too_narrow = edges[
        edges["edge_type"].isin(multi_member_edge_types)
        & canonical_node_ids_json.map(lambda v: len(_member_set(v))).le(1)
    ]
    if len(too_narrow):
        counts = too_narrow.groupby("edge_type").size().to_dict()
        errors.append(f"multi-member edge types have raw-name-only canonical members: {counts}")
    collision_path = DATASET / "dedup_collision_audit.tsv"
    if collision_path.exists():
        collisions = pd.read_csv(collision_path, sep="\t")
        risky = collisions[
            collisions["edge_type"].isin(["trait_syndrome", "fruit_morphology", "life_form", "phytochemical_assertion", "ethnobotanical_use_assertion", "bioactivity_assertion"])
            & collisions.get("distinct_non_tax_role_maps", collisions["distinct_role_maps"]).fillna(0).astype(int).gt(1)
        ]
        if len(risky):
            errors.append(f"dedup collision groups collapse distinct Track 3/5 role maps: {len(risky)}")
    return errors


def _member_set(value: object) -> set[str]:
    try:
        parsed = json.loads(value) if isinstance(value, str) else value
    except Exception:
        parsed = []
    if isinstance(parsed, list):
        return {str(v) for v in parsed if str(v)}
    return set()


def validate_nodes_df(nodes: pd.DataFrame) -> list[str]:
    bad_node_types = sorted(set(nodes["node_type"].dropna()) - ALLOWED_NODE_TYPES)
    errors = [f"unknown node types: {bad_node_types}"] if bad_node_types else []
    accepted_taxa = nodes[nodes["node_type"].isin(["family", "genus", "species", "infraspecific_unit"])]
    synonyms = nodes[nodes["node_type"] == "synonym"]
    if len(accepted_taxa) != 60000:
        errors.append(f"Tier 0 accepted taxonomy node count is {len(accepted_taxa)}, expected 60000")
    if len(synonyms) != 113582:
        errors.append(f"synonym node count is {len(synonyms)}, expected 113582")
    return errors


def validate_heldout_leakage() -> list[str]:
    heldout = ROOT / "substrate" / "staging" / "domestication_sources" / "heldout_validation_set.tsv"
    curated = ROOT / "substrate" / "staging" / "domestication_sources" / "edges" / "crop_pedigree.tsv"
    if not heldout.exists() or not curated.exists():
        return ["M1.6 held-out or crop-pedigree file missing"]
    h = pd.read_csv(heldout, sep="\t")
    c = pd.read_csv(curated, sep="\t")
    heldout_names = {str(x).strip().lower() for x in h["crop_taxon"].dropna()}
    curated_names = {str(x).strip().lower() for x in c["raw_scientific_name"].dropna()}
    overlap = sorted(heldout_names & curated_names)
    return [f"M1.6 held-out leakage under normalized matching: {overlap}"] if overlap else []


def main() -> int:
    nodes = pd.read_parquet(DATASET / "nodes.parquet")
    edges = pd.read_parquet(DATASET / "hyperedges.parquet")
    provenance = pd.read_parquet(DATASET / "provenance.parquet")
    caveats = pd.read_parquet(DATASET / "caveats.parquet")
    errors = []
    errors.extend(validate_nodes_df(nodes))
    errors.extend(validate_edges_df(edges))
    if len(provenance) < len(edges):
        errors.append("provenance table has fewer rows than retained hyperedges")
    if len(caveats) < len(edges):
        errors.append("caveats table has fewer rows than retained hyperedges")
    errors.extend(validate_heldout_leakage())
    if errors:
        print("FAIL: Barrier 1 substrate validation")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"PASS: Barrier 1 substrate validation ({len(nodes)} nodes, {len(edges)} retained hyperedges)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
