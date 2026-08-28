#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-08-28T11:00:00Z
# cycle: 9
# run_id: run-2026-08-28T040704Z
# agent: worker
# milestone: M-TEX-1/stage-by-stage
# ---
"""Three-sub-panel bar chart for the M-TEX-1/panel × three-stage matrix.

Renders one figure with three horizontally-arranged sub-panels, one per
family (spectral / envelope / embedding). Within each sub-panel the
grouped bars are the three ordered pairs on the x-axis; each family's
distance keys are the grouped bars.

Reads the 24-number TSV from `data/tex/stage_by_stage_<seed>.tsv` and
writes to `docs/figures/tex_stage_by_stage_families.png`.

NO aggregate is computed or plotted.
"""
from __future__ import annotations

import argparse
import csv
import os
import sys
from pathlib import Path

assert sys.executable == "/usr/bin/python3", sys.executable

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


PAIR_LABELS = ("orig↔bare", "orig↔fx", "bare↔fx")

FAMILIES = {
    "spectral":  {
        "mel_l1_db":                 ("mel L1 (dB)",             "tab:blue"),
        "spectral_centroid_rmse_hz": ("spectral centroid RMSE (Hz)", "tab:cyan"),
    },
    "envelope":  {
        "rms_env_rmse":     ("RMS-env RMSE (lin)", "tab:orange"),
        "lufs_m_rmse_lu":   ("LUFS-M RMSE (LU)",   "tab:red"),
    },
    "embedding": {
        "embedding_cosine_distance": ("VGGish cosine dist",     "tab:green"),
    },
}


def load_rows(tsv_path: Path):
    rows = []
    with tsv_path.open() as f:
        rdr = csv.DictReader(f, delimiter="\t")
        for row in rdr:
            rows.append(row)
    if len(rows) != 3:
        raise RuntimeError(f"expected 3 rows in {tsv_path}, got {len(rows)}")
    return rows


def _series_for_key(rows, key):
    return [float(row[key]) for row in rows]


def render(tsv_path: Path, out_png: Path, title_suffix: str = "") -> None:
    rows = load_rows(tsv_path)
    fig, axes = plt.subplots(1, 3, figsize=(14, 4.5))
    x = np.arange(len(PAIR_LABELS))

    for ax, (fam_name, keys) in zip(axes, FAMILIES.items()):
        n = len(keys)
        width = 0.8 / n
        for i, (key, (label, color)) in enumerate(keys.items()):
            vals = _series_for_key(rows, key)
            offs = (i - (n - 1) / 2) * width
            bars = ax.bar(x + offs, vals, width, label=label, color=color,
                          edgecolor="black", linewidth=0.6)
            for b, v in zip(bars, vals):
                ax.text(b.get_x() + b.get_width() / 2,
                        b.get_height(),
                        f"{v:.2g}",
                        ha="center", va="bottom", fontsize=8)
        ax.set_xticks(x)
        ax.set_xticklabels(PAIR_LABELS)
        ax.set_title(f"{fam_name}")
        ax.legend(loc="best", fontsize=8, frameon=True)
        ax.margins(y=0.18)
        ax.grid(axis="y", linestyle=":", alpha=0.5)

    caption = ("M-TEX-1/panel across three ordered stage pairs on "
               "synth_030s (fluidsynth-fallback seed). Per-family bars; "
               "NO aggregate. Family disagreement is signal, not noise.")
    if title_suffix:
        caption = caption + " " + title_suffix
    fig.suptitle(caption, fontsize=10, wrap=True)
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    out_png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(str(out_png), dpi=140)
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tsv", default="data/tex/stage_by_stage_synth_030s.tsv")
    ap.add_argument("--out", default=os.environ.get(
        "FIGURE_OUT", "docs/figures/tex_stage_by_stage_families.png"))
    args = ap.parse_args()
    render(Path(args.tsv), Path(args.out))
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
