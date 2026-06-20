from __future__ import annotations

import csv
import math
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "hidden_mode_observability_toy.py"
CSV_PATH = ROOT / "data" / "hidden_mode_observability.csv"


def run_script() -> None:
    subprocess.run([str(ROOT / ".sciml-venv" / "bin" / "python"), str(SCRIPT)], check=True)


def read_rows() -> list[dict[str, str]]:
    with CSV_PATH.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def test_observed_objective_is_blind_to_hidden_error() -> None:
    run_script()
    rows = read_rows()
    assert rows
    assert all(math.isclose(float(row["observed_residual_l2_sq"]), 0.0) for row in rows)
    assert all(math.isclose(float(row["observed_state_error"]), 0.0) for row in rows)
    assert all(math.isclose(float(row["hidden_state_l2_error"]), 1.0) for row in rows)


def test_full_state_residual_certificate_detects_hidden_mode() -> None:
    run_script()
    rows = read_rows()
    full_residuals = [float(row["full_state_residual_l2_sq"]) for row in rows]
    assert full_residuals == sorted(full_residuals)
    assert all(value > 0.0 for value in full_residuals)


def test_observability_rank_reports_hidden_nullspace() -> None:
    run_script()
    rows = read_rows()
    assert all(int(row["observability_rank"]) == 1 for row in rows)
    assert all(int(row["state_dim"]) == 2 for row in rows)
    assert all(int(row["hidden_nullspace_dimension"]) == 1 for row in rows)
