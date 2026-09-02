#!/usr/bin/env python3
"""c5 Track B: canonical tempo choice on operator-section drums stem via librosa.

Uses drums-stem beat_track on the operator-section drums.wav; cross-checks
against full-mix beat_track and against the c4 RC5 baseline (whole-song).
Same tempo expected but different beat-grid offset. Does NOT overwrite the
c49 RC5 baseline (READ-ONLY anchor).
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import librosa
import numpy as np
import soundfile as sf

SEC_DIR = Path("data/v3_spine/31a164f845f8e27e/operator_section")


def beat_track_of(wav_path: Path, start_bpm: float = 120.0) -> tuple[float, np.ndarray]:
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

    tempo_drums, beats_drums = beat_track_of(drums)
    tempo_full, beats_full = beat_track_of(section)

    # Cross-check against RC5 baseline
    rc5 = json.loads(
        Path("data/recreate_v2/baseline/31a164f845f8e27e/rc5_tempo_bpm.json").read_text()
    )
    baseline_bpm = float(rc5["estimated_bpm"])

    # Prefer drums; fall back to full-mix if drums is silent/undetectable
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
        "cycle": 5,
        "song_sha16": "31a164f845f8e27e",
        "section": "operator_section_t_233.63918_to_263.63918s",
        "source": source,
        "fallback_reason": fallback,
        "detected_bpm": chosen_bpm,
        "meter": [4, 4],
        "cross_checks": {
            "drums_operator_section_bpm": tempo_drums,
            "full_mix_operator_section_bpm": tempo_full,
            "rc5_baseline_full_song_bpm": baseline_bpm,
        },
        "delta_vs_rc5_baseline_bpm": chosen_bpm - baseline_bpm,
        "note": (
            "Tempo detected on the operator-chosen section only. Same song, "
            "different beat-grid offset expected vs c4 full-song RC5 anchor. "
            "READ-ONLY baseline unchanged."
        ),
    }
    out = SEC_DIR / "tempo_choice.json"
    out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(f"drums_bpm={tempo_drums:.4f} full_bpm={tempo_full:.4f} baseline={baseline_bpm:.4f} chosen={chosen_bpm:.4f}")


if __name__ == "__main__":
    main()
