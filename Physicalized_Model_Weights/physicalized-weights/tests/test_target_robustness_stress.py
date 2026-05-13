# created: 2026-05-13T17:34:00Z
# cycle: 7
# run_id: run-2026-05-13T015136Z
# agent: worker
# milestone: M-ROBUST-1
"""Direct tests for M-ROBUST-1 target robustness stress model."""

from __future__ import annotations

import csv
import importlib.util
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "physicalized-weights" / "scripts" / "target_robustness_stress.py"
DATA_DIR = ROOT / "physicalized-weights" / "data"

spec = importlib.util.spec_from_file_location("target_robustness_stress", SCRIPT)
robust = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules[spec.name] = robust
spec.loader.exec_module(robust)


def rows() -> list[dict[str, str]]:
    robust.main()
    with (DATA_DIR / "target_robustness_results.csv").open(newline="") as f:
        return list(csv.DictReader(f))


def row_by_id(case_id: str) -> dict[str, str]:
    return {row["case_id"]: row for row in rows()}[case_id]


def summary() -> dict[str, object]:
    robust.main()
    return json.loads((DATA_DIR / "target_robustness_summary.json").read_text())


def test_high_update_targets_cannot_win_under_calibrated_settings() -> None:
    tenant = row_by_id("tenant_adapter_or_lora__calibrated")
    training = row_by_id("training_optimizer_state__calibrated")
    assert tenant["best_winning_strategy"] != "physicalized_target"
    assert training["best_winning_strategy"] != "physicalized_target"
    assert tenant["blocker_class"] in {"anti_target_mechanism", "high_update_cadence"}


def test_zero_volume_cases_cannot_win() -> None:
    control = row_by_id("zero_volume_control")
    assert control["label"] == "zero_volume_blocked"
    assert control["best_winning_strategy"] != "physicalized_target"


def test_all_fallback_cases_cannot_win() -> None:
    control = row_by_id("all_fallback_control")
    assert control["label"] == "all_fallback_blocked"
    assert control["best_winning_strategy"] != "physicalized_target"


def test_high_software_savings_weakens_physicalized_wins() -> None:
    control = row_by_id("high_software_savings_control")
    assert control["label"] == "best_programmable_baseline"
    assert control["blocker_class"] == "software_savings_compress_margin"
    assert float(control["margin_vs_best_programmable"]) > 0


def test_antitargets_remain_antitargets_under_plausible_assumptions() -> None:
    anti_targets = {
        "decoder_dense_weights",
        "attention_kv_or_dynamic_context",
        "tenant_adapter_or_lora",
        "training_optimizer_state",
    }
    plausible = [r for r in rows() if r["regime"] == "favorable_plausible" and r["target_class"] in anti_targets]
    assert plausible
    assert all(r["best_winning_strategy"] != "physicalized_target" for r in plausible)
    assert all(float(r["margin_vs_best_programmable"]) > 0 for r in plausible)


def test_extreme_counterfactual_wins_are_labeled_noncurrent() -> None:
    wins = [r for r in rows() if r["label"] == "counterfactual_not_current_evidence"]
    assert wins
    assert all(r["current_measured_evidence"] == "False" for r in wins)
    assert all(r["current_superiority_claim"] == "False" for r in wins)


def test_summary_has_no_current_superiority_claim() -> None:
    data = summary()
    assert data["target_count"] >= 8
    assert data["calibrated_physicalized_win_count"] == 0
    assert data["anti_target_plausible_win_count"] == 0
    assert data["current_superiority_claim_count"] == 0
    assert data["current_artifacts_reopen"] is False
    assert data["status_mismatches"] == []


def test_frontier_fields_and_png_exist() -> None:
    sample = row_by_id("small_keyword_or_policy_classifier__favorable_plausible")
    assert sample["minimum_physicalized_savings_to_tie"] != "no_finite_tie"
    assert sample["maximum_allowable_update_frequency_per_day"] != "no_finite_tie"
    assert sample["minimum_utilization_needed"] != "no_finite_tie"
    png = DATA_DIR / "target_robustness_frontier.png"
    assert png.exists()
    assert png.read_bytes().startswith(b"\x89PNG")
    assert png.stat().st_size > 1000


def run() -> None:
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"PASS {name}")


if __name__ == "__main__":
    run()
