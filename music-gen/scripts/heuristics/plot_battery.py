#!/usr/bin/env -S /usr/bin/python3
# plot_battery.py — histograms of the 4 mess-scale heuristics across all 7 clips
# created: 2026-08-28T05:20:00Z  cycle: 4  run_id: run-2026-08-28T040704Z
# agent: worker (clone-1)  milestone: M-HEUR-1
"""Emit 4 per-heuristic histograms + 3 meta-descriptor bar charts.

Histograms are aggregated across all 3 seeds (7 clips total). One PNG per
heuristic under data/heuristics/battery_histograms/.
Meta bar charts are per seed, co-located with their meta_descriptors.json.
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path


def main() -> int:
    assert sys.executable == "/usr/bin/python3", f"wrong interpreter: {sys.executable}"
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    root = Path("/home/user/long-exposure-runs/music-gen")
    heur_dir = root / "data" / "heuristics"

    # 1) Aggregate all 7 clips across seeds
    per_heuristic: dict[str, list[float]] = {
        "melody": [], "timbre": [], "form": [], "dynamics": [],
    }
    nulls: dict[str, list[str]] = {k: [] for k in per_heuristic}
    for tsv in sorted(heur_dir.glob("*/clip_battery.tsv")):
        with tsv.open() as f:
            r = csv.DictReader(f, delimiter="\t")
            for row in r:
                for h in per_heuristic:
                    v = row.get(f"{h}__mess_scale", "")
                    if v == "":
                        nulls[h].append(f"{tsv.parent.name}#{row['clip_index']}:{row.get(f'{h}__reason', '')}")
                    else:
                        per_heuristic[h].append(float(v))

    out_dir = heur_dir / "battery_histograms"
    out_dir.mkdir(parents=True, exist_ok=True)
    for h, vals in per_heuristic.items():
        fig, ax = plt.subplots(figsize=(6, 3.5))
        if vals:
            ax.hist(vals, bins=10, range=(0, 1), color="#4a7", edgecolor="black")
        ax.set_xlim(0, 1)
        ax.set_xlabel("mess_scale")
        ax.set_ylabel("clip count (of 7 total)")
        title = f"{h}_quality — n={len(vals)}"
        if nulls[h]:
            title += f", null={len(nulls[h])} ({', '.join(nulls[h])})"
        ax.set_title(title, fontsize=9)
        fig.tight_layout()
        out = out_dir / f"hist_{h}.png"
        fig.savefig(out, dpi=110)
        plt.close(fig)
        print(f"WROTE {out}")

    # 2) Per-seed meta-descriptor bar charts
    for meta_path in sorted(heur_dir.glob("*/meta_descriptors.json")):
        with meta_path.open() as f:
            md = json.load(f)
        labels = ["dyn_trajectory", "form_coherence", "peak_loc_frac", "heur_variance"]
        keys = ["dynamics_trajectory", "form_coherence", "peak_location_fraction",
                "heuristic_variance_across_clips"]
        values = [md.get(k) for k in keys]
        # Skip Nones for plotting; annotate as "null"
        plot_vals = [0 if v is None else v for v in values]
        colors = ["#a44" if v is None else "#468" for v in values]
        fig, ax = plt.subplots(figsize=(6, 3.5))
        ax.bar(labels, plot_vals, color=colors, edgecolor="black")
        for i, v in enumerate(values):
            annot = "null" if v is None else f"{v:.4g}"
            ax.text(i, plot_vals[i], annot, ha="center", va="bottom", fontsize=8)
        ax.set_title(f"meta descriptors — {md['source_id']} (dur={md['duration_s']}s)",
                     fontsize=9)
        ax.axhline(0, color="black", lw=0.5)
        fig.tight_layout()
        out = meta_path.parent / "meta_bars.png"
        fig.savefig(out, dpi=110)
        plt.close(fig)
        print(f"WROTE {out}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
