from pathlib import Path
import subprocess

import pandas as pd


ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "tracks" / "track2" / "data"
FIGURE = ROOT / "tracks" / "track2" / "figures" / "track2_wave4_validation_ablation.png"
REPORT = ROOT / "tracks" / "track2" / "reports" / "track2_wave4_validation_closure.md"
SCRIPT = ROOT / "tracks" / "track2" / "scripts" / "track2_wave4_validation_closure.py"


def run_closure():
    subprocess.run(["python3", str(ROOT / "tracks" / "track2" / "scripts" / "track2_validation_recovery.py")], cwd=ROOT, check=True)
    subprocess.run(["python3", str(ROOT / "tracks" / "track2" / "scripts" / "track2_ablation_checks.py")], cwd=ROOT, check=True)
    subprocess.run(["python3", str(SCRIPT)], cwd=ROOT, check=True)


def test_closure_classifies_all_heldout_cases_without_validation_claims():
    run_closure()
    outcomes = pd.read_csv(DATA / "track2_wave4_validation_outcomes.tsv", sep="\t")
    assert len(outcomes) == 8
    assert outcomes["wave4_outcome_status"].eq("validated").sum() == 0
    assert set(outcomes["wave4_outcome_status"]) == {"data_limited", "insufficient_support", "falsified"}
    assert not outcomes["inferred_anachronism_claim"].astype(bool).any()
    assert not outcomes["enters_master_prediction_ledger"].astype(bool).any()


def test_closure_preserves_expected_null_and_data_limited_profile():
    run_closure()
    outcomes = pd.read_csv(DATA / "track2_wave4_validation_outcomes.tsv", sep="\t")
    counts = outcomes["wave4_outcome_status"].value_counts().to_dict()
    assert counts["data_limited"] == 6
    assert counts["insufficient_support"] == 1
    assert counts["falsified"] == 1
    asimina = outcomes[outcomes["heldout_scientific_name"].eq("Asimina triloba")].iloc[0]
    assert asimina["wave4_outcome_status"] == "falsified"
    assert "ablation_fragile" in asimina["blocking_controls"]


def test_closure_ablation_controls_remove_validation_ready_status():
    run_closure()
    ablations = pd.read_csv(DATA / "ghost_partner_ablation_results.tsv", sep="\t")
    singleton = ablations[ablations["ablation"].eq("remove_singleton_source_rows")].iloc[0]
    normalized = ablations[ablations["ablation"].eq("source_count_candidate_class_normalized")].iloc[0]
    no_modern = ablations[ablations["ablation"].eq("remove_modern_failure_component")].iloc[0]
    assert singleton["candidate_rows"] == 0
    assert singleton["heldout_validation_ready"] == 0
    assert normalized["heldout_validation_ready"] == 0
    assert no_modern["pending_validation_count"] == 0


def test_closure_report_and_figure_are_audit_ready():
    run_closure()
    text = REPORT.read_text()
    assert "No held-out Janzen-Martin case is validated" in text
    assert "H2 is not supported at the requested 30% canonical recovery threshold" in text
    assert "prediction_ledger.tsv" in text
    assert "A `falsified` outcome here means falsified as a Wave 4 validation-ready" in text
    assert FIGURE.exists()
    assert FIGURE.stat().st_size > 1000


def test_master_ledgers_remain_header_only():
    run_closure()
    for name in ["prediction_ledger.tsv", "speculation_ledger.tsv"]:
        lines = [line for line in (ROOT / name).read_text().splitlines() if line.strip()]
        assert len(lines) == 1
