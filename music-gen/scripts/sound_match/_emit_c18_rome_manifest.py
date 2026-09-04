#!/usr/bin/env -S /usr/bin/python3
"""c18 Track 2: emit Rome v4 stem_manifest.json (skeleton parallel to WIG c17)."""
import hashlib
import json
from pathlib import Path

stems_dir = Path('data/v3_spine/51e433ade2a845e1/operator_section/rc9_6stem')
out_dir = Path('data/v4/profiles/51e433ade2a845e1')
out_dir.mkdir(parents=True, exist_ok=True)

stems = {}
for name in ['bass', 'drums', 'guitar', 'piano', 'other', 'vocals']:
    p = stems_dir / f'{name}.wav'
    stems[name] = {
        'relpath': str(p),
        'sha256': hashlib.sha256(p.read_bytes()).hexdigest(),
        'size_bytes': p.stat().st_size,
    }

manifest = {
    'kind': 'v4_stem_manifest',
    'song_sha16': '51e433ade2a845e1',
    'song_title': 'Rome',
    'cycle': 18,
    'run_id': 'run-2026-08-28T040704Z',
    'agent': 'worker',
    'created': '2026-09-04T04:15:00Z',
    'audio_sha256': (
        '51e433ade2a845e1'  # short id; full sha not required at skeleton stage
    ),
    'source': {
        'kind': 'htdemucs_6s',
        'relpath': str(stems_dir) + '/',
        'section_t_start_s': 62.74031746031746,
        'section_t_end_s': 92.74031746031747,
        'section_duration_s': 30.0,
        'section_source': 'data/recreate_v2/focus_set_v2.json',
    },
    'stems': stems,
    'blocked_on': '_manager/M-V4-METRIC-SEMANTICS-c16',
    'note_metric_semantics_carryover': (
        'candidate acceptance under this song’s profile suite awaits '
        'Track 2 operator resolution'
    ),
    'env_pin_sha256': (
        '2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca'
    ),
    'schema_shape_note': (
        'byte-parallel to WIG c17 manifest at '
        'data/v4/profiles/252eb21ce7df7328/stem_manifest.json'
    ),
}

out = out_dir / 'stem_manifest.json'
out.write_text(json.dumps(manifest, sort_keys=True, indent=2) + '\n')
print('WROTE', out)
print('sha16', hashlib.sha256(out.read_bytes()).hexdigest()[:16])
for k, v in stems.items():
    print(f'  {k}: {v["sha256"][:16]}  {v["size_bytes"]} B')
