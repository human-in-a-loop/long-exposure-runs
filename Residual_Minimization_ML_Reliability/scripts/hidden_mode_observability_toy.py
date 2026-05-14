# created: 2026-05-14T14:45:00Z
# cycle: 50
# run_id: run-2026-05-14T030813Z
# agent: worker
# milestone: M-10
"""CAT-11 toy: partial observation ignores a hidden ODE mode."""

from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
CSV_PATH = DATA / "hidden_mode_observability.csv"
PNG_PATH = DATA / "hidden_mode_observability.png"


def bad_hidden_mode_values(alpha: float) -> dict[str, float | int | str]:
    """For x=(0,1), observed x1 equation is exact while hidden x2 is wrong."""
    observed_residual_l2_sq = 0.0
    observed_state_error = 0.0
    hidden_state_l2_error = 1.0
    full_state_residual_l2_sq = alpha**2
    observability_rank = 1
    state_dim = 2
    return {
        "case": "hidden_constant_bad_family",
        "alpha": alpha,
        "observed_residual_l2_sq": observed_residual_l2_sq,
        "observed_state_error": observed_state_error,
        "hidden_state_l2_error": hidden_state_l2_error,
        "full_state_residual_l2_sq": full_state_residual_l2_sq,
        "observability_rank": observability_rank,
        "state_dim": state_dim,
        "hidden_nullspace_dimension": state_dim - observability_rank,
        "classification": "partial_observation_failure",
    }


def build_rows(alphas: list[float] | None = None) -> list[dict[str, float | int | str]]:
    if alphas is None:
        alphas = [0.25, 0.5, 1.0, 2.0, 4.0, 8.0, 16.0]
    return [bad_hidden_mode_values(alpha) for alpha in alphas]


def write_csv(rows: list[dict[str, float | int | str]], path: Path = CSV_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    header = [
        "case",
        "alpha",
        "observed_residual_l2_sq",
        "observed_state_error",
        "hidden_state_l2_error",
        "full_state_residual_l2_sq",
        "observability_rank",
        "state_dim",
        "hidden_nullspace_dimension",
        "classification",
    ]
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=header)
        writer.writeheader()
        writer.writerows(rows)


def plot_rows(rows: list[dict[str, float | int | str]], path: Path = PNG_PATH) -> None:
    alphas = [float(row["alpha"]) for row in rows]
    observed = [float(row["observed_residual_l2_sq"]) for row in rows]
    hidden = [float(row["hidden_state_l2_error"]) for row in rows]
    full = [float(row["full_state_residual_l2_sq"]) for row in rows]

    fig, ax = plt.subplots(figsize=(6.7, 4.2), constrained_layout=True)
    ax.loglog(alphas, [max(v, 1e-16) for v in observed], "o-", label="observed residual")
    ax.loglog(alphas, hidden, "s--", label="hidden-state error")
    ax.loglog(alphas, full, "^-", label="full-state residual certificate")
    ax.set_xlabel(r"hidden stiffness $\alpha$")
    ax.set_ylabel("value")
    ax.set_title("Observed residual is zero while hidden-state physical error remains nonzero.")
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


if __name__ == "__main__":
    main()
