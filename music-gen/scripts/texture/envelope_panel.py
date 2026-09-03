#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-08-28T05:20:00Z
# cycle: 4
# run_id: run-2026-08-28T040704Z
# agent: worker
# milestone: M-TEX-1/panel/envelope
# ---
"""Dynamics envelope panel: RMS-envelope RMSE + LUFS-M RMSE.

RMS: mono-mixed, ``librosa.feature.rms`` at hop=512 n_fft=2048.
LUFS-M: momentary loudness per EBU R128 (400 ms integration, 100 ms hop),
computed on stereo input (mono is duplicated to stereo internally).
Values below -70 LUFS (R128 absolute silence gate) are dropped.
"""
from __future__ import annotations

import numpy as np
import librosa
import pyloudnorm as pyln

from .spectral_panel import HOP_LENGTH, N_FFT, _to_mono

LUFS_WINDOW_S = 0.400
LUFS_HOP_S = 0.100
LUFS_ABS_GATE = -70.0  # EBU R128 absolute silence gate


def rms_envelope_rmse(a: np.ndarray, b: np.ndarray, sr: int) -> float:
    a_m = _to_mono(a)
    b_m = _to_mono(b)
    n = min(len(a_m), len(b_m))
    a_m, b_m = a_m[:n], b_m[:n]
    rms_a = librosa.feature.rms(y=a_m, frame_length=N_FFT, hop_length=HOP_LENGTH)[0]
    rms_b = librosa.feature.rms(y=b_m, frame_length=N_FFT, hop_length=HOP_LENGTH)[0]
    nf = min(len(rms_a), len(rms_b))
    return float(np.sqrt(np.mean((rms_a[:nf] - rms_b[:nf]) ** 2)))


def _ensure_stereo(a: np.ndarray) -> np.ndarray:
    a = np.asarray(a, dtype=np.float32)
    if a.ndim == 1:
        return np.stack([a, a], axis=1)  # (samples, 2)
    if a.ndim == 2:
        if a.shape[1] <= 8 and a.shape[0] > a.shape[1]:
            return a  # already (samples, channels)
        return a.T
    raise ValueError(f"unsupported audio ndim={a.ndim}")


def _lufs_momentary_envelope(a: np.ndarray, sr: int) -> np.ndarray:
    """Return a 1-D array of momentary LUFS values, one per 100 ms hop,
    with below-gate values dropped."""
    meter = pyln.Meter(sr, block_size=LUFS_WINDOW_S)
    stereo = _ensure_stereo(a)
    win = int(round(LUFS_WINDOW_S * sr))
    hop = int(round(LUFS_HOP_S * sr))
    n = stereo.shape[0]
    if n < win:
        return np.array([], dtype=np.float32)
    values = []
    for start in range(0, n - win + 1, hop):
        block = stereo[start:start + win]
        try:
            lufs = meter.integrated_loudness(block)
        except Exception:
            lufs = -np.inf
        if np.isfinite(lufs) and lufs > LUFS_ABS_GATE:
            values.append(lufs)
        else:
            values.append(np.nan)
    return np.asarray(values, dtype=np.float32)


def lufs_m_rmse_lu(a: np.ndarray, b: np.ndarray, sr: int) -> float:
    la = _lufs_momentary_envelope(a, sr)
    lb = _lufs_momentary_envelope(b, sr)
    nf = min(len(la), len(lb))
    if nf == 0:
        return float("nan")
    la, lb = la[:nf], lb[:nf]
    # keep only frames where BOTH sides are un-gated (finite).
    mask = np.isfinite(la) & np.isfinite(lb)
    if not mask.any():
        return float("nan")
    return float(np.sqrt(np.mean((la[mask] - lb[mask]) ** 2)))


def envelope_metrics(a: np.ndarray, b: np.ndarray, sr: int) -> dict:
    return {
        "rms_env_rmse": rms_envelope_rmse(a, b, sr),
        "lufs_m_rmse_lu": lufs_m_rmse_lu(a, b, sr),
    }
