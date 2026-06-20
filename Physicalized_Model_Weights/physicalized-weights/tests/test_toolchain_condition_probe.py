# created: 2026-05-13T20:08:00Z
# cycle: 11
# run_id: run-2026-05-13T015136Z
# agent: worker
# milestone: M-TOOLCHAIN-1
"""Direct tests for M-TOOLCHAIN-1 toolchain condition probe."""

from __future__ import annotations

import csv
import importlib.util
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "physicalized-weights" / "scripts" / "toolchain_condition_probe.py"
DATA = ROOT / "physicalized-weights" / "data"
REPORT = ROOT / "physicalized-weights" / "docs" / "toolchain_condition_report.md"

spec = importlib.util.spec_from_file_location("toolchain_condition_probe", SCRIPT)
probe = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules["toolchain_condition_probe"] = probe
spec.loader.exec_module(probe)


def regenerate() -> dict[str, object]:
    probe.main()
    with (DATA / "toolchain_condition_summary.json").open() as handle:
        return json.load(handle)


def test_missing_make_or_cxx_is_environment_block_not_prototype_failure() -> None:
    fake_tools = {
        "verilator": {"available": True},
        "make": {"available": False},
        "cxx_compiler": {"available": False},
    }
    available, missing, status = probe.compiled_status(fake_tools)
    assert available is False
    assert status == "blocked_environment"
    assert set(missing) == {"make", "cxx_compiler"}


def test_summary_counters_preserve_campaign_endpoint() -> None:
    summary = regenerate()
    assert summary["current_superiority_claim_count"] == 0
    assert summary["actual_reopen_candidate_count"] == 0
    assert summary["new_reopen_gate_count"] == 0
    assert summary["performance_claim_reopened"] is False


def test_hash_fields_are_present_and_hex() -> None:
    summary = regenerate()
    hash_fields = [
        "hdl_source_sha256",
        "prototype_generator_sha256",
        "yosys_eval_script_sha256",
        "yosys_script_sha256",
        "verilator_testbench_sha256",
        "prototype_closure_script_sha256",
    ]
    for field in hash_fields:
        assert re.fullmatch(r"[0-9a-f]{64}", summary[field]), field


def test_compiled_results_match_golden_if_present() -> None:
    summary = regenerate()
    compiled_results = DATA / "compiled_verilator_safety_filter_results.csv"
    if summary["compiled_verilator_status"] == "blocked_environment":
        assert summary["compiled_verilator_equivalence_passed"] is None
        assert summary["compiled_verilator_missing_tools"]
        return
    assert compiled_results.exists()
    with compiled_results.open(newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert rows
    assert {row["match"] for row in rows} == {"true"}
    assert summary["compiled_verilator_equivalence_passed"] is True


def test_report_explicitly_blocks_performance_reopen_interpretation() -> None:
    regenerate()
    text = REPORT.read_text()
    assert "not a performance/economic reopen path" in text
    assert "does not add a new reopen gate" in text


def test_outputs_exist_and_matrix_schema_is_stable() -> None:
    regenerate()
    expected = [
        DATA / "toolchain_condition_matrix.csv",
        DATA / "toolchain_condition_summary.json",
        DATA / "toolchain_condition_matrix.png",
        REPORT,
    ]
    for path in expected:
        assert path.exists()
        assert path.stat().st_size > 0
    with (DATA / "toolchain_condition_matrix.csv").open(newline="") as handle:
        reader = csv.DictReader(handle)
        assert reader.fieldnames == [
            "check_id",
            "tool",
            "available",
            "version",
            "required_for",
            "status",
            "blocker",
            "evidence_artifact",
        ]


def run_tests() -> None:
    for name, func in sorted(globals().items()):
        if name.startswith("test_") and callable(func):
            func()
            print(f"PASS {name}")


if __name__ == "__main__":
    run_tests()
