#!/usr/bin/env python3
"""P1 follow-up: enumerate all naming variants used for archive-scratch
and adopt-tests housekeeping events per cycle."""
import json
from collections import defaultdict

events = []
for l in open('promise_ledger.jsonl'):
    l = l.strip()
    if l:
        events.append(json.loads(l))

arc_all = defaultdict(set)
adopt_all = defaultdict(set)
for ev in events:
    mid = ev.get('milestone_id', '')
    cyc = ev.get('cycle')
    if mid.startswith('_archive/') and ('cycle' in mid.lower() or
                                        'scratch' in mid.lower()):
        arc_all[cyc].add(mid)
    if mid.startswith('_infra/') and ('adopt' in mid or 'test' in mid):
        adopt_all[cyc].add(mid)

print('=== ARCHIVE ROWS PER CYCLE (any variant) ===')
for c in sorted(arc_all):
    print(f'  c{c}: {sorted(arc_all[c])}')

print()
print('=== ADOPT/TEST ROWS PER CYCLE (any variant) ===')
for c in sorted(adopt_all):
    print(f'  c{c}: {sorted(adopt_all[c])}')
