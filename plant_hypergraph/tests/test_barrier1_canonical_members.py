# created: 2026-05-17T23:05:00Z
# cycle: 7
# run_id: run-phytograph-cycle7-barrier1-canonical-member-repair
# agent: worker
# milestone: _plan/barrier1-canonical-member-repair

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "tools"))

from barrier1_common import canonical_member_list  # noqa: E402
from validate_barrier1_substrate import validate_edges_df, validate_nodes_df  # noqa: E402


def test_same_taxon_different_trait_members_do_not_collapse():
    first = canonical_member_list(
        edge_type="trait_syndrome",
        raw_scientific_name="Acaena x ovina",
        accepted_taxon_key="wfo:test-acaena-ovina",
        role_map={"taxon": "unresolved_taxon_name:acaena_x_ovina", "trait": "trait:fruit_fleshy"},
    )
    second = canonical_member_list(
        edge_type="trait_syndrome",
        raw_scientific_name="Acaena x ovina",
        accepted_taxon_key="wfo:test-acaena-ovina",
        role_map={"taxon": "unresolved_taxon_name:acaena_x_ovina", "trait": "trait:elaiosome"},
    )
    assert first != second
    assert "trait:fruit_fleshy" in first
    assert "trait:elaiosome" in second


def test_same_taxon_different_compound_members_do_not_collapse():
    first = canonical_member_list(
        edge_type="phytochemical_assertion",
        raw_scientific_name="Abelmoschus esculentus",
        accepted_taxon_key="wfo:test-okra",
        role_map={},
        extra_members=["DUKE_CHEM:QUERCETIN", "Flower"],
    )
    second = canonical_member_list(
        edge_type="phytochemical_assertion",
        raw_scientific_name="Abelmoschus esculentus",
        accepted_taxon_key="wfo:test-okra",
        role_map={},
        extra_members=["DUKE_CHEM:RUTIN", "Flower"],
    )
    assert first != second
    assert "DUKE_CHEM:QUERCETIN" in first
    assert "DUKE_CHEM:RUTIN" in second


def test_resolved_row_has_accepted_key_pending_false_and_member():
    row = pd.DataFrame(
        [
            {
                "edge_id": "ok:resolved",
                "edge_type": "trait_syndrome",
                "source_id": "test",
                "access_date": "2026-05-17",
                "license": "test",
                "provenance_pointer": "test",
                "allowed_evidence_scope": "source-stated assertion only",
                "caveats": "test",
                "inferred_flag": False,
                "raw_scientific_name": "Acaena ovina",
                "accepted_taxon_key": "wfo:wfo-0000985080-2025-12",
                "pending_crosswalk": False,
                "canonical_node_ids_json": json.dumps(["wfo:wfo-0000985080-2025-12", "trait:test"]),
            }
        ]
    )
    assert validate_edges_df(row) == []


def test_unresolved_row_keeps_raw_name_and_machine_reason():
    row = pd.DataFrame(
        [
            {
                "edge_id": "ok:unresolved",
                "edge_type": "trait_syndrome",
                "source_id": "test",
                "access_date": "2026-05-17",
                "license": "test",
                "provenance_pointer": "test",
                "allowed_evidence_scope": "source-stated assertion only",
                "caveats": "canonicalization_status=unresolved; ambiguity_reason=no exact WFO accepted-name or synonym-cluster match",
                "inferred_flag": False,
                "raw_scientific_name": "Not A Real Plant",
                "accepted_taxon_key": "",
                "pending_crosswalk": True,
                "canonical_node_ids_json": json.dumps(["raw_name:not a real plant", "trait:test"]),
            }
        ]
    )
    assert validate_edges_df(row) == []


def test_tier0_count_excludes_synonym_nodes():
    nodes = pd.read_parquet(ROOT / "phytograph_dataset" / "nodes.parquet")
    accepted_taxa = nodes[nodes["node_type"].isin(["family", "genus", "species", "infraspecific_unit"])]
    synonyms = nodes[nodes["node_type"] == "synonym"]
    assert len(accepted_taxa) == 60000
    assert len(synonyms) == 113582
    assert validate_nodes_df(nodes) == []
