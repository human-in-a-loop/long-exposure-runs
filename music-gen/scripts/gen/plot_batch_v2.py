#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-08-28T14:10:00Z
# cycle: 13
# run_id: run-2026-08-28T040704Z
# agent: worker (clone-0, fork 54a6c185816e)
# milestone: M-GEN-1/batch-v2
# ---
"""Plot batch_v2 8-song scoring grid + collision heatmap.

Two output figures (paths taken from FIGURE_OUT env var when invoked
via `figure plot ...`, else defaults under docs/figures/):
  * docs/figures/gen_batch_v2_grid.png
  * docs/figures/gen_batch_v2_collisions.png
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


def plot_grid(batch_root: Path, out_path: Path) -> None:
    """Rows = songs 0..7, columns = heuristic + meta + ear + panel numbers.

    All numeric columns rendered as a heatmap; NaN cells shown grey.
    """
    header, rows = _load_summary(batch_root)
    # Choose columns to render.
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

    # Column-wise normalization for the heatmap.
    norm = np.zeros_like(data)
    for j in range(data.shape[1]):
        col = data[:, j]
        finite = col[np.isfinite(col)]
        if finite.size == 0:
            continue
        lo, hi = float(finite.min()), float(finite.max())
        if hi - lo > 0:
            norm[:, j] = (col - lo) / (hi - lo)
        else:
            norm[:, j] = 0.5

    fig, ax = plt.subplots(figsize=(12, 5.5))
    im = ax.imshow(norm, aspect="auto", cmap="viridis", vmin=0, vmax=1)
    ax.set_xticks(range(len(cols)))
    ax.set_xticklabels([c[1] for c in cols], rotation=40, ha="right", fontsize=9)
    ax.set_yticks(range(len(salts)))
    ax.set_yticklabels([f"salt={s}" for s in salts])
    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            v = data[i, j]
            if np.isnan(v):
                ax.text(j, i, "—", ha="center", va="center", fontsize=8, color="w")
                continue
            txt = f"{v:.2f}" if abs(v) < 100 else f"{v:.0f}"
            ax.text(j, i, txt, ha="center", va="center", fontsize=7,
                    color="white" if norm[i, j] < 0.55 else "black")
    ax.set_title("M-GEN-1/batch-v2 (cycle 13) — 8-song scoring grid "
                 "(columns col-normalized; annotations show raw values)")
    fig.colorbar(im, ax=ax, fraction=0.03, pad=0.02, label="col-normalized")
    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=140)
    plt.close(fig)
    print(f"[plot_batch_v2] wrote {out_path}")


def plot_collisions(batch_root: Path, out_path: Path) -> None:
    coll = json.loads((batch_root / "collision_analysis.json").read_text())
    rule_types = coll["rule_types"]
    salts = coll["salts"]

    fig, axes = plt.subplots(1, len(rule_types), figsize=(3.2 * len(rule_types), 3.6),
                              squeeze=False)
    for k, rt in enumerate(rule_types):
        M = np.array(coll["coerced"]["per_rule_type_matrix"][rt])
        # Diagonal is trivially 1; suppress by masking for visual clarity.
        Mvis = M.astype(float).copy()
        for i in range(len(salts)):
            Mvis[i, i] = 0.5
        ax = axes[0, k]
        im = ax.imshow(Mvis, cmap="RdYlGn_r", vmin=0, vmax=1)
        ax.set_xticks(range(len(salts)))
        ax.set_yticks(range(len(salts)))
        ax.set_xticklabels([str(s) for s in salts], fontsize=8)
        ax.set_yticklabels([str(s) for s in salts], fontsize=8)
        for i in range(len(salts)):
            for j in range(len(salts)):
                if i == j:
                    ax.text(j, i, "·", ha="center", va="center", color="grey", fontsize=8)
                elif M[i, j]:
                    ax.text(j, i, "×", ha="center", va="center", color="white", fontsize=10)
        # Salt=4 row/col highlight.
        ax.axhline(4 - 0.5, color="cyan", lw=0.8)
        ax.axhline(4 + 0.5, color="cyan", lw=0.8)
        ax.axvline(4 - 0.5, color="cyan", lw=0.8)
        ax.axvline(4 + 0.5, color="cyan", lw=0.8)
        n_pairs = sum(1 for i in range(len(salts)) for j in range(i+1, len(salts))
                       if M[i, j])
        ax.set_title(f"{rt}\n({n_pairs} collision pairs)", fontsize=10)
        ax.set_xlabel("salt")
        if k == 0:
            ax.set_ylabel("salt")
    total = coll["coerced"]["total_pairwise_collisions"]
    fig.suptitle(f"M-GEN-1/batch-v2 (cycle 13) — pairwise rule_id collisions "
                 f"per rule_type at N=8 (total = {total}); "
                 f"salt=4 highlighted (cyan)", fontsize=11, y=1.02)
    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=140, bbox_inches="tight")
    plt.close(fig)
    print(f"[plot_batch_v2] wrote {out_path}")


def _load_summary(batch_root: Path):
    lines = (batch_root / "summary.tsv").read_text().strip().splitlines()
    header = lines[0].split("\t")
    rows = []
    for ln in lines[1:]:
        vals = ln.split("\t")
        rows.append(dict(zip(header, vals)))
    return header, rows


def _main(argv):
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--batch-root", type=Path,
                    default=_REPO / "data" / "gen" / "batch_v2")
    ap.add_argument("--figures-dir", type=Path,
                    default=_REPO / "docs" / "figures")
    ap.add_argument("--only", choices=("grid", "collisions", "both"), default="both")
    args = ap.parse_args(argv)

    if args.only in ("grid", "both"):
        out = Path(os.environ.get("FIGURE_OUT")) if os.environ.get("FIGURE_OUT") and args.only == "grid" \
              else (args.figures_dir / "gen_batch_v2_grid.png")
        plot_grid(args.batch_root, out)
    if args.only in ("collisions", "both"):
        out = Path(os.environ.get("FIGURE_OUT")) if os.environ.get("FIGURE_OUT") and args.only == "collisions" \
              else (args.figures_dir / "gen_batch_v2_collisions.png")
        plot_collisions(args.batch_root, out)
    return 0


if __name__ == "__main__":
    raise SystemExit(_main(sys.argv[1:]))
