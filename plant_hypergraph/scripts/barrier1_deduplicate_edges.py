# created: 2026-05-17T21:25:00Z
# cycle: 4
# run_id: run-phytograph-cycle4-barrier1
# agent: worker
# milestone: _plan/barrier1-substrate-freeze
"""Deduplicate merged Barrier-1 hyperedges by canonical edge key."""

from __future__ import annotations

import json

import pandas as pd

from barrier1_common import DATASET, ROOT, write_parquet, write_tsv


def sorted_members(value: str) -> str:
    try:
        members = json.loads(value) if isinstance(value, str) else []
    except Exception:
        members = [str(value)]
    return json.dumps(sorted({str(m) for m in members if str(m)}))


def member_width(value: str) -> int:
    try:
        parsed = json.loads(value) if isinstance(value, str) else []
    except Exception:
        parsed = []
    return len({str(m) for m in parsed if str(m)})


def non_tax_role_signature(value: str) -> str:
    try:
        parsed = json.loads(value) if isinstance(value, str) else {}
    except Exception:
        parsed = {}
    members: list[str] = []

    def walk(role: str, item: object) -> None:
        if isinstance(item, dict):
            for key, inner in item.items():
                walk(str(key), inner)
        elif isinstance(item, list):
            for inner in item:
                walk(role, inner)
        else:
            text = str(item).strip()
            if not text or text.lower() == "nan":
                return
            if role in {"taxon", "source"} or text.startswith(("unresolved_taxon_name:", "raw_name:", "wfo:")):
                return
            members.append(f"{role}={text}")

    if isinstance(parsed, dict):
        for key, inner in parsed.items():
            walk(str(key), inner)
    return json.dumps(sorted(set(members)))


def main() -> None:
    edges = pd.read_parquet(DATASET / "hyperedges.parquet")
    edges["dedup_members"] = edges["canonical_node_ids_json"].map(sorted_members)
    # Intentional intra-source multiplicity survives when record IDs differ and the source allows it.
    edges["multiplicity_component"] = ""
    keep_multiplicity = edges["evidence_multiplicity_allowed"].fillna(False).astype(bool)
    edges.loc[keep_multiplicity, "multiplicity_component"] = edges.loc[keep_multiplicity, "source_record_id"].fillna("").astype(str)
    edges["dedup_key"] = (
        edges["edge_type"].astype(str)
        + "\t"
        + edges["dedup_members"].astype(str)
        + "\t"
        + edges["source_id"].astype(str)
        + "\t"
        + edges["multiplicity_component"].astype(str)
    )
    raw_name_key = (
        edges["edge_type"].astype(str)
        + "\t"
        + edges["raw_scientific_name"].fillna("").astype(str).str.strip().str.lower()
        + "\t"
        + edges["source_id"].astype(str)
        + "\t"
        + edges["multiplicity_component"].astype(str)
    )
    edge_type_audit = (
        edges.assign(raw_name_key=raw_name_key)
        .groupby(["source_group", "edge_type"], dropna=False)
        .agg(
            input_rows=("edge_id", "count"),
            retained_raw_name_only_before=("raw_name_key", pd.Series.nunique),
            retained_full_member_after=("dedup_key", pd.Series.nunique),
        )
        .reset_index()
    )
    edge_type_audit["raw_name_only_collapsed_rows"] = edge_type_audit["input_rows"] - edge_type_audit["retained_raw_name_only_before"]
    edge_type_audit["full_member_collapsed_rows"] = edge_type_audit["input_rows"] - edge_type_audit["retained_full_member_after"]
    write_tsv(edge_type_audit, DATASET / "dedup_before_after_by_edge_type.tsv")
    group_sizes = edges.groupby("dedup_key").size().rename("group_size").reset_index()
    duplicate_keys = group_sizes[group_sizes["group_size"] > 1]["dedup_key"]
    duplicate_groups = edges[edges["dedup_key"].isin(duplicate_keys)].copy()
    write_parquet(duplicate_groups, DATASET / "duplicate_edge_groups.parquet")
    collision_audit = (
        duplicate_groups.assign(
            canonical_member_width=duplicate_groups["canonical_node_ids_json"].map(member_width),
            role_signature=duplicate_groups["role_map_json"].fillna("{}").astype(str),
            non_tax_role_signature=duplicate_groups["role_map_json"].fillna("{}").astype(str).map(non_tax_role_signature),
        )
        .groupby(["source_group", "edge_type", "dedup_key"], dropna=False)
        .agg(
            rows=("edge_id", "count"),
            distinct_role_maps=("role_signature", pd.Series.nunique),
            distinct_non_tax_role_maps=("non_tax_role_signature", pd.Series.nunique),
            min_member_width=("canonical_member_width", "min"),
            max_member_width=("canonical_member_width", "max"),
            example_edge_id=("edge_id", "first"),
        )
        .reset_index()
        .sort_values(["source_group", "edge_type", "rows"], ascending=[True, True, False])
    )
    write_tsv(collision_audit, DATASET / "dedup_collision_audit.tsv")

    retained = edges.sort_values(["dedup_key", "confidence"], ascending=[True, False]).drop_duplicates("dedup_key", keep="first").copy()
    retained = retained.drop(columns=["dedup_members", "multiplicity_component", "dedup_key"])
    write_parquet(retained, DATASET / "hyperedges.parquet")

    report = (
        edges.assign(was_duplicate=edges["dedup_key"].isin(duplicate_keys))
        .groupby("source_group", dropna=False)
        .agg(
            input_edges=("edge_id", "count"),
            retained_edges=("dedup_key", pd.Series.nunique),
            duplicate_groups=("dedup_key", lambda s: int(s[s.isin(duplicate_keys)].nunique())),
            duplicate_rows=("was_duplicate", "sum"),
            multiplicity_preserved_rows=("evidence_multiplicity_allowed", "sum"),
        )
        .reset_index()
    )
    report["collapsed_rows"] = report["input_edges"] - report["retained_edges"]
    write_tsv(report, DATASET / "dedup_report.tsv")

    member_audit = (
        edges.assign(canonical_member_width=edges["canonical_node_ids_json"].map(member_width), retained=~edges.duplicated("dedup_key", keep="first"))
        .groupby(["source_group", "edge_type"], dropna=False)
        .agg(
            input_rows=("edge_id", "count"),
            resolved_keys=("accepted_taxon_key", lambda s: int(s.fillna("").astype(str).str.len().gt(0).sum())),
            unresolved_rows=("accepted_taxon_key", lambda s: int(s.fillna("").astype(str).str.len().eq(0).sum())),
            min_member_width=("canonical_member_width", "min"),
            median_member_width=("canonical_member_width", "median"),
            max_member_width=("canonical_member_width", "max"),
            retained_rows=("retained", "sum"),
        )
        .reset_index()
    )
    member_audit["deduplicated_rows"] = member_audit["input_rows"] - member_audit["retained_rows"]
    write_tsv(member_audit, DATASET / "canonical_member_audit.tsv")
    print(report.to_string(index=False))


if __name__ == "__main__":
    main()
