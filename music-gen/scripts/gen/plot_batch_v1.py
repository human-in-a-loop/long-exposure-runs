#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-08-28T12:20:00Z
# cycle: 11
# run_id: run-2026-08-28T040704Z
# agent: worker (clone-0, fork ddd71e9bdb0e)
# milestone: M-GEN-1/batch-v1
# ---
"""5-song × metrics grid figure for M-GEN-1/batch-v1.

Reads data/gen/batch_v1/summary.tsv; produces
docs/figures/gen_batch_v1_grid.png.

No PRNG. Deterministic matplotlib backend (Agg).
"""
from __future__ import annotations

import csv
import os
import sys
from pathlib import Path

assert sys.executable == "/usr/bin/python3", sys.executable
os.environ.setdefault("MPLBACKEND", "Agg")

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


_REPO = Path(__file__).resolve().parent.parent.parent
DEFAULT_TSV = _REPO / "data" / "gen" / "batch_v1" / "summary.tsv"
DEFAULT_OUT = _REPO / "docs" / "figures" / "gen_batch_v1_grid.png"

_ROWS = [
    ("Heuristics (mess-scale ∈ [0,1])",
     [("heur_melody", "melody"),
      ("heur_timbre", "timbre"),
      ("heur_form", "form"),
      ("heur_dynamics", "dynamics")]),
    ("Meta-tracker",
     [("meta_dynamics_trajectory_db", "dyn. traj. dB"),
      ("meta_form_coherence", "form coherence")]),
    ("Texture panel (bare vs effects)",
     [("panel_mel_l1_db", "mel L1 dB"),
      ("panel_spectral_centroid_rmse_hz", "centroid RMSE Hz"),
      ("panel_rms_env_rmse", "RMS env RMSE"),
      ("panel_lufs_m_rmse_lu", "LUFS-M RMSE LU"),
      ("panel_embedding_cosine", "VGGish cos")]),
    ("Ear (uncalibrated)",
     [("ear_prediction", "prediction 1-7"),
      ("n_coercions", "# coercions")]),
]


def _read(tsv: Path):
    rows = list(csv.DictReader(open(tsv), delimiter="\t"))
    salts = [int(r["salt"]) for r in rows]
    return rows, salts


def _plot(tsv: Path, out: Path) -> Path:
    rows, salts = _read(tsv)
    n_rows = sum(len(cols) for _, cols in _ROWS)
    fig, axes = plt.subplots(
        n_rows, 1, figsize=(9.0, max(2.0, n_rows * 1.05)),
        sharex=True, constrained_layout=True,
    )
    if n_rows == 1:
        axes = [axes]

    xs = np.arange(len(salts))
    ax_i = 0
    for panel_title, cols in _ROWS:
        for j, (key, label) in enumerate(cols):
            ax = axes[ax_i]
            vals = []
            for r in rows:
                v = r.get(key, "")
                try:
                    vals.append(float(v))
                except (ValueError, TypeError):
                    vals.append(np.nan)
            ax.bar(xs, vals, color="#4a6fa5", edgecolor="#1c2b3f", width=0.6)
            for x, v in zip(xs, vals):
                if np.isfinite(v):
                    ax.text(x, v, f"{v:.3g}", ha="center", va="bottom", fontsize=7)
            if j == 0:
                ax.set_title(panel_title, fontsize=10, loc="left")
            ax.set_ylabel(label, fontsize=8)
            ax.grid(axis="y", linestyle=":", alpha=0.5)
            ax.set_xticks(xs)
            ax.set_xticklabels([f"salt={s}" for s in salts])
            ax_i += 1
    axes[-1].set_xlabel("salt", fontsize=9)
    fig.suptitle(
        "M-GEN-1/batch-v1: 5-song grid (salts 0..4, post-coherence-gate)\n"
        "Ear is uncalibrated — synthetic labels only",
        fontsize=11,
    )
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=110)
    plt.close(fig)
    return out


def _main(argv):
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--tsv", type=Path, default=DEFAULT_TSV)
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = ap.parse_args(argv)
    p = _plot(args.tsv, args.out)
    print(f"[plot_batch_v1] wrote {p}")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main(sys.argv[1:]))
