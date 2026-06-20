# created: 2026-05-17
# cycle: 2
# run_id: run-phytograph-cycle2-fork-e34b5b2c1c6c-clone-2
# agent: worker
# milestone: M1.4
#
# Uniform provenance + staging helpers for paleobotany_sources clone.
# Stdlib-only. Output format: JSONL (line-delimited JSON), one row per node/edge.
#
# Conforms to phytograph_schema.md v1.0 §4 provenance block.

from __future__ import annotations
import json, hashlib, os
from datetime import datetime, timezone

CLONE_ID = "fork-e34b5b2c1c6c/clone-2/M1.4-paleobotany_sources"
ACCESS_DATE = "2026-05-17"  # this cycle


def provenance(
    source_id: str,
    source_name: str,
    source_version_or_release: str,
    license_spdx: str,
    attribution: str,
    confidence: float,
    source_reliability: float,
    access_mode: str = "literature-curated",  # honest disclosure
) -> dict:
    """Return a phytograph_schema.md §4-conforming provenance block."""
    assert 0.0 <= confidence <= 1.0, f"confidence out of range: {confidence}"
    assert 0.0 <= source_reliability <= 1.0, f"source_reliability out of range"
    return {
        "source_id": source_id,
        "source_name": source_name,
        "source_version_or_release": source_version_or_release,
        "access_date": ACCESS_DATE,
        "license": license_spdx,
        "attribution": attribution,
        "ingest_clone_id": CLONE_ID,
        "confidence": confidence,
        "source_reliability": source_reliability,
        "access_mode": access_mode,
    }


def node_row(node_type: str, node_id: str, label: str, provenance_block: dict,
             temporal: dict | None = None, caveat: dict | None = None,
             attrs: dict | None = None) -> dict:
    """One staged node row. node_id must be source-stable."""
    row = {
        "row_kind": "node",
        "node_type": node_type,
        "node_id": node_id,
        "label": label,
        "provenance": provenance_block,
    }
    if temporal is not None:
        row["T"] = temporal
    if caveat is not None:
        row["C"] = caveat
    if attrs is not None:
        row["attrs"] = attrs
    return row


def edge_row(edge_type: str, edge_id: str, members: list[dict],
             provenance_block: dict, temporal: dict | None = None,
             caveat: dict | None = None, attrs: dict | None = None) -> dict:
    """One staged hyperedge row. members = [{node_id, node_type, role}]."""
    assert len(members) >= 1
    row = {
        "row_kind": "edge",
        "edge_type": edge_type,
        "edge_id": edge_id,
        "members": members,
        "provenance": provenance_block,
    }
    if temporal is not None:
        row["T"] = temporal
    if caveat is not None:
        row["C"] = caveat
    if attrs is not None:
        row["attrs"] = attrs
    return row


def canonical_node_id(node_type: str, source_id: str) -> str:
    """Canonical node id = node_type + ':' + source_id (source-stable per schema §6)."""
    return f"{node_type}:{source_id}"


def write_jsonl(path: str, rows: list[dict]) -> int:
    """Write rows to JSONL. Returns count written."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        for r in rows:
            f.write(json.dumps(r, sort_keys=True) + "\n")
    return len(rows)


def read_jsonl(path: str) -> list[dict]:
    with open(path) as f:
        return [json.loads(line) for line in f if line.strip()]


# Schema v1.0 enumerated types (subset relevant to this clone)
ALLOWED_NODE_TYPES = {
    "taxon", "extinct_fauna", "paleo_context", "region",
    "animal_consumer", "fruit_type", "source",
}
ALLOWED_EDGE_TYPES = {
    "anachronism_candidate_edge", "distribution",
    "animal_consumption_or_dispersal", "paleoclimate_overlap_edge",
    "source_assertion",
}

REQUIRED_PROV_FIELDS = {
    "source_id", "source_name", "source_version_or_release",
    "access_date", "license", "attribution", "ingest_clone_id",
    "confidence", "source_reliability",
}
