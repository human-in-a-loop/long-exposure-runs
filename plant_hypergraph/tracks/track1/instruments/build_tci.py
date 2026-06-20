#!/usr/bin/env python3
"""
Build Track 1 Tree Compatibility Index (TCI) from frozen Barrier-1 substrate
plus Track 1 enrichment.

created: 2026-05-18T03:05:00+00:00
cycle: 9
run_id: run-phytograph-cycle9-m3t1-tci
agent: worker
milestone: _plan/track1-m3t1-instrument

Deterministic, single-core, < 5 min on 363k taxa. Reads-only the substrate +
Track 1 enrichment. Writes to tracks/track1/outputs/.

Formal spec: tracks/track1/instruments/tci_spec.md
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import random
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import pandas as pd

WORKSPACE = Path(__file__).resolve().parents[3]
SUBSTRATE = WORKSPACE / "phytograph_dataset"
T1_ENRICH = WORKSPACE / "tracks" / "track1" / "data" / "reticulation_enrichment_edges.parquet"
T1_SEEDS = WORKSPACE / "tracks" / "track1" / "data" / "canonical_seed_case_status.tsv"
OUT_DIR = WORKSPACE / "tracks" / "track1" / "outputs"

EVIDENCE_EDGE_TYPES = {
    "reticulate_inheritance_evidence",
    "hybridization_event",
    "polyploidization_event",
}
CROP_PEDIGREE = "crop_pedigree"

WFO_GENUS_PREFIX = "wfo:wfo-4"   # WFO genus nodes
WFO_FAMILY_PREFIX = "wfo:wfo-7"  # WFO family nodes

DEFAULT_HOTSPOT_ALPHA = 0.5


# ---------------------------------------------------------------------------
# Loaders
# ---------------------------------------------------------------------------

def load_substrate():
    nodes = pd.read_parquet(SUBSTRATE / "nodes.parquet")
    edges = pd.read_parquet(SUBSTRATE / "hyperedges.parquet")
    return nodes, edges


def load_track1_enrichment():
    df = pd.read_parquet(T1_ENRICH) if T1_ENRICH.exists() else pd.DataFrame()
    return df


# ---------------------------------------------------------------------------
# Taxonomy walk: species/infraspecific -> genus -> family
# ---------------------------------------------------------------------------

def build_parent_map(edges: pd.DataFrame, nodes: pd.DataFrame) -> dict:
    """Map every accepted_taxon_key -> immediate parent accepted_taxon_key (if any)."""
    node_type = dict(zip(nodes.node_id, nodes.node_type))

    def rank(node_id: str) -> int:
        if node_id.startswith(WFO_FAMILY_PREFIX):
            return 3
        if node_id.startswith(WFO_GENUS_PREFIX):
            return 2
        return 1  # species / infraspecific

    parents = {}
    sub = edges[edges.edge_type == "taxonomic_parentage"]
    for j_arr in sub["canonical_node_ids_json"].tolist():
        try:
            members = json.loads(j_arr) if isinstance(j_arr, str) else list(j_arr)
        except Exception:
            continue
        if len(members) < 2:
            continue
        ranked = sorted(members, key=rank)
        child, parent = ranked[0], ranked[-1]
        if rank(parent) > rank(child):
            parents[child] = parent
    return parents


def resolve_genus_family(parents: dict, nodes: pd.DataFrame) -> tuple[dict, dict]:
    """For every node accepted-key, return (genus_key, family_key) by walking up."""
    genus_of = {}
    family_of = {}
    keys = nodes.accepted_taxon_key.dropna().unique().tolist()
    for k in keys:
        g = None
        f = None
        cur = k
        seen = set()
        steps = 0
        while cur and cur not in seen and steps < 10:
            seen.add(cur)
            if cur.startswith(WFO_GENUS_PREFIX) and g is None:
                g = cur
            if cur.startswith(WFO_FAMILY_PREFIX) and f is None:
                f = cur
                break
            cur = parents.get(cur)
            steps += 1
        if k.startswith(WFO_GENUS_PREFIX) and g is None:
            g = k
        if k.startswith(WFO_FAMILY_PREFIX) and f is None:
            f = k
        genus_of[k] = g
        family_of[k] = f
    return genus_of, family_of


# ---------------------------------------------------------------------------
# Index incident reticulation edges per accepted_taxon_key
# ---------------------------------------------------------------------------

def parse_jsonish(value, fallback=None):
    if fallback is None:
        fallback = {}
    if isinstance(value, str) and value:
        try:
            return json.loads(value)
        except Exception:
            return fallback
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return fallback
    return value


def is_event_shaped_reticulation_edge(edge_type: str, role_map_json) -> bool:
    """Return True only for evidence that can support reticulate inheritance.

    Barrier 1 still contains a few pre-repair Track 1 rows whose edge_type is
    `reticulate_inheritance_evidence` but whose preserved role map contains
    only `ploidy_state`. Those rows are ploidy context, not reticulation event
    evidence. The M3.T1 instrument must not lower observed TCI from them.
    """
    if edge_type in {"hybridization_event", "polyploidization_event"}:
        return True
    if edge_type != "reticulate_inheritance_evidence":
        return False
    rmap = parse_jsonish(role_map_json, fallback={})
    if not isinstance(rmap, dict):
        return False
    return any(k in rmap for k in ("child_taxon", "parent_taxa", "parent_taxon", "reticulate_parent"))


def index_incident_evidence(edges: pd.DataFrame, nodes: pd.DataFrame) -> dict:
    """Count incident event-shaped evidence edges per accepted taxon key.

    Chromosome counts and ploidy-state assertions are intentionally excluded:
    their allowed evidence scope does not establish a hybridization or
    polyploidization event. Multi-parent crop pedigrees are counted as
    reticulation evidence on the resolved cultivar/child only.
    """
    counts = Counter()
    accepted_keys = {k for k in nodes.accepted_taxon_key.dropna().unique() if k}

    # 1) edge.accepted_taxon_key direct
    sub = edges[edges.edge_type.isin(EVIDENCE_EDGE_TYPES) & edges.accepted_taxon_key.notna()
                & (edges.accepted_taxon_key != "")]
    for _, row in sub.iterrows():
        k = row.accepted_taxon_key
        if k and k in accepted_keys and is_event_shaped_reticulation_edge(row.edge_type, row.role_map_json):
            counts[k] += 1

    # 2) accepted-key members listed in canonical_node_ids_json (covers parent_taxa roles)
    for et in EVIDENCE_EDGE_TYPES:
        sub2 = edges[edges.edge_type == et]
        for ce, cj, rm in zip(
            sub2.accepted_taxon_key.tolist(),
            sub2.canonical_node_ids_json.tolist(),
            sub2.role_map_json.tolist(),
        ):
            if not is_event_shaped_reticulation_edge(et, rm):
                continue
            members = parse_jsonish(cj, fallback=[])
            for m in members:
                if isinstance(m, str) and m.startswith("wfo:") and m in accepted_keys:
                    if m == ce:
                        continue  # already counted
                    counts[m] += 1

    # 3) crop_pedigree where cultivar role resolves to accepted key
    sub3 = edges[edges.edge_type == CROP_PEDIGREE]
    for ce, rm in zip(sub3.accepted_taxon_key.tolist(), sub3.role_map_json.tolist()):
        if ce and ce in accepted_keys:
            counts[ce] += 1
    return dict(counts)


# ---------------------------------------------------------------------------
# Genus-level structural features (ploidy spread, chromosome-count CV)
# ---------------------------------------------------------------------------

def parse_chrom_midpoint(row) -> float | None:
    """Use parsed_min/parsed_max from Track 1 enrichment if available; else None."""
    pmin = row.get("parsed_min")
    pmax = row.get("parsed_max")
    if pmin is None or (isinstance(pmin, float) and math.isnan(pmin)):
        return None
    pmin = float(pmin)
    if pmax is None or (isinstance(pmax, float) and math.isnan(pmax)) or pmax == 0:
        return pmin
    return 0.5 * (pmin + float(pmax))


def genus_structural_features(t1: pd.DataFrame, genus_of: dict) -> dict:
    """For each genus key g present in genus_of, compute ploidy states & chrom counts."""
    ploidy_by_genus = defaultdict(list)
    chrom_by_genus = defaultdict(list)

    if t1.empty:
        return {"ploidy": ploidy_by_genus, "chrom": chrom_by_genus}

    # Only use rows resolved to accepted key
    t1r = t1[t1.accepted_taxon_key.fillna("").str.startswith("wfo:")]
    for _, r in t1r.iterrows():
        key = r.get("accepted_taxon_key")
        g = genus_of.get(key)
        if not g:
            continue
        if r.get("edge_type") == "ploidy_state_assertion":
            ps = r.get("ploidy_state")
            if isinstance(ps, str) and ps:
                ploidy_by_genus[g].append(ps)
        if r.get("edge_type") == "chromosome_count_assertion":
            mid = parse_chrom_midpoint(r)
            if mid is not None:
                chrom_by_genus[g].append(mid)

    # Also harvest chromosome_count_assertion from substrate (resolved keys)
    return {"ploidy": dict(ploidy_by_genus), "chrom": dict(chrom_by_genus)}


def substrate_chrom_by_genus(edges, genus_of, parents):
    sub = edges[edges.edge_type == "chromosome_count_assertion"]
    out = defaultdict(list)
    for ce, rm, cj in zip(sub.accepted_taxon_key, sub.role_map_json, sub.canonical_node_ids_json):
        if not ce:
            continue
        g = genus_of.get(ce)
        if not g:
            continue
        try:
            rmap = json.loads(rm) if isinstance(rm, str) else rm
        except Exception:
            rmap = {}
        cc = rmap.get("chromosome_count", "") if isinstance(rmap, dict) else ""
        # parse e.g. "2n=10", "2n=120"
        m = re.search(r"(\d+)", str(cc))
        if m:
            out[g].append(float(m.group(1)))
    return dict(out)


# ---------------------------------------------------------------------------
# Synonym + taxonomic conflict per taxon
# ---------------------------------------------------------------------------

def synonym_cluster_size_per_taxon(edges) -> dict:
    out = {}
    sub = edges[edges.edge_type == "synonym_cluster"]
    for ce, cj in zip(sub.accepted_taxon_key, sub.canonical_node_ids_json):
        if not ce:
            continue
        try:
            members = json.loads(cj) if isinstance(cj, str) else list(cj)
        except Exception:
            members = []
        out[ce] = max(out.get(ce, 1), len(members))
    return out


def taxonomic_conflict_per_taxon(edges) -> dict:
    out = Counter()
    sub = edges[edges.edge_type == "taxonomic_conflict"]
    for ce in sub.accepted_taxon_key:
        if ce:
            out[ce] += 1
    return dict(out)


# ---------------------------------------------------------------------------
# Component computations
# ---------------------------------------------------------------------------

def shannon_entropy_norm(items):
    if not items:
        return 0.0
    c = Counter(items)
    n = sum(c.values())
    if len(c) <= 1:
        return 0.0
    H = 0.0
    for v in c.values():
        p = v / n
        H -= p * math.log(p)
    return H / math.log(len(c))


def hotspot_table(df: pd.DataFrame, ploidy_by_genus: dict, alpha: float = DEFAULT_HOTSPOT_ALPHA) -> pd.DataFrame:
    """Aggregate per-taxon TCI rows to genus-level hotspot diagnostics."""
    rows = []
    sub = df[df["genus_key"].fillna("") != ""].copy()
    for g, group in sub.groupby("genus_key", dropna=True):
        ploidies = ploidy_by_genus.get(g, [])
        ploidy_entropy = shannon_entropy_norm(ploidies)
        n_taxa = len(group)
        evidence_taxa = int((group["n_evidence_edges"] > 0).sum())
        structural_taxa = int((group["tci_provenance"] == "structural_only").sum())
        data_limited_taxa = int((group["tci_provenance"] == "data_limited_unknown").sum())
        evidence_fraction = evidence_taxa / n_taxa if n_taxa else 0.0
        hotspot_score = evidence_fraction + alpha * ploidy_entropy
        n_chrom_records = int(group["n_chrom_counts"].fillna(0).max()) if len(group) else 0
        rows.append({
            "genus_key": g,
            "genus_label": group["genus_label"].iloc[0],
            "family_key": group["family_key"].dropna().iloc[0] if group["family_key"].notna().any() else "",
            "family_label": group["family_label"].dropna().iloc[0] if group["family_label"].notna().any() else "",
            "n_taxa_scored": n_taxa,
            "evidence_supported_taxa": evidence_taxa,
            "structural_only_taxa": structural_taxa,
            "data_limited_unknown_taxa": data_limited_taxa,
            "evidence_supported_fraction": round(evidence_fraction, 6),
            "ploidy_entropy_norm": round(ploidy_entropy, 6),
            "hotspot_score": round(hotspot_score, 6),
            "mean_tci": round(float(group["tci"].mean()), 6),
            "min_tci": round(float(group["tci"].min()), 6),
            "n_chrom_records_in_genus": n_chrom_records,
            "data_sufficiency": "sufficient" if n_taxa >= 2 and n_chrom_records >= 3 else "data_limited",
        })
    if not rows:
        return pd.DataFrame()
    return pd.DataFrame(rows).sort_values(
        ["hotspot_score", "evidence_supported_taxa", "n_taxa_scored", "genus_label"],
        ascending=[False, False, False, True],
    )


def write_evidence_partition(t1: pd.DataFrame, out_dir: Path) -> None:
    """Write explicit accepted-key vs pending-crosswalk Track 1 evidence tables."""
    if t1.empty:
        return
    cols = [
        "edge_type", "raw_scientific_name", "accepted_taxon_key", "pending_crosswalk",
        "match_status", "source_id", "allowed_evidence_scope", "canonical_node_ids_json",
    ]
    cols = [c for c in cols if c in t1.columns]
    resolved = t1[t1["accepted_taxon_key"].fillna("") != ""][cols].copy()
    pending = t1[t1["pending_crosswalk"].fillna(False).astype(bool)][cols].copy()
    resolved.to_csv(out_dir / "accepted_key_resolved_reticulation_evidence.tsv", sep="\t", index=False)
    pending.to_csv(out_dir / "pending_crosswalk_reticulation_evidence.tsv", sep="\t", index=False)


def cv(values):
    if len(values) < 3:
        return None
    arr = np.array(values, dtype=float)
    mu = arr.mean()
    if mu == 0:
        return None
    return float(arr.std(ddof=0) / mu)


def compute_components(
    accepted_keys,
    n_evidence_map,
    genus_of,
    family_of,
    ploidy_by_genus,
    chrom_by_genus,
    syn_size,
    conflicts,
    weights=(1.0, 1.0, 1.0, 1.0),
    lam=0.5,
    ablation="none",
):
    rng = random.Random(42)
    rows = []
    w_p, w_c, w_s, w_x = weights

    # Ablation tweaks
    if ablation == "no_ploidy":
        w_p = 0.0
    elif ablation == "no_chrom_cv":
        w_c = 0.0
    elif ablation == "no_synonym":
        w_s = 0.0
    if w_p + w_c + w_s + w_x == 0:
        w_p = w_c = w_s = w_x = 1.0  # degenerate fallback

    for k in accepted_keys:
        n_ev = 0 if ablation == "no_evidence" else n_evidence_map.get(k, 0)

        # observed component
        tci_obs = 1.0 / (1.0 + n_ev)

        g = genus_of.get(k)
        ploidies = ploidy_by_genus.get(g, []) if g else []
        chroms = chrom_by_genus.get(g, []) if g else []

        n_ploidy_states = len(set(ploidies))
        s_ploidy = 1.0 - shannon_entropy_norm(ploidies) if n_ploidy_states > 1 else 1.0
        chrom_cv = cv(chroms)
        s_chrom = 1.0 - min(1.0, chrom_cv) if chrom_cv is not None else 1.0
        syn = syn_size.get(k, 1)
        s_synonym = 1.0 / (1.0 + max(0, syn - 1) / 4.0)
        n_conflict = conflicts.get(k, 0)
        s_conflict = 1.0 / (1.0 + n_conflict)

        # weighted average of structural sub-terms (preserves [0,1])
        wsum = w_p + w_c + w_s + w_x
        tci_struct = (w_p * s_ploidy + w_c * s_chrom + w_s * s_synonym + w_x * s_conflict) / wsum

        # combine
        if ablation == "no_structural":
            tci = tci_obs
        else:
            tci = 1.0 - max(1.0 - tci_obs, lam * (1.0 - tci_struct))

        # provenance
        if n_ev >= 1:
            prov = "evidence_supported"
        elif any(v < 1.0 - 1e-12 for v in (s_ploidy, s_chrom, s_synonym, s_conflict)):
            prov = "structural_only"
        else:
            prov = "data_limited_unknown"

        # confidence
        if n_ev >= 2:
            conf = "high"
        elif n_ev == 1:
            conf = "medium"
        elif (any(v < 1.0 - 1e-12 for v in (s_ploidy, s_chrom, s_synonym, s_conflict))
              and (len(chroms) >= 3 or n_ploidy_states >= 2)):
            conf = "low"
        else:
            conf = "data_limited"

        rows.append({
            "accepted_key": k,
            "genus_key": g,
            "family_key": family_of.get(k),
            "tci": round(tci, 6),
            "tci_observed": round(tci_obs, 6),
            "tci_structural": round(tci_struct, 6),
            "n_evidence_edges": n_ev,
            "n_ploidy_states": n_ploidy_states,
            "n_chrom_counts": len(chroms),
            "chrom_count_cv": None if chrom_cv is None else round(chrom_cv, 6),
            "synonym_cluster_size": syn,
            "n_taxonomic_conflicts": n_conflict,
            "confidence": conf,
            "tci_provenance": prov,
        })
    return rows


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--ablation",
        default="none",
        choices=[
            "none", "no_evidence", "no_structural",
            "no_ploidy", "no_chrom_cv", "no_synonym",
            "shuffle_provenance",
        ],
    )
    ap.add_argument("--weights", default="1,1,1,1", help="w_p,w_c,w_s,w_x")
    ap.add_argument("--lam", type=float, default=0.5)
    ap.add_argument("--out", default=str(OUT_DIR / "tci_per_taxon.tsv"))
    ap.add_argument("--canonical-report", default=str(OUT_DIR / "canonical_recovery_report.tsv"))
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    random.seed(args.seed)
    np.random.seed(args.seed)
    weights = tuple(float(x) for x in args.weights.split(","))
    assert len(weights) == 4

    print(f"[build_tci] loading substrate from {SUBSTRATE}", file=sys.stderr)
    nodes, edges = load_substrate()
    print(f"[build_tci] nodes={len(nodes)} edges={len(edges)}", file=sys.stderr)

    if args.ablation == "shuffle_provenance":
        print(f"[build_tci] shuffling source_id provenance", file=sys.stderr)
        s = edges["source_id"].sample(frac=1.0, random_state=args.seed).reset_index(drop=True)
        edges = edges.copy()
        edges["source_id"] = s.values

    t1 = load_track1_enrichment()
    print(f"[build_tci] track1 enrichment rows={len(t1)}", file=sys.stderr)

    parents = build_parent_map(edges, nodes)
    print(f"[build_tci] parent map size={len(parents)}", file=sys.stderr)
    genus_of, family_of = resolve_genus_family(parents, nodes)

    n_evidence = index_incident_evidence(edges, nodes)
    print(f"[build_tci] taxa with reticulation evidence={len(n_evidence)}", file=sys.stderr)

    feats = genus_structural_features(t1, genus_of)
    ploidy_by_genus = feats["ploidy"]
    chrom_by_genus = feats["chrom"]
    # merge substrate-level chromosome counts (they share semantics with M1.3)
    sub_chrom = substrate_chrom_by_genus(edges, genus_of, parents)
    for g, lst in sub_chrom.items():
        chrom_by_genus[g] = chrom_by_genus.get(g, []) + lst

    syn_size = synonym_cluster_size_per_taxon(edges)
    conflicts = taxonomic_conflict_per_taxon(edges)

    # Score the universe of non-empty accepted-keyed nodes (species + infraspecific + genus + family)
    accepted_keys = sorted({k for k in nodes.accepted_taxon_key.dropna().unique() if k})
    print(f"[build_tci] scoring {len(accepted_keys)} accepted keys", file=sys.stderr)

    rows = compute_components(
        accepted_keys, n_evidence, genus_of, family_of,
        ploidy_by_genus, chrom_by_genus, syn_size, conflicts,
        weights=weights, lam=args.lam, ablation=args.ablation,
    )

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(rows)

    # Attach labels for human readability
    label_map = dict(zip(nodes.node_id, nodes.label))
    df["label"] = df["accepted_key"].map(label_map).fillna("")
    df["genus_label"] = df["genus_key"].map(label_map).fillna("")
    df["family_label"] = df["family_key"].map(label_map).fillna("")
    cols = [
        "accepted_key", "label", "genus_key", "genus_label", "family_key", "family_label",
        "tci", "tci_observed", "tci_structural",
        "n_evidence_edges", "n_ploidy_states", "n_chrom_counts", "chrom_count_cv",
        "synonym_cluster_size", "n_taxonomic_conflicts", "confidence", "tci_provenance",
    ]
    df = df[cols]

    df.to_csv(args.out, sep="\t", index=False)
    print(f"[build_tci] wrote {args.out} rows={len(df)}", file=sys.stderr)
    print(f"[build_tci] provenance breakdown:\n{df['tci_provenance'].value_counts().to_dict()}", file=sys.stderr)
    print(f"[build_tci] evidence_supported count: {(df.n_evidence_edges>0).sum()}", file=sys.stderr)

    hotspots = hotspot_table(df, ploidy_by_genus)
    hotspot_path = OUT_DIR / "tci_hotspots_genus.tsv"
    hotspots.to_csv(hotspot_path, sep="\t", index=False)
    print(f"[build_tci] wrote {hotspot_path} rows={len(hotspots)}", file=sys.stderr)

    write_evidence_partition(t1, OUT_DIR)
    summary = {
        "n_scored_taxa": int(len(df)),
        "n_evidence_supported_taxa": int((df.n_evidence_edges > 0).sum()),
        "n_structural_only_taxa": int((df.tci_provenance == "structural_only").sum()),
        "n_data_limited_unknown_taxa": int((df.tci_provenance == "data_limited_unknown").sum()),
        "n_hotspot_genera": int(len(hotspots)),
        "n_hotspot_genera_sufficient": int((hotspots.data_sufficiency == "sufficient").sum()) if len(hotspots) else 0,
        "tci_min": float(df.tci.min()),
        "tci_mean": float(df.tci.mean()),
        "tci_max": float(df.tci.max()),
        "evidence_boundary": "chromosome_count_assertion and ploidy_state_assertion are structural context, not observed reticulation evidence",
    }
    with (OUT_DIR / "tci_summary.json").open("w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=2, sort_keys=True)
        fh.write("\n")
    print(f"[build_tci] wrote {OUT_DIR / 'tci_summary.json'}", file=sys.stderr)

    # Canonical recovery report (only for --ablation=none).
    # Combines the M1.3 seed-staging table with additional canonical polyploids
    # from the research brief (Key Question 4), looked up by label.
    if args.ablation == "none":
        seed_df = pd.read_csv(T1_SEEDS, sep="\t")
        # Resolvable / multi-source canonical polyploids not in the M1.3 staging
        # but flagged by the brief as canonical recovery targets.
        EXTRA_CANONICAL = [
            "Nicotiana tabacum",        # allotetraploid
            "Gossypium hirsutum",       # allotetraploid
            "Arachis hypogaea",         # allotetraploid; resolved via crop_pedigree
            "Avena sativa",             # allohexaploid; resolved via crop_pedigree
        ]
        label_to_keys = defaultdict(list)
        for _, nr in nodes[["accepted_taxon_key", "label"]].dropna().iterrows():
            label_to_keys[nr["label"]].append(nr["accepted_taxon_key"])
        for lbl in EXTRA_CANONICAL:
            keys = label_to_keys.get(lbl, [])
            key = keys[0] if keys else ""
            status = "resolved" if key else "pending_or_absent"
            seed_df = pd.concat([seed_df, pd.DataFrame([{
                "canonical_seed_taxon": lbl, "status": status,
                "accepted_taxon_key": key, "edge_types_attached": "", "row_count": 0,
            }])], ignore_index=True)

        canon_rows = []
        for _, r in seed_df.iterrows():
            taxon = r["canonical_seed_taxon"]
            key = str(r.get("accepted_taxon_key") or "").strip()
            status = r["status"]
            if status == "missing_from_staging":
                canon_rows.append({
                    "taxon": taxon, "accepted_key": "", "accepted_key_status": "absent",
                    "tci": "", "tci_observed": "",
                    "n_evidence_edges": 0, "recovery_status": "data_limited",
                })
                continue
            if not key:
                canon_rows.append({
                    "taxon": taxon, "accepted_key": "", "accepted_key_status": status,
                    "tci": "", "tci_observed": "",
                    "n_evidence_edges": 0, "recovery_status": "data_limited",
                })
                continue
            sub = df[df.accepted_key == key]
            if sub.empty:
                canon_rows.append({
                    "taxon": taxon, "accepted_key": key, "accepted_key_status": status,
                    "tci": "", "tci_observed": "",
                    "n_evidence_edges": 0, "recovery_status": "data_limited",
                })
                continue
            row = sub.iloc[0]
            recov = "recovered" if (row["n_evidence_edges"] > 0 and row["tci_observed"] < 1.0) else (
                "data_limited" if row["n_evidence_edges"] == 0 else "missed")
            canon_rows.append({
                "taxon": taxon, "accepted_key": key, "accepted_key_status": status,
                "tci": row["tci"], "tci_observed": row["tci_observed"],
                "n_evidence_edges": int(row["n_evidence_edges"]),
                "recovery_status": recov,
            })
        cdf = pd.DataFrame(canon_rows)
        cdf.to_csv(args.canonical_report, sep="\t", index=False)
        print(f"[build_tci] wrote {args.canonical_report}", file=sys.stderr)
        print(f"[build_tci] canonical recovery:\n{cdf['recovery_status'].value_counts().to_dict()}", file=sys.stderr)


if __name__ == "__main__":
    main()
