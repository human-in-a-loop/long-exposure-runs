"""RC4 — Explicit GM program map per stem. Folds into RC1-RC3 merged.midi.

Acceptance (see docs/m_recreate_2_accurate_small_set_rubric.md §RC4):
  - zero merged.midi parts on program 4 unless deliberately logged
"""
from __future__ import annotations

import sys
from pathlib import Path

assert sys.executable == "/usr/bin/python3", sys.executable

RC_ID = "RC4"
ACCEPTANCE_CRITERIA = {
    "program_4_forbidden_unless_logged": True,
    "gm_program_map": {
        "bass": [33, 34],        # Acoustic/Electric Bass Finger
        "drums": "channel_10",   # GM percussion channel
        "other": "per_song_choice_logged",
        "vocals": "lead_voice_or_synth_patch",
    },
    "log_path": "data/recreate_v2/<sha16>/rc4_program_map.json",
}
RUBRIC_HASH_PATH = Path("data/recreate_v2/rubric_hash.txt")


def assign_programs(merged_midi_path: Path, log_out: Path) -> None:
    raise NotImplementedError("c50+ branch")
