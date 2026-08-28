#!/usr/bin/env -S /usr/bin/python3
"""One-shot ledger event emitter for M-GEN-1/batch-v5-n16 branch."""
from __future__ import annotations
import sys
from datetime import datetime, timezone
from pathlib import Path

_LE_PARENT = "/home/user/human-in-a-loop/long-exposure"
if _LE_PARENT not in sys.path:
    sys.path.insert(0, _LE_PARENT)
from long_exposure.workspace_bootstrap import append_ledger_event  # noqa: E402


WS = Path("/home/user/long-exposure-runs/music-gen")
RUN_ID = "run-2026-08-28T040704Z"


def _ts():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _emit(milestone_id, status, level, rationale, narrative, artifacts=None,
          extra=None):
    event = {
        "ts": _ts(),
        "milestone_id": milestone_id,
        "status": status,
        "confidence": {"level": level, "rationale": rationale, "assessor": "worker"},
        "narrative": narrative,
        "run_id": RUN_ID,
        "cycle": 23,
        "agent": "worker",
    }
    if artifacts:
        event["artifacts"] = artifacts
    if extra:
        event.update(extra)
    r = append_ledger_event(WS, event)
    print(f"appended {milestone_id} [{status}/{level}]", r)


CMD = sys.argv[1] if len(sys.argv) > 1 else "register"

if CMD == "register":
    _emit(
        "_plan/register-batch-v5-n16-milestone",
        "validated", "high",
        "plan-file drift fix -- added M-GEN-1/batch-v5-n16 row to Milestones + Sub-milestones tables",
        "Added M-GEN-1/batch-v5-n16 row to Milestones + Sub-milestones tables in plan_of_record.md. Enables cycle-23 fanout worker (clone-0 of fork 3fbd8c1ab57c) to emit M-GEN-1/batch-v5-n16 ledger events without promise_check parser drift.",
        artifacts=["plan_of_record.md"],
    )
    _emit(
        "M-GEN-1/batch-v5-n16",
        "in-progress", "medium",
        "branch start: extending batch-v4's salt range from 8 to 16 salts through frozen I4+I3 pipeline; frozen 3-verdict rubric locked (CONFIRMS_CONSTRUCTION >=90% pairs in {form, arrangement} / PARTIAL_CONFIRM 60-90% / CONFIRMS_H2_LARGER <60%)",
        "Cycle-23 fanout branch (clone-0 of fork 3fbd8c1ab57c) starting the N=16 falsification test of cycle-14 collision-floor construction proof. Investigation-first: batch-v4 anchor manifest captured (32 SHAs), frozen 3-verdict rubric locked before any run. Sampler i4_stratified (SHA anchored) + augmented ledger ledger_i3_dminor (SHA a6fd53e9... source, 1233efd5... augmented) unchanged. K distribution: harmonic=20, rhythmic=melodic=form=arrangement=15 at N=16.",
    )
elif CMD == "checkpoint1":
    _emit(
        "M-GEN-1/batch-v5-n16",
        "in-progress", "medium",
        sys.argv[2],
        sys.argv[3],
    )
elif CMD == "checkpoint2":
    _emit(
        "M-GEN-1/batch-v5-n16",
        "in-progress", "medium",
        sys.argv[2],
        sys.argv[3],
    )
elif CMD == "terminal":
    _emit(
        "M-GEN-1/batch-v5-n16",
        "validated", "high",
        sys.argv[2],
        sys.argv[3],
        artifacts=[sys.argv[i] for i in range(4, len(sys.argv))],
    )
elif CMD == "archive":
    _emit(
        "_archive/batch-v5-scratch",
        "validated", "high",
        "one-shot emitters archived to tools/stale/",
        "Archived tools/_emit_v5_events.py and tools/_emit_v5_capstone.py to tools/stale/ after use.",
        artifacts=["tools/stale/_emit_v5_events.py"],
    )
else:
    print(f"unknown cmd: {CMD}")
    sys.exit(1)
