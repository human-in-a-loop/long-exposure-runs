# created: 2026-05-14T16:45:00Z
# cycle: 54
# run_id: run-2026-05-14T030813Z
# agent: worker
# milestone: M-10
"""CAT-17 toy: zero-excitation ODE data do not identify the parameter."""

from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
CSV_PATH = DATA / "ode_parameter_nonidentifiability.csv"
PNG_PATH = DATA / "ode_parameter_nonidentifiability.png"


def fisher_information(theta: float, x0: float, t_final: float = 1.0, n_grid: int = 2001) -> float:
    t = np.linspace(0.0, t_final, n_grid)
    sensitivity = x0 * t * np.exp(theta * t)
    return float(np.trapezoid(sensitivity**2, t))


def build_rows(
    theta_star: float = -1.0,
    theta_values: list[float] | None = None,
    excited_x0: float = 1.0,
) -> list[dict[str, float | str]]:
    if theta_values is None:
        theta_values = [-4.0, -2.0, -1.0, 0.0, 2.0, 4.0]

    rows: list[dict[str, float | str]] = []
    excited_information_at_star = fisher_information(theta_star, excited_x0)
    for theta in theta_values:
        rows.append(
            {
                "case": "zero_trajectory_unidentified_parameter",
                "theta_star": theta_star,
                "theta": theta,
                "x0": 0.0,
                "state_residual_l2_sq": 0.0,
                "state_data_error": 0.0,
                "parameter_abs_error": abs(theta - theta_star),
                "fisher_information": fisher_information(theta, 0.0),
                "excited_x0": excited_x0,
                "excited_fisher_information_at_theta_star": excited_information_at_star,
                "classification": "parameter_nonidentifiability",
            }
        )
    return rows


def write_csv(rows: list[dict[str, float | str]], path: Path = CSV_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    header = [
        "case",
        "theta_star",
        "theta",
        "x0",
        "state_residual_l2_sq",
        "state_data_error",
        "parameter_abs_error",
        "fisher_information",
        "excited_x0",
        "excited_fisher_information_at_theta_star",
        "classification",
    ]
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=header)
        writer.writeheader()
        writer.writerows(rows)


def plot_rows(rows: list[dict[str, float | str]], path: Path = PNG_PATH) -> None:
    theta = [float(row["theta"]) for row in rows]
    residual = [float(row["state_residual_l2_sq"]) for row in rows]
    param_error = [float(row["parameter_abs_error"]) for row in rows]
    fisher_zero = [float(row["fisher_information"]) for row in rows]
    fisher_excited = [float(row["excited_fisher_information_at_theta_star"]) for row in rows]

    fig, ax = plt.subplots(figsize=(6.7, 4.2), constrained_layout=True)
    ax.plot(theta, residual, "o-", label="zero-trajectory residual")
    ax.plot(theta, param_error, "s-", label=r"parameter error $|\theta-\theta^\star|$")
    ax.plot(theta, fisher_zero, "^-", label="Fisher information, x0=0")
    ax.plot(theta, fisher_excited, "d--", label=r"Fisher information, $x_0=1$ at $\theta^\star$")
    ax.set_xlabel(r"candidate parameter $\theta$")
    ax.set_ylabel("value")
    ax.set_title("Zero trajectory gives zero residual for every parameter; excitation restores identifiability.")
    ax.grid(True, alpha=0.25)
    ax.legend(fontsize=8)
    fig.savefig(path, dpi=180)
    plt.close(fig)


def main() -> None:
    rows = build_rows()
    write_csv(rows)
    plot_rows(rows)
    print(f"wrote {CSV_PATH}")
    print(f"wrote {PNG_PATH}")


if __name__ == "__main__":
    main()
