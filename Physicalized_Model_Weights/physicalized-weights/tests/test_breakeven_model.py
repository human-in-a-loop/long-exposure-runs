# created: 2026-05-13T02:07:00Z
# cycle: 1
# run_id: run-2026-05-13T015136Z
# agent: worker
# milestone: M-MODEL-1

from __future__ import annotations

import csv
import importlib.util
import json
import math
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MODEL_PATH = ROOT / "physicalized-weights" / "scripts" / "breakeven_model.py"
spec = importlib.util.spec_from_file_location("breakeven_model", MODEL_PATH)
model = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules["breakeven_model"] = model
spec.loader.exec_module(model)


def test_zero_volume_never_favors_fixed_physicalization_with_nonzero_fixed_cost() -> None:
    rows = model.evaluate(model.Inputs(requests_per_day=0, update_interval_days=90, fixed_substrate_cost=1000))
    win = model.winner(rows)
    assert win.strategy in {"programmable_unoptimized", "software_optimized"}
    fixed_rows = [r for r in rows if r.strategy in {"fixed_digital_weights", "analog_in_memory", "hybrid_physicalized_submodel"}]
    assert all(math.isinf(r.total_normalized_cost) for r in fixed_rows)


def test_frequent_updates_penalize_fixed_physicalization() -> None:
    frequent = model.winner(model.evaluate(model.Inputs(requests_per_day=1_000_000, update_interval_days=1)))
    slow = model.winner(model.evaluate(model.Inputs(requests_per_day=1_000_000, update_interval_days=365)))
    assert frequent.strategy != "fixed_digital_weights"
    assert slow.total_normalized_cost < frequent.total_normalized_cost


def test_software_savings_shift_physicalization_breakeven_upward() -> None:
    base = model.Inputs(update_interval_days=90, software_memory_savings=0.0)
    improved = model.Inputs(update_interval_days=90, software_memory_savings=0.5)
    base_rows = model.evaluate(base)
    improved_rows = model.evaluate(improved)

    base_sw = next(r for r in base_rows if r.strategy == "software_optimized")
    base_fixed = next(r for r in base_rows if r.strategy == "fixed_digital_weights")
    improved_sw = next(r for r in improved_rows if r.strategy == "software_optimized")
    improved_fixed = next(r for r in improved_rows if r.strategy == "fixed_digital_weights")

    base_be = model.breakeven_requests(base_sw.per_request_cost, base_fixed.per_request_cost, model.fixed_cost("fixed_digital_weights", base))
    improved_be = model.breakeven_requests(improved_sw.per_request_cost, improved_fixed.per_request_cost, model.fixed_cost("fixed_digital_weights", improved))
    assert base_be is not None
    assert improved_be is not None
    assert improved_be > base_be


def test_zero_fixed_cost_improves_physicalized_but_analog_can_still_lose() -> None:
    costly = model.Inputs(requests_per_day=1_000_000, update_interval_days=365, fixed_substrate_cost=350_000)
    free_but_bad_analog = model.Inputs(
        requests_per_day=1_000_000,
        update_interval_days=365,
        fixed_substrate_cost=0,
        analog_conversion_overhead=3.0,
        yield_repair_factor=2.5,
        accuracy_fallback_penalty=0.50,
    )
    costly_fixed = next(r for r in model.evaluate(costly) if r.strategy == "fixed_digital_weights")
    free_fixed = next(r for r in model.evaluate(free_but_bad_analog) if r.strategy == "fixed_digital_weights")
    analog = next(r for r in model.evaluate(free_but_bad_analog) if r.strategy == "analog_in_memory")
    software = next(r for r in model.evaluate(free_but_bad_analog) if r.strategy == "software_optimized")

    assert free_fixed.total_normalized_cost < costly_fixed.total_normalized_cost
    assert analog.total_normalized_cost > software.total_normalized_cost


def test_csv_and_json_schemas_stable(tmp_path: Path) -> None:
    rows = model.grid(model.Inputs())
    csv_path = tmp_path / "breakeven_grid.csv"
    json_path = tmp_path / "breakeven_summary.json"
    model.write_csv(rows, csv_path)
    model.write_summary(rows, model.Inputs(), json_path)

    with csv_path.open(newline="") as f:
        reader = csv.DictReader(f)
        assert reader.fieldnames == [
            "strategy",
            "requests_per_day",
            "update_interval_days",
            "software_memory_savings",
            "fixed_substrate_cost",
            "analog_conversion_overhead",
            "yield_repair_factor",
            "accuracy_fallback_penalty",
            "requests_per_update",
            "per_request_cost",
            "amortized_fixed_cost",
            "total_normalized_cost",
        ]
        first = next(reader)
        assert first["strategy"] in model.STRATEGIES

    summary = json.loads(json_path.read_text())
    assert summary["schema_version"] == 1
    assert summary["strategies"] == list(model.STRATEGIES)
    assert set(summary["winner_counts"]) == set(model.STRATEGIES)
    assert "dominant_variables" in summary
