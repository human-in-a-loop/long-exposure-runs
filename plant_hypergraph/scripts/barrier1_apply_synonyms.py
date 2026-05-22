# created: 2026-05-17T21:20:00Z
# cycle: 4
# run_id: run-phytograph-cycle4-barrier1
# agent: worker
# milestone: _plan/barrier1-substrate-freeze
"""Apply WFO accepted-name and synonym-cluster resolution to merged raw names."""

from __future__ import annotations

import json

import pandas as pd

from barrier1_common import DATASET, ROOT, canonical_members_json, load_name_maps, norm_name, parse_jsonish, write_parquet, write_tsv


def classify_resolution(raw_names: pd.Series, accepted_map: dict[str, str], synonym_map: dict[str, str]) -> pd.DataFrame:
    raw = raw_names.fillna("").astype(str)
    normalized = raw.str.strip().str.lower()
    accepted_exact = normalized.map(accepted_map)
    synonym_exact = normalized.map(synonym_map)
    accepted_key = accepted_exact.fillna(synonym_exact).fillna("")
    status = pd.Series("unresolved", index=raw.index)
    status[raw.str.strip() == ""] = "missing_raw_name"
    status[accepted_exact.notna()] = "accepted_exact"
    status[accepted_exact.isna() & synonym_exact.notna()] = "synonym_exact"
    reason = pd.Series("no exact WFO accepted-name or synonym-cluster match", index=raw.index)
    reason[status == "missing_raw_name"] = "missing raw scientific name"
    reason[status.isin(["accepted_exact", "synonym_exact"])] = ""
    return pd.DataFrame(
        {
            "raw_scientific_name": raw,
            "normalized_name_key": normalized,
            "accepted_taxon_key": accepted_key,
            "match_status": status,
            "ambiguity_reason": reason,
        }
    )


def main() -> None:
    accepted_map, synonym_map = load_name_maps()
    edges = pd.read_parquet(DATASET / "hyperedges.parquet")
    before = (
        edges.groupby("source_group", dropna=False)
        .agg(rows_before=("edge_id", "count"), raw_name_diversity_before=("raw_scientific_name", pd.Series.nunique))
        .reset_index()
    )
    resolution = classify_resolution(edges["raw_scientific_name"], accepted_map, synonym_map)
    resolution.insert(0, "edge_id", edges["edge_id"].values)
    resolution.insert(1, "source_group", edges["source_group"].values)
    resolution.insert(2, "edge_type", edges["edge_type"].values)
    resolution["matched_synonym_id"] = ""
    resolution.loc[resolution["match_status"] == "synonym_exact", "matched_synonym_id"] = resolution.loc[
        resolution["match_status"] == "synonym_exact", "normalized_name_key"
    ]
    write_parquet(resolution, DATASET / "synonym_resolution.parquet")

    resolved = resolution["accepted_taxon_key"].astype(str).str.len().gt(0)
    edges.loc[resolved, "accepted_taxon_key"] = resolution.loc[resolved, "accepted_taxon_key"].values
    edges.loc[resolved, "pending_crosswalk"] = False
    edges.loc[~resolved, "pending_crosswalk"] = True
    if "caveats" not in edges.columns:
        edges["caveats"] = ""
    unresolved_mask = ~resolved
    edges.loc[unresolved_mask, "caveats"] = [
        _append_resolution_caveat(caveat, status, reason)
        for caveat, status, reason in zip(
            edges.loc[unresolved_mask, "caveats"].astype(str),
            resolution.loc[unresolved_mask, "match_status"].astype(str),
            resolution.loc[unresolved_mask, "ambiguity_reason"].astype(str),
        )
    ]
    edges["canonical_node_ids_json"] = [
        canonical_members_json(
            edge_type=row.edge_type,
            raw_scientific_name=row.raw_scientific_name,
            accepted_taxon_key=row.accepted_taxon_key,
            role_map=row.role_map_json,
            extra_members=_raw_members(row.raw_node_ids_json),
        )
        for row in edges.itertuples(index=False)
    ]
    write_parquet(edges, DATASET / "hyperedges.parquet")

    propagated = []
    for row, res in zip(edges.itertuples(index=False), resolution.itertuples(index=False)):
        if not str(res.accepted_taxon_key):
            continue
        members = set(_raw_members(row.canonical_node_ids_json))
        propagated.append(
            {
                "source_group": row.source_group,
                "edge_type": row.edge_type,
                "edge_id": row.edge_id,
                "accepted_taxon_key": res.accepted_taxon_key,
                "propagated": str(row.accepted_taxon_key) == str(res.accepted_taxon_key) and not bool(row.pending_crosswalk) and str(res.accepted_taxon_key) in members,
            }
        )
    propagation = pd.DataFrame(propagated)
    if propagation.empty:
        propagation_summary = pd.DataFrame(columns=["source_group", "edge_type", "resolved_rows", "propagated_rows", "missing_rows"])
    else:
        propagation_summary = (
            propagation.groupby(["source_group", "edge_type"], dropna=False)
            .agg(resolved_rows=("edge_id", "count"), propagated_rows=("propagated", "sum"))
            .reset_index()
        )
        propagation_summary["missing_rows"] = propagation_summary["resolved_rows"] - propagation_summary["propagated_rows"]
    write_tsv(propagation_summary, DATASET / "resolved_key_propagation_audit.tsv")

    unresolved = resolution[~resolution["match_status"].isin(["accepted_exact", "synonym_exact"])].copy()
    write_tsv(unresolved, DATASET / "unresolved_names.tsv")

    after = (
        resolution.assign(resolved_key=lambda d: d["accepted_taxon_key"].where(d["accepted_taxon_key"].astype(bool), d["normalized_name_key"]))
        .groupby("source_group", dropna=False)
        .agg(
            rows_after=("edge_id", "count"),
            accepted_key_diversity_after=("resolved_key", pd.Series.nunique),
            resolved_rows=("accepted_taxon_key", lambda s: int(s.astype(bool).sum())),
            unresolved_rows=("accepted_taxon_key", lambda s: int((~s.astype(bool)).sum())),
        )
        .reset_index()
    )
    delta = before.merge(after, on="source_group", how="outer").fillna(0)
    delta["diversity_delta"] = delta["accepted_key_diversity_after"] - delta["raw_name_diversity_before"]
    write_tsv(delta, DATASET / "synonym_normalization_delta.tsv")
    write_tsv(delta, ROOT / "substrate" / "barrier1_synonym_normalization_delta.tsv")

    reasons = (
        unresolved.groupby(["source_group", "ambiguity_reason"], dropna=False)
        .size()
        .reset_index(name="rows")
        .sort_values(["source_group", "rows"], ascending=[True, False])
    )
    write_tsv(reasons, ROOT / "substrate" / "barrier1_unresolved_name_reasons.tsv")
    print(delta.to_string(index=False))


def _raw_members(value: object) -> list[str]:
    parsed = parse_jsonish(value)
    if isinstance(parsed, list):
        return [str(v) for v in parsed if str(v)]
    if isinstance(parsed, dict):
        return [str(v) for v in parsed.values() if isinstance(v, str) and v]
    return []


def _append_resolution_caveat(caveat: str, status: str, reason: str) -> str:
    addition = f"canonicalization_status={status}; ambiguity_reason={reason}"
    if not caveat or caveat.lower() == "nan":
        return addition
    if "canonicalization_status=" in caveat:
        return caveat
    return f"{caveat}; {addition}"


if __name__ == "__main__":
    main()
