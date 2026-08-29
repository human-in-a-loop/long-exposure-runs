import json, pathlib
m = json.loads(pathlib.Path('data/anchor_manifest_v1.json').read_text())
print('anchor_count:', m.get('anchor_count'))
anchors = m['anchors']
print('type:', type(anchors), 'len:', len(anchors))
if isinstance(anchors, list):
    for i, a in enumerate(anchors):
        if 'SOURCE_DATE_EPOCH' in json.dumps(a):
            print(f'anchor #{i+1}:', json.dumps(a, indent=2))
            break
elif isinstance(anchors, dict):
    for k, v in anchors.items():
        if 'SOURCE_DATE_EPOCH' in k or 'SOURCE_DATE_EPOCH' in json.dumps(v):
            print(f'key {k!r}:', json.dumps(v, indent=2))
            break
