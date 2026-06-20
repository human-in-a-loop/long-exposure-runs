from __future__ import annotations

import csv
import math
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "eigenmode_normalization_toy.py"
CSV_PATH = ROOT / "data" / "eigenmode_normalization.csv"


def run_script() -> None:
    subprocess.run([str(ROOT / ".sciml-venv" / "bin" / "python"), str(SCRIPT)], check=True)


def read_rows() -> list[dict[str, str]]:
    with CSV_PATH.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def test_eigen_residual_is_zero_for_sampled_amplitudes() -> None:
    run_script()
    rows = read_rows()
    assert rows
    assert all(math.isclose(float(row["eigen_residual_l2_sq"]), 0.0) for row in rows)
    assert all(math.isclose(float(row["objective_without_normalization"]), 0.0) for row in rows)


def test_physical_error_is_nonzero_away_from_normalized_amplitude() -> None:
    run_script()
    for row in read_rows():
        amplitude = float(row["amplitude"])
        target = float(row["target_amplitude"])
        error = float(row["physical_l2_error"])
        if math.isclose(amplitude, target, rel_tol=1e-14, abs_tol=1e-14):
            assert math.isclose(error, 0.0, abs_tol=1e-14)
        else:
            assert error > 0.0


def test_normalization_certificate_zero_only_at_sampled_normalized_amplitude() -> None:
    run_script()
    zero_certificate_rows = [
        row for row in read_rows() if math.isclose(float(row["normalization_certificate"]), 0.0, abs_tol=1e-14)
    ]
    assert len(zero_certificate_rows) == 1
    row = zero_certificate_rows[0]
    assert math.isclose(float(row["amplitude"]), float(row["target_amplitude"]), rel_tol=1e-14)
