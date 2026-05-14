from __future__ import annotations

import csv
import math
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "triage_residual_sequences.py"
CSV_PATH = ROOT / "data" / "triage_residual_scaling.csv"


def run_script() -> None:
    subprocess.run([str(ROOT / ".sciml-venv" / "bin" / "python"), str(SCRIPT)], check=True)


def read_rows() -> list[dict[str, str]]:
    with CSV_PATH.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def test_collocation_blind_spot_loss_zero_error_nonzero() -> None:
    run_script()
    rows = [r for r in read_rows() if r["candidate"] == "C1_collocation_blind_spot"]
    assert rows
    assert all(float(r["residual_loss"]) == 0.0 for r in rows)
    assert all(float(r["error_norm"]) > 0.6 for r in rows)
    assert math.isclose(float(rows[0]["error_norm"]), math.sqrt(3.0 / 8.0), rel_tol=1e-12)


def test_certificate_detects_bad_sequences() -> None:
    run_script()
    rows = read_rows()
    c1 = [r for r in rows if r["candidate"] == "C1_collocation_blind_spot"]
    c2 = [r for r in rows if r["candidate"] == "C2_underweighted_trace"]
    assert float(c1[-1]["certificate_norm"]) > float(c1[0]["certificate_norm"])
    assert all(float(r["certificate_norm"]) >= 1.0 for r in c2)
    assert float(c2[-1]["residual_loss"]) < float(c2[0]["residual_loss"])
    assert all(float(r["error_norm"]) == 1.0 for r in c2)


def test_csv_required_columns_finite_nonnegative() -> None:
    run_script()
    required = {"candidate", "n", "residual_loss", "error_norm", "certificate_norm"}
    rows = read_rows()
    assert rows
    assert required <= set(rows[0])
    for row in rows:
        assert int(row["n"]) > 0
        for key in ["residual_loss", "error_norm", "certificate_norm"]:
            value = float(row[key])
            assert math.isfinite(value)
            assert value >= 0.0
