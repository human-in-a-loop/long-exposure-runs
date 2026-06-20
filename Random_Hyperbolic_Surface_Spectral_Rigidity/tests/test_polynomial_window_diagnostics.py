from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import probe_polynomial_window_diagnostics as probe


def make_rows(xs, values, se=0.0):
    return [
        {"n": 1.0 / x, "x": float(x), "observed": float(y), "standard_error": se}
        for x, y in zip(xs, values)
    ]


def test_exact_polynomial_data_recovered_by_matching_degree():
    xs = np.asarray([0.01, 0.02, 0.04, 0.08, 0.16])
    ys = 1.0 + 2.0 * xs - 3.0 * xs**2
    fit = probe.fit_polynomial(xs, ys, 2, "control")
    predicted = fit.polynomial(xs)
    assert np.max(np.abs(predicted - ys)) < 1e-12


def test_heldout_error_near_zero_for_known_polynomial_control():
    xs = np.asarray([0.005, 0.01, 0.02, 0.04, 0.08, 0.16])
    ys = 0.5 - xs + 4.0 * xs**2
    rows = make_rows(xs, ys)
    grouped = {"control": rows}
    _, summary = probe.diagnostic_rows(grouped, [2], 0.25, 0, 123)
    assert summary[0]["holdout_rmse"] < 1e-12
    assert summary[0]["extrapolation_rmse"] < 1e-12


def test_derivative_diagnostic_increases_for_chebyshev_controls():
    xs = np.linspace(0.0, 1.0, 17)
    low = probe.fit_polynomial(xs, np.polynomial.chebyshev.chebval(2 * xs - 1, [0, 0, 1]), 2, "t2")
    high = probe.fit_polynomial(xs, np.polynomial.chebyshev.chebval(2 * xs - 1, [0, 0, 0, 0, 0, 0, 1]), 6, "t6")
    assert abs(high.derivative_at_zero) > abs(low.derivative_at_zero)
    assert high.coefficient_norm > low.coefficient_norm


def test_deterministic_seed_reproduces_bootstrap_rows():
    xs = np.asarray([0.01, 0.02, 0.04, 0.08, 0.16, 0.2])
    rows = make_rows(xs, 1.0 + xs, se=0.01)
    grouped = {"control": rows}
    detail1, summary1 = probe.diagnostic_rows(grouped, [1, 2], 0.25, 3, 99)
    detail2, summary2 = probe.diagnostic_rows(grouped, [1, 2], 0.25, 3, 99)
    assert detail1 == detail2
    assert summary1 == summary2
    assert {
        "template",
        "n",
        "x",
        "observed",
        "fit_degree",
        "prediction",
        "residual",
        "split",
        "bootstrap_id",
        "seed",
    }.issubset(detail1[0])


if __name__ == "__main__":
    test_exact_polynomial_data_recovered_by_matching_degree()
    test_heldout_error_near_zero_for_known_polynomial_control()
    test_derivative_diagnostic_increases_for_chebyshev_controls()
    test_deterministic_seed_reproduces_bootstrap_rows()
    print("all polynomial window diagnostic tests passed")
