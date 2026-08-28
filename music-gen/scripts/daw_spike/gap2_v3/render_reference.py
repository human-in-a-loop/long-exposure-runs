#!/usr/bin/env python3
"""Render the piecewise-fixed reference for GAP-2 v3 envelope-correlation.

Two 5.0-s fixed-parameter renders concatenated to a 10.0-s reference WAV:
  - Segment 1 (0-5 s): fixed Output Mix = 0.35 (midpoint of 0.0 -> 0.7)
  - Segment 2 (5-10 s): fixed Output Mix = 0.45 (midpoint of 0.7 -> 0.2)

This is the reference the automated render is compared against via
Pearson correlation of RMS envelopes; a correlation >= 0.9 proves the
automation actually varies the parameter (rather than being silently
ignored, in which case both halves would sound like a constant render).

The brief calls out "5s @ wet=0.5 + 5s @ wet=0.35, roughly midpointing".
This implementation uses the more precise midpoints (0.35 and 0.45)
computed from the actual automation curve endpoints; documented in the
report.
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
import pathlib
import tempfile

import numpy as np
import soundfile as sf

from scripts.daw_spike.gap2_v3.dawdreamer_automation import render_fixed


def concat_wavs(a: pathlib.Path, b: pathlib.Path, out: pathlib.Path) -> None:
    xa, sra = sf.read(str(a), always_2d=True, dtype='float32')
    xb, srb = sf.read(str(b), always_2d=True, dtype='float32')
    assert sra == srb, (sra, srb)
    y = np.concatenate([xa, xb], axis=0)
    out.parent.mkdir(parents=True, exist_ok=True)
    sf.write(str(out), y, sra, subtype='PCM_16')


def build_reference(plugin_path: pathlib.Path, parameter_index: int, input_wav: pathlib.Path, out_wav: pathlib.Path, values=(0.35, 0.45), sr: int = 44100) -> dict:
    with tempfile.TemporaryDirectory() as td:
        td = pathlib.Path(td)
        seg1 = td / 'seg1.wav'
        seg2 = td / 'seg2.wav'
        info1 = render_fixed(plugin_path, parameter_index, values[0], input_wav, seg1, sr=sr, duration_s=5.0)
        info2 = render_fixed(plugin_path, parameter_index, values[1], input_wav, seg2, sr=sr, duration_s=5.0)
        concat_wavs(seg1, seg2, out_wav)
    return {'segment1': info1, 'segment2': info2, 'reference_wav': str(out_wav), 'fixed_values': list(values)}


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--plugin', default='/usr/lib/vst3/Surge XT Effects.vst3')
    ap.add_argument('--param-index', type=int, default=10)
    ap.add_argument('--input', default='data/daw_spike/gap2_v3/input_10s.wav')
    ap.add_argument('--out', default='data/daw_spike/gap2_v3/reference.wav')
    args = ap.parse_args()
    info = build_reference(pathlib.Path(args.plugin), args.param_index, pathlib.Path(args.input), pathlib.Path(args.out))
    print(info)
