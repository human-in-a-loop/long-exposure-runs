# created: 2026-05-18T23:55:00+00:00
# cycle: 31
# run_id: fork-2f05eabe3800-clone-0-track2-free-tier-ghost-controls
# agent: worker-clone-0
# milestone: M4.V2

from pathlib import Path
import subprocess

import pandas as pd


ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "tracks" / "track2" / "data"
REPORT = ROOT / "tracks" / "track2" / "reports" / "track2_free_tier_ghost_evidence_controls.md"
FIGURE = ROOT / "tracks" / "track2" / "figures" / "track2_free_tier_ghost_control_matrix.png"
SCRIPT = ROOT / "tracks" / "track2" / "scripts" / "track2_free_tier_ghost_evidence_controls.py"
PLOT = ROOT / "tracks" / "track2" / "scripts" / "plot_track2_free_tier_ghost_evidence_controls.py"


def run_sidecar():
    subprocess.run(["python3", str(SCRIPT)], cwd=ROOT, check=True)
    subprocess.run(
        [
            "figure",
            "plot",
            str(PLOT),
            "--out",
            str(FIGURE),
        ],
        cwd=ROOT,
        check=True,
    )


def test_free_tier_matrix_preserves_required_rows_and_columns():
    run_sidecar()
    matrix = pd.read_csv(DATA / "track2_free_tier_ghost_evidence_controls.tsv", sep="\t")
    assert len(matrix[matrix["row_scope"].eq("canonical_heldout")]) == 8
    assert len(matrix[matrix["row_scope"].eq("local_candidate")]) == 31
    assert list(matrix.columns) == [
        "row_scope",
        "heldout_scientific_name",
        "candidate_id",
        "raw_scientific_name",
        "candidate_class",
        "best_rank",
        "accepted_key_before",
        "accepted_key_after_free_tier_recovery",
        "accepted_key_status",
        "modern_failure_seed_status",
        "modern_failure_independent_free_tier_status",
        "source_groups",
        "source_class_count",
        "non_singleton_source_support",
        "living_megafauna_exclusion_status",
        "passes_validation_contract",
        "final_status",
        "rejection_reason",
        "enters_master_prediction_ledger",
        "inferred_anachronism_claim",
    ]


def test_free_tier_controls_keep_h2_unsupported():
    run_sidecar()
    matrix = pd.read_csv(DATA / "track2_free_tier_ghost_evidence_controls.tsv", sep="\t")
    canonical = matrix[matrix["row_scope"].eq("canonical_heldout")]
    assert not matrix["passes_validation_contract"].astype(bool).any()
    assert canonical["accepted_key_after_free_tier_recovery"].fillna("").ne("").sum() == 2
    assert canonical["modern_failure_independent_free_tier_status"].str.startswith("not_found").all()
    assert not canonical["non_singleton_source_support"].astype(bool).any()
    assert canonical["rejection_reason"].fillna("").ne("").all()
    assert "accepted_key_absent" in "|".join(canonical["rejection_reason"].astype(str))


def test_free_tier_sidecar_does_not_promote_claims_or_master_ledgers():
    run_sidecar()
    matrix = pd.read_csv(DATA / "track2_free_tier_ghost_evidence_controls.tsv", sep="\t")
    assert not matrix["inferred_anachronism_claim"].astype(bool).any()
    assert not matrix["enters_master_prediction_ledger"].astype(bool).any()
    for name in ["prediction_ledger.tsv", "speculation_ledger.tsv"]:
        lines = [line for line in (ROOT / name).read_text().splitlines() if line.strip()]
        assert len(lines) == 1


def test_free_tier_report_and_figure_are_audit_ready():
    run_sidecar()
    text = REPORT.read_text()
    assert "Decision: `H2_remains_not_supported_or_data_limited`" in text
    assert "Accepted-key recovery did not improve for absent held-outs" in text
    assert "No row gains independent modern dispersal-failure evidence" in text
    assert "does not write `prediction_ledger.tsv` or `speculation_ledger.tsv`" in text
    assert FIGURE.exists()
    assert FIGURE.stat().st_size > 1000
