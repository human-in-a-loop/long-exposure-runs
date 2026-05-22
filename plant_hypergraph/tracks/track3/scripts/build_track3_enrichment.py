"""
Track 3 Wave 2 convergence-enrichment projection.

Pure projection over the frozen Barrier 1 substrate:
    phytograph_dataset/{hyperedges,nodes,taxon_crosswalk,synonym_resolution}.parquet
                       (READ-ONLY)

Emits per-(trait, accepted_taxon_key) membership rows under
`tracks/track3/data/`. Forbidden from writing any row with
`track_edge_type == "convergence_signature"`: that step is reserved for the
Phase 4.3 instrument. Hard-asserted at output time and again by the pytest
suite under `tracks/track3/tests/`.

Inputs read but never mutated. Mtimes captured at script entry and
re-checked at exit; mismatch aborts the build.

Run:
    python3 tracks/track3/scripts/build_track3_enrichment.py
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

import pandas as pd
import pyarrow.parquet as pq

# Allow running both as a script and as a module
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
from trait_dictionary import (  # noqa: E402
    CANONICAL_TRAITS,
    FLOOR_ACCEPTED_TAXA,
    LABEL_TO_TRAIT,
    PROJECTION_RULE_ID,
    TRAITS_WITHOUT_SUBSTRATE_LABEL,
    trait_for_label,
)

WORKSPACE = Path(__file__).resolve().parents[3]
SUBSTRATE = WORKSPACE / "phytograph_dataset"
TRACK3 = WORKSPACE / "tracks" / "track3"
DATA_DIR = TRACK3 / "data"

SUBSTRATE_FILES = [
    SUBSTRATE / "hyperedges.parquet",
    SUBSTRATE / "nodes.parquet",
    SUBSTRATE / "taxon_crosswalk.parquet",
    SUBSTRATE / "synonym_resolution.parquet",
]

# Canonical Track 3 validation cases the audit must report on.
# Each entry: (label_for_audit, family_regex, trait_required, genus_regex_for_pending_fallback)
# The genus regex matches against raw_scientific_name (left-anchored) so we
# can still surface canonical cases held in pending_crosswalk rows where
# the substrate didn't resolve to a WFO key.
CANONICAL_CASES = [
    ("C4 Poaceae", "Poaceae", "c4_photosynthesis", None),
    ("C4 Cyperaceae", "Cyperaceae", "c4_photosynthesis", r"^(Cyperus|Carex|Eleocharis|Schoenus|Bulbostylis|Fimbristylis|Rhynchospora|Scleria) "),
    ("C4 Amaranthaceae", "Amaranthaceae", "c4_photosynthesis", r"^(Amaranthus|Atriplex|Chenopodium|Salsola|Suaeda|Tecticornia) "),
    ("CAM Crassulaceae", "Crassulaceae", "cam_photosynthesis", r"^(Crassula|Sedum|Sempervivum|Kalanchoe|Echeveria) "),
    ("CAM Orchidaceae", "Orchidaceae", "cam_photosynthesis", r"^(Dendrobium|Cymbidium|Bulbophyllum|Phalaenopsis|Cattleya|Vanda) "),
    ("Succulence Cactaceae", "Cactaceae", "succulence", r"^(Opuntia|Mammillaria|Cereus|Echinocactus|Ferocactus|Carnegiea|Cylindropuntia) "),
    ("Succulence Euphorbiaceae", "Euphorbiaceae", "succulence", r"^Euphorbia "),
    ("Myrmecochory Liliaceae/Melanthiaceae (Trillium)", "Melanthiaceae", "myrmecochory", r"^(Trillium|Asarum|Sanguinaria) "),
    ("Elaiosome Fabaceae (Acacia)", "Fabaceae", "elaiosome", r"^Acacia "),
    ("Drupe Anacardiaceae", "Anacardiaceae", "drupe", r"^(Mangifera|Rhus|Anacardium|Pistacia|Schinus|Toxicodendron) "),
    ("Samara Sapindaceae", "Sapindaceae", "samara", r"^(Acer|Aesculus|Dipteronia) "),
    ("Fleshy fruit Solanaceae", "Solanaceae", "fleshy_fruit", r"^(Solanum|Capsicum|Lycium|Physalis|Nicotiana|Atropa) "),
]


def _mtimes(files):
    return {str(f): os.path.getmtime(f) for f in files if f.exists()}


def _parse_role_map(s: str):
    try:
        return json.loads(s) if isinstance(s, str) else {}
    except Exception:
        return {}


def build_family_lookup(hyperedges_df, nodes_df):
    """Build accepted_key -> (family_id, family_label) lookup from
    taxonomic_parentage edges by walking child -> parent chains."""
    tp = hyperedges_df[hyperedges_df["edge_type"] == "taxonomic_parentage"]
    parent_map = {}
    for _, r in tp.iterrows():
        try:
            arr = json.loads(r["canonical_node_ids_json"])
        except Exception:
            continue
        if not arr:
            continue
        child = r["accepted_taxon_key"]
        if not child:
            continue
        parent = next((x for x in arr if x != child), None)
        if parent:
            parent_map[child] = parent
    node_type = dict(zip(nodes_df["node_id"], nodes_df["node_type"]))
    node_label = dict(zip(nodes_df["node_id"], nodes_df["label"]))

    cache = {}

    def find_family(key, max_depth=25):
        if key in cache:
            return cache[key]
        cur = key
        for _ in range(max_depth):
            nt = node_type.get(cur)
            if nt == "family":
                cache[key] = (cur, node_label.get(cur, ""))
                return cache[key]
            if cur not in parent_map:
                cache[key] = (None, None)
                return cache[key]
            cur = parent_map[cur]
        cache[key] = (None, None)
        return cache[key]

    return find_family


def project(hyperedges_df, nodes_df, find_family):
    """Project Track 3 candidate edges into per-(trait, taxon) rows."""
    sub = hyperedges_df[
        hyperedges_df["edge_type"].isin(["trait_syndrome", "fruit_morphology", "life_form"])
    ].copy()

    # Build node-id -> label map for trait / fruit_type / life_form nodes
    node_label = dict(zip(nodes_df["node_id"], nodes_df["label"]))

    rows = []
    other_bucket_per_label = {}

    for _, r in sub.iterrows():
        rm = _parse_role_map(r["role_map_json"])
        # The trait member is keyed by `trait`, `fruit_type`, or `life_form`
        member_id = rm.get("trait") or rm.get("fruit_type") or rm.get("life_form")
        if not member_id:
            continue
        label = node_label.get(member_id, "")
        if not label:
            # cannot project — route to _other_unknown_node
            trait = "_other"
            other_bucket_per_label[f"<unknown_node:{member_id}>"] = (
                other_bucket_per_label.get(f"<unknown_node:{member_id}>", 0) + 1
            )
        else:
            trait = trait_for_label(label)
            if trait == "_other":
                other_bucket_per_label[label] = other_bucket_per_label.get(label, 0) + 1

        accepted_key = r["accepted_taxon_key"] or ""
        pending = bool(r["pending_crosswalk"])
        family_key, family_label = (None, None)
        if accepted_key and not pending:
            family_key, family_label = find_family(accepted_key)

        rows.append(
            {
                "track_edge_id": f"t3-{r['edge_id']}",
                "track_edge_type": "track3_trait_membership",  # NEVER convergence_signature
                "trait": trait,
                "substrate_label": label,
                "accepted_taxon_key": accepted_key,
                "family_key": family_key or "",
                "family_label": family_label or "",
                "raw_scientific_name": r["raw_scientific_name"] or "",
                "source_edge_id": r["edge_id"],
                "source_id": r["source_id"] or "",
                "license": r["license"] or "",
                "access_date": r["access_date"] or "",
                "pending_crosswalk": pending,
                "allowed_evidence_scope": r["allowed_evidence_scope"] or "",
                "caveats": r["caveats"] if r["caveats"] is not None else "",
                "projection_rule_id": PROJECTION_RULE_ID,
            }
        )

    out = pd.DataFrame(rows)
    return out, other_bucket_per_label


def build_coverage(out_df):
    """Per-trait coverage summary table."""
    rows = []
    all_traits = list(CANONICAL_TRAITS) + TRAITS_WITHOUT_SUBSTRATE_LABEL + ["_other"]
    seen = set()
    for trait in all_traits:
        if trait in seen:
            continue
        seen.add(trait)
        sub = out_df[out_df["trait"] == trait]
        n_edges = len(sub)
        resolved = sub[sub["pending_crosswalk"] == False]
        pending = sub[sub["pending_crosswalk"] == True]
        n_accepted = resolved["accepted_taxon_key"].nunique() if len(resolved) else 0
        n_pending = pending["raw_scientific_name"].nunique() if len(pending) else 0
        n_families = resolved["family_label"].replace("", pd.NA).dropna().nunique()
        # n_orders not in substrate -> not available; report 0
        top_fams = (
            resolved[resolved["family_label"] != ""]
            .groupby("family_label")["accepted_taxon_key"]
            .nunique()
            .sort_values(ascending=False)
            .head(10)
        )
        top_str = "; ".join(f"{k}:{v}" for k, v in top_fams.items())
        floor_met = "yes" if n_accepted >= FLOOR_ACCEPTED_TAXA else "no"
        data_limited = "no" if n_accepted >= FLOOR_ACCEPTED_TAXA else "yes"
        rows.append(
            {
                "trait": trait,
                "n_retained_edges": n_edges,
                "n_accepted_taxa": n_accepted,
                "n_pending_crosswalk_taxa": n_pending,
                "n_families": n_families,
                "n_orders": 0,
                "top_10_families_with_counts": top_str,
                "floor_met_500_taxa": floor_met,
                "data_limited_flag": data_limited,
            }
        )
    return pd.DataFrame(rows)


def build_gap_list(out_df):
    """Report canonical-case reachability.

    A case is `reachable` if any of:
      (a) there is a resolved row whose family_label matches the target family, OR
      (b) there is any row (resolved or pending) whose raw_scientific_name
          starts with a known canonical genus for the target family AND has
          the required trait.
    Path (b) lets us count canonical cases held in pending_crosswalk rows
    that the Barrier-1 crosswalk did not resolve. Reachability is reported
    with the path tag so the audit is transparent.
    """
    gaps = []
    for label, family, trait, genus_re in CANONICAL_CASES:
        # path (a): resolved + family
        sub_resolved = out_df[
            (out_df["trait"] == trait)
            & (out_df["pending_crosswalk"] == False)
            & (out_df["family_label"].str.contains(family, case=False, na=False))
        ]
        n_resolved = sub_resolved["accepted_taxon_key"].nunique()

        # path (b): genus match in raw_scientific_name (resolved + pending)
        n_genus = 0
        if genus_re:
            sub_genus = out_df[
                (out_df["trait"] == trait)
                & (out_df["raw_scientific_name"].str.match(genus_re, na=False))
            ]
            n_genus = sub_genus["raw_scientific_name"].nunique()

        n_total = max(n_resolved, n_genus)
        if n_resolved > 0:
            reachable, path = "yes", "resolved_family_match"
        elif n_genus > 0:
            reachable, path = "yes", "pending_genus_match"
        else:
            reachable, path = "no", "none"

        if reachable == "no":
            any_trait = out_df[out_df["trait"] == trait]
            if any_trait.empty:
                reason = "trait_has_no_retained_edges"
            else:
                reason = "family_and_genus_absent_from_substrate"
        else:
            reason = ""

        gaps.append(
            {
                "canonical_case": label,
                "trait": trait,
                "family_target": family,
                "reachable": reachable,
                "path": path,
                "n_resolved_taxa_family": int(n_resolved),
                "n_genus_match_names": int(n_genus),
                "n_total_reachable": int(n_total),
                "gap_reason": reason,
            }
        )
    return pd.DataFrame(gaps)


def validate_output(out_df, hyperedges_df):
    """Hard assertions. Abort with non-zero exit on failure."""
    # (1) No `convergence_signature` track edges.
    bad = (out_df["track_edge_type"] == "convergence_signature").sum()
    assert bad == 0, f"FORBIDDEN: {bad} rows have track_edge_type=convergence_signature"
    # (2) accepted_taxon_key non-empty when pending_crosswalk=False.
    resolved = out_df[out_df["pending_crosswalk"] == False]
    empty = (resolved["accepted_taxon_key"] == "").sum()
    assert empty == 0, f"{empty} resolved rows have empty accepted_taxon_key"
    # (3) Sum of projected edges <= retained substrate count for the 3 edge types
    candidate_count = hyperedges_df["edge_type"].isin(
        ["trait_syndrome", "fruit_morphology", "life_form"]
    ).sum()
    assert len(out_df) <= candidate_count, (
        f"projected {len(out_df)} rows > retained substrate {candidate_count}"
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    t0 = time.time()
    mtimes_before = _mtimes(SUBSTRATE_FILES)
    print(f"[track3-enrichment] reading substrate from {SUBSTRATE} ...", flush=True)

    hyperedges = pq.read_table(SUBSTRATE / "hyperedges.parquet").to_pandas()
    nodes = pq.read_table(SUBSTRATE / "nodes.parquet").to_pandas()
    # taxon_crosswalk and synonym_resolution are read only for mtime check and
    # for downstream provenance verification (we do not re-normalize).
    _ = pq.read_table(SUBSTRATE / "taxon_crosswalk.parquet").to_pandas()
    _ = pq.read_table(SUBSTRATE / "synonym_resolution.parquet").to_pandas()

    print(f"  hyperedges: {len(hyperedges)} rows", flush=True)
    print(f"  nodes: {len(nodes)} rows", flush=True)

    print("[track3-enrichment] building family lookup ...", flush=True)
    find_family = build_family_lookup(hyperedges, nodes)

    print("[track3-enrichment] projecting Track 3 candidate edges ...", flush=True)
    out, other_bucket = project(hyperedges, nodes, find_family)

    print(f"  projected rows: {len(out)}", flush=True)
    print(f"  _other bucket labels (top): "
          f"{sorted(other_bucket.items(), key=lambda x: -x[1])[:8]}", flush=True)

    validate_output(out, hyperedges)
    print("[track3-enrichment] hard assertions PASSED", flush=True)

    coverage = build_coverage(out)
    gaps = build_gap_list(out)

    if not args.dry_run:
        out_path = DATA_DIR / "convergence_trait_edges.parquet"
        out.to_parquet(out_path, index=False)
        coverage.to_csv(DATA_DIR / "trait_coverage_summary.tsv", sep="\t", index=False)
        gaps.to_csv(DATA_DIR / "track3_gap_list.tsv", sep="\t", index=False)
        # _other bucket diagnostic
        ob_df = pd.DataFrame(
            sorted(other_bucket.items(), key=lambda x: -x[1]),
            columns=["substrate_label", "n_edges"],
        )
        ob_df.to_csv(DATA_DIR / "track3_other_bucket.tsv", sep="\t", index=False)
        print(f"  wrote {out_path}", flush=True)
        print(f"  wrote trait_coverage_summary.tsv ({len(coverage)} rows)", flush=True)
        print(f"  wrote track3_gap_list.tsv ({len(gaps)} rows)", flush=True)
        print(f"  wrote track3_other_bucket.tsv ({len(ob_df)} rows)", flush=True)

    # Final substrate mtime check
    mtimes_after = _mtimes(SUBSTRATE_FILES)
    if mtimes_before != mtimes_after:
        raise RuntimeError(
            f"SUBSTRATE MUTATED during build! before={mtimes_before} after={mtimes_after}"
        )

    print(f"[track3-enrichment] done in {time.time() - t0:.1f}s", flush=True)


if __name__ == "__main__":
    main()
