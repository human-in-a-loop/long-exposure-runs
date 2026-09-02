#!/usr/bin/env python3
"""c20 Rome: tempo choice via librosa.beat.beat_track on chosen-section drums."""
from __future__ import annotations
import json
import sys
from pathlib import Path

import librosa
import numpy as np
import soundfile as sf

SHA16 = "cdd2717e52820ff6"
SEC_DIR = Path(f"data/v3_spine/{SHA16}/operator_section")


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
    baseline_bpm = None
    baseline_path = Path(f"data/recreate_v2/baseline/{SHA16}/rc5_tempo_bpm.json")
    if baseline_path.exists():
        baseline_bpm = float(json.loads(baseline_path.read_text())["estimated_bpm"])
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
        "song_sha16": SHA16,
        "section": "operator_section_t_21.91963718820862_to_51.91963718820862s",
        "source": source,
        "fallback_reason": fallback,
        "detected_bpm": chosen_bpm,
        "meter": [4, 4],
        "cross_checks": {
            "drums_operator_section_bpm": tempo_drums,
            "full_mix_operator_section_bpm": tempo_full,
            "rc5_baseline_full_song_bpm": baseline_bpm,
        },
        "delta_vs_rc5_baseline_bpm": (chosen_bpm - baseline_bpm) if baseline_bpm is not None else None,
        "note": "Disco A tempo detected on operator's D1-chosen section. READ-ONLY baseline unchanged.",
    }
    out = SEC_DIR / "tempo_choice.json"
    out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(f"drums={tempo_drums:.4f} full={tempo_full:.4f} baseline={baseline_bpm} chosen={chosen_bpm:.4f}")


if __name__ == "__main__":
    main()
