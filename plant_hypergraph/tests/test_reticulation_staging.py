# created: 2026-05-17T17:05:00Z
# cycle: 2
# run_id: run-phytograph-cycle2-fanout-e34b5b2c1c6c-clone1
# agent: worker
# milestone: M1.3

import csv
import json
from pathlib import Path


BASE = Path("substrate/staging/reticulation_sources/normalized")
REQUIRED = {
    "edge_type",
    "raw_scientific_name",
    "canonical_node_id",
    "node_roles_json",
    "source_id",
    "source_name",
    "access_date",
    "license",
    "allowed_evidence_scope",
}
ALLOWED_EDGE_TYPES = {
    "chromosome_count_assertion",
    "hybridization_event",
    "polyploidization_event",
    "reticulate_inheritance_evidence",
}


def read_rows(name):
    with (BASE / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def test_staged_edge_rows_have_schema_provenance():
    for table in [
        "chromosome_count_assertions.tsv",
        "ploidy_state_assertions.tsv",
        "hybridization_events.tsv",
        "polyploidization_events.tsv",
        "reticulate_inheritance_evidence.tsv",
    ]:
        rows = read_rows(table)
        assert rows, f"{table} should contain at least one staged row or explicit access-limited seed row"
        for row in rows:
            assert row["edge_type"] in ALLOWED_EDGE_TYPES
            for field in REQUIRED:
                assert row.get(field), f"{table} missing {field}"
            assert row["canonical_node_id"].startswith("raw_name:")
            json.loads(row["node_roles_json"])
            json.loads(row["caveats_json"])


def test_hybrid_events_with_asserted_parents_have_two_parent_roles():
    rows = read_rows("hybridization_events.tsv")
    for row in rows:
        roles = json.loads(row["node_roles_json"])
        if "parent_taxa" in roles:
            assert len(roles["parent_taxa"]) >= 2


def test_inferred_ploidy_is_not_marked_as_established_event_fact():
    rows = read_rows("ploidy_state_assertions.tsv")
    assert rows
    for row in rows:
        assert row["edge_type"] == "reticulate_inheritance_evidence"
        assert row["ploidy_assertion_status"] == "inferred_supporting_evidence_not_event"
        caveats = json.loads(row["caveats_json"])
        assert caveats["not_established_source_fact"] is True


def test_count_only_negative_control_does_not_create_polyploid_event():
    events = read_rows("polyploidization_events.tsv") + read_rows("hybridization_events.tsv")
    event_names = {row["raw_scientific_name"] for row in events}
    assert "Arabidopsis thaliana" not in event_names
