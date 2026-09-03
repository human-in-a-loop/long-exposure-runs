#!/usr/bin/env python3
"""One-shot enumeration of c22/c23 events in main ledger."""
import json
lines = open("promise_ledger.jsonl").readlines()
print(f"total rows: {len(lines)}")
for i, ln in enumerate(lines[1207:], start=1208):
    try:
        ev = json.loads(ln)
    except Exception:
        continue
    c = ev.get("cycle")
    m = ev.get("milestone_id", "?")
    s = ev.get("status", "?")
    if c in (22, 23) or "c23" in m or "d5530f8d1ccc" in ln:
        print(f"  L{i}: cycle={c} status={s} {m[:100]}")
