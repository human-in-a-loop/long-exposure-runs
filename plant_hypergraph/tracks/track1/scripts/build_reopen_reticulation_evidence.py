#!/usr/bin/env python3
# created: 2026-05-18T16:05:00+00:00
# cycle: 23
# run_id: run-phytograph-cycle23-track1-reopen-reticulation-evidence
# agent: worker
# milestone: _plan/track1-reticulation-reopen-evidence
"""Build Track 1 reopen evidence candidate tables from local source artifacts."""
from __future__ import annotations

import csv
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
TRACK = ROOT / "tracks" / "track1"
DATA = TRACK / "data"

CANDIDATES = DATA / "reticulation_reopen_candidate_events.tsv"
DIAGNOSTICS = DATA / "reticulation_reopen_join_diagnostics.tsv"

RESCUED = DATA / "barrier4_rescued_reticulation_edges.tsv"
RECOVERY = DATA / "barrier4_canonical_key_recovery.tsv"
ACCEPTED_BASELINE = TRACK / "outputs" / "accepted_key_resolved_reticulation_evidence.tsv"
PENDING_BASELINE = TRACK / "outputs" / "pending_crosswalk_reticulation_evidence.tsv"
NORMALIZED = ROOT / "substrate" / "staging" / "reticulation_sources" / "normalized"

EVENT_TYPES = {
    "hybridization_event",
    "polyploidization_event",
    "reticulate_inheritance_evidence",
}

ACCEPTED_NAME_BY_KEY = {
    "wfo:wfo-0000905667-2025-12": "Triticum aestivum",
    "wfo:wfo-0000571271-2025-12": "Brassica napus",
    "wfo:wfo-0001341446-2025-12": "Sporobolus anglicus",
    "wfo:wfo-0000473834-2025-12": "Musa acuminata",
    "wfo:wfo-0000473990-2025-12": "Musa balbisiana",
}

SOURCE_NAME = {
    "ccdb": "CCDB chromosome-count seed rows",
    "wood_2009_polyploid_speciation": "Wood et al. 2009 polyploid speciation synthesis",
}


def event_shape_status(edge_type: str, event_shaped: bool) -> str:
    if edge_type in EVENT_TYPES and event_shaped:
        return "event_shaped"
    if edge_type == "chromosome_count_assertion":
        return "chromosome_count_only"
    if edge_type == "ploidy_state_assertion":
        return "ploidy_context_only"
    return "rejected_ambiguous_event_shape"


def snippet(edge_type: str, caveats_json: str) -> str:
    try:
        caveats = json.loads(caveats_json)
    except Exception:
        caveats = {}
    if edge_type == "chromosome_count_assertion":
        return str(caveats.get("raw_count", "chromosome count only"))
    note = str(caveats.get("note", "")).strip()
    parents = caveats.get("parent_names_raw", [])
    if parents:
        return f"{note}; parents={', '.join(parents)}"
    return note or edge_type


def load_rejected_event_rows() -> list[dict[str, str]]:
    recovery = pd.read_csv(RECOVERY, sep="\t", dtype=str).fillna("")
    unrecovered = set(
        recovery.loc[recovery["rescued_accepted_key"] == "", "seed_taxon"].astype(str)
    )
    rows: list[dict[str, str]] = []
    for filename in [
        "hybridization_events.tsv",
        "polyploidization_events.tsv",
        "reticulate_inheritance_evidence.tsv",
    ]:
        path = NORMALIZED / filename
        if not path.exists():
            continue
        df = pd.read_csv(path, sep="\t", dtype=str).fillna("")
        for _, row in df[df["raw_scientific_name"].isin(unrecovered)].iterrows():
            rows.append(
                {
                    "source_id": row["source_id"],
                    "source_name": row["source_name"],
                    "raw_taxon_name": row["raw_scientific_name"],
                    "accepted_key": "",
                    "accepted_name": "",
                    "event_type": row["edge_type"],
                    "evidence_scope": row["allowed_evidence_scope"],
                    "event_shape_status": "rejected_no_accepted_key",
                    "provenance_url_or_path": str(path),
                    "license_or_access_note": row["license"],
                    "supporting_text_snippet": snippet(row["edge_type"], row["caveats_json"]),
                    "join_method": "rejected_no_full_wfo_accepted_key",
                    "caveat": "event-shaped source row retained as inspected context but rejected because no accepted WFO key was recovered",
                }
            )
    return rows


def build_candidate_rows() -> pd.DataFrame:
    rescued = pd.read_csv(RESCUED, sep="\t", dtype=str).fillna("")
    rows: list[dict[str, str]] = []
    for _, row in rescued.iterrows():
        accepted_key = row["rescued_accepted_key"] or row["accepted_taxon_key"]
        join_method = (
            "synonym_rescue_full_wfo"
            if "synonym" in row["rescue_basis"] or row["raw_scientific_name"] == "Spartina anglica"
            else "exact_name_full_wfo"
        )
        caveat = row["allowed_evidence_scope"]
        if join_method.startswith("synonym"):
            caveat += "; synonym rescue, not exact accepted-name recovery"
        if row["edge_type"] not in EVENT_TYPES:
            caveat += "; context only and excluded from reopen event-shaped count"
        rows.append(
            {
                "source_id": row["source_id"],
                "source_name": SOURCE_NAME.get(row["source_id"], row["source_id"]),
                "raw_taxon_name": row["raw_scientific_name"],
                "accepted_key": accepted_key,
                "accepted_name": ACCEPTED_NAME_BY_KEY.get(accepted_key, ""),
                "event_type": row["edge_type"],
                "evidence_scope": row["allowed_evidence_scope"],
                "event_shape_status": event_shape_status(
                    row["edge_type"], str(row["event_shaped_edge"]).lower() == "true"
                ),
                "provenance_url_or_path": str(RESCUED),
                "license_or_access_note": "local cached WFO rescue plus original source license/access note; no live provider call",
                "supporting_text_snippet": snippet(row["edge_type"], row["caveats_json"]),
                "join_method": join_method,
                "caveat": caveat,
            }
        )
    rows.extend(load_rejected_event_rows())
    return pd.DataFrame(rows)


def build_diagnostics(candidates: pd.DataFrame) -> pd.DataFrame:
    accepted = pd.read_csv(ACCEPTED_BASELINE, sep="\t", dtype=str).fillna("")
    pending = pd.read_csv(PENDING_BASELINE, sep="\t", dtype=str).fillna("")
    baseline = pd.concat([accepted, pending], ignore_index=True)
    rows = [
        {
            "source_name": "Barrier 4 frozen accepted-subset baseline",
            "candidate_rows": len(baseline),
            "accepted_key_rows": int((baseline["accepted_taxon_key"] != "").sum()),
            "event_shaped_rows": 0,
            "exact_name_joins": int((accepted["match_status"] == "accepted_exact").sum()),
            "synonym_rescue_joins": 0,
            "rejected_rows": int((baseline["accepted_taxon_key"] == "").sum()),
            "dominant_rejection_reason": "frozen_subset_pending_crosswalk; accepted rows were chromosome/ploidy context only",
        }
    ]
    for source_name, group in candidates.groupby("source_name", sort=True):
        accepted_mask = group["accepted_key"] != ""
        event_mask = group["event_shape_status"] == "event_shaped"
        exact_mask = group["join_method"] == "exact_name_full_wfo"
        synonym_mask = group["join_method"] == "synonym_rescue_full_wfo"
        rejected = int((~accepted_mask).sum())
        if rejected:
            reason = "missing accepted WFO key for inspected event-shaped rows"
        elif not event_mask.any():
            reason = "chromosome-count-only context; no event-shaped rows"
        elif synonym_mask.any():
            reason = "accepted-key gain depends partly on synonym rescue and one source"
        else:
            reason = "none"
        rows.append(
            {
                "source_name": source_name,
                "candidate_rows": len(group),
                "accepted_key_rows": int(accepted_mask.sum()),
                "event_shaped_rows": int((accepted_mask & event_mask).sum()),
                "exact_name_joins": int((accepted_mask & exact_mask).sum()),
                "synonym_rescue_joins": int((accepted_mask & synonym_mask).sum()),
                "rejected_rows": rejected,
                "dominant_rejection_reason": reason,
            }
        )
    return pd.DataFrame(rows)


def main() -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    candidates = build_candidate_rows()
    diagnostics = build_diagnostics(candidates)
    columns = [
        "source_id",
        "source_name",
        "raw_taxon_name",
        "accepted_key",
        "accepted_name",
        "event_type",
        "evidence_scope",
        "event_shape_status",
        "provenance_url_or_path",
        "license_or_access_note",
        "supporting_text_snippet",
        "join_method",
        "caveat",
    ]
    candidates.to_csv(CANDIDATES, sep="\t", index=False, columns=columns, quoting=csv.QUOTE_MINIMAL)
    diagnostics.to_csv(DIAGNOSTICS, sep="\t", index=False, quoting=csv.QUOTE_MINIMAL)


if __name__ == "__main__":
    main()
