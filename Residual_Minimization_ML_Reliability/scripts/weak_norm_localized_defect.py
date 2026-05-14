# created: 2026-05-14T16:20:00Z
# cycle: 53
# run_id: run-2026-05-14T030813Z
# agent: worker
# milestone: M-8
"""M-8 toy: localized L2-scale defects can vanish in negative norms."""

from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
CSV_PATH = DATA / "weak_norm_localized_defect.csv"
PNG_PATH = DATA / "weak_norm_localized_defect.png"


def smooth_bump(z: np.ndarray) -> np.ndarray:
    values = np.zeros_like(z, dtype=float)
    mask = np.abs(z) < 1.0
    values[mask] = np.exp(-1.0 / (1.0 - z[mask] ** 2))
    return values


def localized_defect(x: np.ndarray, epsilon: float, center: float = 0.5) -> np.ndarray:
    """Mean-zero compact interior defect, normalized later to unit L2."""
    offset = 0.45 * epsilon
    left = smooth_bump((x - (center - offset)) / epsilon)
    right = smooth_bump((x - (center + offset)) / epsilon)
    return epsilon ** -0.5 * (left - right)


def l2_norm(u: np.ndarray, dx: float) -> float:
    return float(np.sqrt(dx * np.sum(u * u)))


def hminus_norm_sq_periodic(u: np.ndarray, s: float, dx: float) -> float:
    """Squared periodic H^{-s} norm using orthonormal Fourier coefficients."""
    coeffs = np.fft.fft(u) / u.size
    freqs = np.fft.fftfreq(u.size, d=dx)
    weights = (1.0 + (2.0 * np.pi * freqs) ** 2) ** (-s)
    return float(np.sum(weights * np.abs(coeffs) ** 2))


def build_rows(
    epsilons: list[float] | None = None,
    s: float = 1.0,
    n_grid: int = 32768,
) -> list[dict[str, float | str]]:
    if epsilons is None:
        epsilons = [0.16, 0.12, 0.09, 0.0675, 0.05, 0.0375, 0.028125]
    x = np.linspace(0.0, 1.0, n_grid, endpoint=False)
    dx = 1.0 / n_grid
    rows: list[dict[str, float | str]] = []
    for epsilon in epsilons:
        raw = localized_defect(x, epsilon)
        raw_l2 = l2_norm(raw, dx)
        u = raw / raw_l2
        objective = hminus_norm_sq_periodic(u, s=s, dx=dx)
        rows.append(
            {
                "case": "mean_zero_localized_defect",
                "epsilon": epsilon,
                "s": s,
                "l2_norm": l2_norm(u, dx),
                "hminus_objective": objective,
                "local_l2_certificate": l2_norm(u, dx),
                "linf_certificate": float(np.max(np.abs(u))),
                "mean_abs": float(abs(dx * np.sum(u))),
                "classification": "failure",
            }
        )
    return rows


def write_csv(rows: list[dict[str, float | str]], path: Path = CSV_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    header = [
        "case",
        "epsilon",
        "s",
        "l2_norm",
        "hminus_objective",
        "local_l2_certificate",
        "linf_certificate",
        "mean_abs",
        "classification",
    ]
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=header)
        writer.writeheader()
        writer.writerows(rows)


def fit_log_slope(rows: list[dict[str, float | str]]) -> float:
    eps = np.array([float(row["epsilon"]) for row in rows])
    obj = np.array([float(row["hminus_objective"]) for row in rows])
    slope, _ = np.polyfit(np.log(eps), np.log(obj), 1)
    return float(slope)


def plot_rows(rows: list[dict[str, float | str]], path: Path = PNG_PATH) -> None:
    eps = np.array([float(row["epsilon"]) for row in rows])
    objective = np.array([float(row["hminus_objective"]) for row in rows])
    l2 = np.array([float(row["l2_norm"]) for row in rows])
    linf = np.array([float(row["linf_certificate"]) for row in rows])
    slope = fit_log_slope(rows)

    fig, ax = plt.subplots(figsize=(6.8, 4.4), constrained_layout=True)
    ax.loglog(eps, objective, "o-", label=rf"$\|u_\epsilon\|_{{H^{{-1}}}}^2$; slope {slope:.2f}")
    ax.loglog(eps, l2, "k--", label=r"$\|u_\epsilon\|_{L^2}$")
    ax.loglog(eps, linf / linf[0], "s:", label=r"scaled local max certificate")
    ax.invert_xaxis()
    ax.set_xlabel(r"support scale $\epsilon$")
    ax.set_ylabel("value")
    ax.set_title(r"A localized $L^2$-scale defect becomes small in a negative Sobolev norm as its support shrinks.")
    ax.grid(True, which="both", alpha=0.25)
    ax.legend(fontsize=8)
    fig.savefig(path, dpi=180)
    plt.close(fig)


def main() -> None:
    rows = build_rows()
    write_csv(rows)
    plot_rows(rows)
    print(f"wrote {CSV_PATH}")
    print(f"wrote {PNG_PATH}")
    print(f"fitted log-log slope {fit_log_slope(rows):.3f}")


if __name__ == "__main__":
    main()
