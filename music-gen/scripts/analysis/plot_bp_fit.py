#!/usr/bin/env python3
"""Render the two figures for docs/collision_generation_model_birthday_paradox.md.

  docs/figures/collision_model_bp_fit.png
      6-point predicted vs observed scatter with y=x reference line.
      Batch labels annotated.  Stratified batches drawn as open markers
      at (0, 0) with a note.

  docs/figures/collision_model_bp_per_rule_type_v6.png
      5-bar predicted (scaled) vs observed for batch-v6 per rule_type.

Interpreter-guarded /usr/bin/python3.  No PRNG.  No sidecar_nonfactor.
"""
from __future__ import annotations

import json
import pathlib
import sys

assert sys.executable == "/usr/bin/python3", sys.executable

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = pathlib.Path(__file__).resolve().parents[2]
FITS = json.loads((ROOT / "data" / "collision_model" / "bp_fit_results.json").read_text())
FIG_DIR = ROOT / "docs" / "figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)


def plot_scatter():
    per = FITS["per_batch"]
    fig, ax = plt.subplots(figsize=(6.5, 5.5))
    xs_uc, ys_uc, labels_uc = [], [], []
    xs_st, ys_st, labels_st = [], [], []
    for b in per:
        if b["sampler"] == "stratified":
            xs_st.append(b["predicted_total_pure"])
            ys_st.append(b["observed_total"])
            labels_st.append(b["batch_id"])
        else:
            xs_uc.append(b["predicted_total_pure"])
            ys_uc.append(b["observed_total"])
            labels_uc.append(b["batch_id"])
    lim = max(max(xs_uc + [1]), max(ys_uc + [1])) * 1.1
    ax.plot([0, lim], [0, lim], "k--", alpha=0.5, label="y=x")
    ax.scatter(xs_uc, ys_uc, s=80, c="C0", zorder=3, label="unconditioned sampler")
    ax.scatter(xs_st, ys_st, s=80, facecolors="none", edgecolors="C1", zorder=3, label="stratified sampler (pred=0)")
    for x, y, l in zip(xs_uc, ys_uc, labels_uc):
        ax.annotate(l, (x, y), textcoords="offset points", xytext=(6, -4), fontsize=8)
    for x, y, l in zip(xs_st, ys_st, labels_st):
        ax.annotate(l, (x, y), textcoords="offset points", xytext=(6, 6), fontsize=8, color="C1")
    ax.set_xlabel("BP-pure predicted total pairs")
    ax.set_ylabel("Observed total pairs")
    ax.set_title(
        f"BP fit: alpha_hat={FITS['alpha_hat']:.3f}  R2_pure={FITS['r2_pure']:.3f}  R2_scaled={FITS['r2_scaled']:.3f}"
    )
    ax.legend(loc="upper left", fontsize=8)
    ax.grid(alpha=0.3)
    out = FIG_DIR / "collision_model_bp_fit.png"
    fig.tight_layout()
    fig.savefig(out, dpi=140)
    print(f"wrote {out}")


def plot_shape():
    shape = FITS["shape_fits"]["batch_v6"]
    rt = shape["rule_types"]
    obs = shape["observed"]
    pred = shape["predicted_scaled"]
    x = list(range(len(rt)))
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    w = 0.38
    ax.bar([xi - w / 2 for xi in x], obs, width=w, label="observed", color="C0")
    ax.bar([xi + w / 2 for xi in x], pred, width=w, label="BP-scaled predicted", color="C1", alpha=0.85)
    ax.set_xticks(x)
    ax.set_xticklabels(rt)
    ax.set_xlabel("rule_type")
    ax.set_ylabel("pair count")
    ax.set_title(
        f"batch-v6 per-rule_type: shape R2_scaled={shape['r2_shape_scaled']:.3f} (SHAPE_REFUTES)"
    )
    ax.legend(fontsize=9)
    ax.grid(axis="y", alpha=0.3)
    out = FIG_DIR / "collision_model_bp_per_rule_type_v6.png"
    fig.tight_layout()
    fig.savefig(out, dpi=140)
    print(f"wrote {out}")


if __name__ == "__main__":  # pragma: no cover
    plot_scatter()
    plot_shape()
