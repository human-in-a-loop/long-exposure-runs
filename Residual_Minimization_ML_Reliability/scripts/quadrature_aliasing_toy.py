# created: 2026-05-14T15:20:00Z
# cycle: 51
# run_id: run-2026-05-14T030813Z
# agent: worker
# milestone: M-11
"""CAT-07 toy: Gauss quadrature aliases a nonzero residual to zero."""

from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from numpy.polynomial import legendre as L


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
CSV_PATH = DATA / "quadrature_aliasing.csv"
PNG_PATH = DATA / "quadrature_aliasing.png"


def legendre_values(q: int, x: np.ndarray) -> np.ndarray:
    coeffs = np.zeros(q + 1)
    coeffs[q] = 1.0
    return L.legval(x, coeffs)


def endpoint_values(q: int) -> tuple[float, float]:
    """u_Q(x)=int_{-1}^x P_Q(t)dt has zero endpoints for Q>=1."""
    poly = L.Legendre.basis(q).integ(lbnd=-1.0)
    return float(poly(-1.0)), float(poly(1.0))


def quadrature_aliasing_values(q: int) -> dict[str, float | int | str]:
    nodes, weights = L.leggauss(q)
    residual_at_nodes = legendre_values(q, nodes)
    left, right = endpoint_values(q)
    quadrature_objective = float(np.dot(weights, residual_at_nodes**2) + left**2 + right**2)

    over_nodes, over_weights = L.leggauss(q + 1)
    over_residual = legendre_values(q, over_nodes)
    overintegrated_certificate = float(np.dot(over_weights, over_residual**2))
    exact_residual_l2_sq = 2.0 / (2 * q + 1)

    return {
        "case": "gauss_node_aliasing",
        "q": q,
        "quadrature_objective": quadrature_objective,
        "exact_residual_l2_sq": exact_residual_l2_sq,
        "overintegrated_certificate": overintegrated_certificate,
        "endpoint_left": left,
        "endpoint_right": right,
        "max_abs_residual_at_nodes": float(np.max(np.abs(residual_at_nodes))),
        "classification": "quadrature_aliasing_failure",
    }


def build_rows(qs: list[int] | None = None) -> list[dict[str, float | int | str]]:
    if qs is None:
        qs = [2, 3, 4, 5, 8, 12, 16, 24, 32]
    return [quadrature_aliasing_values(q) for q in qs]


def write_csv(rows: list[dict[str, float | int | str]], path: Path = CSV_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    header = [
        "case",
        "q",
        "quadrature_objective",
        "exact_residual_l2_sq",
        "overintegrated_certificate",
        "endpoint_left",
        "endpoint_right",
        "max_abs_residual_at_nodes",
        "classification",
    ]
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=header)
        writer.writeheader()
        writer.writerows(rows)


def plot_rows(rows: list[dict[str, float | int | str]], path: Path = PNG_PATH) -> None:
    qs = [float(row["q"]) for row in rows]
    quadrature = [max(float(row["quadrature_objective"]), 1e-32) for row in rows]
    exact = [float(row["exact_residual_l2_sq"]) for row in rows]
    overintegrated = [float(row["overintegrated_certificate"]) for row in rows]

    fig, ax = plt.subplots(figsize=(6.8, 4.2), constrained_layout=True)
    ax.loglog(qs, quadrature, "o-", label="Q-node quadrature objective")
    ax.loglog(qs, exact, "s--", label=r"exact $\|P_Q\|_{L^2}^2$")
    ax.loglog(qs, overintegrated, "^-", label="(Q+1)-node overintegration")
    ax.set_xlabel("Gauss-Legendre quadrature order Q")
    ax.set_ylabel("residual norm squared")
    ax.set_title("Gauss-node quadrature reports zero residual while the exact residual norm remains positive.")
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
