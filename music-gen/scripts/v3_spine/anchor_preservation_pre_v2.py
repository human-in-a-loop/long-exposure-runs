#!/usr/bin/env /usr/bin/python3
"""Snapshot upstream + cycle-3 anchors for M-V3-SPINE-1 cycle 4 (OPTION A)."""
import hashlib
import json
import os
import sys
from pathlib import Path

SONG_SHA16 = '31a164f845f8e27e'

ANCHORS = [
    # Upstream binaries + SoundFont
    '/usr/share/sounds/sf2/FluidR3_GM.sf2',
    'scripts/palette_render/render_stem.py',
    'workspace/learned_transcribers_venv/bin/muscriptor',
    # Rubric chain
    'docs/v3_spine_rubric.md',
    'data/v3_spine/rubric_hash.txt',
    'docs/v3_spine_rubric_v2.md',
    'data/v3_spine/rubric_hash_v2.txt',
    'docs/v3_spine_canonical_midi_serializer_spec.md',
    'data/v3_spine/canonical_serializer_spec_hash.txt',
    # READ-ONLY rc scripts
    'scripts/recreate_v2/rc7_v2_rerun.py',
    'scripts/recreate_v2/rc6_v2_panel_gate.py',
    'scripts/recreate_v2/rc8_section_selection.py',
    'scripts/recreate_v2/rc4_v2_gm_program_map.py',
    # Baselines
    f'data/recreate_v2/baseline/{SONG_SHA16}/rc5_tempo_bpm.json',
    f'data/recreate_v2/baseline/{SONG_SHA16}/rc7_per_stem_loudness.json',
    f'data/recreate_v2/baseline/{SONG_SHA16}/rc8_chosen_section_verified.json',
    f'data/recreate_v2/baseline/{SONG_SHA16}/rc9_6stem/vocals.wav',
    f'data/recreate_v2/baseline/{SONG_SHA16}/rc9_6stem/drums.wav',
    f'data/recreate_v2/baseline/{SONG_SHA16}/rc9_6stem/bass.wav',
    f'data/recreate_v2/baseline/{SONG_SHA16}/rc9_6stem/guitar.wav',
    f'data/recreate_v2/baseline/{SONG_SHA16}/rc9_6stem/piano.wav',
    f'data/recreate_v2/baseline/{SONG_SHA16}/rc9_6stem/other.wav',
    # Cycle-3 MuScriptor outputs (now READ-ONLY anchors)
    f'data/v3_spine/{SONG_SHA16}/muscriptor/drums.mid',
    f'data/v3_spine/{SONG_SHA16}/muscriptor/drums.json',
    f'data/v3_spine/{SONG_SHA16}/muscriptor/bass.mid',
    f'data/v3_spine/{SONG_SHA16}/muscriptor/bass.json',
    f'data/v3_spine/{SONG_SHA16}/muscriptor/vocals.mid',
    f'data/v3_spine/{SONG_SHA16}/muscriptor/vocals.json',
    f'data/v3_spine/{SONG_SHA16}/muscriptor/guitar.mid',
    f'data/v3_spine/{SONG_SHA16}/muscriptor/guitar.json',
    f'data/v3_spine/{SONG_SHA16}/muscriptor/other.mid',
    f'data/v3_spine/{SONG_SHA16}/muscriptor/other.json',
    f'data/v3_spine/{SONG_SHA16}/muscriptor/piano.mid',
    f'data/v3_spine/{SONG_SHA16}/muscriptor/piano.json',
    f'data/v3_spine/{SONG_SHA16}/muscriptor/full_mix.mid',
    f'data/v3_spine/{SONG_SHA16}/muscriptor/full_mix.json',
]


def sha_of(path: str) -> str:
    with open(path, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()


def main() -> None:
    out_path = Path(f'data/v3_spine/{SONG_SHA16}/anchor_preservation_pre_v2.json')
    out_path.parent.mkdir(parents=True, exist_ok=True)
    entries = []
    missing = []
    for p in ANCHORS:
        if not os.path.exists(p):
            missing.append(p)
            continue
        entries.append({'path': p, 'sha256': sha_of(p)})
    payload = {
        'schema_version': 1,
        'cycle': 4,
        'song_sha16': SONG_SHA16,
        'anchor_count': len(entries),
        'anchors': entries,
        'missing': missing,
        'snapshot_ts': '2026-09-02T00:00:04Z',
    }
    out_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + '\n')
    print(f'wrote {out_path} ({len(entries)} anchors, {len(missing)} missing)')
    if missing:
        print('MISSING:', missing)
        sys.exit(1)


if __name__ == '__main__':
    main()
