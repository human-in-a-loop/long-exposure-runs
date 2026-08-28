#!/usr/bin/env python3
"""_v3_sweep — enumerate all per-milestone consecutive status transitions in
promise_ledger.jsonl. Feeds design of _STATE_TRANSITIONS for
_infra/ledger-schema-hardening-v3.
"""
import json, collections, sys
from pathlib import Path

WORKSPACE = Path("/home/user/long-exposure-runs/music-gen")
events = []
for raw in (WORKSPACE / "promise_ledger.jsonl").read_text().splitlines():
    line = raw.strip()
    if not line:
        continue
    events.append(json.loads(line))
print("total events:", len(events))

by_m = collections.defaultdict(list)
for ev in events:
    by_m[ev.get("milestone_id")].append(ev)
print("distinct milestones:", len(by_m))

transitions = collections.Counter()
first_statuses = collections.Counter()
for m, evs in by_m.items():
    evs.sort(key=lambda e: e.get("ts", ""))
    seq = [e.get("status") for e in evs]
    first_statuses[seq[0]] += 1
    for i in range(len(seq) - 1):
        transitions[(seq[i], seq[i + 1])] += 1

print("First-status distribution:", dict(first_statuses))
print("Distinct consecutive transitions:", len(transitions))
for (a, b), c in sorted(transitions.items(), key=lambda x: -x[1]):
    print(f"  {a!r:>20} -> {b!r:<20}  count={c}")
