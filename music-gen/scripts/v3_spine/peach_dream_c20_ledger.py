#!/usr/bin/env /usr/bin/python3
"""c20 clone-2: 4-row housekeeping ledger for Peach Dream (M-V3-FOCUS-1 build-out).

Rows (ts+1s ordering per convention):
  1. M-INGEST-1/egress-probe-cycle20-clone-2
  2. _plan/register-c20-v3-focus-song-88d247468cb6d49f-clone-2
  3. _infra/adopt-cycle20-tests-clone-2
  4. _archive/cycle-20-scratch-clone-2
"""
from __future__ import annotations
import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

os.environ.setdefault("PYTHONHASHSEED", "0")
os.environ.setdefault("SOURCE_DATE_EPOCH", "1756463424")
os.environ.setdefault("TZ", "UTC")
os.environ.setdefault("LC_ALL", "C.UTF-8")

if sys.executable != "/usr/bin/python3":
    raise RuntimeError(f"ledger requires /usr/bin/python3 (got {sys.executable})")

WSROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(WSROOT))

from long_exposure.workspace_bootstrap import append_ledger_event  # noqa: E402

RUN_ID = "run-2026-08-28T040704Z"
CYCLE = 20
AGENT = "worker-clone-2"


def _now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _base(mid, narrative, artifacts, status="validated", conf="high"):
    return {
        "milestone_id": mid,
        "status": status,
        "confidence": {"level": conf, "rationale": "measured", "assessor": "worker-clone-2"},
        "narrative": narrative,
        "artifacts": artifacts,
        "cycle": CYCLE,
        "run_id": RUN_ID,
        "agent": AGENT,
        "ts": _now_iso(),
    }


def build_events():
    events = []
    events.append(_base(
        "M-INGEST-1/egress-probe-cycle20-clone-2",
        "Cycle-20 clone-2 linear egress probe: HTTP 429 + tv_embedded unchanged. "
        "No PyPI/network access attempted; proxy TLS respected.",
        ["data/ingestion/egress_status.jsonl"],
    ))
    events.append(_base(
        "_plan/register-c20-v3-focus-song-88d247468cb6d49f-clone-2",
        "Register c20 clone-2 Peach Dream (sha16 88d247468cb6d49f) as third of four "
        "M-V3-FOCUS-1 build-outs per c20 OPERATOR STEERING break-glass directive. "
        "Chosen section t=172.87..202.87s from focus_set_v2.json. Full v3 per-stem "
        "chain end-to-end delivered under data/v3/deliveries/88d247468cb6d49f/.",
        ["data/v3/deliveries/88d247468cb6d49f/cycle20/verdict.json",
         "data/v3/deliveries/88d247468cb6d49f/operator_section/manifest.json"],
    ))
    events.append(_base(
        "_infra/adopt-cycle20-tests-clone-2",
        "Adopting tests/test_v3_focus_peach_dream_c20.py (12 test cases) — Peach Dream "
        "focus-song variant of the c9..c19 12-case shape.",
        ["tests/test_v3_focus_peach_dream_c20.py"],
    ))
    events.append(_base(
        "_archive/cycle-20-scratch-clone-2",
        "No one-shot scratch to archive this cycle — per-song sibling scripts under "
        "scripts/v3_spine/peach_dream_c20_*.py are first-class and remain live for "
        "downstream Peach Dream operator ear + M-V3-CORPUS scaling.",
        [],
    ))
    return events


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    events = build_events()
    if args.dry_run:
        print(json.dumps([{"milestone_id": e["milestone_id"], "status": e["status"]}
                          for e in events], indent=2))
        return
    prev_ts = None
    for e in events:
        # enforce ts+1s ordering
        if prev_ts is not None:
            cur = datetime.strptime(e["ts"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
            prv = datetime.strptime(prev_ts, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
            if (cur - prv).total_seconds() < 1:
                time.sleep(1.1 - (cur - prv).total_seconds() % 1)
                e["ts"] = _now_iso()
        append_ledger_event(str(WSROOT), e)
        print(f"appended: {e['milestone_id']} ts={e['ts']}")
        prev_ts = e["ts"]


if __name__ == "__main__":
    main()
