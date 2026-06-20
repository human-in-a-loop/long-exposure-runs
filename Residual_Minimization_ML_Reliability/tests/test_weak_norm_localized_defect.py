from __future__ import annotations

import csv
import math
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "weak_norm_localized_defect.py"
CSV_PATH = ROOT / "data" / "weak_norm_localized_defect.csv"


def run_script() -> None:
    subprocess.run([str(ROOT / ".sciml-venv" / "bin" / "python"), str(SCRIPT)], check=True)


def read_rows() -> list[dict[str, str]]:
    with CSV_PATH.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def test_l2_norm_remains_constant_across_localization_scales() -> None:
    run_script()
    rows = read_rows()
    assert rows
    assert all(math.isclose(float(row["l2_norm"]), 1.0, rel_tol=1e-3, abs_tol=1e-3) for row in rows)
    assert all(math.isclose(float(row["local_l2_certificate"]), 1.0, rel_tol=1e-3, abs_tol=1e-3) for row in rows)


def test_negative_norm_objective_decreases_as_support_shrinks() -> None:
    run_script()
    rows = sorted(read_rows(), key=lambda row: float(row["epsilon"]), reverse=True)
    objectives = [float(row["hminus_objective"]) for row in rows]
    assert objectives == sorted(objectives, reverse=True)
    assert objectives[-1] < objectives[0] / 10.0


def test_local_certificate_remains_nonzero_and_mean_mode_is_suppressed() -> None:
    run_script()
    rows = read_rows()
    assert all(float(row["linf_certificate"]) > 1.0 for row in rows)
    assert all(float(row["mean_abs"]) < 1e-12 for row in rows)
    assert {row["classification"] for row in rows} == {"failure"}
