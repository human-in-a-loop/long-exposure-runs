#!/usr/bin/python3
# c50 pre-registration sibling stub for RC4 under rubric-v2 first-class-parts path.
# Sibling of scripts/recreate_v2/rc4_gm_program_map.py (c49 v1) which is
# preserved READ-ONLY.
# Created: 2026-08-29
# Cycle: 50
# Run id: run-2026-08-28T040704Z
# Agent: worker
# Milestone: M-RECREATE-2/accurate-small-set/rc-v2-stubs-registered
#
# Per D3 htdemucs_6s: guitar (GM 25-30), piano (GM 0-4), residual 'other'
# gets logged patch choice. Implementation lands in c51+ RC-v2 branches
# (folds into RC1-v2/RC9 merged.midi emission).

import sys

if sys.executable != "/usr/bin/python3":
    raise RuntimeError(f"rc4_v2 requires /usr/bin/python3 (got {sys.executable})")

RC_ID = "M-RECREATE-2/accurate-small-set/rc4-gm-program-map (v2 first-class)"
ACCEPTANCE_CRITERIA = (
    "merged.midi contains distinct guitar (GM 25-30) + piano (GM 0-4) parts "
    "with logged GM programs; zero parts on GM program 4 unless deliberately "
    "chosen and logged"
)
BASELINE_ANCHOR_PATH = "data/recreate_v2/baseline/<sha16>/rc9_6stem/ OR rc9_htdemucs_6s_blocked.json"
RUBRIC_HASH_PATH = "data/recreate_v2/rubric_hash_v2.txt"


def run(*args, **kwargs):
    raise NotImplementedError("c51+ branch")


if __name__ == "__main__":
    run()
