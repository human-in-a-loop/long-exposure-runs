"""One-shot probe: enumerate in-progress rows and future-cycle rows in the main ledger."""
import json

in_prog = []
future = []
with open('promise_ledger.jsonl') as f:
    for i, line in enumerate(f, 1):
        r = json.loads(line)
        if r.get('status') == 'in-progress':
            in_prog.append((i, r.get('milestone_id'), r.get('cycle'), r.get('agent')))
        if r.get('cycle') in (37, 40):
            future.append((i, r.get('milestone_id'), r.get('cycle'), r.get('status'), r.get('agent')))

print('IN-PROGRESS rows:')
for x in in_prog:
    print(' ', x)
print()
print('Cycle-37/40 rows:')
for x in future:
    print(' ', x)
