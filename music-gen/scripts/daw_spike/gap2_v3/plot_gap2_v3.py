#!/usr/bin/env python3
"""Plot GAP-2 v3 automation figure: waveform + envelope overlay + 3-point curve.

3 stacked panels:
  1. Top: automated.wav RMS envelope + reference.wav RMS envelope overlay
  2. Middle: automated.wav waveform (mono) + flat_control.wav waveform overlay
  3. Bottom: 3-point automation curve visualization + reference step function

Annotates env_correlation and curve-vs-envelope delta.
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import sys

os.environ.setdefault('MPLBACKEND', 'Agg')
os.environ.setdefault('OMP_NUM_THREADS', '1')

assert sys.executable == '/usr/bin/python3', sys.executable

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import soundfile as sf


ROOT = pathlib.Path('/home/user/long-exposure-runs/music-gen')
DATA = ROOT / 'data/daw_spike/gap2_v3'
FIG_OUT = ROOT / 'docs/figures/daw_spike_gap2_v3_automation.png'
CURVE = [(0.0, 0.0), (5.0, 0.7), (10.0, 0.2)]
REFERENCE_VALUES = (0.35, 0.45)


def rms_env(x, sr, n_fft=2048, hop=512):
    if x.ndim > 1:
        x = x.mean(axis=1)
    x = x.astype(np.float64)
    pad = n_fft // 2
    xp = np.pad(x, (pad, pad), mode='constant')
    n = 1 + (len(xp) - n_fft) // hop
    env = np.empty(n, dtype=np.float64)
    for i in range(n):
        seg = xp[i * hop : i * hop + n_fft]
        env[i] = float(np.sqrt(np.mean(seg * seg)))
    return env, np.arange(n) * hop / sr


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default=str(FIG_OUT))
    args = ap.parse_args()

    xa, sr = sf.read(str(DATA / 'automated.wav'), always_2d=True, dtype='float64')
    xr, _ = sf.read(str(DATA / 'reference.wav'), always_2d=True, dtype='float64')
    xf, _ = sf.read(str(DATA / 'flat_control.wav'), always_2d=True, dtype='float64')
    summary = json.loads((DATA / 'summary.json').read_text())

    env_a, te_a = rms_env(xa, sr)
    env_r, te_r = rms_env(xr, sr)
    env_f, te_f = rms_env(xf, sr)

    t = np.arange(len(xa)) / sr
    mono_a = xa.mean(axis=1)
    mono_f = xf.mean(axis=1)

    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(11, 9), sharex=True)

    ax1.plot(te_a, env_a, label='automated (3-point curve 0.0 -> 0.7 -> 0.2)', linewidth=1.4, color='#1f6feb')
    ax1.plot(te_r, env_r, label='piecewise-fixed reference (5s @ 0.35 + 5s @ 0.45)', linewidth=1.4, color='#d97706', linestyle='--')
    ax1.plot(te_f, env_f, label='flat-curve control (const 0.5)', linewidth=1.0, color='#6b7280', alpha=0.7)
    corr = summary['run1_env_correlation']
    fcorr = summary['run1_flat_env_correlation']
    ax1.set_ylabel('RMS envelope')
    ax1.set_title(
        'GAP-2 v3 — DawDreamer set_automation on Surge XT Effects VST3 (Output Mix, index 10)\n'
        f'env_corr(automated, reference) = {corr:.4f}   |   env_corr(flat_control, reference) = {fcorr:.4f}'
    )
    ax1.legend(loc='upper right', fontsize=8)
    ax1.grid(alpha=0.3)

    ax2.plot(t, mono_a, label='automated waveform (mono mixdown)', linewidth=0.35, color='#1f6feb', alpha=0.8)
    ax2.plot(t, mono_f, label='flat-control waveform', linewidth=0.35, color='#6b7280', alpha=0.5)
    diff = summary['auto_vs_flat_max_sample_diff']
    ax2.set_ylabel('amplitude')
    ax2.set_title(f'automated vs flat-control waveform | auto_vs_flat max sample diff = {diff:.6f}')
    ax2.legend(loc='upper right', fontsize=8)
    ax2.grid(alpha=0.3)

    # Bottom: the 3-point automation curve + reference step function.
    xs = np.linspace(0, 10, 1000)
    curve_xs = np.asarray([p[0] for p in CURVE])
    curve_ys = np.asarray([p[1] for p in CURVE])
    curve_interp = np.interp(xs, curve_xs, curve_ys)
    ref_step = np.where(xs < 5.0, REFERENCE_VALUES[0], REFERENCE_VALUES[1])
    flat = np.full_like(xs, 0.5)
    ax3.plot(xs, curve_interp, label='3-point automation curve (linear interp)', color='#1f6feb', linewidth=1.6)
    ax3.plot(xs, ref_step, label=f'reference step function ({REFERENCE_VALUES[0]}/{REFERENCE_VALUES[1]})', color='#d97706', linestyle='--', linewidth=1.4)
    ax3.plot(xs, flat, label='flat-control curve (const 0.5)', color='#6b7280', linewidth=1.0, alpha=0.7)
    ax3.scatter(curve_xs, curve_ys, color='#1f6feb', s=40, zorder=5)
    for x, y in CURVE:
        ax3.annotate(f'({x:.1f}s, {y:.2f})', (x, y), textcoords='offset points', xytext=(6, 6), fontsize=8)
    cvd = summary['curve_vs_envelope_delta']
    cvea = summary['curve_vs_envelope_automated']
    cvef = summary['curve_vs_envelope_flat_control']
    ax3.set_ylabel('Output Mix (normalized 0..1)')
    ax3.set_xlabel('time (s)')
    ax3.set_title(
        f'automation curves | curve_vs_env(automated) = {cvea:.4f}   '
        f'curve_vs_env(flat) = {cvef:.4f}   delta = {cvd:.4f}'
    )
    ax3.legend(loc='upper right', fontsize=8)
    ax3.grid(alpha=0.3)
    ax3.set_ylim(-0.05, 1.0)

    fig.suptitle(
        f'Verdict: {summary["verdict"]}   |   DawDreamer {summary["dawdreamer_version"]}   |   byte-determinism x2: {summary["byte_determinism_x2"]}',
        y=1.00, fontsize=10,
    )
    fig.tight_layout()
    FIG_OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.out, dpi=110, bbox_inches='tight')
    print(f'wrote {args.out}')


if __name__ == '__main__':
    main()
