#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-08-28T23:30:00Z
# cycle: 25
# run_id: run-2026-08-28T040704Z
# agent: worker (clone-0, fork dc8cba4b79eb)
# milestone: M-GEN-1/batch-v6-unconditioned-n16
# ---
"""Render batch-v6 figures: grid, collision_heatmap, attribution."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

os.environ.setdefault("PYTHONHASHSEED", "0")
os.environ["MPLBACKEND"] = "Agg"
assert sys.executable == "/usr/bin/python3", sys.executable

_REPO = Path(__file__).resolve().parent.parent.parent

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

BATCH_ROOT = _REPO / "data" / "gen" / "batch_v6"
FIG_DIR = _REPO / "docs" / "figures"
RULE_TYPES = ("harmonic", "rhythmic", "melodic", "form", "arrangement")


def plot_grid(coll, verdict, out_path):
    fig, ax = plt.subplots(figsize=(11, 6))
    ax.axis("off")
    header = ["salt"] + list(RULE_TYPES)
    rows = []
    # We reload sampling_manifests for the coerced rule_ids.
    coerced = {}
    for s in range(16):
        sm = json.loads((BATCH_ROOT / f"song_{s}" / "sampling_manifest.json").read_text())
        coerced[s] = dict(sm["chosen_rule_ids"])
    for s in range(16):
        row = [str(s)]
        for rt in RULE_TYPES:
            rid = coerced[s][rt]
            row.append(rid[:10])
        rows.append(row)
    tbl = ax.table(cellText=rows, colLabels=header, loc="center", cellLoc="center")
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(8)
    tbl.scale(1, 1.2)
    plt.suptitle(f"batch-v6-unconditioned-n16 grid — cycle-13 sampler, N=16\n"
                 f"verdict={verdict['verdict']}  pairs={verdict['observed_pairs']}  "
                 f"{{form,arr}}={verdict['form_arrangement_fraction']:.2f}  "
                 f"{{K=15 union}}={verdict['k15_union_fraction']:.2f}",
                 fontsize=10)
    plt.tight_layout()
    plt.savefig(out_path, dpi=120, bbox_inches="tight")
    plt.close()


def plot_collision_heatmap(coll, out_path):
    # Union heatmap: cell (i,j) = number of rule_types matching between salts i, j.
    n = coll["n_salts"]
    matrices = coll["coerced"]["per_rule_type_matrix"]
    U = np.zeros((n, n), dtype=int)
    for rt in RULE_TYPES:
        U += np.array(matrices[rt], dtype=int)
    np.fill_diagonal(U, 0)  # ignore self-comparisons

    fig, axes = plt.subplots(1, 6, figsize=(24, 4), gridspec_kw={"width_ratios": [1]*5 + [1]})
    for k, rt in enumerate(RULE_TYPES):
        M = np.array(matrices[rt], dtype=int)
        np.fill_diagonal(M, 0)
        ax = axes[k]
        im = ax.imshow(M, cmap="Blues", vmin=0, vmax=1)
        ax.set_title(f"{rt}\n(K={coll['K_distribution'][rt]})", fontsize=10)
        ax.set_xlabel("s_j")
        if k == 0:
            ax.set_ylabel("s_i")
        ax.set_xticks(range(n))
        ax.set_yticks(range(n))
        ax.tick_params(labelsize=7)
    ax = axes[5]
    im = ax.imshow(U, cmap="viridis", vmin=0)
    ax.set_title("union count (any_rt)", fontsize=10)
    ax.set_xlabel("s_j")
    ax.set_xticks(range(n))
    ax.set_yticks(range(n))
    ax.tick_params(labelsize=7)
    fig.colorbar(im, ax=ax, shrink=0.75)
    plt.suptitle("batch-v6 collision heatmap (per rule_type + union) — N=16", fontsize=11)
    plt.tight_layout()
    plt.savefig(out_path, dpi=110, bbox_inches="tight")
    plt.close()


def plot_attribution(coll, verdict, out_path):
    prim = verdict["attribution"]
    anyrt = verdict["attribution_any_rt"]
    x = np.arange(len(RULE_TYPES))
    w = 0.4
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.bar(x - w/2, [prim[rt] for rt in RULE_TYPES], w, label="primary (cycle-13 tiebreak)")
    ax.bar(x + w/2, [anyrt[rt] for rt in RULE_TYPES], w, label="any_rt (multi-count)")
    ax.set_xticks(x)
    ax.set_xticklabels([f"{rt}\nK={verdict['K_distribution'][rt]}" for rt in RULE_TYPES])
    ax.set_ylabel("collision pair count")
    ax.set_title(f"batch-v6 per-rule_type attribution (N=16, pairs={verdict['observed_pairs']})\n"
                 f"verdict={verdict['verdict']}  {{form,arr}}={verdict['form_arrangement_fraction']:.2%}  "
                 f"{{K=15 union}}={verdict['k15_union_fraction']:.2%}")
    ax.axhline(y=0, color="k", linewidth=0.5)
    ax.legend()
    # Reference lines: pigeonhole strict-forbidden zone (K>=N) shading.
    for i, rt in enumerate(RULE_TYPES):
        if verdict["K_distribution"][rt] >= 16:
            ax.axvspan(i-0.45, i+0.45, alpha=0.08, color="red")
    ax.text(0.02, 0.98, "red band = pigeonhole-forbidden (K≥N)",
            transform=ax.transAxes, va="top", fontsize=8, color="red")
    plt.tight_layout()
    plt.savefig(out_path, dpi=120, bbox_inches="tight")
    plt.close()


def _main(argv):
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    coll = json.loads((BATCH_ROOT / "collision_analysis.json").read_text())
    verdict = json.loads((BATCH_ROOT / "hypothesis_verdict.json").read_text())
    plot_grid(coll, verdict, FIG_DIR / "batch_v6_grid.png")
    plot_collision_heatmap(coll, FIG_DIR / "batch_v6_collision_heatmap.png")
    plot_attribution(coll, verdict, FIG_DIR / "batch_v6_attribution.png")
    for name in ("batch_v6_grid", "batch_v6_collision_heatmap", "batch_v6_attribution"):
        print(f"[plot_batch_v6] wrote {FIG_DIR / (name + '.png')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main(sys.argv[1:]))
