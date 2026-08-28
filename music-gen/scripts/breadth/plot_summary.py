#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-08-28T11:32:00Z
# cycle: 10
# run_id: run-2026-08-28T040704Z
# agent: worker
# milestone: M-INGEST-1/breadth-second-seeds
# ---
"""Grouped-bar chart of panel numbers per seed for M-INGEST-1/breadth-second-seeds.

Reads data/breadth/summary.tsv. Emits docs/figures/pipeline_breadth_panel.png.

The 5 metric families are on distinct scales, so the chart uses one
subplot per metric (shared x = seed_id). This is the honest
"panel refuses aggregation" convention from M-TEX-1/panel.
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

assert sys.executable == '/usr/bin/python3', sys.executable

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path('/home/user/long-exposure-runs/music-gen')
IN_TSV = ROOT / 'data' / 'breadth' / 'summary.tsv'
OUT_PNG = ROOT / 'docs' / 'figures' / 'pipeline_breadth_panel.png'

METRICS = [
    ('panel_mel_l1_db',                'mel L1 (dB)',              'lower = closer'),
    ('panel_spectral_centroid_rmse_hz','spectral centroid RMSE (Hz)','lower = closer'),
    ('panel_rms_env_rmse',             'RMS-env RMSE',             'lower = closer'),
    ('panel_lufs_m_rmse_lu',           'LUFS-M RMSE (LU)',         'lower = closer'),
    ('panel_embedding_cosine',         'VGGish cosine dist.',      'lower = closer'),
]


def main() -> None:
    rows = list(csv.DictReader(IN_TSV.open(), delimiter='\t'))
    seeds = [r['seed_id'].replace(' (baseline, cycle 9)', '\n(baseline\ncycle 9)') for r in rows]
    colors = ['#3477c9' if 'baseline' not in r['seed_id'] else '#a0a0a0' for r in rows]

    OUT_PNG.parent.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(1, 5, figsize=(18, 4.5))
    for ax, (col, label, direction) in zip(axes, METRICS):
        vals = [float(r[col]) for r in rows]
        ax.bar(range(len(seeds)), vals, color=colors)
        ax.set_xticks(range(len(seeds)))
        ax.set_xticklabels(seeds, rotation=0, ha='center', fontsize=8)
        ax.set_title(label, fontsize=10)
        ax.set_xlabel(direction, fontsize=8, color='#666')
        ax.grid(axis='y', alpha=0.3)
        for i, v in enumerate(vals):
            ax.text(i, v, f'{v:.3g}', ha='center', va='bottom', fontsize=8)
        ax.set_ylim(0, max(vals) * 1.20 if max(vals) > 0 else 1.0)

    fig.suptitle('M-INGEST-1/breadth-second-seeds: original-vs-bare-MIDI texture panel\n'
                 '(per-family, no aggregate — panel refuses aggregation by design)',
                 fontsize=11)
    fig.tight_layout(rect=[0, 0, 1, 0.94])
    fig.savefig(str(OUT_PNG), dpi=120, bbox_inches='tight')
    plt.close(fig)
    print(f'wrote {OUT_PNG}')


if __name__ == '__main__':
    main()
