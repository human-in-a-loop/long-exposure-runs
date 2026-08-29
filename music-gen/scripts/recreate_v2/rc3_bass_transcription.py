"""RC3 — Bass-specific transcription stub. c50+ RC branch owner implements.

Baseline reference: data/recreate_v2/baseline/<sha16>/rc3_bass_{pyin_voiced_segments,low_band_energy}.json
Acceptance (see docs/m_recreate_2_accurate_small_set_rubric.md §RC3):
  - bass note count in [0.5x, 2x] of baseline voiced_segments_count
  - low-band (<250 Hz) energy correlation >= 0.5 vs baseline envelope
  - median MIDI pitch < 55
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

assert sys.executable == "/usr/bin/python3", sys.executable

RC_ID = "RC3"
ACCEPTANCE_CRITERIA = {
    "note_count_ratio_range": (0.5, 2.0),
    "low_band_correlation_gte": 0.5,
    "low_band_upper_hz": 250.0,
    "median_midi_pitch_lt": 55,
    "reference": "baseline/<sha16>/rc3_bass_pyin_voiced_segments.json + rc3_bass_low_band_energy.json",
}
BASELINE_ANCHOR_PATH = Path("data/recreate_v2/baseline")
RUBRIC_HASH_PATH = Path("data/recreate_v2/rubric_hash.txt")


def load_baseline(sha16: str) -> tuple[dict, dict]:
    d = BASELINE_ANCHOR_PATH / sha16
    return (
        json.loads((d / "rc3_bass_pyin_voiced_segments.json").read_text()),
        json.loads((d / "rc3_bass_low_band_energy.json").read_text()),
    )


def transcribe_bass(stems_dir: Path, out_midi: Path) -> None:
    raise NotImplementedError("c50+ branch")
