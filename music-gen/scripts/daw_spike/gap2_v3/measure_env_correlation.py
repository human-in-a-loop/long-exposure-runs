#!/usr/bin/env python3
"""Envelope-correlation measurement for GAP-2 v3.

Pearson correlation of RMS envelopes (hop=512, n_fft=2048, mono
mixdown) between the automated render and the piecewise-fixed
reference. Mirrors the methodology cycle-12 clone-2 used at
data/daw_spike/gap1_midi_import_measurement.json (env_correlation
= 1.000 there) for direct comparability.
"""
from __future__ import annotations

import os
import sys

os.environ.setdefault('OMP_NUM_THREADS', '1')
os.environ.setdefault('MKL_NUM_THREADS', '1')
os.environ.setdefault('OPENBLAS_NUM_THREADS', '1')
os.environ.setdefault('PYTHONHASHSEED', '0')

assert sys.executable == '/usr/bin/python3', sys.executable

import argparse
import json
import pathlib

import numpy as np
import soundfile as sf


def rms_envelope(x: np.ndarray, sr: int, n_fft: int = 2048, hop: int = 512) -> np.ndarray:
    """Frame-wise RMS envelope on the mono mixdown, matching cycle-12 methodology."""
    if x.ndim > 1:
        x = x.mean(axis=1)
    x = x.astype(np.float64)
    # Centered frames (like librosa default): pad by n_fft//2 on each side
    pad = n_fft // 2
    xp = np.pad(x, (pad, pad), mode='constant')
    n = 1 + (len(xp) - n_fft) // hop
    env = np.empty(n, dtype=np.float64)
    for i in range(n):
        seg = xp[i * hop : i * hop + n_fft]
        env[i] = float(np.sqrt(np.mean(seg * seg)))
    return env


def pearson(a: np.ndarray, b: np.ndarray) -> float:
    a = a - a.mean()
    b = b - b.mean()
    denom = float(np.sqrt(np.sum(a * a) * np.sum(b * b)))
    if denom < 1e-30:
        return 0.0
    return float(np.sum(a * b) / denom)


def envelope_for(wav_path: pathlib.Path):
    x, sr = sf.read(str(wav_path), always_2d=True, dtype='float64')
    return rms_envelope(x, sr), sr


def curve_vs_envelope(wav_path: pathlib.Path, curve_points, sr_expected: int = 44100, n_fft: int = 2048, hop: int = 512) -> float:
    """Pearson corr between the automation CURVE (sampled to envelope hop) and the WAV envelope.

    Direct test that the parameter drives the audible signal shape.
    """
    env, sr = envelope_for(wav_path)
    assert sr == sr_expected, sr
    # Envelope frame times (centered, matching librosa default)
    n = len(env)
    times = np.arange(n) * hop / sr  # first frame at t=0 due to centered padding
    xs = np.asarray([p[0] for p in curve_points], dtype=np.float64)
    ys = np.asarray([p[1] for p in curve_points], dtype=np.float64)
    curve = np.interp(times, xs, ys)
    return pearson(env, curve)


def measure(automated: pathlib.Path, reference: pathlib.Path, out_json: pathlib.Path) -> dict:
    xa, sra = sf.read(str(automated), always_2d=True, dtype='float64')
    xb, srb = sf.read(str(reference), always_2d=True, dtype='float64')
    assert sra == srb, (sra, srb)
    ea = rms_envelope(xa, sra)
    eb = rms_envelope(xb, srb)
    n = min(len(ea), len(eb))
    ea, eb = ea[:n], eb[:n]
    corr = pearson(ea, eb)
    result = {
        'automated_wav': str(automated),
        'reference_wav': str(reference),
        'sr': sra,
        'n_fft': 2048,
        'hop': 512,
        'envelope_len': int(n),
        'env_correlation': corr,
        'automated_peak': float(np.max(np.abs(xa))),
        'reference_peak': float(np.max(np.abs(xb))),
        'automated_rms': float(np.sqrt(np.mean(xa * xa))),
        'reference_rms': float(np.sqrt(np.mean(xb * xb))),
    }
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(result, indent=2))
    return result


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--automated', default='data/daw_spike/gap2_v3/automated.wav')
    ap.add_argument('--reference', default='data/daw_spike/gap2_v3/reference.wav')
    ap.add_argument('--out', default='data/daw_spike/gap2_v3/env_correlation.json')
    a = ap.parse_args()
    r = measure(pathlib.Path(a.automated), pathlib.Path(a.reference), pathlib.Path(a.out))
    print(json.dumps(r, indent=2))
