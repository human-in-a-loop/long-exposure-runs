#!/usr/bin/env python3
"""c20 clone-0 WIG: emit 5 ledger events (1 substantive + 4 housekeeping).

Uses ledger_append helper — routes to per-clone shadow ledger under fanout.
"""
from __future__ import annotations
import hashlib
import json
import subprocess
import sys
import uuid
from pathlib import Path

RUN_ID = "run-2026-09-02T173400Z"
TS = "2026-09-02T17:34:00Z"
CYCLE = 20

VERDICT_PATH = Path("data/v3/deliveries/252eb21ce7df7328/cycle20/verdict.json")
VERDICT_SHA = hashlib.sha256(VERDICT_PATH.read_bytes()).hexdigest()
STATE_SNAPSHOT_PATH = Path("data/v3_spine/252eb21ce7df7328/cycle20/state_snapshot.json")
STATE_SHA = hashlib.sha256(STATE_SNAPSHOT_PATH.read_bytes()).hexdigest()

NS = uuid.UUID("6ba7b810-9dad-11d1-80b4-00c04fd430c8")  # any stable ns

def eid(milestone_id):
    return str(uuid.uuid5(NS, f"{milestone_id}|{RUN_ID}|{CYCLE}|clone-0"))

EVENTS = [
    {
        "milestone_id": "M-V3-FOCUS-1/wig-verdict-c20-emitted",
        "event_id": eid("M-V3-FOCUS-1/wig-verdict-c20-emitted"),
        "run_id": RUN_ID,
        "cycle": CYCLE,
        "agent": "worker",
        "ts": TS,
        "status": "action_required",
        "confidence": {
            "level": "high",
            "rationale": (
                "Honest PARTIAL verdict — MuScriptor bg task terminated at 3/7 probes; "
                "downstream chain (canonicalize→merge→render→vocals-overlay→mix-match→"
                "deliver→panel) not run per FD-1. rubric_hash_v2 three-way byte-equality "
                "chain (doc SHA == rubric_hash_v2.txt == verdict.rubric_hash_v2) holds."
            ),
            "assessor": "worker",
        },
        "narrative": (
            "c20 fork 88d75f9754c3 clone-0: WIG (What If I Go, sha16 252eb21ce7df7328) "
            "focus-song v3 per-stem chain PARTIAL. htdemucs_6s complete (6/6 stems "
            "byte-det x2). MuScriptor 3/7 probes complete (drums non-empty, bass "
            "non-empty, guitar empty); background task terminated before piano/vocals/"
            "other/full_mix. Downstream chain NOT EXECUTED per FD-1 (no tuning/retry on "
            "background-task termination; operator decides restart). Operator A/B WAVs "
            "+ full-song WAV NOT EMITTED. Verdict V3_FOCUS_SONG_PARTIAL_pending_operator "
            "emitted at data/v3/deliveries/252eb21ce7df7328/cycle20/verdict.json (sha "
            f"{VERDICT_SHA[:16]}…) with three-way rubric_hash_v2 byte-equality "
            "(c49db5a12e955f26…). Existing artifacts preserved READ-ONLY. Discipline: "
            "FD-1, FD-6 (operator ear only LANDS authority for eventual A/B), cycle<N>/ "
            "placement convention. blocked_on_operator=true, "
            "blocked_on_muscriptor_completion=true."
        ),
        "artifacts": [
            str(VERDICT_PATH),
            str(STATE_SNAPSHOT_PATH),
            "scripts/v3_spine/verdict_wig_c20_partial.py",
            "scripts/v3_spine/compute_wig_c20_state.py",
        ],
    },
    {
        "milestone_id": "_plan/register-c20-wig-focus-sub-leaves",
        "event_id": eid("_plan/register-c20-wig-focus-sub-leaves"),
        "run_id": RUN_ID,
        "cycle": CYCLE,
        "agent": "worker",
        "ts": TS,
        "status": "validated",
        "confidence": {
            "level": "high",
            "rationale": (
                "Plan-of-record row registration for c20 WIG focus-song sub-leaf per "
                "housekeeping pattern; auto-suffix -clone-0 per c33 harness-clone-"
                "namespace-guard writer."
            ),
            "assessor": "worker",
        },
        "narrative": (
            "c20 clone-0 (fork 88d75f9754c3) plan-of-record row registering "
            "M-V3-FOCUS-1/wig-verdict-c20-emitted sub-leaf introduced this cycle. "
            "Honest PARTIAL verdict per FD-1. Auto-suffix -clone-0 by c33 harness "
            "writer guard per c32 fanout-namespace convention."
        ),
        "artifacts": [],
    },
    {
        "milestone_id": "M-INGEST-1/egress-probe-cycle20-wig",
        "event_id": eid("M-INGEST-1/egress-probe-cycle20-wig"),
        "run_id": RUN_ID,
        "cycle": CYCLE,
        "agent": "worker",
        "ts": TS,
        "status": "validated",
        "confidence": {
            "level": "high",
            "rationale": (
                "Periodic egress retry probe per c49 policy path A (per-clone). Failure "
                "mode HTTP 429 + tv_embedded unchanged from c47-c19 registry; not the "
                "two-consecutive media_ok=true unblock signal."
            ),
            "assessor": "worker",
        },
        "narrative": (
            "c20 clone-0 (fork 88d75f9754c3) WIG-branch egress retry probe per c49 policy "
            "path A. HTTP 429 + tv_embedded unchanged from c47-c19 registry. Not the "
            "two-consecutive media_ok=true unblock signal. Not blocking. Bookkeeping only "
            "(this branch focused on WIG per-stem chain and did not touch harvester "
            "surface)."
        ),
        "artifacts": [],
    },
    {
        "milestone_id": "_infra/adopt-cycle20-wig-tests",
        "event_id": eid("_infra/adopt-cycle20-wig-tests"),
        "run_id": RUN_ID,
        "cycle": CYCLE,
        "agent": "worker",
        "ts": TS,
        "status": "validated",
        "confidence": {
            "level": "high",
            "rationale": (
                "Adoption of pre-landed WIG c20 test file (12-case shape) per housekeeping "
                "pattern; not modified this cycle."
            ),
            "assessor": "worker",
        },
        "narrative": (
            "c20 clone-0 (fork 88d75f9754c3) housekeeping: adopt tests/test_v3_focus_wig_"
            "c20.py (12-case shape) as READ-ONLY reference. Test suite pre-landed prior to "
            "this turn; not modified this cycle (PARTIAL verdict makes most preconditions "
            "unmet — determinism gates skip cleanly when A/B WAVs absent). No new test file "
            "introduced."
        ),
        "artifacts": ["tests/test_v3_focus_wig_c20.py"],
    },
    {
        "milestone_id": "_archive/cycle-20-wig-scratch",
        "event_id": eid("_archive/cycle-20-wig-scratch"),
        "run_id": RUN_ID,
        "cycle": CYCLE,
        "agent": "worker",
        "ts": TS,
        "status": "validated",
        "confidence": {
            "level": "high",
            "rationale": (
                "Bookkeeping row for one-shot emitters. Deferred physical move to "
                "tools/stale/ to preserve reproducibility of PARTIAL verdict pending "
                "operator directive on muscriptor restart."
            ),
            "assessor": "worker",
        },
        "narrative": (
            "c20 clone-0 (fork 88d75f9754c3) housekeeping: verdict_wig_c20_partial.py, "
            "compute_wig_c20_state.py, and emit_wig_c20_ledger.py are one-shot emitters "
            "per c29+ pattern. Physical move to tools/stale/ deferred this cycle to "
            "preserve reproducibility of the PARTIAL verdict pending operator directive "
            "on muscriptor restart. Substantive artifacts (verdict.json, "
            "state_snapshot.json) remain in place at data/v3/deliveries/252eb21ce7df7328/"
            "cycle20/ and data/v3_spine/252eb21ce7df7328/cycle20/."
        ),
        "artifacts": [],
    },
]


def main():
    ok = 0
    fail = 0
    for ev in EVENTS:
        cmd = [
            "/usr/bin/python3", "-m", "long_exposure.tools.ledger_append",
            "--event", json.dumps(ev),
        ]
        r = subprocess.run(cmd, capture_output=True)
        out = r.stdout.decode(errors="replace")
        err = r.stderr.decode(errors="replace")
        if r.returncode == 0:
            print(f"  OK  {ev['milestone_id']}")
            ok += 1
        else:
            print(f"  FAIL {ev['milestone_id']}  rc={r.returncode}")
            print(f"    stdout: {out[:400]}")
            print(f"    stderr: {err[:400]}")
            fail += 1
    print(f"\n{ok}/{ok+fail} events appended")
    return 0 if fail == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
