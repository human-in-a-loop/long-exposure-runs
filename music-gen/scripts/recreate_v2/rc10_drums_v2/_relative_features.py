#!/usr/bin/env /usr/bin/python3
# RC10 Drums v2 — relative-feature extractor.
# created: 2026-09-02, cycle 55, run-2026-08-28T040704Z, worker, fork 7cc01d726807 clone-0
# milestone: M-RECREATE-2/accurate-small-set/rc10-transcription-real-stem-resurvey/drums-v2
import sys
import numpy as np
import librosa

if sys.executable != "/usr/bin/python3":
    raise RuntimeError(f"interpreter guard: expected /usr/bin/python3, got {sys.executable}")

EPS = 1e-12


def detect_onsets(y, sr):
    """Same detector as c54 v1 — onset TIMING preserved (operator constraint)."""
    return librosa.onset.onset_detect(
        y=y, sr=sr, hop_length=512, backtrack=True, units="time",
    )


def _centroid_hz(win, sr):
    if len(win) < 32:
        return 0.0
    c = librosa.feature.spectral_centroid(y=win, sr=sr, hop_length=256)[0]
    if c.size == 0:
        return 0.0
    return float(np.mean(c))


def _hf_lf_ratio_db10(win, sr):
    if len(win) < 32:
        return 0.0
    S = np.abs(librosa.stft(win, n_fft=1024, hop_length=256, center=True)) ** 2
    freqs = librosa.fft_frequencies(sr=sr, n_fft=1024)
    lo = S[freqs < 500.0].sum() + EPS
    hi = S[freqs >= 500.0].sum() + EPS
    return float(np.log10(hi / lo))


def _decay_ms(win, sr):
    if len(win) < 32:
        return float(len(win) / sr * 1000.0)
    rms = librosa.feature.rms(y=win, hop_length=128)[0]
    if rms.size == 0:
        return float(len(win) / sr * 1000.0)
    peak_idx = int(np.argmax(rms))
    peak_val = float(rms[peak_idx])
    if peak_val <= EPS:
        return float(len(win) / sr * 1000.0)
    thr = 0.10 * peak_val
    for i in range(peak_idx, rms.size):
        if float(rms[i]) <= thr:
            return float((i - peak_idx) * 128 / sr * 1000.0)
    # never crossed
    return float((rms.size - peak_idx) * 128 / sr * 1000.0)


def extract_features(y, sr, onsets_s, window_ms=25.0):
    """Return (N, 3) matrix: [centroid_hz, hf_lf_log10, decay_ms] per onset."""
    half = int(round(sr * window_ms / 1000.0))
    N = len(onsets_s)
    feats = np.zeros((N, 3), dtype=np.float64)
    for k, t in enumerate(onsets_s):
        center = int(round(float(t) * sr))
        a = max(0, center - half)
        b = min(len(y), center + half)
        win = y[a:b].astype(np.float32)
        feats[k, 0] = _centroid_hz(win, sr)
        feats[k, 1] = _hf_lf_ratio_db10(win, sr)
        feats[k, 2] = _decay_ms(win, sr)
    return feats
