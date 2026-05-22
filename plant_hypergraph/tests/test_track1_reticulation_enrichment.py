# created: 2026-05-18T00:35:00Z
# cycle: 8
# run_id: run-phytograph-cycle8-fork-56e44dff3ca4-clone0-track1-wave2
# agent: worker
# milestone: _plan/track1-wave2-enrichment-data-limited
"""Track 1 Wave 2 enrichment tests (A–F per brief)."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
T1_DATA = ROOT / "tracks" / "track1" / "data"
DATASET = ROOT / "phytograph_dataset"
STAGING = ROOT / "substrate" / "staging" / "reticulation_sources" / "normalized"

EXPECTED_EDGE_TYPES = {
    "chromosome_count_assertion",
    "ploidy_state_assertion",
    "hybridization_event",
    "polyploidization_event",
    "reticulate_inheritance_evidence",
}

CANONICAL_SEEDS = {
    "Triticum aestivum",
    "Brassica napus",
    "Spartina anglica",
    "Tragopogon mirus",
}

STAGED_FILE_BASENAMES = [
    "chromosome_count_assertions",
    "ploidy_state_assertions",
    "hybridization_events",
    "polyploidization_events",
    "reticulate_inheritance_evidence",
]


@pytest.fixture(scope="module")
def union() -> pd.DataFrame:
    return pd.read_parquet(T1_DATA / "reticulation_enrichment_edges.parquet")


@pytest.fixture(scope="module")
def seed_status() -> pd.DataFrame:
    return pd.read_csv(T1_DATA / "canonical_seed_case_status.tsv", sep="\t", keep_default_na=False)


def test_a_no_mixed_states(union: pd.DataFrame) -> None:
    """Every row: resolved (non-null key, pending=False) XOR pending (null key, pending=True)."""
    has_key = union["accepted_taxon_key"].astype(str).str.len().gt(0)
    pending = union["pending_crosswalk"].astype(bool)
    # resolved invariant: has_key implies not pending
    bad_resolved = union[has_key & pending]
    # pending invariant: not has_key implies pending
    bad_pending = union[~has_key & ~pending]
    assert len(bad_resolved) == 0, f"rows with key but pending=True: {bad_resolved}"
    assert len(bad_pending) == 0, f"rows without key but pending=False: {bad_pending}"


def test_b_allowed_evidence_scope_preserved(union: pd.DataFrame) -> None:
    """allowed_evidence_scope must appear verbatim from staging."""
    for basename in STAGED_FILE_BASENAMES:
        staged = pd.read_csv(STAGING / f"{basename}.tsv", sep="\t", keep_default_na=False)
        staged_scopes = set(staged["allowed_evidence_scope"].tolist())
        enriched_scopes = set(
            union.loc[union["source_file_basename"] == basename, "allowed_evidence_scope"].tolist()
        )
        assert staged_scopes == enriched_scopes, (
            f"{basename}: scope drift staged={staged_scopes} enriched={enriched_scopes}"
        )


def test_c_canonical_seed_status_explicit(seed_status: pd.DataFrame) -> None:
    """Each canonical seed taxon has a row with an explicit status in {resolved,pending_crosswalk,missing_from_staging}."""
    valid = {"resolved", "pending_crosswalk", "missing_from_staging"}
    seeds_in = set(seed_status["canonical_seed_taxon"].tolist())
    missing = CANONICAL_SEEDS - seeds_in
    assert not missing, f"canonical seeds absent from status table: {missing}"
    for seed in CANONICAL_SEEDS:
        row = seed_status[seed_status["canonical_seed_taxon"] == seed].iloc[0]
        assert row["status"] in valid, f"{seed} has invalid status {row['status']}"


def test_d_no_silent_drops(union: pd.DataFrame) -> None:
    """Total rows in union equals sum of staged rows (no silent drops; no explicit drops this cycle)."""
    staged_total = 0
    for basename in STAGED_FILE_BASENAMES:
        staged_total += len(pd.read_csv(STAGING / f"{basename}.tsv", sep="\t", keep_default_na=False))
    assert len(union) == staged_total, f"emitted={len(union)} != staged={staged_total}"


def test_e_accepted_keys_closed_under_crosswalk(union: pd.DataFrame) -> None:
    """No accepted_taxon_key in enrichment is missing from substrate's taxon_crosswalk."""
    crosswalk = pd.read_parquet(DATASET / "taxon_crosswalk.parquet")
    valid_keys = set(crosswalk["accepted_taxon_key"].astype(str).tolist())
    enriched_keys = set(
        union.loc[union["accepted_taxon_key"].astype(str).str.len().gt(0), "accepted_taxon_key"].tolist()
    )
    orphan = enriched_keys - valid_keys
    assert not orphan, f"accepted_taxon_keys not in substrate crosswalk: {orphan}"


def test_f_schema_clean(union: pd.DataFrame) -> None:
    """Exactly the five M1.3 edge types; no Track 3/5 leakage; no forbidden columns."""
    observed = set(union["edge_type"].tolist())
    assert observed == EXPECTED_EDGE_TYPES, f"edge_type drift: {observed}"
    forbidden_cols = {"tree_compatibility_index", "convergence_signature"}
    leaked = forbidden_cols & set(union.columns)
    assert not leaked, f"forbidden columns appeared: {leaked}"
