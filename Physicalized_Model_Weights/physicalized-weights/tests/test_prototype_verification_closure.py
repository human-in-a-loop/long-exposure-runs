# created: 2026-05-13T04:12:00Z
# cycle: 1
# run_id: run-2026-05-13T015136Z
# agent: worker
# milestone: M-PROTO-1
"""Tests for the M-PROTO-1 verification closure contract."""

from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "physicalized-weights" / "data"
CLOSURE_JSON = DATA / "prototype_verification_closure.json"
MATRIX_CSV = DATA / "prototype_equivalence_matrix.csv"


def load_closure() -> dict:
    with CLOSURE_JSON.open() as handle:
        return json.load(handle)


def test_missing_compiled_verilator_records_make_constraint() -> None:
    closure = load_closure()
    compiled = closure["compiled_verilator"]
    if not compiled["compiled_simulation_present"]:
        assert compiled["make_available"] is False
        assert compiled["make_constraint_recorded"] is True
        assert compiled["compiled_simulation_passed"] is False
        assert compiled["compiled_simulation_status"] == "blocked_make_unavailable"


def test_compiled_verilator_if_present_must_match_contract() -> None:
    closure = load_closure()
    compiled = closure["compiled_verilator"]
    if compiled["compiled_simulation_present"]:
        assert compiled["compiled_simulation_passed"] is True
        with MATRIX_CSV.open(newline="") as handle:
            rows = list(csv.DictReader(handle))
        assert rows
        assert {row["compiled_verilator"] for row in rows} == {"pass"}


def test_yosys_eval_and_python_golden_agree_for_every_vector() -> None:
    with MATRIX_CSV.open(newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert rows
    for row in rows:
        assert row["python_golden"] == "pass"
        assert row["route_output"] == "pass"
        assert row["yosys_eval"] == "pass"
        assert row["overall"] == "pass"


def test_hdl_source_hash_recorded() -> None:
    closure = load_closure()
    digest = closure["hashes"]["hdl_source_sha256"]
    assert isinstance(digest, str)
    assert len(digest) == 64
    int(digest, 16)


def test_structural_evidence_is_present_and_checked() -> None:
    closure = load_closure()
    checks = closure["checks"]
    assert checks["verilator_lint_passed"] is True
    assert checks["yosys_synthesis_passed"] is True
    assert checks["yosys_reports_no_memories_or_processes"] is True
    assert checks["graphviz_artifacts_present"] is True
    assert checks["structural_artifacts_fresh"] is True
    assert closure["freshness"]["structural_artifacts_fresh"] is True
    for artifact in [
        DATA / "verilator_safety_filter.log",
        DATA / "yosys_safety_filter.log",
        DATA / "safety_filter_core_netlist.dot",
        DATA / "safety_filter_core_netlist.png",
    ]:
        assert artifact.exists()
        assert artifact.stat().st_size > 0


def test_csv_and_json_schemas_are_stable() -> None:
    with MATRIX_CSV.open(newline="") as handle:
        reader = csv.DictReader(handle)
        assert reader.fieldnames == [
            "case_id",
            "python_golden",
            "route_output",
            "yosys_eval",
            "verilator_lint",
            "yosys_synthesis",
            "graphviz_artifacts",
            "compiled_verilator",
            "overall",
        ]
    closure = load_closure()
    assert closure["schema_version"] == 1
    assert closure["milestone_id"] == "M-PROTO-1"
    assert closure["closure_status"] == "validated"
    assert closure["evidence_contract"] in {
        "amended_lint_yosys_eval_synthesis",
        "compiled_verilator_plus_yosys",
    }
    assert closure["parameters"]["hdl_params_match_python"] is True
    assert closure["parameters"]["summary_params_match_python"] is True


def run_tests() -> None:
    for name, func in sorted(globals().items()):
        if name.startswith("test_") and callable(func):
            func()
            print(f"PASS {name}")


if __name__ == "__main__":
    run_tests()
