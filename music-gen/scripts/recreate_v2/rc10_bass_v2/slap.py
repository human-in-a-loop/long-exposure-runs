#!/usr/bin/env /usr/bin/python3
# D4 slap/pop detector: HF (2-8kHz) transient burst > 3x rolling median.
# created: 2026-09-02, cycle 55, run-2026-08-28T040704Z, worker, fork 7cc01d726807 clone-1
import numpy as np
import librosa


HF_LO_HZ = 2000.0
HF_HI_HZ = 8000.0
WIN_MS = 100.0            # ±100 ms around onset
ROLLING_HALF_S = 1.0      # ±1 s rolling median
SLAP_RATIO = 3.0
N_FFT = 2048
HOP = 512


def hf_energy_series(y, sr, n_fft=N_FFT, hop=HOP):
    """Sum of |S|² across bins in [HF_LO_HZ, HF_HI_HZ]. Deterministic."""
    S = np.abs(librosa.stft(y, n_fft=n_fft, hop_length=hop, center=True)) ** 2
    freqs = librosa.fft_frequencies(sr=sr, n_fft=n_fft)
    band = (freqs >= HF_LO_HZ) & (freqs <= HF_HI_HZ)
    return S[band, :].sum(axis=0), hop


def detect_slaps(y, sr, onset_times_s):
    """Return list[bool] per onset: True iff HF burst > SLAP_RATIO × rolling median.

    Per-onset E_hf = sum of hf_energy_series in ±WIN_MS window.
    Rolling median M_hf(t) = median of E_hf over ±ROLLING_HALF_S window.
    """
    ef, hop = hf_energy_series(y, sr)
    if len(ef) == 0 or len(onset_times_s) == 0:
        return [False] * len(onset_times_s)
    frames_per_sec = sr / hop
    win_frames = max(1, int(round((WIN_MS / 1000.0) * frames_per_sec)))
    roll_frames = max(1, int(round(ROLLING_HALF_S * frames_per_sec)))

    # Per-onset E_hf: sum energy in ±win_frames around the onset frame
    n = len(ef)
    e_per_onset = np.zeros(len(onset_times_s), dtype=np.float64)
    onset_frames = np.zeros(len(onset_times_s), dtype=np.int64)
    for i, t in enumerate(onset_times_s):
        f = int(round(t * frames_per_sec))
        f = max(0, min(n - 1, f))
        a = max(0, f - win_frames)
        b = min(n, f + win_frames + 1)
        e_per_onset[i] = float(ef[a:b].sum())
        onset_frames[i] = f

    # Rolling median over frame domain (same series ef, not per-onset)
    # M(t) = median of ef in [t - roll_frames, t + roll_frames + 1]
    flags = []
    for i, f in enumerate(onset_frames):
        a = max(0, f - roll_frames)
        b = min(n, f + roll_frames + 1)
        m = float(np.median(ef[a:b]))
        # Sum per-onset window equivalent: baseline is (2*win_frames+1) frames of median
        baseline = m * (2 * win_frames + 1)
        flags.append(bool(e_per_onset[i] > SLAP_RATIO * baseline))
    return flags
