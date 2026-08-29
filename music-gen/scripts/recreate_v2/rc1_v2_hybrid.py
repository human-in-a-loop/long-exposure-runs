#!/usr/bin/python3
# c50 pre-registration sibling stub for RC1 under rubric-v2 hybrid vocal path.
# Sibling of scripts/recreate_v2/rc1_vocals_transcription.py (c49 v1) which is
# preserved READ-ONLY. c49 rubric-v1 chain remains intact.
# Created: 2026-08-29
# Cycle: 50
# Run id: run-2026-08-28T040704Z
# Agent: worker
# Milestone: M-RECREATE-2/accurate-small-set/rc-v2-stubs-registered
#
# See docs/m_recreate_2_accurate_small_set_rubric_v2.md §2 (D2 hybrid vocals).
# Implementation lands in c51+ RC-v2 Branch A.

import sys

if sys.executable != "/usr/bin/python3":
    raise RuntimeError(f"rc1_v2 requires /usr/bin/python3 (got {sys.executable})")

RC_ID = "M-RECREATE-2/accurate-small-set/rc1-vocals-transcription (v2 hybrid path)"
ACCEPTANCE_CRITERIA = (
    "vocal-part note count > 0 in merged.midi AND voiced-time coverage >= 50%; "
    "ORIGINAL vocals stem time-aligned + loudness-preserved (LUFS-S +/- 0.5 LU) "
    "and layered as final render (D2)"
)
BASELINE_ANCHOR_PATH = "data/recreate_v2/baseline/<sha16>/rc1_vocals_voiced_time_s.json"
RUBRIC_HASH_PATH = "data/recreate_v2/rubric_hash_v2.txt"


def run(*args, **kwargs):
    raise NotImplementedError("c51+ branch")


if __name__ == "__main__":
    run()
