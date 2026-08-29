#!/usr/bin/python3
# c50 pre-registration stub for RC9 (first-class parts per instrument).
# Created: 2026-08-29
# Cycle: 50
# Run id: run-2026-08-28T040704Z
# Agent: worker
# Milestone: M-RECREATE-2/accurate-small-set/rc9-first-class-parts
#
# See docs/m_recreate_2_accurate_small_set_rubric_v2.md §3 (RC9) + §2 (D3).
# Depends on D3 htdemucs_6s fetch outcome. c50 records the fetch attempt
# at data/recreate_v2/fetchability_htdemucs_6s.jsonl; if BLOCKED the fallback
# to 4-stem is surfaced as a first-class finding per operator directive.

import sys

if sys.executable != "/usr/bin/python3":
    raise RuntimeError(f"RC9 requires /usr/bin/python3 (got {sys.executable})")

RC_ID = "M-RECREATE-2/accurate-small-set/rc9-first-class-parts"
ACCEPTANCE_CRITERIA = (
    "guitar (GM 25-30) + piano (GM 0-4) become distinct parts with own "
    "transcription and own GM programs in merged.midi; residual 'other' gets "
    "logged patch choice"
)
BASELINE_ANCHOR_PATH = (
    "data/recreate_v2/baseline/<sha16>/rc9_6stem/ "
    "OR data/recreate_v2/baseline/<sha16>/rc9_htdemucs_6s_blocked.json"
)
RUBRIC_HASH_PATH = "data/recreate_v2/rubric_hash_v2.txt"


def run(*args, **kwargs):
    raise NotImplementedError("c51+ branch")


if __name__ == "__main__":
    run()
