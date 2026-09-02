import json, os
plan_events = {}
with open('promise_ledger.jsonl') as f:
    for line in f:
        try:
            e = json.loads(line)
        except Exception:
            continue
        mid = e.get('milestone_id', '')
        if mid.startswith('_plan/'):
            arts = e.get('artifacts', [])
            plan_events.setdefault(mid, []).append({
                'cycle': e.get('cycle'),
                'artifacts': arts,
                'narrative': (e.get('narrative') or e.get('summary') or '')[:80],
            })

print('Total distinct _plan/* milestones:', len(plan_events))
print()
missing_docs = []
for mid, events in sorted(plan_events.items()):
    all_arts = set()
    for ev in events:
        for a in (ev['artifacts'] or []):
            all_arts.add(a)
    docs_arts = [a for a in all_arts if a.endswith('.md')]
    n_events = len(events)
    if docs_arts:
        marker = 'OK'
    else:
        marker = 'NO-DOC'
        missing_docs.append(mid)
    print(marker, mid, 'events=' + str(n_events), 'docs=' + str(docs_arts[:3]))

print()
print('Milestones without any .md doc artifact:', len(missing_docs))
for m in missing_docs:
    print(' ', m)
