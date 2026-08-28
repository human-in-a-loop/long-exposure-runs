#!/usr/bin/env python3
"""One-shot: capture batch-v4 anchors as frozen ground truth for batch-v5-n16."""
import json, hashlib, os, sys
from datetime import datetime, timezone

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(REPO, 'data/gen/batch_v4/batch_manifest.json')
dst_dir = os.path.join(REPO, 'data/gen/batch_v5_n16')
os.makedirs(dst_dir, exist_ok=True)
dst = os.path.join(dst_dir, 'batch_v4_anchor_reference.json')

m = json.load(open(src))
h = hashlib.sha256(open(src,'rb').read()).hexdigest()
anchors = {}
for r in m['per_song']:
    s = r['salt']
    sh = r['sha']
    anchors[f'song_{s}'] = {
        'musicxml': sh['musicxml'],
        'midi': sh['midi'],
        'bare_wav': sh['bare_wav'],
        'effects_wav': sh['effects_wav'],
    }
out = {
    'source_manifest_sha256': h,
    'captured_at': datetime.now(timezone.utc).isoformat(),
    'salts': list(range(8)),
    'anchors': anchors,
}
json.dump(out, open(dst,'w'), indent=2, sort_keys=True)
print('WROTE', dst)
print('source_manifest_sha256:', h)
print('songs:', len(anchors))
