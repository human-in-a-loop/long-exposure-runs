#!/usr/bin/env /usr/bin/python3
"""c20 clone-2: librosa tempo_choice on Peach Dream chosen-section drums.

Per-song sibling of scripts/v3_spine/tempo_map_operator_section.py (READ-ONLY).
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import librosa
import numpy as np
import soundfile as sf

SEC_DIR = Path("data/v3_spine/88d247468cb6d49f/chosen_section")


def beat_track_of(wav_path: Path, start_bpm: float = 120.0):
    audio, sr = sf.read(str(wav_path), always_2d=True)
    mono = audio.mean(axis=1).astype(np.float32)
    tempo, beats = librosa.beat.beat_track(y=mono, sr=sr, start_bpm=start_bpm, units="time")
    return float(np.asarray(tempo).flatten()[0]), beats


def main():
    drums = SEC_DIR / "rc9_6stem" / "drums.wav"
    section = SEC_DIR / "section.wav"
    if not drums.exists() or not section.exists():
        print(f"FATAL: missing {drums} {section}", file=sys.stderr)
        sys.exit(1)

    tempo_drums, _ = beat_track_of(drums)
    tempo_full, _ = beat_track_of(section)

    if tempo_drums <= 20.0:
        chosen_bpm = tempo_full
        source = "chosen_section_full_mix_librosa_beat_track"
        fallback = "drums_yielded_unreliable_tempo"
    else:
        chosen_bpm = tempo_drums
        source = "chosen_section_drums_librosa_beat_track"
        fallback = None

    payload = {
        "schema_version": 1, "cycle": 20, "clone": "clone-2",
        "song_sha16": "88d247468cb6d49f",
        "section": "chosen_section_t_172.87256_to_202.87256s",
        "source": source, "fallback_reason": fallback,
        "detected_bpm": chosen_bpm, "meter": [4, 4],
        "cross_checks": {
            "drums_chosen_section_bpm": tempo_drums,
            "full_mix_chosen_section_bpm": tempo_full,
        },
        "note": "Tempo detected on operator's chosen section only (Peach Dream).",
    }
    out = SEC_DIR / "tempo_choice.json"
    out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(f"drums_bpm={tempo_drums:.4f} full_bpm={tempo_full:.4f} chosen={chosen_bpm:.4f}")


if __name__ == "__main__":
    main()
