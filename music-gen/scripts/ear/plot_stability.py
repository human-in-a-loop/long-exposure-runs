"""Figures for the M-EAR-1/synthetic-label-stability-audit report.

Emits:
  docs/figures/ear_stability_mae_envelope.png
  docs/figures/ear_stability_tau_matrix.png
"""
# created: 2026-08-28T18:15:00Z  cycle: 22  run_id: run-2026-08-28T040704Z
# agent: worker (clone-2, fork cc548ca0c2e5)  milestone: M-EAR-1/synthetic-label-stability-audit
from __future__ import annotations
from . import _interp  # noqa: F401

import json
import os
from pathlib import Path

os.environ.setdefault("MPLBACKEND", "Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402


REPORT = Path("data/ear/stability_audit/stability_report.json")
OUT_DIR = Path("docs/figures")


def _load():
    return json.loads(REPORT.read_text())


def plot_mae_envelope(rep: dict, out: Path) -> None:
    per_recipe = rep["per_recipe"]
    families = [r["family"] for r in per_recipe]
    maes = [r["mean_mae"] for r in per_recipe]
    fam_colors = {
        "hash-noise": "#666666",
        "linear-projection": "#1f77b4",
        "nonlinear": "#2ca02c",
        "signed-popcount": "#d62728",
    }
    colors = [fam_colors.get(f, "#000000") for f in families]
    envelope = rep["mae_envelope"]
    cycle6 = rep["cycle6_reference"]["mae_mean"]

    fig, ax = plt.subplots(figsize=(8, 4.5), dpi=110)
    xs = np.arange(len(per_recipe))
    ax.bar(xs, maes, color=colors, edgecolor="black", linewidth=0.5,
           label="_nolegend_")
    ax.axhline(envelope["p05"], color="#aa5555", linestyle="--", linewidth=1.0,
               label=f"5th pct = {envelope['p05']:.3f}")
    ax.axhline(envelope["p50"], color="#333333", linestyle="-", linewidth=1.0,
               label=f"50th pct = {envelope['p50']:.3f}")
    ax.axhline(envelope["p95"], color="#aa5555", linestyle="--", linewidth=1.0,
               label=f"95th pct = {envelope['p95']:.3f}")
    ax.axhline(cycle6, color="orange", linewidth=2.0,
               label=f"cycle-6 (PC1+noise) MAE = {cycle6:.3f}")
    ax.set_xticks(xs)
    ax.set_xticklabels([f"r{r['idx']}\n{r['family'][:5]}" for r in per_recipe],
                       fontsize=8)
    ax.set_ylabel("mean 5-fold MAE (K=7 ordinal)")
    ax.set_title("MAE envelope across 10 SHA-256-salted synthetic recipes\n"
                 "C1 verdict: cycle-6 MAE " +
                 ("INSIDE" if rep["criteria"]["C1"]["verdict"] == "PASS" else "OUTSIDE") +
                 f" [5th, 95th] → {rep['criteria']['C1']['verdict']}",
                 fontsize=10)
    ax.legend(loc="upper left", fontsize=8, framealpha=0.9)
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=110)
    plt.close(fig)


def plot_tau_matrix(rep: dict, out: Path) -> None:
    n = rep["n_recipes"]
    M = np.full((n, n), np.nan, dtype=np.float64)
    for p in rep["tau_pairs"]:
        M[p["recipe_i"], p["recipe_j"]] = p["kendall_tau"]
        M[p["recipe_j"], p["recipe_i"]] = p["kendall_tau"]
    for i in range(n):
        M[i, i] = 1.0

    fig, ax = plt.subplots(figsize=(6.5, 5.5), dpi=110)
    im = ax.imshow(M, cmap="RdBu_r", vmin=-1, vmax=1)
    ax.set_xticks(np.arange(n))
    ax.set_yticks(np.arange(n))
    fams = [r["family"][:5] for r in rep["per_recipe"]]
    ax.set_xticklabels([f"r{i}\n{fams[i]}" for i in range(n)], fontsize=7)
    ax.set_yticklabels([f"r{i} {fams[i]}" for i in range(n)], fontsize=7)
    for i in range(n):
        for j in range(n):
            v = M[i, j]
            ax.text(j, i, f"{v:.2f}", ha="center", va="center",
                    fontsize=6, color="black" if abs(v) < 0.4 else "white")
    tau_sum = rep["tau_summary"]
    ax.set_title("Pairwise Kendall τ-b across 10 synthetic-label recipes\n"
                 f"mean = {tau_sum['mean']:.3f}   5th = {tau_sum['p05']:.3f}   "
                 f"min = {tau_sum['min']:.3f}\n"
                 f"C2 verdict: mean τ {'≥' if tau_sum['mean'] >= 0.7 else '<'} 0.7 → "
                 f"{rep['criteria']['C2']['verdict']}",
                 fontsize=10)
    fig.colorbar(im, ax=ax, shrink=0.8, label="Kendall τ-b")
    fig.tight_layout()
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=110)
    plt.close(fig)


def main() -> int:
    rep = _load()
    plot_mae_envelope(rep, OUT_DIR / "ear_stability_mae_envelope.png")
    plot_tau_matrix(rep, OUT_DIR / "ear_stability_tau_matrix.png")
    print(f"wrote {OUT_DIR / 'ear_stability_mae_envelope.png'}")
    print(f"wrote {OUT_DIR / 'ear_stability_tau_matrix.png'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
