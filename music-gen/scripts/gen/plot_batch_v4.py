#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-08-28T18:20:00Z
# cycle: 16
# run_id: run-2026-08-28T040704Z
# agent: worker (clone-1, fork cc548ca0c2e5)
# milestone: M-GEN-1/batch-v4-compound
# ---
"""Plot batch-v4 8-song scoring grid + collision heatmap.

Structural parallel to scripts/gen/plot_batch_v2.py; only the batch
root and figure filenames differ. The heatmap is annotated with the
anchor cross-reference category per (salt, file_kind), so the
CONFIRMS_H0_STRICT verdict is visually reproducible from the figure.

Outputs (default paths):
  * docs/figures/batch_v4_grid.png
  * docs/figures/batch_v4_collision_heatmap.png
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


def _load_xref(batch_root: Path):
    return json.loads((batch_root / "anchor_cross_reference.json").read_text())


def plot_grid(batch_root: Path, out_path: Path) -> None:
    header, rows = _load_summary(batch_root)
    xref = _load_xref(batch_root)

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
    norm = np.zeros_like(data)
    for j in range(data.shape[1]):
        col = data[:, j]
        finite = col[np.isfinite(col)]
        if finite.size == 0:
            continue
        lo, hi = float(finite.min()), float(finite.max())
        norm[:, j] = (col - lo) / (hi - lo) if hi > lo else 0.5

    fig, ax = plt.subplots(figsize=(13, 5.5))
    im = ax.imshow(norm, aspect="auto", cmap="viridis", vmin=0, vmax=1)
    ax.set_xticks(range(len(cols)))
    ax.set_xticklabels([c[1] for c in cols], rotation=40, ha="right", fontsize=9)
    ax.set_yticks(range(len(salts)))

    # Salt label carries the anchor-XREF category (based on musicxml cell).
    per_cell = xref["per_cell"]
    ylabels = []
    for s in salts:
        cat = per_cell[f"salt_{s}/musicxml"]["category"]
        short = {"matches_both": "≡both",
                 "matches_i4_only": "≡i4",
                 "matches_i3_only": "≡i3",
                 "novel": "novel"}[cat]
        ylabels.append(f"salt={s}  [{short}]")
    ax.set_yticklabels(ylabels)

    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            v = data[i, j]
            if np.isnan(v):
                ax.text(j, i, "—", ha="center", va="center", fontsize=8, color="w")
                continue
            txt = f"{v:.2f}" if abs(v) < 100 else f"{v:.0f}"
            ax.text(j, i, txt, ha="center", va="center", fontsize=7,
                    color="white" if norm[i, j] < 0.55 else "black")
    ax.set_title("M-GEN-1/batch-v4-compound (cycle 16) — 8-song scoring grid; "
                 "per-salt anchor-XREF category in brackets")
    fig.colorbar(im, ax=ax, fraction=0.03, pad=0.02, label="col-normalized")
    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=140)
    plt.close(fig)
    print(f"[plot_batch_v4] wrote {out_path}")


def plot_collisions(batch_root: Path, out_path: Path) -> None:
    coll = json.loads((batch_root / "collision_analysis.json").read_text())
    rule_types = coll["rule_types"]
    salts = coll["salts"]

    fig, axes = plt.subplots(1, len(rule_types),
                             figsize=(3.2 * len(rule_types), 3.6),
                             squeeze=False)
    for k, rt in enumerate(rule_types):
        M = np.array(coll["coerced"]["per_rule_type_matrix"][rt])
        Mvis = M.astype(float).copy()
        for i in range(len(salts)):
            Mvis[i, i] = 0.5
        ax = axes[0, k]
        ax.imshow(Mvis, cmap="RdYlGn_r", vmin=0, vmax=1)
        ax.set_xticks(range(len(salts)))
        ax.set_yticks(range(len(salts)))
        ax.set_xticklabels([str(s) for s in salts], fontsize=8)
        ax.set_yticklabels([str(s) for s in salts], fontsize=8)
        for i in range(len(salts)):
            for j in range(len(salts)):
                if i == j:
                    ax.text(j, i, "·", ha="center", va="center",
                            color="grey", fontsize=8)
                elif M[i, j]:
                    ax.text(j, i, "×", ha="center", va="center",
                            color="white", fontsize=10)
        n_pairs = sum(1 for i in range(len(salts))
                      for j in range(i + 1, len(salts)) if M[i, j])
        ax.set_title(f"{rt}\n({n_pairs} collision pairs)", fontsize=10)
        ax.set_xlabel("salt")
        if k == 0:
            ax.set_ylabel("salt")
    total = coll["coerced"]["total_pairwise_collisions"]
    fig.suptitle(
        f"M-GEN-1/batch-v4-compound (cycle 16) — pairwise rule_id collisions "
        f"per rule_type at N=8 (total = {total}); "
        f"I3 augmented ledger + I4 stratified sampler",
        fontsize=11, y=1.02,
    )
    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=140, bbox_inches="tight")
    plt.close(fig)
    print(f"[plot_batch_v4] wrote {out_path}")


def _main(argv):
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--batch-root", type=Path,
                    default=_REPO / "data" / "gen" / "batch_v4")
    ap.add_argument("--figures-dir", type=Path,
                    default=_REPO / "docs" / "figures")
    ap.add_argument("--only", choices=("grid", "collisions", "both"),
                    default="both")
    args = ap.parse_args(argv)

    if args.only in ("grid", "both"):
        out = (Path(os.environ["FIGURE_OUT"])
               if os.environ.get("FIGURE_OUT") and args.only == "grid"
               else args.figures_dir / "batch_v4_grid.png")
        plot_grid(args.batch_root, out)
    if args.only in ("collisions", "both"):
        out = (Path(os.environ["FIGURE_OUT"])
               if os.environ.get("FIGURE_OUT") and args.only == "collisions"
               else args.figures_dir / "batch_v4_collision_heatmap.png")
        plot_collisions(args.batch_root, out)
    return 0


if __name__ == "__main__":
    raise SystemExit(_main(sys.argv[1:]))
