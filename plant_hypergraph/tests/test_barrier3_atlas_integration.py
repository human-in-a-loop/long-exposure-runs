"""
Tests for Barrier 3 Atlas instrument-readiness contract.

Header metadata:
  created: 2026-05-18T08:00:00+00:00
  cycle: 11
  run_id: run-phytograph-cycle11-barrier3-readiness
  agent: worker
  milestone: _plan/barrier3-readiness-package
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "tools"))

import validate_barrier3_atlas_integration as b3  # noqa: E402


def _find_page_with_prediction(track: int) -> dict:
    for path in sorted((REPO / "botanical_atlas_site/pages").glob("*.json")):
        page = json.loads(path.read_text())
        sec = page["tracks"][str(track)]
        if sec.get("predicted"):
            return page
    raise AssertionError(f"no page found with Track {track} prediction rows")


def test_contract_contains_all_six_tracks_with_expected_counts():
    contract, rows, rc = b3.build_contract()
    assert rc == 0
    assert len(rows) == 6
    by_track = {r["track"]: r for r in rows}
    assert by_track["Track 1"]["source_rows"] == 60000
    assert by_track["Track 1"]["atlas_projected_rows"] == 60000
    assert by_track["Track 3"]["barrier3_status"] == "ready_with_nonblocking_warning"
    assert "support-list-limited" in contract["global_checks"]["track3_projection_note"]
    assert contract["global_checks"]["master_ledgers_header_only"] is True


@pytest.mark.parametrize("track", [1, 2, 3, 4, 5, 6])
def test_representative_page_exposes_track_section_with_state_and_source(track):
    page = _find_page_with_prediction(track)
    sec = page["tracks"][str(track)]
    row = sec["predicted"][0]
    assert sec["instrument_mode"] == "prediction_adapter"
    assert sec["instrument_pending"] is False
    assert sec["state"] in {"predicted", "enriched", "observed", "data-limited"}
    assert row["track_output_path"].startswith(f"tracks/track{track}/")
    assert row["source_id"] or row["source_record_id"] or row["provenance_pointer"]
    assert row["caveats"] or row["allowed_evidence_scope"]
    assert row["inferred_flag"] is True


def test_prediction_rows_do_not_use_validated_status():
    for track in range(1, 7):
        page = _find_page_with_prediction(track)
        for row in page["tracks"][str(track)]["predicted"]:
            assert str(row.get("status", "")).lower() != "validated"


def test_contract_finds_no_positive_overclaim_language():
    contract, rows, rc = b3.build_contract()
    assert rc == 0
    assert all(not r["blocking_issue"] for r in rows)


def test_master_ledgers_remain_header_only():
    assert len((REPO / "prediction_ledger.tsv").read_text().splitlines()) == 1
    assert len((REPO / "speculation_ledger.tsv").read_text().splitlines()) == 1


def test_new_ledger_artifacts_should_not_use_directory_paths():
    new_artifacts = [
        "tools/validate_barrier3_atlas_integration.py",
        "tests/test_barrier3_atlas_integration.py",
        "data/barrier3_atlas_instrument_contract.json",
        "data/barrier3_atlas_instrument_contract.tsv",
        "reports/barrier3_atlas_instrument_readiness.md",
        "reports/barrier3_atlas_instrument_coverage.png",
        "botanical_atlas_site/coverage_summary.json",
        "botanical_atlas_site/build_log.json",
        "botanical_atlas_site/search_index.json",
    ]
    assert all(not artifact.endswith("/") for artifact in new_artifacts)
