#!/usr/bin/env /usr/bin/python3
# RC10 Branch A drums candidate: onset detect + band-energy classifier → GM ch10 {36,38,42}.
# created: 2026-09-02, cycle 54, run-2026-08-28T040704Z, worker, fork bdd7bb47f1b5 clone-0
import numpy as np
import librosa

# GM percussion:
KICK, SNARE, HIHAT = 36, 38, 42


def _band_energy(y, sr, lo, hi):
    """RMS energy in [lo, hi] Hz on a short window centered around now."""
    # FFT-based; caller passes a short window
    n = len(y)
    if n < 32:
        return 0.0
    Y = np.abs(np.fft.rfft(y * np.hanning(n)))
    freqs = np.fft.rfftfreq(n, 1.0 / sr)
    m = (freqs >= lo) & (freqs < hi)
    if not m.any():
        return 0.0
    return float(np.sqrt((Y[m] ** 2).mean()))


def _classify(y, sr, t_onset_s, hop_ms=30):
    """Classify one onset by dominant band energy in a small window."""
    half = int(round(sr * hop_ms / 1000.0))
    center = int(round(t_onset_s * sr))
    a = max(0, center - half)
    b = min(len(y), center + half)
    win = y[a:b]
    if len(win) < 32:
        return HIHAT
    e_kick = _band_energy(win, sr, 50, 120)
    e_snare_lo = _band_energy(win, sr, 200, 500)
    e_snare_hi = _band_energy(win, sr, 4000, 8000)
    e_hihat = _band_energy(win, sr, 6000, 12000)
    # priority: kick dominates when low-band strong; snare needs both bands;
    # otherwise hihat as HF default.
    scores = {
        KICK: e_kick * 1.4,
        SNARE: (e_snare_lo * 0.5 + e_snare_hi * 0.5) * 1.0,
        HIHAT: e_hihat * 0.9,
    }
    return max(scores.items(), key=lambda kv: kv[1])[0]


def transcribe(y, sr):
    """Return list of {onset_s, pitch, velocity, duration_s}."""
    onsets = librosa.onset.onset_detect(
        y=y, sr=sr, hop_length=512, backtrack=True, units="time"
    )
    notes = []
    for i, t in enumerate(onsets):
        pitch = _classify(y, sr, float(t))
        # duration is a nominal short percussive note (safely above 32nd-note at typical BPM)
        dur = 0.15
        notes.append({
            "onset_s": float(t),
            "pitch": int(pitch),
            "velocity": 90,   # provisional; D4 replaces w/ envelope-derived
            "duration_s": dur,
            "channel": 10,
        })
    return notes


def reference_onsets(y, sr):
    return list(map(float, librosa.onset.onset_detect(
        y=y, sr=sr, hop_length=512, backtrack=True, units="time"
    )))
