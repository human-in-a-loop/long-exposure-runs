#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-08-28T22:00:00Z
# cycle: 23
# run_id: run-2026-08-28T040704Z
# agent: worker (clone-0, fork 3fbd8c1ab57c)
# milestone: M-GEN-1/batch-v5-n16
# ---
"""Plot batch-v5-n16 16-song scoring grid + collision heatmap + attribution.

Outputs (default paths):
  * docs/figures/batch_v5_n16_grid.png
  * docs/figures/batch_v5_n16_collision_heatmap.png
  * docs/figures/batch_v5_n16_attribution.png
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

os.environ.setdefault("PYTHONHASHSEED", "0")
assert sys.executable == "/usr/bin/python3", sys.executable

_REPO = Path(__file__).resolve().parent.parent.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def _load_summary(batch_root: Path):
    lines = (batch_root / "summary.tsv").read_text().strip().splitlines()
    header = lines[0].split("\t")
    rows = [dict(zip(header, ln.split("\t"))) for ln in lines[1:]]
    return header, rows


def plot_grid(batch_root: Path, out_path: Path) -> None:
    header, rows = _load_summary(batch_root)
    cols = [
        ("heur_melody",   "melody"),
        ("heur_timbre",   "timbre"),
        ("heur_form",     "form"),
        ("heur_dynamics", "dynamics"),
        ("meta_dynamics_trajectory_db", "meta_dyn_traj_dB"),
        ("meta_form_coherence",         "meta_form_coh"),
        ("ear_prediction",              "ear_pred"),
        ("panel_mel_l1_db",             "mel_L1_dB"),
        ("panel_spectral_centroid_rmse_hz", "sc_RMSE_Hz"),
        ("panel_rms_env_rmse",          "rms_env_RMSE"),
        ("panel_lufs_m_rmse_lu",        "LUFS_M_RMSE"),
        ("panel_embedding_cosine",      "emb_cos"),
    ]
    salts = [int(r["salt"]) for r in rows]
    data = np.full((len(salts), len(cols)), np.nan)
    for i, r in enumerate(rows):
        for j, (k, _) in enumerate(cols):
            v = r.get(k, "")
            if v == "" or v is None:
                continue
            try:
                data[i, j] = float(v)
            except ValueError:
                pass
    norm = np.zeros_like(data)
    for j in range(data.shape[1]):
        col = data[:, j]
        finite = col[np.isfinite(col)]
        if finite.size == 0:
            continue
        lo, hi = float(finite.min()), float(finite.max())
        norm[:, j] = (col - lo) / (hi - lo) if hi > lo else 0.5

    fig, ax = plt.subplots(figsize=(13, 8))
    im = ax.imshow(norm, aspect="auto", cmap="viridis", vmin=0, vmax=1)
    ax.set_xticks(range(len(cols)))
    ax.set_xticklabels([c[1] for c in cols], rotation=40, ha="right", fontsize=9)
    ax.set_yticks(range(len(salts)))
    # Salts 0..7 tagged as "≡v4" (anchor-regression proven byte-identical).
    ylabels = [f"salt={s}  [{'≡v4' if s < 8 else 'new'}]" for s in salts]
    ax.set_yticklabels(ylabels)
    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            v = data[i, j]
            if np.isnan(v):
                ax.text(j, i, "—", ha="center", va="center",
                        fontsize=7, color="w")
                continue
            txt = f"{v:.2f}" if abs(v) < 100 else f"{v:.0f}"
            ax.text(j, i, txt, ha="center", va="center", fontsize=6,
                    color="white" if norm[i, j] < 0.55 else "black")
    ax.set_title("M-GEN-1/batch-v5-n16 (cycle 23) — 16-song scoring grid; "
                 "salts 0..7 byte-identical to batch-v4")
    fig.colorbar(im, ax=ax, fraction=0.03, pad=0.02, label="col-normalized")
    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=140)
    plt.close(fig)
    print(f"[plot_batch_v5] wrote {out_path}")


def plot_collisions(batch_root: Path, out_path: Path) -> None:
    coll = json.loads((batch_root / "collision_analysis.json").read_text())
    rule_types = coll["rule_types"]
    salts = coll["salts"]
    n = len(salts)

    fig, axes = plt.subplots(1, len(rule_types),
                             figsize=(3.6 * len(rule_types), 4.0),
                             squeeze=False)
    for k, rt in enumerate(rule_types):
        M = np.array(coll["coerced"]["per_rule_type_matrix"][rt])
        Mvis = M.astype(float).copy()
        for i in range(n):
            Mvis[i, i] = 0.5
        ax = axes[0, k]
        ax.imshow(Mvis, cmap="RdYlGn_r", vmin=0, vmax=1)
        ax.set_xticks(range(n))
        ax.set_yticks(range(n))
        ax.set_xticklabels([str(s) for s in salts], fontsize=7)
        ax.set_yticklabels([str(s) for s in salts], fontsize=7)
        for i in range(n):
            for j in range(n):
                if i == j:
                    ax.text(j, i, "·", ha="center", va="center",
                            color="grey", fontsize=7)
                elif M[i, j]:
                    ax.text(j, i, "×", ha="center", va="center",
                            color="white", fontsize=8)
        n_pairs = sum(1 for i in range(n)
                      for j in range(i + 1, n) if M[i, j])
        K = {"harmonic": 20, "rhythmic": 15, "melodic": 15,
             "form": 15, "arrangement": 15}[rt]
        headline = f"{rt}  K={K}\n({n_pairs} collision pairs)"
        ax.set_title(headline, fontsize=10,
                     color=("crimson" if rt in ("form", "arrangement") else "black"))
        ax.set_xlabel("salt")
        if k == 0:
            ax.set_ylabel("salt")
    total = coll["coerced"]["total_pairwise_collisions"]
    fig.suptitle(
        f"M-GEN-1/batch-v5-n16 (cycle 23) — pairwise rule_id collisions per "
        f"rule_type at N=16 (total pairs = {total}); "
        f"I3 augmented ledger + I4 stratified sampler; K_form=K_arrangement=15<N",
        fontsize=11, y=1.02,
    )
    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=140, bbox_inches="tight")
    plt.close(fig)
    print(f"[plot_batch_v5] wrote {out_path}")


def plot_attribution(batch_root: Path, out_path: Path) -> None:
    coll = json.loads((batch_root / "collision_analysis.json").read_text())
    rule_types = coll["rule_types"]
    primary = [coll["coerced"]["primary_histogram_tiebreak"][rt]
               for rt in rule_types]
    any_rt = [coll["coerced"]["histogram_any_rt"][rt] for rt in rule_types]
    total = coll["coerced"]["total_pairwise_collisions"]
    frac = coll["coerced"]["form_arrangement_primary_fraction"]

    fig, ax = plt.subplots(figsize=(9, 4.6))
    xpos = np.arange(len(rule_types))
    w = 0.36
    b1 = ax.bar(xpos - w/2, primary, w, label="primary (tiebreak)",
                color=["#d62728" if rt in ("form", "arrangement") else "#7f7f7f"
                       for rt in rule_types])
    b2 = ax.bar(xpos + w/2, any_rt, w, label="any-rt (multi-count)",
                color=["#ff9896" if rt in ("form", "arrangement") else "#c7c7c7"
                       for rt in rule_types])
    for b in list(b1) + list(b2):
        h = b.get_height()
        ax.text(b.get_x() + b.get_width()/2, h + 0.03,
                str(int(h)), ha="center", va="bottom", fontsize=9)
    ax.set_xticks(xpos)
    ax.set_xticklabels(rule_types)
    ax.set_ylabel("collision pair count")
    ax.set_title(
        f"M-GEN-1/batch-v5-n16 — per-rule_type collision attribution at N=16\n"
        f"total pairs = {total};  {{form,arrangement}} primary fraction = {frac:.3f}"
    )
    # Rubric threshold lines (in count units) require total > 0.
    if total > 0:
        ax.axhline(0.90 * total, color="green", linestyle="--", linewidth=1,
                   alpha=0.6, label="0.90 × total (CONFIRMS_CONSTRUCTION)")
        ax.axhline(0.60 * total, color="orange", linestyle="--", linewidth=1,
                   alpha=0.6, label="0.60 × total (PARTIAL_CONFIRM boundary)")
    ax.legend(fontsize=8, loc="upper right")
    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=140)
    plt.close(fig)
    print(f"[plot_batch_v5] wrote {out_path}")


def _main(argv):
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--batch-root", type=Path,
                    default=_REPO / "data" / "gen" / "batch_v5_n16")
    ap.add_argument("--figures-dir", type=Path,
                    default=_REPO / "docs" / "figures")
    ap.add_argument("--only", choices=("grid", "collisions", "attribution", "all"),
                    default="all")
    args = ap.parse_args(argv)

    if args.only in ("grid", "all"):
        plot_grid(args.batch_root, args.figures_dir / "batch_v5_n16_grid.png")
    if args.only in ("collisions", "all"):
        plot_collisions(args.batch_root,
                        args.figures_dir / "batch_v5_n16_collision_heatmap.png")
    if args.only in ("attribution", "all"):
        plot_attribution(args.batch_root,
                         args.figures_dir / "batch_v5_n16_attribution.png")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main(sys.argv[1:]))
