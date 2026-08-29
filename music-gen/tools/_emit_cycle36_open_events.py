"""One-shot emitter: cycle-36 branch-A clone-0 opening ledger events.

Appends _run/cycle_36_launched-clone-0 and M-INGEST-1/egress-probe-clone-0.
Archived to tools/stale/ after use per housekeeping convention.
"""
# created: 2026-08-29T07:20:00Z  cycle: 36  run_id: run-2026-08-28T040704Z
# agent: worker (clone-0, fork 87da4f517029)  milestone: _run/cycle_36_launched-clone-0
import sys
assert sys.executable == "/usr/bin/python3", sys.executable

import os
sys.path.insert(0, "/home/user/human-in-a-loop/long-exposure")
sys.path.insert(0, ".")

# Set clone-context env vars so writer auto-suffixes -clone-0 on infra-family ids.
os.environ["AGENT_CLONE_ID"] = "0"
os.environ["AGENT_FORK_ID"] = "87da4f517029"
os.environ["AGENT_INSTANCE_DIR"] = "/home/user/music-gen-instance/fork-87da4f517029/clone-0"

from long_exposure.workspace_bootstrap import append_ledger_event

# Event 1: cycle 36 launched (clone-0 branch-A)
append_ledger_event(".", {
    "milestone_id": "_run/cycle_36_launched",
    "status": "validated",
    "cycle": 36,
    "run_id": "run-2026-08-28T040704Z",
    "ts": "2026-08-29T07:20:00Z",
    "confidence": {
        "level": "high",
        "rationale": "Cycle 36 Branch A (clone-0) launched per c35 handoff.",
        "assessor": "worker",
    },
    "narrative": (
        "Cycle 36 Branch A launched. Scope: M-EAR-1/real-label-training-v0 - "
        "first real-label ear-model training pass on the 43-song rated corpus "
        "(10 band-4 + 10 band-5 + 13 band-6 + 10 band-7 across "
        "corpus/ratings/{4,5,6,7}/*.mp3). Fires the c26 Path B pre-registered "
        "plan on the c6 pinned chassis (2052-D features + CORN 1-7 head). "
        "Rubric committed BEFORE any script under scripts/ear_v0/ lands; "
        "rubric SHA-256 636c2cd0486760f38bda7d02f1be8472f9e756176e83bb3d8e61ee53491bb2e9 "
        "recorded at data/ear_v0/rubric_hash.txt."
    ),
    "agent": "worker",
    "artifacts": [
        "docs/ear_v0_real_label_training_rubric.md",
        "data/ear_v0/rubric_hash.txt",
    ],
})

# Event 2: egress-probe (validated at emission per c26 convention; media_ok=false)
append_ledger_event(".", {
    "milestone_id": "M-INGEST-1/egress-probe",
    "status": "validated",
    "cycle": 36,
    "run_id": "run-2026-08-28T040704Z",
    "ts": "2026-08-29T07:20:30Z",
    "confidence": {
        "level": "high",
        "rationale": "Non-blocking egress probe per c34 baseline; googlevideo.com CDN still 403.",
        "assessor": "worker",
    },
    "narrative": (
        "Egress-probe row per convention (media_ok=false). Rated audio is "
        "on-disk under corpus/ratings/{4,5,6,7}/*.mp3 so this branch does not "
        "require network. Explicit validated at emission (not in_progress) "
        "per c26 c-egress-probe-emission-convention pattern, closing the c35 "
        "clone-0 emitter bug the c35 auditor flagged. Ingestion-unblock "
        "signal (two consecutive media_ok=true rows) unchanged; egress "
        "remains 403 at *.googlevideo.com."
    ),
    "agent": "worker",
})

print("cycle-36 opening ledger events appended")
