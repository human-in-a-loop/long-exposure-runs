#!/usr/bin/env /usr/bin/python3
# RC10 Branch A D2 content metrics.
# created: 2026-09-02, cycle 54, run-2026-08-28T040704Z, worker, fork bdd7bb47f1b5 clone-0
import numpy as np
import librosa


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


def framewise_f0_agreement(y_ref, y_pred, sr):
    """% of jointly-voiced frames within 1 semitone. pyin both."""
    fmin = float(librosa.note_to_hz("C1"))
    fmax = float(librosa.note_to_hz("C4"))
    f0_a, vf_a, vp_a = librosa.pyin(y_ref, sr=sr, fmin=fmin, fmax=fmax, hop_length=512)
    f0_b, vf_b, vp_b = librosa.pyin(y_pred, sr=sr, fmin=fmin, fmax=fmax, hop_length=512)
    n = min(len(f0_a), len(f0_b))
    if n == 0:
        return 0.0
    ma = np.isfinite(f0_a[:n]) & vf_a[:n]
    mb = np.isfinite(f0_b[:n]) & vf_b[:n]
    both = ma & mb
    if not both.any():
        return 0.0
    semi_a = 12 * np.log2(f0_a[:n][both] / 440.0) + 69
    semi_b = 12 * np.log2(f0_b[:n][both] / 440.0) + 69
    within = np.abs(semi_a - semi_b) <= 1.0
    return float(within.mean())


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


def median_midi_pitch(notes):
    ps = [int(n["pitch"]) for n in notes]
    if not ps:
        return 0
    return int(np.median(ps))


def drums_gate(f1, count_ratio):
    return bool(f1 >= 0.60 and 0.5 <= count_ratio <= 2.0)


def bass_gate(f0_agree, low_corr, med_midi, count_ratio):
    return bool(
        f0_agree >= 0.60
        and low_corr >= 0.5
        and med_midi < 55
        and 0.5 <= count_ratio <= 2.0
    )
