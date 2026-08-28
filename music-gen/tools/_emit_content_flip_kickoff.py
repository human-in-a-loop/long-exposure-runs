#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-08-28T14:00:00Z
# cycle: 14
# run_id: run-2026-08-28T040704Z
# agent: worker
# milestone: M-TEX-1/panel/embedding/content-flip-analysis
# ---
"""Emit plan-registration + kickoff ledger events for the content-flip branch."""
import json, uuid, datetime, subprocess, sys
assert sys.executable == "/usr/bin/python3", sys.executable

def uid(payload):
    canon = json.dumps(
        {k: payload[k] for k in sorted(payload) if k not in ("event_id", "ts")},
        separators=(",", ":"),
        sort_keys=True,
    )
    return str(uuid.uuid5(uuid.NAMESPACE_URL, canon))


ts = datetime.datetime.now(datetime.timezone.utc).isoformat()

events = [
    {
        "milestone_id": "_plan/register-content-flip-milestone",
        "status": "validated",
        "confidence": {"level": "high", "assessor": "worker",
                       "rationale": "plan-file drift fix so promise_check resolves M-TEX-1/panel/embedding/content-flip-analysis events"},
        "narrative": "Registered M-TEX-1/panel/embedding/content-flip-analysis in the 5-col Milestones table and in the 3-col Sub-milestones table before emitting any events under this ID (plan-file drift lesson cycles 6-13).",
        "artifacts": ["plan_of_record.md"],
        "cycle": 14, "agent": "worker",
        "run_id": "run-2026-08-28T040704Z", "ts": ts,
    },
    {
        "milestone_id": "M-TEX-1/panel/embedding/content-flip-analysis",
        "status": "in-progress",
        "confidence": {"level": "medium", "assessor": "worker",
                       "rationale": "branch kickoff — cycle-13 anchor byte-identity + sweep + flip characterization still to be established this cycle"},
        "narrative": "Cycle-14 clone-2 kickoff: characterize the cycle-13 VGGish family-disagreement content-dependence via a 2-axis synthetic sweep (polyphony P1..P4 x envelope E1..E4). Cycle-9 pinned DawDreamer chain duplicated locally in scripts/tex/content_flip/apply_pinned_chain.py; scripts.tex.render_effects_layered.py itself remains untouched.",
        "artifacts": ["plan_of_record.md"],
        "cycle": 14, "agent": "worker",
        "run_id": "run-2026-08-28T040704Z", "ts": ts,
    },
]

WS = "/home/user/long-exposure-runs/music-gen"
for e in events:
    e["event_id"] = uid(e)
    r = subprocess.run(
        ["/usr/bin/python3", "-m", "long_exposure.tools.ledger_append",
         "--workspace", WS, "--event", json.dumps(e)],
        capture_output=True, text=True,
        env={"PYTHONPATH": "/home/user/human-in-a-loop/long-exposure",
             "PATH": "/usr/bin:/bin"},
    )
    print(e["milestone_id"], "rc=", r.returncode, r.stdout.strip(), r.stderr.strip())
