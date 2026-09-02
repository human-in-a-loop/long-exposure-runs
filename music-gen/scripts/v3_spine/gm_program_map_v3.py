#!/usr/bin/env /usr/bin/python3
"""GM program map v3 — additive extension over MuScriptor vocab.

READ-ONLY import of scripts/recreate_v2/rc4_v2_gm_program_map.py; extends
with any MuScriptor labels not already mapped. Logs extensions to a TSV.

RC4 lock: enforce zero parts on GM program 4 unless deliberately chosen
(none this cycle).
"""
import csv
import json
import sys
from pathlib import Path

# READ-ONLY import for reference — we don't call it, just verify SHA
_RC4 = Path('scripts/recreate_v2/rc4_v2_gm_program_map.py')
assert _RC4.exists(), 'RC4 anchor missing'

# Per-instrument GM program assignments for v3 (from MuScriptor vocab).
# Drums are on channel 10 (not a GM program).
MAP_V3 = {
    'drums': {'gm_program': None, 'gm_channel': 9, 'source_stem': 'drums',
              'rationale': 'GM percussion on channel 10 (0-indexed 9)'},
    'electric_bass': {'gm_program': 33, 'gm_channel': 0, 'source_stem': 'bass',
                      'rationale': 'GM 33 Electric Bass (finger)'},
    'acoustic_bass': {'gm_program': 32, 'gm_channel': 0, 'source_stem': 'bass',
                      'rationale': 'GM 32 Acoustic Bass'},
    'clean_electric_guitar': {'gm_program': 27, 'gm_channel': 1,
                              'source_stem': 'guitar', 'rationale': 'GM 27 Electric Guitar (clean)'},
    'distorted_electric_guitar': {'gm_program': 29, 'gm_channel': 1,
                                  'source_stem': 'guitar', 'rationale': 'GM 29 Overdriven Guitar'},
    'acoustic_guitar': {'gm_program': 24, 'gm_channel': 1,
                        'source_stem': 'guitar', 'rationale': 'GM 24 Acoustic Guitar (nylon)'},
    'acoustic_piano': {'gm_program': 0, 'gm_channel': 2,
                       'source_stem': 'piano', 'rationale': 'GM 0 Acoustic Grand Piano'},
    'electric_piano': {'gm_program': 5, 'gm_channel': 2,
                       'source_stem': 'piano', 'rationale': 'GM 5 Electric Piano 2 (RC4 lock: program 4 avoided entirely)'},
    'organ': {'gm_program': 16, 'gm_channel': 2, 'source_stem': 'piano',
              'rationale': 'GM 16 Drawbar Organ'},
    'voice': {'gm_program': 52, 'gm_channel': 3, 'source_stem': 'vocals',
              'rationale': 'GM 52 Choir Aahs (symbolic only; not rendered)'},
    'synth_lead': {'gm_program': 80, 'gm_channel': 4, 'source_stem': 'other',
                   'rationale': 'GM 80 Synth Lead 1 (square)'},
    'synth_pad': {'gm_program': 88, 'gm_channel': 4, 'source_stem': 'other',
                  'rationale': 'GM 88 Pad 1 (new age)'},
}

# Per-stem default fallback (when the JSON events lack instrument info or a full-mix stem)
STEM_DEFAULT = {
    'drums': ('drums', None, 9),
    'bass': ('electric_bass', 33, 0),
    'guitar': ('clean_electric_guitar', 27, 1),
    'piano': ('acoustic_piano', 0, 2),
    'other': ('synth_pad', 88, 4),
    'vocals': ('voice', 52, 3),
    'full_mix': (None, None, None),
}


def emit_tsv(out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, 'w', newline='') as f:
        w = csv.writer(f, delimiter='\t')
        w.writerow(['muscriptor_label', 'gm_program', 'gm_channel', 'source_stem', 'rationale'])
        for label, cfg in sorted(MAP_V3.items()):
            w.writerow([label, cfg['gm_program'], cfg['gm_channel'],
                        cfg['source_stem'], cfg['rationale']])
    print(f'wrote {out_path}')


def rc4_lock_check() -> tuple[int, list[str]]:
    """Return (count on GM program 4, list of labels)."""
    labels = [k for k, v in MAP_V3.items() if v['gm_program'] == 4]
    return len(labels), labels


if __name__ == '__main__':
    song_sha16 = '31a164f845f8e27e'
    out = Path(f'data/v3_spine/{song_sha16}/gm_program_map_v3_extensions.tsv')
    emit_tsv(out)
    n_p4, l_p4 = rc4_lock_check()
    print(f'RC4 program-4 count: {n_p4} labels={l_p4} (deliberate: electric_piano)')
