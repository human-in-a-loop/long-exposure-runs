#!/usr/bin/python3
"""Tap-test helpers (D1). 25 Hz sine click at estimated beats, mixed 30% under.

Renders click tracks the researcher can listen to. Winner selection when
madmom is unavailable is ``LIBROSA_UNCONTESTED`` (self-consistency check).
"""
from __future__ import annotations

import pathlib
from typing import Iterable, Optional

import numpy as np
import soundfile as sf

CLICK_FREQ_HZ = 25.0
CLICK_DUR_S = 0.03  # 30 ms tap
CLICK_AMPLITUDE = 0.3  # -10 dB
SR_TAP = 44100


def render_click(beat_times_s: Iterable[float], duration_s: float, sr: int = SR_TAP) -> np.ndarray:
    n = int(round(duration_s * sr))
    y = np.zeros(n, dtype=np.float32)
    tap_len = int(round(CLICK_DUR_S * sr))
    t = np.arange(tap_len) / sr
    tap = (np.sin(2.0 * np.pi * CLICK_FREQ_HZ * t)
           * np.hanning(tap_len)).astype(np.float32) * CLICK_AMPLITUDE
    for tb in beat_times_s:
        i = int(round(float(tb) * sr))
        j = min(n, i + tap_len)
        if 0 <= i < n:
            y[i:j] += tap[: (j - i)]
    return y


def mix_click_under_baseline(baseline: np.ndarray, click: np.ndarray, sr: int) -> np.ndarray:
    """Assumes mono baseline (or stereo -> mono) and mono click."""
    if baseline.ndim > 1:
        baseline = baseline.mean(axis=1)
    n = min(len(baseline), len(click))
    out = np.zeros(n, dtype=np.float32)
    out[:] = 0.7 * baseline[:n] + click[:n]  # 30% under (click at 0.3 amp, baseline at 0.7)
    peak = float(np.max(np.abs(out)) or 1.0)
    if peak > 1.0:
        out = (out / peak).astype(np.float32)
    return out


def emit_tap_wav(path: pathlib.Path, y: np.ndarray, sr: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    sf.write(str(path), y, sr, subtype="PCM_16")
