# created: 2026-05-14T03:20:00Z
# cycle: 1
# run_id: run-2026-05-14T030813Z
# agent: worker
# milestone: M-1
"""Numerical scaling checks for residual-minimization counterexamples."""

from __future__ import annotations

import math
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
CSV_PATH = DATA / "triage_residual_scaling.csv"
SCALING_PNG = DATA / "triage_residual_scaling.png"
PROFILES_PNG = DATA / "triage_bad_sequence_profiles.png"


def collocation_row(n: int, m: int = 8) -> dict[str, float | int | str]:
    """Fixed-node blind spot: sampled residual zero, global error constant."""
    return {
        "candidate": "C1_collocation_blind_spot",
        "n": n,
        "residual_loss": 0.0,
        "error_norm": math.sqrt(3.0 / 8.0),
        "certificate_norm": (math.pi * m * n) ** 2 / 2.0,
    }


def trace_leakage_row(n: int) -> dict[str, float | int | str]:
    """Underweighted trace: residual plus shrinking boundary penalty vanishes."""
    return {
        "candidate": "C2_underweighted_trace",
        "n": n,
        "residual_loss": 1.0 / (n * n),
        "error_norm": 1.0,
        "certificate_norm": 1.0,
    }


def build_rows(ns: list[int]) -> list[dict[str, float | int | str]]:
    rows: list[dict[str, float | int | str]] = []
    for n in ns:
        rows.append(collocation_row(n))
        rows.append(trace_leakage_row(n))
    return rows


def write_csv(rows: list[dict[str, float | int | str]], path: Path = CSV_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    header = ["candidate", "n", "residual_loss", "error_norm", "certificate_norm"]
    with path.open("w", encoding="utf-8") as f:
        f.write(",".join(header) + "\n")
        for row in rows:
            f.write(",".join(str(row[key]) for key in header) + "\n")


def plot_scaling(rows: list[dict[str, float | int | str]], path: Path = SCALING_PNG) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(10, 4), constrained_layout=True)
    for candidate, label in [
        ("C1_collocation_blind_spot", "C1 sampled blind spot"),
        ("C2_underweighted_trace", "C2 trace leakage"),
    ]:
        subset = [r for r in rows if r["candidate"] == candidate]
        ns = np.array([float(r["n"]) for r in subset])
        residual = np.array([float(r["residual_loss"]) for r in subset])
        error = np.array([float(r["error_norm"]) for r in subset])
        cert = np.array([float(r["certificate_norm"]) for r in subset])
        axes[0].loglog(ns, np.maximum(residual, 1e-16), "o-", label=f"{label}: loss")
        axes[0].loglog(ns, error, "s--", label=f"{label}: error")
        axes[1].loglog(ns, cert, "o-", label=label)

    axes[0].set_xlabel("n")
    axes[0].set_ylabel("loss or L2 error")
    axes[0].set_title("Vanishing residual objective, nonvanishing error")
    axes[0].legend(fontsize=8)
    axes[0].grid(True, which="both", alpha=0.25)
    axes[1].set_xlabel("n")
    axes[1].set_ylabel("certificate norm")
    axes[1].set_title("Certificate detects the bad sequences")
    axes[1].legend(fontsize=8)
    axes[1].grid(True, which="both", alpha=0.25)
    fig.suptitle("Residual loss can vanish while physical error remains bounded for explicit approximating sequences.")
    fig.savefig(path, dpi=180)
    plt.close(fig)


def plot_profiles(path: Path = PROFILES_PNG, m: int = 8, n: int = 3) -> None:
    x = np.linspace(0.0, 1.0, 4001)
    u_collocation = np.sin(np.pi * m * n * x) ** 2
    du_collocation = np.pi * m * n * np.sin(2.0 * np.pi * m * n * x)
    nodes = np.arange(m + 1) / m

    fig, axes = plt.subplots(1, 2, figsize=(10, 4), constrained_layout=True)
    axes[0].plot(x, u_collocation, label=r"$u_n(x)=\sin^2(\pi mnx)$")
    axes[0].plot(x, np.zeros_like(x), "k--", label=r"$u^\star=0$")
    axes[0].plot(nodes, np.zeros_like(nodes), "ro", ms=4, label="collocation nodes")
    axes[0].set_title("C1 profile hides between fixed nodes")
    axes[0].set_xlabel("x")
    axes[0].set_ylabel("u")
    axes[0].legend(fontsize=8)
    axes[0].grid(True, alpha=0.25)

    axes[1].plot(x, du_collocation, label=r"$u_n'(x)$")
    axes[1].plot(nodes, np.zeros_like(nodes), "ro", ms=4, label=r"sampled $u_n'=0$")
    axes[1].set_title("Sampled residual misses oscillatory derivative")
    axes[1].set_xlabel("x")
    axes[1].set_ylabel("derivative residual")
    axes[1].legend(fontsize=8)
    axes[1].grid(True, alpha=0.25)
    fig.suptitle("The wrong sequence hides from the training residual by localization, oscillation, or sampling blind spots.")
    fig.savefig(path, dpi=180)
    plt.close(fig)


def main() -> None:
    ns = [1, 2, 4, 8, 16, 32, 64]
    rows = build_rows(ns)
    write_csv(rows)
    plot_scaling(rows)
    plot_profiles()
    print(f"wrote {CSV_PATH}")
    print(f"wrote {SCALING_PNG}")
    print(f"wrote {PROFILES_PNG}")


if __name__ == "__main__":
    main()
