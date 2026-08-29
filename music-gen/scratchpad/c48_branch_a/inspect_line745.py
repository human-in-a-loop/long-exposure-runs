import json
from long_exposure.tools._ledger_schema import content_hash_event_id
with open('promise_ledger.jsonl') as f:
    lines = f.readlines()
print('total lines:', len(lines))
row = json.loads(lines[744])
print('milestone_id:', row['milestone_id'])
print('on-disk event_id:', row['event_id'])
print('supersedes:', row.get('supersedes'))
print('supersedes_path:', row.get('supersedes_path'))
print('re-derived (current writer, supersedes IN hash):', content_hash_event_id(row))
row2 = {k: v for k, v in row.items() if k != 'supersedes'}
print('re-derived (supersedes STRIPPED):', content_hash_event_id(row2))
