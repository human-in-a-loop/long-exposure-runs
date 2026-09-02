#!/usr/bin/env /usr/bin/python3
# D3+D5 onset-segmented pyin + articulation encoder producing v2 notes JSON schema:
#   {onset_s: float, duration_s: float, midi: int, velocity: int,
#    articulation: str in {"sustained","ghost","slap"}}
# created: 2026-09-02, cycle 55, run-2026-08-28T040704Z, worker, fork 7cc01d726807 clone-1
import numpy as np
import librosa

from ._common import MIN_DURATION_S, FMIN_HZ, FMAX_HZ
from .slap import detect_slaps


ONSET_DELTA = 0.02   # low-delta captures ghost notes
HOP = 512
FRAME_LEN = 2048
GHOST_MAX_DUR_S = 0.080
GHOST_MAX_VEL = 50
SUSTAINED_VEL_MIN = 40
SUSTAINED_VEL_MAX = 90
SLAP_VELOCITY = 100


def detect_onsets(y, sr):
    """librosa.onset.onset_detect with low delta + backtrack (D3)."""
    frames = librosa.onset.onset_detect(
        y=y, sr=sr, hop_length=HOP, delta=ONSET_DELTA, backtrack=True, units="frames"
    )
    times = librosa.frames_to_time(frames, sr=sr, hop_length=HOP)
    return times.astype(np.float64), frames.astype(np.int64)


def _pyin_median_midi(y_seg, sr):
    """Run pyin on a segment, return (midi_int or None, median_voiced_prob)."""
    if len(y_seg) < FRAME_LEN:
        return None, 0.0
    try:
        f0, vf, vp = librosa.pyin(
            y_seg, sr=sr, fmin=FMIN_HZ, fmax=FMAX_HZ,
            hop_length=HOP, frame_length=FRAME_LEN, center=True,
        )
    except Exception:
        return None, 0.0
    finite = np.isfinite(f0) & vf
    if not finite.any():
        return None, 0.0
    med_vp = float(np.median(vp[finite]))
    if med_vp <= 0.1:
        return None, med_vp
    f0v = f0[finite]
    hz = float(np.median(f0v))
    if not np.isfinite(hz) or hz <= 0:
        return None, med_vp
    midi = int(round(float(librosa.hz_to_midi(hz))))
    return midi, med_vp


def _segment_rms(y_seg):
    if len(y_seg) == 0:
        return 0.0
    return float(np.sqrt(np.mean(y_seg ** 2) + 1e-12))


def transcribe_bass_v2(y, sr):
    """Return list of v2 notes. Same-pitch consecutive onsets become SEPARATE notes.

    Per D3: onset-segmented pyin (fmin=E1, fmax=E4). Per D4: slap detector on
    original bass stem. Per D5: articulation-priority (slap > ghost > sustained).
    """
    onset_times, _ = detect_onsets(y, sr)
    if len(onset_times) == 0:
        return []

    # Build inter-onset intervals; the last interval extends to end-of-signal.
    dur = len(y) / sr
    boundaries = np.concatenate([onset_times, [dur]])
    slap_flags = detect_slaps(y, sr, onset_times.tolist())

    # Pass 1: compute per-interval midi, raw RMS peak, duration.
    intervals = []
    for i in range(len(onset_times)):
        t0 = float(onset_times[i])
        t1 = float(boundaries[i + 1])
        seg_dur = t1 - t0
        if seg_dur < MIN_DURATION_S:
            intervals.append(None)
            continue
        i0 = int(round(t0 * sr))
        i1 = min(len(y), int(round(t1 * sr)))
        y_seg = y[i0:i1]
        midi, _mvp = _pyin_median_midi(y_seg, sr)
        if midi is None:
            intervals.append(None)
            continue
        rms = _segment_rms(y_seg)
        intervals.append({
            "onset_s": t0,
            "duration_s": seg_dur,
            "midi": midi,
            "rms_peak": rms,
            "slap": bool(slap_flags[i]),
        })

    # Pass 2: peak-normalize RMS across valid intervals for velocity mapping.
    rms_values = [iv["rms_peak"] for iv in intervals if iv is not None]
    max_rms = max(rms_values) if rms_values else 1.0
    if max_rms <= 0:
        max_rms = 1.0

    notes = []
    for iv in intervals:
        if iv is None:
            continue
        # Priority-ordered articulation
        if iv["slap"]:
            articulation = "slap"
            velocity = SLAP_VELOCITY
        else:
            # non-slap velocity: RMS-peak → [40, 90] linearly, peak-normalized per song
            rel = iv["rms_peak"] / max_rms
            velocity = int(round(SUSTAINED_VEL_MIN + rel * (SUSTAINED_VEL_MAX - SUSTAINED_VEL_MIN)))
            velocity = max(1, min(127, velocity))
            if iv["duration_s"] < GHOST_MAX_DUR_S and velocity < GHOST_MAX_VEL:
                articulation = "ghost"
            else:
                articulation = "sustained"
        notes.append({
            "onset_s": float(iv["onset_s"]),
            "duration_s": float(iv["duration_s"]),
            "midi": int(iv["midi"]),
            "velocity": int(velocity),
            "articulation": articulation,
        })
    return notes


def onset_reference(y, sr):
    """Reference bass onsets for the D6 metric-1 F1 computation."""
    onset_times, _ = detect_onsets(y, sr)
    return onset_times.tolist()
