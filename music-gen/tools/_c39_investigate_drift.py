#!/usr/bin/python3
"""Investigate the 192 vs 195 event count and 1060ms drift."""
import sys
sys.path.insert(0, '.')
from scripts.score_bridge_v2._shared import load_midi_events, REF_MIDI_PATH
from pathlib import Path
from collections import Counter
import mido

out = Path(sys.argv[1])

# Inspect mscore3 MIDI header/tempo/tracks
m = mido.MidiFile(str(out))
print('cand PPQ:', m.ticks_per_beat)
print('cand tracks:', len(m.tracks))
for i, tr in enumerate(m.tracks[:3]):
    print(f'track {i} name:', getattr(tr, 'name', '?'), 'len:', len(tr))
    for msg in tr[:10]:
        print('  ', msg)

r = mido.MidiFile(str(REF_MIDI_PATH))
print('\nref PPQ:', r.ticks_per_beat)
print('ref tracks:', len(r.tracks))
for i, tr in enumerate(r.tracks[:3]):
    print(f'track {i} name:', getattr(tr, 'name', '?'), 'len:', len(tr))
    for msg in tr[:10]:
        print('  ', msg)

# Sort events, look at first/last onsets
cand = sorted(load_midi_events(out), key=lambda x: (x[0], x[2]))
ref = sorted(load_midi_events(REF_MIDI_PATH), key=lambda x: (x[0], x[2]))
print(f'\ncand first onset: {cand[0][0]:.4f}s  last onset: {cand[-1][0]:.4f}s')
print(f'ref  first onset: {ref[0][0]:.4f}s  last onset: {ref[-1][0]:.4f}s')

# Pitch distribution comparison
print('\ncand pitch counter:', dict(sorted(Counter(x[2] for x in cand).items())))
print('ref  pitch counter:', dict(sorted(Counter(x[2] for x in ref).items())))
