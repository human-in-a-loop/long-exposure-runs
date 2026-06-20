from __future__ import annotations

import csv
import math
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "weak_norm_high_frequency_toy.py"
CSV_PATH = ROOT / "data" / "weak_norm_scaling.csv"


def run_script() -> None:
    subprocess.run([str(ROOT / ".sciml-venv" / "bin" / "python"), str(SCRIPT)], check=True)


def read_rows() -> list[dict[str, str]]:
    with CSV_PATH.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def test_direct_hminus_objective_decays_while_l2_error_stays_fixed() -> None:
    run_script()
    rows = [
        row
        for row in read_rows()
        if row["case"] == "direct_Hminus_failure" and math.isclose(float(row["s"]), 1.0)
    ]
    objectives = [float(row["objective"]) for row in rows]
    assert objectives == sorted(objectives, reverse=True)
    assert objectives[-1] < objectives[0] / 1000.0
    assert all(math.isclose(float(row["physical_l2_error"]), 1.0) for row in rows)


def test_stronger_negative_norm_decays_faster() -> None:
    run_script()
    rows = read_rows()
    by_k = {}
    for row in rows:
        if row["case"] == "direct_Hminus_failure":
            by_k.setdefault(int(row["k"]), {})[float(row["s"])] = float(row["objective"])
    assert by_k
    for values in by_k.values():
        assert values[2.0] <= values[1.0]


def test_elliptic_matched_negative_control_is_stability_baseline() -> None:
    run_script()
    rows = [row for row in read_rows() if row["case"] == "elliptic_matched_negative_control"]
    assert rows
    assert all(row["classification"] == "stability_baseline" for row in rows)
    assert all(math.isclose(float(row["objective"]), 1.0) for row in rows)
    assert all(math.isclose(float(row["matched_stability_baseline"]), 1.0) for row in rows)
