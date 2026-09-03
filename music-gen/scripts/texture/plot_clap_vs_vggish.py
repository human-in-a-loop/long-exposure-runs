#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-08-28T11:05:00Z
# cycle: 11
# run_id: run-2026-08-28T040704Z
# agent: worker
# milestone: M-TEX-1/panel/embedding
# ---
"""Family-disagreement comparison figure for the CLAP-upgrade branch.

CLAP could not be brought up in the current environment (roberta-base
egress blocked; see docs/clap_embedding_upgrade_report.md §2). This
figure therefore shows the VGGish-rung family-disagreement signal on
its own, alongside a fetchability-ladder outcome panel that documents
each rung's status. That is deliberate: the figure is the visual
record of the ladder's designed failure mode.

Two sub-panels:
  (i)  cycle-9 stage-by-stage triplet — 3 ordered pairs × 4 numeric
       families ({mel_l1_db, spectral_centroid_rmse_hz, rms_env_rmse,
       embedding_cosine_distance}). Bars grouped by pair; CLAP column
       shown as an explicit N/A block with the fetchability-ladder rung
       that blocked it.
  (ii) cycle-10 synth_060s pair — 1 pair × 4 numeric families. Same
       convention.

Regenerate:  FIGURE_OUT=docs/figures/clap_vs_vggish_family_disagreement.png \\
             /usr/bin/python3 scripts/texture/plot_clap_vs_vggish.py
"""
from __future__ import annotations

import os
import pathlib
import sys

assert sys.executable == "/usr/bin/python3", sys.executable

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[2]

# --- data from data/tex/clap_upgrade_results.tsv (kept inline for legibility) --
CYCLE9 = [
    # pair,                        mel_l1_db, sc_rmse_hz, rms_env,  emb_cos
    ("original\nvs\nbare_midi",     9.906,     2804.91,    0.02759,  0.12342),
    ("original\nvs\neffects_layered",10.937,   2743.49,    0.04875,  0.09513),
    ("bare_midi\nvs\neffects_layered",6.533,    211.79,    0.04492,  0.06715),
]
CYCLE10 = [
    ("original\nvs\nbare_midi",    10.7548,   2764.96,    0.02887,  0.16190),
]
METRIC_LABELS = [
    "mel_l1_db",
    "spectral_centroid_rmse_hz",
    "rms_env_rmse",
    "embedding_cosine_distance",
]


def _bar_group(ax, pairs, values, title):
    n_pairs = len(pairs)
    n_metrics = len(METRIC_LABELS)
    x = np.arange(n_pairs)
    width = 0.18
    colors = ["#4C72B0", "#DD8452", "#55A467", "#C44E52"]
    for i, (label, color) in enumerate(zip(METRIC_LABELS, colors)):
        vs = [values[p][i] for p in range(n_pairs)]
        # normalise so that four disparate scales fit one axis:
        # divide by the max of that metric across pairs to show relative shape.
        max_v = max(vs) if max(vs) > 0 else 1.0
        norm = [v / max_v for v in vs]
        bars = ax.bar(x + i * width - 1.5 * width, norm, width,
                      label=f"{label}\n(÷{max_v:.3g})", color=color)
        for b, raw in zip(bars, vs):
            ax.text(b.get_x() + b.get_width() / 2.0, b.get_height() + 0.02,
                    f"{raw:.3g}", ha="center", va="bottom", fontsize=7)
    ax.set_xticks(x)
    ax.set_xticklabels(pairs, fontsize=8)
    ax.set_ylabel("value normalised to max across pairs (labels show raw)")
    ax.set_ylim(0, 1.35)
    ax.set_title(title, fontsize=10)
    ax.legend(loc="upper right", fontsize=6, framealpha=0.9)
    ax.grid(True, axis="y", linestyle=":", alpha=0.4)


def _ladder_panel(ax):
    ax.axis("off")
    rungs = [
        ("1.0 import laion_clap",           "BLOCKED", "torchvision::nms op missing on CPU-only torch (workaround: register_fake noop)"),
        ("1.1 import laion_clap (patched)", "OK",      "module tree walks after noop patch"),
        ("1.2 CLAP_Module(enable_fusion=False)", "BLOCKED",
                                                  "workspace egress SSL-cert blocks HF fetch of roberta-base config"),
        ("1.3 CLAP weight fetch",           "N/A",     "not attempted; upstream blocked at rung 1.2"),
        ("2   tfhub VGGish",                "OK",      "cached from cycle 4; 128-D, self-distance ≤ 7.4e-8"),
        ("3   none_available",              "reserved","ladder resolved at rung 2"),
    ]
    y = 1.0
    dy = 1.0 / (len(rungs) + 1)
    ax.text(0.02, y, "Fetchability ladder outcome (rung log source: data/tex/panel_rung_log.jsonl)",
            transform=ax.transAxes, weight="bold", fontsize=10)
    color_map = {"BLOCKED": "#C44E52", "OK": "#55A467", "N/A": "#888",
                 "reserved": "#888"}
    for probe, status, why in rungs:
        y -= dy
        ax.text(0.02, y, probe, transform=ax.transAxes, family="monospace",
                fontsize=8)
        ax.text(0.42, y, status, transform=ax.transAxes, family="monospace",
                weight="bold", fontsize=9, color=color_map.get(status, "black"))
        ax.text(0.55, y, why, transform=ax.transAxes, fontsize=7.5,
                color="#333")


def main() -> int:
    out = pathlib.Path(os.environ.get(
        "FIGURE_OUT",
        ROOT / "docs" / "figures" / "clap_vs_vggish_family_disagreement.png"))
    out.parent.mkdir(parents=True, exist_ok=True)

    fig = plt.figure(figsize=(13, 9))
    gs = fig.add_gridspec(2, 2, height_ratios=[1.2, 1.0])

    ax1 = fig.add_subplot(gs[0, 0])
    _bar_group(ax1,
               pairs=[p[0] for p in CYCLE9],
               values=[[p[1], p[2], p[3], p[4]] for p in CYCLE9],
               title="(i) Cycle-9 stage-by-stage triplet — VGGish rung "
                     "(CLAP N/A: fetchability rung 1.2 blocked)")

    ax2 = fig.add_subplot(gs[0, 1])
    _bar_group(ax2,
               pairs=[p[0] for p in CYCLE10],
               values=[[p[1], p[2], p[3], p[4]] for p in CYCLE10],
               title="(ii) Cycle-10 synth_060s pair — VGGish rung "
                     "(CLAP N/A)")

    ax3 = fig.add_subplot(gs[1, :])
    _ladder_panel(ax3)

    fig.suptitle(
        "M-TEX-1/panel/embedding CLAP upgrade attempt — cycle 11.  "
        "CLAP unreachable in this workspace; ladder fell back to VGGish "
        "as designed. Non-embedding numbers are the same VGGish-era numbers "
        "the panel already published; the swap did not happen.",
        fontsize=11)
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    fig.savefig(out, dpi=140)
    plt.close(fig)
    print(f"[OK] wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
