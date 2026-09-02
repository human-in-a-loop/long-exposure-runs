import json, hashlib
p = json.load(open('data/deprecation_and_anchor_pin/anchor_preservation_pre.json'))
print('manifest_pre_anchor_count:', p.get('manifest_pre_anchor_count'))
print('manifest_pre_n_entries:', p.get('manifest_pre_n_entries'))
print('manifest_pre_sha:', p.get('manifest_pre_sha'))
anchors_pre = p.get('anchors_pre', [])
print('anchors_pre len:', len(anchors_pre))
# Compare each of first 18 to current manifest anchors [0:18]
m = json.load(open('data/anchor_manifest_v1.json'))
cur = m['anchors']
# Compare canonical JSON of each entry i (0..17) to anchors_pre[i]
diffs = 0
for i in range(len(anchors_pre)):
    a_pre = json.dumps(anchors_pre[i], sort_keys=True, separators=(',',':'))
    a_cur = json.dumps(cur[i], sort_keys=True, separators=(',',':'))
    if a_pre != a_cur:
        diffs += 1
        print('DIFF at index', i)
        print('  pre :', a_pre[:200])
        print('  cur :', a_cur[:200])
print('total diffs in first', len(anchors_pre), 'entries:', diffs)
print('entry #19 (0-based idx 18) anchor_id:', cur[18].get('anchor_id') if len(cur)>18 else 'MISSING')
