import hashlib, json
# Verify the baseline manifest itself is byte-equal to its pinned sha
with open('data/harness_and_writer_hardening_v3/baseline_replay_manifest.jsonl','rb') as f: d=f.read()
sha = hashlib.sha256(d).hexdigest()
print('baseline_replay_manifest.jsonl SHA:', sha)
print('pinned baseline_manifest_sha:', open('data/harness_and_writer_hardening_v3/baseline_manifest_sha.txt').read().strip())
print('verdict-pinned:', 'c175d65a87bae90be2b8212fbfc0a547ff49964e5fbc30582fef2be5933871f3')
print()
# Verify each pre-edit canonical row hash matches current promise_ledger.jsonl row content-hash
# The manifest records pre-edit canonical sha per line 1..793. Re-canonicalize the current ledger's raw rows and compare.
lines = open('promise_ledger.jsonl','rb').read().splitlines()
print('current promise_ledger.jsonl line count:', len(lines))
manifest = [json.loads(l) for l in open('data/harness_and_writer_hardening_v3/baseline_replay_manifest.jsonl','rb').read().splitlines()]
print('manifest rows:', len(manifest))
# For each of first 793 lines, canonicalize and compare
mismatches = 0
first_mismatch = None
for i in range(min(793, len(lines))):
    row = json.loads(lines[i])
    canon = json.dumps(row, sort_keys=True, separators=(',',':')).encode('utf-8')
    cur_sha = hashlib.sha256(canon).hexdigest()
    expected = manifest[i]['canonical_sha256_pre_edit']
    if cur_sha != expected:
        mismatches += 1
        if first_mismatch is None:
            first_mismatch = (i+1, expected, cur_sha, manifest[i].get('milestone_id'), manifest[i].get('event_id'))
print('canonical sha mismatches in first 793 rows:', mismatches)
if first_mismatch:
    print('first mismatch: line', first_mismatch[0], 'milestone_id', first_mismatch[3])
    print('  expected:', first_mismatch[1])
    print('  computed:', first_mismatch[2])
print('total current lines:', len(lines), '(expected 793 pre-edit + post-edit additions)')
