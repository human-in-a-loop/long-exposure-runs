from __future__ import annotations

import csv
import math
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "quadrature_aliasing_toy.py"
CSV_PATH = ROOT / "data" / "quadrature_aliasing.csv"


def run_script() -> None:
    subprocess.run([str(ROOT / ".sciml-venv" / "bin" / "python"), str(SCRIPT)], check=True)


def read_rows() -> list[dict[str, str]]:
    with CSV_PATH.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def test_gauss_quadrature_objective_is_numerically_zero() -> None:
    run_script()
    rows = read_rows()
    assert rows
    for row in rows:
        assert abs(float(row["quadrature_objective"])) < 1e-24
        assert abs(float(row["max_abs_residual_at_nodes"])) < 1e-12


def test_exact_residual_norm_matches_legendre_formula() -> None:
    run_script()
    for row in read_rows():
        q = int(row["q"])
        expected = 2.0 / (2 * q + 1)
        assert math.isclose(float(row["exact_residual_l2_sq"]), expected, rel_tol=1e-14)
        assert math.isclose(float(row["overintegrated_certificate"]), expected, rel_tol=1e-12)


def test_endpoint_penalties_vanish() -> None:
    run_script()
    for row in read_rows():
        assert abs(float(row["endpoint_left"])) < 1e-14
        assert abs(float(row["endpoint_right"])) < 1e-14
