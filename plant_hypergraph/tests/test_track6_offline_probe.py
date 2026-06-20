import importlib.util
import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
BUILDER_PATH = ROOT / "scripts" / "build_track6_offline_probe.py"
SCORER_PATH = ROOT / "tracks" / "track6" / "scripts" / "score_offline_probe.py"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_question_bank_has_expected_offline_categories():
    builder = load_module(BUILDER_PATH, "track6_builder")
    bank = builder.build_question_bank(target_per_category=5)
    categories = set(bank["category"])
    assert {
        "synonym_confusion",
        "hybrid_pedigree",
        "region_conditional",
        "ghost_partner_reasoning",
        "convergence_detection",
        "phytochemistry_safety",
        "toxicity_lookalike_media_scope",
    } <= categories
    assert bank["offline_only"].all()
    assert not bank["source_edge_id"].isna().any()
    assert not bank["license"].isna().any()


def test_ground_truth_edges_are_schema_shaped_without_live_responses():
    builder = load_module(BUILDER_PATH, "track6_builder_edges")
    bank = builder.build_question_bank(target_per_category=3)
    edges = builder.build_edges(bank)
    assert set(edges["edge_type"]) == {"adversarial_probe_edge"}
    assert len(edges) == len(bank)
    for role_json in edges["role_map_json"].head(20):
        role = json.loads(role_json)
        assert role["foundation_model_response"] == ["foundation_model_response:offline_unrun"]
        assert role["scoring_rule"] == "track6_offline_required_forbidden_terms_v1"


def test_scorer_passes_scoped_answer_and_rejects_forbidden_claim():
    builder = load_module(BUILDER_PATH, "track6_builder_score_fixture")
    scorer = load_module(SCORER_PATH, "track6_scorer")
    bank = builder.build_question_bank(target_per_category=1)
    good_row = bank.iloc[0]
    bad_row = bank.iloc[1]
    good_required = json.loads(good_row.required_terms_json)
    bad_required = json.loads(bad_row.required_terms_json)
    bad_forbidden = json.loads(bad_row.forbidden_terms_json)[0]
    good_response = " ".join(good_required) + " with scoped evidence only"
    bad_response = " ".join(bad_required) + f" {bad_forbidden}"
    responses = pd.DataFrame(
        [
            {"question_id": good_row.question_id, "response_text": good_response},
            {"question_id": bad_row.question_id, "response_text": bad_response},
        ]
    )
    scored = scorer.score_responses(pd.DataFrame([good_row, bad_row]), responses)
    assert bool(scored.iloc[0]["passed"]) is True
    assert bool(scored.iloc[1]["passed"]) is False


def test_builder_source_does_not_import_provider_harness():
    text = BUILDER_PATH.read_text()
    forbidden = ["openai", "anthropic", "google.generativeai", "gemini_provider", "FMClient"]
    assert all(term not in text for term in forbidden)
