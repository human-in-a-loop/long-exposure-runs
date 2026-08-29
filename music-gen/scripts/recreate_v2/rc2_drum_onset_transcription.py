"""RC2 — Drum onset transcription (c51 clone-1 implementation).

Baseline reference: data/recreate_v2/baseline/<sha16>/rc2_drum_onset_count.json
Pre-registered classifier bands: data/recreate_v2/rc2_classifier_bands.json
Rubric: docs/rc2_rc3_impl_rubric.md
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

assert sys.executable == "/usr/bin/python3", sys.executable

import numpy as np
import librosa

RC_ID = "RC2"
ACCEPTANCE_CRITERIA = {
    "onset_f1_gte": 0.60,
    "count_ratio_range": (0.5, 2.0),
    "gm_channel": 10,
    "gm_notes": {"kick": 36, "snare": 38, "hihat": 42},
    "reference": "baseline/<sha16>/rc2_drum_onset_count.json",
}
BASELINE_ANCHOR_PATH = Path("data/recreate_v2/baseline")
RUBRIC_HASH_PATH = Path("data/rc2_rc3_impl/rubric_hash.txt")
CLASSIFIER_BANDS_PATH = Path("data/recreate_v2/rc2_classifier_bands.json")


def load_bands() -> dict:
    return json.loads(CLASSIFIER_BANDS_PATH.read_text())


def transcribe_drums(drums_wav_path: Path, t_start_s: float, t_end_s: float,
                     sr: int = 44100) -> list[dict]:
    bands = load_bands()
    y_full, native_sr = librosa.load(str(drums_wav_path), sr=sr, mono=True)
    i0 = int(t_start_s * sr)
    i1 = int(t_end_s * sr)
    y = y_full[i0:i1]
    p = bands["onset_detect_params"]
    onset_times = librosa.onset.onset_detect(
        y=y, sr=sr,
        hop_length=p["hop_length"],
        units=p["units"],
        pre_max=p["pre_max"], post_max=p["post_max"],
        pre_avg=p["pre_avg"], post_avg=p["post_avg"],
        delta=p["delta"], wait=p["wait"],
        backtrack=p["backtrack"],
    )
    n_fft = 2048
    win = int(0.050 * sr)
    kick_lo, kick_hi = bands["kick_band_hz"]
    snare_lo, snare_hi = bands["snare_band_hz"]
    hihat_lo, hihat_hi = bands["hihat_band_hz"]
    notes = []
    for t in onset_times:
        i = int(t * sr)
        seg = y[i:i + win]
        if len(seg) < 32:
            continue
        # single STFT frame band-RMS
        n = min(n_fft, 1 << (len(seg) - 1).bit_length())
        n = max(n, 256)
        S = np.abs(np.fft.rfft(seg, n=n))
        freqs = np.fft.rfftfreq(n, 1.0 / sr)
        def band_rms(lo, hi):
            mask = (freqs >= lo) & (freqs < hi)
            if not mask.any():
                return 0.0
            v = S[mask]
            return float(np.sqrt(np.mean(v * v)))
        rk = band_rms(kick_lo, kick_hi)
        rs = band_rms(snare_lo, snare_hi)
        rh = band_rms(hihat_lo, hihat_hi)
        labels = ("kick", "snare", "hihat")
        rms = (rk, rs, rh)
        idx = int(np.argmax(rms))
        label = labels[idx]
        midi_note = bands["gm_channel_10_notes"][label]
        notes.append({
            "time_s": float(t),
            "midi_note": int(midi_note),
            "label": label,
            "confidence": float(rms[idx] / (sum(rms) + 1e-12)),
            "band_rms": {"kick": rk, "snare": rs, "hihat": rh},
        })
    return notes


if __name__ == "__main__":
    # Import guard sanity — this module is called via c51 driver.
    print(json.dumps({"module": "rc2_drum_onset_transcription", "status": "importable"}))
