from __future__ import annotations

import csv
import math
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "trace_leakage_toy.py"
CSV_PATH = ROOT / "data" / "trace_leakage_scaling.csv"


def run_script() -> None:
    subprocess.run([str(ROOT / ".sciml-venv" / "bin" / "python"), str(SCRIPT)], check=True)


def read_rows() -> list[dict[str, str]]:
    with CSV_PATH.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def test_bad_constant_has_vanishing_objective_and_unit_error() -> None:
    run_script()
    rows = [row for row in read_rows() if row["case"] == "bad_constant"]
    objectives = [float(row["objective"]) for row in rows]
    assert objectives == sorted(objectives, reverse=True)
    assert objectives[-1] < objectives[0] / 1000.0
    assert all(math.isclose(float(row["physical_l2_error"]), 1.0) for row in rows)


def test_fixed_trace_certificate_detects_boundary_failure_point() -> None:
    run_script()
    rows = [row for row in read_rows() if row["case"] == "bad_constant"]
    assert rows
    assert all(math.isclose(float(row["trace_value"]), 1.0) for row in rows)
    assert all(math.isclose(float(row["fixed_trace_certificate"]), 1.0) for row in rows)


def test_shrinking_control_reduces_error_and_certificate() -> None:
    run_script()
    rows = [row for row in read_rows() if row["case"] == "shrinking_constant_control"]
    assert rows[-1]["n"] == "128"
    assert float(rows[-1]["physical_l2_error"]) < float(rows[0]["physical_l2_error"])
    assert float(rows[-1]["fixed_trace_certificate"]) < float(rows[0]["fixed_trace_certificate"])
