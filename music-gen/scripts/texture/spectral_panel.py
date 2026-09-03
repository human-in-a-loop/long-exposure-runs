#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-08-28T05:20:00Z
# cycle: 4
# run_id: run-2026-08-28T040704Z
# agent: worker
# milestone: M-TEX-1/panel/spectral
# ---
"""Spectral panel: multi-scale log-mel L1 (dB) + spectral centroid RMSE (Hz).

Channel policy: MONO mix-down via ``librosa.to_mono``.
STFT: hop_length=512, n_fft=2048.
Multi-scale n_mels: {64, 128, 256} averaged. The 128-mel scale matches
clone-1's DAW-spike agreement panel (scripts/daw/agreement.py); the multi-
scale panel adds 64 and 256 on top.

log-mel dB uses ``librosa.power_to_db(mel + 1e-10)`` (same eps as clone-1).
"""
from __future__ import annotations

import numpy as np
import librosa

HOP_LENGTH = 512
N_FFT = 2048
N_MELS_SCALES = (64, 128, 256)


def _to_mono(a: np.ndarray) -> np.ndarray:
    a = np.asarray(a, dtype=np.float32)
    if a.ndim == 1:
        return a
    if a.ndim == 2:
        # librosa convention: (channels, samples). Accept (samples, channels) too.
        if a.shape[0] <= 8 and a.shape[1] > a.shape[0]:
            return librosa.to_mono(a)
        return librosa.to_mono(a.T)
    raise ValueError(f"unsupported audio ndim={a.ndim}")


def _mel_l1_db_single(a: np.ndarray, b: np.ndarray, sr: int, n_mels: int) -> float:
    mel_a = librosa.feature.melspectrogram(y=a, sr=sr, n_mels=n_mels, hop_length=HOP_LENGTH, n_fft=N_FFT)
    mel_b = librosa.feature.melspectrogram(y=b, sr=sr, n_mels=n_mels, hop_length=HOP_LENGTH, n_fft=N_FFT)
    log_a = librosa.power_to_db(mel_a + 1e-10)
    log_b = librosa.power_to_db(mel_b + 1e-10)
    return float(np.mean(np.abs(log_a - log_b)))


def mel_l1_db_multiscale(a: np.ndarray, b: np.ndarray, sr: int) -> dict:
    """Return per-scale mel L1 (dB) and their mean."""
    a_m = _to_mono(a)
    b_m = _to_mono(b)
    n = min(len(a_m), len(b_m))
    a_m, b_m = a_m[:n], b_m[:n]
    per_scale = {n_mels: _mel_l1_db_single(a_m, b_m, sr, n_mels) for n_mels in N_MELS_SCALES}
    return {
        "per_scale": per_scale,
        "mean": float(np.mean(list(per_scale.values()))),
    }


def spectral_centroid_rmse_hz(a: np.ndarray, b: np.ndarray, sr: int) -> float:
    a_m = _to_mono(a)
    b_m = _to_mono(b)
    n = min(len(a_m), len(b_m))
    a_m, b_m = a_m[:n], b_m[:n]
    sc_a = librosa.feature.spectral_centroid(y=a_m, sr=sr, hop_length=HOP_LENGTH, n_fft=N_FFT)[0]
    sc_b = librosa.feature.spectral_centroid(y=b_m, sr=sr, hop_length=HOP_LENGTH, n_fft=N_FFT)[0]
    nf = min(len(sc_a), len(sc_b))
    return float(np.sqrt(np.mean((sc_a[:nf] - sc_b[:nf]) ** 2)))


def spectral_metrics(a: np.ndarray, b: np.ndarray, sr: int) -> dict:
    """Panel-facing entry. Returns dict with two keys.

    ``mel_l1_db`` is the mean across the three mel scales. The per-scale
    breakdown is stashed on the returned dict under ``_mel_l1_db_per_scale``
    for diagnostics but is NOT part of the panel's public seven-key contract.
    """
    ms = mel_l1_db_multiscale(a, b, sr)
    return {
        "mel_l1_db": ms["mean"],
        "spectral_centroid_rmse_hz": spectral_centroid_rmse_hz(a, b, sr),
        "_mel_l1_db_per_scale": ms["per_scale"],
    }
