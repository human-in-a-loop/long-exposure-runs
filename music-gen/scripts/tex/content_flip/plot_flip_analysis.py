#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-08-28T14:35:00Z
# cycle: 14
# run_id: run-2026-08-28T040704Z
# agent: worker
# milestone: M-TEX-1/panel/embedding/content-flip-analysis
# ---
"""Two-subpanel figure for the M-TEX-1/panel/embedding content-flip sweep.

Left panel:  polyphony sweep P1..P4 — paired bars per variant of dmel and
             dvgg vs baseline P4. Sign disagreement is visually obvious
             (bars on opposite sides of zero).

Right panel: envelope sweep E1..E4 — same construction with baseline E4.

Cycle-13 anchor across-stage signs are annotated at the top for context.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

os.environ.setdefault("MPLBACKEND", "Agg")

assert sys.executable == "/usr/bin/python3", sys.executable

import matplotlib.pyplot as plt
import numpy as np

WS = Path(__file__).resolve().parents[3]


def _plot_axis(ax, axis_data: dict, title: str) -> None:
    entries = sorted(axis_data["entries"], key=lambda e: e["rank"])
    labels = [e["variant_id"] for e in entries]
    dmel = [e["dmel_vs_baseline"] for e in entries]
    dvgg = [e["dvgg_vs_baseline"] for e in entries]

    x = np.arange(len(labels))
    w = 0.35

    # Normalize magnitude for visual comparison (mel in dB scale, vgg in [0,2]).
    max_mel = max(abs(m) for m in dmel) or 1.0
    max_vgg = max(abs(v) for v in dvgg) or 1.0
    nm = [m / max_mel for m in dmel]
    nv = [v / max_vgg for v in dvgg]

    b1 = ax.bar(x - w/2, nm, width=w, label="mel_l1_db Δ (normalized)",
                color="#1f77b4")
    b2 = ax.bar(x + w/2, nv, width=w, label="VGGish cosine Δ (normalized)",
                color="#d62728")
    ax.axhline(0, color="black", linewidth=0.8)

    # Sign disagreement marker
    for i, e in enumerate(entries):
        if e["agree"] == -1:
            ax.text(i, 1.05, "✗", color="red", ha="center", fontsize=10,
                    fontweight="bold")
        elif e["agree"] == +1:
            ax.text(i, 1.05, "=", color="green", ha="center", fontsize=10)
        else:
            ax.text(i, 1.05, "•", color="gray", ha="center", fontsize=10)

    for i, e in enumerate(entries):
        ax.text(i - w/2, nm[i] + (0.03 if nm[i] >= 0 else -0.08),
                f"{dmel[i]:.2g}", ha="center", fontsize=7, color="#1f77b4")
        ax.text(i + w/2, nv[i] + (0.03 if nv[i] >= 0 else -0.08),
                f"{dvgg[i]:.2g}", ha="center", fontsize=7, color="#d62728")

    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylim(-1.4, 1.4)
    ax.set_ylabel("Δ vs baseline (normalized to axis max |Δ|)")
    ax.set_title(f"{title}\nbaseline={axis_data['baseline_variant']}, "
                 f"verdict-piece: {axis_data['n_agree']}✓ / "
                 f"{axis_data['n_disagree']}✗ / {axis_data['n_tie']}·")
    ax.legend(loc="lower right", fontsize=8)
    ax.grid(True, axis="y", linestyle=":", alpha=0.4)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--in-json",
                    default="data/tex/embedding_flip_analysis/threshold_characterization.json")
    ap.add_argument("--out-png",
                    default="docs/figures/tex_embedding_flip_analysis.png")
    args = ap.parse_args()

    in_json = (WS / args.in_json).resolve()
    out_png = (WS / args.out_png).resolve()
    data = json.loads(in_json.read_text())

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    _plot_axis(axes[0], data["polyphony_axis"],
               "Polyphony sweep (P1 mono → P4 4-voice)")
    _plot_axis(axes[1], data["envelope_axis"],
               "Envelope sweep (E1 sine → E2 decay → E3 perc → E4 sustain)")

    anchors = data["cycle13_anchors_across_stage"]
    anchor_line = " | ".join(
        f"{s}: mel Δ {a['d_mel_l1_db_orig_eff_vs_orig_bare']:+.2f}dB, "
        f"vgg Δ {a['d_vggish_orig_eff_vs_orig_bare']:+.4f} "
        f"→ {'AGREE' if a['agree']==1 else ('DISAGREE' if a['agree']==-1 else 'TIE')}"
        for s, a in anchors.items())
    fig.suptitle("M-TEX-1/panel/embedding VGGish content-flip sweep — "
                 f"verdict: {data['verdict']}",
                 fontsize=13, y=1.02)
    fig.text(0.5, -0.02,
             f"Cycle-13 anchors (across-stage bare→effects vs across-stage orig→bare):\n{anchor_line}",
             ha="center", fontsize=8, color="#333")

    out_png.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(out_png, dpi=140, bbox_inches="tight")
    print(f"[plot_flip_analysis] wrote {out_png}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
