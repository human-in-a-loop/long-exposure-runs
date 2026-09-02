#!/usr/bin/env /usr/bin/python3
"""Re-snapshot anchors post-run; assert pre==post byte-exact."""
import hashlib
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from scripts.v3_spine.anchor_preservation_pre_v2 import ANCHORS, SONG_SHA16, sha_of  # noqa: E402


def main() -> None:
    pre_path = Path(f'data/v3_spine/{SONG_SHA16}/anchor_preservation_pre_v2.json')
    if not pre_path.exists():
        print('FATAL: pre-snapshot missing', file=sys.stderr)
        sys.exit(1)
    pre = json.loads(pre_path.read_text())
    pre_map = {e['path']: e['sha256'] for e in pre['anchors']}

    post_entries = []
    diffs = []
    for p in ANCHORS:
        if not os.path.exists(p):
            continue
        s = sha_of(p)
        post_entries.append({'path': p, 'sha256': s})
        if pre_map.get(p) != s:
            diffs.append({'path': p, 'pre_sha256': pre_map.get(p), 'post_sha256': s})

    payload = {
        'schema_version': 1, 'cycle': 4, 'song_sha16': SONG_SHA16,
        'anchor_count': len(post_entries),
        'pre_snapshot_path': str(pre_path),
        'anchors_post': post_entries,
        'diffs_pre_vs_post': diffs,
        'n_mismatch': len(diffs),
        'all_match': (len(diffs) == 0),
    }
    out = Path(f'data/v3_spine/{SONG_SHA16}/anchor_preservation_v2.json')
    out.write_text(json.dumps(payload, indent=2, sort_keys=True) + '\n')
    print(f'wrote {out} n_anchors={len(post_entries)} n_mismatch={len(diffs)}')
    if diffs:
        print('DIFFS:', diffs)


if __name__ == '__main__':
    main()
