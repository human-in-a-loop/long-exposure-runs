import json, hashlib, sys
m = json.load(open('data/anchor_manifest_v1.json'))
print('anchor_count field:', m.get('anchor_count'))
anchors = m.get('anchors', [])
print('actual anchors list len:', len(anchors))
sde_idx = -1
for i, a in enumerate(anchors):
    if 'SOURCE_DATE_EPOCH' in json.dumps(a):
        sde_idx = i
        print('entry index (1-based):', i+1)
        print('  anchor_id:', a.get('anchor_id'))
        print('  cycle:', a.get('cycle'))
        print('  kind:', a.get('kind'))
        print('  is_readonly:', a.get('is_readonly'))
        print('  keys:', sorted(a.keys()))
        if 'value' in a:
            v = str(a['value']).encode('utf-8')
            expected = hashlib.sha256(v).hexdigest()
            print('  value:', repr(a['value']))
            print('  stored value_sha256:', a.get('value_sha256'))
            print('  computed value_sha256:', expected)
            print('  value_sha256 match:', expected == a.get('value_sha256'))
        if 'entry_sha256' in a:
            entry_dict = {"key": a.get("key"), "value": a.get("value"), "value_sha256": a.get("value_sha256")}
            canon = json.dumps(entry_dict, sort_keys=True, separators=(',',':')).encode('utf-8')
            expected_entry = hashlib.sha256(canon).hexdigest()
            print('  stored entry_sha256:', a.get('entry_sha256'))
            print('  computed entry_sha256:', expected_entry)
            print('  entry_sha256 match:', expected_entry == a.get('entry_sha256'))
        # print the full record for context
        print('  FULL RECORD:', json.dumps(a, sort_keys=True, indent=2))
        break
if sde_idx == -1:
    print('SOURCE_DATE_EPOCH not found; anchor summary:')
    for i,a in enumerate(anchors):
        print('  #', i+1, 'anchor_id=', a.get('anchor_id'), 'cycle=', a.get('cycle'))
