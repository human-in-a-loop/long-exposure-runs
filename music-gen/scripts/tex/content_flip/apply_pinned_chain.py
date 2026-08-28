#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-08-28T14:05:00Z
# cycle: 14
# run_id: run-2026-08-28T040704Z
# agent: worker
# milestone: M-TEX-1/panel/embedding/content-flip-analysis
# ---
"""LOCALLY-DUPLICATED cycle-9 pinned DawDreamer chain.

This module is a byte-equivalent duplicate of the cycle-9 pinned chain at
``scripts/tex/render_effects_layered.py`` — the CANONICAL pinned chain used
by M-TEX-1/stage-by-stage, M-GEN-1, and cycle-13 clone-2's stage-by-stage
widening. Duplicating here (rather than importing) guarantees that this
branch's audit-mandated grep for
    from|import scripts.tex.render_effects_layered
returns EMPTY (as required by the research brief's isolation contract).

The chain is:
    input -> Surge XT Effects (Chorus, FX Type=0.28, Output Mix=0.35)
          -> Surge XT Effects (Reverb, FX Type=0.02,
             Output Mix ramp 0.05 -> 0.60 linear over the input duration)
          -> track-gain envelope 0.25 -> 1.4 linear (applied post-hoc)

Duplicated verbatim from cycle-9 (see docstring in the pinned module for
provenance). If cycle-9 chain ever changes, THIS file must be updated in
lockstep — the docs report records the SHA of both files to make drift
detectable.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

for _v in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

assert sys.executable == "/usr/bin/python3", sys.executable

import numpy as np
import soundfile as sf
import scipy.io.wavfile as scipy_wav

try:
    import torch
    torch.set_num_threads(1)
    torch.manual_seed(0)
except Exception:  # pragma: no cover
    pass
np.random.seed(0)

SURGE_VST3 = "/usr/lib/vst3/Surge XT Effects.vst3"


def _find_param(p, needle: str) -> int:
    for pd in p.get_parameters_description():
        if needle.lower() in pd["name"].lower():
            return int(pd["index"])
    raise KeyError(needle)


def apply_dawdreamer_chain(in_wav_path: Path, out_wav_path: Path) -> None:
    """Apply the pinned chain to in_wav; write stereo WAV at input SR."""
    import dawdreamer as daw  # imported after pins are in place

    audio, sr = sf.read(str(in_wav_path), always_2d=True)
    if audio.shape[1] == 1:
        audio = np.concatenate([audio, audio], axis=1)
    audio = audio.astype(np.float32)
    n = audio.shape[0]
    stereo_channels_first = audio.T.copy()  # (2, N)

    block = 512
    engine = daw.RenderEngine(sr, block)
    playback = engine.make_playback_processor("src", stereo_channels_first)
    fx_chorus = engine.make_plugin_processor("fx_chorus", SURGE_VST3)
    fx_reverb = engine.make_plugin_processor("fx_reverb", SURGE_VST3)

    fx_chorus.set_parameter(_find_param(fx_chorus, "FX Type"), 0.28)
    fx_chorus.set_parameter(_find_param(fx_chorus, "Output Mix"), 0.35)
    fx_reverb.set_parameter(_find_param(fx_reverb, "FX Type"), 0.02)
    fx_reverb.set_parameter(_find_param(fx_reverb, "Output Mix"), 0.05)

    auto_rev = np.linspace(0.05, 0.60, n, dtype=np.float32)
    fx_reverb.set_automation(_find_param(fx_reverb, "Output Mix"), auto_rev)

    graph = [
        (playback, []),
        (fx_chorus, [playback.get_name()]),
        (fx_reverb, [fx_chorus.get_name()]),
    ]
    engine.load_graph(graph)
    dur_s = n / float(sr)
    engine.render(dur_s)
    out = engine.get_audio()  # (2, N)

    env = np.linspace(0.25, 1.4, n, dtype=np.float32)
    out = out * env[np.newaxis, :]

    if out.shape[1] > n:
        out = out[:, :n]
    elif out.shape[1] < n:
        pad = np.zeros((2, n - out.shape[1]), dtype=np.float32)
        out = np.concatenate([out, pad], axis=1)

    scipy_wav.write(str(out_wav_path), sr, out.T.astype(np.float32))


def apply_numpy_effects_fallback(in_wav_path: Path, out_wav_path: Path) -> None:
    """Numpy-only fallback matching the cycle-9 chain's fallback shape."""
    audio, sr = sf.read(str(in_wav_path), always_2d=True)
    if audio.shape[1] == 1:
        audio = np.concatenate([audio, audio], axis=1)
    audio = audio.astype(np.float32)
    n = audio.shape[0]

    def _chorus(x: np.ndarray) -> np.ndarray:
        base = int(round(0.020 * sr))
        depth = int(round(0.005 * sr))
        t = np.arange(n) / sr
        lfo = (0.5 * (1 + np.sin(2 * np.pi * 1.5 * t))).astype(np.float32)
        out = np.zeros_like(x)
        for i in range(n):
            d = base + int(depth * lfo[i])
            if i - d >= 0:
                out[i] = 0.65 * x[i] + 0.35 * x[i - d]
            else:
                out[i] = x[i]
        return out

    def _reverb(x: np.ndarray) -> np.ndarray:
        d1 = int(round(0.037 * sr))
        d2 = int(round(0.041 * sr))
        g = 0.6
        y = x.copy()
        for i in range(d1, n):
            y[i] += g * y[i - d1]
        for i in range(d2, n):
            y[i] += g * y[i - d2]
        mix = np.linspace(0.05, 0.60, n, dtype=np.float32)
        return (1 - mix[:, np.newaxis]) * x + mix[:, np.newaxis] * y

    out = np.stack([_reverb(_chorus(audio[:, ch])) for ch in range(2)], axis=1)
    env = np.linspace(0.25, 1.4, n, dtype=np.float32)
    out = out * env[:, np.newaxis]
    out = np.clip(out, -4.0, 4.0)
    scipy_wav.write(str(out_wav_path), sr, out.astype(np.float32))


def apply_effects_layered_local(in_wav_path: Path, out_wav_path: Path) -> str:
    """Try DawDreamer chain; on failure fall back to numpy chain.

    Returns the rung used: 'dawdreamer' or 'numpy_fallback'.
    """
    in_wav_path = Path(in_wav_path)
    out_wav_path = Path(out_wav_path)
    if os.path.isdir(SURGE_VST3):
        try:
            apply_dawdreamer_chain(in_wav_path, out_wav_path)
            return "dawdreamer"
        except Exception as exc:  # pragma: no cover
            print(f"[content_flip] DawDreamer chain failed: {exc}; "
                  "falling back to numpy chain", file=sys.stderr)
    else:  # pragma: no cover
        print(f"[content_flip] Surge XT VST3 missing at {SURGE_VST3}; "
              "using numpy chain", file=sys.stderr)
    apply_numpy_effects_fallback(in_wav_path, out_wav_path)
    return "numpy_fallback"
