"""RC3 — Bass pyin monophonic transcription (c51 clone-1 implementation).

Baseline reference: data/recreate_v2/baseline/<sha16>/rc3_bass_pyin_voiced_segments.json
Approach doc: docs/rc3_bass_approach.md
Rubric: docs/rc2_rc3_impl_rubric.md
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

assert sys.executable == "/usr/bin/python3", sys.executable

import numpy as np
import librosa

RC_ID = "RC3"
ACCEPTANCE_CRITERIA = {
    "note_count_ratio_range": (0.5, 2.0),
    "low_band_correlation_gte": 0.5,
    "low_band_upper_hz": 250.0,
    "median_midi_pitch_lt": 55,
    "reference": "baseline/<sha16>/rc3_bass_pyin_voiced_segments.json",
}
BASELINE_ANCHOR_PATH = Path("data/recreate_v2/baseline")
RUBRIC_HASH_PATH = Path("data/rc2_rc3_impl/rubric_hash.txt")

FMIN_HZ = 41.203  # E1 (librosa.note_to_hz('E1'))
FMAX_HZ = 329.628  # E4
HOP = 512


def transcribe_bass(bass_wav_path: Path, t_start_s: float, t_end_s: float,
                    sr: int = 44100) -> list[dict]:
    y_full, native_sr = librosa.load(str(bass_wav_path), sr=sr, mono=True)
    i0 = int(t_start_s * sr)
    i1 = int(t_end_s * sr)
    y = y_full[i0:i1]
    f0, voiced_flag, _ = librosa.pyin(
        y, fmin=FMIN_HZ, fmax=FMAX_HZ, sr=sr, hop_length=HOP,
    )
    times = librosa.times_like(f0, sr=sr, hop_length=HOP)
    # Group contiguous voiced runs (min 60ms).
    min_frames = max(1, int(0.060 * sr / HOP))
    notes = []
    i = 0
    n = len(voiced_flag)
    while i < n:
        if not voiced_flag[i] or f0[i] is None or (isinstance(f0[i], float) and np.isnan(f0[i])):
            i += 1
            continue
        j = i
        while j < n and voiced_flag[j] and not np.isnan(f0[j]):
            j += 1
        run_len = j - i
        if run_len >= min_frames:
            f0_run = f0[i:j]
            f0_run = f0_run[~np.isnan(f0_run)]
            if len(f0_run) > 0:
                med_f0 = float(np.median(f0_run))
                if med_f0 > 0:
                    midi = int(round(float(librosa.hz_to_midi(med_f0))))
                    notes.append({
                        "start_s": float(times[i]),
                        "end_s": float(times[j - 1]),
                        "midi_note": midi,
                        "velocity": 100,
                        "median_f0_hz": med_f0,
                    })
        i = j
    return notes


if __name__ == "__main__":
    print(json.dumps({"module": "rc3_bass_transcription", "status": "importable"}))
