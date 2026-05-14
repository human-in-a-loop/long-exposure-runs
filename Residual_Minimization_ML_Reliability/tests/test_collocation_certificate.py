from __future__ import annotations

import csv
import math
import subprocess
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "collocation_certificate_scaling.py"
CSV_PATH = ROOT / "data" / "collocation_certificate_scaling.csv"


def run_script() -> None:
    subprocess.run([str(ROOT / ".sciml-venv" / "bin" / "python"), str(SCRIPT)], check=True)


def read_rows() -> list[dict[str, str]]:
    with CSV_PATH.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def test_fixed_uniform_nodes_make_bad_sequence_loss_zero() -> None:
    m = 8
    n = 5
    nodes = np.arange(m + 1) / m
    derivative_samples = math.pi * m * n * np.sin(2.0 * math.pi * m * n * nodes)
    endpoints = np.sin(math.pi * m * n * np.array([0.0, 1.0])) ** 2
    sampled_objective = float(np.mean(derivative_samples**2) + np.sum(endpoints**2))
    assert math.isclose(sampled_objective, 0.0, abs_tol=1e-20)


def test_l2_error_squared_exact_value() -> None:
    run_script()
    rows = read_rows()
    assert rows
    assert all(math.isclose(float(row["l2_error_sq"]), 3.0 / 8.0, rel_tol=1e-12) for row in rows)


def test_sampled_certificate_bounds_l2_error() -> None:
    run_script()
    for row in read_rows():
        assert float(row["bound_rhs"]) >= float(row["l2_error_sq"])
        assert float(row["bound_ratio"]) >= 1.0


def test_regularity_term_grows_with_hidden_oscillation() -> None:
    run_script()
    rows = [row for row in read_rows() if int(row["m"]) == 8]
    certs = [float(row["regularity_certificate"]) for row in rows]
    sampled_losses = [float(row["sampled_loss"]) for row in rows]
    assert all(loss == 0.0 for loss in sampled_losses)
    assert certs == sorted(certs)
    assert certs[-1] > certs[0] * 1000.0


def test_control_sequence_shrinks_with_epsilon() -> None:
    import importlib.util

    spec = importlib.util.spec_from_file_location("collocation_certificate_scaling", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    large = module.control_values(m=8, epsilon=1e-1)
    small = module.control_values(m=8, epsilon=1e-3)
    assert small["sampled_loss"] < large["sampled_loss"]
    assert small["regularity_certificate"] < large["regularity_certificate"]
    assert small["l2_error_sq"] < large["l2_error_sq"]
    assert small["bound_rhs"] >= small["l2_error_sq"]
