"""RC6 — Panel gate replacing mel-L1-only. c52+ branch after RC1-RC3 land.

Baseline references:
  - data/recreate_v2/baseline/<sha16>/rc6_centroid_time_series.npy
  - data/recreate_v2/baseline/<sha16>/rc6_vggish_or_none.json (deferred note)

Acceptance (see docs/m_recreate_2_accurate_small_set_rubric.md §RC6):
  LANDS iff ALL of:
    (1) RC1, RC2, RC3 per-song accepts
    (2) VGGish cos(original, effects) <= VGGish cos(original, bare)
    (3) centroid_rmse(original, effects) <= centroid_rmse(original, bare)
  Mel-L1 alone can NEVER confer LANDS.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

assert sys.executable == "/usr/bin/python3", sys.executable

RC_ID = "RC6"
ACCEPTANCE_CRITERIA = {
    "conditions_are_AND": True,
    "cond_1": "RC1+RC2+RC3 per-song accepts",
    "cond_2": "vggish_cos(orig, effects) <= vggish_cos(orig, bare)",
    "cond_3": "centroid_rmse(orig, effects) <= centroid_rmse(orig, bare)",
    "mel_l1_alone_gate_forbidden": True,
    "reference": (
        "baseline/<sha16>/rc6_centroid_time_series.npy + "
        "baseline/<sha16>/rc6_vggish_or_none.json (VGGish wired in by RC6 branch)"
    ),
}
BASELINE_ANCHOR_PATH = Path("data/recreate_v2/baseline")
RUBRIC_HASH_PATH = Path("data/recreate_v2/rubric_hash.txt")


def load_baseline(sha16: str) -> dict:
    d = BASELINE_ANCHOR_PATH / sha16
    return {
        "centroid_ts_path": str(d / "rc6_centroid_time_series.npy"),
        "vggish_note": json.loads((d / "rc6_vggish_or_none.json").read_text()),
    }


def evaluate_panel_gate(original: Path, bare: Path, effects: Path) -> dict:
    raise NotImplementedError("c52+ branch")
