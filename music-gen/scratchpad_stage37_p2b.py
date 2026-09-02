import hashlib, json
from long_exposure.tools._ledger_schema import canonical_json, canonical_json_bytes
# The manifest column is "canonical_sha256_pre_edit" — likely a hash of canonical_json() or canonical_json_bytes(default: no supersedes)
lines = open('promise_ledger.jsonl','rb').read().splitlines()
manifest = [json.loads(l) for l in open('data/harness_and_writer_hardening_v3/baseline_replay_manifest.jsonl','rb').read().splitlines()]

def try_flavor(fn, label, use_bytes=False):
    m = 0
    fm = None
    for i in range(min(793, len(lines))):
        row = json.loads(lines[i])
        payload = fn(row)
        if not use_bytes:
            payload = payload.encode('utf-8')
        cur = hashlib.sha256(payload).hexdigest()
        exp = manifest[i]['canonical_sha256_pre_edit']
        if cur != exp:
            m += 1
            if fm is None:
                fm = (i+1, exp, cur, manifest[i].get('milestone_id'))
    print(label, 'mismatches:', m, 'first:', fm[0] if fm else 'none')
    return m

try_flavor(canonical_json, 'canonical_json (no supersedes)')
try_flavor(lambda e: canonical_json_bytes(e, include_supersedes=False), 'canonical_json_bytes(sup=False)', use_bytes=True)
try_flavor(lambda e: canonical_json_bytes(e, include_supersedes=True), 'canonical_json_bytes(sup=True)', use_bytes=True)
