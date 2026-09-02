#!/usr/bin/env python3
"""c20 clone-0: tempo detection on WIG operator-section drums stem (sibling of c5)."""
from __future__ import annotations
import json
import sys
from pathlib import Path

import librosa
import numpy as np
import soundfile as sf

SEC_DIR = Path("data/v3_spine/252eb21ce7df7328/operator_section")


def beat_track_of(wav_path: Path, start_bpm: float = 120.0):
    audio, sr = sf.read(str(wav_path), always_2d=True)
    mono = audio.mean(axis=1).astype(np.float32)
    tempo, beats = librosa.beat.beat_track(y=mono, sr=sr, start_bpm=start_bpm, units="time")
    return float(np.asarray(tempo).flatten()[0]), beats


def main():
    drums = SEC_DIR / "rc9_6stem" / "drums.wav"
    section = SEC_DIR / "section.wav"
    if not drums.exists() or not section.exists():
        print(f"FATAL: missing inputs {drums} {section}", file=sys.stderr)
        sys.exit(1)

    tempo_drums, _ = beat_track_of(drums)
    tempo_full, _ = beat_track_of(section)

    rc5_path = Path("data/recreate_v2/baseline/252eb21ce7df7328/rc5_tempo_bpm.json")
    if rc5_path.exists():
        rc5 = json.loads(rc5_path.read_text())
        baseline_bpm = float(rc5.get("estimated_bpm", 0.0))
    else:
        baseline_bpm = 0.0

    if tempo_drums <= 20.0:
        chosen_bpm = tempo_full
        source = "operator_section_full_mix_librosa_beat_track"
        fallback = "drums_operator_section_yielded_unreliable_tempo"
    else:
        chosen_bpm = tempo_drums
        source = "operator_section_drums_librosa_beat_track"
        fallback = None

    payload = {
        "schema_version": 1,
        "cycle": 20,
        "clone": "0",
        "song_sha16": "252eb21ce7df7328",
        "section": "operator_section_t_72.77133_to_102.77133s",
        "source": source,
        "fallback_reason": fallback,
        "detected_bpm": chosen_bpm,
        "meter": [4, 4],
        "cross_checks": {
            "drums_operator_section_bpm": tempo_drums,
            "full_mix_operator_section_bpm": tempo_full,
            "rc5_baseline_full_song_bpm": baseline_bpm,
        },
        "delta_vs_rc5_baseline_bpm": chosen_bpm - baseline_bpm if baseline_bpm else None,
        "note": (
            "Tempo detected on WIG operator-chosen section only. "
            "READ-ONLY baseline unchanged."
        ),
    }
    out = SEC_DIR / "tempo_choice.json"
    out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(f"drums_bpm={tempo_drums:.4f} full_bpm={tempo_full:.4f} baseline={baseline_bpm:.4f} chosen={chosen_bpm:.4f}")


if __name__ == "__main__":
    main()
