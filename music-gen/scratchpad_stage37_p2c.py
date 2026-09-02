import hashlib, json
lines = open('promise_ledger.jsonl','rb').read().splitlines()
manifest = [json.loads(l) for l in open('data/harness_and_writer_hardening_v3/baseline_replay_manifest.jsonl','rb').read().splitlines()]
m = 0
fm = None
for i in range(min(793, len(lines))):
    cur = hashlib.sha256(lines[i]).hexdigest()
    exp = manifest[i]['canonical_sha256_pre_edit']
    if cur != exp:
        m += 1
        if fm is None:
            fm = (i+1, exp, cur, manifest[i].get('milestone_id'))
print('raw-line SHA mismatches (first 793):', m, 'first:', fm)
# Try with trailing newline
m2 = 0
for i in range(min(793, len(lines))):
    cur = hashlib.sha256(lines[i]+b'\n').hexdigest()
    exp = manifest[i]['canonical_sha256_pre_edit']
    if cur != exp:
        m2 += 1
print('raw-line-with-newline SHA mismatches:', m2)
# Also check the field name — maybe it's the canonicalized-json bytes but with different encoding
# What is the manifest entry for line 1?
print()
print('Manifest[0]:', manifest[0])
print('Raw line 1 first 200 bytes:', lines[0][:200])
print('Raw line 1 sha:', hashlib.sha256(lines[0]).hexdigest())
print('Raw line 1 sha+nl:', hashlib.sha256(lines[0]+b'\n').hexdigest())
# Try with ensure_ascii=True
row = json.loads(lines[0])
core = {k:v for k,v in row.items() if k not in ('event_id','ts')}
ascii_bytes = json.dumps(core, sort_keys=True, separators=(',',':'), ensure_ascii=True).encode('utf-8')
print('ascii-canonical (no event_id, no ts) sha:', hashlib.sha256(ascii_bytes).hexdigest())
# Try v2 with supersedes excluded
core2 = {k:v for k,v in row.items() if k not in ('event_id','ts','supersedes')}
ascii_bytes2 = json.dumps(core2, sort_keys=True, separators=(',',':'), ensure_ascii=True).encode('utf-8')
print('ascii-canonical (no event_id, ts, supersedes) sha:', hashlib.sha256(ascii_bytes2).hexdigest())
# Try preserving event_id
core3 = {k:v for k,v in row.items() if k not in ('ts',)}
b3 = json.dumps(core3, sort_keys=True, separators=(',',':'), ensure_ascii=False).encode('utf-8')
print('canonical (no ts) sha:', hashlib.sha256(b3).hexdigest())
core4 = {k:v for k,v in row.items()}
b4 = json.dumps(core4, sort_keys=True, separators=(',',':'), ensure_ascii=False).encode('utf-8')
print('canonical (all fields) sha:', hashlib.sha256(b4).hexdigest())
print()
print('Expected line 1:', manifest[0]['canonical_sha256_pre_edit'])
