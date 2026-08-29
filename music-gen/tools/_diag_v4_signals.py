#!/usr/bin/env -S /usr/bin/python3
"""Diagnostic: inspect v4 signal characteristics for salt=0.

Answers: are the WAVs NaN/inf-clean? Are they very hot? Are they silent?
Why is LUFS-M NaN?
"""
from __future__ import annotations
import sys, shutil, tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import soundfile as sf

from scripts.palette_render.render_stem import render_stem, SAMPLE_RATE, SAMPLE_COUNT
from scripts.palette_render_v4.derive_parameter_dict_8x8 import derive_per_salt
from scripts.gen_palette_batch_v2.sample_rule_triple_v2 import sample_triples

DISPATCH = {"drums": "fluidsynth_gm", "bass": "sfizz", "other": "sfizz"}

t = sample_triples([0])
p = derive_per_salt(t[0], DISPATCH)
print("salt=0 params:")
for stem, info in p.items():
    print(f"  {stem}: {info['parameter_dict']}")

tmp = Path(tempfile.mkdtemp(prefix="diag_"))
stem_wavs = []
for stem in ("drums", "bass", "other"):
    d = tmp / stem
    r = render_stem(stem, DISPATCH[stem], d, parameter_dict=p[stem]["parameter_dict"])
    stem_wavs.append(Path(r["run1_wav_path"]))
    y, sr = sf.read(str(r["run1_wav_path"]), always_2d=True)
    print(f"{stem}: shape={y.shape} min={y.min():.6f} max={y.max():.6f} "
          f"nan={np.isnan(y).any()} inf={np.isinf(y).any()} "
          f"rms={float(np.sqrt(np.mean(y**2))):.6f}")

accum = np.zeros((SAMPLE_COUNT, 2), dtype=np.float32)
for sw in stem_wavs:
    y, sr = sf.read(str(sw), always_2d=True)
    if y.shape[1] == 1:
        y = np.concatenate([y, y], axis=1)
    n = min(y.shape[0], SAMPLE_COUNT)
    accum[:n, :] += y[:n, :].astype(np.float32)
print(f"combined: min={accum.min():.6f} max={accum.max():.6f} "
      f"nan={np.isnan(accum).any()} inf={np.isinf(accum).any()} "
      f"rms={float(np.sqrt(np.mean(accum**2))):.6f}")

# Now try LUFS on the combined vs original.
import pyloudnorm as pyln
meter = pyln.Meter(SAMPLE_RATE)

orig, sr = sf.read("data/tex/renders/synth_030s/original.wav", always_2d=True)
if orig.shape[1] == 1:
    orig = np.concatenate([orig, orig], axis=1)
try:
    lufs_orig = meter.integrated_loudness(orig)
    print(f"LUFS orig integrated: {lufs_orig}")
except Exception as e:
    print(f"LUFS orig failed: {e}")

try:
    lufs_v4 = meter.integrated_loudness(accum)
    print(f"LUFS v4-salt0 integrated: {lufs_v4}")
except Exception as e:
    print(f"LUFS v4-salt0 failed: {e}")

shutil.rmtree(tmp)
