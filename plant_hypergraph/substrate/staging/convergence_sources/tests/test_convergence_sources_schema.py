# created: 2026-05-17T18:20:00Z
# cycle: 2
# run_id: run-phytograph-cycle2-fanout-e34b5b2c1c6c-clone3
# agent: worker
# milestone: M1.5
"""Schema and evidence-scope checks for M1.5 convergence-source staging."""

from __future__ import annotations

import csv
import json
import pathlib

BASE = pathlib.Path(__file__).resolve().parents[1]
DATA = BASE / "data"


def rows(name: str) -> list[dict[str, str]]:
    with (DATA / name).open("r", newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def test_required_files_exist() -> None:
    for name in [
        "staged_nodes.tsv",
        "staged_edges.tsv",
        "source_registry.tsv",
        "rejected_records.tsv",
        "ingest_summary.json",
    ]:
        assert (DATA / name).exists(), name
    assert (BASE / "INGEST_AUDIT.md").exists()


def test_edge_types_are_frozen_schema_types() -> None:
    edges = rows("staged_edges.tsv")
    assert edges
    assert {row["edge_type"] for row in edges} <= {"fruit_morphology", "life_form", "trait_syndrome", "convergence_signature"}
    assert "convergence_signature" not in {row["edge_type"] for row in edges}


def test_provenance_complete_for_every_edge() -> None:
    required = [
        "source_id",
        "source_name",
        "source_version",
        "source_url",
        "doi",
        "license",
        "attribution",
        "access_date",
        "source_reliability",
        "confidence",
        "allowed_evidence_scope",
        "disallowed_evidence_scope",
        "ingest_clone_id",
    ]
    for row in rows("staged_edges.tsv"):
        assert all(row[field] for field in required), row["edge_id"]
        assert row["ingest_clone_id"] == "clone-3"
        json.loads(row["role_map_json"])


def test_scale_threshold_has_at_least_five_lists() -> None:
    counts: dict[str, int] = {}
    for row in rows("staged_edges.tsv"):
        counts[row["trait_name"]] = counts.get(row["trait_name"], 0) + 1
    assert sum(1 for value in counts.values() if value >= 500) >= 5


def test_evidence_scope_is_not_overclaimed() -> None:
    for row in rows("staged_edges.tsv"):
        forbidden = row["disallowed_evidence_scope"]
        if row["edge_type"] == "fruit_morphology":
            assert "ecological dispersal syndrome" in forbidden
        assert "convergence" in forbidden or "phylogenetic independence" in forbidden
        assert row["direct_source_claim"] == "true"


def test_taxonomy_is_preserved_as_unresolved() -> None:
    edges = rows("staged_edges.tsv")
    nodes = rows("staged_nodes.tsv")
    assert {row["pending_crosswalk"] for row in edges} == {"true"}
    taxon_nodes = [row for row in nodes if row["node_type"] == "unresolved_taxon_name"]
    assert taxon_nodes
    assert {row["pending_crosswalk"] for row in taxon_nodes} == {"true"}


def test_negative_checks_are_recorded() -> None:
    rejected = rows("rejected_records.tsv")
    assert len(rejected) >= 20
    classes = {row["reject_class"] for row in rejected}
    assert {"forbidden_scope", "inference", "forbidden_expansion", "license_registration"} <= classes
