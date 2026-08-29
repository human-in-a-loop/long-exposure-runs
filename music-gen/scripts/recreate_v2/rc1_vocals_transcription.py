"""RC1 — Vocals transcription stub. c50+ RC branch owner implements.

Baseline reference: data/recreate_v2/baseline/<sha16>/rc1_vocals_voiced_time_s.json
Acceptance (see docs/m_recreate_2_accurate_small_set_rubric.md §RC1):
  - vocal-part note count > 0 in produced merged.midi
  - voiced-time coverage >= 50% of baseline voiced_time_s
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

assert sys.executable == "/usr/bin/python3", sys.executable

RC_ID = "RC1"
ACCEPTANCE_CRITERIA = {
    "vocal_part_note_count_gt": 0,
    "voiced_time_coverage_gte": 0.50,
    "reference": "baseline/<sha16>/rc1_vocals_voiced_time_s.json",
}
BASELINE_ANCHOR_PATH = Path("data/recreate_v2/baseline")
RUBRIC_HASH_PATH = Path("data/recreate_v2/rubric_hash.txt")


def load_baseline(sha16: str) -> dict:
    p = BASELINE_ANCHOR_PATH / sha16 / "rc1_vocals_voiced_time_s.json"
    return json.loads(p.read_text())


def transcribe_vocals(stems_dir: Path, out_midi: Path) -> None:
    raise NotImplementedError("c50+ branch")
