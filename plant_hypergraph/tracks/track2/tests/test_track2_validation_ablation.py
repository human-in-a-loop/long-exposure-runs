from pathlib import Path
import subprocess

import pandas as pd


ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "tracks" / "track2" / "data"
FIGURE = ROOT / "tracks" / "track2" / "figures" / "ghost_partner_ablation_sensitivity.png"
REPORT = ROOT / "tracks" / "track2" / "reports" / "track2_validation_and_ablation.md"
RECOVERY_SCRIPT = ROOT / "tracks" / "track2" / "scripts" / "track2_validation_recovery.py"
ABLATION_SCRIPT = ROOT / "tracks" / "track2" / "scripts" / "track2_ablation_checks.py"


def run_validation_layer():
    subprocess.run(["python3", str(RECOVERY_SCRIPT)], cwd=ROOT, check=True)
    subprocess.run(["python3", str(ABLATION_SCRIPT)], cwd=ROOT, check=True)


def test_heldout_recovery_classifies_all_canonical_cases():
    run_validation_layer()
    recovery = pd.read_csv(DATA / "janzen_martin_accepted_key_recovery.tsv", sep="\t").fillna("")
    assert len(recovery) == 8
    assert set(recovery["accepted_key_status"]).issubset(
        {
            "accepted_key_already_present",
            "accepted_key_recovered",
            "accepted_key_absent",
        }
    )
    assert {"data_limited", "insufficient_support", "validation_ready"}.issubset(
        set(recovery["validation_class"])
    )
    assert recovery["recovery_reason"].str.len().gt(0).all()


def test_modern_failure_queue_preserves_hypothesis_guardrails():
    run_validation_layer()
    queue = pd.read_csv(DATA / "modern_dispersal_failure_evidence_queue.tsv", sep="\t")
    assert len(queue) == 31
    assert set(queue["modern_failure_evidence_status"]).issubset(
        {"seed_modern_failure_present", "needs_independent_modern_failure_check"}
    )
    assert queue["evidence_queue_action"].str.len().gt(0).all()
    assert not queue["inferred_anachronism_claim"].astype(bool).any()
    assert not queue["enters_master_prediction_ledger"].astype(bool).any()


def test_ablation_results_expose_singleton_source_fragility():
    run_validation_layer()
    ablations = pd.read_csv(DATA / "ghost_partner_ablation_results.tsv", sep="\t")
    singleton = ablations[ablations["ablation"].eq("remove_singleton_source_rows")].iloc[0]
    no_failure = ablations[ablations["ablation"].eq("remove_modern_failure_component")].iloc[0]
    assert singleton["candidate_rows"] == 0
    assert singleton["heldout_validation_ready"] == 0
    assert no_failure["pending_validation_count"] == 0
    assert FIGURE.exists()
    assert FIGURE.stat().st_size > 1000


def test_report_distinguishes_validation_and_ablation_statuses():
    run_validation_layer()
    validation = pd.read_csv(DATA / "ghost_partner_validation_scores.tsv", sep="\t").fillna("")
    assert "ablation_outcome" in validation.columns
    assert "falsified_by_ablation" in set(validation["ablation_outcome"])
    text = REPORT.read_text()
    assert "No held-out case is validated by this branch" in text
    assert "falsified_by_ablation" in text
    assert "prediction_ledger.tsv" in text
