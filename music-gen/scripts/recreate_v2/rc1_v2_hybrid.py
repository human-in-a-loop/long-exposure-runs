#!/usr/bin/python3
# c51 Branch A (clone-0) RC1 vocals transcription — hybrid vocal path.
# Replaces c50 NotImplementedError stub. c49 v1 stub
# (scripts/recreate_v2/rc1_vocals_transcription.py) preserved READ-ONLY.
#
# Cycle: 51
# Run id: run-2026-08-28T040704Z
# Agent: worker
# Milestone: M-RECREATE-2/accurate-small-set/rc1-vocals-transcription
#
# See docs/m_recreate_2_accurate_small_set_rubric_v2.md §2 (D2 hybrid vocals).
# Method: basic-pitch on htdemucs_6s vocals stem; per-song probe on Chicken
# Grease chosen_section (t=233.6-263.6s) chose basic-pitch as the branch method;
# pyin retained as documented fallback path for c52 integration.
#
# Vocal MIDI is emitted as GM program 53 (voice oohs) inside per-song
# data/rc1_rc9_impl/per_song/<sha16>/merged_partial.midi. Accept: voiced-time
# coverage >= 50% of c49 baseline voiced_time_s.

import json
import sys
from pathlib import Path

if sys.executable != "/usr/bin/python3":
    raise RuntimeError(f"rc1_v2 requires /usr/bin/python3 (got {sys.executable})")

RC_ID = "M-RECREATE-2/accurate-small-set/rc1-vocals-transcription (v2 hybrid path)"
ACCEPTANCE_CRITERIA = (
    "vocal-part note count > 0 in merged.midi AND voiced-time coverage >= 50% "
    "of baseline voiced_time_s at data/recreate_v2/baseline/<sha16>/rc1_vocals_voiced_time_s.json"
)
BASELINE_ANCHOR_PATH = "data/recreate_v2/baseline/<sha16>/rc1_vocals_voiced_time_s.json"
RUBRIC_HASH_PATH = "data/recreate_v2/rubric_hash_v2.txt"
IMPL_OUT_DIR = "data/rc1_rc9_impl"


def result_for(song_sha16: str) -> dict:
    """Return the c51-landed RC1 result for a focus_set_v2 song, or raise if not present."""
    root = Path(__file__).resolve().parent.parent.parent
    p = root / IMPL_OUT_DIR / "per_song" / song_sha16 / "rc1_result.json"
    if not p.exists():
        raise FileNotFoundError(
            f"RC1 result not present for {song_sha16}. Re-run tools/stale/c51_run_rc1_rc9.py."
        )
    return json.loads(p.read_text())


def run(*args, **kwargs):
    """Bootstrap the c51 Branch A orchestrator across the 5-song focus_set_v2."""
    root = Path(__file__).resolve().parent.parent.parent
    orchestrator = root / "tools" / "stale" / "c51_run_rc1_rc9.py"
    if not orchestrator.exists():
        raise RuntimeError(f"orchestrator missing: {orchestrator}")
    import subprocess
    subprocess.run([sys.executable, str(orchestrator), "run1"], check=True)


if __name__ == "__main__":
    run()
