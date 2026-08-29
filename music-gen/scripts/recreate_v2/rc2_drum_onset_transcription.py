"""RC2 — Drum onset-based transcription stub. c50+ RC branch owner implements.

Baseline reference: data/recreate_v2/baseline/<sha16>/rc2_drum_onset_count.json
Acceptance (see docs/m_recreate_2_accurate_small_set_rubric.md §RC2):
  - drum onset F1 >= 0.60 vs onset_times_s array
  - drum note count in [0.5x, 2x] of baseline onset_count
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

assert sys.executable == "/usr/bin/python3", sys.executable

RC_ID = "RC2"
ACCEPTANCE_CRITERIA = {
    "onset_f1_gte": 0.60,
    "count_ratio_range": (0.5, 2.0),
    "gm_channel": 10,
    "gm_notes": {"kick": 36, "snare": 38, "hihat": 42},
    "reference": "baseline/<sha16>/rc2_drum_onset_count.json",
}
BASELINE_ANCHOR_PATH = Path("data/recreate_v2/baseline")
RUBRIC_HASH_PATH = Path("data/recreate_v2/rubric_hash.txt")


def load_baseline(sha16: str) -> dict:
    p = BASELINE_ANCHOR_PATH / sha16 / "rc2_drum_onset_count.json"
    return json.loads(p.read_text())


def transcribe_drums(stems_dir: Path, out_midi: Path) -> None:
    raise NotImplementedError("c50+ branch")
