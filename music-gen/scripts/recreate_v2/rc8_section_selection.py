#!/usr/bin/python3
# c50 pre-registration stub for RC8 (peak-section-selection).
# Created: 2026-08-29
# Cycle: 50
# Run id: run-2026-08-28T040704Z
# Agent: worker
# Milestone: M-RECREATE-2/accurate-small-set/rc8-peak-section-selection
#
# See docs/m_recreate_2_accurate_small_set_rubric_v2.md §3 (RC8) + §2 (D1).
# Implementation lands in c51+ RC-v2 Branch (folded into A/B/C per §10 handoff).

import sys

if sys.executable != "/usr/bin/python3":
    raise RuntimeError(f"RC8 requires /usr/bin/python3 (got {sys.executable})")

RC_ID = "M-RECREATE-2/accurate-small-set/rc8-peak-section-selection"
ACCEPTANCE_CRITERIA = (
    "chosen-section metadata (song_id,t_start_s,t_end_s,combined_score,"
    "rms_score,onset_density_score,weights) present in provenance (A8) AND "
    "reproduces focus_set_v2.json.chosen_section byte-for-byte"
)
BASELINE_ANCHOR_PATH = "data/recreate_v2/focus_set_v2.json"
RUBRIC_HASH_PATH = "data/recreate_v2/rubric_hash_v2.txt"


def run(*args, **kwargs):
    raise NotImplementedError("c51+ branch")


if __name__ == "__main__":
    run()
