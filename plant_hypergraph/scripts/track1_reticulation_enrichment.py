# created: 2026-05-18T00:30:00Z
# cycle: 8
# run_id: run-phytograph-cycle8-fork-56e44dff3ca4-clone0-track1-wave2
# agent: worker
# milestone: _plan/track1-wave2-enrichment-data-limited
"""Track 1 Wave 2 reticulation enrichment at M1.3-limited scale.

Projects the 28 staged M1.3 reticulation seed rows onto the frozen Barrier-1
substrate's accepted-key namespace. Writes only to tracks/track1/data/.

This is NOT the M3.T1 tree_compatibility_index instrument. No reticulation
index, no convergence_signature, no schema fields are added. We attach
accepted_taxon_key where the substrate-published synonym maps resolve the
raw name, otherwise we mark pending_crosswalk=True and preserve the raw
name. Per-file edge_type is used as authoritative (the staged ploidy_state
file currently carries an over-broad edge_type column from a pre-Barrier-1
demotion cycle; we re-label by filename so the brief's five distinct edge
types appear, and audit-log this).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from barrier1_common import (  # noqa: E402
    canonical_member_list,
    load_name_maps,
    norm_name,
    parse_jsonish,
    resolve_name,
)

STAGING_DIR = ROOT / "substrate" / "staging" / "reticulation_sources" / "normalized"
T1_DATA = ROOT / "tracks" / "track1" / "data"
DATASET = ROOT / "phytograph_dataset"

# Per-file edge_type override. File basename → edge_type emitted in enrichment.
# Brief Key Question 2 enumerates these five distinct M1.3 edge types.
FILE_EDGE_TYPE_MAP: dict[str, str] = {
    "chromosome_count_assertions": "chromosome_count_assertion",
    "ploidy_state_assertions": "ploidy_state_assertion",
    "hybridization_events": "hybridization_event",
    "polyploidization_events": "polyploidization_event",
    "reticulate_inheritance_evidence": "reticulate_inheritance_evidence",
}

CANONICAL_SEED_TAXA: list[str] = [
    "Triticum aestivum",
    "Brassica napus",
    "Spartina anglica",
    "Tragopogon mirus",
    "Tragopogon miscellus",
    "Musa acuminata × balbisiana",
    "Musa acuminata",
    "Musa balbisiana",
]


def load_staged(file_basename: str) -> pd.DataFrame:
    path = STAGING_DIR / f"{file_basename}.tsv"
    df = pd.read_csv(path, sep="\t", dtype=str, keep_default_na=False)
    df["src_file"] = file_basename
    df["assigned_edge_type"] = FILE_EDGE_TYPE_MAP[file_basename]
    return df


def enrich(df: pd.DataFrame, accepted_map: dict[str, str], synonym_map: dict[str, str]) -> pd.DataFrame:
    out_rows: list[dict] = []
    for row in df.itertuples(index=False):
        raw_name = str(getattr(row, "raw_scientific_name", "")).strip()
        accepted_key, match_status, ambiguity_reason = resolve_name(
            raw_name, accepted_map, synonym_map
        )
        pending = not bool(accepted_key)
        role_map_raw = getattr(row, "node_roles_json", "")
        role_map = parse_jsonish(role_map_raw)
        caveats_raw = getattr(row, "caveats_json", "")
        caveats = parse_jsonish(caveats_raw)
        # Tag this row's canonicalization status for downstream auditors.
        caveats = dict(caveats) if isinstance(caveats, dict) else {"_orig": caveats}
        caveats["canonicalization_status"] = match_status
        if ambiguity_reason:
            caveats["ambiguity_reason"] = ambiguity_reason
        # Build canonical member set using Barrier-1 logic.
        members = canonical_member_list(
            edge_type=getattr(row, "assigned_edge_type"),
            raw_scientific_name=raw_name,
            accepted_taxon_key=accepted_key,
            role_map=role_map,
        )
        out = {
            "edge_type": getattr(row, "assigned_edge_type"),
            "raw_scientific_name": raw_name,
            "accepted_taxon_key": accepted_key,
            "pending_crosswalk": pending,
            "match_status": match_status,
            "node_roles_json": json.dumps(role_map, sort_keys=True) if role_map else "{}",
            "canonical_node_ids_json": json.dumps(members),
            "source_id": getattr(row, "source_id", ""),
            "source_name": getattr(row, "source_name", ""),
            "source_version_or_release": getattr(row, "source_version_or_release", ""),
            "access_date": getattr(row, "access_date", ""),
            "license": getattr(row, "license", ""),
            "attribution": getattr(row, "attribution", ""),
            "confidence": getattr(row, "confidence", ""),
            "source_reliability": getattr(row, "source_reliability", ""),
            "allowed_evidence_scope": getattr(row, "allowed_evidence_scope", ""),
            "caveats_json": json.dumps(caveats, sort_keys=True),
            "temporal_annotation": getattr(row, "temporal_annotation", ""),
            "staged_edge_type_column": getattr(row, "edge_type", ""),
            "source_file_basename": getattr(row, "src_file"),
        }
        # Preserve chromosome-count-specific fields if present.
        for col in (
            "raw_count",
            "count_type",
            "parsed_min",
            "parsed_max",
            "is_range",
            "is_approximate",
            "is_mixed_or_irregular",
            "parse_status",
            "count_source_type",
            "ploidy_state",
            "ploidy_assertion_status",
        ):
            if hasattr(row, col):
                out[col] = getattr(row, col)
        out_rows.append(out)
    return pd.DataFrame(out_rows)


def main() -> None:
    T1_DATA.mkdir(parents=True, exist_ok=True)
    accepted_map, synonym_map = load_name_maps()
    print(f"loaded substrate maps: accepted={len(accepted_map)} synonym={len(synonym_map)}")

    per_type: dict[str, pd.DataFrame] = {}
    all_frames: list[pd.DataFrame] = []
    staged_counts: dict[str, int] = {}
    for basename, edge_type in FILE_EDGE_TYPE_MAP.items():
        staged = load_staged(basename)
        staged_counts[edge_type] = len(staged)
        enriched = enrich(staged, accepted_map, synonym_map)
        per_type[edge_type] = enriched
        out_path = T1_DATA / f"{basename}.parquet"
        enriched.to_parquet(out_path, index=False)
        print(f"wrote {out_path} rows={len(enriched)}")
        all_frames.append(enriched)

    union = pd.concat(all_frames, ignore_index=True, sort=False)
    union_path = T1_DATA / "reticulation_enrichment_edges.parquet"
    union.to_parquet(union_path, index=False)
    print(f"wrote {union_path} rows={len(union)}")

    # Coverage summary
    summary_rows = []
    for edge_type, df in per_type.items():
        resolved = int((~df["pending_crosswalk"]).sum())
        pending = int(df["pending_crosswalk"].sum())
        keys_covered = int(df.loc[~df["pending_crosswalk"], "accepted_taxon_key"].nunique())
        source_breakdown = df["source_id"].value_counts().to_dict()
        license_breakdown = df["license"].value_counts().to_dict()
        summary_rows.append(
            {
                "edge_type": edge_type,
                "staged_rows": staged_counts[edge_type],
                "resolved_rows": resolved,
                "pending_rows": pending,
                "accepted_keys_covered": keys_covered,
                "source_id_breakdown": json.dumps(source_breakdown, sort_keys=True),
                "license_breakdown": json.dumps(license_breakdown, sort_keys=True),
            }
        )
    summary = pd.DataFrame(summary_rows)
    summary_path = T1_DATA / "reticulation_coverage_summary.tsv"
    summary.to_csv(summary_path, sep="\t", index=False)
    print(f"wrote {summary_path}")

    # Canonical seed case status
    seed_rows = []
    for seed in CANONICAL_SEED_TAXA:
        norm_seed = norm_name(seed)
        # find all rows matching by normalized raw name across the union
        match = union[union["raw_scientific_name"].apply(norm_name) == norm_seed]
        if len(match) == 0:
            status = "missing_from_staging"
            attached_types: list[str] = []
            accepted_key = ""
        else:
            accepted_keys = set(match.loc[~match["pending_crosswalk"], "accepted_taxon_key"].tolist())
            if accepted_keys:
                status = "resolved"
                accepted_key = sorted(accepted_keys)[0]
            else:
                status = "pending_crosswalk"
                accepted_key = ""
            attached_types = sorted(set(match["edge_type"].tolist()))
        seed_rows.append(
            {
                "canonical_seed_taxon": seed,
                "status": status,
                "accepted_taxon_key": accepted_key,
                "edge_types_attached": ",".join(attached_types),
                "row_count": int(len(match)),
            }
        )
    seed_df = pd.DataFrame(seed_rows)
    seed_path = T1_DATA / "canonical_seed_case_status.tsv"
    seed_df.to_csv(seed_path, sep="\t", index=False)
    print(f"wrote {seed_path}")

    # Quick summary to stdout
    total_staged = sum(staged_counts.values())
    total_emitted = len(union)
    total_resolved = int((~union["pending_crosswalk"]).sum())
    print(
        f"SUMMARY staged={total_staged} emitted={total_emitted} "
        f"resolved={total_resolved} pending={total_emitted - total_resolved} "
        f"distinct_edge_types={union['edge_type'].nunique()}"
    )


if __name__ == "__main__":
    main()
