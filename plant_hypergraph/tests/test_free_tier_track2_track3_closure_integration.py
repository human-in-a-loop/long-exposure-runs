#!/usr/bin/env python3
# created: 2026-05-18T23:59:58+00:00
# cycle: 32
# run_id: run-phytograph-cycle32-free-tier-track2-track3-closure-integration
# agent: worker
# milestone: _plan/free-tier-track2-track3-closure-integration

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STATUS = ROOT / "data/reopen/reopen_closure_status.tsv"
CLOSURE_REPORT = ROOT / "reports/reopen/free_tier_track2_track3_closure_integration.md"
RECOVERY_REPORT = ROOT / "reports/reopen/free_tier_recovery_integration.md"
ROOT_DOCS = [
    ROOT / "final_report.md",
    ROOT / "audit_report.md",
    ROOT / "research_contribution_ledger.md",
    ROOT / "falsification_and_ablation_report.md",
    ROOT / "artifact_index.md",
]


def _read_tsv(path):
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def test_track2_track3_status_table_rows_preserve_non_promotion():
    rows = _read_tsv(STATUS)
    by_track = {row["track"]: row for row in rows}

    assert by_track["Track 2"]["result"] == "H2_remains_not_supported_or_data_limited"
    assert "0/8 canonical held-outs pass the validation contract" in by_track["Track 2"][
        "quantitative_blocker"
    ]
    assert "accepted-key modern-failure evidence" in by_track["Track 2"][
        "allowed_future_reopen_evidence"
    ]
    assert "source-class-independent held-out recovery" in by_track["Track 2"][
        "allowed_future_reopen_evidence"
    ]

    assert by_track["Track 3"]["result"] == "confound_limited"
    assert "3069 accepted-key trait carrier rows" in by_track["Track 3"][
        "quantitative_blocker"
    ]
    assert "0 traits are controlled_convergence_ready" in by_track["Track 3"][
        "quantitative_blocker"
    ]
    assert "phylogenetically separated carrier sets" in by_track["Track 3"][
        "allowed_future_reopen_evidence"
    ]

    assert by_track["Track 2"]["master_ledger_action"] == (
        "no_master_prediction_or_speculation_row; validated_non_promotion"
    )
    assert by_track["Track 3"]["master_ledger_action"] == (
        "no_master_prediction_or_speculation_row; validated_non_promotion"
    )


def test_closure_report_carries_branch_counts_and_claim_boundaries():
    text = CLOSURE_REPORT.read_text(encoding="utf-8")
    assert "8 canonical held-outs and 31 local candidates" in text
    assert "0/8 validation-contract pass" in text
    assert "3,069 accepted-key" in text
    assert "0 controlled-ready traits" in text
    assert "does not establish a new anachronism" in text
    assert "does not establish a convergence or adaptive-origin claim" in text
    assert "No master prediction or speculation row" in text


def test_root_reports_and_recovery_integration_reference_track2_track3_closure():
    required = [
        "H2_remains_not_supported_or_data_limited",
        "0/8 canonical held-outs",
        "confound_limited",
        "0 controlled-ready traits",
    ]
    for path in [RECOVERY_REPORT, *ROOT_DOCS]:
        text = path.read_text(encoding="utf-8")
        for phrase in required:
            assert phrase in text, f"{phrase!r} missing from {path}"


def test_branch_outputs_still_match_integrated_counts():
    track2 = _read_tsv(ROOT / "tracks/track2/data/track2_free_tier_ghost_evidence_controls.tsv")
    canonical = [row for row in track2 if row["row_scope"] == "canonical_heldout"]
    assert len(canonical) == 8
    assert sum(row["passes_validation_contract"] == "True" for row in canonical) == 0
    assert {row["inferred_anachronism_claim"] for row in track2} == {"False"}

    summary = json.loads(
        (ROOT / "tracks/track3/data/track3_free_tier_trait_confound_summary.json").read_text(
            encoding="utf-8"
        )
    )
    assert summary["matrix_rows"] == 3069
    assert summary["h3_decision"] == "confound_limited"
    assert summary["controlled_convergence_ready_traits"] == []


def test_figures_and_master_ledgers_remain_stable():
    for path in (
        ROOT / "tracks/track2/figures/track2_free_tier_ghost_control_matrix.png",
        ROOT / "tracks/track3/figures/track3_free_tier_trait_confound_matrix.png",
    ):
        assert path.exists()
        assert path.stat().st_size > 10_000

    for path in (ROOT / "prediction_ledger.tsv", ROOT / "speculation_ledger.tsv"):
        assert len(path.read_text(encoding="utf-8").splitlines()) == 1
