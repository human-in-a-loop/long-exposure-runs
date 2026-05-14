from __future__ import annotations

import csv
import math
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "positivity_mass_toy.py"
CSV_PATH = ROOT / "data" / "positivity_mass_toy.csv"


def run_script() -> None:
    subprocess.run([str(ROOT / ".sciml-venv" / "bin" / "python"), str(SCRIPT)], check=True)


def read_rows() -> list[dict[str, str]]:
    with CSV_PATH.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def test_aggregate_residual_zero_for_good_boundary_and_bad_mass_correct_paths() -> None:
    run_script()
    rows = read_rows()
    assert rows
    for row in rows:
        assert math.isclose(float(row["mass"]), 1.0, abs_tol=1e-14)
        assert math.isclose(float(row["mass_derivative"]), 0.0, abs_tol=1e-14)
        assert math.isclose(float(row["aggregate_residual"]), 0.0, abs_tol=1e-14)


def test_positivity_certificate_detects_negative_concentrations_only() -> None:
    run_script()
    for row in read_rows():
        certificate = float(row["positivity_certificate"])
        minimum = float(row["minimum_concentration"])
        if minimum < 0.0:
            assert certificate > 0.0
        else:
            assert math.isclose(certificate, 0.0, abs_tol=1e-14)


def test_csv_contains_admissible_boundary_and_inadmissible_states() -> None:
    run_script()
    rows = read_rows()
    classes = {row["classification"] for row in rows}
    cases = {row["case"] for row in rows}
    assert "admissible_simplex_state" in classes
    assert "mass_correct_but_negative" in classes
    assert "positivity_boundary_c1_zero" in cases
    assert "positivity_boundary_c2_zero" in cases
