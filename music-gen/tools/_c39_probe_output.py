#!/usr/bin/python3
"""Quick fidelity probe on the mscore3-generated MIDI."""
import sys
sys.path.insert(0, '.')
from scripts.score_bridge_v2._shared import load_midi_events, REF_MIDI_PATH
from pathlib import Path

out = Path(sys.argv[1])
cand = load_midi_events(out)
ref = load_midi_events(REF_MIDI_PATH)
print('cand notes:', len(cand), '  ref notes:', len(ref))
c_sorted = sorted(cand, key=lambda x: (x[0], x[2]))
r_sorted = sorted(ref, key=lambda x: (x[0], x[2]))
n = min(len(c_sorted), len(r_sorted))
onsets = [abs(c_sorted[i][0] - r_sorted[i][0]) * 1000 for i in range(n)]
ppq480 = 60.0 / 120.0 / 480.0
durs = [abs(c_sorted[i][1] - r_sorted[i][1]) / ppq480 for i in range(n)]
print(f'onset drift ms max: {max(onsets):.6f}')
print(f'onset drift ms mean: {sum(onsets)/n:.6f}')
print(f'duration drift ticks (PPQ=480) max: {max(durs):.6f}')
print(f'duration drift ticks mean: {sum(durs)/n:.6f}')
