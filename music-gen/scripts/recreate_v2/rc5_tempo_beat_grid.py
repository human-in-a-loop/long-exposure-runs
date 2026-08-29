"""RC5 — Tempo/beat-grid estimation stub. c51 linear branch owner implements.

Baseline reference: data/recreate_v2/baseline/<sha16>/rc5_tempo_bpm.json
Acceptance (see docs/m_recreate_2_accurate_small_set_rubric.md §RC5):
  - |estimated_bpm - score_bpm| <= 2
This also closes the c37/c39-42 quantization defect.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

assert sys.executable == "/usr/bin/python3", sys.executable

RC_ID = "RC5"
ACCEPTANCE_CRITERIA = {
    "bpm_delta_le": 2.0,
    "detector": "librosa.beat.beat_track(units='time')",
    "reference": "baseline/<sha16>/rc5_tempo_bpm.json",
}
BASELINE_ANCHOR_PATH = Path("data/recreate_v2/baseline")
RUBRIC_HASH_PATH = Path("data/recreate_v2/rubric_hash.txt")


def load_baseline(sha16: str) -> dict:
    p = BASELINE_ANCHOR_PATH / sha16 / "rc5_tempo_bpm.json"
    return json.loads(p.read_text())


def apply_tempo_grid(original_mix: Path, musicxml_out: Path) -> None:
    raise NotImplementedError("c50+/c51 branch")
