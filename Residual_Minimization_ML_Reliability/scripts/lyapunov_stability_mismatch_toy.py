# created: 2026-05-14T16:45:00Z
# cycle: 54
# run_id: run-2026-05-14T030813Z
# agent: worker
# milestone: M-10
"""CAT-14 toy: equilibrium-trajectory residual misses off-trajectory stability."""

from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
CSV_PATH = DATA / "lyapunov_stability_mismatch.csv"
PNG_PATH = DATA / "lyapunov_stability_mismatch.png"


def true_field(x: np.ndarray | float) -> np.ndarray | float:
    return -x


def bad_field(x: np.ndarray | float) -> np.ndarray | float:
    return x


def lyapunov_derivative(x: np.ndarray | float, field_value: np.ndarray | float) -> np.ndarray | float:
    return 2.0 * x * field_value


def build_rows(times: np.ndarray | None = None, x0: float = 1.0) -> list[dict[str, float | str]]:
    if times is None:
        times = np.linspace(0.0, 2.0, 9)

    rows: list[dict[str, float | str]] = []
    for t in times:
        true_x = x0 * np.exp(-t)
        bad_x = x0 * np.exp(t)
        rows.append(
            {
                "case": "equilibrium_training_off_trajectory_deployment",
                "t": float(t),
                "training_x": 0.0,
                "true_training_residual": 0.0,
                "bad_training_residual": 0.0,
                "deployment_x0": x0,
                "true_deployment_x": float(true_x),
                "bad_deployment_x": float(bad_x),
                "deployment_abs_error": float(abs(bad_x - true_x)),
                "true_lyapunov_dot_at_x1": float(lyapunov_derivative(1.0, true_field(1.0))),
                "bad_lyapunov_dot_at_x1": float(lyapunov_derivative(1.0, bad_field(1.0))),
                "classification": "deployment_region_stability_failure",
            }
        )
    return rows


def write_csv(rows: list[dict[str, float | str]], path: Path = CSV_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    header = [
        "case",
        "t",
        "training_x",
        "true_training_residual",
        "bad_training_residual",
        "deployment_x0",
        "true_deployment_x",
        "bad_deployment_x",
        "deployment_abs_error",
        "true_lyapunov_dot_at_x1",
        "bad_lyapunov_dot_at_x1",
        "classification",
    ]
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=header)
        writer.writeheader()
        writer.writerows(rows)


def plot_rows(rows: list[dict[str, float | str]], path: Path = PNG_PATH) -> None:
    times = [float(row["t"]) for row in rows]
    true_x = [float(row["true_deployment_x"]) for row in rows]
    bad_x = [float(row["bad_deployment_x"]) for row in rows]
    error = [float(row["deployment_abs_error"]) for row in rows]

    fig, ax = plt.subplots(figsize=(6.7, 4.2), constrained_layout=True)
    ax.plot(times, true_x, "o-", label=r"true rollout $x'= -x$")
    ax.plot(times, bad_x, "s-", label=r"learned rollout $\hat f(x)=x$")
    ax.plot(times, error, "^-", label="deployment absolute error")
    ax.axhline(0.0, color="black", linewidth=0.8)
    ax.set_xlabel("time")
    ax.set_ylabel("state or error")
    ax.set_title(
        "Training residual on the equilibrium trajectory is zero, but the learned vector field violates the Lyapunov decrease certificate off trajectory."
    )
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
