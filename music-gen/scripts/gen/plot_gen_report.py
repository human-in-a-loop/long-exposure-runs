#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-08-28T11:20:00Z
# cycle: 10
# run_id: run-2026-08-28T040704Z
# agent: worker (clone-0, fork 00b3ae64444c)
# milestone: M-GEN-1/first-generation
# ---
"""Regenerate the report figure: heuristic bar chart + panel numbers table.

Called by the report authoring pipeline. Uses matplotlib; theme-agnostic.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

assert sys.executable == "/usr/bin/python3", sys.executable

os.environ.setdefault("MPLBACKEND", "Agg")
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def make_figure(scoring_json: Path, out_png: Path) -> Path:
    scoring = json.loads(Path(scoring_json).read_text())
    heur = scoring["heuristics"]
    panel = scoring["texture_panel_bare_vs_effects"]
    ear = scoring["ear"]

    fig, axes = plt.subplots(1, 2, figsize=(10, 4.2), dpi=100)

    # Left: heuristic mess-scale bar chart.
    names = ["melody", "timbre", "form", "dynamics"]
    vals = [heur[f"{n}_quality"]["mess_scale"] or 0.0 for n in names]
    colors = ["#4C72B0", "#55A868", "#C44E52", "#8172B2"]
    axes[0].bar(names, vals, color=colors, edgecolor="black")
    axes[0].set_ylim(0, 1)
    axes[0].set_ylabel("mess-scale [0, 1]")
    axes[0].set_title(f"M-HEUR-1 battery on effects_layered.wav\n(ear = {ear['prediction']}/7 UNCALIBRATED)")
    axes[0].axhline(y=0.5, color="gray", linestyle="--", alpha=0.4, linewidth=0.8)
    for i, v in enumerate(vals):
        axes[0].text(i, v + 0.02, f"{v:.3f}", ha="center", fontsize=9)

    # Right: panel numbers as a text table.
    axes[1].axis("off")
    panel_rows = [
        ("mel_l1_db", f"{panel['mel_l1_db']:.3f}"),
        ("spectral_centroid_rmse_hz", f"{panel['spectral_centroid_rmse_hz']:.2f}"),
        ("rms_env_rmse", f"{panel['rms_env_rmse']:.4f}"),
        ("lufs_m_rmse_lu", f"{panel['lufs_m_rmse_lu']:.2f}"),
        ("embedding_cosine_distance", f"{panel['embedding_cosine_distance']:.4f}"),
        ("embedding_rung", str(panel["embedding_rung"])),
        ("sr_hz", str(panel["sr_hz"])),
        ("n_samples_compared", str(panel["n_samples_compared"])),
    ]
    tbl = axes[1].table(
        cellText=panel_rows,
        colLabels=["M-TEX-1/panel key", "value"],
        loc="center",
        cellLoc="left",
    )
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(9)
    tbl.scale(1.0, 1.4)
    axes[1].set_title("M-TEX-1/panel: bare_midi vs effects_layered")

    fig.suptitle("M-GEN-1/first-generation — first deterministic clip", fontsize=12)
    fig.tight_layout(rect=[0, 0, 1, 0.94])
    out_png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_png, dpi=110)
    plt.close(fig)
    return out_png


def _main(argv: list[str]) -> int:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--scoring", type=Path, default=Path("data/gen/scoring_v1.json"))
    ap.add_argument("--out", type=Path, default=Path("docs/figures/gen_first_generation_provenance.png"))
    args = ap.parse_args(argv)
    p = make_figure(args.scoring, args.out)
    print(f"[plot_gen_report] wrote {p}")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main(sys.argv[1:]))
