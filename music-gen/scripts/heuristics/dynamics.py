# dynamics_quality — mess-scale [0,1] via crest factor + envelope-range ratio + envelope variance dB
# created: 2026-08-28T05:20:00Z  cycle: 4  run_id: run-2026-08-28T040704Z
# agent: worker (clone-1)  milestone: M-HEUR-1/dynamics
"""Dynamics heuristic.

Features:
- crest_factor         = max(|y|) / rms(y)
- envelope_range_ratio = p95(rms) / p05(rms), clipped to [1, 20] then log2-normalized to [0,1]
- envelope_variance    = std(rms_dB) / 12.0    (12 dB is a coarse "expressive" ceiling)

Null-with-reason: len(y)/sr < 5.0 → mess_scale=None, reason="too_short_for_dynamics".
"""
from __future__ import annotations

import math

import librosa
import numpy as np

from .mess_scale import HeuristicResult, blend, mess_scale


BLIND_SPOTS = (
    "heavily compressed / mastered audio collapses toward the loudness-war floor: crest factor ≈ 3-4× and envelope_range_ratio ≈ 1-2× regardless of the actual musical dynamics.",
    "silence pockets inside a clip inflate p95/p05 ratio spuriously; a bar of rest between two loud events reads as huge dynamic range without any actual crescendo.",
    "envelope-variance dB is undefined for silent frames; the mixer floor (−80 dB fallback) truncates near-silent passages and biases variance downward.",
    "the crest factor is a scalar and cannot distinguish 'one loud transient in a quiet piece' from 'a piece that alternates loud and quiet'.",
)

CREST_ANCHORS = ((2.0, 0.0), (4.0, 0.3), (8.0, 0.7), (20.0, 1.0))
RANGE_RATIO_LOG_ANCHORS = ((0.0, 0.0), (1.0, 0.35), (2.5, 0.75), (4.3, 1.0))  # log2(1)=0..log2(20)≈4.32
ENV_VAR_ANCHORS = ((0.0, 0.0), (0.15, 0.3), (0.5, 0.7), (1.0, 1.0))

MIN_CLIP_S = 5.0


def dynamics_quality(y: np.ndarray, sr: int) -> HeuristicResult:
    np.random.seed(0)
    name = "dynamics_quality"
    raw: dict = {
        "duration_s": None,
        "crest_factor": None,
        "envelope_p95_rms": None,
        "envelope_p05_rms": None,
        "envelope_range_ratio": None,
        "envelope_variance_db": None,
    }
    if y.size == 0:
        return HeuristicResult(name, raw, None, "empty_audio", BLIND_SPOTS)
    dur_s = y.size / float(sr)
    raw["duration_s"] = dur_s
    if dur_s < MIN_CLIP_S:
        return HeuristicResult(name, raw, None, "too_short_for_dynamics", BLIND_SPOTS)

    peak = float(np.max(np.abs(y)))
    rms_whole = float(np.sqrt(np.mean(y * y)))
    if rms_whole < 1e-9:
        return HeuristicResult(name, raw, None, "silent_audio", BLIND_SPOTS)
    crest = peak / rms_whole
    raw["crest_factor"] = crest

    rms = librosa.feature.rms(y=y, hop_length=512)[0]
    if rms.size < 4:
        return HeuristicResult(name, raw, None, "too_few_rms_frames", BLIND_SPOTS)
    p95 = float(np.percentile(rms, 95))
    p05 = float(np.percentile(rms, 5))
    raw["envelope_p95_rms"] = p95
    raw["envelope_p05_rms"] = p05
    ratio = p95 / max(p05, 1e-9)
    ratio_clipped = min(max(ratio, 1.0), 20.0)
    raw["envelope_range_ratio"] = ratio
    log2_ratio = math.log2(ratio_clipped)

    rms_db = 20.0 * np.log10(np.maximum(rms, 10 ** (-80 / 20)))
    env_std_db = float(np.std(rms_db))
    env_var_norm = env_std_db / 12.0
    raw["envelope_variance_db"] = env_std_db

    m_crest = mess_scale(crest, CREST_ANCHORS)
    m_range = mess_scale(log2_ratio, RANGE_RATIO_LOG_ANCHORS)
    m_var = mess_scale(env_var_norm, ENV_VAR_ANCHORS)
    m = blend((m_crest, m_range, m_var), (0.25, 0.4, 0.35))
    raw["mess__crest"] = m_crest
    raw["mess__range"] = m_range
    raw["mess__envvar"] = m_var
    return HeuristicResult(name, raw, m, None, BLIND_SPOTS)
