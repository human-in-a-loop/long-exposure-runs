# created: 2026-05-18T23:59:45+00:00
# cycle: 31
# run_id: run-phytograph-cycle31-fork-2f05eabe3800-postmerge-integration
# agent: worker
# milestone: _plan/fork-2f05eabe3800-postmerge-integration

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _read_tsv(path):
    with (ROOT / path).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def test_track2_free_tier_ghost_controls_remain_null_and_track_local():
    rows = _read_tsv("tracks/track2/data/track2_free_tier_ghost_evidence_controls.tsv")
    canonical = [row for row in rows if row["row_scope"] == "canonical_heldout"]
    local = [row for row in rows if row["row_scope"] == "local_candidate"]

    assert len(canonical) == 8
    assert len(local) == 31
    assert sum(row["accepted_key_before"] != "" for row in canonical) == 2
    assert {row["modern_failure_independent_free_tier_status"] for row in canonical} == {
        "not_found_beyond_seed_citation_local_only",
        "not_found_modern_failure_absent_local_only",
    }
    assert {row["non_singleton_source_support"] for row in canonical} == {"False"}
    assert sum(row["living_megafauna_exclusion_status"] == "passes_living_megafauna_exclusion" for row in canonical) == 7
    assert {row["passes_validation_contract"] for row in canonical} == {"False"}
    assert {row["enters_master_prediction_ledger"] for row in rows} == {"False"}
    assert {row["inferred_anachronism_claim"] for row in rows} == {"False"}


def test_track3_free_tier_trait_confound_matrix_remains_confound_limited():
    matrix = _read_tsv("tracks/track3/data/track3_free_tier_trait_taxon_matrix.tsv")
    readiness = _read_tsv("tracks/track3/data/track3_free_tier_trait_readiness.tsv")
    summary = json.loads(
        (ROOT / "tracks/track3/data/track3_free_tier_trait_confound_summary.json").read_text(
            encoding="utf-8"
        )
    )

    assert len(matrix) == 3069
    assert len(readiness) == 15
    assert summary["h3_decision"] == "confound_limited"
    assert summary["controlled_convergence_ready_traits"] == []
    assert summary["drupe_status"] == "data_limited_pending_prior"
    assert summary["capsule_status"] == "data_limited_pending_prior"
    assert {row["enters_master_prediction_ledger"] for row in readiness} == {"False"}
    assert [
        row["trait"]
        for row in readiness
        if row["controlled_readiness_status"] == "controlled_convergence_ready"
    ] == []


def test_integration_report_records_no_promotion_boundary():
    report = (ROOT / "reports/fork_2f05eabe3800_postmerge_integration.md").read_text(
        encoding="utf-8"
    )

    assert "H2_remains_not_supported_or_data_limited" in report
    assert "`confound_limited`" in report
    assert "No prediction or speculation row promoted." in report
    assert "not an audit decision" in report


def test_branch_figures_and_master_ledgers_are_stable():
    for path in (
        "tracks/track2/figures/track2_free_tier_ghost_control_matrix.png",
        "tracks/track3/figures/track3_free_tier_trait_confound_matrix.png",
    ):
        figure = ROOT / path
        assert figure.exists()
        assert figure.stat().st_size > 10_000

    for path in ("prediction_ledger.tsv", "speculation_ledger.tsv"):
        lines = (ROOT / path).read_text(encoding="utf-8").splitlines()
        assert len(lines) == 1
