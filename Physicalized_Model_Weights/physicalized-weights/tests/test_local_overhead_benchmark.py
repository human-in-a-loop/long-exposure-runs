# created: 2026-05-13T08:10:00Z
# cycle: 3
# run_id: run-2026-05-13T015136Z
# agent: worker
# milestone: M-MEASURE-1

from __future__ import annotations

import csv
import importlib.util
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT_DIR = ROOT / "physicalized-weights" / "scripts"
SCRIPT_PATH = SCRIPT_DIR / "local_overhead_benchmark.py"
spec = importlib.util.spec_from_file_location("local_overhead_benchmark", SCRIPT_PATH)
bench = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules["local_overhead_benchmark"] = bench
spec.loader.exec_module(bench)


def benchmark_rows() -> list[dict[str, str]]:
    with bench.BENCHMARK_CSV.open(newline="") as f:
        return list(csv.DictReader(f))


def test_all_validated_workload_scenario_ids_appear() -> None:
    workload_ids = [row.scenario_id for row in bench.read_workloads()]
    output_ids = []
    for row in benchmark_rows():
        if row["scenario_id"] not in output_ids:
            output_ids.append(row["scenario_id"])
    assert output_ids == workload_ids


def test_benchmark_output_schema_is_stable() -> None:
    with bench.BENCHMARK_CSV.open(newline="") as f:
        reader = csv.DictReader(f)
        assert reader.fieldnames == [
            "scenario_id",
            "component",
            "measurement_status",
            "sample_count",
            "feature_length",
            "fallback_frequency",
            "near_threshold_frequency",
            "accepted_fast_path_credit_per_day",
            "median_ns_per_request",
            "p10_ns_per_request",
            "p90_ns_per_request",
            "mean_ns_per_request",
            "latency_weighted_proxy",
            "unit",
        ]
    with bench.GAP_MATRIX_CSV.open(newline="") as f:
        reader = csv.DictReader(f)
        assert reader.fieldnames == ["quantity", "measurement_status", "local_artifact", "production_requirement", "overclaim_guardrail"]
    summary = json.loads(bench.SUMMARY_JSON.read_text())
    assert summary["schema_version"] == 1
    assert summary["milestone_id"] == "M-MEASURE-1"
    assert summary["measurement_status"]["programmable_accelerator_energy"] == "production_required"


def test_fixed_seed_request_construction_is_deterministic() -> None:
    workloads = bench.read_workloads()
    assert [row.scenario_id for row in workloads][:3] == [
        "high_volume_stable_moderation",
        "bursty_consumer_traffic",
        "low_volume_enterprise_deployment",
    ]
    first = workloads[0]
    assert bench.build_requests(first) == bench.build_requests(first)


def test_all_fallback_keeps_dispatch_and_audit_but_no_fast_path_credit() -> None:
    rows = [row for row in benchmark_rows() if row["scenario_id"] == "fallback_all_control"]
    assert rows
    assert {row["accepted_fast_path_credit_per_day"] for row in rows} == {"0.000"}
    route = next(row for row in rows if row["component"] == "route_fallback_decision_proxy")
    audit = next(row for row in rows if row["component"] == "audit_serialization_proxy")
    assert route["median_ns_per_request"]
    assert audit["median_ns_per_request"]
    assert float(route["fallback_frequency"]) == 1.0


def test_zero_invocation_control_has_no_fake_per_request_advantage() -> None:
    rows = [row for row in benchmark_rows() if row["scenario_id"] == "zero_invocation_control"]
    assert rows
    for row in rows:
        assert row["sample_count"] == "0"
        assert row["feature_length"] == "0"
        assert row["measurement_status"] == "not_measured_zero_volume"
        assert row["median_ns_per_request"] == ""
        assert row["latency_weighted_proxy"] == ""


def test_gap_matrix_does_not_overclaim_production_energy() -> None:
    with bench.GAP_MATRIX_CSV.open(newline="") as f:
        rows = list(csv.DictReader(f))
    accelerator_energy = next(row for row in rows if row["quantity"] == "programmable_accelerator_energy")
    assert accelerator_energy["measurement_status"] == "production_required"
    assert "never label accelerator energy as locally measured" in accelerator_energy["overclaim_guardrail"]
    assert not any(row["quantity"].endswith("_energy") and row["measurement_status"] == "locally_measured_proxy" for row in rows)


def test_figure_exists_and_is_nonempty() -> None:
    assert bench.LATENCY_PNG.exists()
    assert bench.LATENCY_PNG.stat().st_size > 100


if __name__ == "__main__":
    bench.main()
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"PASS {name}")
