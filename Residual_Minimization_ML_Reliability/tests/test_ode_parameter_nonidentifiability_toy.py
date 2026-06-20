from __future__ import annotations

import csv
import math
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "ode_parameter_nonidentifiability_toy.py"
CSV_PATH = ROOT / "data" / "ode_parameter_nonidentifiability.csv"


def run_script() -> None:
    subprocess.run([str(ROOT / ".sciml-venv" / "bin" / "python"), str(SCRIPT)], check=True)


def read_rows() -> list[dict[str, str]]:
    with CSV_PATH.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def test_zero_trajectory_residual_is_zero_for_multiple_parameters() -> None:
    run_script()
    rows = read_rows()
    assert len(rows) >= 3
    assert all(math.isclose(float(row["x0"]), 0.0) for row in rows)
    assert all(math.isclose(float(row["state_residual_l2_sq"]), 0.0) for row in rows)
    assert all(math.isclose(float(row["state_data_error"]), 0.0) for row in rows)


def test_parameter_error_can_be_nonzero_while_residual_is_zero() -> None:
    run_script()
    rows = read_rows()
    wrong_rows = [row for row in rows if not math.isclose(float(row["theta"]), float(row["theta_star"]))]
    assert wrong_rows
    assert all(float(row["parameter_abs_error"]) > 0.0 for row in wrong_rows)
    assert all(math.isclose(float(row["state_residual_l2_sq"]), 0.0) for row in wrong_rows)


def test_fisher_certificate_is_zero_without_excitation_and_positive_with_excitation() -> None:
    run_script()
    rows = read_rows()
    assert all(math.isclose(float(row["fisher_information"]), 0.0) for row in rows)
    assert all(float(row["excited_fisher_information_at_theta_star"]) > 0.0 for row in rows)
    assert all(row["classification"] == "parameter_nonidentifiability" for row in rows)
