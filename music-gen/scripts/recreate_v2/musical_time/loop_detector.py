#!/usr/bin/python3
"""D3 Loop-length detection via bar-level SSM + autocorr-peak method.

Per-bar feature: 12-D chroma-CQT mean + 1-D onset density.
Pairwise cosine SSM → autocorrelate diagonal → argmax at lag > 1.
"""
from __future__ import annotations

import json
import pathlib
from typing import Any, Dict, List

import numpy as np

MIN_BARS = 4


def _l2n(x: np.ndarray, axis: int = -1) -> np.ndarray:
    n = np.linalg.norm(x, axis=axis, keepdims=True)
    return x / np.where(n < 1e-12, 1.0, n)


def bar_boundaries(
    downbeat_start_s: float, tempo_bpm: float, beats_per_bar: int, duration_s: float
) -> np.ndarray:
    if tempo_bpm <= 0:
        return np.array([downbeat_start_s, duration_s], dtype=np.float64)
    bar_s = 60.0 / tempo_bpm * beats_per_bar
    n = int(np.floor((duration_s - downbeat_start_s) / bar_s)) + 1
    return downbeat_start_s + np.arange(n + 1) * bar_s


def per_bar_features(
    y_mono: np.ndarray, sr: int, bar_edges_s: np.ndarray
) -> np.ndarray:
    """Return (N_bars, 13) array — 12 chroma + 1 onset-density."""
    import librosa

    hop = 512
    chroma = librosa.feature.chroma_cqt(y=y_mono, sr=sr, hop_length=hop)
    onset_env = librosa.onset.onset_strength(y=y_mono, sr=sr, hop_length=hop)
    frames_per_s = sr / hop
    duration_s = len(y_mono) / sr

    n_bars = max(0, len(bar_edges_s) - 1)
    feats = np.zeros((n_bars, 13), dtype=np.float64)
    for i in range(n_bars):
        t0 = float(bar_edges_s[i])
        t1 = float(bar_edges_s[i + 1])
        if t1 <= 0 or t0 >= duration_s or t1 <= t0:
            continue
        f0 = max(0, int(round(t0 * frames_per_s)))
        f1 = max(f0 + 1, int(round(t1 * frames_per_s)))
        f1 = min(f1, chroma.shape[1])
        if f1 <= f0:
            continue
        feats[i, :12] = chroma[:, f0:f1].mean(axis=1)
        feats[i, 12] = float(onset_env[f0:f1].sum() / max(1e-6, (t1 - t0)))
    return feats


def compute_loop_length(feats: np.ndarray) -> Dict[str, Any]:
    """Return loop-length verdict from per-bar features.

    Confidence is computed mean-centered against off-lag baseline so that
    values near 1.0 are only reachable for truly periodic content. Search
    is restricted to lag ∈ [2, N // 2] so that K = floor(N / lag) ≥ 2 —
    the aggregator has ≥ 2 repeats to vote on (K=1 would be trivial).
    """
    n_bars = feats.shape[0]
    if n_bars < MIN_BARS:
        return {
            "loop_length_bars": 0,
            "loop_length_confidence": 0.0,
            "ssm_diag_shape": [n_bars, n_bars],
            "autocorr_peaks": [],
            "reason": "insufficient_bars",
        }

    F = _l2n(feats, axis=1)
    ssm = F @ F.T  # (n_bars, n_bars) cosine similarity (features l2-normed)

    autocorr: List[float] = []
    for lag in range(0, n_bars):
        diag = np.diagonal(ssm, offset=lag)
        autocorr.append(float(diag.mean()))
    autocorr_a = np.asarray(autocorr, dtype=np.float64)

    max_lag = max(2, n_bars // 2)
    if max_lag < 2:
        best_lag = 0
        conf = 0.0
    else:
        # Search only lags that admit ≥ 2 repeats.
        search = autocorr_a[2 : max_lag + 1]
        if search.size == 0:
            best_lag = 0
            conf = 0.0
        else:
            best_lag = int(np.argmax(search) + 2)
            # Mean-centered confidence: peak – mean-of-off-lags, normalised
            # by (1 − mean-of-off-lags) so a perfectly periodic signal gives 1.0
            # and an aperiodic signal (peak == baseline) gives 0.
            baseline_mask = np.ones_like(autocorr_a, dtype=bool)
            baseline_mask[0] = False
            baseline_mask[best_lag] = False
            baseline = float(autocorr_a[baseline_mask].mean()) if baseline_mask.any() else 0.0
            peak = float(autocorr_a[best_lag])
            denom = max(1e-12, 1.0 - baseline)
            conf = float(max(0.0, (peak - baseline) / denom))

    return {
        "loop_length_bars": int(best_lag),
        "loop_length_confidence": conf,
        "ssm_diag_shape": [int(n_bars), int(n_bars)],
        "autocorr_peaks": [float(x) for x in autocorr_a.tolist()],
    }


def emit_loop_length(out_path: pathlib.Path, result: Dict[str, Any]) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2, sort_keys=True))
