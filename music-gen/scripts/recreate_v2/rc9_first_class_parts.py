#!/usr/bin/python3
# c51 Branch A (clone-0) RC9 first-class guitar/piano parts.
# Replaces c50 NotImplementedError stub.
#
# Cycle: 51
# Run id: run-2026-08-28T040704Z
# Agent: worker
# Milestone: M-RECREATE-2/accurate-small-set/rc9-first-class-parts
#
# See docs/m_recreate_2_accurate_small_set_rubric_v2.md §2 (D3 first-class parts).
# Method: basic-pitch on htdemucs_6s guitar + piano + other stems per focus_set_v2
# song. GM patch chosen deterministically per song via SHA-256 tiebreak over the
# allowed pool:
#   * guitar patch ∈ [25, 30]
#   * piano  patch ∈ [0, 4]
#   * other  patch ∈ [26, 40, 45, 48, 52] (logged choice)
# Accept: guitar_notes > 0 AND piano_notes > 0. If either is 0, honestly log
# null_reason (e.g. "electronic production; guitar/piano stems near-silent").

import json
import sys
from pathlib import Path

if sys.executable != "/usr/bin/python3":
    raise RuntimeError(f"rc9 requires /usr/bin/python3 (got {sys.executable})")

RC_ID = "M-RECREATE-2/accurate-small-set/rc9-first-class-parts"
ACCEPTANCE_CRITERIA = (
    "merged.midi contains distinct guitar/piano/other parts with logged GM "
    "programs (guitar in [25,30], piano in [0,4]); guitar_notes > 0 AND "
    "piano_notes > 0 per song, else honest null_reason logged."
)
BASELINE_ANCHOR_PATH = "data/recreate_v2/baseline/<sha16>/rc9_6stem/"
RUBRIC_HASH_PATH = "data/recreate_v2/rubric_hash_v2.txt"
IMPL_OUT_DIR = "data/rc1_rc9_impl"


def result_for(song_sha16: str) -> dict:
    """Return the c51-landed RC9 result for a focus_set_v2 song, or raise if not present."""
    root = Path(__file__).resolve().parent.parent.parent
    p = root / IMPL_OUT_DIR / "per_song" / song_sha16 / "rc9_result.json"
    if not p.exists():
        raise FileNotFoundError(
            f"RC9 result not present for {song_sha16}. Re-run tools/stale/c51_run_rc1_rc9.py."
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
