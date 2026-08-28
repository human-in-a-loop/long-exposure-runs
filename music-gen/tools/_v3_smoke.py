#!/usr/bin/env python3
"""Smoke: cycle-15 additions load cleanly and reject the flagship pattern."""
import sys
sys.path.insert(0, "/home/user/human-in-a-loop/long-exposure")
from long_exposure.tools._ledger_schema import (
    _STATE_TRANSITIONS, validate_history, STATUS_VALUES, validate_event,
)

# Sanity: every transition uses statuses in the canonical vocabulary.
for a, b in _STATE_TRANSITIONS:
    assert a in STATUS_VALUES, a
    assert b in STATUS_VALUES, b
print("transitions:", len(_STATE_TRANSITIONS))
print("all in STATUS_VALUES:", True)

# Positive control: reopen path clean.
rows_ok = [
    {"milestone_id": "M-T-1", "ts": "2026-08-28T01:00:00Z",
     "event_id": "a", "status": "in-progress"},
    {"milestone_id": "M-T-1", "ts": "2026-08-28T02:00:00Z",
     "event_id": "b", "status": "validated"},
    {"milestone_id": "M-T-1", "ts": "2026-08-28T03:00:00Z",
     "event_id": "c", "status": "reopened"},
    {"milestone_id": "M-T-1", "ts": "2026-08-28T04:00:00Z",
     "event_id": "d", "status": "in-progress"},
]
assert validate_history(rows_ok) == [], validate_history(rows_ok)

# Negative control: cycle-13 line-250 pattern
rows_bad = [
    {"milestone_id": "M-T-2", "ts": "2026-08-28T01:00:00Z",
     "event_id": "a", "status": "validated"},
    {"milestone_id": "M-T-2", "ts": "2026-08-28T02:00:00Z",
     "event_id": "b", "status": "in-progress"},
]
errs = validate_history(rows_bad)
assert len(errs) == 1, errs
assert "M-T-2" in errs[0] and "validated" in errs[0] and "in-progress" in errs[0], errs
print("bad msg:", errs[0])

# Also: run against real ledger.
import json
from pathlib import Path
events = []
for raw in Path("/home/user/long-exposure-runs/music-gen/promise_ledger.jsonl").read_text().splitlines():
    line = raw.strip()
    if not line: continue
    events.append(json.loads(line))
errs = validate_history(events)
print(f"validate_history on 301-row ledger: {len(errs)} errors")
if errs:
    for e in errs[:5]:
        print("  ", e)
    sys.exit(1)
print("OK")
