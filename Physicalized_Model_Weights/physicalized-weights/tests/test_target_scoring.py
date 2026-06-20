# created: 2026-05-13T02:28:00Z
# cycle: 1
# run_id: run-2026-05-13T015136Z
# agent: worker
# milestone: M-TARGET-1

from __future__ import annotations

import csv
import importlib.util
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = ROOT / "physicalized-weights" / "scripts" / "target_scoring.py"
spec = importlib.util.spec_from_file_location("target_scoring", SCRIPT_PATH)
scoring = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules["target_scoring"] = scoring
spec.loader.exec_module(scoring)


def test_minimum_candidate_and_antitarget_counts_present() -> None:
    rows, _ = scoring.score_components()
    assert sum(1 for row in rows if row.category == "candidate") >= 8
    assert sum(1 for row in rows if row.category == "anti-target") >= 4


def test_full_frontier_llm_fixed_dense_weights_not_top_target() -> None:
    rows, _ = scoring.score_components()
    frontier = next(row for row in rows if row.component_id == "frontier_dense")
    top = next(row for row in rows if row.rank == 1)
    assert top.component_id != "frontier_dense"
    assert frontier.category == "anti-target"
    assert frontier.rank > 8


def test_stronger_software_savings_do_not_improve_viability() -> None:
    base_rows, _ = scoring.score_components(software_memory_savings=0.0)
    strong_rows, _ = scoring.score_components(software_memory_savings=0.5)
    base = {row.component_id: row.total_score for row in base_rows}
    strong = {row.component_id: row.total_score for row in strong_rows}
    assert set(base) == set(strong)
    assert all(strong[key] <= base[key] for key in base)


def test_zero_reuse_or_near_zero_update_interval_caps_score() -> None:
    original = scoring.components
    zero_reuse = scoring.Component(
        "zero_reuse_probe",
        "Zero reuse probe",
        "candidate",
        "modeled",
        90,
        0.0,
        5.0,
        5.0,
        5.0,
        5.0,
        5.0,
        5.0,
        "probe",
        "probe",
        "probe",
    )
    near_zero_update = scoring.Component(
        "near_zero_update_probe",
        "Near-zero update probe",
        "candidate",
        "modeled",
        0.1,
        5.0,
        5.0,
        5.0,
        5.0,
        5.0,
        5.0,
        5.0,
        "probe",
        "probe",
        "probe",
    )
    scoring.components = lambda: original() + [zero_reuse, near_zero_update]
    try:
        rows, _ = scoring.score_components()
    finally:
        scoring.components = original
    assert next(row for row in rows if row.component_id == "zero_reuse_probe").total_score <= 1.9
    assert next(row for row in rows if row.component_id == "near_zero_update_probe").total_score <= 1.9


def test_csv_and_json_schemas_stable(tmp_path: Path) -> None:
    rows, calibration = scoring.score_components()
    csv_path = tmp_path / "target_scores.csv"
    json_path = tmp_path / "target_scores_summary.json"
    scoring.write_csv(rows, csv_path)
    scoring.write_summary(rows, calibration, json_path, software_memory_savings=0.35)

    with csv_path.open(newline="") as f:
        reader = csv.DictReader(f)
        assert reader.fieldnames == [
            "rank",
            "component_id",
            "name",
            "category",
            "evidence_level",
            "update_interval_days",
            "reuse_volume",
            "update_stability",
            "approximation_tolerance",
            "integration_complexity",
            "energy_upside_vs_baseline",
            "software_baseline_resistance",
            "evidence_quality",
            "total_score",
            "baseline_penalty",
            "recommended_next_target",
            "baseline_comparison",
            "rationale",
            "falsifier",
        ]
        first = next(reader)
        assert first["component_id"]
        assert first["category"] in {"candidate", "anti-target"}

    summary = json.loads(json_path.read_text())
    assert summary["schema_version"] == 1
    assert summary["candidate_count"] >= 8
    assert summary["anti_target_count"] >= 4
    assert summary["recommended_next_target"]["category"] == "candidate"
    assert summary["axes"] == list(scoring.AXES)
