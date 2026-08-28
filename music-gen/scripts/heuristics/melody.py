# melody_quality — mess-scale [0,1] via pyin contour smoothness + interval variety + PCP entropy
# created: 2026-08-28T05:20:00Z  cycle: 4  run_id: run-2026-08-28T040704Z
# agent: worker (clone-1)  milestone: M-HEUR-1/melody
"""Melody heuristic.

Extracts F0 with librosa.pyin (C2..C7), drops unvoiced frames.

Features:
- contour_smoothness = 1 / (1 + Δpitch_semitones_RMS)
- interval_variety   = min(1.0, unique_intervals / 12)
- pitch_class_entropy = H(pcp) / log2(12), pcp = normalized pitch-class histogram

Blend: 0.4·smoothness + 0.3·variety + 0.3·entropy.

Null-with-reason: voiced-frame fraction < 0.1 → mess_scale=None,
reason="unvoiced_dominant".
"""
from __future__ import annotations

import math

import librosa
import numpy as np

from .mess_scale import HeuristicResult, blend, mess_scale


BLIND_SPOTS = (
    "percussion-only or noise tracks: pyin is not meaningful; falls back to null-with-reason when voiced-frame fraction < 0.1, but partially-pitched percussion (e.g. tuned toms) can slip through with meaningless F0.",
    "polyphonic content: pyin picks a single salient F0 per frame; harmony and counterpoint are collapsed to the loudest voice.",
    "atonal vs. tonal bias: pitch-class entropy penalizes strongly tonal music (a diatonic piece caps around H/log2(12) ≈ log2(7)/log2(12) ≈ 0.78) more than atonal / 12-tone material.",
    "octave errors: pyin may octave-jump; the smoothness feature is sensitive to these as ±12 semitone spikes.",
)

SMOOTHNESS_ANCHORS = ((0.0, 0.0), (0.25, 0.35), (0.55, 0.75), (0.85, 1.0))
VARIETY_ANCHORS = ((0.0, 0.0), (0.25, 0.35), (0.5, 0.7), (1.0, 1.0))
ENTROPY_ANCHORS = ((0.0, 0.0), (0.4, 0.4), (0.7, 0.85), (1.0, 1.0))


def melody_quality(y: np.ndarray, sr: int) -> HeuristicResult:
    np.random.seed(0)  # determinism plant; pyin is deterministic but future-proof
    name = "melody_quality"
    raw: dict = {
        "voiced_fraction": None,
        "pitch_delta_semitones_rms": None,
        "unique_interval_count": None,
        "contour_smoothness": None,
        "interval_variety": None,
        "pitch_class_entropy": None,
    }
    if y.size == 0:
        return HeuristicResult(name, raw, None, "empty_audio", BLIND_SPOTS)

    f0, voiced_flag, voiced_prob = librosa.pyin(
        y,
        fmin=librosa.note_to_hz("C2"),
        fmax=librosa.note_to_hz("C7"),
        sr=sr,
        frame_length=2048,
    )
    voiced_fraction = float(np.nan_to_num(voiced_flag).mean())
    raw["voiced_fraction"] = voiced_fraction
    if voiced_fraction < 0.1:
        return HeuristicResult(name, raw, None, "unvoiced_dominant", BLIND_SPOTS)

    voiced = f0[np.isfinite(f0) & (voiced_flag == True)]  # noqa: E712
    if voiced.size < 3:
        return HeuristicResult(name, raw, None, "too_few_voiced_frames", BLIND_SPOTS)

    semitones = 12.0 * np.log2(voiced / 440.0) + 69.0  # MIDI pitch space
    deltas = np.diff(semitones)
    delta_rms = float(np.sqrt(np.mean(deltas * deltas)))
    contour_smoothness = 1.0 / (1.0 + delta_rms)
    raw["pitch_delta_semitones_rms"] = delta_rms
    raw["contour_smoothness"] = contour_smoothness

    # Interval variety: rounded to nearest semitone, absolute
    intervals_int = np.rint(np.abs(deltas)).astype(int)
    unique_intervals = int(len(set(int(x) for x in intervals_int if x != 0)))
    interval_variety = min(1.0, unique_intervals / 12.0)
    raw["unique_interval_count"] = float(unique_intervals)
    raw["interval_variety"] = interval_variety

    # Pitch-class entropy
    pcs = np.rint(semitones).astype(int) % 12
    hist = np.bincount(pcs, minlength=12).astype(float)
    if hist.sum() == 0:
        return HeuristicResult(name, raw, None, "empty_pitch_histogram", BLIND_SPOTS)
    p = hist / hist.sum()
    p_nonzero = p[p > 0]
    H = float(-(p_nonzero * np.log2(p_nonzero)).sum())
    entropy_norm = H / math.log2(12)
    raw["pitch_class_entropy"] = entropy_norm

    m_smooth = mess_scale(contour_smoothness, SMOOTHNESS_ANCHORS)
    m_var = mess_scale(interval_variety, VARIETY_ANCHORS)
    m_ent = mess_scale(entropy_norm, ENTROPY_ANCHORS)
    m = blend((m_smooth, m_var, m_ent), (0.4, 0.3, 0.3))
    raw["mess__smoothness"] = m_smooth
    raw["mess__variety"] = m_var
    raw["mess__entropy"] = m_ent
    return HeuristicResult(name, raw, m, None, BLIND_SPOTS)
