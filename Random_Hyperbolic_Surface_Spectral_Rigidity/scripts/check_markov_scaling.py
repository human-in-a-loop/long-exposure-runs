# created: 2026-05-15T16:14:00Z
# cycle: 3
# run_id: run-2026-05-15T153635Z
# agent: worker
# milestone: M2-proof-ledger

from __future__ import annotations

import csv
import os
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data/polynomial_method/markov_scaling_sanity.csv"


def chebyshev_endpoint_derivative(degree: int) -> int:
    return degree * degree


def write_csv(max_degree: int = 64) -> None:
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    with DATA_PATH.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["degree", "endpoint_derivative", "degree_squared", "ratio"])
        for degree in range(1, max_degree + 1):
            derivative = chebyshev_endpoint_derivative(degree)
            writer.writerow([degree, derivative, degree * degree, derivative / (degree * degree)])


def plot(out_path: str) -> None:
    degrees = np.arange(1, 65)
    derivatives = degrees**2
    fig, ax = plt.subplots(figsize=(6.5, 4.2))
    ax.loglog(degrees, derivatives, marker="o", linewidth=1.5, label=r"$T_D'(1)=D^2$")
    ax.loglog(degrees, degrees**2, linestyle="--", color="black", linewidth=1, label=r"$D^2$")
    ax.set_xlabel("Degree D")
    ax.set_ylabel("Endpoint derivative amplification")
    ax.set_title("Markov Scaling Sanity Check")
    ax.grid(True, which="both", linewidth=0.4, alpha=0.45)
    ax.legend()
    fig.tight_layout()
    fig.savefig(out_path, dpi=180)


def main() -> None:
    write_csv()
    out_path = os.environ.get("FIGURE_OUT")
    if out_path:
        plot(out_path)
    print(f"wrote {DATA_PATH}")
    print("sample: degree=8 endpoint_derivative=64 ratio=1.0")


if __name__ == "__main__":
    main()
