#!/usr/bin/env /usr/bin/python3
"""D2 vocals overlay: SHA-verified copy of htdemucs vocals stem into the render dir."""
import hashlib
import json
import shutil
from pathlib import Path

SONG_SHA16 = '31a164f845f8e27e'
SRC = Path(f'data/recreate_v2/baseline/{SONG_SHA16}/rc9_6stem/vocals.wav')
DST_DIR = Path(f'data/v3_spine/{SONG_SHA16}/render')
DST = DST_DIR / 'vocals_htdemucs.wav'


def sha256(p: Path) -> str:
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def main():
    DST_DIR.mkdir(parents=True, exist_ok=True)
    src_sha = sha256(SRC)
    shutil.copy2(SRC, DST)
    dst_sha = sha256(DST)
    assert src_sha == dst_sha, 'copy corruption'
    payload = {
        'schema_version': 1, 'cycle': 4, 'song_sha16': SONG_SHA16,
        'src': str(SRC), 'src_sha256': src_sha,
        'dst': str(DST), 'dst_sha256': dst_sha,
        'note': 'READ-ONLY copy of htdemucs vocals stem for D2 vocals overlay.',
    }
    open(DST_DIR / 'vocals_overlay.json', 'w').write(json.dumps(payload, indent=2, sort_keys=True) + '\n')
    print(f'copied vocals sha={src_sha[:16]}')


if __name__ == '__main__':
    main()
