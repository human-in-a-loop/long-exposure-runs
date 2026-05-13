# created: 2026-05-13T18:38:00Z
# cycle: 8
# run_id: run-2026-05-13T015136Z
# agent: worker
# milestone: M-DEFER-1
"""Direct tests for M-DEFER-1 campaign deferral watchlist."""

from __future__ import annotations

import csv
import importlib.util
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "physicalized-weights" / "scripts" / "build_campaign_deferral_watchlist.py"
DATA_DIR = ROOT / "physicalized-weights" / "data"

spec = importlib.util.spec_from_file_location("build_campaign_deferral_watchlist", SCRIPT)
watch = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules[spec.name] = watch
spec.loader.exec_module(watch)


def rows() -> list[dict[str, str]]:
    watch.main()
    with (DATA_DIR / "campaign_deferral_watchlist_results.csv").open(newline="") as f:
        return list(csv.DictReader(f))


def summary() -> dict[str, object]:
    watch.main()
    return json.loads((DATA_DIR / "campaign_deferral_watchlist_summary.json").read_text())


def row_by_id(trigger_id: str) -> dict[str, str]:
    return {row["trigger_id"]: row for row in rows()}[trigger_id]


def test_current_disposition_has_no_active_superiority_claim() -> None:
    data = summary()
    assert data["current_superiority_claim_count"] == 0
    assert data["current_artifacts_reopen"] is False
    dispositions = {item["claim_id"]: item["disposition"] for item in data["claim_dispositions"]}
    assert dispositions["safety_filter_performance_or_economic_winner"] == "falsified_under_stronger_programmable_baseline"
    assert dispositions["non_safety_target_classes_current_superiority"] == "no_calibrated_current_superiority_claim"


def test_synthetic_proxy_template_vendor_only_are_insufficient() -> None:
    blocked = [
        "vendor_benchmark_only",
        "synthetic_counterfactual_only",
        "local_proxy_only",
        "template_or_dryrun_only",
    ]
    for trigger_id in blocked:
        row = row_by_id(trigger_id)
        assert row["classification"] == "insufficient_substitute"
        assert row["action_scope"] == "no_reopen"


def test_measured_package_triggers_require_lifecycle_and_uncertainty() -> None:
    measured = [
        row_by_id("measured_shadow_or_canary_package"),
        row_by_id("measured_production_package"),
        row_by_id("new_stable_high-volume_target_evidence"),
    ]
    assert all(row["classification"] == "inactive_reopen_trigger" for row in measured)
    assert all(row["requires_phase4_lifecycle"] == "True" for row in measured)
    assert all(row["requires_uncertainty_durability"] == "True" for row in measured)


def test_hdl_toolchain_triggers_are_prototype_only() -> None:
    for trigger_id in ["compiled_verilator_available", "hdl_design_scope_change"]:
        row = row_by_id(trigger_id)
        assert row["classification"] == "prototype_verification_trigger"
        assert row["action_scope"] == "prototype_verification_only"
        assert row["can_activate_current_superiority_claim"] == "False"


def test_summary_adds_no_gate_and_no_current_claim() -> None:
    data = summary()
    assert data["new_reopen_gate_count"] == 0
    assert data["current_superiority_claim_count"] == 0
    assert data["phase4_future_reopen_condition_unchanged"] is True
    assert data["measured_triggers_require_lifecycle_and_uncertainty"] is True
    assert data["prototype_triggers_reopen_performance_claim"] is False


def test_every_trigger_has_owner_and_action() -> None:
    for row in rows():
        assert row["owning_prior_milestone"]
        assert row["action_if_observed"]
    assert summary()["all_triggers_have_owner_and_action"] is True


def test_png_exists_and_is_nontrivial() -> None:
    watch.main()
    png = DATA_DIR / "campaign_deferral_watchlist.png"
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
