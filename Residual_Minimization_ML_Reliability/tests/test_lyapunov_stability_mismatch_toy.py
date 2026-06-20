from __future__ import annotations

import csv
import math
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "lyapunov_stability_mismatch_toy.py"
CSV_PATH = ROOT / "data" / "lyapunov_stability_mismatch.csv"


def run_script() -> None:
    subprocess.run([str(ROOT / ".sciml-venv" / "bin" / "python"), str(SCRIPT)], check=True)


def read_rows() -> list[dict[str, str]]:
    with CSV_PATH.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def test_training_residual_at_equilibrium_is_zero_for_both_fields() -> None:
    run_script()
    rows = read_rows()
    assert rows
    assert all(math.isclose(float(row["training_x"]), 0.0) for row in rows)
    assert all(math.isclose(float(row["true_training_residual"]), 0.0) for row in rows)
    assert all(math.isclose(float(row["bad_training_residual"]), 0.0) for row in rows)


def test_deployment_error_from_x0_one_grows() -> None:
    run_script()
    rows = read_rows()
    errors = [float(row["deployment_abs_error"]) for row in rows]
    assert math.isclose(errors[0], 0.0)
    assert errors[-1] > 7.0
    assert errors == sorted(errors)


def test_bad_field_violates_lyapunov_decrease_away_from_zero() -> None:
    run_script()
    rows = read_rows()
    assert all(float(row["true_lyapunov_dot_at_x1"]) < 0.0 for row in rows)
    assert all(float(row["bad_lyapunov_dot_at_x1"]) > 0.0 for row in rows)
    assert all(row["classification"] == "deployment_region_stability_failure" for row in rows)
