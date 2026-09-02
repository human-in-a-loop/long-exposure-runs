import json, uuid, hashlib
from long_exposure.tools._ledger_schema import canonical_json_bytes, content_hash_event_id, content_hash_event_id_v2
lines = open('promise_ledger.jsonl','rb').read().splitlines()
row = json.loads(lines[744])
print('line 745 event_id:', row.get('event_id'))
print('line 745 milestone:', row.get('milestone_id'))
print('has supersedes field:', 'supersedes' in row)
print('supersedes value:', row.get('supersedes'))
# Use library functions directly
u_off = content_hash_event_id(row)
u_on  = content_hash_event_id_v2(row)
print('content_hash_event_id     (default/OFF):', u_off)
print('content_hash_event_id_v2  (v2/ON)     :', u_on)
print('c48 pinned baseline (OFF):', '658231db-5d86-56e5-8ca9-2a9bed7fdf9f')
print('c48 pinned alternate (ON):', '6366af60-acb7-5e3f-a2e5-89b47f42c82f')
print('baseline match:', str(u_off) == '658231db-5d86-56e5-8ca9-2a9bed7fdf9f')
print('alternate match:', str(u_on) == '6366af60-acb7-5e3f-a2e5-89b47f42c82f')
# Also check the line_745_divergence fixture
d = json.load(open('data/harness_and_writer_hardening_v3/line_745_divergence.json'))
print('divergence fixture:', json.dumps(d, indent=2, sort_keys=True)[:600])
