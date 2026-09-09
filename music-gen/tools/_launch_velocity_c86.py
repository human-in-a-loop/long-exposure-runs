#!/usr/bin/python3
"""c86 one-shot detached launcher for scripts/v5/velocity_v5.py (READ-ONLY scripts.v3_spine.launch_detached, start_new_session=True).

created: 2026-09-09T23:20:00Z
cycle: 86
run_id: run-2026-09-06T000000Z
agent: worker
milestone: M-V5-GEN-1/F2-bass-melody-dynamics

Writes data/v5/logs/velocity_v5_c86.launch.json {pid, cmd, log, launched_utc}. Retained in-tree per docs/emitter_exemption_policy.md.
"""
import json
import os
import sys
import time
from pathlib import Path

_WS = Path(__file__).resolve().parent.parent
os.chdir(_WS)
sys.path.insert(0, str(_WS))
from scripts.v3_spine.launch_detached import launch_detached  # noqa: E402  READ-ONLY

cmd = ["/usr/bin/python3", "scripts/v5/velocity_v5.py"] + sys.argv[1:]
log = Path("data/v5/logs/velocity_v5_c86.log")
pid = launch_detached(cmd, log, _WS)
rec = {"pid": pid, "cmd": cmd, "log": str(log), "launched_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "cycle": 86, "agent": "worker",
       "launcher": "scripts/v3_spine/launch_detached.launch_detached (READ-ONLY; start_new_session=True)"}
Path("data/v5/logs/velocity_v5_c86.launch.json").write_text(json.dumps(rec, indent=2) + "\n")
print(json.dumps(rec))
