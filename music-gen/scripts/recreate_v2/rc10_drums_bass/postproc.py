#!/usr/bin/env /usr/bin/python3
# RC10 Branch A D4 post-processing pipeline: beat-snap, glitch-drop, velocity, range.
# created: 2026-09-02, cycle 54, run-2026-08-28T040704Z, worker, fork bdd7bb47f1b5 clone-0
import numpy as np


def beat_grid_snap(notes, bpm, tol_ms=50):
    """Snap onsets to beat grid within ±tol_ms. Out-of-tolerance kept unsnapped."""
    if bpm <= 0:
        return notes
    beat_s = 60.0 / float(bpm)
    tol_s = tol_ms / 1000.0
    out = []
    for n in notes:
        t = n["onset_s"]
        k = round(t / beat_s)
        snapped = k * beat_s
        if abs(snapped - t) <= tol_s:
            m = dict(n)
            m["onset_s"] = float(snapped)
            m["snapped"] = True
            out.append(m)
        else:
            m = dict(n)
            m["snapped"] = False
            out.append(m)
    return out


def glitch_drop(notes, bpm):
    if bpm <= 0:
        return notes
    thresh = 60.0 / float(bpm) / 8.0  # 32nd note
    return [n for n in notes if n["duration_s"] >= thresh]


def envelope_velocity(notes, y, sr, bpm):
    """Derive velocity from local RMS envelope over 1-beat window, per-stem norm to [1,127]."""
    if len(notes) == 0:
        return notes
    beat_s = 60.0 / max(1e-6, float(bpm))
    win = max(int(sr * beat_s), 512)
    hop = 512
    rms = []
    times = []
    i = 0
    while i + win <= len(y):
        seg = y[i : i + win]
        rms.append(float(np.sqrt((seg ** 2).mean() + 1e-12)))
        times.append((i + win / 2.0) / sr)
        i += hop
    if not rms:
        return notes
    rms = np.asarray(rms)
    times = np.asarray(times)
    vmax = float(rms.max()) or 1.0
    vmin = float(rms.min())
    out = []
    for n in notes:
        t = n["onset_s"]
        idx = int(np.clip(np.searchsorted(times, t), 0, len(rms) - 1))
        v = (rms[idx] - vmin) / max(1e-9, vmax - vmin)
        m = dict(n)
        m["velocity"] = int(np.clip(round(1 + 126 * v), 1, 127))
        out.append(m)
    return out


def range_filter(notes, kind):
    """kind ∈ {'drums', 'bass'}."""
    if kind == "drums":
        allowed = {36, 38, 42}
        return [n for n in notes if int(n["pitch"]) in allowed]
    if kind == "bass":
        return [n for n in notes if 24 <= int(n["pitch"]) <= 71]
    return notes


def apply_d4(notes, y, sr, bpm, kind):
    n1 = beat_grid_snap(notes, bpm)
    n2 = glitch_drop(n1, bpm)
    n3 = envelope_velocity(n2, y, sr, bpm)
    n4 = range_filter(n3, kind)
    return n4
