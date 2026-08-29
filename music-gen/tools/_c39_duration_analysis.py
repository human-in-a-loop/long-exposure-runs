#!/usr/bin/python3
"""Analyze how fixture durations map to standard type+dot at divisions=960."""
import re
import pathlib
from collections import Counter

TYPE_BASE_QL = {
    'whole': 4.0, 'half': 2.0, 'quarter': 1.0, 'eighth': 0.5,
    '16th': 0.25, '32nd': 0.125, '64th': 0.0625,
    '128th': 0.03125, '256th': 0.015625,
}
CANONICAL_DIVISIONS = 960


def build_duration_map(divs=CANONICAL_DIVISIONS):
    m = {}
    for name, base_ql in TYPE_BASE_QL.items():
        for dots in [0, 1, 2, 3]:
            mult = 2 - (2 ** -dots)
            ticks_f = base_ql * divs * mult
            if ticks_f == int(ticks_f):
                ticks = int(ticks_f)
                if ticks not in m:
                    m[ticks] = (name, dots)
    return m


text = pathlib.Path(
    'data/score_bridge_real_audio/inputs/merged_real_audio.musicxml'
).read_text()
durations_raw = [int(x) for x in re.findall(r'<duration>(\d+)</duration>', text)]
factor = CANONICAL_DIVISIONS / 10080.0  # = 2/21
rescaled = []
non_integer_pre_snap = 0
for d in durations_raw:
    r = d * factor
    if abs(r - round(r)) > 1e-9:
        non_integer_pre_snap += 1
    rescaled.append(max(1, int(round(r))))

dmap = build_duration_map()
print('duration map (ticks -> type,dot):')
for k in sorted(dmap):
    print(' ', k, '->', dmap[k])

print('---')
print('total durations:', len(rescaled))
print('non-integer pre-snap:', non_integer_pre_snap)
in_map = sum(1 for r in rescaled if r in dmap)
print('map hits:', in_map, '/', len(rescaled))
misses = Counter(r for r in rescaled if r not in dmap)
print('unique missing ticks:', len(misses))
print('top-20 missing ticks by frequency:')
for tk, count in misses.most_common(20):
    print(' ', tk, 'ql~', tk / CANONICAL_DIVISIONS, 'count', count)
