#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-08-28T11:35:00Z
# cycle: 13
# run_id: run-2026-08-28T040704Z
# agent: worker
# milestone: M-TEX-1/stage-by-stage
# ---
"""3-seed × 3-family grid figure for M-TEX-1/stage-by-stage widening.

Rows = seeds (synth_030s, seed_mid_50s, synth_060s).
Columns = families (spectral: mel_l1_db, envelope: rms_env_rmse, embedding: VGGish cosine).
Bars per cell = the 3 ordered pairs (O-B, O-E, B-E).

Explicitly refuses to aggregate. Y-axes per family fixed across seeds for
cross-seed comparability. Output: docs/figures/tex_stage_by_stage_3seeds.png.

Run: /usr/bin/python3 scripts/tex/plot_stage_by_stage_v2.py
"""
from __future__ import annotations
import os, sys
from pathlib import Path

for _v in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

assert sys.executable == "/usr/bin/python3", sys.executable

WS = Path(__file__).resolve().parents[2]
if str(WS) not in sys.path:
    sys.path.insert(0, str(WS))

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

SEEDS = ("synth_030s", "seed_mid_50s", "synth_060s")
SEED_LABELS = {
    "synth_030s":   "synth_030s\n(polyphonic 30 s)",
    "seed_mid_50s": "seed_mid_50s\n(mono→stereo triad-sine 50 s)",
    "synth_060s":   "synth_060s\n(polyphonic 60 s)",
}

FAMILIES = (
    ("spectral",  "mel_l1_db",                  "log-mel L1 (dB)"),
    ("envelope",  "rms_env_rmse",               "RMS-envelope RMSE"),
    ("embedding", "embedding_cosine_distance",  "VGGish cosine distance"),
)

PAIRS = (("original", "bare_midi"), ("original", "effects_layered"), ("bare_midi", "effects_layered"))
PAIR_LABELS = ("O↔B", "O↔E", "B↔E")
PAIR_COLORS = ("#4c72b0", "#dd8452", "#55a467")


def _load_tsv(path: Path) -> dict:
    lines = path.read_text().strip().split("\n")
    header = lines[0].split("\t")
    rows = []
    for line in lines[1:]:
        vals = line.split("\t")
        row = dict(zip(header, vals))
        rows.append(row)
    return {(r["a_stage"], r["b_stage"]): r for r in rows}


def main() -> None:
    tsvs = {seed: _load_tsv(WS / "data" / "tex" / f"stage_by_stage_{seed}.tsv")
            for seed in SEEDS}

    fig, axes = plt.subplots(nrows=len(SEEDS), ncols=len(FAMILIES),
                             figsize=(11.5, 8.0), sharex=False, sharey=False)

    # Per-family y-axis limits across seeds for comparability.
    for j, (_fam, key, _label) in enumerate(FAMILIES):
        vmax = 0.0
        for seed in SEEDS:
            for pair in PAIRS:
                v = float(tsvs[seed][pair][key])
                if v > vmax:
                    vmax = v
        for i in range(len(SEEDS)):
            axes[i, j].set_ylim(0, vmax * 1.10)

    for i, seed in enumerate(SEEDS):
        for j, (fam, key, label) in enumerate(FAMILIES):
            ax = axes[i, j]
            heights = [float(tsvs[seed][pair][key]) for pair in PAIRS]
            xs = np.arange(len(PAIRS))
            ax.bar(xs, heights, color=PAIR_COLORS, edgecolor="black", linewidth=0.5)
            for x, h in zip(xs, heights):
                ax.text(x, h, f"{h:.3g}", ha="center", va="bottom", fontsize=8)
            ax.set_xticks(xs)
            ax.set_xticklabels(PAIR_LABELS, fontsize=9)
            if i == 0:
                ax.set_title(f"{fam}\n{label}", fontsize=10)
            if j == 0:
                ax.set_ylabel(SEED_LABELS[seed], fontsize=9)
            ax.grid(axis="y", linestyle=":", alpha=0.4)

    fig.suptitle(
        "M-TEX-1/stage-by-stage widening — 3 seeds × 3 families × 3 pairs\n"
        "(cycle-13; cycle-9 chain applied verbatim; VGGish embedding rung)",
        fontsize=11,
    )
    fig.tight_layout(rect=(0, 0, 1, 0.94))

    out = WS / "docs" / "figures" / "tex_stage_by_stage_3seeds.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=140)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
