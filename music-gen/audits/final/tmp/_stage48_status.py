#!/usr/bin/env python3
import json
from collections import Counter

statuses = Counter()
confidences = Counter()
milestones_state = {}

with open('/home/user/long-exposure-runs/music-gen/promise_ledger.jsonl') as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        try:
            e = json.loads(line)
        except Exception:
            continue
        mid = e.get('milestone_id')
        st = e.get('status')
        conf = e.get('confidence', {})
        if isinstance(conf, dict):
            lvl = conf.get('level', '')
        else:
            lvl = str(conf)
        if mid and st:
            milestones_state[mid] = {
                'status': st,
                'confidence': lvl,
                'ts': e.get('ts', ''),
                'cycle': e.get('cycle'),
            }

for mid, info in milestones_state.items():
    statuses[info['status']] += 1
    confidences[info['confidence']] += 1

print('# Terminal status distribution (last event per milestone):')
for s, c in statuses.most_common():
    print(f'  {c:4d}  {s}')
print()
print('# Confidence distribution:')
for c, n in confidences.most_common():
    print(f'  {n:4d}  {c}')
print()
print(f'# Total distinct milestones with events: {len(milestones_state)}')

inprog = [mid for mid, info in milestones_state.items() if info['status'] == 'in-progress']
low_val = [mid for mid, info in milestones_state.items() if info['confidence'] == 'low' and info['status'] == 'validated']
print(f'# in-progress: {len(inprog)}')
for m in sorted(inprog):
    print(f'    {m}')
print(f'# low-confidence validated: {len(low_val)}')
for m in sorted(low_val):
    print(f'    {m}')
