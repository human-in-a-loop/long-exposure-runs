# created: 2026-05-14T03:45:00Z
# cycle: 1
# run_id: run-2026-05-14T030813Z
# agent: worker
# milestone: M-3
"""Scaling checks for the fixed-collocation blind spot and sampled certificate."""

from __future__ import annotations

import csv
import math
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
CSV_PATH = DATA / "collocation_certificate_scaling.csv"
SCALING_PNG = DATA / "collocation_certificate_scaling.png"
PROFILES_PNG = DATA / "collocation_certificate_profiles.png"


def bad_sequence_values(m: int, n: int) -> dict[str, float | int]:
    h = 1.0 / m
    sampled_loss = 0.0
    l2_error_sq = 3.0 / 8.0
    du_l2_sq = (math.pi * m * n) ** 2 / 2.0
    d2u_l2_sq = 2.0 * (math.pi * m * n) ** 4
    regularity_certificate = 4.0 * h * sampled_loss + 4.0 * h * h * d2u_l2_sq
    bound_rhs = regularity_certificate
    return {
        "m": m,
        "n": n,
        "h": h,
        "sampled_loss": sampled_loss,
        "l2_error_sq": l2_error_sq,
        "du_l2_sq": du_l2_sq,
        "d2u_l2_sq": d2u_l2_sq,
        "regularity_certificate": regularity_certificate,
        "bound_rhs": bound_rhs,
        "bound_ratio": bound_rhs / l2_error_sq,
    }


def control_values(m: int, epsilon: float) -> dict[str, float | int | str]:
    h = 1.0 / m
    # u_eps = eps*x*(1-x), u' = eps*(1-2x), u'' = -2 eps.
    nodes = np.arange(m) / m
    derivative_samples = epsilon * (1.0 - 2.0 * nodes)
    sampled_sum = float(np.sum(derivative_samples**2))
    sampled_loss = h * sampled_sum
    l2_error_sq = epsilon**2 / 30.0
    du_l2_sq = epsilon**2 / 3.0
    d2u_l2_sq = 4.0 * epsilon**2
    regularity_certificate = 4.0 * h * sampled_sum + 4.0 * h * h * d2u_l2_sq
    bound_rhs = 2.0 * 0.0 + regularity_certificate
    return {
        "case": "control",
        "m": m,
        "epsilon": epsilon,
        "h": h,
        "sampled_loss": sampled_loss,
        "l2_error_sq": l2_error_sq,
        "du_l2_sq": du_l2_sq,
        "d2u_l2_sq": d2u_l2_sq,
        "regularity_certificate": regularity_certificate,
        "bound_rhs": bound_rhs,
        "bound_ratio": bound_rhs / l2_error_sq if l2_error_sq else math.inf,
    }


def build_rows(ms: list[int], ns: list[int]) -> list[dict[str, float | int]]:
    rows: list[dict[str, float | int]] = []
    for m in ms:
        for n in ns:
            rows.append(bad_sequence_values(m, n))
    return rows


def write_csv(rows: list[dict[str, float | int]], path: Path = CSV_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    header = [
        "m",
        "n",
        "h",
        "sampled_loss",
        "l2_error_sq",
        "du_l2_sq",
        "d2u_l2_sq",
        "regularity_certificate",
        "bound_rhs",
        "bound_ratio",
    ]
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=header)
        writer.writeheader()
        writer.writerows(rows)


def plot_scaling(rows: list[dict[str, float | int]], path: Path = SCALING_PNG) -> None:
    subset = [row for row in rows if int(row["m"]) == 8]
    ns = np.array([float(row["n"]) for row in subset])
    sampled_loss = np.array([float(row["sampled_loss"]) for row in subset])
    l2_error_sq = np.array([float(row["l2_error_sq"]) for row in subset])
    regularity = np.array([float(row["regularity_certificate"]) for row in subset])
    bound_ratio = np.array([float(row["bound_ratio"]) for row in subset])

    fig, axes = plt.subplots(1, 2, figsize=(10, 4), constrained_layout=True)
    axes[0].loglog(ns, np.maximum(sampled_loss, 1e-16), "o-", label="sampled collocation loss")
    axes[0].loglog(ns, l2_error_sq, "s--", label=r"$\|u_n\|_{L^2}^2$")
    axes[0].loglog(ns, regularity, "^-", label="fill-distance regularity certificate")
    axes[0].set_xlabel("oscillation index n")
    axes[0].set_ylabel("value")
    axes[0].set_title("Zero sampled loss, nonzero error")
    axes[0].legend(fontsize=8)
    axes[0].grid(True, which="both", alpha=0.25)

    axes[1].loglog(ns, bound_ratio, "o-", color="tab:green")
    axes[1].axhline(1.0, color="black", linestyle="--", linewidth=1.0, label="valid bound threshold")
    axes[1].set_xlabel("oscillation index n")
    axes[1].set_ylabel("bound RHS / L2 error squared")
    axes[1].set_title("Certificate bound is safely positive")
    axes[1].legend(fontsize=8)
    axes[1].grid(True, which="both", alpha=0.25)

    fig.suptitle("Fixed collocation loss remains zero while the fill-distance regularity certificate detects hidden oscillations.")
    fig.savefig(path, dpi=180)
    plt.close(fig)


def plot_profiles(path: Path = PROFILES_PNG, m: int = 8, n: int = 3) -> None:
    x = np.linspace(0.0, 1.0, 4001)
    u = np.sin(np.pi * m * n * x) ** 2
    du = np.pi * m * n * np.sin(2.0 * np.pi * m * n * x)
    d2u = 2.0 * (np.pi * m * n) ** 2 * np.cos(2.0 * np.pi * m * n * x)
    left_nodes = np.arange(m) / m

    fig, axes = plt.subplots(1, 2, figsize=(10, 4), constrained_layout=True)
    axes[0].plot(x, u, label=r"$u_n$")
    axes[0].plot(left_nodes, np.zeros_like(left_nodes), "ro", ms=4, label="left collocation nodes")
    axes[0].set_xlabel("x")
    axes[0].set_ylabel("u")
    axes[0].set_title("Wrong solution between fixed nodes")
    axes[0].legend(fontsize=8)
    axes[0].grid(True, alpha=0.25)

    axes[1].plot(x, du, label=r"$u_n'$")
    axes[1].plot(x, d2u / np.max(np.abs(d2u)) * np.max(np.abs(du)), "--", label="scaled curvature")
    axes[1].plot(left_nodes, np.zeros_like(left_nodes), "ro", ms=4, label=r"sampled $u_n'=0$")
    axes[1].set_xlabel("x")
    axes[1].set_ylabel("derivative residual")
    axes[1].set_title("Curvature reveals between-node variation")
    axes[1].legend(fontsize=8)
    axes[1].grid(True, alpha=0.25)

    fig.suptitle("The bad sequence satisfies sampled residual constraints but violates the sampled stability certificate through large between-node curvature.")
    fig.savefig(path, dpi=180)
    plt.close(fig)


def main() -> None:
    rows = build_rows(ms=[4, 8, 16], ns=[1, 2, 4, 8, 16, 32])
    write_csv(rows)
    plot_scaling(rows)
    plot_profiles()
    print(f"wrote {CSV_PATH}")
    print(f"wrote {SCALING_PNG}")
    print(f"wrote {PROFILES_PNG}")


if __name__ == "__main__":
    main()
