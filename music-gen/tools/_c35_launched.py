#!/usr/bin/env python3
"""Emit _run/cycle_35_launched-clone-2 (validated per convention this branch codifies)."""
import os, sys
assert sys.executable == "/usr/bin/python3", sys.executable
sys.path.insert(0, "/home/user/human-in-a-loop/long-exposure")
from long_exposure.workspace_bootstrap import append_ledger_event
from pathlib import Path
import datetime as _dt

# Clear clone-context env so writer does not double-suffix our explicit -clone-2 label.
for v in ("AGENT_FORK_ID", "AGENT_INSTANCE_DIR", "AGENT_CLONE_ID"):
    os.environ.pop(v, None)

WS = Path("/home/user/long-exposure-runs/music-gen")
RUN_ID = "run-2026-08-28T040704Z"
TS = _dt.datetime.now(_dt.timezone.utc).isoformat()

evt = {
    "milestone_id": "_run/cycle_35_launched-clone-2",
    "status": "validated",
    "ts": TS,
    "agent": "worker",
    "cycle": 35,
    "run_id": RUN_ID,
    "confidence": {"level": "high", "rationale": "start-of-cycle marker per launched-event convention this branch codifies (validated at emission, not open work)", "assessor": "worker"},
    "narrative": "Cycle 35 Branch C (fork 07063458736e, clone-2) launched: anchor-manifest freeze + launched-event convention codification. New peer sub-milestone _infra/anchor-manifest-v1 extending the c14/c22/c32/c33 infra-hardening chain. Writing status=validated at emission per the convention this branch codifies.",
    "artifacts": [],
}
append_ledger_event(WS, evt)
print("emitted:", evt["milestone_id"])
