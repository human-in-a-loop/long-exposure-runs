# timbre_quality — mess-scale [0,1] via MFCC-delta RMS + centroid range + flatness variance
# created: 2026-08-28T05:20:00Z  cycle: 4  run_id: run-2026-08-28T040704Z
# agent: worker (clone-1)  milestone: M-HEUR-1/timbre
"""Timbre heuristic.

Features:
- mfcc_delta_rms   = mean(|MFCC[t] - MFCC[t-1]|) across the 13 coefficients,
                     normalized by a nominal per-step scale.
- centroid_range   = (p95 - p05)(spectral_centroid) / (sr/4). The (sr/4)
                     denominator is a coarse Nyquist-half normalization.
- flatness_variance = std(spectral_flatness).
"""
from __future__ import annotations

import librosa
import numpy as np

from .mess_scale import HeuristicResult, blend, mess_scale


BLIND_SPOTS = (
    "low-SNR (noisy or lo-fi) audio biases spectral centroid downward, deflating centroid_range irrespective of true timbral motion.",
    "MFCC-delta RMS conflates timbral evolution with note onsets; at 512-hop resolution the two are inseparable.",
    "reverb widens perceived spectral flatness spuriously; a wet reverb-tail track scores as more timbrally varied than a dry version of the same source.",
    "silence-padded clips flatten every feature; near-silent audio scores toward the low anchor for all three features.",
)

MFCC_DELTA_ANCHORS = ((0.0, 0.0), (5.0, 0.3), (15.0, 0.7), (35.0, 1.0))
CENTROID_RANGE_ANCHORS = ((0.0, 0.0), (0.05, 0.4), (0.2, 0.8), (0.4, 1.0))
FLATNESS_VAR_ANCHORS = ((0.0, 0.0), (0.02, 0.3), (0.08, 0.7), (0.2, 1.0))


def timbre_quality(y: np.ndarray, sr: int) -> HeuristicResult:
    np.random.seed(0)
    name = "timbre_quality"
    raw: dict = {
        "mfcc_delta_rms": None,
        "spectral_centroid_p95_hz": None,
        "spectral_centroid_p05_hz": None,
        "centroid_range_norm": None,
        "flatness_variance": None,
    }
    if y.size == 0:
        return HeuristicResult(name, raw, None, "empty_audio", BLIND_SPOTS)
    if float(np.abs(y).max()) < 1e-6:
        return HeuristicResult(name, raw, None, "silent_audio", BLIND_SPOTS)

    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
    if mfcc.shape[1] < 2:
        return HeuristicResult(name, raw, None, "too_short_for_mfcc", BLIND_SPOTS)
    deltas = np.abs(np.diff(mfcc, axis=1))
    mfcc_delta_rms = float(np.sqrt(np.mean(deltas * deltas)))
    raw["mfcc_delta_rms"] = mfcc_delta_rms

    centroid = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
    p95 = float(np.percentile(centroid, 95))
    p05 = float(np.percentile(centroid, 5))
    centroid_range = (p95 - p05) / (sr / 4.0)
    raw["spectral_centroid_p95_hz"] = p95
    raw["spectral_centroid_p05_hz"] = p05
    raw["centroid_range_norm"] = centroid_range

    flatness = librosa.feature.spectral_flatness(y=y)[0]
    flatness_var = float(np.std(flatness))
    raw["flatness_variance"] = flatness_var

    m_mfcc = mess_scale(mfcc_delta_rms, MFCC_DELTA_ANCHORS)
    m_cent = mess_scale(centroid_range, CENTROID_RANGE_ANCHORS)
    m_flat = mess_scale(flatness_var, FLATNESS_VAR_ANCHORS)
    m = blend((m_mfcc, m_cent, m_flat), (0.4, 0.35, 0.25))
    raw["mess__mfcc_delta"] = m_mfcc
    raw["mess__centroid_range"] = m_cent
    raw["mess__flatness_var"] = m_flat
    return HeuristicResult(name, raw, m, None, BLIND_SPOTS)
