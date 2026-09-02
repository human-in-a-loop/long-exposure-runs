#!/usr/bin/env /usr/bin/python3
# D6 four-metric composite gate for RC10 bass v2.
# created: 2026-09-02, cycle 55, run-2026-08-28T040704Z, worker, fork 7cc01d726807 clone-1
import numpy as np


def onset_f1(pred_onsets_s, ref_onsets_s, tol_s=0.050):
    """Standard F1 on onset times with tol seconds matching (greedy 1-to-1)."""
    pred = sorted(float(x) for x in pred_onsets_s)
    ref = sorted(float(x) for x in ref_onsets_s)
    if not pred and not ref:
        return 1.0, 0, 0, 0
    if not pred or not ref:
        return 0.0, 0, len(pred), len(ref)
    used_r = [False] * len(ref)
    tp = 0
    for p in pred:
        best = -1
        best_d = tol_s + 1e-9
        for j, r in enumerate(ref):
            if used_r[j]:
                continue
            d = abs(p - r)
            if d < best_d:
                best_d = d
                best = j
            if r - p > tol_s:
                break
        if best >= 0:
            used_r[best] = True
            tp += 1
    fp = len(pred) - tp
    fn = len(ref) - tp
    p = tp / (tp + fp) if (tp + fp) else 0.0
    r = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2 * p * r / (p + r) if (p + r) else 0.0
    return float(f1), int(tp), int(fp), int(fn)


def note_count_ratio(pred_notes, ref_onsets_s):
    n_ref = max(1, len(ref_onsets_s))
    return float(len(pred_notes)) / float(n_ref)


def velocity_std(notes):
    if not notes:
        return 0.0
    vels = np.array([int(n["velocity"]) for n in notes], dtype=np.float64)
    return float(np.std(vels, ddof=0))


def low_band_correlation(y_ref, y_pred, sr, cutoff=250.0):
    """Pearson on hop=512 RMS envelopes of low-pass filtered stems."""
    from scipy.signal import butter, sosfiltfilt
    sos = butter(4, cutoff / (sr / 2), btype="low", output="sos")
    ra = _rms_env(sosfiltfilt(sos, y_ref).astype(np.float32))
    rb = _rms_env(sosfiltfilt(sos, y_pred).astype(np.float32))
    n = min(len(ra), len(rb))
    if n < 2:
        return 0.0
    ra, rb = ra[:n], rb[:n]
    va, vb = ra - ra.mean(), rb - rb.mean()
    d = float(np.sqrt((va ** 2).sum() * (vb ** 2).sum()))
    if d == 0.0:
        return 0.0
    return float((va * vb).sum() / d)


def _rms_env(y, hop=512):
    n = len(y) // hop
    if n == 0:
        return np.zeros(1, dtype=np.float32)
    y = y[: n * hop].reshape(n, hop)
    return np.sqrt((y ** 2).mean(axis=1) + 1e-12).astype(np.float32)


def bass_v2_gate(f1, count_ratio, vel_std, low_corr):
    """D6 composite: ALL 4 must hold."""
    m1 = bool(f1 >= 0.60)
    m2 = bool(0.7 <= count_ratio <= 1.5)
    m3 = bool(vel_std >= 10.0)
    m4 = bool(low_corr >= 0.5)
    return {
        "m1_onset_f1_ge_060": m1,
        "m2_count_ratio_070_150": m2,
        "m3_vel_std_ge_10": m3,
        "m4_low_corr_ge_05": m4,
        "all_pass": bool(m1 and m2 and m3 and m4),
        "num_pass": int(m1) + int(m2) + int(m3) + int(m4),
    }
