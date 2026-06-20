from pathlib import Path
import subprocess

import pandas as pd


ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "tracks" / "track2" / "data"
FIGURE = ROOT / "tracks" / "track2" / "figures" / "ghost_candidate_score_components.png"
REPORT = ROOT / "tracks" / "track2" / "reports" / "track2_ghost_hyperedges.md"
SCRIPT = ROOT / "scripts" / "track2_ghost_partner_ranker.py"


def run_ranker():
    subprocess.run(["python3", str(SCRIPT)], cwd=ROOT, check=True)


def test_ranker_outputs_candidate_scores_and_no_anachronism_truth_field():
    run_ranker()
    scores = pd.read_csv(DATA / "ghost_partner_candidate_scores.tsv", sep="\t")
    assert len(scores) == 31
    assert "is_anachronistic" not in scores.columns
    assert not scores["inferred_anachronism_claim"].astype(bool).any()
    assert not scores["enters_prediction_ledger"].astype(bool).any()
    assert set(scores["candidate_status"]).issubset(
        {
            "candidate_pending_validation",
            "data_limited",
            "insufficient_support",
            "excluded_schema_scope",
        }
    )
    assert REPORT.exists()
    report_text = REPORT.read_text().lower()
    assert "not claim" in report_text
    assert "established anachronism" in report_text


def test_track_local_prediction_tsv_has_validation_targets_and_caveats():
    run_ranker()
    predictions = pd.read_csv(DATA / "ghost_partner_predictions.tsv", sep="\t")
    assert len(predictions) == 31
    assert predictions["prediction_id"].str.startswith("T2-GHOST-").all()
    assert predictions["prediction_statement"].str.contains("Hypothesis for validation").all()
    assert predictions["hypothesis_caveat"].str.contains("not established anachronism").all()
    assert predictions["expected_validation_source"].str.len().gt(0).all()
    assert not predictions["inferred_anachronism_claim"].astype(bool).any()
    assert not predictions["enters_master_prediction_ledger"].astype(bool).any()
    assert set(predictions["status"]).issubset({"pending", "data_limited", "superseded"})


def test_master_prediction_ledger_remains_empty_during_track2_ranker():
    run_ranker()
    master = pd.read_csv(ROOT / "prediction_ledger.tsv", sep="\t")
    assert len(master) == 0


def test_positive_seed_candidate_has_component_support():
    run_ranker()
    scores = pd.read_csv(DATA / "ghost_partner_candidate_scores.tsv", sep="\t")
    row = scores[scores["raw_scientific_name"].eq("Asimina triloba")].iloc[0]
    assert row["morphology_support"] > 0
    assert row["extinct_partner_support"] > 0
    assert row["modern_failure_support"] > 0
    assert row["spatiotemporal_compatibility"] > 0
    assert row["candidate_status"] == "candidate_pending_validation"


def test_missing_accepted_key_is_data_limited_not_prediction():
    run_ranker()
    scores = pd.read_csv(DATA / "ghost_partner_candidate_scores.tsv", sep="\t")
    missing_key = scores[scores["accepted_taxon_key"].fillna("").eq("")]
    assert len(missing_key) >= 20
    assert set(missing_key["candidate_status"]).issubset(
        {"data_limited", "insufficient_support"}
    )


def test_large_fruit_without_failure_signal_stays_low_support():
    run_ranker()
    scores = pd.read_csv(DATA / "ghost_partner_candidate_scores.tsv", sep="\t")
    row = scores[scores["raw_scientific_name"].eq("Annona cherimola")].iloc[0]
    assert row["morphology_support"] > 0
    assert row["modern_failure_support"] == 0
    assert row["candidate_score"] <= 0.55
    assert row["candidate_status"] == "insufficient_support"


def test_living_megafauna_compatible_cases_are_flagged_and_figure_nonblank():
    run_ranker()
    scores = pd.read_csv(DATA / "ghost_partner_candidate_scores.tsv", sep="\t")
    ambiguous = scores[scores["penalty_living_megafauna_ambiguous"] > 0]
    assert len(ambiguous) > 0
    assert ambiguous["ambiguity_flag"].str.contains("living_megafauna").all()
    bison = scores[scores["extinct_fauna_node_id"].str.contains("Bison_latifrons")]
    assert not bison.empty
    assert bison["penalty_living_megafauna_ambiguous"].eq(1.0).all()
    extinct_only = scores[
        scores["extinct_fauna_node_id"].str.contains("Mammut|Cuvieronius|Notiomastodon")
    ]
    assert not extinct_only.empty
    assert extinct_only["penalty_living_megafauna_ambiguous"].eq(0.0).all()
    assert FIGURE.exists()
    assert FIGURE.stat().st_size > 1000


def test_janzen_martin_heldout_recovery_scaffold_is_not_validation_result():
    run_ranker()
    heldout = pd.read_csv(DATA / "janzen_martin_heldout_recovery_scaffold.tsv", sep="\t")
    assert len(heldout) == 8
    assert "Persea americana" in set(heldout["heldout_scientific_name"])
    assert "Maclura pomifera" in set(heldout["heldout_scientific_name"])
    assert heldout["validation_use"].str.contains("do not train").all()
    assert set(heldout["recovery_bucket"]).issubset(
        {
            "recovered_validation_ready_seed",
            "recovered_but_data_limited",
            "recovered_but_insufficient_support",
            "not_recovered_in_seed_layer",
        }
    )
